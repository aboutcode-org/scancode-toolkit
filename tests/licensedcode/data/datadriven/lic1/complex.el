;;;; -*- mode:emacs-lisp;coding:utf-8;lexical-binding:t -*-
;;;;****************************************************************************
;;;;FILE:               pjb-sources.el
;;;;LANGUAGE:           emacs lisp
;;;;SYSTEM:             emacs
;;;;USER-INTERFACE:     emacs
;;;;DESCRIPTION
;;;;
;;;;    This module exports functions helpful in writting programs.
;;;;
;;;;    See also state-coding.el
;;;;
;;;;AUTHORS
;;;;    <PJB> Pascal J. Bourguignon
;;;;MODIFICATIONS
;;;;    2006-03-21 <PJB> Added convert-alternative.
;;;;    2004-11-01 <PJB> Renamed carnot to karnaugh.
;;;;                     Nicolas Léonard Sadi Carnot (1796 - 1832)
;;;;                     -- French Mathematician (2nd law of thermodynamics) vs.
;;;;                     Maurice Karnaugh
;;;;                     -- Bell Labs Telecommunication Engineer.
;;;;                     Thanks to josephoswaldgg@hotmail.com for reminding me
;;;;                     the correct name.
;;;;    2004-09-16 <PJB> Corrected an out-of-bound bug in case-lisp-region
;;;;                     reported by starseeke@cy.iec.udel.edu
;;;;    2004-03-23 <PJB> Added insert-columns.
;;;;    2003-06-02 <PJB> Corrected pjb-add-change-log-entry
;;;;    2003-01-20 <PJB> Added walk-sexps, map-sexps, replace-sexps;
;;;;                     reimplemented get-sexps with walk-sexps.
;;;;    2003-01-19 <PJB> Added comment regexp in pjb-sources-data.
;;;;    2003-01-18 <PJB> Added pjb-add-change-log-entry.
;;;;    2003-01-17 <PJB> Made pjb-update-eof use mode instead of filename.
;;;;    2003-01-08 <PJB> Moved in pjb-class & pjb-attrib.
;;;;    2001-01-15 <PJB> Updated pjb-update-eof.
;;;;    199?-??-?? <PJB> Creation.
;;;;BUGS
;;;;LEGAL
;;;;    LGPL
;;;;
;;;;    Copyright Pascal Bourguignon 1990 - 2011
;;;;
;;;;    This library is free software; you can redistribute it and/or
;;;;    modify it under the terms of the GNU Lesser General Public
;;;;    License as published by the Free Software Foundation; either
;;;;    version 2 of the License, or (at your option) any later version.
;;;;
;;;;    This library is distributed in the hope that it will be useful,
;;;;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;;;;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
;;;;    Lesser General Public License for more details.
;;;;
;;;;    You should have received a copy of the GNU Lesser General Public
;;;;    License along with this library; if not, write to the Free Software
;;;;    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
;;;;
;;;;****************************************************************************
(require 'font-lock)
(require 'add-log)

(require 'pjb-cl)
(require 'pjb-utilities)


;; egrep 'defun|defmacro' pjb-sources.el|sed -e 's/(def\(un\|macro\) /;; /'

;; upcase-lisp-region (start end)
;; upcase-lisp ()
;; downcase-lisp-region (start end)
;; downcase-lisp ()

;; skip-comments ()
;; walk-sexps (fun)
;; map-sexps (source-file fun &rest cl-keys)
;; get-sexps (source-file &rest cl-keys)
;; replace-sexps (source-file transformer &rest cl-keys)

;; pjb-attrib (name type &rest args)
;; pjb-defclass (name super &rest args)

;; integer-to-bool-list (n &rest cl-keys)

;; karnaugh-solve (conditions actions table &optional bool-vals action-vals)
;; karnaugh (conditions actions &optional bool-vals)

;; pjb-add-change-log-entry (&optional log-entry)
;; pjb-update-eof (&optional *silent*)

;; pjb-grep-here (pattern)

;; generate-options (options defaults)



(defun mode-name (&optional mode)
  "
RETURN: A string containing the name of the mode, without the -mode suffix.
"
  (let ((mode (cl:string (or mode major-mode))))
    (if (and (< 5 (length mode))
             (string= "-mode" (subseq mode (- (length mode) 5))))
        (subseq mode 0 (- (length mode) 5))
        mode)))

;; ------------------------------------------------------------------------

(defun ooestimate (project-name
                   key-class-count         ;; 1+
                   reusable-domain-objects ;; 0+
                   user-interface-complexity ;; 1,2,3
                   person-count              ;; 1+
                   experience-ratio          ;; [0.0 .. 1.0]
                   )
  (interactive "sProject name:
nKey Class Count:
nReusable Domain Objects:
nUser Interface Complexity (1 2 3):
nPerson Count:
nExperience Ratio [0.0,1.0]: ")
  (let* ((person-day-per-class (+ 15 (* 2.5 (- 1.0 experience-ratio))))
         (total-class-count    (* key-class-count
                                  (+ 1.0 user-interface-complexity)))
         (total-person-days (* total-class-count person-day-per-class))
         (total-months (/ total-person-days 20.000000 person-count)))
    (insert
     (concatenate 'string
       (format "OOEstimate for Project %s:\n\n" project-name)
       (format "   key class count:           %6d\n" key-class-count)
       (format "   reusable domain objects:   %6d\n" reusable-domain-objects)
       (format "   user interface complexity: %s\n"
         (cdr (assoc user-interface-complexity
                     '((1 . "simple") (2 . "medium") (3 . "complex")))))
       (format "   person count:              %6d\n" person-count)
       (format "   experience ratio:          %6.1f\n" experience-ratio)
       (format "\n")
       (format "   total class count:         %6d\n" total-class-count)
       (format "   person day per class       %6.1f\n" person-day-per-class)
       (format "   total person days:         %6d\n" total-person-days)
       (format "   total months:              %6d\n" total-months)))))


;; ------------------------------------------------------------------------
;; pjb-sources-data
;; ------------------------------------------------------------------------
;; some data about source files.

(defparameter *lisp-modes*
  '(emacs-lisp-mode ledit-mode
    lisp-interaction-mode lisp-mode scheme-mode
    common-lisp-mode fi:common-lisp-mode)
  "A list of major modes used to edit lisp or sexp files.")

(defstruct (header-comment-description
             (:type list)
             (:conc-name hcd-))
  major-modes
  header-first-format
  header-title-format
  header-comment-format
  header-last-format
  eof-format
  comment-regexp)


(defparameter *header-comment-descriptions*
  `(((ada-mode snmp-mode snmpv2-mode vhdl-mode sql-mode)
     "--%s"
     "--%s"
     "--    %s"
     "--%s"
     "---- %-32s -- %19s -- %-8s ----"
     "--.*$")
    ((dcl-mode simula-mode )
     "!!%s"
     "!!%s"
     "!!    %s"
     "!!%s"
     "!!!! %-32s -- %19s -- %-8s !!!!"
     "!.*$")
    ((c++-mode c-initialize-cc-mode c-mode cperl-mode cwarn-mode
               idl-mode idlwave-mode java-mode objc-mode pike-mode
               prolog-mode )
     "//%s"
     "//%s"
     "//    %s"
     "//%s"
     "/*** %-32s -- %19s -- %-8s ***/"
     "\\(/\\*.*?\\*/\\)\\|\\(//.*$\\)")
    (,(append '(asm-mode dsssl-mode zone-mode) *lisp-modes*)
      ";;;;%s"
      ";;;;%s"
      ";;;;    %s"
      ";;;;%s"
      ";;;; %-32s -- %19s -- %-8s ;;;;"
      "\\(#|\\([^|]\\||[^#]\\)*|#\\)\\|\\(;.*$\\)")
    ((text-mode)
     "\\(/\\*.*?\\*/\\)\\|\\(//.*$\\)") ;; \(/\*.*?\*/\)\|\(//.*$\)

    ;; ( LSOURCE    ";;;; %-32s -- %19s -- %-8s ;;;;"
    ;;  (asm-mode dsssl-mode emacs-lisp-mode ledit-mode
    ;;   lisp-interaction-mode lisp-mode scheme-mode
    ;;   common-lisp-mode fi:common-lisp-mode
    ;;   zone-mode  )
    ;;  ";;;;%s"
    ;;  ";;;;%s"
    ;;  ";;;;%s"
    ;;  ";;;;    %s"
    ;;  "\\(#|\\([^|]\\||[^#]\\)*|#\\)\\|\\(;.*$\\)")
    ;; ( TEXT       "" ;;";;;; %-32s -- %19s -- %-8s ;;;;"
    ;;  (text-mode)
    ;;  "%s"
    ;;  "%s"
    ;;  "%s"
    ;;  "    %s"
    ;;  "%s"
    ;;  "" ;;";;;; %-32s -- %19s -- %-8s ;;;;"
    ;;  "\\(^;.*$\\)")

    ((awk-mode eshell-mode icon-mode m4-mode makefile-mode makefile-gmake-mode makefile-bsdmake-mode
               octave-mode perl-mode sh-mode shell-script-mode ruby-mode
               tcl-mode )
     "#%s"
     "#%s"
     "#    %s"
     "#%s"
     "#### %-32s -- %19s -- %-8s ####"
     "#.*$")
    ((caml-mode delphi-mode modula-2-mode pascal-mode)
     "(*%s"
     "%s"
     "    %s"
     "%s*)"
     "(*** %-32s -- %19s -- %-8s ***)"
     "(\\*.*?\\*)")
    ((f90-mode fortran-mode)
     "C%s"
     "C%s"
     "C    %s"
     "C%s"
     "CCCC %-32s -- %19s -- %-8s CCCC"
     "^C.*$")
    ((nroff-mode )
     "\\\"\"\"%s"
     "\\\"\"\"%s"
     "\\\"\"\"    %s"
     "\\\"\"\"%s"
     "\\\"\"\" %-32s -- %19s -- %-8s \"\"\"\""
     "\\\".*$")
    ((html-autoview-mode html-mode sgml-mode sgml-name-8bit-mode )
     "<!--%s"
     "%s"
     "    %s"
     "%s-->"
     "<!-- %-32s == %19s == %-8s -->"
     "<!--.*?-->")
    ((latex-mode matlab-mode metafont-mode metapost-mode
                 plain-TeX-mode plain-tex-mode ps-mode
                 reftex-index-phrases-mode reftex-mode
                 slitex-mode tex-mode )
     "%%%s"
     "%%%s"
     "%%    %s"
     "%%%s"
     "%%%%%%%% %-32s -- %19s -- %-8s %%%%%%%%"
     "%%.*$")
    ((scribe-mode)
     "@Comment[%68s]"
     "@Comment[%67s ]"
     "@Comment[    %63s ]"
     "@Comment[%68s]"
     "@Comment[ %-32s -- %19s -- %-8s ]"
     "@Comment\\[[^]]*\\]"))
  "This list contains pjb-source structures, that are lists composed of:
   - a tag,
   - a format string used to make the end of file tag,
   - a list of (major) modes,
   - a format string to format comment lines in the header comment,
   - a regexp string to match a comment in these modes.")


(defun header-comment-description-for-mode (mode)
  (find-if (lambda (entry) (member* mode (hcd-major-modes entry) :test (function eq)))
           *header-comment-descriptions*))


(defun random-case-region (start end)
  (interactive "r")
  (goto-char start)
  (let ((chars (buffer-substring start end)))
    (loop
       for i from 0 below (length chars)
       do (setf (aref chars i) (if (zerop (random 2))
                                   (downcase (aref chars i))
                                   (upcase   (aref chars i)))))
    (delete-region start end)
    (insert chars)))


;; ------------------------------------------------------------------------
;; Converting LISP symbols between COMMON-LISP and emacs
;; ie. converts to down-case or to up-case only the unescaped symbols.
;;

(defun skip-to-next-sexp ()
  (interactive)
  (while (or
          (looking-at "\\([ \n\t\v\f\r]+\\)") ;  spaces
          (looking-at "\\(;.*$\\)")           ;  ;xxx      comment
          (looking-at "\\(#|\\([^|]\\||[^#]\\)*|#\\)")) ;  #|xxx|#   comment
    (goto-char (match-end 0))))

(defun cl-looking-at-what ()
  (cond
    ((looking-at "[ \n\t\v\f\r]") :space)
    ((looking-at ";")  :semicolon-comment) ; ;xxx
    ((looking-at "#|") :sharp-comment)     ;  #|xxx|#
    ((looking-at "\"") :string)            ; "xx\"x"
    ((looking-at "(")  :beginning-of-list)
    ((looking-at ")")  :end-of-list)
    ((looking-at ",@") :comma-at)
    ((looking-at ",")  :comma)
    ((looking-at "'")  :quote)
    ((looking-at "`")  :backquote)
    (t                 :atom)))


(defun cl-skip-over-sharp-comment ()
  (let ((start (match-beginning 0)))
    (goto-char (match-end 0))
    (loop named :search do
      (re-search-forward "\\(#|\\||#\\)")
      (if (string= "#|" (match-string 0))
          (progn
            (cl-skip-over-sharp-comment)
            (goto-char (match-end 0)))
          (let ((end (match-end 0)))
            (set-match-data (list start (point)))
            (return-from :search))))))

(defun cl-skip-over (&optional what)
  (setf what (or what (cl-looking-at-what)))
  (case what
    ((:space)             (looking-at "[ \n\t\v\f\r]+"))
    ((:semicolon-comment) (looking-at ";.*$"))
    ((:sharp-comment)     (when (looking-at "#|")
                            (cl-skip-over-sharp-comment)
                            t))
    ((:string)            (looking-at "\"\\(\\(\\|\\\\.\\|\\\\\n\\)[^\\\\\"]*\\)*\""))
    ((:beginning-of-list) (looking-at "("))
    ((:end-of-list)       (looking-at ")"))
    ((:quote)             (looking-at "'"))
    ((:backquote)         (looking-at "`"))
    ((:comma)             (looking-at ","))
    ((:comma-at)          (looking-at ",@"))
    ((:atom)              (looking-at
                           "\\(|[^|]*|\\|\\\\.\\|#[^|]\\|[^\"\\#|;()'`, \n\t\v\f\r\\]\\)+"))
    (otherwise (error "cannot skip over %s" what)))
  (goto-char (match-end 0)))


(defun cl-forward  (&optional n)
  (interactive "p")
  (setf n (or n 1))
  (dotimes (i n t)
    (cl-skip-over)))


(defun cl-what-is-at-point ()
  (interactive)
  (message "%s" (cl-looking-at-what)))


(defun case-lisp-region (start end transform)
  "
do:      applies transform on all subregions from start to end that are not
         a quoted character, a quote symbol, a comment (;... or #|...|#),
         or a string.
"
  (save-excursion
    (goto-char start)
    (while (< (point) end)
      (while (and (< (point) end)
                  (or (looking-at "[^\"#|;\\\\]+")
                      (and (looking-at "#")
                           (not (looking-at "#|")))))
        (goto-char (match-end 0)))
      (funcall transform start (min end (point)))
      (cl-skip-over)
      (setq start (point)))))


(defun put-dash-in-name (name)
  "
DO:          Insert a dash between all transitions from lower case
             to upper case.
RETURN:      A new string in upper case and dash.
"
  (do ((parts '())
       (i 1 (1+ i))
       (p 0))
      ((<= (length name) i)
       (progn
         (push (string-upcase (subseq name p i)) parts)
         (unsplit-string (nreverse parts) "-")))
    (when (and (lower-case-p (char name (1- i)))
               (upper-case-p (char name i)))
      (push (string-upcase (subseq name p i)) parts)
      (setq p i))))


(defun upcase-lisp-region (start end)
  "
DO:      From the start to end, converts to upcase all symbols.
         Does not touch string literals, comments starting with ';' and
         symbols quoted with '|' or with '\'.
"
  (interactive "*r")
  (case-lisp-region start end (function upcase-region))
  (message "Upcase LISP Done."))


(defun upcase-lisp ()
  "
DO:      From the (point) to (point-max), converts to upcase all symbols.
         Does not touch string literals, comments starting with ';' and
         symbols quoted with '|' or with '\'.
"
  (interactive "*")
  (upcase-lisp-region (point) (point-max)))


(defun downcase-lisp-region (start end)
  "
DO:      From the start to end, converts to low-case all symbols.
         Does not touch string literals, comments starting with ';' and
         symbols quoted with '|' or with '\'.
"
  (interactive "*r")
  (case-lisp-region start end (function downcase-region))
  (message "Downcase LISP Done."))


(defun downcase-lisp ()
  "
DO:      From the (point) to (point-max), converts to lowcase all symbols.
         Does not touch string literals, comments starting with ';' and
         symbols quoted with '|' or with '\'.
"
  (interactive "*")
  (downcase-lisp-region (point) (point-max)))


(defun pjb-case-insensitive-regexp (start end)
  "
DO:      Replace the selection with a case insensitive regexp,
         ie. all letter characters are replaced by [Xx] matching
         both lower case and upper case.
"
  (interactive "r")
  (do ((letters (concatenate 'string
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
                  "abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ"))
       (text        (buffer-substring-no-properties start end))
       (replacement (make-string (* 4 (- end start)) (character " ")))
       (rlen 0) ;; no fill pointer in emacs lisp...
       (i    0 (1+ i)))
      ((>= i (length text))
       (progn
         (delete-region start end)
         (insert (subseq replacement 0 rlen))))
    (if (position (char text i) letters)
        (progn
          (setf (char replacement rlen) (character "["))
          (incf rlen)
          (setf (char replacement rlen) (char-upcase   (char text i)))
          (incf rlen)
          (setf (char replacement rlen) (char-downcase (char text i)))
          (incf rlen)
          (setf (char replacement rlen) (character "]"))
          (incf rlen))
        (progn
          (setf (char replacement rlen) (char text i))
          (incf rlen)))))





(defun pjb-rx-not-string (string)
  (case  (length string)
    ((0)        `(* anything))
    ((1)        `(not (any ,string)))
    (otherwise  `(or (not (any ,(subseq string 0 1)))
                     (seq ,(subseq string 0 1)
                          ,(pjb-rx-not-string (subseq string 1)))))))

;; (pjb-rx-not-string "Hello")
;; (or (not (any "H")) (seq "H" (or (not (any "e")) (seq "e" (or (not (any "l")) (seq "l" (or (not (any "l")) (seq "l" (not (any "o"))))))))))


(defun pjb-regexp-not-string (string)
  (let ((chars (coerce (delete-duplicates
                      (sort (coerce string 'list) (function <))) 'string)))
    (rx-to-string `(seq bot
                        (* (not (any ,chars)))
                        ,(pjb-rx-not-string string)
                        (* (not (any ,chars)))
                        eot))))

;; (pjb-regexp-not-string "abc")
;; "\\(?:\\`[^a-c]*\\(?:[^a]\\|a\\(?:[^b]\\|b[^c]\\)\\)[^a-c]*\\'\\)"


;; (list (pjb-regexp-not-string "hello")
;;       (pjb-regexp-not-string "WORLD"))
;; ("\\(?:\\`[^ehlo]*\\(?:[^h]\\|h\\(?:[^e]\\|e\\(?:[^l]\\|l\\(?:[^l]\\|l[^o]\\)\\)\\)\\)[^ehlo]*\\'\\)"
;;  "\\(?:\\`[^DLORW]*\\(?:[^W]\\|W\\(?:[^O]\\|O\\(?:[^R]\\|R\\(?:[^L]\\|L[^D]\\)\\)\\)\\)[^DLORW]*\\'\\)")


;; (pp (pjb-rx-not-string "hello"))
;; (pp (pjb-rx-not-string "WORLD"))
;;
;; (both
;;  (or
;;   (not
;;    (any "h"))
;;   (seq "h"
;;        (or
;;         (not
;;          (any "e"))
;;         (seq "e"
;;              (or
;;               (not
;;                (any "l"))
;;               (seq "l"
;;                    (or
;;                     (not
;;                      (any "l"))
;;                     (seq "l"
;;                          (not
;;                           (any "o"))))))))))
;;
;;  (or
;;   (not
;;    (any "W"))
;;   (seq "W"
;;        (or
;;         (not
;;          (any "O"))
;;         (seq "O"
;;              (or
;;               (not
;;                (any "R"))
;;               (seq "R"
;;                    (or
;;                     (not
;;                      (any "L"))
;;                     (seq "L"
;;                          (not
;;                           (any "D")))))))))))
;;
;;
;; (defun pjb-rx-both  (r1 r2)
;;
;;   )


(defconstant *apl-letters*
  '("I-BEAM" "SQUISH-QUAD" "QUAD-EQUAL" "QUAD-DIVIDE" "QUAD-DIAMOND" "QUAD-JOT"
    "QUAD-CIRCLE" "CIRCLE-STILE" "CIRCLE-JOT" "SLASH-BAR" "BACKSLASH-BAR"
    "QUAD-SLASH" "QUAD-BACKSLASH" "QUAD-LESS-THAN" "QUAD-GREATER-THAN"
    "LEFTWARDS-VANE" "RIGHTWARDS-VANE" "QUAD-LEFTWARDS-ARROW"
    "QUAD-RIGHTWARDS-ARROW" "CIRCLE-BACKSLASH" "DOWN-TACK-UNDERBAR" "DELTA-STILE"
    "QUAD-DOWN-CARET" "QUAD-DELTA" "DOWN-TACK-JOT" "UPWARDS-VANE"
    "QUAD-UPWARDS-ARROW" "UP-TACK-OVERBAR" "DEL-STILE" "QUAD-UP-CARET" "QUAD-DEL"
    "UP-TACK-JOT" "DOWNWARDS-VANE" "QUAD-DOWNWARDS-ARROW" "QUOTE-UNDERBAR"
    "DELTA-UNDERBAR" "DIAMOND-UNDERBAR" "JOT-UNDERBAR" "CIRCLE-UNDERBAR"
    "UP-SHOE-JOT" "QUOTE-QUAD" "CIRCLE-STAR" "QUAD-COLON" "UP-TACK-DIAERESIS"
    "DEL-DIAERESIS" "STAR-DIAERESIS" "JOT-DIAERESIS" "CIRCLE-DIAERESIS"
    "DOWN-SHOE-STILE" "LEFT-SHOE-STILE" "TILDE-DIAERESIS"
    "GREATER-THAN-DIAERESIS" "COMMA-BAR" "DEL-TILDE" "ZILDE"
    "STILE-TILDE" "SEMICOLON-UNDERBAR"
    "QUAD-NOT-EQUAL" "QUAD-QUESTION" "DOWN-CARET-TILDE" "UP-CARET-TILDE"
    nil nil nil "ALPHA-UNDERBAR" "EPSILON-UNDERBAR" "IOTA-UNDERBAR"
    "OMEGA-UNDERBAR" nil)
  "APL functional characters from unicode.")

;; (dolist (l (sort (cons "QUAD" (copy-list *apl-letters*)) (function STRING<))) (insert (format ";; %s %s\n" l (replace-regexp-in-string "-" " " l))))

;; ALPHA-UNDERBAR ALPHA UNDERBAR
;; BACKSLASH-BAR BACKSLASH BAR
;; CIRCLE-BACKSLASH CIRCLE BACKSLASH
;; CIRCLE-DIAERESIS CIRCLE DIAERESIS
;; CIRCLE-JOT CIRCLE JOT
;; CIRCLE-STAR CIRCLE STAR
;; CIRCLE-STILE CIRCLE STILE
;; CIRCLE-UNDERBAR CIRCLE UNDERBAR
;; COMMA-BAR COMMA BAR
;; DEL-DIAERESIS DEL DIAERESIS
;; DEL-STILE DEL STILE
;; DEL-TILDE DEL TILDE
;; DELTA-STILE DELTA STILE
;; DELTA-UNDERBAR DELTA UNDERBAR
;; DIAMOND-UNDERBAR DIAMOND UNDERBAR
;; DOWN-CARET-TILDE DOWN CARET TILDE
;; DOWN-SHOE-STILE DOWN SHOE STILE
;; DOWN-TACK-JOT DOWN TACK JOT
;; DOWN-TACK-UNDERBAR DOWN TACK UNDERBAR
;; DOWNWARDS-VANE DOWNWARDS VANE
;; EPSILON-UNDERBAR EPSILON UNDERBAR
;; GREATER-THAN-DIAERESIS GREATER THAN DIAERESIS
;; I-BEAM I BEAM
;; IOTA-UNDERBAR IOTA UNDERBAR
;; JOT-DIAERESIS JOT DIAERESIS
;; JOT-UNDERBAR JOT UNDERBAR
;; LEFT-SHOE-STILE LEFT SHOE STILE
;; LEFTWARDS-VANE LEFTWARDS VANE
;; OMEGA-UNDERBAR OMEGA UNDERBAR
;; QUAD Q U A D
;; QUAD-BACKSLASH QUAD BACKSLASH
;; QUAD-CIRCLE QUAD CIRCLE
;; QUAD-COLON QUAD COLON
;; QUAD-DEL QUAD DEL
;; QUAD-DELTA QUAD DELTA
;; QUAD-DIAMOND QUAD DIAMOND
;; QUAD-DIVIDE QUAD DIVIDE
;; QUAD-DOWN-CARET QUAD DOWN CARET
;; QUAD-DOWNWARDS-ARROW QUAD DOWNWARDS ARROW
;; QUAD-EQUAL QUAD EQUAL
;; QUAD-GREATER-THAN QUAD GREATER THAN
;; QUAD-JOT QUAD JOT
;; QUAD-LEFTWARDS-ARROW QUAD LEFTWARDS ARROW
;; QUAD-LESS-THAN QUAD LESS THAN
;; QUAD-NOT-EQUAL QUAD NOT EQUAL
;; QUAD-QUESTION QUAD QUESTION
;; QUAD-RIGHTWARDS-ARROW QUAD RIGHTWARDS ARROW
;; QUAD-SLASH QUAD SLASH
;; QUAD-UP-CARET QUAD UP CARET
;; QUAD-UPWARDS-ARROW QUAD UPWARDS ARROW
;; QUOTE-QUAD QUOTE QUAD
;; QUOTE-UNDERBAR QUOTE UNDERBAR
;; RIGHTWARDS-VANE RIGHTWARDS VANE
;; SEMICOLON-UNDERBAR SEMICOLON UNDERBAR
;; SLASH-BAR SLASH BAR
;; SQUISH-QUAD SQUISH QUAD
;; STAR-DIAERESIS STAR DIAERESIS
;; STILE-TILDE STILE TILDE
;; TILDE-DIAERESIS TILDE DIAERESIS
;; UP-CARET-TILDE UP CARET TILDE
;; UP-SHOE-JOT UP SHOE JOT
;; UP-TACK-DIAERESIS UP TACK DIAERESIS
;; UP-TACK-JOT UP TACK JOT
;; UP-TACK-OVERBAR UP TACK OVERBAR
;; UPWARDS-VANE UPWARDS VANE
;; ZILDE ZILDE




;; (loop for code1 = 123 for code2 from 54 below 96
;;       do (insert (make-char 'mule-unicode-0100-24ff code1 code2)))

;; (font-lock-add-keywords nil (apl-letter-font-lock))
;; (apl-letter-font-lock)

(defparameter *letter-regexp-format* "[^A-Za-z0-9]\\(%s\\)[^A-Za-z0-9]")

(defun apl-letter-font-lock ()
  "
RETURN: A font-lock-keywords list mapping greek letter names
        to greek characters.
"
  (when (<= 21 emacs-major-version)
    (cons
     `(,(format "[^-A-Za-z0-9]\\(%s\\)[^-A-Za-z]"  "QUAD")
        (1 (progn (compose-region (match-beginning 1) (match-end 1)
                                  ,(make-char 'mule-unicode-0100-24ff
                                              124 53)
                                  'decompose-region)
                  nil)))
     (let ((code1 123) (code2 (1- 54)))
       (mapcan
        (lambda (letter)
          (incf code2)
          (when letter
            `((,(format *letter-regexp-format* letter)
                (1 (progn (compose-region (match-beginning 1) (match-end 1)
                                          ,(make-char 'mule-unicode-0100-24ff
                                                      code1 code2)
                                          'decompose-region)
                          nil))))))
        *apl-letters*)))))



(defconstant *greek-letters*
  '( "alpha" "beta" "gamma" "delta" "epsilon" "zeta" "eta"
    "theta" "iota" "kappa" "lambda" "mu" "nu" "xi" "omicron" "pi"
    "rho"  "terminalsigma" "sigma" "tau"
    "upsilon" "phi" "chi" "psi" "omega" )
  "The order of these strings is fixed by the encoding of greek-iso8859-7!")


(defun greek-letter-font-lock ()
  "
RETURN: A font-lock-keywords list mapping greek letter names
        to greek characters.
"
  (when (and (<= 21 emacs-major-version) (<= emacs-major-version 22))
    (let ((maj 64) (min 96))
      (mapcan
       (lambda (letter)
         (incf maj) (incf min)
         `(
           (,(format *letter-regexp-format* (upcase letter))
             (1 (progn (compose-region (match-beginning 1) (match-end 1)
                                       ,(make-char 'greek-iso8859-7 maj)
                                       'decompose-region)
                       nil)))
           (,(format *letter-regexp-format* (downcase letter))
             (1 (progn (compose-region (match-beginning 1) (match-end 1)
                                       ,(make-char 'greek-iso8859-7 min)
                                       'decompose-region)
                       nil)))))
       *greek-letters*))))


(defun tree-upcase-strings (tree)
  (cond
    ((stringp tree) (string-upcase tree))
    ((consp tree) (cons (tree-upcase-strings (car tree))
                        (tree-upcase-strings (cdr tree))))
    (t tree)))


(defvar pretty-greek t)
(defvar *greek-flk* '())

(defun pretty-greek ()
  "
Show LAMBDA keyword as a greek letter lambda in lisp source code.
 (add-hook 'emacs-lisp-mode-hook 'pretty-greek)
 (add-hook 'lisp-mode-hook       'pretty-greek)
"
  (interactive)
  (unless (and (boundp 'pretty-greek) (not pretty-greek))
    (setf font-lock-keywords-case-fold-search nil)
    (setf *greek-flk*
          (sort (append (greek-letter-font-lock) (apl-letter-font-lock))
                (lambda (a b) (> (length (car a)) (length (car b))))))
    (font-lock-add-keywords nil *greek-flk*)))


(defun cancel-pretty-greek ()
  (interactive)
  (font-lock-remove-keywords nil *greek-flk*))



;; (dolist (item   (greek-letter-font-lock))
;;   (insert (format "%S\n" item)))


;; Most of them are available in Unicode.  You can use TeX notation to
;; enter them with the TeX input method, e.g. \nabla -> [].
;;
;; You don't even need the font-lock if you're using Emacs Lisp, as Emacs
;; is perfectly happy about using the characters directly in symbols.  I
;; think this also works with clisp.




;;;---------------------------------------------------------------------
;;; update-def-names implements an obsolete style.

(defvar update-def-names nil
  "Whether update-def-names should add comment with the name of the
definition at the end of the form when it's longer than
`update-def-names-minimum-lines' lines.")

(defvar update-def-names-minimum-lines 20)

(defun def-name (def arg)
  ;; (message "def-name %S %S" def arg)
  (cond
    ((atom arg) arg)
    ((STRING-EQUAL (cl:string (first arg)) "SETF") arg)
    (t (first arg)))) ;;def-name

(defun update-def-names (&optional verbose)
  "
DO:      Update comments at the end of each defmacro,defun,defwhatever
         that stands on serveral lines.
"
  (interactive "*")
  (when update-def-names
    (let ((error-point nil))
      (handler-case
          (save-excursion
            (goto-char (point-min))
            (forward-sexp)
            (while (< (point) (point-max))
              (let ((start (point))
                    end)
                (backward-sexp)
                (setq end (point))
                (let ((sexp (progn (when (looking-at "#!") (forward-line 1))
                                   (sexp-at-point))))
                  (when verbose
                    (message "point:%6d --  sexp: %s"
                             (point) (if (consp sexp) (car sexp) sexp)))
                  (forward-sexp)
                  (when (and (< update-def-names-minimum-lines
                                (count-lines start end))
                             (consp sexp)
                             (symbolp (car sexp))
                             (<= 3 (length (symbol-name (car sexp))))
                             (STRING-EQUAL (symbol-name (car sexp)) "DEF"
                                           (kw END1) 3))
                    (delete-region (point) (progn (end-of-line) (point)))
                    (insert (format ";;%s"
                              (def-name (first sexp) (second sexp)))))))
              (handler-case (forward-sexp)
                (scan-error (err)
                  (setq error-point (point))
                  (message "signal 1 %S %S" 'scan-error err)
                  (signal 'scan-error err)) )))
        (error (err)
          (when error-point
            (goto-char error-point)
            (skip-to-next-sexp))
          (message "signal 2 %S %S" (car err) (cdr err))
          (signal (car err) (cdr err)))))))

;;;
;;;---------------------------------------------------------------------





;; ------------------------------------------------------------------------
;; map-sexps
;; ------------------------------------------------------------------------
;; Applies a function on all s-exps from a lisp source file.
;;

(defun skip-comments ()
  "
DO:     Move the point over spaces and lisp comments ( ;...\n or #| ... |# ),
        in the current buffer.
RETURN: (not eof)
"
  (interactive)
  (let* ((data (header-comment-description-for-mode major-mode))
         (comment-regexp (hcd-comment-regexp data))
         (space-or-comment (format "\\(%s\\)\\|\\(%s\\)"
                             "[ \t\n\v\f\r]+"
                             comment-regexp)) )
    (unless data
      (error "Don't know how to handle this major mode %S." major-mode))
    (while (looking-at space-or-comment)
      (goto-char (match-end 0)))
    (< (point) (point-max))))


(defparameter *source-readtable*
  (when (fboundp 'COPY-READTABLE)
    (let ((rt (COPY-READTABLE nil)))
      (SET-DISPATCH-MACRO-CHARACTER (cl-char ?#) (cl-char ?+)
                                    (lambda (stream subchar arg)
                                      `('\#+ ,(READ stream nil nil t)))
                                    rt)
      (SET-DISPATCH-MACRO-CHARACTER (cl-char ?#) (cl-char ?-)
                                    (lambda (stream subchar arg)
                                      `('\#- ,(READ stream nil nil t)))
                                    rt)
      rt)))

(defun cl-sexp-at-point ()
  (let ((*READTABLE* *source-readtable*))
    (READ-FROM-STRING
     (buffer-substring-no-properties
      (progn (forward-sexp  1) (point))
      (progn (forward-sexp -1) (point))))))

;; (MAKE-PATHNAME :type "elc")
;; (MERGE-PATHNAMES (mkpathname nil nil nil nil "elc" nil)
;;                  (mkpathname nil nil nil nil nil nil) nil)
;; (LOAD "/home/pjb/src/public/lisp/common-lisp/source.lisp")
;;
;; (PATHNAME  (mkpathname nil nil nil nil nil nil))
;; (merge-directories nil nil)


(defvar *map-sexps-top-level* nil "Private")
(defvar *map-sexps-deeply*    nil "Private")
(defvar *map-sexps-atoms*     nil "Private")
(defvar *map-sexps-function*  nil "Private")


(defvar *walk-sexps-end-marker* nil)

(defun walk-sexps (fun)
  "
DO:     Recursively scan sexps from (point) in current buffer up to
        the end-of-file or until scan-sexps raises a scan-error.
        Call fun on each sexps and each of their children etc.
fun:    A function (sexp start end)
        sexp:    The sexp parsed from a source file.
        start:   The point starting the sexp.
        end:     The point ending the sexp.
NOTE:   All positions are kept in markers, so modifying the buffer between
        start and end should be OK.
        However  ' or ` are passed as (quote ...) or (backquote ...)
        to the function fun without reparsing the sexp inside them.
        Ie. if you modify such a source, (which can be detected looking at
        the character at start position),  you still get the original sexp.
"
  (let ((quote-stack '())
        (start-stack '())
        (*walk-sexps-end-marker* (make-marker))
        quote-depth
        start-m sexp)
    (skip-comments)
    (while (/= (point) (point-max))
      (when (member major-mode *lisp-modes*)
        ;; gather the quotes:
        (while (looking-at "['`] *")
          ;; quote or backquote
          ;; NOT NEEDED ANYMORE WITH GNU Emacs 21.
          ;; --- (push (set-marker (make-marker) (point)) start-stack)
          ;; --- (push (if (= (char-after) ?') 'quote 'backquote) quote-stack)
          (forward-char 1)
          (skip-comments)))
      ;; get the sexp:
      (setq start-m (set-marker (make-marker) (point)))
      (forward-sexp 1)
      (set-marker *walk-sexps-end-marker* (point))
      ;; (forward-sexp -1)
      ;; (assert (= (marker-position start-m) (point)) t)
      (goto-char (marker-position start-m))
      (setq sexp (cl-sexp-at-point))
      ;; push the quotes on the sexp:
      (setq quote-depth (length quote-stack))
      (while quote-stack
        (setq sexp (cons (pop quote-stack) (list sexp))))
      ;; process the quotes:
      (setq start-stack (nreverse start-stack))
      (dotimes (i quote-depth)
        (message "sexp = %S\nstart = %S\nend = %S\n" sexp (marker-position (car start-stack)) *walk-sexps-end-marker*)
        (funcall fun sexp
                 (marker-position (car start-stack)) *walk-sexps-end-marker*)
        (set-marker (pop start-stack) nil)
        (setq sexp (cadr sexp)))
      ;; process the sexp:
      (message "sexp = %S\nstart = %S\nend = %S\n" sexp  (marker-position start-m) *walk-sexps-end-marker*)
      (funcall fun sexp (marker-position start-m)  *walk-sexps-end-marker*)
      (when *map-sexps-deeply*
        (when (= (char-syntax (char-after (marker-position start-m))) 40) ;; "("
          ;; then the subsexps:
          (goto-char (marker-position start-m))
          (down-list 1)
          (loop
             (condition-case nil
                 (walk-sexps fun)
               (scan-error (return-from nil))))
          (up-list 1)))
      ;; then go to the next sexp:
      (goto-char (marker-position *walk-sexps-end-marker*))
      (set-marker start-m nil)
      (set-marker *walk-sexps-end-marker* nil)))
  nil)



(defun map-sexps-filter (sexp start end)
  (when (and (or *map-sexps-top-level* *map-sexps-deeply*)
             (or *map-sexps-atoms* (not (atom sexp))))
    (funcall *map-sexps-function* sexp start end))
  (setq *map-sexps-top-level* nil))

(defun* new-map-sexps (source-file fun &key (deeply t) (atoms nil))
   "
DO:     Scan all sexps in the source file.
        (skipping spaces and comment between top-level sexps).
        If the deeply flag is set,
        then subsexps are also passed to the function fun, after the sexp,
        else only the top-level sexps are
        If the atoms flags is set
        then atoms are also considered (and passed to the selector).
fun:    A function (sexp start end)
        sexp:    The sexp parsed from a source file.
        start:   The point starting the sexp.
        end:     The point ending the sexp.
KEYS:   :deeply   (boolean,  default nil)
        :atoms    (boolean,  default nil)
NOTE:   Scanning stops as soon as an error is detected by forward-sexp.
RETURN: The list of results from fun.
"
   (error "Not implemented yet."))

(defun* new-map-sexps (source-file fun &key (deeply t) (atoms nil))
   "
DO:     Scan all sexps in the source file.
        (skipping spaces and comment between top-level sexps).
        If the deeply flag is set,
        then subsexps are also passed to the function fun, after the sexp,
        else only the top-level sexps are
        If the atoms flags is set
        then atoms are also considered (and passed to the selector).
fun:    A function (sexp start end)
        sexp:    The sexp parsed from a source file.
        start:   The point starting the sexp.
        end:     The point ending the sexp.
KEYS:   :deeply   (boolean,  default nil)
        :atoms    (boolean,  default nil)
NOTE:   Scanning stops as soon as an error is detected by forward-sexp.
RETURN: The list of results from fun.
"
   (error "Not implemented yet.")
   `(source-text:map-source-file ,fun ,source-file
                                 :deeply ,deeply
                                 :atoms ,atoms))

(defun* map-sexps (source-file fun &key (deeply t) (atoms nil))
  "
DO:     Scan all sexps in the source file.
        (skipping spaces and comment between top-level sexps).
        If the deeply flag is set,
        then subsexps are also passed to the function fun, after the sexp,
        else only the top-level sexps are
        If the atoms flags is set
        then atoms are also considered (and passed to the selector).
fun:    A function (sexp start end)
        sexp:    The sexp parsed from a source file.
        start:   The point starting the sexp.
        end:     The point ending the sexp.
KEYS:   :deeply   (boolean,  default nil)
        :atoms    (boolean,  default nil)
NOTE:   Scanning stops as soon as an error is detected by forward-sexp.
RETURN: The list of results from fun.
"
  (error "Doesn't work, need re-implementation; see new-map-sexps.")
  (message "map-sexps deeply %S  atoms %S" cl-deeply cl-atoms)
  (save-excursion
    (save-restriction
      (let ((old-buffer            (current-buffer))
            (existing-buffer       (buffer-named source-file))
            (*map-sexps-deeply*    cl-deeply)
            (*map-sexps-atoms*     cl-atoms)
            (*map-sexps-top-level* t)
            (*map-sexps-function*  fun)
            last-bosexp)
        (if existing-buffer
            (switch-to-buffer existing-buffer)
            (find-file source-file))
        (widen)
        (goto-char (point-min))
        (while (< (point) (point-max))
          (setq *map-sexps-top-level* t)
          (walk-sexps (function map-sexps-filter)))
        (if existing-buffer
            (switch-to-buffer old-buffer)
            (kill-buffer (current-buffer)))))))


(defun old-old-map-sexps (source-file fun)
  "
DO:     Scan all top-level sexps in the source file.
        (skipping spaces and comment between top-level sexps).
fun:    A function (sexp start end)
        sexp:    The sexp parsed from a source file.
        start:   The point starting the sexp.
        end:     The point ending the sexp.
:deeply
NOTE:   Scanning stops as soon as an error is detected by forward-sexp.
RETURN: The list of results from fun.
"
  (save-excursion
    (save-restriction
      (let ((old-buffer (current-buffer))
            (existing-buffer (buffer-named source-file))
            last-bosexp)
        (if existing-buffer
            (switch-to-buffer existing-buffer)
            (find-file source-file))
        (widen)
        (goto-char (point-max))
        (forward-sexp -1)
        (setq last-bosexp (point))
        (goto-char (point-min))
        (prog1
            (loop with eof  = (gensym)
               while (<= (point) last-bosexp)
               for end   = (progn (forward-sexp 1)  (point))
               for start = (progn (forward-sexp -1) (point))
               for sexp  = (condition-case nil (sexp-at-point) (error eof))
               until (eq eof sexp)
               collect (funcall fun sexp start end) into map-sexps-result
               do (condition-case nil
                      (forward-sexp 1)
                    (error               (goto-char (point-max)))
                    (wrong-type-argument (goto-char (point-max))))
               finally (unless existing-buffer (kill-buffer source-file))
               finally return (nreverse map-sexps-result))
          (switch-to-buffer old-buffer))))))


(defun count-sexps ()
  (interactive)
  (save-excursion
    (goto-char (point-min))
    (let ((place (point))
          (count 0))
      (forward-sexp)
      (while (< place (point))
        (incf count)
        (setq place (point))
        (forward-sexp))
      (message "There are %d top-level sexps." count)
      count))) ;;count-sexps

;; ------------------------------------------------------------------------
;; get-sexps
;; ------------------------------------------------------------------------
;; Read all s-exps from a lisp source file. Can filter s-exps by a given
;; selector function.
;;

(defun get-sexps (source-file &key (selector (function (lambda (s) t)))
                                (deeply   nil)
                                (atoms    nil))
  "
KEYS:    :selector (function: sexp --> boolean, default: (lambda (s) t))
         :deeply   (boolean,  default nil)
         :atoms    (boolean,  default nil)
DO:      Scan all sexp in the source-file.
         A selector function may indicate which sexp must be collected.
         If the deeply flag is set,
         then if a sexp is not selected then sub-sexp are scanned and tested.
         If the atoms flags is set
         then atoms are also considered (and passed to the selector).
NOTE:    Scanning stops as soon as an error is detected by forward-sexp.
RETURN:  A list of selected sexp.
"
  (save-excursion
    (let ((get-sexps-result '()))
      (map-sexps
       source-file
       (lambda (sexp start end)
         (when (funcall selector sexp)
           (push sexp get-sexps-result)))
       :deeply deeply :atoms atoms)
      (nreverse get-sexps-result))))


;;; (show
;;;  (sort
;;;   (let ((histo (make-hash-table)) (max-lisp-eval-depth 1000))
;;;     (mapc (lambda (path)
;;;             (message path)
;;;             (mapcar (lambda (sexp) (incf (gethash (depth sexp) histo 0)))
;;;                     (get-sexps path)))
;;;           (directory "~/src/common/lisp/emacs/[a-z]*.el"))
;;;     (let ((result '()))
;;;       (maphash (lambda (deep value) (push (cons deep value) result)) histo)
;;;       result))
;;;   (lambda (a b) (< (car a) (car b))))
;;;  )
;;;
;;; ==> ((1 . 325) (2 . 329) (3 . 231) (4 . 163) (5 . 138) (6 . 158) (7 .
;;; 102) (8 . 94) (9 . 63) (10 . 40) (11 . 16) (12 . 20) (13 . 9) (14 . 4)
;;; (15 . 5) (16 . 4) (17 . 2) (19 . 2) (23 . 1))



;; (defun old-get-sexps (source-file &rest cl-keys)
;;   "
;; KEYS:    :selector (a function, default: true)
;;          :deeply   (a boolean,  default nil)
;;          :atoms    (a boolean,  default nil)
;; DO:      Scan all sexp in the source-file.
;;          A selector function (sexp->bool) may indicate which sexp must
;;          be collected.  If the deeply flag is set, then if a sexp is not
;;          selected then sub-sexp are scanned and tested.  If the atoms flags
;;          is set then atoms are also considered (and passed to the selector).
;; NOTE:    Scanning stops as soon as an error is detected by forward-sexp.
;; RETURN:  A list of selected sexp.
;; "
;;   (cl-parsing-keywords ((:selector (function identity))
;;                         (:deeply   nil)
;;                         (:atoms    nil)) nil
;;     (save-excursion
;;       (save-restriction
;;         (let ((existing-buffer (buffer-named source-file)))
;;           (if existing-buffer
;;               (set-buffer existing-buffer)
;;               (find-file source-file))
;;           (widen)
;;           (goto-char (point-min))
;;           (loop with result = nil
;;              while (/= (point) (point-max))
;;              for sexp = (condition-case nil (sexp-at-point) (error nil))
;;              do (flet ((deeply-select
;;                            (sexp)
;;                          (if (atom sexp)
;;                              (if (and cl-atoms (funcall cl-selector sexp))
;;                                  (push sexp result))
;;                              (let (subsexp)
;;                                (while sexp
;;                                  (if (consp sexp)
;;                                      (setq subsexp (car sexp)
;;                                            sexp    (cdr sexp))
;;                                      (setq subsexp sexp
;;                                            sexp    nil))
;;                                  (cond
;;                                    ((atom subsexp)
;;                                     (if (and cl-atoms
;;                                              (funcall cl-selector subsexp))
;;                                         (push subsexp result)))
;;                                    ((funcall cl-selector subsexp)
;;                                     (push subsexp result))
;;                                    (cl-deeply
;;                                     (deeply-select subsexp))))))))
;;                   (if (atom sexp)
;;                       (if (and cl-atoms (funcall cl-selector sexp))
;;                           (push sexp result))
;;                       (cond
;;                         ((funcall cl-selector sexp)
;;                          (push sexp result))
;;                         (cl-deeply
;;                          (deeply-select sexp)))))
;;              (condition-case nil
;;                  (forward-sexp 1)
;;                (error (goto-char (point-max)))
;;                (wrong-type-argument (goto-char (point-max))))
;;              finally (unless existing-buffer (kill-buffer source-file))
;;              finally return (nreverse result))
;;           ))))
;;   ) ;;old-get-sexps



;; ------------------------------------------------------------------------
;; replace-sexps
;; ------------------------------------------------------------------------
;; Applies a transformer function to all s-exps from a lisp source file,
;; replacing them by the result of this transformer function in the source file.
;;

;;; TODO: Use CLISP to pretty print, or find an elisp pretty printer.
;;; "(LET ((*PRINT-READABLY* T))
;;;    (SETF (READTABLE-CASE *READTABLE*) :PRESERVE)
;;;    (WRITE (QUOTE ~S )))"


(defun* replace-sexps (source-file transformer &key (deeply nil) (atoms nil))
  "
DO:             Scan all sexp in the source-file.
                Each sexps is given to the transformer function whose result
                replaces the original sexps in the source-file.
                If the deeply flag is set, then the transformer is applied
                recursively to the sub-sexps.
                If the atoms flags is set then atoms are also considered
                (and passed to the transformer).
KEYS:           :deeply    (a boolean,  default nil)
                :atoms     (a boolean,  default nil)
transformer:    A function sexp --> sexp.
                If returing its argument (eq),
                then no replacement takes place (the comments and formating
                is then preserved.  Otherwise the source of the sexp is
                replaced by the returned sexp.
NOTE:           For now, no pretty-printing is done.
"
  (map-sexps
   source-file
   (lambda (sexp start end)
     (let ((replacement (funcall transformer sexp)))
       (unless (eq replacement sexp)
         (delete-region start end)
         (insert (let ((print-escape-newlines t)
                       (print-level nil)
                       (print-circle nil)
                       (print-length nil)) (format "%S" replacement)))
         (set-marker end (point)))))
   :deeply deeply :atoms atoms)
  nil)



;; ------------------------------------------------------------------------
;; clean-if*
;; ------------------------------------------------------------------------
;; Replace if* by if, when, unless or cond.
;;

(defun escape-sharp ()
  (interactive)
  (save-excursion
    (goto-char (point-min))
    (while
        (re-search-forward "\\(#\\([^A-Za-z0-9()\\\\ ]\\|\\\\.\\)*\\)" nil t)
      (let* ((match (match-string 1))
             (escap (base64-encode-string match t)))
        (replace-match (format "|ESCAPED-SHARP:%s|" escap) t t)))))


;;; (let ((s "toto #.\\( titi"))
;;; (string-match  "\\(#\\(\\\\.\\|[^A-Za-z0-9()\\\\ ]\\)*\\)" s)
;;; (match-string 1 s))



(defun unescape-sharp ()
  (interactive)
  (save-excursion
    (goto-char (point-min))
    (while (re-search-forward
            "\\(|ESCAPED-SHARP:\\([A-Za-z0-9+/=*]*\\)|\\)" nil t)
      (let* ((escap (match-string 2))
             (match (base64-decode-string escap)))
        (replace-match match t t nil 1)))))


(defun clean-if* ()
  (interactive "*")
  (escape-sharp)
  (unwind-protect
       (replace-sexps
        (buffer-file-name)
        (lambda (sexp)
          (message "sexp=%S" sexp )
          (let ((backquoted (eql '\` (car sexp)))
                (original-sexp sexp))
            (when backquoted (setq sexp (second sexp)))
            (if (and (consp sexp) (symbolp (car sexp))
                     (STRING-EQUAL 'IF* (car sexp)))
                (do* ((subs (cons 'ELSEIF (cdr sexp)))
                      (clauses '())
                      (condition)
                      (statements)
                      (token))
                     ((null subs)
                      (let ((result
                             (progn ;;generate the new sexp
                               (setq clauses (nreverse clauses))
                               (cond
                                 ((and (= 1 (length clauses))
                                       (every
                                        (lambda (clause) (not (null (cdr clause))))
                                        ;; clause = (cons condition statements)
                                        clauses)) ;; a when
                                  `(when ,(car (first clauses))
                                     ,@(cdr (first clauses))))
                                 ((or (= 1 (length clauses))
                                      (< 2 (length clauses))
                                      (not (eq t (car (second clauses))))) ;; a cond
                                  `(cond ,@clauses))
                                 (t ;; a if
                                  `(if ,(car (first clauses))
                                       ,(if (= 1 (length (cdr (first clauses))))
                                            (cadr (first clauses))
                                            `(progn ,@(cdr (first clauses))))
                                       ,(if (= 1 (length (cdr (second clauses))))
                                            (cadr (second clauses))
                                            `(progn ,@(cdr (second clauses)))))))) ))
                        (message "sexp=%S\nresult=%S" sexp result)
                        (if backquoted (list '\` result) result)))
                  ;; read the condition:
                  (setq token (pop subs))
                  (cond
                    ((not (symbolp token))
                     (error "unexpected token %S in %S" token sexp))
                    ((null subs)
                     (error "unexpected end of sexp in %S" sexp))
                    ((STRING-EQUAL token 'ELSEIF)
                     (setq condition (pop subs))
                     (unless (or (STRING-EQUAL (car subs) 'THEN)
                                 (STRING-EQUAL (car subs) 'THENRET))
                       (error "missing THEN after condition in %S" sexp))
                     (pop subs))
                    ((STRING-EQUAL token 'ELSE)
                     (setq condition t))
                    (t
                     (error "unexpected token %S in %S" token sexp)))
                  ;; read the statements:
                  (do () ((or (null subs)
                              (and (consp subs) (symbolp (car subs))
                                   (member* (car subs) '(ELSEIF ELSE)
                                             :test (function STRING-EQUAL)))))
                    (push (pop subs) statements))
                  (push (cons condition (nreverse statements)) clauses)
                  (setq condition nil statements nil))
                original-sexp)))
        :deeply t :atoms nil)
    (unescape-sharp)))


;; ------------------------------------------------------------------------
;; karnaugh & karnaugh-solve
;; ------------------------------------------------------------------------
;; karnaugh: Displays a truth table either to be edited of with computed actions.
;; karnaugh-solve: Generate functions for the actions given as a thuth table.
;;


(defun integer-to-bool-list (n &key length)
  "
PRE:     n>=0
RETURN:  The list of the binary digits of n, from the least significant.
"
  (unless (integerp n)
    (error "Argument must be integer, not %S." n))
  (when (< n 0)
    (setq n (abs n)))
  (if length
      (loop for m = n then (/ m 2)
         for i from 0 below length
         collect (/= 0 (mod m 2)) into digits
         finally return digits)
      (loop for m = n then (/ m 2)
         while (< 0 m)
         collect (/= 0 (mod m 2)) into digits
         finally return digits)))


;;; (insert (karnaugh '(a b c d e)
;;;                 '(( do-1 . (lambda (a b c d e) (and a (or b c))))
;;;                   ( do-2 . (lambda (a b c d e) (or (not a) b)))
;;;                   ( do-3 . (lambda (a b c d e) (and (not a) b (not c)))))
;;;                 '(FAUX . VRAI)))

;;; (show
;;; (karnaugh-solve '(a b) '(carry sum)
;;;                           '(( 0 0  0 0)
;;;                             ( 0 1  0 1)
;;;                             ( 1 0  0 1)
;;;                             ( 1 1  1 0))
;;;                           '( 0 . 1))
;;; )

;;; (insert (karnaugh '(a b c)
;;;                 '((action . (lambda (a b c)
;;;                               (or (and a (and b (not c)))
;;;                                   (or (and (not a) (and b (not c)))
;;;                                       (or (and (not a) c)
;;;                                           (and (not b) c)))))))
;;;                 '(F . T)))


(defun karnaugh-solve (conditions actions table &optional bool-vals action-vals)
  "
DO:         Finds an expression for each actions,
            in function of the conditions, given the truth table.
conditions: A list of symbols or symbol names.
            Since the conditions are used as argument name for the expressions,
            it may not contain reserved symbols such as t.
actions:    A list of symbols or symbol names.
table:      Each line of the table is a list
            with the truth value of all conditions
            followed by the truth value of all actions.
            Missing combinations are deemed false for all actions.
bool-vals   Specifies the atoms used as truth values
            for the conditions. Default is (NO . YES).
action-vals Specifies the atoms used as truth values
            for the actions. Default is bool-vals.
PRE:        for each line in table,
               (= (length line) (+ (length conditions) (length actions))).
RETURN:     A list of cons (action . (lambda (conditions) expression)).
EXAMPLE:    (karnaugh-solve '(a b) '(carry sum)
                          '(( 0 0  0 0)
                            ( 0 1  0 1)
                            ( 1 0  0 1)
                            ( 1 1  1 0))
                          '( 0 . 1))
            ==> ((carry . (lambda (a b) (and a b)))
                 (sum   . (lambda (a b) (or (and a (not b)) (and (not a) b)))))
NOTE:       Current implementation does not simplify the expressions.
SEE ALSO:   `karnaugh' and `gentable'.
"
  (when (null bool-vals)
    (setq bool-vals '(NO . YES)))
  (when (null action-vals)
    (setq action-vals bool-vals))
  (setq conditions (mapcar (lambda (item)
                             (if (stringp item)
                                 (intern item) item)) conditions))
  (setq actions (mapcar (lambda (item)
                          (if (stringp item)
                              (intern item) item)) actions))
  (let* ((c-no    (car bool-vals))
         (c-yes   (cdr bool-vals))
         (a-no    (car action-vals))
         (a-yes   (cdr action-vals))
         (i       (length conditions))
         (act-ind (mapcar (lambda (action)
                            (prog1 (list action i) (setq i (1+ i))))
                          actions)))
    (mapc (lambda (line)
            (mapc (lambda (action)
                    (if (eq a-yes (nth (cadr action) line))
                        (nconc action (list line))))
                  act-ind))
          table)
    (mapcar
     (lambda (action)
       (cons (car action)
             (list 'lambda conditions
                   (cons 'or
                         (mapcar
                          (lambda (line)
                            (cons 'and
                                  (mapcar*
                                   (lambda (cond-name cond-val)
                                     (if (eq c-yes cond-val)
                                         cond-name
                                         (list 'not cond-name)))
                                   conditions line)))
                          (cddr action))))))
     act-ind)))



(defun karnaugh (conditions actions &optional bool-vals action-vals)
  "
DO:           Generates a truth table for all combinations of the conditions.
conditions:   A list of strings or symbols.
actions:      A list of actions. An action can be a string or a symbol,
              or a cons whose car is a string or a symbol (the name of the
              action) and whose cdr is a lambda taking as arguments boolean
              values for the conditions, and returning a boolean value for
              the action.
              If such a function for an action is given, it's used to
              compute the cases when the action must be run.
bool-vals     A cons of symbol or string (false . true) used as values for the
              conditions.
action-vals   A cons of symbol or string (false . true) used as values for the
              actions.
SEE ALSO:     `karnaugh-solve' and `gentable'.
"
  (when (null bool-vals)
    (setq bool-vals '("NO" . "YES")))
  (when (null action-vals)
    (setq action-vals '("·" . "×")))
  (when (symbolp (car bool-vals))
    (setf (car bool-vals) (symbol-name (car bool-vals))))
  (when (symbolp (cdr bool-vals))
    (setf (cdr bool-vals) (symbol-name (cdr bool-vals))))
  (when (< 8 (length conditions))
    (error "Too many conditions."))
  (setq conditions (mapcar (lambda (item)
                             (if (stringp item) item (format "%s" item)))
                           conditions))
  (let* ((size-bool-vals
          (max (length (car bool-vals)) (length (cdr bool-vals))))
         (c-count (length conditions))
         (a-count (length actions))
         (s-count (+ c-count a-count))
         (a-title
          (mapcar (lambda (item)
                    (cond
                      ((stringp item) item)
                      ((symbolp item) (symbol-name item))
                      ((consp item)
                       (cond
                         ((stringp (car item)) (car item))
                         ((symbolp (car item)) (symbol-name (car item)))
                         (t (error "Invalid action %S." item)))
                       )
                      (t (error "Invalid action %S." item))))
                  actions))
         (a-indic (make-array (list a-count)
                              :initial-contents (mapcar (lambda (item)
                                                          (if (consp item)
                                                              (cdr item) nil))
                                                        actions)))
         (a-complex (loop for i across a-indic until i finally return i))
         ;; whether a-indic contains at least one indicator.
         (sizes
          (let ((sizes (make-array (list s-count))))
            (loop for cnd in conditions
               for i = 0 then (1+ i)
               do (setf (aref sizes i) (max size-bool-vals (length cnd))))
            (loop for act in a-title
               for i = c-count then (1+ i)
               do (setf (aref sizes i) (max 3 (length act))))
            sizes))
         (line-length
          (loop for i from 0 below s-count
             sum  (+ 3 (aref sizes i)) into l
             finally return (1+ l)))
         (line
          (loop with line = (make-string line-length (character "-"))
             for i from 0 below s-count
             for position = (+ (aref sizes i) 3)
             then (+ position  (aref sizes i) 3)
             ;;do (printf "sizes=%S i=%d p=%d\n" sizes i position)
             do      (setf (aref line position) (character "+"))
             finally (setf (aref line 0) (character "+"))
             finally return line))
         (act-part
          (if a-complex
              nil
              (loop for i from c-count below s-count
                 collect (concatenate
                             'string
                           (make-string (+ 2 (aref sizes i)) (character " "))
                           "|")
                 into parts
                 finally return (apply 'concatenate 'string parts))))
         (new-line (make-string 1 (character 10))))
    ;;(printf "line-length=%d\n" line-length)
    (concatenate 'string
      line new-line
      "|"
      (loop for item in conditions
         for i from 0 below c-count
         collect (concatenate 'string
                   " " (string-pad item (aref sizes i) :justification :center) " |")
         into title
         finally return (apply 'concatenate 'string title))

      (loop for item in a-title
         for i from c-count below s-count
         collect (concatenate 'string
                   " " (string-pad item (aref sizes i) :justification :center) " |")
         into title
         finally return  (apply 'concatenate 'string title))
      new-line
      line new-line
      (loop for i from (1- (expt 2 c-count)) downto 0
         for conditions = (nreverse (integer-to-bool-list i :length c-count))
         collect (concatenate 'string
                   ;; conditions
                   (loop
                      for k from 0 below c-count
                      for c in conditions
                      for l = (+ 3 (aref sizes k))
                      for s = (string-pad
                               (if c (cdr bool-vals) (car bool-vals))
                               l :justification :center)
                      do (setf (char s (1- l)) (character "|"))
                      collect s into items
                      finally return (apply 'concatenate 'string "|" items))
                   ;; actions
                   (if act-part
                       act-part
                       (loop
                          for k from 0 below a-count
                          for l = (+ 3 (aref sizes (+ c-count k)))
                          for f = (aref a-indic k)
                          for s = (string-pad
                                   (if f (if (apply f conditions)
                                             (cdr action-vals)
                                             (car action-vals)) "")
                                   l :justification :center)
                          do (setf (char s (1- l)) (character "|"))
                          collect s into items
                          finally return (apply 'concatenate 'string items)))
                   new-line) into lines
         finally return (apply 'concatenate 'string lines))
      line new-line)))




(defun combine (&rest args)
  "
RETURN:  (elt args 0) x (elt args 1) x ... x (elt args (1- (length args)))
         = the set of tuples built taking one item in order from each list
           in args.
EXAMPLE: (COMBINE '(WWW FTP) '(EXA) '(COM ORG)))
           --> ((WWW EXA COM) (WWW EXA ORG) (FTP EXA COM) (FTP EXA ORG))
"
  (cond
    ((null args) '(nil))
    ((consp (car args))
     (mapcan (lambda (item) (apply (function combine) item (cdr args)))
             (car args)))
    (t
     (mapcan (lambda (rest) (list (cons (car args) rest)))
             (apply (function combine) (cdr args))))))


(defun compute-column-widths (rows)
  (if (or (null rows) (every (function null) rows))
      nil
      (cons (reduce (function max)
                    (mapcar (function length)
                            (mapcar (function car) rows)))
            (compute-column-widths (mapcar (function cdr) rows)))))


(defmacro with-standard-output-to-string (&rest body)
  `(with-output-to-string ,@body))

;;#+COMMON-LISP
;;(defmacro with-standard-output-to-string (&body body)
;;  `(with-output-to-string (*standard-output*) ,@body))


(defun gentable (conditions actions)
  "Needs a better name.
  (gentable '((input  :stream :terminal nil)
              (output :stream :terminal nil)
              (wait   t nil))
            '((use (lambda (i o w) (and w (or (eq i :stream) (eq o :stream)))))
             result))
"
  (setf conditions
        (delete* nil (mapcar
                     (lambda (c) (if (atom c) (cons c '(no yes)) c))
                     conditions)
                :key (function cdr)))
  (setf actions
        (delete* nil (mapcar
                     (lambda (a) (if (atom a) (list a (lambda (&rest args) "")) a))
                     actions)
                :key (function cdr)))
  (let* ((title
           (mapcar (lambda (x) (format "%s" x)) ;(format "%s" x))
                   (nconc (mapcar (function first) conditions)
                          (mapcar (function first) actions))))
         (rows
          (mapcar
           (lambda (conditions)
             (nconc (mapcar (lambda (x) (format "%s" x)) conditions)
                    (mapcar
                     (lambda (action)
                       (format "%s"
                         (apply (cond
                                  ((symbolp (second action))
                                   (eval `(function ,(second action))))
                                  ((and (consp (second action))
                                        (eq 'lambda (first (second action))))
                                   (eval (second action)))
                                  ((functionp (second action))
                                   (second action))
                                  (t (error "What is it %S" action)))
                                conditions)))
                     actions)))
           (apply (function combine) (mapcar (function cdr) conditions))))
         (widths (compute-column-widths (cons title rows)))
         (line (with-standard-output-to-string
                   (loop initially (princ "+")
                      for w in  widths
                      do (progn
                           (princ (make-string (+ 2 w) ?-))
                           (princ "+"))))))
    (with-standard-output-to-string
        (flet ((print-row (row)
                 (loop
                    initially (princ "|")
                    for item in row
                    for width in widths
                    do (progn
                         (princ (string-pad item (+ 2 width)
                                            :justification :center))
                         (princ "|")))
                 (terpri)))
          (loop
             initially (progn
                         (princ line) (terpri)
                         (print-row title)
                         (princ line) (terpri))
             for row in rows
             do (print-row row) (princ line)  (terpri)
             finally (terpri))))))



;; ------------------------------------------------------------------------
;; SOURCE HEADER
;; ------------------------------------------------------------------------
;; Inserts and Edit the comment at the top of source files.
;; See the beginning of this file to have an example of such an header!
;;



;; ------------------------------------------------------------------------
;; Extract, format, and update copyright lines.
;; ------------------------------------------------------------------------

(defun pjb-copyright-regexp (hcd)
  (let* ((comment-format (or (hcd-header-comment-format hcd) "%s"))
         (pattern  "Copyright ")
         (base-re  (format "^%s" (regexp-quote (format comment-format pattern))))
         (pos      (+ (search pattern base-re) (length pattern)))
         (left-re  (subseq base-re 0 pos))
         (right-re (subseq base-re pos)))
    (format "%s *\\(.*?\\) +\\([0-9]+\\)\\(\\( +-\\|,\\) +\\([0-9]+\\)\\)*\\( +-\\|,\\) +\\([0-9]+\\).*%s"
            left-re right-re)))


(defun regexp-results (match string)
  (let ((data (match-data t)))
    (when data
      (coerce
       (loop
          for (beg end) on data by (function cddr)
          while (or (null beg) (integerp beg))
          collect (list beg end (when (and beg end) (subseq string (1- beg) (1- end)))))
       'vector))))


(defun pjb-process-copyrights (hcd fun)
  "
Call the function `fun' with  the beginning and end points of each
copyright line, and a list containing the copyright owner, the first
and last year of the copyright.
"
  (let ((re   (pjb-copyright-regexp hcd))
        (text (buffer-substring-no-properties (point-min) (point-max))))
    (save-excursion
      (goto-char (point-min))
      (with-marker (end (point-max))
       (loop
          with next = (make-marker)
          while (re-search-forward re end t)
          do (let ((res (regexp-results t text)))
               (set-marker next (1+ (second (aref res 0))))
               (funcall fun
                        (first  (aref res 0))
                        (second (aref res 0))
                        (list (third (aref res 1))
                              (nth-value 0 (cl:parse-integer (third (aref res 2))))
                              (nth-value 0 (cl:parse-integer (third (aref res 7))))))
               (goto-char (1- (marker-position next)))))))))


(defun pjb-extract-copyrights (hcd)
  (let ((pjb-extract-copyrights/result '()))
    (pjb-process-copyrights hcd
                            (lambda (start end copyright)
                              (declare (ignore start end))
                              (push copyright pjb-extract-copyrights/result)))
    (nreverse pjb-extract-copyrights/result)))

;; (pjb-extract-copyrights  (header-comment-description-for-mode major-mode))

(defun pjb-format-copyright (hcd author first-year last-year)
  "A string containing a copyright line in a comment."
  (let ((comment-format (hcd-header-comment-format hcd)))
   (format comment-format
           (format "Copyright %s %04d - %04d"
                   author first-year last-year))))

(defun pjb-update-copyright ()
  "Update the copyright lines with the current year in the current buffer."
  (interactive)
  (let ((current-year  (third (calendar-current-date)))
        (hcd (header-comment-description-for-mode major-mode)))
    (pjb-process-copyrights
     hcd
     (lambda (start end copyright)
       (destructuring-bind (owner first-year last-year) copyright
         (declare (ignore last-year))
         (when (every (lambda (name) (search name owner))
                      (remove-if (lambda (word)
                                   (and (<= (length word) 2)
                                        (char= (aref word 1) (character "."))))
                                 (split-string  user-full-name " ")))
           (delete-region start end)
           (insert (pjb-format-copyright hcd owner first-year current-year))))))))


(defvar *source-extensions*
  '(".lisp" ".cl" ".asd" ".el"
    "Makefile"
    ".c" ".cc" ".cpp" ".c++"
    ".h" ".hh" ".hpp" ".h++"
    ".m" ".mm"))

(defvar *ignorable-directories*
  '("_darcs" ".darcsrepo" ".svn" ".hg" ".git" "CVS" "RCS" "MT" "SCCS"
    ".tmp_versions" "{arch}" ".arch-ids"
    "BitKeeper" "ChangeSet" "autom4te.cache"))

(defun process-all-files-in-directory (directory good-files-re what how)
  "Visits each file in the given `directory' and subdirectories ecluding `*ingorable-directories*' whose path matches `good-file-re' and calls the `how' thunk in the buffer of the visited file, displaying the `what' message."
  (let ((bad-directories-re (format "/%s$" (regexp-opt *ignorable-directories*))))
    (message "%s in %S" what directory)
    (with-files (path directory :recursive t :exceptions (lambda (path) (string-match bad-directories-re path)))
      (when (string-match good-files-re path)
        (with-file (path :save t :kill t :literal nil)
          (message "%s of file %S" what path)
          (funcall how))))))

(defun pjb-update-copyright-directory (&optional directory)
  "Updates the copyright in all source files `*source-extensions*' in the `directory'."
  (interactive "DDirectory: ")
  (process-all-files-in-directory (or directory default-directory)
                                  (format "\\(%s\\)$" (regexp-opt *source-extensions*))
                                  "Updating copyright"
                                  (function pjb-update-copyright)))

(defun pjb-bump-asdf-version (&optional vf)
  "Bump the version in the asdf systems in the current buffer.
vf= 1 => increment the minor.
vf= 4 => increment the major.
vf=16 => increment the version.
"
  (interactive "p")
  (let* ((vf    (or vf 1))
         (field (case vf
                  ((1)  3)
                  ((4)  2)
                  ((16) 1)
                  (otherwse
                   (error "Invalid version field parameter %d, should be (member 1 4 16)"
                          vf))))
         (fmt  (case field
                 ((1) "%d.0.0")
                 ((2)   "%d.0")
                 ((3)     "%d"))))
    (goto-char (point-min))
    (while (re-search-forward  ":version +\"\\([0-9]+\\)\\.\\([0-9]+\\)\\.\\([0-9]+\\)\"" (point-max) t)
      (replace-region (match-beginning field) (match-end 3)
                      (format fmt (1+ (parse-integer (match-string field))))))))

(defun pjb-bump-asdf-version-in-directory (vf &optional directory)
  "Bumps the ASD system version in all asd files in the `directory' (recursively).
vf= 1 => increment the minor.
vf= 4 => increment the major.
vf=16 => increment the version.
"
  (interactive "p\nDDirectory: ")
  (process-all-files-in-directory (or directory default-directory)
                                  "\\(\\.asd\\)$"
                                  "Bumping version of asd systems"
                                  (lambda ()
                                    (pjb-bump-asdf-version vf))))



;; ------------------------------------------------------------------------
;; pjb-add-change-log-entry
;; ------------------------------------------------------------------------
;; Inserts a change log entry in the current source,
;; and in the GNU-style ChangeLog file.

(defvar *pjb-sources-initials* nil
  "Initials of the developer, to be inserted in MODIFICATIONS log entries
by pjb-add-change-log-entry.")


(defun hcd-justify-text (first-margin other-margin text)
  (let ((flen (length first-margin))
        (olen (length other-margin))
        (lines (split-string text "[\n\v\r\f]+")) )
    (cond
      ((null lines)          first-margin)
      ((= (length lines) 1) (concatenate 'string first-margin (car lines)))
      (t (when (< olen flen)
           (setq other-margin
                 (concatenate 'string other-margin
                              (make-string (- flen olen) (character " ")))))
         (apply (function concatenate)
                'string
                first-margin
                (list-insert-separator
                 lines  (concatenate 'string "\n" other-margin)))))))


(defun pjb-add-change-log-entry (&optional log-entry)
  (interactive "*")
  (widen)
  (goto-char (point-min))
  (let* ((data (header-comment-description-for-mode major-mode))
         (comment-format (hcd-header-comment-format data))
         (entry-head (format "%s <%s> "
                       (funcall add-log-time-format)
                       (or *pjb-sources-initials*
                           (user-real-login-name)
                           add-log-full-name))))
    (unless data
      (error "Don't know how to handle this major mode %S." major-mode))
    (unless (re-search-forward "\\<MODIFICATIONS\\>" nil t)
      (error "Can't find the MODIFICATIONS section. Please add an header first."))
    (goto-char (match-end 0))
    (insert "\n")
    (if log-entry
        (dolist
            (line
              (mapcar (lambda (line) (format comment-format line))
                      (split-string
                       (hcd-justify-text entry-head entry-head log-entry)
                       "\n")))
          (insert line))
        (insert (format comment-format entry-head)))))


(defun pjb-reformat-change-log-dates ()
  (interactive "*")
  (save-excursion
    (save-restriction
      (widen)
      (goto-char (point-min))
      (let* ((data (header-comment-description-for-mode major-mode))
             (comment-format (hcd-header-comment-format data))
             start end)
        (unless data
          (error "Don't know how to handle this major mode %S." major-mode))
        (unless (re-search-forward "\\<MODIFICATIONS\\>" nil t)
          (error "Can't find the MODIFICATIONS section. Please add an header first."))
        (setq start (match-end 0))
        (unless (re-search-forward "\\<BUGS\\|LEGAL\\>" nil t)
          (error "Can't find the LEGAL section. Please add an header first."))
        (setq end (match-beginning 0))
        (goto-char start)
        (while (re-search-forward "\\<\\([0-9][0-9]\\)/\\([0-9][0-9]\\)/\\([0-9][0-9][0-9][0-9]\\)\\> <" end t)
          (replace-match
           (format "%s-%s-%s <"
             (match-string 3) (match-string 2) (match-string 1))))
        (goto-char start)
        (while (re-search-forward "\\<\\([0-9][0-9][0-9][0-9]\\)/\\([0-9][0-9]\\)/\\([0-9][0-9]\\)\\> <" end t)
          (replace-match
           (format "%s-%s-%s <"
             (match-string 1) (match-string 2) (match-string 3))))))))


(defmacro format-insert (&rest form-args)
  `(progn ,@(mapcar (lambda (form-arg) `(insert (format ,@form-arg))) form-args)))


(defun pjb-insert-package (pname)
  (interactive "sPackage name: ")
  (setq pname (string-upcase pname))
  (let ((nick (subseq pname (1+ (or (position (character ".")
                                              pname :from-end t) -1)))))
    (format-insert
     ("(DEFINE-PACKAGE \"%s\"\n" pname)
     ("  ;;(:NICKNAMES \"%s\")\n" nick)
     ("  (:DOCUMENTATION \"\")\n")
     ("  (:FROM \"COMMON-LISP\"                           :IMPORT :ALL)\n")
     ("  (:FROM \"COM.INFORMATIMAGO.COMMON-LISP.UTILITY\" :IMPORT :ALL)\n")
     ("  (:FROM \"COM.INFORMATIMAGO.COMMON-LISP.STRING\"  :IMPORT :ALL)\n")
     ("  (:FROM \"COM.INFORMATIMAGO.COMMON-LISP.LIST\"    :IMPORT :ALL)\n")
     ("  (:EXPORT ))\n\n"))))


(defun pjb-wrap-in-eval-when (start end)
  (interactive "r")
  (let ((b (make-marker))
          (e (make-marker)))
      (set-marker b  (min start end))
      (set-marker e  (max start end))
      (goto-char b)
      (insert "(eval-when (:compile-toplevel :load-toplevel :execute)\n")
      (goto-char e)
      (insert ");;eval-when")
      (indent-region b (1+ e))
      (goto-char b)))

;; ------------------------------------------------------------------------
;; pjb-add-header
;; ------------------------------------------------------------------------
;; Insert a fresh header at the beginning of the buffer.
;;

(defun pjb-fill-a-line (format length)
  (do* ((stars (make-string length ?*) (subseq stars 1))
        (line  (format format stars) (format format stars)))
       ((<= (length line) length) line)))



(defparameter pjb-sources-licenses
  ;; http://spdx.org/licenses/
  ;; SPDX-License-Identifier: BSD-2-Clause
  '(("GPL2"
     t
     "This program is free software; you can redistribute it and/or"
     "modify it under the terms of the GNU General Public License"
     "as published by the Free Software Foundation; either version"
     "2 of the License, or (at your option) any later version."
     ""
     "This program is distributed in the hope that it will be"
     "useful, but WITHOUT ANY WARRANTY; without even the implied"
     "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR"
     "PURPOSE.  See the GNU General Public License for more details."
     ""
     "You should have received a copy of the GNU General Public"
     "License along with this program; if not, write to the Free"
     "Software Foundation, Inc., 59 Temple Place, Suite 330,"
     "Boston, MA 02111-1307 USA")

    ("LGPL2"
     t
     "This library is free software; you can redistribute it and/or"
     "modify it under the terms of the GNU Lesser General Public"
     "License as published by the Free Software Foundation; either"
     "version 2 of the License, or (at your option) any later"
     "version."
     ""
     "This library is distributed in the hope that it will be"
     "useful, but WITHOUT ANY WARRANTY; without even the implied"
     "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR"
     "PURPOSE.  See the GNU Lesser General Public License for more"
     "details."
     ""
     "You should have received a copy of the GNU Lesser General"
     "Public License along with this library; if not, write to the"
     "Free Software Foundation, Inc., 59 Temple Place, Suite 330,"
     "Boston, MA 02111-1307 USA")

    ("LLGPL"
     t

     "This library is licenced under the Lisp Lesser General Public"
     "License."
     ""
     "This library is free software; you can redistribute it and/or"
     "modify it under the terms of the GNU Lesser General Public"
     "License as published by the Free Software Foundation; either"
     "version 2 of the License, or (at your option) any later"
     "version."
     ""
     "This library is distributed in the hope that it will be"
     "useful, but WITHOUT ANY WARRANTY; without even the implied"
     "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR"
     "PURPOSE.  See the GNU Lesser General Public License for more"
     "details."
     ""
     "You should have received a copy of the GNU Lesser General"
     "Public License along with this library; if not, write to the"
     "Free Software Foundation, Inc., 59 Temple Place, Suite 330,"
     "Boston, MA 02111-1307 USA")

    ("GPL3"
     t
     "This program is free software: you can redistribute it and/or modify"
     "it under the terms of the GNU General Public License as published by"
     "the Free Software Foundation, either version 3 of the License, or"
     "(at your option) any later version."
     ""
     "This program is distributed in the hope that it will be useful,"
     "but WITHOUT ANY WARRANTY; without even the implied warranty of"
     "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
     "GNU General Public License for more details."
     ""
     "You should have received a copy of the GNU General Public License"
     "along with this program.  If not, see <http://www.gnu.org/licenses/>.")

    ("GPL3-fr"
     t
     "Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le"
     "modifier suivant les termes de la GNU General Public License telle que"
     "publiée par la Free Software Foundation : soit la version 3 de cette"
     "licence, soit (à votre gré) toute version ultérieure."
     ""
     "Ce programme est distribué dans lespoir quil vous sera utile, mais SANS"
     "AUCUNE GARANTIE : sans même la garantie implicite de COMMERCIALISABILITÉ"
     "ni dADÉQUATION À UN OBJECTIF PARTICULIER. Consultez la Licence Générale"
     "Publique GNU pour plus de détails."
     ""
     "Vous devriez avoir reçu une copie de la Licence Générale Publique GNU avec"
     "ce programme ; si ce nest pas le cas, consultez :"
     "<http://www.gnu.org/licenses/>.")

    ("AGPL3"
     t
     "This program is free software: you can redistribute it and/or modify"
     "it under the terms of the GNU Affero General Public License as published by"
     "the Free Software Foundation, either version 3 of the License, or"
     "(at your option) any later version."
     ""
     "This program is distributed in the hope that it will be useful,"
     "but WITHOUT ANY WARRANTY; without even the implied warranty of"
     "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
     "GNU Affero General Public License for more details."
     ""
     "You should have received a copy of the GNU Affero General Public License"
     "along with this program.  If not, see <http://www.gnu.org/licenses/>.")

    ("LGPL3"
     t

     "This library is free software; you can redistribute it and/or"
     "modify it under the terms of the GNU Lesser General Public"
     "License as published by the Free Software Foundation; either"
     "version 3 of the License, or (at your option) any later"
     "version."
     ""
     "This library is distributed in the hope that it will be"
     "useful, but WITHOUT ANY WARRANTY; without even the implied"
     "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR"
     "PURPOSE.  See the GNU Lesser General Public License for more"
     "details."
     ""
     "You should have received a copy of the  GNU Lesser General"
     "Public License along with this library."
     "If not, see <http://www.gnu.org/licenses/>.")

    ("BSD-2"
     t
     "All rights reserved."
     ""
     "Redistribution and use in source and binary forms, with or without"
     "modification, are permitted provided that the following conditions are"
     "met: "
     ""
     "1. Redistributions of source code must retain the above copyright"
     "   notice, this list of conditions and the following disclaimer. "
     ""
     "2. Redistributions in binary form must reproduce the above copyright"
     "   notice, this list of conditions and the following disclaimer in the"
     "   documentation and/or other materials provided with the"
     "   distribution. "
     ""
     "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS"
     "\"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT"
     "LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR"
     "A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT"
     "OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,"
     "SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT"
     "LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,"
     "DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY"
     "THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT"
     "(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE"
     "OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
     ""
     "The views and conclusions contained in the software and documentation"
     "are those of the authors and should not be interpreted as representing"
     "official policies,  either expressed or implied, of the FreeBSD"
     "Project.")

    ("BSD-3"
     t
     "Redistribution and use in source and binary forms, with or"
     "without modification, are permitted provided that the following"
     "conditions are met:"
     ""
     "   1. Redistributions of source code must retain the above"
     "      copyright notice, this list of conditions and the"
     "      following disclaimer."
     ""
     "   2. Redistributions in binary form must reproduce the above"
     "      copyright notice, this list of conditions and the"
     "      following disclaimer in the documentation and/or other"
     "      materials provided with the distribution."
     ""
     "   3. The name of the author may not be used to endorse or"
     "      promote products derived from this software without"
     "      specific prior written permission."
     ""
     "THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY"
     "EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,"
     "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A"
     "PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR"
     "BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,"
     "EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED"
     "TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,"
     "DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND"
     "ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT"
     "LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING"
     "IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF"
     "THE POSSIBILITY OF SUCH DAMAGE.")

    ("Public Domain"
     nil
     "This software is in Public Domain."
     "You're free to do with it as you please.")

    ("Reserved"
     t
     "All Rights Reserved."
     ""
     "This program may not be included in any commercial product"
     "without the author written permission. It may be used freely"
     "for any non-commercial purpose, provided that this header is"
     "always included.")

    ("Proprietary"
     t
     "All Rights Reserved."
     ""
     "This program and its documentation constitute intellectual property "
     "of Pascal J. Bourguignon and is protected by the copyright laws of "
     "the European Union and other countries.")

    ("medicalis"
     t
     "Copyright 2008 Medical Information Systems. "
     ""
     "All Rights Reserved.")

    ("ubudu-proprietary"
     t
     "Copyright (c) 2011-2014, UBUDU SAS"
     "All Rights Reserved."
     ""
     "This program and its documentation constitute intellectual property "
     "of Ubudu SAS and is protected by the copyright laws of "
     "the European Union and other countries.")
    ("ubudu-public"
     t
     "Copyright (c) 2011-2014, UBUDU SAS"
     "All rights reserved."
     ""
     "Redistribution and use in source and binary forms, with or without"
     "modification, are permitted provided that the following conditions are met:"
     ""
     "* Redistributions of source code must retain the above copyright notice, this"
     "  list of conditions and the following disclaimer."
     ""
     "* Redistributions in binary form must reproduce the above copyright notice,"
     "  this list of conditions and the following disclaimer in the documentation"
     "  and/or other materials provided with the distribution."
     ""
     "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\""
     "AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE"
     "IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE"
     "DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE"
     "FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL"
     "DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR"
     "SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER"
     "CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,"
     "OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE"
     "OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."))
  "An a-list of (license name,  copyright-flag copyright-line...).
   When the copyright-flag is not nil, a copyright line is displayed.
   URL: http://www.gnu.org/licenses/license-list.html")


(defun pjb-insert-license (license lic-data formated-copyright-lines
                           title-format comment-format)
  "PRIVATE"
  (insert (format title-format "LEGAL"))
  (insert "\n")
  (insert (format comment-format license))
  (insert "\n")
  (insert (format comment-format ""))
  (insert "\n")
  (when (pop lic-data)
    (dolist (line formated-copyright-lines)
      (insert line)
      (insert "\n"))
    (insert (format comment-format ""))
    (insert "\n")
    )
  (do ((line (pop lic-data) (pop lic-data)))
      ((null line))
    (insert (format comment-format line))
    (insert "\n")))


(defun pjb-add-header (license &optional system user-interface owner start-year end-year
                       modification description)
  "
DO:               Inserts a header at the beginning of the file with
                  various  informations.
`license'         a string naming one license in `pjb-sources-licenses'.
`system'          a string naming a system (default: \"POSIX\").
`user-interface'  a string naming a user interface (default: \"NONE\").
`author'          a string naming the copyright owner (default: the author).
`start-year'      the starting year of the copyright (default: the current year).
`end-year'        the starting year of the copyright (default: the current year).
`modification'    the modification comment (default: empty, the programmer can edit it later).
`description'     the description of the file (default: \"XXX\", the programmer can edit it later).
"
  (interactive
   (list (completing-read "License: " pjb-sources-licenses
                          nil t nil nil "GPL")))
  (goto-char (point-min))
  (let* ((data           (header-comment-description-for-mode major-mode))
         (first-format   (hcd-header-first-format data))
         (last-format    (hcd-header-last-format data))
         (title-format   (hcd-header-title-format data))
         (comment-format (hcd-header-comment-format data))
         (file-name      (basename (or (buffer-file-name (current-buffer))
                                       "Untitled")))
         (language       (subseq (symbol-name major-mode)
                                 0 (search "-mode" (symbol-name major-mode))))
         (author-abrev   *pjb-sources-initials*)
         (author         (or add-log-full-name (user-full-name)))
         (owner          (or owner author))
         (email          user-mail-address)
         (year           (third (calendar-current-date)))
         (start-year     (or start-year year))
         (end-year       (or end-year   year))
         (line-length    78)
         (lic-data       (cdr (assoc license pjb-sources-licenses)))
         (system         (or system "POSIX"))
         (user-interface (or user-interface "NONE"))
         (modification   (or modification ""))
         (description    (or description "XXX")))
    (unless data
      (error "Don't know how to handle this major mode %S." major-mode))
    ;; (setq license (completing-read "License: " pjb-sources-licenses
    ;;                                nil t nil nil "GPL"))
    (cond
      ((eq major-mode 'emacs-lisp-mode)
       (setq language "emacs lisp"))
      ((eq major-mode 'lisp-mode)
       (setq language "Common-Lisp")
       (setq system   "Common-Lisp")))
    (save-excursion
      (save-restriction
        (widen)
        (goto-char (point-min))
        (insert (format title-format (format " -*- mode:%s;coding:utf-8 -*-"
                                             (mode-name major-mode))))
        (insert "\n")
        (insert (pjb-fill-a-line first-format line-length))
        (insert "\n")
        (insert (format title-format (format "%-20s%s" "FILE:" file-name)))
        (insert "\n")
        (insert (format title-format (format "%-20s%s" "LANGUAGE:" language)))
        (insert "\n")
        (insert (format title-format (format "%-20s%s" "SYSTEM:" system)))
        (insert "\n")
        (insert (format title-format (format "%-20s%s" "USER-INTERFACE:"
                                             user-interface)))
        (insert "\n")
        (insert (format title-format "DESCRIPTION"))
        (insert "\n")
        (insert (format comment-format ""))
        (insert "\n")
        (insert (format comment-format description))
        (insert "\n")
        (insert (format comment-format ""))
        (insert "\n")
        (insert (format title-format "AUTHORS"))
        (insert "\n")
        (insert (format comment-format (format "<%s> %s <%s>"
                                         author-abrev author email)))
        (insert "\n")
        (insert (format title-format "MODIFICATIONS"))
        (insert "\n")
        (insert (format title-format "BUGS"))
        (insert "\n")
        (pjb-insert-license
         license lic-data
         (list (pjb-format-copyright data owner start-year end-year))
         title-format comment-format)
        (insert (pjb-fill-a-line last-format line-length))
        (insert "\n")
        (insert (format comment-format ""))
        (insert "\n"))))
  (pjb-add-change-log-entry modification))


;; ------------------------------------------------------------------------
;; pjb-change-license
;; ------------------------------------------------------------------------
;; Change the license in the header.
;;


(defun pjb-change-license (license)
  "
DO:         Assuming there's already a header with a LEGAL section,
            change the license.
"
  (interactive (list
                (completing-read "License: " pjb-sources-licenses
                                 nil t nil nil "GPL")))
  (let* ((data           (header-comment-description-for-mode major-mode))
         (first-format   (hcd-header-first-format data))
         (last-format    (hcd-header-last-format data))
         (title-format   (hcd-header-title-format data))
         (comment-format (hcd-header-comment-format data))
         (file-name      (basename (or (buffer-file-name (current-buffer))
                                       "Untitled")))
         (language       (subseq (symbol-name major-mode)
                                 0 (search "-mode" (symbol-name major-mode))))
         (author-abrev   *pjb-sources-initials*)
         (author         (or add-log-full-name (user-full-name)))
         (email          user-mail-address)
         (year           (nth 2 (calendar-current-date)))
         (line-length    78)
         lic-data
         start end
         (copyrights '()))
    (unless data
      (error "Don't know how to handle this major mode %S." major-mode))
    (setq lic-data (cdr (assoc license pjb-sources-licenses)))
    (save-excursion
      (save-restriction
        (widen)
        (goto-char (point-min))
        (if (re-search-forward
             (format "^%s" (regexp-quote (format title-format "LEGAL")))
             nil t)
            (progn (beginning-of-line)  (setq start (point)))
            (error "Can't find a LEGAL section. Please use M-x pjb-add-header"))
        (if (re-search-forward
             (format "^%s"
               (format (regexp-quote last-format)
                 (format "%s.*"
                   (regexp-quote "*************"))))
             nil t)
            (progn (beginning-of-line) (setq end (point)))
            (error
             "Can't find the end of the header. Please use M-x pjb-add-header"))
        (goto-char start)
        (setf copyrights  (let ((old-copyrights (pjb-extract-copyrights data)))
                            (cond
                              (old-copyrights
                               (mapcar  (lambda (old-copyright)
                                          (destructuring-bind (author year-0 year-1) old-copyright
                                            (pjb-format-copyright data author year-0 year-1)))
                                        old-copyrights))
                              ((prefix-numeric-value t)
                               '())
                              (t
                               (list (pjb-format-copyright data author year year))))))
        (delete-region start end)
        (pjb-insert-license  license lic-data copyrights
                             title-format comment-format))))
  :changed)


;; ------------------------------------------------------------------------
;; pjb-update-eof
;; ------------------------------------------------------------------------
;; Inserts or update a comment at the end of the current source buffer
;; containing the name of the file, the author and the date.
;;


;;; (mapc (lambda (s) (printf "%s\n" s))
;;;       (sort
;;;        (let ((res '()))
;;;          (mapatoms (lambda (sym)
;;;                      (when (and (fboundp sym)
;;;                                 (string-has-suffix
;;;                                   (symbol-name sym) "-mode"))
;;;                        (push sym res))))
;;;          res)
;;;        (lambda (a b) (STRING<= (symbol-name a) (symbol-name b))))
;;;       )



;;; (defun pjb-ue-file-kind (name)
;;;   "
;;; DO:     Determine the file kind based on matching patterns in
;;;         pjb-ue-extensions. If this cannot be done, looks at the major-mode.
;;; "
;;;   (let ((e pjb-ue-extensions)
;;;         k l r)
;;;     (while e
;;;       (setq k (caar e)
;;;             l (cdar e)
;;;             e (cdr e))
;;;       (while l
;;;         ;; (message "Matching %s %S \n" (car l) name)
;;;         (if (string-match (car l) name)
;;;             (setq r k
;;;                   e nil
;;;                   l nil))
;;;         (setq l (cdr l))))
;;;     r));;pjb-ue-file-kind


(defvar *pjb-ue-silent* nil
  "When true, no error is issued if the file kind can't be determined.")


(defun pjb-ue-get-format-for-mode (mode)
  (let ((data (header-comment-description-for-mode mode)))
    (cond
      (data     (hcd-eof-format data))
      (*pjb-ue-silent*  "")
      (t        (error (format "Unknown mode."))))))


(defun pjb-ue-make-eof-for-current-buffer (format-string)
  (let ((bn (basename (or (buffer-file-name (current-buffer)) "Untitled"))))
    (format format-string
      bn
      ""       ;; (format-time-string "%Y-%m-%d %H:%M:%S")
      ""       ;;(user-real-login-name)
      )))


(defun pjb-ue-split-format-string (format-string)
  (let ((save-case-fold-search case-fold-search)
        (position 0)
        (index)
        (chunks nil)
        )
    (setq index (string-match "%[0-9-.]*[sdefgcS]" format-string position))
    (while index
      (push (substring format-string position index) chunks)
      (setq position (match-end 0))
      (setq index (string-match "%[0-9-.]*[sdefgcS]" format-string position))
      )
    (push (substring format-string position index) chunks)
    (nreverse chunks)))


(defun pjb-ue-make-regexp-for-current-buffer (format-string)
  (concat "^"
          (unsplit-string
           (mapcar 'regexp-quote
                   (pjb-ue-split-format-string format-string)) ".*")
          "$"))


;; Don't test pjb-update-eof without an eof string in this file,
;; since it contains matching format string much higher in the text...

(defun pjb-update-eof (&optional *pjb-ue-silent*)
  "
DO:         Insert a comment at the end of the source file with
            the name of the file, the author, and the date.
silent:     When non-nil, don't issue any message whent the file type can't
            be determined.
"
  (interactive "*")
  (save-excursion
    (goto-char (point-max))
    (let* ((format-string (pjb-ue-get-format-for-mode major-mode))
           (eof-string    (pjb-ue-make-eof-for-current-buffer format-string)) )
      (if (re-search-backward
           (pjb-ue-make-regexp-for-current-buffer format-string) nil t)
          (progn
            (delete-region (match-beginning 0) (match-end 0))
            (insert eof-string))
          (progn
            (goto-char (point-max))
            (insert (format "\n%s\n" eof-string)) )))))


;; ------------------------------------------------------------------------




;;; (when nil
;;;   (defun haha-bug! ()
;;;     (interactive)
;;;     (let ((test-buffer (get-buffer-create "*Exemple*")))
;;;       (switch-to-buffer test-buffer)
;;;       (erase-buffer)
;;;       ;; Setup of the test buffer
;;;       (insert "***************************************************************************\n")
;;;       (insert "                  A TITLE COMMENT                    \n")
;;;       (insert "****************************************************/\n")
;;;       (let ((i 0))
;;;         (while (< i 100)
;;;           (insert " a b c d e f g h i j k l m n o p q r s t u v w x y z \n")
;;;           (insert " A B C D E F G H I J K L M N O P Q R S T U V W X Y Z \n")
;;;           (setq i (1+ i))
;;;           ))
;;;       (insert "/*** PATTTTTERN -- PATTTTTTERN -- PATTTTTTERN ***/\n")
;;;       (goto-char (point-min)) ;; does not matter where.
;;;       ;; Here we start the problematic procedure.
;;;       (save-excursion
;;;         (goto-char (point-max))
;;;         (if (re-search-backward "^/\\*\\*\\* .* -- .* -- .* \\*\\*\\*/$" nil t)
;;;             (replace-match "/*** REPLACE -- REPLACE -- REPLACE ***/" t t)
;;;           (goto-char (point-max))
;;;           (insert "/*** REPLACE -- REPLACE -- REPLACE ***/")))))
;;;   )




;;    We need to parse C arguments.
;;
;;    We may have string or character literals (in which we must ignore
;;    parenthesis coma and new-lines).
;;
;;    We may have other parenthesis (expected well formed).
;;
;;    We may have coma, inside parenthesis.
;;
;; Syntax:
;;
;;    arglist  ::= '(' argument [ ',' argument ] ...  ')' .
;;    argument ::=  [ stuff | arglist ] ...
;;    stuff    ::=  string | char | not-coma-or-paren .
;;    string   ::=  '"' [ not-dbl-quote | '\' any-char ] '"' .
;;    char     ::=  ''' [ not-sgl-quote | '\' any-char ] ''' .
;;

;;;  (defun pjb-rotate-arguments ()
;;;  "This function will swap the argument the point is over with the
;;; previous one (or the last if it's over the first)."
;;;  (interactive)
;;;  (let ( start
;;;       (end (point)) )
;;;    (if (looking-at "[^)]*)")
;;;      (setq end (match-end 0))
;;;    (error "Point not at closing parenthesis."))
;;;    (goto-char end)
;;;   ;; search the opening parenthesis (code stollen from blink-matching-open).
;;;    (setq start (and
;;;           (> (point) (1+ (point-min)))
;;;           ;; Verify an even number of quoting characters precede the close.
;;;           (= 1 (logand 1 (- (point)
;;;                   (save-excursion
;;;                     (forward-char -1)
;;;                     (skip-syntax-backward "/\\")
;;;                     (point)))))
;;;           (let* ((oldpos (point))
;;;              (blinkpos)
;;;              (mismatch))
;;;           (save-restriction
;;;             (if blink-matching-paren-distance
;;;               (narrow-to-region (max (point-min)
;;;                          (- (point) blink-matching-paren-distance))
;;;                       oldpos))
;;;             (condition-case ()
;;;               (let ((parse-sexp-ignore-comments
;;;                  (and parse-sexp-ignore-comments
;;;                     (not blink-matching-paren-dont-ignore-comments))))
;;;               (setq blinkpos (scan-sexps oldpos -1)))
;;;             (error nil)))
;;;           (and blinkpos
;;;              (/= (char-syntax (char-after blinkpos))
;;;                ?\$)
;;;              (setq mismatch
;;;                (or (null (matching-paren (char-after blinkpos)))
;;;                  (/= (char-after (1- oldpos))
;;;                    (matching-paren (char-after blinkpos))))))
;;;           (when mismatch
;;;             (error "Mismatch."))
;;;           blinkpos
;;;           )))
;;;    (unless start
;;;      (error "Could not find a corresponding opening parenthesis."))
;;;    (message "Should parse this: %S." (buffer-substring start end))
;;;    )) ;;pjb-rotate-arguments




;; ------------------------------------------------------------------------
;; generate-options
;; ------------------------------------------------------------------------
;; Generate C source to parse simple flag options in argv
;;

(defun true-atom (atom)
  (and atom (atom atom)))


(defun nodep (node)
  (or (atom node)
      (and (true-atom (car node)) (true-atom (cdr node)))))


(defun flatten-tree (tree)
  "tree --> list"
  (cond
    ((null tree)  tree)
    ((nodep tree) (list tree))
    (t (append (flatten-tree (car tree)) (flatten-tree (cdr tree))))))


'(mapcar (lambda (io) (equal (cadr io) (flatten-tree (car io))))
  '(
    (  a                  (a)              )
    (  (a)                (a)              )
    (  ((a))              (a)              )
    (  ((a b))            (a b)            )
    (  ((a . b))          ((a . b))        )
    (  (a b)              (a b)            )
    (  (a (b c))          (a b c)          )
    (  ((a . b) c)        ((a . b) c)      )
    (  (a (b . c))        (a (b . c))      )
    (  ((x y) (b . c))    (x y (b . c))    )
    (  ((b . c) (x y))    ((b . c) x y)    )
    ))


(defun collapse-alist (alist)
  "Sorts the alist on the car of each item, then colapse the cdr of each item
 whose car is the same into a list consed with that car."
  (do* ((items (sort (copy-seq alist)
                     (lambda (a b) (STRING<= (symbol-name (car a))
                                             (symbol-name (car b)))))
               (cdr items))
        (cur-var (caar items) (caar items))
        (cur-opt (cdar items) (cdar items))
        (last-var nil)
        (last-opt nil)
        (result   nil))
       ((null items)
        (progn (if last-var  (push (cons last-var last-opt) result))
               (nreverse result)) )
    (cond
      ((eq cur-var last-var)   (push cur-opt last-opt))
      (last-var
       (push (cons last-var last-opt) result)
       (setq last-var cur-var
             last-opt (list cur-opt)))
      (t (setq last-var cur-var
               last-opt (list cur-opt))))))



(defun generate-options (options defaults)
  "Generate C code to parse argv[].
 OPTIONS is a list  of (option flag...)
 DEFAULTS is a list of options that are on by defaults.

 (generate-options '((-a all) (-b before not_after) (-c change)) '( -a -c))
 ==>
    const char usage_options[]=\"[-a] [-b] [-c] \";

    int         all             =1;
    int         before          =0;
    int         change          =1;
    int         not_after       =0;

    for(i=1;i<argc;i++){
        if(strcmp(argv[i],\"-a\")==0){          all=1;
        }else if(strcmp(argv[i],\"-b\")==0){
            before=1;
            not_after=1;
        }else if(strcmp(argv[i],\"-c\")==0){    change=1;
        }else{
            usage(argv[0]);
            exit(1);
        }
    }
"
  ;; print usage string:
  (printf "\n")
  (printf "    const char usage_options[]=%S;\n"
          (apply 'concat (mapcar (lambda (x) (format "[%s] " (car x)))
                                 options)))
  ;; print option flag declarations:
  (printf "\n")
  (mapc (lambda (x)
          (printf "    int         %-16s=%d;\n"
                  (car x) (if (intersection (cdr x) defaults) 1 0)))
        (collapse-alist (flatten-tree
                         (mapcar (lambda (x)
                                   (mapcar (lambda (y) (cons y (car x)))
                                           (cdr x)))
                                 options))))
  ;;print option parsing:
  (printf "\n")
  (printf "    for(i=1;i<argc;i++){\n")
  (let ((else "") (spaces "      "))
    (mapc (lambda (x)
            (if (= 1 (length (cdr x)))
                (progn
                  (printf "%8s%sif(strcmp(argv[i],\"%s\")==0){"
                          "" else (car x) )
                  (mapc (lambda (y) (printf "%s    %s=1;\n" spaces y)) (cdr x)))
                (progn
                  (printf "%8s%sif(strcmp(argv[i],\"%s\")==0){\n"
                          "" else (car x) )
                  (mapc (lambda (y) (printf "%12s%s=1;\n" "" y)) (cdr x))))
            (setq else "}else "
                  spaces ""))
          options))
  (printf "%8s}else{\n" "")
  (printf "%12susage(argv[0],usage_options);\n" "")
  (printf "%12sexit(1);\n" "")
  (printf "%8s}\n" "")
  (printf "    }\n"))



;;;---------------------------------------------------------------------
;;;


(defun lse-newline ()
  "Insert newline and line number incremented with the same step
   as previously."
  (interactive)
  (newline)
  (let ((nlpt (point))
        (line (progn
                (forward-line -1)
                (beginning-of-line)
                (if (looking-at "[0-9]+")
                    (let ((curr (string-to-number (match-string 0))))
                      (forward-line -1)
                      (beginning-of-line)
                      (if (looking-at "[0-9]+")
                          (let ((prev (string-to-number (match-string 0))))
                            (+ curr (abs (- curr prev))))
                          (+ 10 curr)))
                    10))))
    (goto-char nlpt)
    (beginning-of-line)
    (insert (format "%d " line))
    (when (looking-at " +")
      (delete-region (match-beginning 0) (match-end 0))))) ;;lse-newline

(defvar line-num-map (make-sparse-keymap))
(define-key line-num-map "\n"  'lse-newline)
(define-key line-num-map "\r"  'lse-newline)

(defun insert-line-numbers ()
  (interactive)
  (save-excursion
    (save-restriction
      (widen)
      (let ((fmt (format "%%0%dd "
                   (1+ (truncate
                        (log (count-lines (point-min) (point-max))
                             10)))))
            (i 0))
        (goto-char (point-min))
        (while (< (point) (point-max))
          (setq i (1+ i))
          (insert (format fmt i))
          (forward-line))))))


(defun delete-line-numbers ()
  (interactive)
  (save-excursion
    (save-restriction
      (widen)
      (goto-char (point-min))
      (while (< (point) (point-max))
        (if (looking-at "[0-9][0-9]* ")
            (delete-region (match-beginning 0) (match-end 0)))
        (forward-line)))))


(defun renumber-lines ()
  (interactive)
  (delete-line-numbers)
  (insert-line-numbers))


(defun compose-line-numbers ()
  (interactive)
  (when (<= 21 emacs-major-version)
    (let ((fmt (format "\n%%0%dd "
                 (1+ (truncate
                      (log (count-lines (point-min) (point-max))
                           10)))))
          (number 1))
      (goto-char (point-min))
      (while  (re-search-forward "\n" (point-max) t)
        (compose-region (match-beginning 0)
                        (match-end 0)
                        (format fmt number)
                        'decompose-region)
        (setq number (1+ number))))))


;;;------------------------------------------------------------------------
;;;
;;; Some commands used to convert C headers into sbcl alien definitions.
;;;

(defun c-function-to-lisp-alien ()
  (interactive)
  (while (re-search-forward "extern \\(.*[^A-Z0-9a-z_]\\)\\([a-zA-Z_][A-Z0-9a-z_]*\\) *__P((\\(.*\\)));" nil t)
    (let ((where   (match-beginning 0))
          (restype (match-string 1))
          (fname   (match-string 2))
          (args    (split-string (match-string 3) " *, *"))
          (arestype nil))
      (while (string-match "^\\(.*\\)\\(\\* *\\)$" restype)
        (push '* arestype)
        (setq restype (match-string-no-properties 1 restype)))
      (setq restype (mapcar (function intern) (split-string restype)))
      (if (= 1 (length restype)) (setq restype (car restype)))
      (while arestype
        (setq restype (list (pop arestype) restype)))
      (goto-char where)
      (insert ";;; ")
      (forward-line)
      (insert (format "(DEFINE-ALIEN-ROUTINE \"%s\" %S\n" fname restype))
      (dolist (arg args)
        (insert (format "  (  %s  :IN)\n" arg)))
      (insert " )\n\n"))))


(defun c-variable-to-lisp-alien ()
  (interactive)
  (while (re-search-forward "extern \\(.*[^A-Z0-9a-z_]\\)\\([a-zA-Z_][A-Z0-9a-z_]*\\)[  ]*;" nil t)
    (let ((start   (match-beginning 0))
          (end     (match-end 0))
          (type    (match-string-no-properties 1))
          (name    (match-string-no-properties 2))
          (atype nil))
      (while (string-match "^\\(.*\\)\\(\\* *\\)$" type)
        (push '* atype)
        (setq type (match-string-no-properties 1 type)))
      (setq type (mapcar (function intern) (split-string type)))
      (if (= 1 (length type)) (setq type (car type)))
      (while atype
        (setq type (list (pop atype) type)))
      (delete-region start end)
      (insert (format "(DEFINE-ALIEN-VARIABLE \"%s\" %S)\n"
                name type)))))


(defun c-define-to-lisp-constant ()
  "Substitute #define C constants into lisp defconstant forms."
  (interactive)
  (let ((start (point)))
    (while (re-search-forward  "^#[      ]*define[       ][      ]*\\([A-Za-z_][A-Za-z_0-9]*\\)[         ][      ]*\\(.*?\\)[    ][      ]*/\\* *\\(..*\\) *\\*/ *$" nil t)
      (let ((start   (match-beginning 0))
            (end     (match-end 0))
            (name    (match-string-no-properties 1))
            (value   (match-string-no-properties 2))
            (comment (match-string-no-properties 3)))
        (delete-region start end)
        (insert (format "(defconstant %s %s%s)"
                  name value
                  (if (= 0 (length comment))
                      "" (format " \"%s\"" comment))))))
    (goto-char start)
    (while (re-search-forward  "^#[      ]*define[       ][      ]*\\([A-Za-z_][A-Za-z_0-9]*\\)[         ][      ]*\\(.*?\\)[    ]*$" nil t)
      (let ((start   (match-beginning 0))
            (end     (match-end 0))
            (name    (match-string-no-properties 1))
            (value   (match-string-no-properties 2)) )
        (delete-region start end)
        (insert (format "(defconstant %s %s)"  name value))))))



(defun c-left-shift-to-number ()
  "Substitute any literal ([0-9]*<<[0-9]) expression into the actual value."
  (interactive)
  (while (re-search-forward  "(\\([0-9]*\\)<<\\([0-9]*\\))" nil t)
    (let ((start   (match-beginning 0))
          (end     (match-end 0))
          (n       (car (read-from-string (match-string-no-properties 1))))
          (s       (car (read-from-string (match-string-no-properties 2)))))

      (delete-region start end)
      (insert (format "%d" (* n (expt 2 s)))))))



(defun c-comments-to-lisp ()
  "Convert all C comments /* */ or // into lisp comments,
from the point down to the end of the buffer."
  (interactive)
  (while (re-search-forward "/\\*\\(\\([^*]\\|\\*[^/]\\)*\\)\\*/" nil t)
    (let ((start (match-beginning 0))
          (end   (match-end 0))
          (comment (match-string-no-properties 1)))
      (delete-region start end)
      (insert
       (unsplit-string
        (mapcar (lambda (line) (concatenate 'string ";; " line))
                (split-string comment "\n"))
        "\n")))))

;;;
;;;---------------------------------------------------------------------




;;;---------------------------------------------------------------------
;;;

(defun arg-name (num)
  "RETURN: a one letter named argument name."
  (let* ((arg-chars "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
         (base (length arg-chars))
         (digit (mod num base)))
    (if (< num base)
        (cl:string (char arg-chars num))
        (concatenate 'string
          (arg-name (1- (/ num base)))
          (cl:string (char arg-chars digit))))))

;; (dotimes (n (* 27 27))  (show n (arg-name n)))

(defun clean-arg-list (arg-list)
  (let ((arg-num -1))
    (mapcar
     (lambda (arg)
       (cond
         ((member arg '(&WHOLE &REST &OPTIONAL &KEY &ENVIRONMENT &BODY
                        &AUX &ALLOW-OTHER-KEYS
                        &whole &rest &optional &key &environment
                        &body &aux &allow-other-keys))
          arg)
         ((symbolp arg) arg) ;; (intern (arg-name (incf arg-num))))
         ((consp arg)  (first arg)) ;; (intern (arg-name (incf arg-num))))
         (t (error "Unexpected argument %S." arg))))
     arg-list)))


(defun get-generics-from-methods-of-file (file &optional all)
  "Private: use insert-generics."
  (mapcar
   (lambda (def) `(DEFGENERIC ,(second def)
                      ,(clean-arg-list (find-if (function listp) (cddr def)))))
   (let ((m (delete-duplicates
             (get-sexps
              file
              :selector (lambda (sexp)
                          (and (listp sexp)
                               (symbolp (car sexp))
                               (STRING-EQUAL (car sexp) "DEFMETHOD"))))
             :key (function second)
             :test (function eql)))
         (g (if all
                nil
                (delete-duplicates
                 (get-sexps
                  file
                  :selector (lambda (sexp)
                              (and (listp sexp)
                                   (symbolp (car sexp))
                                   (STRING-EQUAL (car sexp) "DEFGENERIC"))))
                 :key (function second)
                 :test (function eql)))))
     (delete-if
      (lambda (sexp) (or (member* (second sexp)
                                 '(INITIALIZE-INSTANCE PRINT-OBJECT)
                                 :test (function STRING-EQUAL))
                         (member* (second sexp) g
                                 :key (function second)
                                 :test (function STRING-EQUAL))))
      m))))


(defun insert-generics (&optional imported)
  "Insert (DEFGENERIC ...) sexps from the (defmethod ...) found in file."
  (interactive)
  (mapcar
   (lambda (def) (insert (format "%S\n" def)))
   (set-difference
    (get-generics-from-methods-of-file (buffer-file-name))
    imported
    :key (function second)
    :test (function STRING-EQUAL))))


(defun insert-definitions ()
  "Insert the names of all defined symbols in this file.
defconstant deftype defstruct defclass defvar defparameter
defun defmacro defgeneric defmethod"
  (interactive)
  (mapcar
   (lambda (def) (insert (format "%S " def)))
   (delete-duplicates
    (mapcar (lambda (sexp) (if (consp (second sexp))
                               (if (symbolp (first (second sexp)))
                                   (STRING-UPCASE (first (second sexp)))
                                   "")
                               (STRING-UPCASE (second sexp))))
            (get-sexps
             (buffer-file-name)
             :selector (lambda (sexp)
                         (message "sexp  = %S" sexp)
                         (and (listp sexp)
                              (symbolp (first sexp))
                              (STRING-EQUAL (first sexp) "DEF"
                                            (kw END1) 3)))))
    :test (function string=))))

(defalias 'insert-exports 'insert-definitions)


;; (defun current-defstruct-sexp (&optional at-point)
;;   "
;; RETURN: The defstruct that surrounds the point or just follows the point.
;; "
;;   (save-excursion
;;     (flet ((defstructp (sexp)
;;              (and (listp sexp)
;;                   (symbolp (first sexp))
;;                   (let ((case-insensitive t))
;;                     (member* (symbol-name (first sexp))
;;                              '("defstruct" "cl:defstruct"
;;                                "common-lisp:defstruct")
;;                              :test  (function string-equal))))))
;;       (loop
;;          for sexp = (sexp-at-point)
;;          while (and (not at-point)
;;                     (not (defstructp sexp))
;;                     (ignore-errors
;;                       (progn (up-list)
;;                              (backward-sexp)
;;                              t)))
;;          finally (return (when (defstructp sexp) sexp))))))
;;
;;
;; (defun symbols-defined-by-defstruct (form)
;;   (destructuring-bind (name-and-options &rest slots) (rest form)
;;     (let* ((name    (if (symbolp name-and-options)
;;                     name-and-options
;;                     (first name-and-options)))
;;           (options (if (symbolp name-and-options)
;;                        '()
;;                        (rest name-and-options)))
;;            (conc-name))
;;       )
;;     ))
;;
;;
;; (defun export-structure ()
;;   "
;; NOTE:   The defstruct taken is either the defstruct just preceding the point,
;;         or if there's none, the defstruct the point is or just following.
;; DO:
;; "
;;   (interactive)
;;   (save-excursion
;;     (let ((struct (or (save-excursion
;;                         (backward-sexp)
;;                         (current-defstruct-sexp t))
;;                       (progn
;;                         (skip-chars-forward " \t\n")
;;                         (current-defstruct-sexp)))))
;;       (if struct
;;           (insert-in-exports (symbols-defined-by-defstruct struct))
;;           (error "There is not defstruct around the point.")))))
;;
;;
;;
;; (progn
;;   (defstruct person
;;     (name "" :type string)
;;     age
;;     addresse))



(defun insert-columns (&optional arg)
  "Inserts two or three lines of digits numbering the columns."
  (interactive "P")
  ;;(message "arg=%S" (prefix-numeric-value arg))
  (if (= 1 (prefix-numeric-value arg))
      (setf arg 80)
      (setf arg (prefix-numeric-value arg)))
  (end-of-line)
  (when (< 100 arg)
    (insert "\n")
    (loop for i from 0 below arg
       do (insert (format "%d" (mod (truncate i 100) 10)))))
  (insert "\n")
  (loop for i from 0 below arg
     do (insert (format "%d" (mod (truncate i 10) 10))))
  (insert "\n")
  (loop for i from 0 below arg
     do (insert (format "%d" (mod i 10))))
  (insert "\n"))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun memstr (item list)
  (or (member* item list :test (function STRING-EQUAL))
      (let ((colon (position (character ":") (cl:string item))))
        (and colon
             (member* (subseq (cl:string item) (1+ colon)) list
                      :test (function STRING-EQUAL))))))

(defun symbol-name= (a b)
  (setf a (let ((colon (position (character ":") (cl:string a))))
            (if colon
                (subseq (cl:string a) (1+ colon))
                a))
        b (let ((colon (position (character ":") (cl:string a))))
            (if colon
                (subseq (cl:string a) (1+ colon))
                b)))
  (string-equal a b))


(defun parse-alternative ()
  (interactive)
  (let ((form (progn (forward-sexp) (backward-sexp) (sexp-at-point))))
    (if (atom form)
        (error "Not an alternative")
        (cond ((symbol-name= (car form) 'cond) (cdr form))
              ((symbol-name= (car form) 'if)
               (case (length form)
                 ((1) (error "IF with no test and no branch"))
                 ((2) (error "IF with no branch"))
                 ((3) (list (cdr form)))
                 ((4) (list (list (cadr form) (caddr form))
                            (list t (cadddr form))))
                 (otherwise (error "IF with more than two branches"))))
              ((symbol-name= (car form) 'when)
               (list (cdr form)))
              ((symbol-name= (car form) 'unless)
               (list `(,(if (and (consp (cadr form))
                                 (symbol-name= (caadr form) 'not))
                            (cadadr form)
                            `(not ,(cadr form)))
                        ,@(cddr form))))))))

(defun make-cond (alternatives)
  `(cond ,@alternatives))

(defun make-when (alternatives)
  (if (= 1 (length alternatives))
      `(when ,@(first alternatives))
      (error "Cannot convert multiple branches to a when form")))

(defun make-unless (alternatives)
  (if (= 1 (length alternatives))
      (if (and (consp (caar alternatives))
               (symbol-name= (caaar alternatives) 'not))
          `(unless ,@(cdaar alternatives)      ,@(cdar alternatives))
          `(unless (not ,(caar alternatives))  ,@(cdar alternatives)))
      (error "Cannot convert multiple branches to a when form")))

(defun make-if   (alternatives)
  (if (= 1 (length alternatives))
      `(if ,(caar alternatives)
           ,(if (<= (length (cdar alternatives)) 1)
                (cadar alternatives)
                `(progn ,@(cdar alternatives))))
      `(if ,(caar alternatives)
           ,(if (<=  (length (cdar alternatives)) 1)
                (cadar alternatives)
                `(progn ,@(cdar alternatives)))
           ,(if (symbol-name= (caadr alternatives) 't)
                (if (<= (length (cdadr alternatives)) 1)
                    (cadadr alternatives)
                    `(progn ,@(cdadr alternatives)))
                (make-if (cdr alternatives))))))

(defun convert-alternative (target)
  (interactive
   (list
    (completing-read  "Target operator: " '("cond""if""when""unless"))))
  (let* ((alternative (parse-alternative))
         (start (point))
         (end (progn (forward-sexp) (point)))
         (new-form (funcall (ecase (intern (string-downcase target))
                              ((cond)   (function make-cond))
                              ((if)     (function make-if))
                              ((when)   (function make-when))
                              ((unless) (function make-unless))) alternative)))
    (delete-region start end)
    ;; TODO: use the same kind of symbol in the new-form as in the alternative:
    ;;       cond --> if
    ;;       COND --> IF
    ;;       package:cond --> package:if
    ;;       PACKAGE:COND --> PACKAGE:IF
    ;; TODO: some pretty printing
    (insert (format "%S" new-form))))

(when nil
  ;; (if test)
  (if test then)
  (if test then else)
  (if test then else maybe)

  (cond)
  (cond (test-1))
  (cond (test-1 expr-11))
  (cond (test-1 expr-11 expr-12))
  (cond (test-1 expr-11 expr-12) (test-2 expr-21 expr-22))
  (cond (test-1 expr-11 expr-12)
        (test-2 expr-21 expr-22)
        (test-3 expr-31 expr-32))
  (cond (t expr-11 expr-12))
  (cond (test-1 expr-11 expr-12) (t expr-21 expr-22))
  (cond (test-1 expr-11 expr-12) (test-2 expr-21 expr-22)  (t expr-31 expr-32))

  (when test)
  (when test when)
  (when test when-1 when-2)
  (when (not test))
  (when (not test) when)
  (when (not test) when-1 when-2)

  (CL:UNLESS test)
  (unless test unless)                  ;
  (unless test unless-1 unless-2)
  (unless (not test))
  (unless (not test) unless)
  (unless (not test) unless-1 unless-2)
  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;



;; We'll use some functions from pjb-cl-magic.el to process emacs lisp
;; argument lists.

(defun function-parameter-list (function)
  "Return the parameter list of the emacs FUNCTION."
  (let* ((def   (if (symbolp function)
                    (if (subrp (symbol-function function))
                        function
                        (symbol-function function))
                    function))
         (help  (help-function-arglist def))
         (doc   (documentation function))
         (split (help-split-fundoc doc function)))
    (or help
        (when  (first split) (cdar (read-from-string (first split))))
        split
        :unknown)))


(defun function-argument-counts (function)
  "Return a cons continaing the minimum and maximum number of arguments
the FUNCTION can take."
  (let* ((args (split-lambda-list-on-keywords
                (maptree (lambda (item)
                           (if (memq item '(&optional &rest))
                               (intern (string-upcase item))
                               item))
                         (function-parameter-list (function enlarge-window)))
                :ordinary))
         (min (length (cdr (assoc '&MANDATORY args)))))
    (if (assoc '&REST args)
        (cons min '&rest)
        (cons min (+ min (length (cdr (assoc '&OPTIONAL args))))))))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defvar *sources* "/tmp")
(defvar *sources-cache* '())

(defun directory-recursive-find-files-named (directory name)
  (split-string (shell-command-to-string (format "find %s -name %s -print0 | head -40"
                                                 (shell-quote-argument (expand-file-name directory))
                                                 (shell-quote-argument name)))
                "\0" t))



(require 'filecache)

(defun remove-trailling-slashes (path)
  (while (char= ?/ (aref path (1- (length path))))
    (setf path (subseq path 0 (1- (length path)))))
  (if (zerop (length path))
      "/"
      path))


(defun* expand-path-alternatives (path)
  (let ((items '())
        (start 0)
        (lbrace (position ?{ path)))
    (while (and lbrace
                (or (zerop lbrace)
                    (char/= ?\\ (aref path (1- lbrace)))))
      (let ((rbrace (position ?} path :start lbrace)))
        (while (and rbrace
                    (char= ?\\ (aref path (1- rbrace))))
          (setf rbrace (position ?} path :start (1+ rbrace))))
        (if rbrace
            (progn
              (when (plusp lbrace)
                (push (list (substring path start lbrace)) items))
              (push (split-string (substring path (1+ lbrace) rbrace) ",") items)
              (setf start (1+ rbrace))
              (setf lbrace (position ?{ path :start start)))
            (setf lbrace nil))))
    (push (list (substring path start)) items)
    (mapcar (lambda (components) (apply (function concat) components))
        (apply (function combine) (nreverse items)))))


(defun set-sources (directory &optional project-type)
  (interactive "sSource directory:
SProject Type: ")
  (message "Caching paths…")
  (let ((directory     (remove-trailling-slashes directory))
        (exclude-names '("debug" "release" ".svn" ".git" ".hg" ".cvs"))
        (include-types (ecase project-type
                         ((nil)
                          '("xib" "h" "c" "m" "hh"  "cc" "mm" "hxx" "cxx"
                            "lisp" "asd" "cl" "el"
                            "rb"
                            "java" "xml"
                            "logs" "txt"
                            "html" "iml" "json" "md" "prefs" "project" "properties" "sh"))
                         ((lisp cl)
                          '("lisp" "asd" "cl" "el"
                            "xib" "logs" "txt" "html"))
                         ((android)
                          '("h" "c" "m" "hh"  "cc" "mm" "hxx" "cxx"
                            "java" "xml"
                            "logs" "txt"
                            "html" "iml" "json" "md" "prefs" "project" "properties" "sh"))
                         ((cocoa)
                          '("h" "c" "m" "hh"  "cc" "mm" "hxx" "cxx"
                            "xml" "logs" "txt"
                            "html" "iml" "json" "md" "prefs" "project" "properties" "sh")))))
    (handler-case
        (dolist (directory (mapcar (function remove-trailling-slashes)
                                   (expand-path-alternatives directory)))
          (let ((*sources* directory))
            (file-cache-add-directory-recursively
             directory
             (format ".*\\.\\(%s\\)$" (mapconcat (function identity) include-types "\\|")))))
      (error (err)
        (message (format "error while caching files: %s" err))))
    (setf *sources* directory)
    (setf *sources-cache* (sort (mapcar (function car) file-cache-alist)
                                (function string<)))
    (let ((directory (expand-file-name directory)))
      (set-shadow-map (list (cons (format "%s/" directory)
                                  (format "%s%s/" (file-name-directory directory) *shadow-directory-name*)))))
    (message "Caching paths… Complete.")
    (setf grep-find-command
          (format "find %s \\( \\( %s \\) -prune \\) -o -type f  \\( %s \\) -print0 | xargs -0 grep -niH -e "
                  *sources*
                  (mapconcat (lambda (name) (format "-name %s" name))     exclude-names " -o ")
                  (mapconcat (lambda (type) (format "-name \\*.%s" type)) include-types " -o "))
          grep-host-defaults-alist nil)))


(defun sources-find-file-named (name)
  (interactive (list
                (completing-read
                 "File name: "
                 (mapcar (lambda (x) (cons x nil)) *sources-cache*)
                 (constantly t)
                 nil)))
  ;; (interactive "sFile name: ")
  (let ((files (directory-recursive-find-files-named *sources* name)))
    (case (length files)
      ((0) (message "No such file."))
      ((1) (find-file (first files)))
      (otherwise (find-file (x-popup-menu (list '(0 0) (selected-window))
                                          (list "Source Find File Named"
                                                (cons "Select a file"
                                                      (sort (mapcar (lambda (path) (cons path path))
                                                                    files)
                                                            (lambda (a b)
                                                              (let ((a (car a))
                                                                    (b (car b)))
                                                               (or (< (length a) (length b))
                                                                   (and (= (length a) (length b))
                                                                        (string< a b)))))))))))))
  (global-set-key (kbd "A-f") 'sources-find-file-named))



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun comment-line (start end)
  "Comments a region using the infamous 'line' boxing style:

/*
 * Like
 * this.
 */

"
  (interactive "r")
  (save-excursion
   ;; Insert end of comment:
   (goto-char end)
   (unless (bolp)
     (insert "\n"))
   (insert " */\n")

   (with-marker (end end)
     ;; Insert begin of comment:
     (goto-char start)
     (unless (bolp)
       (insert "\n"))
     (insert "/*\n")
     ;; Add line header:
     (replace-regexp "^" " * " nil (point) (- end 1)))))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(provide 'pjb-sources)
;;;; THE END ;;;;

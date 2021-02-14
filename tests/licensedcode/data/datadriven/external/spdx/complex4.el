
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


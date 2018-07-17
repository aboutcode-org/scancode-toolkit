/*
;uInt longest_match_x64(
;    deflate_state *s,
;    IPos cur_match);                             // current match 

; gvmat64.S -- Asm portion of the optimized longest_match for 32 bits x86_64
;  (AMD64 on Athlon 64, Opteron, Phenom
;     and Intel EM64T on Pentium 4 with EM64T, Pentium D, Core 2 Duo, Core I5/I7)
; this file is translation from gvmat64.asm to GCC 4.x (for Linux, Mac XCode)
; Copyright (C) 1995-2010 Jean-loup Gailly, Brian Raiter and Gilles Vollant.
;
; File written by Gilles Vollant, by converting to assembly the longest_match
;  from Jean-loup Gailly in deflate.c of zLib and infoZip zip.
;  and by taking inspiration on asm686 with masm, optimised assembly code
;        from Brian Raiter, written 1998
;
;  This software is provided 'as-is', without any express or implied
;  warranty.  In no event will the authors be held liable for any damages
;  arising from the use of this software.
;
;  Permission is granted to anyone to use this software for any purpose,
;  including commercial applications, and to alter it and redistribute it
;  freely, subject to the following restrictions:
;
;  1. The origin of this software must not be misrepresented; you must not
;     claim that you wrote the original software. If you use this software
;     in a product, an acknowledgment in the product documentation would be
;     appreciated but is not required.
;  2. Altered source versions must be plainly marked as such, and must not be
;     misrepresented as being the original software
;  3. This notice may not be removed or altered from any source distribution.
;
;         http://www.zlib.net
;         http://www.winimage.com/zLibDll
;         http://www.muppetlabs.com/~breadbox/software/assembly.html
;

/* Copyright (C) 2005 Analog Devices
   Author: Jean-Marc Valin */
/**
   modification, are permitted provided that the following conditions
   are met:
   
   - Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
   
   - Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.
   
   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
         "%0 = (A1 += %2.L*%1.H);\n\t"
         "%0 = %0 + %4;\n\t"
   : "=&W" (res), "=&d" (b)
   : "d" (a), "1" (b), "d" (c)
   : "A1"
         );
         "%0 = (A1 += %2.L*%1.H);\n\t"
         "%0 = %0 + %4;\n\t"
   : "=&W" (res), "=&d" (b)
   : "d" (a), "1" (b), "d" (c)
   : "A1"
         );
 *
 * The horribleness of the code is probably mine (matt).
 *
 * Modifications copyright 2003 Matt Johnston
 *
 * PuTTY is copyright 1997-2003 Simon Tatham.
 * 
 * Portions copyright Robert de Bath, Joris van Rantwijk, Delian
 * Delchev, Andreas Schultz, Jeroen Massar, Wez Furlong, Nicolas Barry,
 * Justin Bradford, and CORE SDI S.A.
 * and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT.  IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE
 * FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * Helper routines. (The base64 ones are defined in sshpubk.c.)
 */

#define isbase64(c) (	((c) >= 'A' && (c) <= 'Z') || \
						 ((c) >= 'a' && (c) <= 'z') || \
						 ((c) >= '0' && (c) <= '9') || \
						 (c) == '+' || (c) == '/' || (c) == '=' \
						 )

	{
		int slen = 60;					   /* starts at 60 due to "Comment: " */
		char *c = key->comment;
		while ((int)strlen(c) > slen) {
			fprintf(fp, "%.*s\\\n", slen, c);
			c += slen;
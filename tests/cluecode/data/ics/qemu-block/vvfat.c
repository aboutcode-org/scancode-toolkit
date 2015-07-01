/*
 * QEMU Block driver for virtual VFAT (shadows a local directory)
 *
 * Copyright (c) 2004,2005 Johannes E. Schindelin
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
	unsigned char* c=(unsigned char*)direntry;
	int i;
	for(i=1;i<11 && c[i] && c[i]!=0xff;i+=2)
#define ADD_CHAR(c) {buffer[j] = (c); if (buffer[j] < ' ') buffer[j] = 0xb0; j++;}
	    ADD_CHAR(c[i]);
	for(i=14;i<26 && c[i] && c[i]!=0xff;i+=2)
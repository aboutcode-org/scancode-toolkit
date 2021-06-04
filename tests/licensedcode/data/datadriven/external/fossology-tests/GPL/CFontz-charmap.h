/*
 * Character mapping for CFontz 63x by Peter Marschall <peter@adpm.de>
 *
 * Translates ISO 8859-1 to CFontz 63x charset (not for CF633).
 *
 * This file is released under the GNU General Public License.
 * Refer to the COPYING file distributed with this package.
 *
 * The following translations are being performed:
 * - map umlaut characters to the corresponding umlaut characters
 * - map other accented characters to the corresponding accented characters
 * - map unmappable accented characters to their base characters
 * - map beta (=sharp s), micro and various currency symbols
 * - back-quote simulated by single quote
 * - diaeresis simulated by double quote
 * - degree simulated by superscript zero
 * - multiplication sign simulated by x
 * - division sign simulated by :
 *
 */

#include "hd44780-charmap.h"

const unsigned char CFontz_charmap[] = {	// mapped chars: ? means ToDo
/* #0 */
    0,   1,   2,   3,   4,   5,   6,   7,
    8,   9,  10,  11,  12,  13,  14,  15,
   16,  17,  18,  19,  20,  21,  22,  23,
   24,  25,  26,  27,  28,  29,  30,  31,
  /* #32 */
   32,  33,  34,  35, 162,  37,  38,  39,	// $
   40,  41,  42,  43,  44,  45,  46,  47,
   48,  49,  50,  51,  52,  53,  54,  55,
   56,  57,  58,  59,  60,  61,  62,  63,
  /* #64 */
  160,  65,  66,  67,  68,  69,  70,  71,	// @
   72,  73,  74,  75,  76,  77,  78,  79,
   80,  81,  82,  83,  84,  85,  86,  87,
   88,  89,  90, 250, 251, 252,  29, 196,	// [ \ ] ^ _
  /* #96 */
   39,  97,  98,  99, 100, 101, 102, 103,	// `
  104, 105, 106, 107, 108, 109, 110, 111,
  112, 113, 114, 115, 116, 117, 118, 119,
  120, 121, 122, 253, 254, 255, 206,  32,	// { | } ~ DEL
  /* #128 */
  128, 129, 130, 131, 132, 133, 134, 135,
  136, 137, 138, 139, 140, 141, 142, 143,
  144, 145, 146, 147, 148, 149, 150, 151,
  152, 153, 154, 155, 156, 157, 158, 159,
  /* #160 */
   32,  64, 177, 161,  36, 163, 254,  95,	// SPC ¡ ¢ £ CURR ¥ | §
   34, 169, 170,  20, 172, 173, 174, 175,	// " ? ? « ? ? ? ?
  128, 140, 130, 131, 180, 143, 182, 222,	// ° ± ² ³ ? µ ? ·
  184, 129, 186,  21, 139, 138, 190,  96,	// ? ¹ ? » 1/4 1/2 ? ¿
  /* #192 */
   65, 226,  65,  65,  91, 174, 188, 169,	// À Á Â Ã Ä Å Æ Ç
  197, 191, 198,  69,  73, 227,  73,  73,	// È É Ê Ë Ì Í Î Ï
   68,  93,  79, 228, 236,  79,  92, 120,	// Ð Ñ Ò Ó Ô Õ Ö ×
  171,  85, 229,  85,  94, 230, 222, 190,	// Ø Ù Ú Û Ü Ý ? ß
  /* #224 */
  127, 231,  97,  97, 123, 175, 189, 200,	// à á â ã ä å æ ç
  164, 165, 199, 101, 167, 232, 105, 105,	// è é ê ë ì í î ï
  240, 125, 168, 233, 237, 111, 124,  58,	// ? ñ ò ó ô õ ö ÷
  172, 166, 234, 117, 126, 235, 254, 121 	// ø ù ú û ü ý ? ÿ
};

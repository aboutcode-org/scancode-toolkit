/* CPU data for m32c.

THIS FILE IS MACHINE GENERATED WITH CGEN.

Copyright 1996-2005 Free Software Foundation, Inc.

This file is part of the GNU Binutils and/or GDB, the GNU debugger.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.

*/

#include "sysdep.h"
#include <stdio.h>
#include <stdarg.h>
#include "ansidecl.h"
#include "bfd.h"
#include "symcat.h"
#include "m32c-desc.h"
#include "m32c-opc.h"
#include "opintl.h"
#include "libiberty.h"
#include "xregex.h"

/* Attributes.  */

static const CGEN_ATTR_ENTRY bool_attr[] =
{
  { "#f", 0 },
  { "#t", 1 },
  { 0, 0 }
};

static const CGEN_ATTR_ENTRY MACH_attr[] ATTRIBUTE_UNUSED =
{
  { "base", MACH_BASE },
  { "m16c", MACH_M16C },
  { "m32c", MACH_M32C },
  { "max", MACH_MAX },
  { 0, 0 }
};

static const CGEN_ATTR_ENTRY ISA_attr[] ATTRIBUTE_UNUSED =
{
  { "m16c", ISA_M16C },
  { "m32c", ISA_M32C },
  { "max", ISA_MAX },
  { 0, 0 }
};

static const CGEN_ATTR_ENTRY RL_TYPE_attr[] ATTRIBUTE_UNUSED =
{
  { "NONE", RL_TYPE_NONE },
  { "JUMP", RL_TYPE_JUMP },
  { "1ADDR", RL_TYPE_1ADDR },
  { "2ADDR", RL_TYPE_2ADDR },
  { 0, 0 }
};

const CGEN_ATTR_TABLE m32c_cgen_ifield_attr_table[] =
{
  { "MACH", & MACH_attr[0], & MACH_attr[0] },
  { "ISA", & ISA_attr[0], & ISA_attr[0] },
  { "RL_TYPE", & RL_TYPE_attr[0], & RL_TYPE_attr[0] },
  { "VIRTUAL", &bool_attr[0], &bool_attr[0] },
  { "PCREL-ADDR", &bool_attr[0], &bool_attr[0] },
  { "ABS-ADDR", &bool_attr[0], &bool_attr[0] },
  { "RESERVED", &bool_attr[0], &bool_attr[0] },
  { "SIGN-OPT", &bool_attr[0], &bool_attr[0] },
  { "SIGNED", &bool_attr[0], &bool_attr[0] },
  { 0, 0, 0 }
};

const CGEN_ATTR_TABLE m32c_cgen_hardware_attr_table[] =
{
  { "MACH", & MACH_attr[0], & MACH_attr[0] },
  { "ISA", & ISA_attr[0], & ISA_attr[0] },
  { "RL_TYPE", & RL_TYPE_attr[0], & RL_TYPE_attr[0] },
  { "VIRTUAL", &bool_attr[0], &bool_attr[0] },
  { "CACHE-ADDR", &bool_attr[0], &bool_attr[0] },
  { "PC", &bool_attr[0], &bool_attr[0] },
  { "PROFILE", &bool_attr[0], &bool_attr[0] },
  { 0, 0, 0 }
};

const CGEN_ATTR_TABLE m32c_cgen_operand_attr_table[] =
{
  { "MACH", & MACH_attr[0], & MACH_attr[0] },
  { "ISA", & ISA_attr[0], & ISA_attr[0] },
  { "RL_TYPE", & RL_TYPE_attr[0], & RL_TYPE_attr[0] },
  { "VIRTUAL", &bool_attr[0], &bool_attr[0] },
  { "PCREL-ADDR", &bool_attr[0], &bool_attr[0] },
  { "ABS-ADDR", &bool_attr[0], &bool_attr[0] },
  { "SIGN-OPT", &bool_attr[0], &bool_attr[0] },
  { "SIGNED", &bool_attr[0], &bool_attr[0] },
  { "NEGATIVE", &bool_attr[0], &bool_attr[0] },
  { "RELAX", &bool_attr[0], &bool_attr[0] },
  { "SEM-ONLY", &bool_attr[0], &bool_attr[0] },
  { 0, 0, 0 }
};

const CGEN_ATTR_TABLE m32c_cgen_insn_attr_table[] =
{
  { "MACH", & MACH_attr[0], & MACH_attr[0] },
  { "ISA", & ISA_attr[0], & ISA_attr[0] },
  { "RL_TYPE", & RL_TYPE_attr[0], & RL_TYPE_attr[0] },
  { "ALIAS", &bool_attr[0], &bool_attr[0] },
  { "VIRTUAL", &bool_attr[0], &bool_attr[0] },
  { "UNCOND-CTI", &bool_attr[0], &bool_attr[0] },
  { "COND-CTI", &bool_attr[0], &bool_attr[0] },
  { "SKIP-CTI", &bool_attr[0], &bool_attr[0] },
  { "DELAY-SLOT", &bool_attr[0], &bool_attr[0] },
  { "RELAXABLE", &bool_attr[0], &bool_attr[0] },
  { "RELAXED", &bool_attr[0], &bool_attr[0] },
  { "NO-DIS", &bool_attr[0], &bool_attr[0] },
  { "PBB", &bool_attr[0], &bool_attr[0] },
  { 0, 0, 0 }
};

/* Instruction set variants.  */

static const CGEN_ISA m32c_cgen_isa_table[] = {
  { "m16c", 32, 32, 8, 56 },
  { "m32c", 32, 32, 8, 80 },
  { 0, 0, 0, 0, 0 }
};

/* Machine variants.  */

static const CGEN_MACH m32c_cgen_mach_table[] = {
  { "m16c", "m16c", MACH_M16C, 0 },
  { "m32c", "m32c", MACH_M32C, 0 },
  { 0, 0, 0, 0 }
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_entries[] =
{
  { "r0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r1", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "r2", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "r3", 3, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr =
{
  & m32c_cgen_opval_h_gr_entries[0],
  4,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_QI_entries[] =
{
  { "r0l", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r0h", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "r1l", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "r1h", 3, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr_QI =
{
  & m32c_cgen_opval_h_gr_QI_entries[0],
  4,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_HI_entries[] =
{
  { "r0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r1", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "r2", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "r3", 3, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr_HI =
{
  & m32c_cgen_opval_h_gr_HI_entries[0],
  4,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_SI_entries[] =
{
  { "r2r0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r3r1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr_SI =
{
  & m32c_cgen_opval_h_gr_SI_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_ext_QI_entries[] =
{
  { "r0l", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r1l", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr_ext_QI =
{
  & m32c_cgen_opval_h_gr_ext_QI_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_gr_ext_HI_entries[] =
{
  { "r0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_gr_ext_HI =
{
  & m32c_cgen_opval_h_gr_ext_HI_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r0l_entries[] =
{
  { "r0l", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r0l =
{
  & m32c_cgen_opval_h_r0l_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r0h_entries[] =
{
  { "r0h", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r0h =
{
  & m32c_cgen_opval_h_r0h_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r1l_entries[] =
{
  { "r1l", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r1l =
{
  & m32c_cgen_opval_h_r1l_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r1h_entries[] =
{
  { "r1h", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r1h =
{
  & m32c_cgen_opval_h_r1h_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r0_entries[] =
{
  { "r0", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r0 =
{
  & m32c_cgen_opval_h_r0_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r1_entries[] =
{
  { "r1", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r1 =
{
  & m32c_cgen_opval_h_r1_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r2_entries[] =
{
  { "r2", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r2 =
{
  & m32c_cgen_opval_h_r2_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r3_entries[] =
{
  { "r3", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r3 =
{
  & m32c_cgen_opval_h_r3_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r0l_r0h_entries[] =
{
  { "r0l", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "r0h", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r0l_r0h =
{
  & m32c_cgen_opval_h_r0l_r0h_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r2r0_entries[] =
{
  { "r2r0", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r2r0 =
{
  & m32c_cgen_opval_h_r2r0_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r3r1_entries[] =
{
  { "r3r1", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r3r1 =
{
  & m32c_cgen_opval_h_r3r1_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_r1r2r0_entries[] =
{
  { "r1r2r0", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_r1r2r0 =
{
  & m32c_cgen_opval_h_r1r2r0_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_ar_entries[] =
{
  { "a0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "a1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_ar =
{
  & m32c_cgen_opval_h_ar_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_ar_QI_entries[] =
{
  { "a0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "a1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_ar_QI =
{
  & m32c_cgen_opval_h_ar_QI_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_ar_HI_entries[] =
{
  { "a0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "a1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_ar_HI =
{
  & m32c_cgen_opval_h_ar_HI_entries[0],
  2,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_ar_SI_entries[] =
{
  { "a1a0", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_ar_SI =
{
  & m32c_cgen_opval_h_ar_SI_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_a0_entries[] =
{
  { "a0", 0, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_a0 =
{
  & m32c_cgen_opval_h_a0_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_a1_entries[] =
{
  { "a1", 1, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_a1 =
{
  & m32c_cgen_opval_h_a1_entries[0],
  1,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cond16_entries[] =
{
  { "geu", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "c", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "gtu", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "eq", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "z", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "n", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "le", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "o", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "ge", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "ltu", 248, {0, {{{0, 0}}}}, 0, 0 },
  { "nc", 248, {0, {{{0, 0}}}}, 0, 0 },
  { "leu", 249, {0, {{{0, 0}}}}, 0, 0 },
  { "ne", 250, {0, {{{0, 0}}}}, 0, 0 },
  { "nz", 250, {0, {{{0, 0}}}}, 0, 0 },
  { "pz", 251, {0, {{{0, 0}}}}, 0, 0 },
  { "gt", 252, {0, {{{0, 0}}}}, 0, 0 },
  { "no", 253, {0, {{{0, 0}}}}, 0, 0 },
  { "lt", 254, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cond16 =
{
  & m32c_cgen_opval_h_cond16_entries[0],
  18,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cond16c_entries[] =
{
  { "geu", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "c", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "gtu", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "eq", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "z", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "n", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "ltu", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "nc", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "leu", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "ne", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "nz", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "pz", 7, {0, {{{0, 0}}}}, 0, 0 },
  { "le", 8, {0, {{{0, 0}}}}, 0, 0 },
  { "o", 9, {0, {{{0, 0}}}}, 0, 0 },
  { "ge", 10, {0, {{{0, 0}}}}, 0, 0 },
  { "gt", 12, {0, {{{0, 0}}}}, 0, 0 },
  { "no", 13, {0, {{{0, 0}}}}, 0, 0 },
  { "lt", 14, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cond16c =
{
  & m32c_cgen_opval_h_cond16c_entries[0],
  18,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cond16j_entries[] =
{
  { "le", 8, {0, {{{0, 0}}}}, 0, 0 },
  { "o", 9, {0, {{{0, 0}}}}, 0, 0 },
  { "ge", 10, {0, {{{0, 0}}}}, 0, 0 },
  { "gt", 12, {0, {{{0, 0}}}}, 0, 0 },
  { "no", 13, {0, {{{0, 0}}}}, 0, 0 },
  { "lt", 14, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cond16j =
{
  & m32c_cgen_opval_h_cond16j_entries[0],
  6,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cond16j_5_entries[] =
{
  { "geu", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "c", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "gtu", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "eq", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "z", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "n", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "ltu", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "nc", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "leu", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "ne", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "nz", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "pz", 7, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cond16j_5 =
{
  & m32c_cgen_opval_h_cond16j_5_entries[0],
  12,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cond32_entries[] =
{
  { "ltu", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "nc", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "leu", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "ne", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "nz", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "pz", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "no", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "gt", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "ge", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "geu", 8, {0, {{{0, 0}}}}, 0, 0 },
  { "c", 8, {0, {{{0, 0}}}}, 0, 0 },
  { "gtu", 9, {0, {{{0, 0}}}}, 0, 0 },
  { "eq", 10, {0, {{{0, 0}}}}, 0, 0 },
  { "z", 10, {0, {{{0, 0}}}}, 0, 0 },
  { "n", 11, {0, {{{0, 0}}}}, 0, 0 },
  { "o", 12, {0, {{{0, 0}}}}, 0, 0 },
  { "le", 13, {0, {{{0, 0}}}}, 0, 0 },
  { "lt", 14, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cond32 =
{
  & m32c_cgen_opval_h_cond32_entries[0],
  18,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cr1_32_entries[] =
{
  { "dct0", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "dct1", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "flg", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "svf", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "drc0", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "drc1", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "dmd0", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "dmd1", 7, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cr1_32 =
{
  & m32c_cgen_opval_h_cr1_32_entries[0],
  8,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cr2_32_entries[] =
{
  { "intb", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "sp", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "sb", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "fb", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "svp", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "vct", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "isp", 7, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cr2_32 =
{
  & m32c_cgen_opval_h_cr2_32_entries[0],
  7,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cr3_32_entries[] =
{
  { "dma0", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "dma1", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "dra0", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "dra1", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "dsa0", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "dsa1", 7, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cr3_32 =
{
  & m32c_cgen_opval_h_cr3_32_entries[0],
  6,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_cr_16_entries[] =
{
  { "intbl", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "intbh", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "flg", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "isp", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "sp", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "sb", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "fb", 7, {0, {{{0, 0}}}}, 0, 0 }
};

CGEN_KEYWORD m32c_cgen_opval_h_cr_16 =
{
  & m32c_cgen_opval_h_cr_16_entries[0],
  7,
  0, 0, 0, 0, ""
};

static CGEN_KEYWORD_ENTRY m32c_cgen_opval_h_flags_entries[] =
{
  { "c", 0, {0, {{{0, 0}}}}, 0, 0 },
  { "d", 1, {0, {{{0, 0}}}}, 0, 0 },
  { "z", 2, {0, {{{0, 0}}}}, 0, 0 },
  { "s", 3, {0, {{{0, 0}}}}, 0, 0 },
  { "b", 4, {0, {{{0, 0}}}}, 0, 0 },
  { "o", 5, {0, {{{0, 0}}}}, 0, 0 },
  { "i", 6, {0, {{{0, 0}}}}, 0, 0 },
  { "u", 7, {0, {{{0, 0}}}}, 0, 0 }
};



// EPOS--  Memory Map for the PC

// This work is licensed under the Creative Commons 
// Attribution-NonCommercial-NoDerivs License. To view a copy of this license, 
// visit http://creativecommons.org/licenses/by-nc-nd/2.0/ or send a letter to 
// Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.

#ifndef __memory_map_pc_h
#define __memory_map_pc_h

__BEGIN_SYS

template <>
struct Memory_Map<PC>
{
    enum {
	MEM_BASE =		0,
	MEM_SIZE =	32 * 1024 * 1024
    };

    /*enum {
	BASE =		0x00000000,
	TOP =		0xffffffff,
	APP_LO =	0x00000000,
	APP_CODE =	0x00000000,
	APP_DATA =	0x00400000,
	APP_HI =	0x7fffffff,
	PHY_MEM =	0x80000000,
	IO_MEM =	0xd0000000,
	SYS =		0xafc00000,
	INT_VEC =	SYS + 0x00000000,
	SYS_PT =	SYS + 0x00002000,
	SYS_PD =	SYS + 0x00003000,
	SYS_INFO =	SYS + 0x00004000,
	SYS_CODE =	SYS + 0x00300000,
	SYS_DATA =	SYS + 0x00340000,
	SYS_STACK =	SYS + 0x003c0000,
	MACH1 =		SYS + 0x00001000,
	MACH2 =		TOP,
	MACH3 =		TOP,
    };*/
    
    enum {
	BASE =		0x00000000,
	TOP =		0x20000000,
	APP_LO =	0x00008000,
	APP_CODE =	0x00008000,
	APP_DATA =	0x00400000,
	APP_HI =	0x0fffffff,
	PHY_MEM =	0x10000000,
	IO_MEM =	0x20000000,
	SYS =		0x1f400000,
	INT_VEC =	SYS + 0x00000000,
	GDT =		SYS + 0x00001000,
	SYS_PT =	SYS + 0x00002000,
	SYS_PD =	SYS + 0x00003000,
	SYS_INFO =	SYS + 0x00004000,
	SYS_CODE =	SYS + 0x00300000,
	SYS_DATA =	SYS + 0x00340000,
	SYS_STACK =	SYS + 0x003c0000,
	MACH1 =		SYS + 0x00001000, //GDT
	MACH2 =		TOP,
	MACH3 =		TOP,
    };
};

__END_SYS

#endif

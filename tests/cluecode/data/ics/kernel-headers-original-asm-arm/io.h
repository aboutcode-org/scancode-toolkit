/*
 *  linux/include/asm-arm/io.h
 *
 *  Copyright (C) 1996-2000 Russell King
 *
 * This program is free software; you can redistribute it and/or modify
 * IO port primitives for more information.
 */
#ifdef __mem_pci
#define readb(c) ({ __u8  __v = __raw_readb(__mem_pci(c)); __v; })
#define readw(c) ({ __u16 __v = le16_to_cpu((__force __le16) \
					__raw_readw(__mem_pci(c))); __v; })
#define readl(c) ({ __u32 __v = le32_to_cpu((__force __le32) \
					__raw_readl(__mem_pci(c))); __v; })
#define readb_relaxed(addr) readb(addr)
#define readw_relaxed(addr) readw(addr)
#define readsw(p,d,l)		__raw_readsw(__mem_pci(p),d,l)
#define readsl(p,d,l)		__raw_readsl(__mem_pci(p),d,l)

#define writeb(v,c)		__raw_writeb(v,__mem_pci(c))
#define writew(v,c)		__raw_writew((__force __u16) \
					cpu_to_le16(v),__mem_pci(c))
#define writel(v,c)		__raw_writel((__force __u32) \
					cpu_to_le32(v),__mem_pci(c))

#define writesb(p,d,l)		__raw_writesb(__mem_pci(p),d,l)
#define writesw(p,d,l)		__raw_writesw(__mem_pci(p),d,l)
#define writesl(p,d,l)		__raw_writesl(__mem_pci(p),d,l)

#define memset_io(c,v,l)	_memset_io(__mem_pci(c),(v),(l))
#define memcpy_fromio(a,c,l)	_memcpy_fromio((a),__mem_pci(c),(l))
#define memcpy_toio(c,a,l)	_memcpy_toio(__mem_pci(c),(a),(l))

#define eth_io_copy_and_sum(s,c,l,b) \
				eth_copy_and_sum((s),__mem_pci(c),(l),(b))

static inline int

#elif !defined(readb)

#define readb(c)			(__readwrite_bug("readb"),0)
#define readw(c)			(__readwrite_bug("readw"),0)
#define readl(c)			(__readwrite_bug("readl"),0)
#define writeb(v,c)			__readwrite_bug("writeb")
#define writew(v,c)			__readwrite_bug("writew")
/*
   * Copyright (c) 2003-2007, Virtual Iron Software, Inc.
   *
   * Portions have been modified by Virtual Iron Software, Inc.
   * (c) 2007. This file and the modifications can be redistributed and/or
   * modified under the terms and conditions of the GNU General Public
   * License, version 2.1 and not any later version of the GPL, as published
   * by the Free Software Foundation. 
   *
   * This improves the performance of Standard VGA,
   * the mode used during Windows boot and by the Linux
   * splash screen.
   *
   * It does so by buffering all the stdvga programmed output ops
   * and memory mapped ops (both reads and writes) that are sent to QEMU.
   *
   * We maintain locally essential VGA state so we can respond
   * immediately to input and read ops without waiting for
   * QEMU. We snoop output and write ops to keep our state
   * up-to-date.
   *
   * PIO input ops are satisfied from cached state without
   * bothering QEMU.
   *
   * PIO output and mmio ops are passed through to QEMU, including
   * mmio read ops. This is necessary because mmio reads
   * can have side effects.
   */

#include <xen/config.h>
#include <xen/types.h>
#include <xen/sched.h>
#include <xen/domain_page.h>
#include <asm/hvm/support.h>
#include <xen/numa.h>
#include <xen/paging.h>

#define VGA_MEM_BASE 0xa0000
#define VGA_MEM_SIZE 0x20000

#define PAT(x) (x)
static const uint32_t mask16[16] = {
  PAT(0x00000000),
  PAT(0x000000ff),
  PAT(0x0000ff00),
  PAT(0x0000ffff),
  PAT(0x00ff0000),
  PAT(0x00ff00ff),
  PAT(0x00ffff00),
  PAT(0x00ffffff),
  PAT(0xff000000),
  PAT(0xff0000ff),
  PAT(0xff00ff00),
  PAT(0xff00ffff),
  PAT(0xffff0000),
  PAT(0xffff00ff),
  PAT(0xffffff00),
  PAT(0xffffffff),
};

/* force some bits to zero */
static const uint8_t sr_mask[8] = {
  (uint8_t)~0xfc,
  (uint8_t)~0xc2,
  (uint8_t)~0xf0,
  (uint8_t)~0xc0,
  (uint8_t)~0xf1,
  (uint8_t)~0xff,
  (uint8_t)~0xff,
  (uint8_t)~0x00,
};

static const uint8_t gr_mask[9] = {
  (uint8_t)~0xf0, /* 0x00 */
  (uint8_t)~0xf0, /* 0x01 */
  (uint8_t)~0xf0, /* 0x02 */
  (uint8_t)~0xe0, /* 0x03 */
  (uint8_t)~0xfc, /* 0x04 */
  (uint8_t)~0x84, /* 0x05 */
  (uint8_t)~0xf0, /* 0x06 */
  (uint8_t)~0xf0, /* 0x07 */
  (uint8_t)~0x00, /* 0x08 */
};

static uint8_t *vram_getb(struct hvm_hw_stdvga *s, unsigned int a)
{
  struct page_info *pg = s->vram_page[(a >> 12) & 0x3f];
  uint8_t *p = __map_domain_page(pg);
  return &p[a & 0xfff];
}

static uint32_t *vram_getl(struct hvm_hw_stdvga *s, unsigned int a)
{
  struct page_info *pg = s->vram_page[(a >> 10) & 0x3f];
  uint32_t *p = __map_domain_page(pg);
  return &p[a & 0x3ff];
}

static void vram_put(struct hvm_hw_stdvga *s, void *p)
{
  unmap_domain_page(p);
}

static int stdvga_outb(uint64_t addr, uint8_t val)
{
  struct hvm_hw_stdvga *s = ¤t->domain->arch.hvm_domain.stdvga;
  int rc = 1, prev_stdvga = s->stdvga;

  switch ( addr )
  {
    case 0x3c4: /* sequencer address register */
      s->sr_index = val;
      break;

    case 0x3c5: /* sequencer data register */
      rc = (s->sr_index < sizeof(s->sr));
      if ( rc )
        s->sr[s->sr_index] = val & sr_mask[s->sr_index] ;
      break;

    case 0x3ce: /* graphics address register */
      s->gr_index = val;
      break;

    case 0x3cf: /* graphics data register */
      rc = (s->gr_index < sizeof(s->gr));
      if ( rc )
        s->gr[s->gr_index] = val & gr_mask[s->gr_index];
      break;

    default:
      rc = 0;
      break;
  }

  /* When in standard vga mode, emulate here all writes to the vram buffer
     * so we can immediately satisfy reads without waiting for qemu. */
  s->stdvga = (s->sr[7] == 0x00);

  if ( !prev_stdvga && s->stdvga )
  {
    /*
       * (Re)start caching of video buffer.
       * XXX TODO: In case of a restart the cache could be unsynced.
       */
    s->cache = 1;
    gdprintk(XENLOG_INFO, "entering stdvga and caching modes\n");
  }
  else if ( prev_stdvga && !s->stdvga )
  {
    gdprintk(XENLOG_INFO, "leaving stdvga\n");
  }

  return rc;
}

static void stdvga_out(uint32_t port, uint32_t bytes, uint32_t val)
{
  switch ( bytes )
  {
    case 1:
      stdvga_outb(port, val);
      break;

    case 2:
      stdvga_outb(port + 0, val >> 0);
      stdvga_outb(port + 1, val >> 8);
      break;

    default:
      break;
  }
}

static int stdvga_intercept_pio(
    int dir, uint32_t port, uint32_t bytes, uint32_t *val)
{
  struct hvm_hw_stdvga *s = ¤t->domain->arch.hvm_domain.stdvga;

  if ( dir == IOREQ_WRITE )
  {
    spin_lock(&s->lock);
    stdvga_out(port, bytes, *val);
    spin_unlock(&s->lock);
  }

  return X86EMUL_UNHANDLEABLE; /* propagate to external ioemu */
}

static unsigned int stdvga_mem_offset(
    struct hvm_hw_stdvga *s, unsigned int mmio_addr)
{
  unsigned int memory_map_mode = (s->gr[6] >> 2) & 3;
  unsigned int offset = mmio_addr & 0x1ffff;

  switch ( memory_map_mode )
  {
    case 0:
      break;
    case 1:
      if ( offset >= 0x10000 )
        goto fail;
      offset += 0; /* assume bank_offset == 0; */
      break;
    case 2:
      offset -= 0x10000;
      if ( offset >= 0x8000 )
        goto fail;
      break;
    default:
    case 3:
      offset -= 0x18000;
      if ( offset >= 0x8000 )
        goto fail;
      break;
  }

  return offset;

fail:
  return ~0u;
}

#define GET_PLANE(data, p) (((data) >> ((p) * 8)) & 0xff)

static uint8_t stdvga_mem_readb(uint64_t addr)
{
  struct hvm_hw_stdvga *s = ¤t->domain->arch.hvm_domain.stdvga;
  int plane;
  uint32_t ret, *vram_l;
  uint8_t *vram_b;

  addr = stdvga_mem_offset(s, addr);
  if ( addr == ~0u )
    return 0xff;

  if ( s->sr[4] & 0x08 )
  {
    /* chain 4 mode : simplest access */
    vram_b = vram_getb(s, addr);
    ret = *vram_b;
    vram_put(s, vram_b);
  }
  else if ( s->gr[5] & 0x10 )
  {
    /* odd/even mode (aka text mode mapping) */
    plane = (s->gr[4] & 2) | (addr & 1);
    vram_b = vram_getb(s, ((addr & ~1) << 1) | plane);
    ret = *vram_b;
    vram_put(s, vram_b);
  }
  else
  {
    /* standard VGA latched access */
    vram_l = vram_getl(s, addr);
    s->latch = *vram_l;
    vram_put(s, vram_l);

    if ( !(s->gr[5] & 0x08) )
    {
      /* read mode 0 */
      plane = s->gr[4];
      ret = GET_PLANE(s->latch, plane);
    }
    else
    {
      /* read mode 1 */
      ret = (s->latch ^ mask16[s->gr[2]]) & mask16[s->gr[7]];
      ret |= ret >> 16;
      ret |= ret >> 8;
      ret = (~ret) & 0xff;
    }
  }

  return ret;
}

static uint64_t stdvga_mem_read(uint64_t addr, uint64_t size)
{
  uint64_t data = 0;

  switch ( size )
  {
    case 1:
      data = stdvga_mem_readb(addr);
      break;

    case 2:
      data = stdvga_mem_readb(addr);
      data |= stdvga_mem_readb(addr + 1) << 8;
      break;

    case 4:
      data = stdvga_mem_readb(addr);
      data |= stdvga_mem_readb(addr + 1) << 8;
      data |= stdvga_mem_readb(addr + 2) << 16;
      data |= stdvga_mem_readb(addr + 3) << 24;
      break;

    case 8:
      data = (uint64_t)(stdvga_mem_readb(addr));
      data |= (uint64_t)(stdvga_mem_readb(addr + 1)) << 8;
      data |= (uint64_t)(stdvga_mem_readb(addr + 2)) << 16;
      data |= (uint64_t)(stdvga_mem_readb(addr + 3)) << 24;
      data |= (uint64_t)(stdvga_mem_readb(addr + 4)) << 32;
      data |= (uint64_t)(stdvga_mem_readb(addr + 5)) << 40;
      data |= (uint64_t)(stdvga_mem_readb(addr + 6)) << 48;
      data |= (uint64_t)(stdvga_mem_readb(addr + 7)) << 56;
      break;

    default:
      gdprintk(XENLOG_WARNING, "invalid io size: %"PRId64"\n", size);
      break;
  }

  return data;
}

static void stdvga_mem_writeb(uint64_t addr, uint32_t val)
{
  struct hvm_hw_stdvga *s = ¤t->domain->arch.hvm_domain.stdvga;
  int plane, write_mode, b, func_select, mask;
  uint32_t write_mask, bit_mask, set_mask, *vram_l;
  uint8_t *vram_b;

  addr = stdvga_mem_offset(s, addr);
  if ( addr == ~0u )
    return;

  if ( s->sr[4] & 0x08 )
  {
    /* chain 4 mode : simplest access */
    plane = addr & 3;
    mask = (1 << plane);
    if ( s->sr[2] & mask )
    {
      vram_b = vram_getb(s, addr);
      *vram_b = val;
      vram_put(s, vram_b);
    }
  }
  else if ( s->gr[5] & 0x10 )
  {
    /* odd/even mode (aka text mode mapping) */
    plane = (s->gr[4] & 2) | (addr & 1);
    mask = (1 << plane);
    if ( s->sr[2] & mask )
    {
      addr = ((addr & ~1) << 1) | plane;
      vram_b = vram_getb(s, addr);
      *vram_b = val;
      vram_put(s, vram_b);
    }
  }
  else
  {
    write_mode = s->gr[5] & 3;
    switch ( write_mode )
    {
      default:
      case 0:
        /* rotate */
        b = s->gr[3] & 7;
        val = ((val >> b) | (val << (8 - b))) & 0xff;
        val |= val << 8;
        val |= val << 16;

        /* apply set/reset mask */
        set_mask = mask16[s->gr[1]];
        val = (val & ~set_mask) | (mask16[s->gr[0]] & set_mask);
        bit_mask = s->gr[8];
        break;
      case 1:
        val = s->latch;
        goto do_write;
      case 2:
        val = mask16[val & 0x0f];
        bit_mask = s->gr[8];
        break;
      case 3:
        /* rotate */
        b = s->gr[3] & 7;
        val = (val >> b) | (val << (8 - b));

        bit_mask = s->gr[8] & val;
        val = mask16[s->gr[0]];
        break;
    }

    /* apply logical operation */
    func_select = s->gr[3] >> 3;
    switch ( func_select )
    {
      case 0:
      default:
        /* nothing to do */
        break;
      case 1:
        /* and */
        val &= s->latch;
        break;
      case 2:
        /* or */
        val |= s->latch;
        break;
      case 3:
        /* xor */
        val ^= s->latch;
        break;
    }

    /* apply bit mask */
    bit_mask |= bit_mask << 8;
    bit_mask |= bit_mask << 16;
    val = (val & bit_mask) | (s->latch & ~bit_mask);

do_write:
    /* mask data according to sr[2] */
    mask = s->sr[2];
    write_mask = mask16[mask];
    vram_l = vram_getl(s, addr);
    *vram_l = (*vram_l & ~write_mask) | (val & write_mask);
    vram_put(s, vram_l);
  }
}

static void stdvga_mem_write(uint64_t addr, uint64_t data, uint64_t size)
{
  /* Intercept mmio write */
  switch ( size )
  {
    case 1:
      stdvga_mem_writeb(addr, (data >> 0) & 0xff);
      break;

    case 2:
      stdvga_mem_writeb(addr+0, (data >> 0) & 0xff);
      stdvga_mem_writeb(addr+1, (data >> 8) & 0xff);
      break;

    case 4:
      stdvga_mem_writeb(addr+0, (data >> 0) & 0xff);
      stdvga_mem_writeb(addr+1, (data >> 8) & 0xff);
      stdvga_mem_writeb(addr+2, (data >> 16) & 0xff);
      stdvga_mem_writeb(addr+3, (data >> 24) & 0xff);
      break;

    case 8:
      stdvga_mem_writeb(addr+0, (data >> 0) & 0xff);
      stdvga_mem_writeb(addr+1, (data >> 8) & 0xff);
      stdvga_mem_writeb(addr+2, (data >> 16) & 0xff);
      stdvga_mem_writeb(addr+3, (data >> 24) & 0xff);
      stdvga_mem_writeb(addr+4, (data >> 32) & 0xff);
      stdvga_mem_writeb(addr+5, (data >> 40) & 0xff);
      stdvga_mem_writeb(addr+6, (data >> 48) & 0xff);
      stdvga_mem_writeb(addr+7, (data >> 56) & 0xff);
      break;

    default:
      gdprintk(XENLOG_WARNING, "invalid io size: %"PRId64"\n", size);
      break;
  }
}

static uint32_t read_data;

static int mmio_move(struct hvm_hw_stdvga *s, ioreq_t *p)
{
  int i;
  int sign = p->df ? -1 : 1;
  p2m_type_t p2mt;
  struct domain *d = current->domain;

  if ( p->data_is_ptr )
  {
    if ( p->dir == IOREQ_READ )
    {
      uint64_t addr = p->addr, data = p->data, tmp;
      for ( i = 0; i < p->count; i++ ) 
      {
        tmp = stdvga_mem_read(addr, p->size);
        if ( hvm_copy_to_guest_phys(data, &tmp, p->size) !=
            HVMCOPY_okay )
        {
          struct page_info *dp = get_page_from_gfn(
              d, data >> PAGE_SHIFT, &p2mt, P2M_ALLOC);
          /*
             * The only case we handle is vga_mem <-> vga_mem.
             * Anything else disables caching and leaves it to qemu-dm.
             */
          if ( (p2mt != p2m_mmio_dm) || (data < VGA_MEM_BASE) ||
              ((data + p->size) > (VGA_MEM_BASE + VGA_MEM_SIZE)) )
          {
            if ( dp )
              put_page(dp);
            return 0;
          }
          ASSERT(!dp);
          stdvga_mem_write(data, tmp, p->size);
        }
        data += sign * p->size;
        addr += sign * p->size;
      }
    }
    else
    {
      uint32_t addr = p->addr, data = p->data, tmp;
      for ( i = 0; i < p->count; i++ )
      {
        if ( hvm_copy_from_guest_phys(&tmp, data, p->size) !=
            HVMCOPY_okay )
        {
          struct page_info *dp = get_page_from_gfn(
              d, data >> PAGE_SHIFT, &p2mt, P2M_ALLOC);
          if ( (p2mt != p2m_mmio_dm) || (data < VGA_MEM_BASE) ||
              ((data + p->size) > (VGA_MEM_BASE + VGA_MEM_SIZE)) )
          {
            if ( dp )
              put_page(dp);
            return 0;
          }
          ASSERT(!dp);
          tmp = stdvga_mem_read(data, p->size);
        }
        stdvga_mem_write(addr, tmp, p->size);
        data += sign * p->size;
        addr += sign * p->size;
      }
    }
  }
  else
  {
    if ( p->dir == IOREQ_READ )
    {
      uint32_t addr = p->addr;
      for ( i = 0; i < p->count; i++ )
      {
        p->data = stdvga_mem_read(addr, p->size);
        addr += sign * p->size;
      }
    }
    else
    {
      uint32_t addr = p->addr;
      for ( i = 0; i < p->count; i++ )
      {
        stdvga_mem_write(addr, p->data, p->size);
        addr += sign * p->size;
      }
    }
  }

  read_data = p->data;
  return 1;
}

static int stdvga_intercept_mmio(ioreq_t *p)
{
  struct domain *d = current->domain;
  struct hvm_hw_stdvga *s = &d->arch.hvm_domain.stdvga;
  int buf = 0, rc;

  if ( p->size > 8 )
  {
    gdprintk(XENLOG_WARNING, "invalid mmio size %d\n", (int)p->size);
    return X86EMUL_UNHANDLEABLE;
  }

  spin_lock(&s->lock);

  if ( s->stdvga && s->cache )
  {
    switch ( p->type )
    {
      case IOREQ_TYPE_COPY:
        buf = mmio_move(s, p);
        if ( !buf )
          s->cache = 0;
        break;
      default:
        gdprintk(XENLOG_WARNING, "unsupported mmio request type:%d "
            "addr:0x%04x data:0x%04x size:%d count:%d state:%d "
            "isptr:%d dir:%d df:%d\n",
            p->type, (int)p->addr, (int)p->data, (int)p->size,
            (int)p->count, p->state,
            p->data_is_ptr, p->dir, p->df);
        s->cache = 0;
    }
  }
  else
  {
    buf = (p->dir == IOREQ_WRITE);
  }

  rc = (buf && hvm_buffered_io_send(p));

  spin_unlock(&s->lock);

  return rc ? X86EMUL_OKAY : X86EMUL_UNHANDLEABLE;
}

void stdvga_init(struct domain *d)
{
  struct hvm_hw_stdvga *s = &d->arch.hvm_domain.stdvga;
  struct page_info *pg;
  void *p;
  int i;

  memset(s, 0, sizeof(*s));
  spin_lock_init(&s->lock);

  for ( i = 0; i != ARRAY_SIZE(s->vram_page); i++ )
  {
    pg = alloc_domheap_page(NULL, MEMF_node(domain_to_node(d)));
    if ( pg == NULL )
      break;
    s->vram_page[i] = pg;
    p = __map_domain_page(pg);
    clear_page(p);
    unmap_domain_page(p);
  }

  if ( i == ARRAY_SIZE(s->vram_page) )
  {
    /* Sequencer registers. */
    register_portio_handler(d, 0x3c4, 2, stdvga_intercept_pio);
    /* Graphics registers. */
    register_portio_handler(d, 0x3ce, 2, stdvga_intercept_pio);
    /* MMIO. */
    register_buffered_io_handler(
        d, VGA_MEM_BASE, VGA_MEM_SIZE, stdvga_intercept_mmio);
  }
}

void stdvga_deinit(struct domain *d)
{
  struct hvm_hw_stdvga *s = &d->arch.hvm_domain.stdvga;
  int i;

  for ( i = 0; i != ARRAY_SIZE(s->vram_page); i++ )
  {
    if ( s->vram_page[i] == NULL )
      continue;
    free_domheap_page(s->vram_page[i]);
    s->vram_page[i] = NULL;
  }
}

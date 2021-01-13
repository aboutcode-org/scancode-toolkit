/*
 *  Copyright (C) 1997	Wu Ching Chen
 *  2.1.x update (C) 1998  Krzysztof G. Baranowski
 *  2.5.x update (C) 2002  Red Hat <alan@redhat.com>
 *  2.6.x update (C) 2004  Red Hat <alan@redhat.com>
 *
 * Marcelo Tosatti <marcelo@conectiva.com.br> : SMP fixes
 *
 * Wu Ching Chen : NULL pointer fixes  2000/06/02
 *		   support atp876 chip
 *		   enable 32 bit fifo transfer
 *		   support cdrom & remove device run ultra speed
 *		   fix disconnect bug  2000/12/21
 *		   support atp880 chip lvd u160 2001/05/15
 *		   fix prd table bug 2001/09/12 (7.1)
 */

#include <linux/module.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/types.h>
#include <linux/string.h>
#include <linux/ioport.h>
#include <linux/delay.h>
#include <linux/proc_fs.h>
#include <linux/spinlock.h>
#include <linux/pci.h>
#include <linux/blkdev.h>
#include <asm/system.h>
#include <asm/io.h>

#include <scsi/scsi.h>
#include <scsi/scsi_cmnd.h>
#include <scsi/scsi_device.h>
#include <scsi/scsi_host.h>

#include "atp870u.h"

static struct scsi_host_template atp870u_template;
static void send_s870(struct Scsi_Host *host);


static irqreturn_t atp870u_intr_handle(int irq, void *dev_id,
					struct pt_regs *regs)
{
	unsigned long flags;
	unsigned short int tmpcip, id;
	unsigned char i, j, target_id, lun;
	unsigned char *prd;
	struct scsi_cmnd *workrequ;
	unsigned int workportu, tmport;
	unsigned long adrcntu, k;
	int errstus;
	struct Scsi_Host *host = dev_id;
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;

	dev->in_int = 1;
	workportu = dev->ioport;
	tmport = workportu;

	if (dev->working != 0) {
		tmport += 0x1f;
		j = inb(tmport);
		if ((j & 0x80) == 0) {
			dev->in_int = 0;
			return IRQ_NONE;
		}

		tmpcip = dev->pciport;
		if ((inb(tmpcip) & 0x08) != 0) {
			tmpcip += 0x2;
			for (k = 0; k < 1000; k++) {
				if ((inb(tmpcip) & 0x08) == 0) {
					goto stop_dma;
				}
				if ((inb(tmpcip) & 0x01) == 0) {
					goto stop_dma;
				}
			}
		}
stop_dma:
		tmpcip = dev->pciport;
		outb(0x00, tmpcip);
		tmport -= 0x08;

		i = inb(tmport);

		tmport -= 0x02;
		target_id = inb(tmport);
		tmport += 0x02;

		/*
		 *      Remap wide devices onto id numbers
		 */

		if ((target_id & 0x40) != 0) {
			target_id = (target_id & 0x07) | 0x08;
		} else {
			target_id &= 0x07;
		}

		if ((j & 0x40) != 0) {
			if (dev->last_cmd == 0xff) {
				dev->last_cmd = target_id;
			}
			dev->last_cmd |= 0x40;
		}

		if (i == 0x85) {
			if ((dev->last_cmd & 0xf0) != 0x40) {
				dev->last_cmd = 0xff;
			}
			/*
			 *      Flip wide
			 */
			if (dev->wide_idu != 0) {
				tmport = workportu + 0x1b;
				outb(0x01, tmport);
				while ((inb(tmport) & 0x01) != 0x01) {
					outb(0x01, tmport);
				}
			}
			/*
			 *      Issue more commands
			 */
			spin_lock_irqsave(dev->host->host_lock, flags);
			if (((dev->quhdu != dev->quendu) || (dev->last_cmd != 0xff)) && (dev->in_snd == 0)) {
				send_s870(host);
			}
			spin_unlock_irqrestore(dev->host->host_lock, flags);
			/*
			 *      Done
			 */
			dev->in_int = 0;
			goto out;
		}

		if (i == 0x40) {
			dev->last_cmd |= 0x40;
			dev->in_int = 0;
			goto out;
		}

		if (i == 0x21) {
			if ((dev->last_cmd & 0xf0) != 0x40) {
				dev->last_cmd = 0xff;
			}
			tmport -= 0x05;
			adrcntu = 0;
			((unsigned char *) &adrcntu)[2] = inb(tmport++);
			((unsigned char *) &adrcntu)[1] = inb(tmport++);
			((unsigned char *) &adrcntu)[0] = inb(tmport);
			k = dev->id[target_id].last_lenu;
			k -= adrcntu;
			dev->id[target_id].tran_lenu = k;
			dev->id[target_id].last_lenu = adrcntu;
			tmport -= 0x04;
			outb(0x41, tmport);
			tmport += 0x08;
			outb(0x08, tmport);
			dev->in_int = 0;
			goto out;
		}
		if ((i == 0x80) || (i == 0x8f)) {
			lun = 0;
			tmport -= 0x07;
			j = inb(tmport);
			if (j == 0x44 || i == 0x80) {
				tmport += 0x0d;
				lun = inb(tmport) & 0x07;
			} else {
				if ((dev->last_cmd & 0xf0) != 0x40) {
					dev->last_cmd = 0xff;
				}
				if (j == 0x41) {
					tmport += 0x02;
					adrcntu = 0;
					((unsigned char *) &adrcntu)[2] = inb(tmport++);
					((unsigned char *) &adrcntu)[1] = inb(tmport++);
					((unsigned char *) &adrcntu)[0] = inb(tmport);
					k = dev->id[target_id].last_lenu;
					k -= adrcntu;
					dev->id[target_id].tran_lenu = k;
					dev->id[target_id].last_lenu = adrcntu;
					tmport += 0x04;
					outb(0x08, tmport);
					dev->in_int = 0;
					goto out;
				} else {
					outb(0x46, tmport);
					dev->id[target_id].dirctu = 0x00;
					tmport += 0x02;
					outb(0x00, tmport++);
					outb(0x00, tmport++);
					outb(0x00, tmport++);
					tmport += 0x03;
					outb(0x08, tmport);
					dev->in_int = 0;
					goto out;
				}
			}
			if (dev->last_cmd != 0xff) {
				dev->last_cmd |= 0x40;
			}
			tmport = workportu + 0x10;
			outb(0x45, tmport);
			tmport += 0x06;
			target_id = inb(tmport);
			/*
			 *      Remap wide identifiers
			 */
			if ((target_id & 0x10) != 0) {
				target_id = (target_id & 0x07) | 0x08;
			} else {
				target_id &= 0x07;
			}
			workrequ = dev->id[target_id].curr_req;
			tmport = workportu + 0x0f;
			outb(lun, tmport);
			tmport += 0x02;
			outb(dev->id[target_id].devspu, tmport++);
			adrcntu = dev->id[target_id].tran_lenu;
			k = dev->id[target_id].last_lenu;
			outb(((unsigned char *) &k)[2], tmport++);
			outb(((unsigned char *) &k)[1], tmport++);
			outb(((unsigned char *) &k)[0], tmport++);
			/* Remap wide */
			j = target_id;
			if (target_id > 7) {
				j = (j & 0x07) | 0x40;
			}
			/* Add direction */
			j |= dev->id[target_id].dirctu;
			outb(j, tmport++);
			outb(0x80, tmport);

			/* enable 32 bit fifo transfer */
			if (dev->deviceid != 0x8081) {
				tmport = workportu + 0x3a;
				if ((dev->ata_cdbu[0] == 0x08) || (dev->ata_cdbu[0] == 0x28) || (dev->ata_cdbu[0] == 0x0a) || (dev->ata_cdbu[0] == 0x2a)) {
					outb((unsigned char) ((inb(tmport) & 0xf3) | 0x08), tmport);
				} else {
					outb((unsigned char) (inb(tmport) & 0xf3), tmport);
				}
			} else {
				tmport = workportu - 0x05;
				if ((dev->ata_cdbu[0] == 0x08) || (dev->ata_cdbu[0] == 0x28) || (dev->ata_cdbu[0] == 0x0a) || (dev->ata_cdbu[0] == 0x2a)) {
					outb((unsigned char) ((inb(tmport) & 0x3f) | 0xc0), tmport);
				} else {
					outb((unsigned char) (inb(tmport) & 0x3f), tmport);
				}
			}

			tmport = workportu + 0x1b;
			j = 0;
			id = 1;
			id = id << target_id;
			/*
			 *      Is this a wide device
			 */
			if ((id & dev->wide_idu) != 0) {
				j |= 0x01;
			}
			outb(j, tmport);
			while ((inb(tmport) & 0x01) != j) {
				outb(j, tmport);
			}

			if (dev->id[target_id].last_lenu == 0) {
				tmport = workportu + 0x18;
				outb(0x08, tmport);
				dev->in_int = 0;
				goto out;
			}
			prd = dev->id[target_id].prd_posu;
			while (adrcntu != 0) {
				id = ((unsigned short int *) (prd))[2];
				if (id == 0) {
					k = 0x10000;
				} else {
					k = id;
				}
				if (k > adrcntu) {
					((unsigned short int *) (prd))[2] = (unsigned short int)
					    (k - adrcntu);
					((unsigned long *) (prd))[0] += adrcntu;
					adrcntu = 0;
					dev->id[target_id].prd_posu = prd;
				} else {
					adrcntu -= k;
					dev->id[target_id].prdaddru += 0x08;
					prd += 0x08;
					if (adrcntu == 0) {
						dev->id[target_id].prd_posu = prd;
					}
				}
			}
			tmpcip = dev->pciport + 0x04;
			outl(dev->id[target_id].prdaddru, tmpcip);
			tmpcip -= 0x02;
			outb(0x06, tmpcip);
			outb(0x00, tmpcip);
			tmpcip -= 0x02;
			tmport = workportu + 0x18;
			/*
			 *      Check transfer direction
			 */
			if (dev->id[target_id].dirctu != 0) {
				outb(0x08, tmport);
				outb(0x01, tmpcip);
				dev->in_int = 0;
				goto out;
			}
			outb(0x08, tmport);
			outb(0x09, tmpcip);
			dev->in_int = 0;
			goto out;
		}

		/*
		 *      Current scsi request on this target
		 */

		workrequ = dev->id[target_id].curr_req;

		if (i == 0x42) {
			if ((dev->last_cmd & 0xf0) != 0x40) {
				dev->last_cmd = 0xff;
			}
			errstus = 0x02;
			workrequ->result = errstus;
			goto go_42;
		}
		if (i == 0x16) {
			if ((dev->last_cmd & 0xf0) != 0x40) {
				dev->last_cmd = 0xff;
			}
			errstus = 0;
			tmport -= 0x08;
			errstus = inb(tmport);
			workrequ->result = errstus;
go_42:
			/*
			 *      Complete the command
			 */
			 
			if (workrequ->use_sg) {
				pci_unmap_sg(dev->pdev,
					(struct scatterlist *)workrequ->buffer,
					workrequ->use_sg,
					workrequ->sc_data_direction);
			} else if (workrequ->request_bufflen &&
					workrequ->sc_data_direction != DMA_NONE) {
				pci_unmap_single(dev->pdev,
					workrequ->SCp.dma_handle,
					workrequ->request_bufflen,
					workrequ->sc_data_direction);
			}
			spin_lock_irqsave(dev->host->host_lock, flags);
			(*workrequ->scsi_done) (workrequ);

			/*
			 *      Clear it off the queue
			 */
			dev->id[target_id].curr_req = NULL;
			dev->working--;
			spin_unlock_irqrestore(dev->host->host_lock, flags);
			/*
			 *      Take it back wide
			 */
			if (dev->wide_idu != 0) {
				tmport = workportu + 0x1b;
				outb(0x01, tmport);
				while ((inb(tmport) & 0x01) != 0x01) {
					outb(0x01, tmport);
				}
			}
			/*
			 *      If there is stuff to send and nothing going then send it
			 */
			spin_lock_irqsave(dev->host->host_lock, flags);
			if (((dev->last_cmd != 0xff) || (dev->quhdu != dev->quendu)) && (dev->in_snd == 0)) {
				send_s870(host);
			}
			spin_unlock_irqrestore(dev->host->host_lock, flags);
			dev->in_int = 0;
			goto out;
		}
		if ((dev->last_cmd & 0xf0) != 0x40) {
			dev->last_cmd = 0xff;
		}
		if (i == 0x4f) {
			i = 0x89;
		}
		i &= 0x0f;
		if (i == 0x09) {
			tmpcip = tmpcip + 4;
			outl(dev->id[target_id].prdaddru, tmpcip);
			tmpcip = tmpcip - 2;
			outb(0x06, tmpcip);
			outb(0x00, tmpcip);
			tmpcip = tmpcip - 2;
			tmport = workportu + 0x10;
			outb(0x41, tmport);
			dev->id[target_id].dirctu = 0x00;
			tmport += 0x08;
			outb(0x08, tmport);
			outb(0x09, tmpcip);
			dev->in_int = 0;
			goto out;
		}
		if (i == 0x08) {
			tmpcip = tmpcip + 4;
			outl(dev->id[target_id].prdaddru, tmpcip);
			tmpcip = tmpcip - 2;
			outb(0x06, tmpcip);
			outb(0x00, tmpcip);
			tmpcip = tmpcip - 2;
			tmport = workportu + 0x10;
			outb(0x41, tmport);
			tmport += 0x05;
			outb((unsigned char) (inb(tmport) | 0x20), tmport);
			dev->id[target_id].dirctu = 0x20;
			tmport += 0x03;
			outb(0x08, tmport);
			outb(0x01, tmpcip);
			dev->in_int = 0;
			goto out;
		}
		tmport -= 0x07;
		if (i == 0x0a) {
			outb(0x30, tmport);
		} else {
			outb(0x46, tmport);
		}
		dev->id[target_id].dirctu = 0x00;
		tmport += 0x02;
		outb(0x00, tmport++);
		outb(0x00, tmport++);
		outb(0x00, tmport++);
		tmport += 0x03;
		outb(0x08, tmport);
		dev->in_int = 0;
		goto out;
	} else {
//              tmport = workportu + 0x17;
//              inb(tmport);
//              dev->working = 0;
		dev->in_int = 0;
	}
out:
	return IRQ_HANDLED;
}

/**
 *	atp870u_queuecommand	-	Queue SCSI command
 *	@req_p: request block
 *	@done: completion function
 *
 *	Queue a command to the ATP queue. Called with the host lock held.
 */
 
static int atp870u_queuecommand(struct scsi_cmnd *req_p,
		void (*done) (struct scsi_cmnd *))
{
	unsigned short int m;
	unsigned int tmport;
	struct Scsi_Host *host;
	struct atp_unit *dev;

	if (req_p->device->channel != 0) {
		req_p->result = 0x00040000;
		done(req_p);
		return 0;
	};

	host = req_p->device->host;
	dev = (struct atp_unit *)&host->hostdata;
	
	m = 1;
	m = m << req_p->device->id;

	/*
	 *      Fake a timeout for missing targets
	 */

	if ((m & dev->active_idu) == 0) {
		req_p->result = 0x00040000;
		done(req_p);
		return 0;
	}
	if (done) {
		req_p->scsi_done = done;
	} else {
		printk(KERN_WARNING "atp870u_queuecommand: done can't be NULL\n");
		req_p->result = 0;
		done(req_p);
		return 0;
	}
	/*
	 *      Count new command
	 */

	dev->quendu++;
	if (dev->quendu >= qcnt) {
		dev->quendu = 0;
	}
	/*
	 *      Check queue state
	 */
	if (dev->quhdu == dev->quendu) {
		if (dev->quendu == 0) {
			dev->quendu = qcnt;
		}
		dev->quendu--;
		req_p->result = 0x00020000;
		done(req_p);
		return 0;
	}
	dev->querequ[dev->quendu] = req_p;
	tmport = dev->ioport + 0x1c;
	if ((inb(tmport) == 0) && (dev->in_int == 0) && (dev->in_snd == 0)) {
		send_s870(host);
	}
	return 0;
}

/**
 *	send_s870	-	send a command to the controller
 *	@host: host
 *
 *	On entry there is work queued to be done. We move some of that work to the
 *	controller itself. 
 *
 *	Caller holds the host lock.
 */
 
static void send_s870(struct Scsi_Host *host)
{
	unsigned int tmport;
	struct scsi_cmnd *workrequ;
	unsigned int i;
	unsigned char j, target_id;
	unsigned char *prd;
	unsigned short int tmpcip, w;
	unsigned long l;
	dma_addr_t bttl;
	unsigned int workportu;
	struct scatterlist *sgpnt;
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;
	int sg_count;

	if (dev->in_snd != 0) {
		return;
	}
	dev->in_snd = 1;
	if ((dev->last_cmd != 0xff) && ((dev->last_cmd & 0x40) != 0)) {
		dev->last_cmd &= 0x0f;
		workrequ = dev->id[dev->last_cmd].curr_req;
		if (workrequ != NULL) {	/* check NULL pointer */
			goto cmd_subp;
		}
		dev->last_cmd = 0xff;
		if (dev->quhdu == dev->quendu) {
			dev->in_snd = 0;
			return;
		}
	}
	if ((dev->last_cmd != 0xff) && (dev->working != 0)) {
		dev->in_snd = 0;
		return;
	}
	dev->working++;
	j = dev->quhdu;
	dev->quhdu++;
	if (dev->quhdu >= qcnt) {
		dev->quhdu = 0;
	}
	workrequ = dev->querequ[dev->quhdu];
	if (dev->id[workrequ->device->id].curr_req == 0) {
		dev->id[workrequ->device->id].curr_req = workrequ;
		dev->last_cmd = workrequ->device->id;
		goto cmd_subp;
	}
	dev->quhdu = j;
	dev->working--;
	dev->in_snd = 0;
	return;
cmd_subp:
	workportu = dev->ioport;
	tmport = workportu + 0x1f;
	if ((inb(tmport) & 0xb0) != 0) {
		goto abortsnd;
	}
	tmport = workportu + 0x1c;
	if (inb(tmport) == 0) {
		goto oktosend;
	}
abortsnd:
	dev->last_cmd |= 0x40;
	dev->in_snd = 0;
	return;
oktosend:
	memcpy(&dev->ata_cdbu[0], &workrequ->cmnd[0], workrequ->cmd_len);
	if (dev->ata_cdbu[0] == READ_CAPACITY) {
		if (workrequ->request_bufflen > 8) {
			workrequ->request_bufflen = 0x08;
		}
	}
	if (dev->ata_cdbu[0] == 0x00) {
		workrequ->request_bufflen = 0;
	}

	tmport = workportu + 0x1b;
	j = 0;
	target_id = workrequ->device->id;

	/*
	 *      Wide ?
	 */
	w = 1;
	w = w << target_id;
	if ((w & dev->wide_idu) != 0) {
		j |= 0x01;
	}
	outb(j, tmport);
	while ((inb(tmport) & 0x01) != j) {
		outb(j, tmport);
	}

	/*
	 *      Write the command
	 */

	tmport = workportu;
	outb(workrequ->cmd_len, tmport++);
	outb(0x2c, tmport++);
	outb(0xcf, tmport++);
	for (i = 0; i < workrequ->cmd_len; i++) {
		outb(dev->ata_cdbu[i], tmport++);
	}
	tmport = workportu + 0x0f;
	outb(workrequ->device->lun, tmport);
	tmport += 0x02;
	/*
	 *      Write the target
	 */
	outb(dev->id[target_id].devspu, tmport++);

	/*
	 *      Figure out the transfer size
	 */
	if (workrequ->use_sg) {
		l = 0;
		sgpnt = (struct scatterlist *) workrequ->request_buffer;
		sg_count = pci_map_sg(dev->pdev, sgpnt, workrequ->use_sg,
				workrequ->sc_data_direction);
		for (i = 0; i < workrequ->use_sg; i++) {
			if (sgpnt[i].length == 0 || workrequ->use_sg > ATP870U_SCATTER) {
				panic("Foooooooood fight!");
			}
			l += sgpnt[i].length;
		}
	} else if(workrequ->request_bufflen && workrequ->sc_data_direction != PCI_DMA_NONE) {
		workrequ->SCp.dma_handle = pci_map_single(dev->pdev,
				workrequ->request_buffer,
				workrequ->request_bufflen,
				workrequ->sc_data_direction);
		l = workrequ->request_bufflen;
	}
	else l = 0;
	/*
	 *      Write transfer size
	 */
	outb((unsigned char) (((unsigned char *) (&l))[2]), tmport++);
	outb((unsigned char) (((unsigned char *) (&l))[1]), tmport++);
	outb((unsigned char) (((unsigned char *) (&l))[0]), tmport++);
	j = target_id;
	dev->id[j].last_lenu = l;
	dev->id[j].tran_lenu = 0;
	/*
	 *      Flip the wide bits
	 */
	if ((j & 0x08) != 0) {
		j = (j & 0x07) | 0x40;
	}
	/*
	 *      Check transfer direction
	 */
	if (workrequ->sc_data_direction == DMA_TO_DEVICE) {
		outb((unsigned char) (j | 0x20), tmport++);
	} else {
		outb(j, tmport++);
	}
	outb((unsigned char) (inb(tmport) | 0x80), tmport);
	outb(0x80, tmport);
	tmport = workportu + 0x1c;
	dev->id[target_id].dirctu = 0;
	if (l == 0) {
		if (inb(tmport) == 0) {
			tmport = workportu + 0x18;
			outb(0x08, tmport);
		} else {
			dev->last_cmd |= 0x40;
		}
		dev->in_snd = 0;
		return;
	}
	tmpcip = dev->pciport;
	prd = dev->id[target_id].prd_tableu;
	dev->id[target_id].prd_posu = prd;

	/*
	 *      Now write the request list. Either as scatter/gather or as
	 *      a linear chain.
	 */

	if (workrequ->use_sg) {
		sgpnt = (struct scatterlist *) workrequ->request_buffer;
		i = 0;
		for (j = 0; j < workrequ->use_sg; j++) {
			bttl = sg_dma_address(&sgpnt[j]);
			l = sg_dma_len(&sgpnt[j]);
			while (l > 0x10000) {
				(((u16 *) (prd))[i + 3]) = 0x0000;
				(((u16 *) (prd))[i + 2]) = 0x0000;
				(((u32 *) (prd))[i >> 1]) = cpu_to_le32(bttl);
				l -= 0x10000;
				bttl += 0x10000;
				i += 0x04;
			}
			(((u32 *) (prd))[i >> 1]) = cpu_to_le32(bttl);
			(((u16 *) (prd))[i + 2]) = cpu_to_le16(l);
			(((u16 *) (prd))[i + 3]) = 0;
			i += 0x04;
		}
		(((u16 *) (prd))[i - 1]) = cpu_to_le16(0x8000);
	} else {
		/*
		 *      For a linear request write a chain of blocks
		 */
		bttl = workrequ->SCp.dma_handle;
		l = workrequ->request_bufflen;
		i = 0;
		while (l > 0x10000) {
			(((u16 *) (prd))[i + 3]) = 0x0000;
			(((u16 *) (prd))[i + 2]) = 0x0000;
			(((u32 *) (prd))[i >> 1]) = cpu_to_le32(bttl);
			l -= 0x10000;
			bttl += 0x10000;
			i += 0x04;
		}
		(((u16 *) (prd))[i + 3]) = cpu_to_le16(0x8000);
		(((u16 *) (prd))[i + 2]) = cpu_to_le16(l);
		(((u32 *) (prd))[i >> 1]) = cpu_to_le32(bttl);
	}
	tmpcip = tmpcip + 4;
	dev->id[target_id].prdaddru = dev->id[target_id].prd_phys;
	outl(dev->id[target_id].prd_phys, tmpcip);
	tmpcip = tmpcip - 2;
	outb(0x06, tmpcip);
	outb(0x00, tmpcip);
	tmpcip = tmpcip - 2;

	if (dev->deviceid != 0x8081) {
		tmport = workportu + 0x3a;
		if ((dev->ata_cdbu[0] == 0x08) || (dev->ata_cdbu[0] == 0x28) || (dev->ata_cdbu[0] == 0x0a) || (dev->ata_cdbu[0] == 0x2a)) {
			outb((inb(tmport) & 0xf3) | 0x08, tmport);
		} else {
			outb(inb(tmport) & 0xf3, tmport);
		}
	} else {
		tmport = workportu - 0x05;
		if ((dev->ata_cdbu[0] == 0x08) || (dev->ata_cdbu[0] == 0x28) || (dev->ata_cdbu[0] == 0x0a) || (dev->ata_cdbu[0] == 0x2a)) {
			outb((unsigned char) ((inb(tmport) & 0x3f) | 0xc0), tmport);
		} else {
			outb((unsigned char) (inb(tmport) & 0x3f), tmport);
		}
	}
	tmport = workportu + 0x1c;

	if (workrequ->sc_data_direction == DMA_TO_DEVICE) {
		dev->id[target_id].dirctu = 0x20;
		if (inb(tmport) == 0) {
			tmport = workportu + 0x18;
			outb(0x08, tmport);
			outb(0x01, tmpcip);
		} else {
			dev->last_cmd |= 0x40;
		}
		dev->in_snd = 0;
		return;
	}
	if (inb(tmport) == 0) {
		tmport = workportu + 0x18;
		outb(0x08, tmport);
		outb(0x09, tmpcip);
	} else {
		dev->last_cmd |= 0x40;
	}
	dev->in_snd = 0;
}

static unsigned char fun_scam(struct atp_unit *dev, unsigned short int *val)
{
	unsigned int tmport;
	unsigned short int i, k;
	unsigned char j;

	tmport = dev->ioport + 0x1c;
	outw(*val, tmport);
FUN_D7:
	for (i = 0; i < 10; i++) {	/* stable >= bus settle delay(400 ns)  */
		k = inw(tmport);
		j = (unsigned char) (k >> 8);
		if ((k & 0x8000) != 0) {	/* DB7 all release?    */
			goto FUN_D7;
		}
	}
	*val |= 0x4000;		/* assert DB6           */
	outw(*val, tmport);
	*val &= 0xdfff;		/* assert DB5           */
	outw(*val, tmport);
FUN_D5:
	for (i = 0; i < 10; i++) {	/* stable >= bus settle delay(400 ns) */
		if ((inw(tmport) & 0x2000) != 0) {	/* DB5 all release?       */
			goto FUN_D5;
		}
	}
	*val |= 0x8000;		/* no DB4-0, assert DB7    */
	*val &= 0xe0ff;
	outw(*val, tmport);
	*val &= 0xbfff;		/* release DB6             */
	outw(*val, tmport);
FUN_D6:
	for (i = 0; i < 10; i++) {	/* stable >= bus settle delay(400 ns)  */
		if ((inw(tmport) & 0x4000) != 0) {	/* DB6 all release?  */
			goto FUN_D6;
		}
	}

	return j;
}

static void tscam(struct Scsi_Host *host)
{

	unsigned int tmport;
	unsigned char i, j, k;
	unsigned long n;
	unsigned short int m, assignid_map, val;
	unsigned char mbuf[33], quintet[2];
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;
	static unsigned char g2q_tab[8] = {
		0x38, 0x31, 0x32, 0x2b, 0x34, 0x2d, 0x2e, 0x27
	};

/*  I can't believe we need this before we've even done anything.  Remove it
 *  and see if anyone bitches.
	for (i = 0; i < 0x10; i++) {
		udelay(0xffff);
	}
 */

	tmport = dev->ioport + 1;
	outb(0x08, tmport++);
	outb(0x7f, tmport);
	tmport = dev->ioport + 0x11;
	outb(0x20, tmport);

	if ((dev->scam_on & 0x40) == 0) {
		return;
	}
	m = 1;
	m <<= dev->host_idu;
	j = 16;
	if (dev->chip_veru < 4) {
		m |= 0xff00;
		j = 8;
	}
	assignid_map = m;
	tmport = dev->ioport + 0x02;
	outb(0x02, tmport++);	/* 2*2=4ms,3EH 2/32*3E=3.9ms */
	outb(0, tmport++);
	outb(0, tmport++);
	outb(0, tmport++);
	outb(0, tmport++);
	outb(0, tmport++);
	outb(0, tmport++);

	for (i = 0; i < j; i++) {
		m = 1;
		m = m << i;
		if ((m & assignid_map) != 0) {
			continue;
		}
		tmport = dev->ioport + 0x0f;
		outb(0, tmport++);
		tmport += 0x02;
		outb(0, tmport++);
		outb(0, tmport++);
		outb(0, tmport++);
		if (i > 7) {
			k = (i & 0x07) | 0x40;
		} else {
			k = i;
		}
		outb(k, tmport++);
		tmport = dev->ioport + 0x1b;
		if (dev->chip_veru == 4) {
			outb(0x01, tmport);
		} else {
			outb(0x00, tmport);
		}
wait_rdyok:
		tmport = dev->ioport + 0x18;
		outb(0x09, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		k = inb(tmport);
		if (k != 0x16) {
			if ((k == 0x85) || (k == 0x42)) {
				continue;
			}
			tmport = dev->ioport + 0x10;
			outb(0x41, tmport);
			goto wait_rdyok;
		}
		assignid_map |= m;

	}
	tmport = dev->ioport + 0x02;
	outb(0x7f, tmport);
	tmport = dev->ioport + 0x1b;
	outb(0x02, tmport);

	outb(0, 0x80);

	val = 0x0080;		/* bsy  */
	tmport = dev->ioport + 0x1c;
	outw(val, tmport);
	val |= 0x0040;		/* sel  */
	outw(val, tmport);
	val |= 0x0004;		/* msg  */
	outw(val, tmport);
	inb(0x80);		/* 2 deskew delay(45ns*2=90ns) */
	val &= 0x007f;		/* no bsy  */
	outw(val, tmport);
	mdelay(128);
	val &= 0x00fb;		/* after 1ms no msg */
	outw(val, tmport);
wait_nomsg:
	if ((inb(tmport) & 0x04) != 0) {
		goto wait_nomsg;
	}
	outb(1, 0x80);
	udelay(100);
	for (n = 0; n < 0x30000; n++) {
		if ((inb(tmport) & 0x80) != 0) {	/* bsy ? */
			goto wait_io;
		}
	}
	goto TCM_SYNC;
wait_io:
	for (n = 0; n < 0x30000; n++) {
		if ((inb(tmport) & 0x81) == 0x0081) {
			goto wait_io1;
		}
	}
	goto TCM_SYNC;
wait_io1:
	inb(0x80);
	val |= 0x8003;		/* io,cd,db7  */
	outw(val, tmport);
	inb(0x80);
	val &= 0x00bf;		/* no sel     */
	outw(val, tmport);
	outb(2, 0x80);
TCM_SYNC:
	udelay(0x800);
	if ((inb(tmport) & 0x80) == 0x00) {	/* bsy ? */
		outw(0, tmport--);
		outb(0, tmport);
		tmport = dev->ioport + 0x15;
		outb(0, tmport);
		tmport += 0x03;
		outb(0x09, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0);
		tmport -= 0x08;
		inb(tmport);
		return;
	}
	val &= 0x00ff;		/* synchronization  */
	val |= 0x3f00;
	fun_scam(dev, &val);
	outb(3, 0x80);
	val &= 0x00ff;		/* isolation        */
	val |= 0x2000;
	fun_scam(dev, &val);
	outb(4, 0x80);
	i = 8;
	j = 0;
TCM_ID:
	if ((inw(tmport) & 0x2000) == 0) {
		goto TCM_ID;
	}
	outb(5, 0x80);
	val &= 0x00ff;		/* get ID_STRING */
	val |= 0x2000;
	k = fun_scam(dev, &val);
	if ((k & 0x03) == 0) {
		goto TCM_5;
	}
	mbuf[j] <<= 0x01;
	mbuf[j] &= 0xfe;
	if ((k & 0x02) != 0) {
		mbuf[j] |= 0x01;
	}
	i--;
	if (i > 0) {
		goto TCM_ID;
	}
	j++;
	i = 8;
	goto TCM_ID;

TCM_5:			/* isolation complete..  */
/*    mbuf[32]=0;
	printk(" \n%x %x %x %s\n ",assignid_map,mbuf[0],mbuf[1],&mbuf[2]); */
	i = 15;
	j = mbuf[0];
	if ((j & 0x20) != 0) {	/* bit5=1:ID upto 7      */
		i = 7;
	}
	if ((j & 0x06) == 0) {	/* IDvalid?             */
		goto G2Q5;
	}
	k = mbuf[1];
small_id:
	m = 1;
	m <<= k;
	if ((m & assignid_map) == 0) {
		goto G2Q_QUIN;
	}
	if (k > 0) {
		k--;
		goto small_id;
	}
G2Q5:			/* srch from max acceptable ID#  */
	k = i;			/* max acceptable ID#            */
G2Q_LP:
	m = 1;
	m <<= k;
	if ((m & assignid_map) == 0) {
		goto G2Q_QUIN;
	}
	if (k > 0) {
		k--;
		goto G2Q_LP;
	}
G2Q_QUIN:		/* k=binID#,       */
	assignid_map |= m;
	if (k < 8) {
		quintet[0] = 0x38;	/* 1st dft ID<8    */
	} else {
		quintet[0] = 0x31;	/* 1st  ID>=8      */
	}
	k &= 0x07;
	quintet[1] = g2q_tab[k];

	val &= 0x00ff;		/* AssignID 1stQuintet,AH=001xxxxx  */
	m = quintet[0] << 8;
	val |= m;
	fun_scam(dev, &val);
	val &= 0x00ff;		/* AssignID 2ndQuintet,AH=001xxxxx */
	m = quintet[1] << 8;
	val |= m;
	fun_scam(dev, &val);

	goto TCM_SYNC;

}

void is870(struct Scsi_Host *host, unsigned int wkport)
{
	unsigned int tmport;
	unsigned char i, j, k, rmb, n;
	unsigned short int m;
	static unsigned char mbuf[512];
	static unsigned char satn[9] = { 0, 0, 0, 0, 0, 0, 0, 6, 6 };
	static unsigned char inqd[9] = { 0x12, 0, 0, 0, 0x24, 0, 0, 0x24, 6 };
	static unsigned char synn[6] = { 0x80, 1, 3, 1, 0x19, 0x0e };
	static unsigned char synu[6] = { 0x80, 1, 3, 1, 0x0c, 0x0e };
	static unsigned char synw[6] = { 0x80, 1, 3, 1, 0x0c, 0x07 };
	static unsigned char wide[6] = { 0x80, 1, 2, 3, 1, 0 };
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;

	tmport = wkport + 0x3a;
	outb((unsigned char) (inb(tmport) | 0x10), tmport);

	for (i = 0; i < 16; i++) {
		if ((dev->chip_veru != 4) && (i > 7)) {
			break;
		}
		m = 1;
		m = m << i;
		if ((m & dev->active_idu) != 0) {
			continue;
		}
		if (i == dev->host_idu) {
			printk(KERN_INFO "         ID: %2d  Host Adapter\n", dev->host_idu);
			continue;
		}
		tmport = wkport + 0x1b;
		if (dev->chip_veru == 4) {
			outb(0x01, tmport);
		} else {
			outb(0x00, tmport);
		}
		tmport = wkport + 1;
		outb(0x08, tmport++);
		outb(0x7f, tmport++);
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		j = i;
		if ((j & 0x08) != 0) {
			j = (j & 0x07) | 0x40;
		}
		outb(j, tmport);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
		dev->active_idu |= m;

		tmport = wkport + 0x10;
		outb(0x30, tmport);
		tmport = wkport + 0x04;
		outb(0x00, tmport);

phase_cmd:
		tmport = wkport + 0x18;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			tmport = wkport + 0x10;
			outb(0x41, tmport);
			goto phase_cmd;
		}
sel_ok:
		tmport = wkport + 3;
		outb(inqd[0], tmport++);
		outb(inqd[1], tmport++);
		outb(inqd[2], tmport++);
		outb(inqd[3], tmport++);
		outb(inqd[4], tmport++);
		outb(inqd[5], tmport);
		tmport += 0x07;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(inqd[6], tmport++);
		outb(inqd[7], tmport++);
		tmport += 0x03;
		outb(inqd[8], tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
		tmport = wkport + 0x1b;
		if (dev->chip_veru == 4) {
			outb(0x00, tmport);
		}
		tmport = wkport + 0x18;
		outb(0x08, tmport);
		tmport += 0x07;
		j = 0;
rd_inq_data:
		k = inb(tmport);
		if ((k & 0x01) != 0) {
			tmport -= 0x06;
			mbuf[j++] = inb(tmport);
			tmport += 0x06;
			goto rd_inq_data;
		}
		if ((k & 0x80) == 0) {
			goto rd_inq_data;
		}
		tmport -= 0x08;
		j = inb(tmport);
		if (j == 0x16) {
			goto inq_ok;
		}
		tmport = wkport + 0x10;
		outb(0x46, tmport);
		tmport += 0x02;
		outb(0, tmport++);
		outb(0, tmport++);
		outb(0, tmport++);
		tmport += 0x03;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if (inb(tmport) != 0x16) {
			goto sel_ok;
		}
inq_ok:
		mbuf[36] = 0;
		printk(KERN_INFO "         ID: %2d  %s\n", i, &mbuf[8]);
		dev->id[i].devtypeu = mbuf[0];
		rmb = mbuf[1];
		n = mbuf[7];
		if (dev->chip_veru != 4) {
			goto not_wide;
		}
		if ((mbuf[7] & 0x60) == 0) {
			goto not_wide;
		}
		if ((dev->global_map & 0x20) == 0) {
			goto not_wide;
		}
		tmport = wkport + 0x1b;
		outb(0x01, tmport);
		tmport = wkport + 3;
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
try_wide:
		j = 0;
		tmport = wkport + 0x14;
		outb(0x05, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(wide[j++], tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto try_wide;
		}
		continue;
widep_out:
		tmport = wkport + 0x18;
		outb(0x20, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(0, tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto widep_out;
		}
		continue;
widep_in:
		tmport = wkport + 0x14;
		outb(0xff, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;
		k = 0;
widep_in1:
		j = inb(tmport);
		if ((j & 0x01) != 0) {
			tmport -= 0x06;
			mbuf[k++] = inb(tmport);
			tmport += 0x06;
			goto widep_in1;
		}
		if ((j & 0x80) == 0x00) {
			goto widep_in1;
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto widep_out;
		}
		continue;
widep_cmd:
		tmport = wkport + 0x10;
		outb(0x30, tmport);
		tmport = wkport + 0x14;
		outb(0x00, tmport);
		tmport += 0x04;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			if (j == 0x4e) {
				goto widep_out;
			}
			continue;
		}
		if (mbuf[0] != 0x01) {
			goto not_wide;
		}
		if (mbuf[1] != 0x02) {
			goto not_wide;
		}
		if (mbuf[2] != 0x03) {
			goto not_wide;
		}
		if (mbuf[3] != 0x01) {
			goto not_wide;
		}
		m = 1;
		m = m << i;
		dev->wide_idu |= m;
not_wide:
		if ((dev->id[i].devtypeu == 0x00) || (dev->id[i].devtypeu == 0x07) || ((dev->id[i].devtypeu == 0x05) && ((n & 0x10) != 0))) {
			goto set_sync;
		}
		continue;
set_sync:
		tmport = wkport + 0x1b;
		j = 0;
		if ((m & dev->wide_idu) != 0) {
			j |= 0x01;
		}
		outb(j, tmport);
		tmport = wkport + 3;
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
try_sync:
		j = 0;
		tmport = wkport + 0x14;
		outb(0x06, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				if ((m & dev->wide_idu) != 0) {
					outb(synw[j++], tmport);
				} else {
					if ((m & dev->ultra_map) != 0) {
						outb(synu[j++], tmport);
					} else {
						outb(synn[j++], tmport);
					}
				}
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto try_sync;
		}
		continue;
phase_outs:
		tmport = wkport + 0x18;
		outb(0x20, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00) {
			if ((inb(tmport) & 0x01) != 0x00) {
				tmport -= 0x06;
				outb(0x00, tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		j = inb(tmport);
		if (j == 0x85) {
			goto tar_dcons;
		}
		j &= 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto phase_outs;
		}
		continue;
phase_ins:
		tmport = wkport + 0x14;
		outb(0xff, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;
		k = 0;
phase_ins1:
		j = inb(tmport);
		if ((j & 0x01) != 0x00) {
			tmport -= 0x06;
			mbuf[k++] = inb(tmport);
			tmport += 0x06;
			goto phase_ins1;
		}
		if ((j & 0x80) == 0x00) {
			goto phase_ins1;
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport);
		if (j == 0x85) {
			goto tar_dcons;
		}
		j &= 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto phase_outs;
		}
		continue;
phase_cmds:
		tmport = wkport + 0x10;
		outb(0x30, tmport);
tar_dcons:
		tmport = wkport + 0x14;
		outb(0x00, tmport);
		tmport += 0x04;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			continue;
		}
		if (mbuf[0] != 0x01) {
			continue;
		}
		if (mbuf[1] != 0x03) {
			continue;
		}
		if (mbuf[4] == 0x00) {
			continue;
		}
		if (mbuf[3] > 0x64) {
			continue;
		}
		if (mbuf[4] > 0x0c) {
			mbuf[4] = 0x0c;
		}
		dev->id[i].devspu = mbuf[4];
		if ((mbuf[3] < 0x0d) && (rmb == 0)) {
			j = 0xa0;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x1a) {
			j = 0x20;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x33) {
			j = 0x40;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x4c) {
			j = 0x50;
			goto set_syn_ok;
		}
		j = 0x60;
set_syn_ok:
		dev->id[i].devspu = (dev->id[i].devspu & 0x0f) | j;
	}
	tmport = wkport + 0x3a;
	outb((unsigned char) (inb(tmport) & 0xef), tmport);
}

static void is880(struct Scsi_Host *host, unsigned int wkport)
{
	unsigned int tmport;
	unsigned char i, j, k, rmb, n, lvdmode;
	unsigned short int m;
	static unsigned char mbuf[512];
	static unsigned char satn[9] = { 0, 0, 0, 0, 0, 0, 0, 6, 6 };
	static unsigned char inqd[9] = { 0x12, 0, 0, 0, 0x24, 0, 0, 0x24, 6 };
	static unsigned char synn[6] = { 0x80, 1, 3, 1, 0x19, 0x0e };
	unsigned char synu[6] = { 0x80, 1, 3, 1, 0x0a, 0x0e };
	static unsigned char synw[6] = { 0x80, 1, 3, 1, 0x19, 0x0e };
	unsigned char synuw[6] = { 0x80, 1, 3, 1, 0x0a, 0x0e };
	static unsigned char wide[6] = { 0x80, 1, 2, 3, 1, 0 };
	static unsigned char u3[9] = { 0x80, 1, 6, 4, 0x09, 00, 0x0e, 0x01, 0x02 };
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;

	lvdmode = inb(wkport + 0x3f) & 0x40;

	for (i = 0; i < 16; i++) {
		m = 1;
		m = m << i;
		if ((m & dev->active_idu) != 0) {
			continue;
		}
		if (i == dev->host_idu) {
			printk(KERN_INFO "         ID: %2d  Host Adapter\n", dev->host_idu);
			continue;
		}
		tmport = wkport + 0x5b;
		outb(0x01, tmport);
		tmport = wkport + 0x41;
		outb(0x08, tmport++);
		outb(0x7f, tmport++);
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		j = i;
		if ((j & 0x08) != 0) {
			j = (j & 0x07) | 0x40;
		}
		outb(j, tmport);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
		dev->active_idu |= m;

		tmport = wkport + 0x50;
		outb(0x30, tmport);
		tmport = wkport + 0x54;
		outb(0x00, tmport);

phase_cmd:
		tmport = wkport + 0x58;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			tmport = wkport + 0x50;
			outb(0x41, tmport);
			goto phase_cmd;
		}
sel_ok:
		tmport = wkport + 0x43;
		outb(inqd[0], tmport++);
		outb(inqd[1], tmport++);
		outb(inqd[2], tmport++);
		outb(inqd[3], tmport++);
		outb(inqd[4], tmport++);
		outb(inqd[5], tmport);
		tmport += 0x07;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(inqd[6], tmport++);
		outb(inqd[7], tmport++);
		tmport += 0x03;
		outb(inqd[8], tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
		tmport = wkport + 0x5b;
		outb(0x00, tmport);
		tmport = wkport + 0x58;
		outb(0x08, tmport);
		tmport += 0x07;
		j = 0;
rd_inq_data:
		k = inb(tmport);
		if ((k & 0x01) != 0) {
			tmport -= 0x06;
			mbuf[j++] = inb(tmport);
			tmport += 0x06;
			goto rd_inq_data;
		}
		if ((k & 0x80) == 0) {
			goto rd_inq_data;
		}
		tmport -= 0x08;
		j = inb(tmport);
		if (j == 0x16) {
			goto inq_ok;
		}
		tmport = wkport + 0x50;
		outb(0x46, tmport);
		tmport += 0x02;
		outb(0, tmport++);
		outb(0, tmport++);
		outb(0, tmport++);
		tmport += 0x03;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if (inb(tmport) != 0x16) {
			goto sel_ok;
		}
inq_ok:
		mbuf[36] = 0;
		printk(KERN_INFO "         ID: %2d  %s\n", i, &mbuf[8]);
		dev->id[i].devtypeu = mbuf[0];
		rmb = mbuf[1];
		n = mbuf[7];
		if ((mbuf[7] & 0x60) == 0) {
			goto not_wide;
		}
		if ((i < 8) && ((dev->global_map & 0x20) == 0)) {
			goto not_wide;
		}
		if (lvdmode == 0) {
			goto chg_wide;
		}
		if (dev->sp[i] != 0x04)	// force u2
		{
			goto chg_wide;
		}

		tmport = wkport + 0x5b;
		outb(0x01, tmport);
		tmport = wkport + 0x43;
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
try_u3:
		j = 0;
		tmport = wkport + 0x54;
		outb(0x09, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(u3[j++], tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto u3p_in;
		}
		if (j == 0x0a) {
			goto u3p_cmd;
		}
		if (j == 0x0e) {
			goto try_u3;
		}
		continue;
u3p_out:
		tmport = wkport + 0x58;
		outb(0x20, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(0, tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto u3p_in;
		}
		if (j == 0x0a) {
			goto u3p_cmd;
		}
		if (j == 0x0e) {
			goto u3p_out;
		}
		continue;
u3p_in:
		tmport = wkport + 0x54;
		outb(0x09, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;
		k = 0;
u3p_in1:
		j = inb(tmport);
		if ((j & 0x01) != 0) {
			tmport -= 0x06;
			mbuf[k++] = inb(tmport);
			tmport += 0x06;
			goto u3p_in1;
		}
		if ((j & 0x80) == 0x00) {
			goto u3p_in1;
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto u3p_in;
		}
		if (j == 0x0a) {
			goto u3p_cmd;
		}
		if (j == 0x0e) {
			goto u3p_out;
		}
		continue;
u3p_cmd:
		tmport = wkport + 0x50;
		outb(0x30, tmport);
		tmport = wkport + 0x54;
		outb(0x00, tmport);
		tmport += 0x04;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			if (j == 0x4e) {
				goto u3p_out;
			}
			continue;
		}
		if (mbuf[0] != 0x01) {
			goto chg_wide;
		}
		if (mbuf[1] != 0x06) {
			goto chg_wide;
		}
		if (mbuf[2] != 0x04) {
			goto chg_wide;
		}
		if (mbuf[3] == 0x09) {
			m = 1;
			m = m << i;
			dev->wide_idu |= m;
			dev->id[i].devspu = 0xce;
			continue;
		}
chg_wide:
		tmport = wkport + 0x5b;
		outb(0x01, tmport);
		tmport = wkport + 0x43;
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
try_wide:
		j = 0;
		tmport = wkport + 0x54;
		outb(0x05, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(wide[j++], tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto try_wide;
		}
		continue;
widep_out:
		tmport = wkport + 0x58;
		outb(0x20, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				outb(0, tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto widep_out;
		}
		continue;
widep_in:
		tmport = wkport + 0x54;
		outb(0xff, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;
		k = 0;
widep_in1:
		j = inb(tmport);
		if ((j & 0x01) != 0) {
			tmport -= 0x06;
			mbuf[k++] = inb(tmport);
			tmport += 0x06;
			goto widep_in1;
		}
		if ((j & 0x80) == 0x00) {
			goto widep_in1;
		}
		tmport -= 0x08;
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto widep_in;
		}
		if (j == 0x0a) {
			goto widep_cmd;
		}
		if (j == 0x0e) {
			goto widep_out;
		}
		continue;
widep_cmd:
		tmport = wkport + 0x50;
		outb(0x30, tmport);
		tmport = wkport + 0x54;
		outb(0x00, tmport);
		tmport += 0x04;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			if (j == 0x4e) {
				goto widep_out;
			}
			continue;
		}
		if (mbuf[0] != 0x01) {
			goto not_wide;
		}
		if (mbuf[1] != 0x02) {
			goto not_wide;
		}
		if (mbuf[2] != 0x03) {
			goto not_wide;
		}
		if (mbuf[3] != 0x01) {
			goto not_wide;
		}
		m = 1;
		m = m << i;
		dev->wide_idu |= m;
not_wide:
		if ((dev->id[i].devtypeu == 0x00) || (dev->id[i].devtypeu == 0x07) || ((dev->id[i].devtypeu == 0x05) && ((n & 0x10) != 0))) {
			m = 1;
			m = m << i;
			if ((dev->async & m) != 0) {
				goto set_sync;
			}
		}
		continue;
set_sync:
		if (dev->sp[i] == 0x02) {
			synu[4] = 0x0c;
			synuw[4] = 0x0c;
		} else {
			if (dev->sp[i] >= 0x03) {
				synu[4] = 0x0a;
				synuw[4] = 0x0a;
			}
		}
		tmport = wkport + 0x5b;
		j = 0;
		if ((m & dev->wide_idu) != 0) {
			j |= 0x01;
		}
		outb(j, tmport);
		tmport = wkport + 0x43;
		outb(satn[0], tmport++);
		outb(satn[1], tmport++);
		outb(satn[2], tmport++);
		outb(satn[3], tmport++);
		outb(satn[4], tmport++);
		outb(satn[5], tmport++);
		tmport += 0x06;
		outb(0, tmport);
		tmport += 0x02;
		outb(dev->id[i].devspu, tmport++);
		outb(0, tmport++);
		outb(satn[6], tmport++);
		outb(satn[7], tmport++);
		tmport += 0x03;
		outb(satn[8], tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		if ((inb(tmport) != 0x11) && (inb(tmport) != 0x8e)) {
			continue;
		}
		while (inb(tmport) != 0x8e);
try_sync:
		j = 0;
		tmport = wkport + 0x54;
		outb(0x06, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;

		while ((inb(tmport) & 0x80) == 0) {
			if ((inb(tmport) & 0x01) != 0) {
				tmport -= 0x06;
				if ((m & dev->wide_idu) != 0) {
					if ((m & dev->ultra_map) != 0) {
						outb(synuw[j++], tmport);
					} else {
						outb(synw[j++], tmport);
					}
				} else {
					if ((m & dev->ultra_map) != 0) {
						outb(synu[j++], tmport);
					} else {
						outb(synn[j++], tmport);
					}
				}
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport) & 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto try_sync;
		}
		continue;
phase_outs:
		tmport = wkport + 0x58;
		outb(0x20, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00) {
			if ((inb(tmport) & 0x01) != 0x00) {
				tmport -= 0x06;
				outb(0x00, tmport);
				tmport += 0x06;
			}
		}
		tmport -= 0x08;
		j = inb(tmport);
		if (j == 0x85) {
			goto tar_dcons;
		}
		j &= 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto phase_outs;
		}
		continue;
phase_ins:
		tmport = wkport + 0x54;
		outb(0x06, tmport);
		tmport += 0x04;
		outb(0x20, tmport);
		tmport += 0x07;
		k = 0;
phase_ins1:
		j = inb(tmport);
		if ((j & 0x01) != 0x00) {
			tmport -= 0x06;
			mbuf[k++] = inb(tmport);
			tmport += 0x06;
			goto phase_ins1;
		}
		if ((j & 0x80) == 0x00) {
			goto phase_ins1;
		}
		tmport -= 0x08;
		while ((inb(tmport) & 0x80) == 0x00);
		j = inb(tmport);
		if (j == 0x85) {
			goto tar_dcons;
		}
		j &= 0x0f;
		if (j == 0x0f) {
			goto phase_ins;
		}
		if (j == 0x0a) {
			goto phase_cmds;
		}
		if (j == 0x0e) {
			goto phase_outs;
		}
		continue;
phase_cmds:
		tmport = wkport + 0x50;
		outb(0x30, tmport);
tar_dcons:
		tmport = wkport + 0x54;
		outb(0x00, tmport);
		tmport += 0x04;
		outb(0x08, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0x00);
		tmport -= 0x08;
		j = inb(tmport);
		if (j != 0x16) {
			continue;
		}
		if (mbuf[0] != 0x01) {
			continue;
		}
		if (mbuf[1] != 0x03) {
			continue;
		}
		if (mbuf[4] == 0x00) {
			continue;
		}
		if (mbuf[3] > 0x64) {
			continue;
		}
		if (mbuf[4] > 0x0e) {
			mbuf[4] = 0x0e;
		}
		dev->id[i].devspu = mbuf[4];
		if (mbuf[3] < 0x0c) {
			j = 0xb0;
			goto set_syn_ok;
		}
		if ((mbuf[3] < 0x0d) && (rmb == 0)) {
			j = 0xa0;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x1a) {
			j = 0x20;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x33) {
			j = 0x40;
			goto set_syn_ok;
		}
		if (mbuf[3] < 0x4c) {
			j = 0x50;
			goto set_syn_ok;
		}
		j = 0x60;
set_syn_ok:
		dev->id[i].devspu = (dev->id[i].devspu & 0x0f) | j;
	}
}

static void atp870u_free_tables(struct Scsi_Host *host)
{
	struct atp_unit *atp_dev = (struct atp_unit *)&host->hostdata;
	int k;

	for (k = 0; k < 16; k++) {
		if (!atp_dev->id[k].prd_tableu)
			continue;
		pci_free_consistent(atp_dev->pdev, 1024, atp_dev->id[k].prd_tableu,
					atp_dev->id[k].prd_phys);
		atp_dev->id[k].prd_tableu = NULL;
	}
}

static int atp870u_init_tables(struct Scsi_Host *host)
{
	struct atp_unit *dev = (struct atp_unit *)&host->hostdata;
	int k, i;

	for (i = k = 0; k < 16; k++) {
		dev->id[k].prd_tableu = pci_alloc_consistent(dev->pdev, 1024, &dev->id[k].prd_phys);
		if (!dev->id[k].prd_tableu) {
			atp870u_free_tables(host);
			return -ENOMEM;
		}
		dev->id[k].devspu = 0x20;
		dev->id[k].devtypeu = 0;
		dev->id[k].curr_req = NULL;
	}
	dev->active_idu = 0;
	dev->wide_idu = 0;
	dev->host_idu = 0x07;
	dev->quhdu = 0;
	dev->quendu = 0;
	dev->chip_veru = 0;
	dev->last_cmd = 0xff;
	dev->in_snd = 0;
	dev->in_int = 0;
	for (k = 0; k < qcnt; k++) {
		dev->querequ[k] = NULL;
	}
	for (k = 0; k < 16; k++) {
		dev->id[k].curr_req = NULL;
		dev->sp[k] = 0x04;
	}
	return 0;
}

/* return non-zero on detection */
static int atp870u_probe(struct pci_dev *dev, const struct pci_device_id *ent)
{
	unsigned char k, m;
	unsigned long flags;
	unsigned int base_io, error, tmport;
	unsigned char host_id;
	unsigned short n;
	struct Scsi_Host *shpnt;
	struct atp_unit atp_dev, *p;
	static int count;

	if (pci_enable_device(dev))
		return -EIO;

	if (pci_set_dma_mask(dev, 0xFFFFFFFFUL)) {
		printk(KERN_ERR "atp870u: 32bit DMA mask required but not available.\n");
		return -EIO;
	}
	
	memset(&atp_dev, 0, sizeof atp_dev);
 
	/*
	 * It's probably easier to weed out some revisions like
	 * this than via the PCI device table
	 */
	if (ent->device == PCI_DEVICE_ID_ARTOP_AEC7610) {
		error = pci_read_config_byte(dev, PCI_CLASS_REVISION, &atp_dev.chip_veru);
		if (atp_dev.chip_veru < 2)
			return -EIO;
	}

	switch (ent->device) {
	case 0x8081:
	case PCI_DEVICE_ID_ARTOP_AEC7612UW:
	case PCI_DEVICE_ID_ARTOP_AEC7612SUW:
		atp_dev.chip_veru = 0x04;
	default:
		break;
	}

	base_io = pci_resource_start(dev, 0);

	if (ent->device != 0x8081) {
		error = pci_read_config_byte(dev, 0x49, &host_id);
		base_io &= 0xfffffff8;

		printk(KERN_INFO "   ACARD AEC-671X PCI Ultra/W SCSI-3 Host Adapter: %d "
			"IO:%x, IRQ:%d.\n", count, base_io, dev->irq);

		atp_dev.unit = count;	
		atp_dev.ioport = base_io;
		atp_dev.pciport = base_io + 0x20;
		atp_dev.deviceid = ent->device;
		host_id &= 0x07;
		atp_dev.host_idu = host_id;
		tmport = base_io + 0x22;
		atp_dev.scam_on = inb(tmport);
		tmport += 0x0b;
		atp_dev.global_map = inb(tmport++);
		atp_dev.ultra_map = inw(tmport);

		if (atp_dev.ultra_map == 0) {
			atp_dev.scam_on = 0x00;
			atp_dev.global_map = 0x20;
			atp_dev.ultra_map = 0xffff;
		}

		shpnt = scsi_host_alloc(&atp870u_template, sizeof(struct atp_unit));
		if (!shpnt)
			return -ENOMEM;

		p = (struct atp_unit *)&shpnt->hostdata;
		
		atp_dev.host = shpnt;
		atp_dev.pdev = dev;
		pci_set_drvdata(dev, p);
		memcpy(p, &atp_dev, sizeof atp_dev);
		if (atp870u_init_tables(shpnt) < 0)
			goto unregister;

		if (request_irq(dev->irq, atp870u_intr_handle, SA_SHIRQ, "atp870u", shpnt)) {
			printk(KERN_ERR "Unable to allocate IRQ%d for Acard controller.\n", dev->irq);
			goto free_tables;
		}

		spin_lock_irqsave(shpnt->host_lock, flags);
		if (atp_dev.chip_veru > 0x07) {	/* check if atp876 chip then enable terminator */
			tmport = base_io + 0x3e;
			outb(0x00, tmport);
		}
 
		tmport = base_io + 0x3a;
		k = (inb(tmport) & 0xf3) | 0x10;
		outb(k, tmport);
		outb((k & 0xdf), tmport);
		mdelay(32);
		outb(k, tmport);
		mdelay(32);
		tmport = base_io;
		outb((host_id | 0x08), tmport);
		tmport += 0x18;
		outb(0, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0)
			mdelay(1);

		tmport -= 0x08;
		inb(tmport);
		tmport = base_io + 1;
		outb(8, tmport++);
		outb(0x7f, tmport);
		tmport = base_io + 0x11;
		outb(0x20, tmport);

		tscam(shpnt);
		is870(shpnt, base_io);
		tmport = base_io + 0x3a;
		outb((inb(tmport) & 0xef), tmport);
		tmport++;
		outb((inb(tmport) | 0x20), tmport);
	} else {
		base_io &= 0xfffffff8;
		host_id = inb(base_io + 0x39);
		host_id >>= 0x04;

		printk(KERN_INFO "   ACARD AEC-67160 PCI Ultra3 LVD Host Adapter: %d"
			"    IO:%x, IRQ:%d.\n", count, base_io, dev->irq);
		atp_dev.ioport = base_io + 0x40;
		atp_dev.pciport = base_io + 0x28;
		atp_dev.deviceid = ent->device;
		atp_dev.host_idu = host_id;

		tmport = base_io + 0x22;
		atp_dev.scam_on = inb(tmport);
		tmport += 0x13;
		atp_dev.global_map = inb(tmport);
		tmport += 0x07;
		atp_dev.ultra_map = inw(tmport);

		n = 0x3f09;
next_fblk:
		if (n >= 0x4000)
			goto flash_ok;

		m = 0;
		outw(n, base_io + 0x34);
		n += 0x0002;
		if (inb(base_io + 0x30) == 0xff)
			goto flash_ok;

		atp_dev.sp[m++] = inb(base_io + 0x30);
		atp_dev.sp[m++] = inb(base_io + 0x31);
		atp_dev.sp[m++] = inb(base_io + 0x32);
		atp_dev.sp[m++] = inb(base_io + 0x33);
		outw(n, base_io + 0x34);
		n += 0x0002;
		atp_dev.sp[m++] = inb(base_io + 0x30);
		atp_dev.sp[m++] = inb(base_io + 0x31);
		atp_dev.sp[m++] = inb(base_io + 0x32);
		atp_dev.sp[m++] = inb(base_io + 0x33);
		outw(n, base_io + 0x34);
		n += 0x0002;
		atp_dev.sp[m++] = inb(base_io + 0x30);
		atp_dev.sp[m++] = inb(base_io + 0x31);
		atp_dev.sp[m++] = inb(base_io + 0x32);
		atp_dev.sp[m++] = inb(base_io + 0x33);
		outw(n, base_io + 0x34);
		n += 0x0002;
		atp_dev.sp[m++] = inb(base_io + 0x30);
		atp_dev.sp[m++] = inb(base_io + 0x31);
		atp_dev.sp[m++] = inb(base_io + 0x32);
		atp_dev.sp[m++] = inb(base_io + 0x33);
		n += 0x0018;
		goto next_fblk;
flash_ok:
		outw(0, base_io + 0x34);
		atp_dev.ultra_map = 0;
		atp_dev.async = 0;
		for (k = 0; k < 16; k++) {
			n = 1;
			n = n << k;
			if (atp_dev.sp[k] > 1) {
				atp_dev.ultra_map |= n;
			} else {
				if (atp_dev.sp[k] == 0)
					atp_dev.async |= n;
 			}
	 	}
		atp_dev.async = ~(atp_dev.async);
		outb(atp_dev.global_map, base_io + 0x35);
 
		shpnt = scsi_host_alloc(&atp870u_template, sizeof(struct atp_unit));
		if (!shpnt)
			return -ENOMEM;

		p = (struct atp_unit *)&shpnt->hostdata;

		atp_dev.host = shpnt;
		atp_dev.pdev = dev;
		pci_set_drvdata(dev, p);
		memcpy(p, &atp_dev, sizeof atp_dev);
		if (atp870u_init_tables(shpnt) < 0) {
			printk(KERN_ERR "Unable to allocate tables for Acard controller\n");
			goto unregister;
		}

		if (request_irq(dev->irq, atp870u_intr_handle, SA_SHIRQ, "atp870u", shpnt)) {
 			printk(KERN_ERR "Unable to allocate IRQ%d for Acard controller.\n", dev->irq);
			goto free_tables;
		}

		spin_lock_irqsave(shpnt->host_lock, flags);
		tmport = base_io + 0x38;
		k = inb(tmport) & 0x80;
		outb(k, tmport);
		tmport += 0x03;
		outb(0x20, tmport);
		mdelay(32);
		outb(0, tmport);
		mdelay(32);
		tmport = base_io + 0x5b;
		inb(tmport);
		tmport -= 0x04;
		inb(tmport);
		tmport = base_io + 0x40;
		outb((host_id | 0x08), tmport);
		tmport += 0x18;
		outb(0, tmport);
		tmport += 0x07;
		while ((inb(tmport) & 0x80) == 0)
			mdelay(1);
		tmport -= 0x08;
		inb(tmport);
		tmport = base_io + 0x41;
		outb(8, tmport++);
		outb(0x7f, tmport);
		tmport = base_io + 0x51;
		outb(0x20, tmport);

		tscam(shpnt);
		is880(shpnt, base_io);
		tmport = base_io + 0x38;
		outb(0xb0, tmport);
	}

	if (p->chip_veru == 4)
		shpnt->max_id = 16;

	shpnt->this_id = host_id;
	shpnt->unique_id = base_io;
	shpnt->io_port = base_io;
	if (ent->device == 0x8081) {
		shpnt->n_io_port = 0x60;	/* Number of bytes of I/O space used */
	} else {
		shpnt->n_io_port = 0x40;	/* Number of bytes of I/O space used */
	}
	shpnt->irq = dev->irq;
	spin_unlock_irqrestore(shpnt->host_lock, flags);
	if (ent->device == 0x8081) {
		if (!request_region(base_io, 0x60, "atp870u"))
			goto request_io_fail;
	} else {
		if (!request_region(base_io, 0x40, "atp870u"))
			goto request_io_fail;
	}

	count++;
	if (scsi_add_host(shpnt, &dev->dev))
		goto scsi_add_fail;
	scsi_scan_host(shpnt);
	return 0;
  
scsi_add_fail:
	if (ent->device == 0x8081)
		release_region(base_io, 0x60);
	else
		release_region(base_io, 0x40);
request_io_fail:
	free_irq(dev->irq, shpnt);
free_tables:
	atp870u_free_tables(shpnt);
unregister:
	scsi_host_put(shpnt);
	return -1;
}

/* The abort command does not leave the device in a clean state where
   it is available to be used again.  Until this gets worked out, we will
   leave it commented out.  */

static int atp870u_abort(struct scsi_cmnd * SCpnt)
{
	unsigned char j, k;
	struct scsi_cmnd *workrequ;
	unsigned int tmport;
	struct atp_unit *dev = (struct atp_unit *)&SCpnt->device->host->hostdata;

	printk(KERN_DEBUG "working=%x last_cmd=%x ", dev->working, dev->last_cmd);
	printk(" quhdu=%x quendu=%x ", dev->quhdu, dev->quendu);
	tmport = dev->ioport;
	for (j = 0; j < 0x17; j++) {
		printk(" r%2x=%2x", j, inb(tmport++));
	}
	tmport += 0x05;
	printk(" r1c=%2x", inb(tmport));
	tmport += 0x03;
	printk(" r1f=%2x in_snd=%2x ", inb(tmport), dev->in_snd);
	tmport = dev->pciport;
	printk(" r20=%2x", inb(tmport));
	tmport += 0x02;
	printk(" r22=%2x", inb(tmport));
	tmport = dev->ioport + 0x3a;
	printk(" r3a=%2x \n", inb(tmport));
	tmport = dev->ioport + 0x3b;
	printk(" r3b=%2x \n", inb(tmport));
	for (j = 0; j < 16; j++) {
		if (dev->id[j].curr_req != NULL) {
			workrequ = dev->id[j].curr_req;
			printk("\n que cdb= ");
			for (k = 0; k < workrequ->cmd_len; k++) {
				printk(" %2x ", workrequ->cmnd[k]);
			}
			printk(" last_lenu= %lx ", dev->id[j].last_lenu);
		}
	}
	/* Sort of - the thing handles itself */
	return SUCCESS;
}

static const char *atp870u_info(struct Scsi_Host *notused)
{
	static char buffer[128];

	strcpy(buffer, "ACARD AEC-6710/6712/67160 PCI Ultra/W/LVD SCSI-3 Adapter Driver V2.6+ac ");

	return buffer;
}

#define BLS buffer + len + size
static int atp870u_proc_info(struct Scsi_Host *HBAptr, char *buffer,
		char **start, off_t offset, int length, int inout)
{
	static u8 buff[512];
	int size = 0;
	int len = 0;
	off_t begin = 0;
	off_t pos = 0;

	if (inout)
		return -ENOSYS;
	if (offset == 0) {
		memset(buff, 0, sizeof(buff));
	}
	size += sprintf(BLS, "ACARD AEC-671X Driver Version: 2.6+ac\n");
	len += size;
	pos = begin + len;
	size = 0;

	size += sprintf(BLS, "\n");
	size += sprintf(BLS, "Adapter Configuration:\n");
	size += sprintf(BLS, "               Base IO: %#.4lx\n", HBAptr->io_port);
	size += sprintf(BLS, "                   IRQ: %d\n", HBAptr->irq);
	len += size;
	pos = begin + len;

	*start = buffer + (offset - begin);	/* Start of wanted data */
	len -= (offset - begin);	/* Start slop */
	if (len > length) {
		len = length;	/* Ending slop */
	}
	return (len);
}

static int atp870u_biosparam(struct scsi_device *sdev,
		struct block_device *dev, sector_t capacity, int *ip)
{
	int heads, sectors, cylinders;

	heads = 64;
	sectors = 32;
	cylinders = (unsigned long)capacity / (heads * sectors);

	if (cylinders > 1024) {
		heads = 255;
		sectors = 63;
		cylinders = (unsigned long)capacity / (heads * sectors);
	}
	ip[0] = heads;
	ip[1] = sectors;
	ip[2] = cylinders;

	return 0;
}

static void atp870u_remove(struct pci_dev *pdev)
{
	struct atp_unit *atp_dev = pci_get_drvdata(pdev);
	struct Scsi_Host *pshost = atp_dev->host;

	scsi_remove_host(pshost);
	free_irq(pshost->irq, pshost);
	release_region(pshost->io_port, pshost->n_io_port);
	atp870u_free_tables(pshost);
	scsi_host_put(pshost);
	pci_set_drvdata(pdev, NULL);
}

MODULE_LICENSE("GPL");

static struct scsi_host_template atp870u_template = {
	.module			= THIS_MODULE,
	.name			= "atp870u",
	.proc_name		= "atp870u",
	.proc_info		= atp870u_proc_info,
	.info			= atp870u_info,
	.queuecommand		= atp870u_queuecommand,
	.eh_abort_handler	= atp870u_abort,
	.bios_param		= atp870u_biosparam,
	.can_queue		= qcnt,
	.this_id		= 7,
	.sg_tablesize		= ATP870U_SCATTER,
	.cmd_per_lun		= ATP870U_CMDLUN,
	.use_clustering		= ENABLE_CLUSTERING,
};

static struct pci_device_id atp870u_id_table[] = {
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, 0x8081)			  },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7610)    },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7612UW)  },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7612U)   },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7612S)   },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7612D)	  },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_AEC7612SUW) },
	{ PCI_DEVICE(PCI_VENDOR_ID_ARTOP, PCI_DEVICE_ID_ARTOP_8060)	  },
	{ 0, },
};

MODULE_DEVICE_TABLE(pci, atp870u_id_table);

static struct pci_driver atp870u_driver = {	
	.id_table	= atp870u_id_table,
	.name		= "atp870u",
	.probe		= atp870u_probe,
	.remove		= __devexit_p(atp870u_remove),
};

static int __init atp870u_init(void)
{
	return pci_module_init(&atp870u_driver);
}

static void __exit atp870u_exit(void)
{
	pci_unregister_driver(&atp870u_driver);
}

module_init(atp870u_init);
module_exit(atp870u_exit);


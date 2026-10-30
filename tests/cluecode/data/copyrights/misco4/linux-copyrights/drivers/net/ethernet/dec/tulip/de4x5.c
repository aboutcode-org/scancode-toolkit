Copyright 1994, 1995 Digital Equipment Corporation.

    Testing resources for this driver have been made available


                          Fix recognition bug reported by <bkm@star.rl.ac.uk>.
			  Add request/release_region code.
			  Add loadable modules support for PCI.


                          suggestion by <heiko@colossus.escape.de>.
      0.33     8-Aug-95   Add shared interrupt support (not released yet).
      0.331   21-Aug-95   Fix de4x5_open() with fast CPUs.


			  Made changes suggested by <jeff@router.patch.net>:
			    Change driver to detect all DECchip based cards
			    with DEC_ONLY restriction a special case.


			  Fix for multiple PCI cards reported by <jos@xos.nl>
			  Duh, put the IRQF_SHARED flag into request_interrupt().
			  Fix SMC ethernet address in enet_det[].


			   reported by <koen.gadeyne@barco.com> and
			   <orava@nether.tky.hut.fi>.
			  Add cache locks to prevent a race condition as
			   reported by <csd@microplex.com> and
			   <baba@beckman.uiuc.edu>.
			  Upgraded alloc_device() code.


                          Fix EISA probe bugs reported by <os2@kpi.kharkov.ua>
			  and <michael@compurex.com>.
      0.441   9-Sep-96    Change dc21041_autoconf() to probe quiet BNC media


                           by <bhat@mundook.cs.mu.OZ.AU>
      0.45    8-Dec-96    Include endian functions for PPC use, from work
                           by <cort@cs.nmt.edu> and <g.thomas@opengroup.org>.
      0.451  28-Dec-96    Added fix to allow autoprobe for modules after
                           suggestion from <mjacob@feral.com>.


			   by <cross@gweep.lkg.dec.com>.
			  Added multi-MAC, one SROM feature from discussion
			   with <mjacob@feral.com>.


			  Fix MII PHY reset problem from work done by
			   <paubert@iram.es>.
      0.52   26-Apr-97    Some changes may not credit the right people -
                           a disk crash meant I lost some mail.


                           module load: bug reported by
			   <Piete.Brooks@cl.cam.ac.uk>
			  Fix multi-MAC, one SROM, to work with 2114x chips:
			   bug reported by <cmetz@inner.net>.
			  Make above search independent of BIOS device scan
			   direction.


			   problem reports by
			   <parmee@postecss.ncrfran.france.ncr.com> and
			   <jo@ice.dillingen.baynet.de>.
			  Added argument list to set up each board from either


			   by <belliott@accessone.com>.
      0.533   9-Jan-98    Fix more 64 bit bugs reported by <jal@cs.brown.edu>.
      0.534  24-Jan-98    Fix last (?) endian bug from <geert@linux-m68k.org>
      0.535  21-Feb-98    Fix Ethernet Address PROM reset bug for DC21040.


			   from problem report by <delchini@lpnp09.in2p3.fr>
			  Add MII parallel detection to 2114x_autoconf() for
			   case where no autonegotiation partner exists from
			   problem report by <mlapsley@ndirect.co.uk>.
			  Add ability to force connection type directly even
			   when using SROM control from problem report by
			   <earl@exis.net>.
			  Updated the PCI interface to conform with the latest
			   version. I hope nothing is broken...

			   by <Austin.Donnelly@cl.cam.ac.uk>.
			  Fix is_anc_capable() bug reported by
			   <Austin.Donnelly@cl.cam.ac.uk>.
			  Fix type[13]_infoblock() bug: during MII search, PHY
			   lp->rst not run because lp->ibn not initialised -
			   from report & fix by <paubert@iram.es>.
			  Fix probe bug with EISA & PCI cards present from
                           report by <eirik@netcom.com>.
      0.541  24-Aug-98    Fix compiler problems associated with i386-string
                           ops from multiple bug reports and temporary fix


			   kernels and modules from bug report by
			   <Zlatko.Calusic@CARNet.hr> et al.
      0.542  15-Sep-98    Fix dc2114x_autoconf() to stop multiple messages
                           when media is unconnected.


                           a 21143 by <mmporter@home.com>.
			  Change PCI/EISA bus probing order.
      0.545  28-Nov-99    Further Moto SROM bug fix from


			   from report by <geert@linux-m68k.org>
      0.546  22-Feb-01    Fixes Alpha XP1000 oops.  The srom_search function
                           was causing a page fault when initializing the


      0.547  08-Nov-01    Use library crc32 functions by <Matt_Domsch@dell.com>
      0.548  30-Aug-03    Big 2.6 cleanup. Ported to PCI/EISA probing and
                           generic DMA APIs. Fixed DE425 support on Alpha.
* Copyright (c) 1998 - 2002  Frodo Looijaard <frodol@dds.nl>,
 *			      Kyösti Mälkki <kmalkki@cc.hut.fi>,
 *			      Mark Studebaker <mdsxyz123@yahoo.com>,
 *			      and Bob Dougherty <bobd@stanford.edu>
 *
 * (Some conversion-factor data were contributed by Jonathan Teh Soon Yew


 * From HWMon.cpp (Copyright 1998-2000 Jonathan Teh Soon Yew):
 * voltagefactor[0]=1.25/2628; (2628/1.25=2102.4)   // Vccp
 * voltagefactor[1]=1.25/2628; (2628/1.25=2102.4)   // +2.5V


 * (These conversions were contributed by Jonathan Teh Soon Yew
 * <j.teh@iname.com>)
 */
static inline u8 IN_TO_REG(long val, int in_num)


 * linear fits from HWMon.cpp (Copyright 1998-2000 Jonathan Teh Soon Yew)
 *	if(temp<169)
 *		return double(temp)*0.427-32.08;


 * A fifth-order polynomial fits the unofficial data (provided by Alex van
 * Kaam <darkside@chello.nl>) a bit better.  It also give more reasonable
 * numbers on my machine (ie. they agree with what my BIOS tells me).
 * Here's the fifth-order fit to the 8-bit data:
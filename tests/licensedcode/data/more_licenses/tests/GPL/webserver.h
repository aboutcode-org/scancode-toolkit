/*

webserver.h

--------------------------------------------------------------------------------
gSOAP XML Web services tools
Copyright (C) 2001-2004, Robert van Engelen, Genivia, Inc. All Rights Reserved.
This software is released under one of the following two licenses:
GPL or Genivia's license for commercial use.
--------------------------------------------------------------------------------
GPL license.

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA

Author contact information:
engelen@genivia.com / engelen@acm.org
--------------------------------------------------------------------------------
A commercial use license is available from Genivia, Inc., contact@genivia.com
--------------------------------------------------------------------------------

*/

//gsoap ns service name:	webserver
//gsoap ns service namespace:	http://www.cs.fsu.edu/~engelen/webserver.wsdl
//gsoap ns service location:	http://localhost:8080
//gsoap ns service style:	rpc
//gsoap ns service encoding:	encoded

//gsoap ns schema namespace: urn:demowebserver

int ns__add(double, double, double*);		// HTTP POST request - response
int ns__sub(double, double, double*);		// HTTP POST request - response
int ns__mul(double, double, double*);		// HTTP POST request - response
int ns__div(double, double, double*);		// HTTP POST request - response

//gsoap f schema namespace: urn:form

int f__form1(void);	// one-way MEP

int f__form2(struct f__formResponse { double result; } *);


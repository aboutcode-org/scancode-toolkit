/*
* The CIP4 Software License, Version 1.0
*
*
* Copyright (c) 2001-2004 The International Cooperation for the Integration of 
* Processes in  Prepress, Press and Postpress (CIP4).  All rights 
* reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions
* are met:
*
* 1. Redistributions of source code must retain the above copyright
*    notice, this list of conditions and the following disclaimer. 
*
* 2. Redistributions in binary form must reproduce the above copyright
*    notice, this list of conditions and the following disclaimer in
*    the documentation and/or other materials provided with the
*    distribution.
*
* 3. The end-user documentation included with the redistribution,
*    if any, must include the following acknowledgment:  
*       "This product includes software developed by the
*        The International Cooperation for the Integration of 
*        Processes in  Prepress, Press and Postpress (www.cip4.org)"
*    Alternately, this acknowledgment may appear in the software itself,
*    if and wherever such third-party acknowledgments normally appear.
*
* 4. The names "CIP4" and "The International Cooperation for the Integration of 
*    Processes in  Prepress, Press and Postpress" must
*    not be used to endorse or promote products derived from this
*    software without prior written permission. For written 
*    permission, please contact info@cip4.org.
*
* 5. Products derived from this software may not be called "CIP4",
*    nor may "CIP4" appear in their name, without prior written
*    permission of the CIP4 organization
*
* Usage of this software in commercial products is subject to restrictions. For
* details please consult info@cip4.org.
*
* THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
* WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
* OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED.  IN NO EVENT SHALL THE INTERNATIONAL COOPERATION FOR
* THE INTEGRATION OF PROCESSES IN PREPRESS, PRESS AND POSTPRESS OR
* ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
* SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
* LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
* USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
* OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
* SUCH DAMAGE.
* ====================================================================
*
* This software consists of voluntary contributions made by many
* individuals on behalf of the The International Cooperation for the Integration 
* of Processes in Prepress, Press and Postpress and was
* originally based on software 
* copyright (c) 1999-2001, Heidelberger Druckmaschinen AG 
* copyright (c) 1999-2001, Agfa-Gevaert N.V. 
*  
* For more information on The International Cooperation for the 
* Integration of Processes in  Prepress, Press and Postpress , please see
* <http://www.cip4.org/>.
*  
* 
*/
/******************************************************************************
*                     Copyright 1998 Agfa-Gevaert N.V.                       *
*                           All rights reserved                              *
*                                                                            *
* The material contained herein may not be reproduced in whole or in part,   *
*        without the prior written consent of Agfa-Gevaert N.V.              *
*                                                                            *
******************************************************************************/

/******************************************************************************
*	Includes
******************************************************************************/ 

#include <jdf/lang/Exception.h>
#include <jdf/util/myuti.h>

#include <jdf/io/ByteArrayInputStream.h>


namespace JDF
{
	
/******************************************************************************
*	Forward declarations
	******************************************************************************/ 
	
	
	/******************************************************************************
	*	Defines and constants
	******************************************************************************/ 
	
	/******************************************************************************
	*	Typedefs
	******************************************************************************/ 
	
	
	/******************************************************************************
	*	Classes
	******************************************************************************/ 
	
	/******************************************************************************
	*	Prototypes
	******************************************************************************/ 
	
	
	/******************************************************************************
	*	Implementation
	******************************************************************************/ 
	
ByteArrayInputStream::ByteArrayInputStream(char* buf, int blen,bool takeOwnership) :
mClosed			(false),
mMark			(0),
mPos			(0),
mCount			(blen),
	mBuf			(buf),
	mOwner			(takeOwnership)
{
}

ByteArrayInputStream::ByteArrayInputStream(char* buf, int blen, int off, int len,bool takeOwnership) :
mClosed			(false),
mMark			(0),
mPos			(off),
	mBuf			(buf),
	mOwner			(takeOwnership)
{
	mCount = std::min(blen,(off+len));
}

ByteArrayInputStream::~ByteArrayInputStream()
{
	if (mOwner)
		delete[] mBuf;
}

int ByteArrayInputStream::available()
{
	return mCount - mPos;
}

void ByteArrayInputStream::close()
{
	mClosed = true;
}

void ByteArrayInputStream::mark(int readAheadLimit)
{
	if (readAheadLimit < 0)
		throw IllegalArgumentException("ByteArrayInputStream readAheadLimit is negative");
	
	mMark = mPos;
}

bool ByteArrayInputStream::markSupported()
{
	return true;
}

int ByteArrayInputStream::read()
{	
	// speed up by not copying...
	return (mPos < mCount) ? (unsigned char) mBuf[mPos++] : -1; 
}

int ByteArrayInputStream::read(char* b, int blen)
{
	return ByteArrayInputStream::read(b,blen,0,blen);
}

int ByteArrayInputStream::read(char* b, int blen, int off, int len)
{
	//	if (mClosed == true)
	//		throw IOException("CharArrayInputStream has been closed");
	
	if (b == NULL)
		throw NullPointerException();
	
	if (blen < 0 || len < 0 || (off+len) < 0 || (off+len) > blen)
		throw IndexOutOfBoundsException("ByteArrayInputStream::read one of the arguments in out of bounds");
	
	if (mPos >= mCount)
		return -1;
	
	if ((mPos+len) > mCount)
		len = mCount - mPos;
	
	if (len <= 0)
		return 0;
	else
	{
		memcpy(b+off,mBuf+mPos,len);
		mPos += len;
		return len;
	}
}

void ByteArrayInputStream::reset()
{
	mPos = mMark;
}

long ByteArrayInputStream::skip(long n)
{
	//	if (mClosed == true)
	//	{
	//		throw IOException("CharArrayInputStream has been closed");
	//	}
	
	int available = mCount - mPos;
	
	if (n<=available)
	{
		mPos+=n;
		return n;
	}
	else
	{
		mPos+=available;
		return available;
	}
}

} // namespace JDF

/* end of file */

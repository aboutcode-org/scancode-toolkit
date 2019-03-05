/*! \file
Copyright (c) 2003, The Regents of the University of California, through
Lawrence Berkeley National Laboratory (subject to receipt of any required 
approvals from U.S. Dept. of Energy) 

All rights reserved. 

The source code is distributed under BSD license, see the file License.txt
at the top-level directory.
*/
/*! @file
 * \brief An approximate minimum degree column ordering algorithm
 */
/* ========================================================================== */
/* === colamd - a sparse matrix column ordering algorithm =================== */
/* ========================================================================== */

/*
    colamd:  An approximate minimum degree column ordering algorithm.

    Purpose:

	Colamd computes a permutation Q such that the Cholesky factorization of
	(AQ)'(AQ) has less fill-in and requires fewer floating point operations
	than A'A.  This also provides a good ordering for sparse partial
	pivoting methods, P(AQ) = LU, where Q is computed prior to numerical
	factorization, and P is computed during numerical factorization via
	conventional partial pivoting with row interchanges.  Colamd is the
	column ordering method used in SuperLU, part of the ScaLAPACK library.
	It is also available as user-contributed software for Matlab 5.2,
	available from MathWorks, Inc. (http://www.mathworks.com).  This
	routine can be used in place of COLMMD in Matlab.  By default, the \
	and / operators in Matlab perform a column ordering (using COLMMD)
	prior to LU factorization using sparse partial pivoting, in the
	built-in Matlab LU(A) routine.

    Authors:

	The authors of the code itself are Stefan I. Larimore and Timothy A.
	Davis (davis@cise.ufl.edu), University of Florida.  The algorithm was
	developed in collaboration with John Gilbert, Xerox PARC, and Esmond
	Ng, Oak Ridge National Laboratory.

    Date:

	August 3, 1998.  Version 1.0.

    Acknowledgements:

	This work was supported by the National Science Foundation, under
	grants DMS-9504974 and DMS-9803599.

    Notice:

	Copyright (c) 1998 by the University of Florida.  All Rights Reserved.

	THIS MATERIAL IS PROVIDED AS IS, WITH ABSOLUTELY NO WARRANTY
	EXPRESSED OR IMPLIED.  ANY USE IS AT YOUR OWN RISK.

	Permission is hereby granted to use or copy this program for any
	purpose, provided the above notices are retained on all copies.
	User documentation of any code that uses this code must cite the
	Authors, the Copyright, and "Used by permission."  If this code is
	accessible from within Matlab, then typing "help colamd" or "colamd"
	(with no arguments) must cite the Authors.  Permission to modify the
	code and to distribute modified code is granted, provided the above
	notices are retained, and a notice that the code was modified is
	included with the above copyright notice.  You must also retain the
	Availability information below, of the original version.

	This software is provided free of charge.

    Availability:

	This file is located at

		http://www.cise.ufl.edu/~davis/colamd/colamd.c

	The colamd.h file is required, located in the same directory.
	The colamdmex.c file provides a Matlab interface for colamd.
	The symamdmex.c file provides a Matlab interface for symamd, which is
	a symmetric ordering based on this code, colamd.c.  All codes are
	purely ANSI C compliant (they use no Unix-specific routines, include
	files, etc.).
*/

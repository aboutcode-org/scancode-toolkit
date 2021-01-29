/* ========================================================================== */
/* === colamd/symamd - a sparse matrix column ordering algorithm ============ */
/* ========================================================================== */

/* COLAMD / SYMAMD

    colamd:  an approximate minimum degree column ordering algorithm,
    	for LU factorization of symmetric or unsymmetric matrices,
	QR factorization, least squares, interior point methods for
	linear programming problems, and other related problems.

    symamd:  an approximate minimum degree ordering algorithm for Cholesky
    	factorization of symmetric matrices.

    Purpose:

	Colamd computes a permutation Q such that the Cholesky factorization of
	(AQ)'(AQ) has less fill-in and requires fewer floating point operations
	than A'A.  This also provides a good ordering for sparse partial
	pivoting methods, P(AQ) = LU, where Q is computed prior to numerical
	factorization, and P is computed during numerical factorization via
	conventional partial pivoting with row interchanges.  Colamd is the
	column ordering method used in SuperLU, part of the ScaLAPACK library.
	It is also available as built-in function in MATLAB Version 6,
	available from MathWorks, Inc. (http://www.mathworks.com).  This
	routine can be used in place of colmmd in MATLAB.

    	Symamd computes a permutation P of a symmetric matrix A such that the
	Cholesky factorization of PAP' has less fill-in and requires fewer
	floating point operations than A.  Symamd constructs a matrix M such
	that M'M has the same nonzero pattern of A, and then orders the columns
	of M using colmmd.  The column ordering of M is then returned as the
	row and column ordering P of A. 

    Authors:

	The authors of the code itself are Stefan I. Larimore and Timothy A.
	Davis (DrTimothyAldenDavis@gmail.com).  The algorithm was
	developed in collaboration with John Gilbert, Xerox PARC, and Esmond
	Ng, Oak Ridge National Laboratory.

    Acknowledgements:

	This work was supported by the National Science Foundation, under
	grants DMS-9504974 and DMS-9803599.

    Copyright and License:

	Copyright (c) 1998-2007, Timothy A. Davis, All Rights Reserved.
	COLAMD is also available under alternate licenses, contact T. Davis
	for details.

	This library is free software; you can redistribute it and/or
	modify it under the terms of the GNU Lesser General Public
	License as published by the Free Software Foundation; either
	version 2.1 of the License, or (at your option) any later version.

	This library is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
	Lesser General Public License for more details.

	You should have received a copy of the GNU Lesser General Public
	License along with this library; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
	USA

	Permission is hereby granted to use or copy this program under the
	terms of the GNU LGPL, provided that the Copyright, this License,
	and the Availability of the original version is retained on all copies.
	User documentation of any code that uses this code or any modified
	version of this code must cite the Copyright, this License, the
	Availability note, and "Used by permission." Permission to modify
	the code and to distribute modified code is granted, provided the
	Copyright, this License, and the Availability note are retained,
	and a notice that the code was modified is included.

    Availability:

	The colamd/symamd library is available at http://www.suitesparse.com
	Appears as ACM Algorithm 836.

    See the ChangeLog file for changes since Version 1.0.

    References:

	T. A. Davis, J. R. Gilbert, S. Larimore, E. Ng, An approximate column
	minimum degree ordering algorithm, ACM Transactions on Mathematical
	Software, vol. 30, no. 3., pp. 353-376, 2004.

	T. A. Davis, J. R. Gilbert, S. Larimore, E. Ng, Algorithm 836: COLAMD,
	an approximate column minimum degree ordering algorithm, ACM
	Transactions on Mathematical Software, vol. 30, no. 3., pp. 377-380,
	2004.

*/

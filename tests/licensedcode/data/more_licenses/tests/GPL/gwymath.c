/*
 *  @(#) $Id: gwymath.c 8874 2008-12-28 12:16:22Z yeti-dn $
 *  Copyright (C) 2003 David Necas (Yeti), Petr Klapetek.
 *  E-mail: yeti@gwyddion.net, klapetek@gwyddion.net.
 *
 *  The quicksort algorithm was copied from GNU C library,
 *  Copyright (C) 1991, 1992, 1996, 1997, 1999 Free Software Foundation, Inc.
 *  See below.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111 USA
 */

#include "config.h"
#include <string.h>
#include <libgwyddion/gwymacros.h>
#include <libgwyddion/gwymath.h>

/* Lower symmetric part indexing */
/* i MUST be greater or equal than j */
#define SLi(a, i, j) a[(i)*((i) + 1)/2 + (j)]

#define DSWAP(x, y) GWY_SWAP(gdouble, x, y)

/**
 * gwy_math_humanize_numbers:
 * @unit: The smallest possible step.
 * @maximum: The maximum possible value.
 * @precision: A location to store printf() precession, if not %NULL.
 *
 * Finds a human-friendly representation for a range of numbers.
 *
 * Returns: The magnitude i.e., a power of 1000.
 **/
gdouble
gwy_math_humanize_numbers(gdouble unit,
                          gdouble maximum,
                          gint *precision)
{
    gdouble lm, lu, mag, q;

    g_return_val_if_fail(unit >= 0.0, 0.0);
    g_return_val_if_fail(maximum >= 0.0, 0.0);

    if (G_UNLIKELY(unit == 0.0 || maximum == 0.0)) {
        if (unit > 0.0)
            maximum = unit;
        else if (maximum > 0.0)
            unit = maximum;
        else {
            if (precision)
                *precision = 1;
            return 1.0;
        }
    }

    lm = log10(maximum) + 1e-12;
    lu = log10(unit) - 1e-12;
    mag = 3.0*floor(lm/3.0);
    q = 3.0*ceil(lu/3.0);
    if (q > mag)
        q = 3.0*ceil((lu - 1.0)/3.0);
    if (lu > -0.5 && lm < 3.1) {
        while (lu > mag+2)
            mag += 3.0;
    }
    else if (lm <= 0.5 && lm > -1.5) {
        mag = 0.0;
    }
    else {
        while (q > mag)
            mag += 3.0;
    }

    if (precision) {
        *precision = MAX(0, ceil(mag - lu));
        *precision = MIN(*precision, 16);
    }

    return pow10(mag);
}

/**
 * gwy_math_is_in_polygon:
 * @x: The x coordinate of the test point.
 * @y: The y coordinate of the test point.
 * @poly: An array of coordinate pairs (points) that define a
 *        polygon.
 * @n: The number of corners of the polygon.
 *
 * Establishes wether the test point @x, @y is inside the polygon @poly.
 * The polygon can be defined either clockwise or anti-clockwise and
 * can be a concave, convex or self-intersecting polygon.
 *
 * <warning> Result can be either TRUE or FALSE if the test point
 * is *exactly* on an edge. </warning>
 *
 * Returns: TRUE if the test point is inside poly and FALSE otherwise.
 *
 * Since: 2.7
 **/
/* This neat little check algorithm  was found at
   http://alienryderflex.com/polygon and has been adapted*/
gboolean
gwy_math_is_in_polygon(gdouble x,
                       gdouble y,
                       const gdouble *poly,
                       guint n)
{
    guint i, j = 0;
    gboolean inside = FALSE;
    gdouble xx, yy;

    for (i = 0; i < n; i++) {
        j++;
        if (j == n)
            j = 0;
        if ((poly[2*i + 1] < y && poly[2*j + 1] >= y)
            || (poly[2*j + 1] < y && poly[2*i + 1] >= y)) {
            xx = poly[2*j] - poly[2*i];
            yy = poly[2*j + 1] - poly[2*i + 1];
            if (poly[2*i] + ((y - poly[2*i + 1]) / yy)*xx < x)
                inside = !inside;
        }
    }

    return inside;
}

/**
 * gwy_math_find_nearest_line:
 * @x: X-coordinate of the point to search.
 * @y: Y-coordinate of the point to search.
 * @d2min: Where to store the squared minimal distance, or %NULL.
 * @n: The number of lines (i.e. @coords has 4@n items).
 * @coords: Line coordinates stored as x00, y00, x01, y01, x10, y10, etc.
 * @metric: Metric matrix (2x2, but stored sequentially by rows: m11, m12,
 *          m21, m22), it must be positive definite.  Vector norm is then
 *          calculated as m11*x*x + (m12 + m21)*x*y + m22*y*y.
 *          It can be %NULL, standard Euclidean metric is then used.
 *
 * Finds the line from @coords nearest to the point (@x, @y).
 *
 * Returns: The line number. It may return -1 if (@x, @y) doesn't lie
 *          in the orthogonal stripe of any of the lines.
 **/
gint
gwy_math_find_nearest_line(gdouble x, gdouble y,
                           gdouble *d2min,
                           gint n, const gdouble *coords,
                           const gdouble *metric)
{
    gint i, m;
    gdouble vx, vy, d, d2m = G_MAXDOUBLE;

    g_return_val_if_fail(n > 0, -1);
    g_return_val_if_fail(coords, -1);

    m = -1;
    if (metric) {
        for (i = 0; i < n; i++) {
            gdouble xx = x - (coords[0] + coords[2])/2;
            gdouble yy = y - (coords[1] + coords[3])/2;

            vx = (coords[2] - coords[0])/2;
            vy = (coords[3] - coords[1])/2;
            coords += 4;
            if (vx == 0.0 && vy == 0.0)
                continue;
            d = metric[0]*vx*vx + (metric[1] + metric[2])*vx*vy
                + metric[3]*vy*vy;
            if (d <= 0.0) {
                g_warning("Metric does not evaluate as positive definite");
                continue;
            }
            d = -(metric[0]*vx*xx + (metric[1] + metric[2])*(vx*yy + vy*xx)/2
                  + metric[3]*vy*yy)/d;
            /* Out of orthogonal stripe */
            if (d < -1.0 || d > 1.0)
                continue;
            d = metric[0]*(xx + vx*d)*(xx + vx*d)
                + (metric[1] + metric[2])*(xx + vx*d)*(yy + vy*d)
                + metric[3]*(yy + vy*d)*(yy + vy*d);
            if (d < d2m) {
                d2m = d;
                m = i;
            }
        }
    }
    else {
        for (i = 0; i < n; i++) {
            gdouble xl0 = *(coords++);
            gdouble yl0 = *(coords++);
            gdouble xl1 = *(coords++);
            gdouble yl1 = *(coords++);

            vx = yl1 - yl0;
            vy = xl0 - xl1;
            if (vx == 0.0 && vy == 0.0)
                continue;
            if (vx*(y - yl0) < vy*(x - xl0))
                continue;
            if (vx*(yl1 - y) < vy*(xl1 - x))
                continue;
            d = vx*(x - xl0) + vy*(y - yl0);
            d *= d/(vx*vx + vy*vy);
            if (d < d2m) {
                d2m = d;
                m = i;
            }
        }
    }
    if (d2min)
      *d2min = d2m;

    return m;
}

/**
 * gwy_math_find_nearest_point:
 * @x: X-coordinate of the point to search.
 * @y: Y-coordinate of the point to search.
 * @d2min: Location to store the squared minimal distance to, or %NULL.
 * @n: The number of points (i.e. @coords has 2@n items).
 * @coords: Point coordinates stored as x0, y0, x1, y1, x2, y2, etc.
 * @metric: Metric matrix (2x2, but stored sequentially by rows: m11, m12,
 *          m21, m22).  Vector norm is then calculated as
 *          m11*x*x + (m12 + m21)*x*y + m22*y*y.
 *          It can be %NULL, standard Euclidean metric is then used.
 *
 * Finds the point from @coords nearest to the point (@x, @y).
 *
 * Returns: The point number.
 **/
gint
gwy_math_find_nearest_point(gdouble x, gdouble y,
                            gdouble *d2min,
                            gint n, const gdouble *coords,
                            const gdouble *metric)
{
    gint i, m;
    gdouble d, xd, yd, d2m = G_MAXDOUBLE;

    g_return_val_if_fail(n > 0, -1);
    g_return_val_if_fail(coords, -1);

    m = 0;
    if (metric) {
        for (i = 0; i < n; i++) {
            xd = *(coords++) - x;
            yd = *(coords++) - y;
            d = metric[0]*xd*xd + (metric[1] + metric[2])*xd*yd
                + metric[3]*yd*yd;
            if (d < d2m) {
                d2m = d;
                m = i;
            }
        }
    }
    else {
        for (i = 0; i < n; i++) {
            xd = *(coords++) - x;
            yd = *(coords++) - y;
            d = xd*xd + yd*yd;
            if (d < d2m) {
                d2m = d;
                m = i;
            }
        }
    }
    if (d2min)
      *d2min = d2m;

    return m;
}

/**
 * gwy_math_lin_solve:
 * @n: The size of the system.
 * @matrix: The matrix of the system (@n times @n), ordered by row, then
 *          column.
 * @rhs: The right hand side of the sytem.
 * @result: Where the result should be stored.  May be %NULL to allocate
 *          a fresh array for the result.
 *
 * Solve a regular system of linear equations.
 *
 * Returns: The solution (@result if it wasn't %NULL), may be %NULL if the
 *          matrix is singular.
 **/
gdouble*
gwy_math_lin_solve(gint n, const gdouble *matrix,
                   const gdouble *rhs,
                   gdouble *result)
{
    gdouble *m, *r;

    g_return_val_if_fail(n > 0, NULL);
    g_return_val_if_fail(matrix && rhs, NULL);

    m = (gdouble*)g_memdup(matrix, n*n*sizeof(gdouble));
    r = (gdouble*)g_memdup(rhs, n*sizeof(gdouble));
    result = gwy_math_lin_solve_rewrite(n, m, r, result);
    g_free(r);
    g_free(m);

    return result;
}

/**
 * gwy_math_lin_solve_rewrite:
 * @n: The size of the system.
 * @matrix: The matrix of the system (@n times @n), ordered by row, then
 *          column.
 * @rhs: The right hand side of the sytem.
 * @result: Where the result should be stored.  May be %NULL to allocate
 *          a fresh array for the result.
 *
 * Solves a regular system of linear equations.
 *
 * This is a memory-conservative version of gwy_math_lin_solve() overwriting
 * @matrix and @rhs with intermediate results.
 *
 * Returns: The solution (@result if it wasn't %NULL), may be %NULL if the
 *          matrix is singular.
 **/
gdouble*
gwy_math_lin_solve_rewrite(gint n, gdouble *matrix,
                           gdouble *rhs,
                           gdouble *result)
{
    gint *perm;
    gint i, j, jj;

    g_return_val_if_fail(n > 0, NULL);
    g_return_val_if_fail(matrix && rhs, NULL);

    perm = g_new(gint, n);

    /* elimination */
    for (i = 0; i < n; i++) {
        gdouble *row = matrix + i*n;
        gdouble piv = 0;
        gint pivj = 0;

        /* find pivot */
        for (j = 0; j < n; j++) {
            if (fabs(row[j]) > piv) {
                pivj = j;
                piv = fabs(row[j]);
            }
        }
        if (piv == 0.0) {
            g_warning("Singluar matrix");
            g_free(perm);
            return NULL;
        }
        piv = row[pivj];
        perm[i] = pivj;

        /* subtract */
        for (j = i+1; j < n; j++) {
            gdouble *jrow = matrix + j*n;
            gdouble q = jrow[pivj]/piv;

            for (jj = 0; jj < n; jj++)
                jrow[jj] -= q*row[jj];

            jrow[pivj] = 0.0;
            rhs[j] -= q*rhs[i];
        }
    }

    /* back substitute */
    if (!result)
        result = g_new(gdouble, n);
    for (i = n-1; i >= 0; i--) {
        gdouble *row = matrix + i*n;
        gdouble x = rhs[i];

        for (j = n-1; j > i; j--)
            x -= result[perm[j]]*row[perm[j]];

        result[perm[i]] = x/row[perm[i]];
    }
    g_free(perm);

    return result;
}

/**
 * gwy_math_fit_polynom:
 * @ndata: The number of items in @xdata, @ydata.
 * @xdata: Independent variable data (of size @ndata).
 * @ydata: Dependent variable data (of size @ndata).
 * @n: The degree of polynom to fit.
 * @coeffs: An array of size @n+1 to store the coefficients to, or %NULL
 *          (a fresh array is allocated then).
 *
 * Fits a polynom through a general (x, y) data set.
 *
 * Returns: The coefficients of the polynom (@coeffs when it was not %NULL,
 *          otherwise a newly allocated array).
 **/
gdouble*
gwy_math_fit_polynom(gint ndata,
                     const gdouble *xdata,
                     const gdouble *ydata,
                     gint n,
                     gdouble *coeffs)
{
    gdouble *sumx, *m;
    gint i, j;

    g_return_val_if_fail(ndata >= 0, NULL);
    g_return_val_if_fail(n >= 0, NULL);

    sumx = g_new0(gdouble, 2*n+1);

    if (!coeffs)
        coeffs = g_new0(gdouble, n+1);
    else
        gwy_clear(coeffs, n+1);

    for (i = 0; i < ndata; i++) {
        gdouble x = xdata[i];
        gdouble y = ydata[i];
        gdouble xp;

        xp = 1.0;
        for (j = 0; j <= n; j++) {
            sumx[j] += xp;
            coeffs[j] += xp*y;
            xp *= x;
        }
        for (j = n+1; j <= 2*n; j++) {
            sumx[j] += xp;
            xp *= x;
        }
    }

    m = g_new(gdouble, (n+1)*(n+2)/2);
    for (i = 0; i <= n; i++) {
        gdouble *row = m + i*(i+1)/2;

        for (j = 0; j <= i; j++)
            row[j] = sumx[i+j];
    }
    if (!gwy_math_choleski_decompose(n+1, m))
        gwy_clear(coeffs, n+1);
    else
        gwy_math_choleski_solve(n+1, m, coeffs);

    g_free(m);
    g_free(sumx);

    return coeffs;
}

/**
 * gwy_math_choleski_decompose:
 * @n: The dimension of @a.
 * @matrix: Lower triangular part of a symmetric matrix, stored by rows, i.e.,
 *          matrix = [a_00 a_10 a_11 a_20 a_21 a_22 a_30 ...].
 *
 * Decomposes a symmetric positive definite matrix in place.
 *
 * Returns: Whether the matrix was really positive definite.  If %FALSE,
 *          the decomposition failed and @a does not contain any meaningful
 *          values.
 **/
gboolean
gwy_math_choleski_decompose(gint dim, gdouble *a)
{
    gint i, j, k;
    gdouble s, r;

    for (k = 0; k < dim; k++) {
        /* diagonal element */
        s = SLi(a, k, k);
        for (i = 0; i < k; i++)
            s -= SLi(a, k, i) * SLi(a, k, i);
        if (s <= 0.0)
            return FALSE;
        SLi(a, k, k) = s = sqrt(s);

        /* nondiagonal elements */
        for (j = k+1; j < dim; j++) {
            r = SLi(a, j, k);
            for (i = 0; i < k; i++)
                r -= SLi(a, k, i) * SLi(a, j, i);
            SLi(a, j, k) = r/s;
        }
    }

    return TRUE;
}

/**
 * gwy_math_choleski_solve:
 * @n: The dimension of @a.
 * @decomp: Lower triangular part of Choleski decomposition as computed
 *          by gwy_math_choleski_decompose().
 * @rhs: Right hand side vector.  Is is modified in place, on return it
 *       contains the solution.
 *
 * Solves a system of linear equations with predecomposed symmetric positive
 * definite matrix @a and right hand side @b.
 **/
void
gwy_math_choleski_solve(gint dim, const gdouble *a, gdouble *b)
{
    gint i, j;

    /* back-substitution with the lower triangular matrix */
    for (j = 0; j < dim; j++) {
        for (i = 0; i < j; i++)
            b[j] -= SLi(a, j, i)*b[i];
        b[j] /= SLi(a, j, j);
    }

    /* back-substitution with the upper triangular matrix */
    for (j = dim-1; j >= 0; j--) {
        for (i = j+1; i < dim; i++)
            b[j] -= SLi(a, i, j)*b[i];
        b[j] /= SLi(a, j, j);
    }
}

/**
 * gwy_math_tridiag_solve_rewrite:
 * @n: The dimension of @d.
 * @d: The diagonal of a tridiagonal matrix, its contents will be overwritten.
 * @a: The above-diagonal stripe (it has @n-1 elements).
 * @b: The below-diagonal stripe (it has @n-1 elements).
 * @rhs: The right hand side of the system, upon return it will contain the
 *       solution.
 *
 * Solves a tridiagonal system of linear equations.
 *
 * Returns: %TRUE if the elimination suceeded, %FALSE if the system is
 *          (numerically) singular.  The contents of @d and @rhs may be
 *          overwritten in the case of failure too, but not to any meaningful
 *          values.
 **/
gboolean
gwy_math_tridiag_solve_rewrite(gint n,
                               gdouble *d,
                               const gdouble *a,
                               const gdouble *b,
                               gdouble *rhs)
{
    gint i;

    g_return_val_if_fail(n > 0, FALSE);

    /* Eliminate b[elow diagonal] */
    for (i = 0; i < n-1; i++) {
        /* If d[i] is zero, elimination fails (now or later) */
        if (!d[i])
            return FALSE;
        d[i+1] -= b[i]/d[i]*a[i];
        rhs[i+1] -= b[i]/d[i]*rhs[i];
    }
    if (!d[n-1])
        return FALSE;

    /* Eliminate a[bove diagonal], calculating the solution */
    for (i = n-1; i > 0; i--) {
        rhs[i] /= d[i];
        rhs[i-1] -= a[i-1]*rhs[i];
    }
    rhs[0] /= d[0];

    return TRUE;
}

/* Quickly find median value in an array
 * based on public domain code by Nicolas Devillard */
/**
 * gwy_math_median:
 * @n: Number of items in @array.
 * @array: Array of doubles.  It is modified by this function.  All values are
 *         kept, but their positions in the array change.
 *
 * Finds median of an array of values using Quick select algorithm.
 *
 * Returns: The median value of @array.
 **/
gdouble
gwy_math_median(gsize n, gdouble *array)
{
    gsize lo, hi;
    gsize median;
    gsize middle, ll, hh;

    lo = 0;
    hi = n - 1;
    median = n/2;
    while (TRUE) {
        if (hi <= lo)        /* One element only */
            return array[median];

        if (hi == lo + 1) {  /* Two elements only */
            if (array[lo] > array[hi])
                DSWAP(array[lo], array[hi]);
            return array[median];
        }

        /* Find median of lo, middle and hi items; swap into position lo */
        middle = (lo + hi)/2;
        if (array[middle] > array[hi])
            DSWAP(array[middle], array[hi]);
        if (array[lo] > array[hi])
            DSWAP(array[lo], array[hi]);
        if (array[middle] > array[lo])
            DSWAP(array[middle], array[lo]);

        /* Swap low item (now in position middle) into position (lo+1) */
        DSWAP(array[middle], array[lo + 1]);

        /* Nibble from each end towards middle, swapping items when stuck */
        ll = lo + 1;
        hh = hi;
        while (TRUE) {
            do {
                ll++;
            } while (array[lo] > array[ll]);
            do {
                hh--;
            } while (array[hh] > array[lo]);

            if (hh < ll)
                break;

            DSWAP(array[ll], array[hh]);
        }

        /* Swap middle item (in position lo) back into correct position */
        DSWAP(array[lo], array[hh]);

        /* Re-set active partition */
        if (hh <= median)
            lo = ll;
        if (hh >= median)
            hi = hh - 1;
    }
}

/* Note: The implementation was specialized for doubles and a few things were
 * renamed, otherwise it has not changed.  It is about twice faster than the
 * generic version. */

/* Copyright (C) 1991, 1992, 1996, 1997, 1999 Free Software Foundation, Inc.
   This file is part of the GNU C Library.
   Written by Douglas C. Schmidt (schmidt@ics.uci.edu).

   The GNU C Library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   The GNU C Library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the GNU C Library; if not, write to the Free
   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
   02111-1307 USA.  */

/* If you consider tuning this algorithm, you should consult first:
   Engineering a sort function; Jon Bentley and M. Douglas McIlroy;
   Software - Practice and Experience; Vol. 23 (11), 1249-1265, 1993.  */

/* Discontinue quicksort algorithm when partition gets below this size.
   This particular magic number was chosen to work best on a Sun 4/260. */
/* #define MAX_THRESH 4 */
/* Note: Specialization makes the insertion sort part relatively more
 * efficient, after some benchmarking this seems be about the best value
 * on Athlon 64. */
#define MAX_THRESH 12

/* Stack node declarations used to store unfulfilled partition obligations. */
typedef struct {
    gdouble *lo;
    gdouble *hi;
} stack_node;

/* The next 4 #defines implement a very fast in-line stack abstraction. */
/* The stack needs log (total_elements) entries (we could even subtract
   log(MAX_THRESH)).  Since total_elements has type size_t, we get as
   upper bound for log (total_elements):
   bits per byte (CHAR_BIT) * sizeof(size_t).  */
#define STACK_SIZE      (CHAR_BIT * sizeof(gsize))
#define PUSH(low, high) ((void) ((top->lo = (low)), (top->hi = (high)), ++top))
#define POP(low, high)  ((void) (--top, (low = top->lo), (high = top->hi)))
#define STACK_NOT_EMPTY (stack < top)

/* Order size using quicksort.  This implementation incorporates
   four optimizations discussed in Sedgewick:

   1. Non-recursive, using an explicit stack of pointer that store the
   next array partition to sort.  To save time, this maximum amount
   of space required to store an array of SIZE_MAX is allocated on the
   stack.  Assuming a 32-bit (64 bit) integer for size_t, this needs
   only 32 * sizeof(stack_node) == 256 bytes (for 64 bit: 1024 bytes).
   Pretty cheap, actually.

   2. Chose the pivot element using a median-of-three decision tree.
   This reduces the probability of selecting a bad pivot value and
   eliminates certain extraneous comparisons.

   3. Only quicksorts TOTAL_ELEMS / MAX_THRESH partitions, leaving
   insertion sort to order the MAX_THRESH items within each partition.
   This is a big win, since insertion sort is faster for small, mostly
   sorted array segments.

   4. The larger of the two sub-partitions is always pushed onto the
   stack first, with the algorithm then concentrating on the
   smaller partition.  This *guarantees* no more than log(n)
   stack size is needed (actually O(1) in this case)!  */

/**
 * gwy_math_sort:
 * @n: Number of items in @array.
 * @array: Array of doubles to sort in place.
 *
 * Sorts an array of doubles using a quicksort algorithm.
 *
 * This is usually about twice as fast as the generic quicksort function
 * thanks to specialization for doubles.
 **/
void
gwy_math_sort(gsize n,
              gdouble *array)
{
    if (n < 2)
        /* Avoid lossage with unsigned arithmetic below.  */
        return;

    if (n > MAX_THRESH) {
        gdouble *lo = array;
        gdouble *hi = lo + (n - 1);
        stack_node stack[STACK_SIZE];
        stack_node *top = stack + 1;

        while (STACK_NOT_EMPTY) {
            gdouble *left_ptr;
            gdouble *right_ptr;

            /* Select median value from among LO, MID, and HI. Rearrange
               LO and HI so the three values are sorted. This lowers the
               probability of picking a pathological pivot value and
               skips a comparison for both the LEFT_PTR and RIGHT_PTR in
               the while loops. */

            gdouble *mid = lo + ((hi - lo) >> 1);

            if (*mid < *lo)
                DSWAP(*mid, *lo);
            if (*hi < *mid)
                DSWAP(*mid, *hi);
            else
                goto jump_over;
            if (*mid < *lo)
                DSWAP(*mid, *lo);
jump_over: ;

          left_ptr  = lo + 1;
          right_ptr = hi - 1;

          /* Here's the famous ``collapse the walls'' section of quicksort.
             Gotta like those tight inner loops!  They are the main reason
             that this algorithm runs much faster than others. */
          do {
              while (*left_ptr < *mid)
                  left_ptr++;

              while (*mid < *right_ptr)
                  right_ptr--;

              if (left_ptr < right_ptr) {
                  DSWAP(*left_ptr, *right_ptr);
                  if (mid == left_ptr)
                      mid = right_ptr;
                  else if (mid == right_ptr)
                      mid = left_ptr;
                  left_ptr++;
                  right_ptr--;
              }
              else if (left_ptr == right_ptr) {
                  left_ptr++;
                  right_ptr--;
                  break;
              }
          }
          while (left_ptr <= right_ptr);

          /* Set up pointers for next iteration.  First determine whether
             left and right partitions are below the threshold size.  If so,
             ignore one or both.  Otherwise, push the larger partition's
             bounds on the stack and continue sorting the smaller one. */

          if ((gsize)(right_ptr - lo) <= MAX_THRESH) {
              if ((gsize)(hi - left_ptr) <= MAX_THRESH)
                  /* Ignore both small partitions. */
                  POP(lo, hi);
              else
                  /* Ignore small left partition. */
                  lo = left_ptr;
          }
          else if ((gsize)(hi - left_ptr) <= MAX_THRESH)
              /* Ignore small right partition. */
              hi = right_ptr;
          else if ((right_ptr - lo) > (hi - left_ptr)) {
              /* Push larger left partition indices. */
              PUSH(lo, right_ptr);
              lo = left_ptr;
          }
          else {
              /* Push larger right partition indices. */
              PUSH(left_ptr, hi);
              hi = right_ptr;
          }
        }
    }

    /* Once the BASE_PTR array is partially sorted by quicksort the rest
       is completely sorted using insertion sort, since this is efficient
       for partitions below MAX_THRESH size. BASE_PTR points to the beginning
       of the array to sort, and END_PTR points at the very last element in
       the array (*not* one beyond it!). */

    {
        double *const end_ptr = array + (n - 1);
        double *tmp_ptr = array;
        double *thresh = MIN(end_ptr, array + MAX_THRESH);
        register gdouble *run_ptr;

        /* Find smallest element in first threshold and place it at the
           array's beginning.  This is the smallest array element,
           and the operation speeds up insertion sort's inner loop. */

        for (run_ptr = tmp_ptr + 1; run_ptr <= thresh; run_ptr++) {
            if (*run_ptr < *tmp_ptr)
                tmp_ptr = run_ptr;
        }

        if (tmp_ptr != array)
            DSWAP(*tmp_ptr, *array);

        /* Insertion sort, running from left-hand-side up to right-hand-side.
         */

        run_ptr = array + 1;
        while (++run_ptr <= end_ptr) {
            tmp_ptr = run_ptr - 1;
            while (*run_ptr < *tmp_ptr)
                tmp_ptr--;

            tmp_ptr++;
            if (tmp_ptr != run_ptr) {
                gdouble *hi, *lo;
                gdouble d;

                d = *run_ptr;
                for (hi = lo = run_ptr; --lo >= tmp_ptr; hi = lo)
                    *hi = *lo;
                *hi = d;
            }
        }
    }
}

/************************** Documentation ****************************/

/**
 * SECTION:gwymath
 * @title: Math
 * @short_description: Mathematical utility functions
 * @see_also: #GwyNLFitter, non-linear least square fitter;
 *            <link linkend="gwymathfallback">Math Fallback</link>,
 *            fallback mathematical functions
 *
 * Functions gwy_math_SI_prefix() and gwy_math_humanize_numbers() deal with
 * number representation.
 *
 * Nearest object finding functions gwy_math_find_nearest_line() and
 * gwy_math_find_nearest_point() can be useful in widget and vector layer
 * implementation.
 *
 * And gwy_math_lin_solve(), gwy_math_lin_solve_rewrite(), and
 * gwy_math_fit_polynom() are general purpose numeric methods.
 **/

/**
 * ROUND:
 * @x: A double value.
 *
 * Rounds a number to nearest integer.  Use %GWY_ROUND instead.
 **/

/**
 * GWY_ROUND:
 * @x: A double value.
 *
 * Rounds a number to nearest integer.
 *
 * Since: 2.5
 **/

/**
 * GWY_SQRT3:
 *
 * The square root of 3.
 **/

/**
 * GWY_SQRT_PI:
 *
 * The square root of pi.
 **/

/**
 * SECTION:gwymathfallback
 * @title: Math Fallback
 * @short_description: Fallback implementations of standard mathematical
 *                     functions
 * @include: libgwyddion/gwymathfallback.h
 *
 * Fallback functions
 * <function>gwy_math_fallback_<replaceable>foo</replaceable></function> are
 * defined for mathematical functions
 * <function><replaceable>foo</replaceable></function> that might not be
 * implemented on all platforms and are commonly used in Gwyddion.  These
 * functions are always defined (as <literal>static inline</literal>), however,
 * you should not use them as they can be less efficient or precise than the
 * standard functions.
 *
 * For each unavailable function (and only for those), this header file defines
 * a replacement macro expanding to the name of the fallback function.
 * Therefore after including it, you can use for instance
 * <function>cbrt</function> regardless if the platform provides it or not.
 * Note this header has to be included explicitly to avoid possible inadvertent
 * clashes with other definitions of <function>cbrt</function>.
 *
 * Since all replacement macros expand to names of functions, it is possible
 * to take the address of any of them.
 **/

/**
 * gwy_math_fallback_cbrt:
 * @x: Floating point number.
 * @returns: Cubic root of @x.
 *
 * Fallback for the standard mathematical function
 * <function>cbrt</function>.
 *
 * Since: 2.9
 **/

/**
 * cbrt:
 *
 * Macro defined to gwy_math_callback_cbrt() if the platform does not provide
 * <function>cbrt</function>.
 **/

/**
 * gwy_math_fallback_pow10:
 * @x: Floating point number.
 * @returns: 10 raised to @x.
 *
 * Fallback for the standard mathematical function
 * <function>pow10</function>.
 *
 * Since: 2.9
 **/

/**
 * pow10:
 *
 * Macro defined to gwy_math_callback_pow10() if the platform does not provide
 * <function>pow10</function>.
 **/

/**
 * gwy_math_fallback_hypot:
 * @x: Floating point number.
 * @y: Floating point number.
 * @returns: Length of hypotenuse of a right-angle triangle with sides of
 *           lengths @x and @y.
 *
 * Fallback for the standard mathematical function
 * <function>hypot</function>.
 *
 * Since: 2.9
 **/

/**
 * hypot:
 *
 * Macro defined to gwy_math_callback_hypot() if the platform does not provide
 * <function>hypot</function>.
 **/

/**
 * gwy_math_fallback_acosh:
 * @x: Floating point number greater or equal to 1.0.
 * @returns: Inverse hyperbolic cosine of @x.
 *
 * Fallback for the standard mathematical function
 * <function>acosh</function>.
 *
 * Since: 2.9
 **/

/**
 * acosh:
 *
 * Macro defined to gwy_math_callback_acosh() if the platform does not provide
 * <function>acosh</function>.
 **/

/**
 * gwy_math_fallback_asinh:
 * @x: Floating point number.
 * @returns: Inverse hyperbolic sine of @x.
 *
 * Fallback for the standard mathematical function
 * <function>asinh</function>.
 *
 * Since: 2.9
 **/

/**
 * asinh:
 *
 * Macro defined to gwy_math_callback_asinh() if the platform does not provide
 * <function>asinh</function>.
 **/

/**
 * gwy_math_fallback_atanh:
 * @x: Floating point number in the range [-1, 1].
 * @returns: Inverse hyperbolic tangent of @x.
 *
 * Fallback for the standard mathematical function
 * <function>atanh</function>.
 *
 * Since: 2.9
 **/

/**
 * atanh:
 *
 * Macro defined to gwy_math_callback_atanh() if the platform does not provide
 * <function>atanh</function>.
 **/

/* vim: set cin et ts=4 sw=4 cino=>1s,e0,n0,f0,{0,}0,^0,\:1s,=0,g1s,h0,t0,+1s,c3,(0,u0 : */

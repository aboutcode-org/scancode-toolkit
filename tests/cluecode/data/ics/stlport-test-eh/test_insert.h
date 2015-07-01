/***********************************************************************************
  test_insert.h

 * Copyright (c) 1997
 * Mark of the Unicorn, Inc.
 *
 * Permission to use, copy, modify, distribute and sell this software
 * and its documentation for any purpose is hereby granted without fee,
 * provided that the above copyright notice appear in all copies and
 * that both that copyright notice and this permission notice appear
 * in supporting documentation.  Mark of the Unicorn makes no
 * representations about the suitability of this software for any
    void operator()( C& c ) const
    {
//        prepare_insert_range( c, fPos, fFirst, fLast );
        do_insert_range( c, fPos, fFirst, fLast, container_category(c) );

        // Prevent simulated failures during verification
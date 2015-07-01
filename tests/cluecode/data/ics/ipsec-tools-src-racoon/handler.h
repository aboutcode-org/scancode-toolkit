/* Id: handler.h,v 1.19 2006/02/25 08:25:12 manubsd Exp */

/*
 * Copyright (C) 1995, 1996, 1997, and 1998 WIDE Project.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *                                               sync iv(B) with ive(B).
 *                                               check auth, integrity.
 *                                               encode by ive(B).
 * save to ive(C).          <--[packet(C)]---    save to iv(C).
 * decoded by iv(B).
 *      :
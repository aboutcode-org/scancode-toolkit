# matching.py - bipartite graph maximum matching algorithms
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
# This module uses material from the Wikipedia article Hopcroft--Karp algorithm
# <https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm>, accessed on
# January 3, 2015, which is released under the Creative Commons
# Attribution-Share-Alike License 3.0
# <http://creativecommons.org/licenses/by-sa/3.0/>. That article includes
# pseudocode, which has been translated into the corresponding Python code.
#
# Portions of this module use code from David Eppstein's Python Algorithms and
# Data Structures (PADS) library, which is dedicated to the public domain (for
# proof, see <http://www.ics.uci.edu/~eppstein/PADS/ABOUT-PADS.txt>).
"""Provides functions for computing a maximum cardinality matching in a
bipartite graph.

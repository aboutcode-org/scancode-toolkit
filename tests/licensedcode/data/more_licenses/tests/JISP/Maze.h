//---------------------------------------------------------------------
//  A Set of Tools for Exploring Mazes
//
//  Maze.h
//  version 1.0.0
//
//-----------------------------------------------------------------------
//
//  COPYRIGHT NOTICE, DISCLAIMER, and LICENSE:
//  
//  If you modify this file, you may insert additional notices
//  immediately following this sentence.
//  
//  Copyright 2001 Scott Robert Ladd.
//  All rights reserved, except as noted herein.
//  
//  This computer program source file is supplied "AS IS". Scott Robert
//  Ladd (hereinafter referred to as "Author") disclaims all warranties,
//  expressed or implied, including, without limitation, the warranties
//  of merchantability and of fitness for any purpose. The Author
//  assumes no liability for direct, indirect, incidental, special,
//  exemplary, or consequential damages, which may result from the use
//  of this software, even if advised of the possibility of such damage.
//  
//  The Author hereby grants anyone permission to use, copy, modify, and
//  distribute this source code, or portions hereof, for any purpose,
//  without fee, subject to the following restrictions:
//  
//      1. The origin of this source code must not be misrepresented.
//  
//      2. Altered versions must be plainly marked as such and must not
//         be misrepresented as being the original source.
//  
//      3. This Copyright notice may not be removed or altered from any
//         source or altered source distribution.
//  
//  The Author specifically permits (without fee) and encourages the use
//  of this source code for entertainment, education, or decoration. If
//  you use this source code in a product, acknowledgment is not required
//  but would be appreciated.
//  
//  Acknowledgement:
//      This license is based on the wonderful simple license that
//      accompanies libpng.
//
//-----------------------------------------------------------------------
//
//  For more information on this software package, please visit
//  Scott's web site, Coyote Gulch Productions, at:
//
//      http://www.coyotegulch.com
//  
//-----------------------------------------------------------------------

#if !defined(COYOTE_MAZE_H)
#define COYOTE_MAZE_H

#include <string>
#include <iostream>
#include <cstddef>

namespace CoyoteGulch
{
    class Maze
    {
    // TYPE DECLARATIONS
    public:
        // a value representing the state of a wall
        enum Wall
        {
            WALL_OPEN,
            WALL_CLOSED,
            WALL_SOLID
        };

        // wall identifiers for the four cardinal directions
        enum Direction
        {
            DIR_NORTH,
            DIR_EAST,
            DIR_SOUTH,
            DIR_WEST
        };

        // a row-column position in the maze
        struct Position
        {
            size_t m_row;
            size_t m_col;
        };

        // a cell in a 2D maze grid
        struct Cell
        {
            Wall * m_walls[4];

            // constructor
            Cell();

            // destructor
            Cell(const Cell & source);

            // assignment operator
            Cell & operator = (const Cell & source);

            // destructor
            ~Cell();
        };

        // pluggable object to randomize a Maze
        class Architect
        {
        // INTERFACE
        public:
            // creates a floor plan for a maze
            virtual void CreateFloorPlan(Maze & target) = 0;

        // UTILITIES
        protected:
            // access to data elements in a maze
            static size_t & GetWidth(Maze & target)      { return target.m_width;    }
            static size_t & GetHeight(Maze & target)     { return target.m_height;   }
            static Position & GetEntrance(Maze & target) { return target.m_entrance; }
            static Position & GetExit(Maze & target)     { return target.m_exit;     }
            static Cell ** GetCells(Maze & target)       { return target.m_cells;    }
        };

        // this is a friend so derived types can access Maze elements
        friend class Architect;

    // INTERFACE
    public:
        // constructor
        static Maze Generate(size_t width, size_t height, Architect & architect);

        // a "named constructor" to load a Maze from an istream
        static Maze Load(std::istream & source);

        // copy constructor (exists only to prevent copying)
        Maze(const Maze & source);

        // assignment operator (exists only to prevent assignment)
        Maze & operator = (const Maze & source);

        // destructor
        ~Maze();

        // store a Maze to a stream
        void Persist(std::ostream & receiver);

        // dimension properties
        size_t GetWidth() const  { return m_width; }
        size_t GetHeight() const { return m_height; }

        // locations of "special" cells
        Position EntranceCell() const { return m_entrance; }
        Position ExitCell() const     { return m_exit; }

        // cell and wall properties
        Cell GetCellAt(size_t col, size_t row) const;

    // UTILITIES
    protected:
        // constructor without an architect (for use by Load)
        Maze(size_t width, size_t height);

        // allocates memory and sets intial values for a Maze
        void Construct();

        // utility method to delete all data buffers
        void ClearAll();

        // performs a deep copy of one Maze to another
        void DeepCopy(const Maze & source);

        // read a maze's data from a stream
        void Read(std::istream & source);

    // ELEMENTS
    protected:
        // data elements
        size_t m_width;         // width of the maze in cells
        size_t m_height;        // height of the maze in cells

        Position m_entrance;    // position of the entrance cell
        Position m_exit;        // position of the exit cell

        Cell ** m_cells;        // the cell data
    };

} // end namespace Coyote


#endif

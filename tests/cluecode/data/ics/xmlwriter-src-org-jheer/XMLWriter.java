/**
 * Copyright (c) 2004-2006 Regents of the University of California.
  All rights reserved.

  modification, are permitted provided that the following conditions
  are met:

  1. Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

  2. Redistributions in binary form must reproduce the above copyright
  notice and this list of conditions.

            {
                // character out of range, escape with character value
                m_out.write("&#");
                m_out.write(Integer.toString(c));
                m_out.write(';');
            } else {
                }
                // if character is valid, don't escape
                if (valid) {
                    m_out.write(c);
                }
            }
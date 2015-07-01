/* Copyright (C) 2003 Vladimir Roubtsov. All rights reserved.
 * 
 * This program and the accompanying materials are made available under

// ----------------------------------------------------------------------------
/**
 * @author (C) 2001, Vladimir Roubtsov
 */
final class ConstantCollection implements IConstantCollection
            _clone.m_constants = new ArrayList (constants_count);
            for (int c = 0; c < constants_count; ++ c)
            {
                final CONSTANT_info constant = (CONSTANT_info) m_constants.get (c);
                _clone.m_constants.add (constant == null ? null : constant.clone ());
            }
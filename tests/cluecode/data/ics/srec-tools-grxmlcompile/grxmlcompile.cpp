/*---------------------------------------------------------------------------*
 *  grxmlcompile.cpp  *
 *                                                                           *
 *  Copyright 2007, 2008 Nuance Communciations, Inc.                               *
 *                                                                           *
 *  Licensed under the Apache License, Version 2.0 (the 'License');          *

#define TINYXML_ACKNOWLEDGEMENT	\
	"This tool uses the tinyxml library. \n" \
"Copyright (c) 2007 Project Admins: leethomason \n" \
"The TinyXML software is provided 'as-is', without any express or implied\n" \
"warranty. In no event will the authors be held liable for any damages\n" \
"including commercial applications, and to alter it and redistribute it\n" \
"freely, subject to the following restrictions:\n" 

#define NUANCE_COPYRIGHT \
"// grxmlcompile\n" \
"//\n" \
#if defined(GRXMLCOMPILE_PRINT_ACKNOWLEDGEMENT)
    cout << OPENFST_ACKNOWLEDGEMENT <<std::endl;
    cout << TINYXML_ACKNOWLEDGEMENT <<std::endl;
    cout << NUANCE_COPYRIGHT <<std::endl;
#endif

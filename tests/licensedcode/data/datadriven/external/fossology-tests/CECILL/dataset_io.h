/*************************************************************************
 * MediPy - Copyright (C) Universite de Strasbourg
 * Distributed under the terms of the CeCILL-B license, as published by
 * the CEA-CNRS-INRIA. Refer to the LICENSE file or to
 * http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
 * for details.
 ************************************************************************/

#ifndef _caf64ad4_c17c_4be4_8d6d_035e31ac3b10
#define _caf64ad4_c17c_4be4_8d6d_035e31ac3b10

#include <Python.h>
#include <string>

PyObject* read(std::string const & filename);
void write(PyObject* dataset, std::string const & filename);

#endif // _caf64ad4_c17c_4be4_8d6d_035e31ac3b10

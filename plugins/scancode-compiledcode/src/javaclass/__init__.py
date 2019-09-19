#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import unicode_literals

from StringIO import StringIO

from collections import OrderedDict
from functools import partial
from itertools import chain
from struct import unpack
import os
import sys

import attr

from commoncode import fileutils
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import SCAN_GROUP
from typecode import contenttype

from sourcecode import kernel

from javaclass import javaclass
from javaclass.javaclass import *


@scan_impl
class JavaClassScanner(ScanPlugin):
    """
    Scan java class information from the resource.
    """
    resource_attributes = OrderedDict(
        javaclass=attr.ib(default=attr.Factory(OrderedDict), repr=False),
    )

    options = [
        CommandLineOption(('--javaclass',),
            is_flag=True, default=False,
            help='Collect java class metadata',
            help_group=SCAN_GROUP,
            sort_order=100),
    ]

    def is_enabled(self, javaclass, **kwargs):
        return javaclass

    def get_scanner(self, **kwargs):
        return scan_javaclass


def scan_javaclass(location, **kwargs):
    """
    Return a mapping content  of a class fie
    """
    T = contenttype.get_type(location)
    if not T.is_java_class:
        return

    javaclass_data = OrderedDict()
    SHOW_CONSTS = 1
    data = open(location, 'rb').read()
    f = StringIO(data)
    c = javaclass.Class(f)
    
    javaclass_data['Version'] = 'Version: %i.%i (%s)' % ( c.version[1], c.version[0], getJavacVersion(c.version))

    if SHOW_CONSTS:
        javaclass_data['Constants Pool'] = str(len(c.constants))
        constants = OrderedDict()
        for i in range(1, len(c.constants)):
            const = c.constants[i]

            # part of #711
            # this may happen because of "self.constants.append(None)" in Class.__init__:
            # double and long constants take 2 slots, we must skip the 'None' one
            if not const: continue

            constant_data = OrderedDict()
            if const[0] == CONSTANT_Fieldref:
                constant_data['Field'] = str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_Methodref:
                constant_data['Method'] = str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_InterfaceMethodref:
                constant_data['InterfaceMethod'] = str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_String:
                constant_data['String'] =  str(const[1])

            elif const[0] == CONSTANT_Float:
                constant_data['Float'] =  str(const[1])

            elif const[0] == CONSTANT_Integer:
                constant_data['Integer'] =  str(const[1])

            elif const[0] == CONSTANT_Double:
                constant_data['Double'] =  str(const[1])

            elif const[0] == CONSTANT_Long:
                constant_data['Long'] =  str(const[1])

            # elif const[0] == CONSTANT_NameAndType:
            #   print 'NameAndType\t\t FIXME!!!'

            elif const[0] == CONSTANT_Utf8:
                constant_data['Utf8'] =  str(const[1])

            elif const[0] == CONSTANT_Class:
                constant_data['Class'] =  str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_NameAndType:
                constant_data['NameAndType'] =  str(const[1]) + ', ' + str(const[2])
            else:
                constant_data['Unknown(' + str(const[0]) + ')'] = str(const[1])
            
            constants[i] = constant_data
        
        javaclass_data['Constants'] = constants


    access =[]
    if c.access & ACC_INTERFACE:
        access.append('Interface ')
    if c.access & ACC_SUPER_OR_SYNCHRONIZED:
        access.append('Superclass ')
    if c.access & ACC_FINAL:
        access.append('Final ')
    if c.access & ACC_PUBLIC:
        access.append('Public ')
    if c.access & ACC_ABSTRACT:
        access.append('Abstract ')
    if access:
        javaclass_data['Access'] = ', '.join(access)

    methods = []
    for meth in c.methods:
        methods.append(str(meth))
    if methods:
        javaclass_data['Methods'] = methods

    javaclass_data['Class'] = c.name

    javaclass_data['Super Class'] = c.superClass

    interfaces = []
    for inter in c.interfaces:
        interfaces.append(str(inter))
    if interfaces:
        javaclass_data['Interfaces'] = interfaces
        
    return OrderedDict(
        javaclass=javaclass_data,
    )


from __future__ import absolute_import

import sys
import os
from struct import unpack
from StringIO import StringIO


"""
A python lib for parsing Java class files, suitable for static
analysis of Java programs.

Can also be run as a standalone program to print out information
about a class.

(C)opyright 2006 Jason Petrone <jp_py@demonseed.net>
All Rights Reserved

"""

__author__ = 'Jason Petrone <jp_py@demonseed.net>'
__version__ = '1.0'

# Class file format documented at:
# http://java.sun.com/docs/books/vmspec/html/ClassFile.doc.html

CONSTANT_Class = 7
CONSTANT_Fieldref = 9
CONSTANT_Methodref = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_String = 8
CONSTANT_Integer = 3
CONSTANT_Float = 4
CONSTANT_Long = 5
CONSTANT_Double = 6
CONSTANT_NameAndType = 12
CONSTANT_Utf8 = 1

ACC_DEFAULT = 0x0000
ACC_PUBLIC = 0x0001
ACC_PRIVATE = 0x0002
ACC_PROTECTED = 0x0004
ACC_STATIC = 0x0008
ACC_FINAL = 0x0010
ACC_SUPER_OR_SYNCHRONIZED = 0x0020
ACC_VOLATILE = 0x0040
ACC_NATIVE = 0x0100
ACC_INTERFACE = 0x0200
ACC_ABSTRACT = 0x0400
ACC_STRICT = 0x0800

ACCESS_MASK = ACC_PUBLIC | ACC_PRIVATE | ACC_PROTECTED


def getJavacVersion(versionNum):
    """
    Convert a Java class file tuple (minor, major) to a string
    representing the corresponding javac version.  E.g.  48.0 -> 1.4
    """
    if type(versionNum) in [tuple, list]:
        versionNum = '%i.%i' % (versionNum[1], versionNum[0])

    # todo: add support for Java 6 and 7 formats
    versions = {
        '51.0': '1.7',
        '50.0': '1.6',
        '49.0': '1.5',
        '48.0': '1.4',
        '47.0': '1.3',
        '46.0': '1.2',
        '45.3': '1.1',
    }
    try:
        return versions[versionNum]
    except KeyError:
        return '%s?' % (versionNum)


def _canonicalize(name, package=''):
    """
    If name is in package, will strip package component.
    """
    name = name.replace('/', '.')
    if name.startswith('java.lang.'):
        return name[len('java.lang.'):]
    i = name.rfind('.')
    if i != -1 and package + '.' == name[:i + 1]:
        return name[i + 1:]
    else:
        return name


def fmtAccessFlags(flags, isClass=0):
    """
    Convert an access flags constant to a list of human readable
    properties.
    """
    l = []
    if flags & ACC_PUBLIC:
        l.append('public')
    if flags & ACC_PRIVATE:
        l.append('private')
    if flags & ACC_PROTECTED:
        l.append('protected')
    if flags & ACC_FINAL:
        l.append('final')
    if flags & ACC_NATIVE:
        l.append('native')
    if flags & ACC_STATIC:
        l.append('static')
    if flags & ACC_SUPER_OR_SYNCHRONIZED:
        if not isClass:
            l.append('synchronized')
        # l.append('super') # what is this?
        pass

    # added as part of #711
    if flags & ACC_STRICT:
        l.append('strictfp')
    if flags & ACC_INTERFACE:
        l.append('interface')
    if flags & ACC_ABSTRACT:
        l.append('abstract')
    return ' '.join(l)


def getAccessFromFlags(flags):
    """
    Variant of fmtAccessFlags that returns only one
    of (public, private, protected) and not the other flags (final, native,
    static)
    """
    if flags & ACC_PUBLIC:
        return 'public'
    if flags & ACC_PRIVATE:
        return 'private'
    if flags & ACC_PROTECTED:
        return 'protected'
    return 'default'


class MethodDesc:
    def __init__(self, descStr):
        self.args = []
        self.descStr = descStr
        desc = list(descStr)
        self.args = _parseArgs(desc)
        self.returnType = ''.join(desc)


def _parseArgs(desc, count=-1):
    args = []
    while len(desc) and len(args) != count:
        c = desc.pop(0)
        if c == ')':
            break

        elif c == '(':
            pass

        elif c in ['B', 'C', 'D', 'F', 'I', 'J', 'S', 'Z']:
            args.append(c)

        elif c == 'L':
            s = c
            while c != ';':
                c = desc.pop(0)
                s += c
            args.append(s)

        elif c == '[':
            dim = 1
            while desc[0] == '[':
                dim += 1
                desc.pop(0)
            s = _parseArgs(desc, 1)[0]
            # desc = desc[len(s):]
            args.append(('[' * dim) + s)

    return args


def _fmtType(desc, pkg=''):
    """
    Convert a Java type code into a human readable string.
    """
    types = {'B':'byte', 'C':'char', 'D':'double', 'F':'float', 'I':'int',
             'J':'long', 'S':'short', 'Z':'boolean', 'V':'void'}

    dim = 0
    for i in range(len(desc)):
        if desc[i] == '[':
            dim += 1
        else:
            break

    array = dim * '[]'
    desc = desc[dim:]

    try:
        return '%s%s' % (types[desc], array)
    except KeyError:
        # class
        pass

    if desc.startswith('L'):
        name = desc[1:]
        name = name[:-1]  # strip ;
        name = _canonicalize(name, pkg)
        return '%s%s' % (name, array)
    else:
        raise Exception('UNKNOWN TYPE: ' + desc)


class Method:
    """
    Represents a Java method.
    The bytecode for the method is stored under the key "Code" in attrs.
    """
    def __init__(self, klass, access, name, desc, attrs):
        self.klass = klass
        self.access = access
        self.obj = None
        self.name = name
        self.desc = desc
        self.attrs = attrs
        d = MethodDesc(desc)
        self.args = d.args
        self.returnType = d.returnType

        if self.name == '<init>':
            # constructor
            name = _canonicalize(self.klass.name, self.klass.package)

        args = ', '.join([_fmtType(x, self.klass.package) for x in self.args])
        self.methsig = ('%s %s %s(%s)' %
             (fmtAccessFlags(self.access), _fmtType(self.returnType,
               self.klass.package), name, args))
        # default access results in leading space
        self.methsig = self.methsig.strip()

    def __hash__(self):
        return hash(self.methsig)

    def __eq__(self, obj):
        return self.methsig == obj.methsig

    # def __eq__(self, obj):
    #   return self.klass.name == obj.klass.name \
    #           and self.name == obj.name \
    #           and self.args == obj.args

    def __repr__(self):
        return self.methsig


class Field:

    def __init__(self, klass, access, name, desc, attrs):
        # print 'FIELD ' + str([klass, access, name, desc, attrs])
        self.klass = klass
        self.access = access
        self.name = name
        self.desc = desc
        self.attrs = attrs
        if attrs.has_key('ConstantValue'):
            self.value = attrs['ConstantValue']
        else:
            self.value = None
        self.fieldsig = ('%s %s %s' %
              (fmtAccessFlags(access), _fmtType(desc),
               _canonicalize(self.name, self.klass.package)))
        # default access results in leading space
        self.fieldsig = self.fieldsig.strip()

    def __eq__(self, obj):
        for x in dir(self):
            if x.startswith('__') or x == 'klass':
                continue
            if self.__dict__[x] != obj.__dict__[x]:
                return 0
        return 1

    def __str__(self):
        return self.fieldsig


class FieldRef:
    def __init__(self, klass, name, desc):
        self.klass = klass
        self.name = name
        self.desc = desc


class MethodRef:
    def __init__(self, _class, name, desc):
        self._class = _class
        self.name = name
        self.desc = desc
        self.args = _parseArgs(desc)

    def __repr__(self):
        return self.desc + ' ' + self._class + '.' + self.name


class Class:
    def __init__(self, f):
        """
        Load a java class from file object "f"
        """
        print(f.read(4))  # magic
        self.version = unpack('>HH', f.read(4))

        # print unpack('>H', f.read(2))

        [constCount] = unpack('>H', f.read(2))
        self.constants = [[CONSTANT_Utf8, 'reserved']]
        i = 1

        while i < constCount:
            [tag] = unpack('b', f.read(1))

            if tag == CONSTANT_Class:
                self.constants.append([tag, unpack('>H', f.read(2))[0]])

            elif (tag == CONSTANT_Fieldref or
                 tag == CONSTANT_Methodref or
                 tag == CONSTANT_InterfaceMethodref):

                self.constants.append([tag] + list(unpack('>HH', f.read(4))))

            elif tag == CONSTANT_String:
                self.constants.append([tag] + list(unpack('>H', f.read(2))))

            elif tag == CONSTANT_Float:
                self.constants.append([tag] + list(unpack('>f', f.read(4))))

            elif tag == CONSTANT_Integer:
                self.constants.append([tag] + list(unpack('>i', f.read(4))))

            elif tag == CONSTANT_Double:
                [val] = unpack('>d', f.read(8))
                self.constants.append([tag] + [val])
                # takes up 2 constant pool spots
                self.constants.append(None)  # this needs to be considered in dumpClass!
                i += 1
            elif tag == CONSTANT_Long:
                [hi] = unpack('>l', f.read(4))
                [lo] = unpack('>l', f.read(4))
                self.constants.append([tag, ((long(hi) << 4) + lo)])
                # takes up 2 constant pool spots
                self.constants.append(None)  # this needs to be considered in dumpClass!
                i += 1
            elif tag == CONSTANT_NameAndType:
                self.constants.append([tag] + list(unpack('>HH', f.read(4))))
            elif tag == CONSTANT_Utf8:
                [length] = unpack('>H', f.read(2))
                s = f.read(length)
                self.constants.append([tag, s])
            else:
                raise Exception('UNKNOWN CONST TAG! ' + str(tag) + ' at ' + hex(f.tell()))
            i += 1

        [self.access] = unpack('>H', f.read(2))
        [className] = unpack('>H', f.read(2))
        self.name = self.constants[self.constants[className][1]][1]
        self.package = os.path.dirname(self.name).replace('/', '.')
        # print self.version
        [className] = unpack('>H', f.read(2))


        # added as part of #711: java.lang.Object is an exceptional case
        if self.name != 'java/lang/Object':
            self.superClass = self.constants[self.constants[className][1]][1]
        else:
            self.superClass = ''

        # interfaces
        [count] = unpack('>H', f.read(2))
        self.interfaces = []
        for i in range(count):
            [index] = unpack('>H', f.read(2))
            index = self.constants[index][1]
            iname = self.constants[index][1]
            iname = _canonicalize(iname, self.package)
            self.interfaces.append(iname)

        # build class signature
        access = fmtAccessFlags(self.access, isClass=1)
        name = self.name.replace('/', '.')
        name = _canonicalize(name, self.package)
        self.classSig = '%s class %s' % (access, name)
        if self.superClass != 'java/lang/Object':
            s = _canonicalize(self.superClass, self.package)
            self.classSig += ' extends %s' % (s)
        self.classSig = self.classSig.strip()
        if self.interfaces:
            self.classSig += ' implements ' + ', '.join(self.interfaces)

        # fields
        [count] = unpack('>H', f.read(2))
        self.fields = []
        for i in range(count):
            [access, name, desc, acount] = unpack('>HHHH', f.read(8))
            attrs = {}
            for _ in range(acount):
                [aname, alen] = unpack('>HI', f.read(6))
                aname = self.constants[aname][1]
                attrs[aname] = f.read(alen)
            name = self.constants[name][1]
            desc = self.constants[desc][1]
            self.fields.append(Field(self, access, name, desc, attrs))

        # methods
        methods = []
        [count] = unpack('>H', f.read(2))
        for i in range(count):
            [access, name, desc, acount] = unpack('>HHHH', f.read(8))
            attrs = {}
            for _ in range(acount):
                [aname, alen] = unpack('>HI', f.read(6))
                aname = self.constants[aname][1]
                attrs[aname] = f.read(alen)
            name = self.constants[name][1]
            desc = self.constants[desc][1]
            methods.append(Method(self, access, name, desc, attrs))

        # attributes
        [count] = unpack('>H', f.read(2))
        attrs = {}
        for _ in range(count):
            [aname, alen] = unpack('>HI', f.read(6))
            attrs[self.getConst(aname)] = f.read(alen)
        self.attrs = attrs
        self.methods = methods

    def isPublic(self):
        return self.access & ACC_PUBLIC

    def isPrivate(self):
        return self.access & ACC_PRIVATE

    def isProtected(self):
        return self.access & ACC_PROTECTED

    def getConst(self, index):
        c = self.constants[index]
        if c[0] == CONSTANT_String:
            data = self.constants[c[1]][1]
            return data

        elif c[0] in [CONSTANT_Methodref, CONSTANT_InterfaceMethodref]:
            classi = self.constants[c[1]][1]
            _class = self.constants[classi][1]
            namei = self.constants[c[2]][1]
            name = self.constants[namei][1]
            typei = self.constants[c[2]][2]
            typ = self.constants[typei][1]
            return MethodRef(_class, name, typ)

        elif c[0] == CONSTANT_Class:
            return self.constants[c[1]][1]

        elif c[0] == CONSTANT_Fieldref:
            [var, typ] = self.getConst(c[2])
            return FieldRef(self.getConst(c[1]), var, type)

        elif c[0] == CONSTANT_NameAndType:
            return [self.getConst(c[1]), self.getConst(c[2])]

        elif c[0] == CONSTANT_Utf8:
            return c[1]

        elif c[0] == CONSTANT_Double:
            return c[1]

        elif c[0] == CONSTANT_Float:
            return c[1]

        else:
            raise Exception('UNHANDLED CONST: ' + str([c[0], c[1]]))

    def __str__(self):
        return self.classSig


def dumpClass(path):
    """
    Print out information about a class.
    """
    SHOW_CONSTS = 1
    data = open(path, 'rb').read()
    f = StringIO(data)
    c = Class(f)
    # print file name
    print 'Version: %i.%i (%s)' \
       % (c.version[1], c.version[0], getJavacVersion(c.version))

    if SHOW_CONSTS:
        print 'Constants Pool: ' + str(len(c.constants))
        for i in range(1, len(c.constants)):
            const = c.constants[i]

            # part of #711
            # this may happen because of "self.constants.append(None)" in Class.__init__:
            # double and long constants take 2 slots, we must skip the 'None' one
            if not const: continue


            sys.stdout.write('  ' + str(i) + '\t')
            if const[0] == CONSTANT_Fieldref:
                print 'Field\t\t' + str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_Methodref:
                print 'Method\t\t' + str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_InterfaceMethodref:
                print 'InterfaceMethod\t\t' + str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_String:
                print 'String\t\t' + str(const[1])
            elif const[0] == CONSTANT_Float:
                print 'Float\t\t' + str(const[1])

            elif const[0] == CONSTANT_Integer:
                print 'Integer\t\t' + str(const[1])

            elif const[0] == CONSTANT_Double:
                print 'Double\t\t' + str(const[1])

            elif const[0] == CONSTANT_Long:
                print 'Long\t\t' + str(const[1])

            # elif const[0] == CONSTANT_NameAndType:
            #   print 'NameAndType\t\t FIXME!!!'

            elif const[0] == CONSTANT_Utf8:
                print 'Utf8\t\t' + str(const[1])

            elif const[0] == CONSTANT_Class:
                print 'Class\t\t' + str(c.constants[const[1]][1])

            elif const[0] == CONSTANT_NameAndType:
                print 'NameAndType\t\t' + str(const[1]) + '\t\t' + str(const[2])

            else:
                print 'Unknown(' + str(const[0]) + ')\t\t' + str(const[1])


    print 'Attributes: '

    sys.stdout.write('Interfaces: ')

    sys.stdout.write('Access: ' + hex(c.access))
    sys.stdout.write(' [ ')
    if c.access & ACC_INTERFACE:
        sys.stdout.write('Interface ')
    if c.access & ACC_SUPER_OR_SYNCHRONIZED:
        sys.stdout.write('Superclass ')
    if c.access & ACC_FINAL:
        sys.stdout.write('Final ')
    if c.access & ACC_PUBLIC:
        sys.stdout.write('Public ')
    if c.access & ACC_ABSTRACT:
        sys.stdout.write('Abstract ')
    print ']'

    print 'Methods: '
    for meth in c.methods:
        print '    ' + str(meth)

    print 'Class: ' + c.name

    print 'Super Class: ' + c.superClass

    print 'Interfaces: ',
    for inter in c.interfaces:
        print inter + ", ",



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage %s: <a.class> [b.class] ...' % (sys.argv[0])
        sys.exit(-1)

    for x in sys.argv[1:]:
        dumpClass(x)

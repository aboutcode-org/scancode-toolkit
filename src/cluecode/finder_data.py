#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

from functools import partial


def set_from_text(text):
    return set(u.lower().strip('/') for u in text.split())


JUNK_EMAILS = set_from_text(u'''
    test@test.com
''')


JUNK_HOSTS_AND_DOMAINS = set_from_text(u'''
    exmaple.com
    example.com
    example.net
    example.org
    test.com
    2x.png
    schemas.android.com
    1.2.3.4
    yimg.com
    a.b.c
    maps.google.com
    hostname
''')


JUNK_IPS = set_from_text(u'''
    1.2.3.4
''')


JUNK_URLS = set_from_text(u'''
    http://www.adobe.com/2006/mxml
    http://www.w3.org/1999/XSL/Transform
    http://docs.oasis-open.org/ns/xri/xrd-1.0
    http://www.w3.org/2001/XMLSchema-instance
    http://java.sun.com/xml/ns/persistence/persistence_1_0.xsd
    http://bing.com
    http://google.com
    http://msn.com
    http://maven.apache.org/maven-v4_0_0.xsd
    http://maven.apache.org/POM/4.0.0
    http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd
    http://www.w3.org/1999/02/22-rdf-syntax-ns
    http://www.w3.org/1999/xhtml
    http://www.w3.org/1999/XMLSchema
    http://www.w3.org/1999/XMLSchema-instance
    http://www.w3.org/2000/svg
    http://www.w3.org/2001/XMLSchema
    http://www.w3.org/2000/10/XMLSchema
    http://www.w3.org/2000/10/XMLSchema-instance
    http://www.w3.org/2001/XMLSchema
    http://www.w3.org/2001/XMLSchema-instance
    http://www.w3.org/2002/12/soap-encoding
    http://www.w3.org/2002/12/soap-envelope
    http://www.w3.org/2005/Atom
    http://www.w3.org/2006/01/wsdl
    http://www.w3.org/2006/01/wsdl/http
    http://www.w3.org/2006/01/wsdl/soap
    http://www.w3.org/2006/vcard/ns
    http://www.w3.org/International/O-URL-and-ident.html
    http://www.w3.org/MarkUp
    http://www.w3.org/WAI/GL
    http://xml.apache.org/axis/session
    http://xml.apache.org/xml-soap
    http://docs.oasis-open.org/ns/xri/xrd-1.0
    http://cobertura.sourceforge.net/xml/coverage-01.dtd
    http://findbugs.googlecode.com/svn/trunk/findbugs/etc/docbook/docbookx.dtd
    http://hibernate.sourceforge.net/hibernate-configuration-2.0.dtd
    http://hibernate.sourceforge.net/hibernate-generic.dtd
    http://hibernate.sourceforge.net/hibernate-mapping-2.0.dtd
    http://www.opensymphony.com/xwork/xwork-1.0.dtd
    http://]hostname
    http://+
    http://www
    http://www.w3.org/1999/xhtml
    http://www.w3.org/1999/XSL/Transform
    http://www.w3.org/2001/XMLSchema
    http://www.w3.org/2001/XMLSchema-instance
    http://www.w3.org/hypertext/WWW/Protocols/HTTP/HTRESP.html
    http://www.w3.org/hypertext/WWW/Protocols/HTTP/Object_Headers.html
    http://www.w3.org/P3P
    http://www.w3.org/pub/WWW
    http://www.w3.org/TR/html4/strict.dtd
    http://www.w3.org/TR/REC-html40/loose.dtd
    http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd
    http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd
    http://www.w3.org/TR/xslt
    https:
    https://+
    http://www.example.com
    http://www.example.com/dir/file
    http://www.example.com:dir/file
    http://www.your.org.here
    http://hostname
    https://www.trustedcomputinggroup.org/XML/SCHEMA/TNCCS_1.0.xsd
    http://glade.gnome.org/glade-2.0.dtd
    http://pagesperso-orange.fr/sebastien.godard/sysstat.dtd
    http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd
    http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd
    http://gcc.gnu.org/bugs.html
''')


JUNK_URL_PREFIXES = tuple(set_from_text('''
    http://www.springframework.org/dtd/
    http://www.slickedit.com/dtd/
    http://www.oexchange.org/spec/0.8/
    http://www.puppycrawl.com/dtds/
    http://adobe.com/AS3/2006/builtin
    http://careers.msn.com
    http://foo.bar.baz
    http://foo.bar.com
    http://foobar.com
    http://java.sun.com/xml/ns/
    http://java.sun.com/j2se/1.4/docs/
    http://java.sun.com/j2se/1.5.0/docs/
    http://developer.apple.com/certificationauthority/
    http://www.apple.com/appleca/
    https://www.apple.com/certificateauthority/
    http://schemas.microsoft.com/
    http://dublincore.org/schemas/
    http://www.w3.org/TR/
    http://www.apple.com/DTDs
    http://apache.org/xml/features/
    http://apache.org/xml/properties/
    http://crl.verisign.com/
    http://crl.globalsign.net/
    http://crl.microsoft.com/
    http://crl.thawte.com/
    http://CSC3-2004-crl.verisign.com
    http://csc3-2009-2-crl.verisign.com
    http://dellincca.dell.com/crl
    http://ts-crl.ws.symantec.com
    http://java.sun.com/dtd/
    http://java.sun.com/j2ee/dtds/
    http://jakarta.apache.org/commons/dtds/
    http://jakarta.apache.org/struts/dtds/
    http://www.jboss.org/j2ee/dtd/
    http://glassfish.org/dtds/
    http://docbook.org/xml/simple/
    http://www.oasis-open.org/docbook/xml/
'''))


JUNK_URL_SUFFIXES = tuple(set_from_text('''
   .png
   .jpg
   .gif
'''))


def classify(s, data_set):
    """
    Return True or some classification string value that evaluates to True if
    the data in string s is not junk. Return False if the data in string s is
    classified as 'junk' or uninteresting.
    """
    if not s:
        return False
    s = s.lower().strip('/')
    if s in data_set:
        return False
    return True


classify_ip = partial(classify, data_set=JUNK_IPS)

classify_host = partial(classify, data_set=JUNK_HOSTS_AND_DOMAINS)

classify_email = partial(classify, data_set=JUNK_EMAILS)


def classify_url(url):
    if not url:
        return False
    u = url.lower().strip('/')
    if (u in JUNK_URLS or
        u.startswith(JUNK_URL_PREFIXES)
        or u.endswith(JUNK_URL_SUFFIXES)):
        return False
    return True

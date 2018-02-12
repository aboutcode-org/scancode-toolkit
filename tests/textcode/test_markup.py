# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from commoncode.testcase import FileBasedTesting
from commoncode.testcase import file_cmp
from commoncode import fileutils
from commoncode import text

from textcode import markup


class TestMarkup(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def atest_gen(self):
        """
        Rename to test xxx to regen tests.
        """
        test_dir = self.get_test_loc(u'markup', True)
        expected_dir = self.get_test_loc(u'markup_expected')
        template = u"""
    def test_%(tn)s(self):
        test_file = self.get_test_loc(u'markup/%(test_file)s')
        expected = self.get_test_loc(u'markup_expected/%(test_file)s')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)"""

        for test_file in os.listdir(test_dir):
            tn = text.python_safe_name(test_file)
            location = os.path.join(test_dir, test_file)
            result = markup.convert_to_text(location)
            expected_file = os.path.join(expected_dir, test_file)
            fileutils.copyfile(result, expected_file)
            print(template % locals())

    def test_404_htm(self):
        test_file = self.get_test_loc(u'markup/404.htm')
        expected = self.get_test_loc(u'markup_expected/404.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_a_htm(self):
        test_file = self.get_test_loc(u'markup/a.htm')
        expected = self.get_test_loc(u'markup_expected/a.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_allclasses_frame_html(self):
        test_file = self.get_test_loc(u'markup/allclasses-frame.html')
        expected = self.get_test_loc(u'markup_expected/allclasses-frame.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_chinese_htm(self):
        test_file = self.get_test_loc(u'markup/chinese.htm')
        expected = self.get_test_loc(u'markup_expected/chinese.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_contenttype_html(self):
        test_file = self.get_test_loc(u'markup/contenttype.html')
        expected = self.get_test_loc(u'markup_expected/contenttype.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_double_pygment_in_html_html(self):
        # FIXME: the output is still markup. we need a second pass
        test_file = self.get_test_loc(u'markup/double_pygment_in_html.html')
        expected = self.get_test_loc(u'markup_expected/double_pygment_in_html.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_json_phps(self):
        test_file = self.get_test_loc(u'markup/JSON.phps')
        expected = self.get_test_loc(u'markup_expected/JSON.phps')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_json_phps_html(self):
        test_file = self.get_test_loc(u'markup/JSON.phps.html')
        expected = self.get_test_loc(u'markup_expected/JSON.phps.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_label_html(self):
        test_file = self.get_test_loc(u'markup/Label.html')
        expected = self.get_test_loc(u'markup_expected/Label.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_lgpl_license_html(self):
        test_file = self.get_test_loc(u'markup/lgpl_license.html')
        expected = self.get_test_loc(u'markup_expected/lgpl_license.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_pdl_html(self):
        test_file = self.get_test_loc(u'markup/PDL.html')
        expected = self.get_test_loc(u'markup_expected/PDL.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_jsp_is_markup(self):
        test_file = self.get_test_loc(u'markup/java.jsp')
        assert markup.is_markup(test_file)

    def test_jsp_demarkup(self):
        test_file = self.get_test_loc(u'markup/java.jsp')
        result = list(markup.demarkup(test_file))
        expected = [
            u' version="1.0" encoding="ISO-8859-1"?>\n',
            u' <%@page  session="false" contentType="text/html; charset=ISO-8859-1" %>\n',
            u' <%@page  import="clime.messadmin.model.IServerInfo" %>\n',
            u' <%@taglib  prefix="core" uri="messadmin-core" %>\n',
            u' <%@taglib  prefix="format" uri="messadmin-fmt" %>\n',
            u' HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"--%>\n',
            u' HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"--%>\n',
            u' html \n',
            u'     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n',
            u'     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n',
            u' html \n',
            u'     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n',
            u'     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"--%>\n',
            u' html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n',
            u' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"--%>\n',
            u'\n',
            u' xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n',
            u' IServerInfo serverInfos = (IServerInfo) request.getAttribute("serverInfos");\n',
            u'   String webFilesRoot = (String) request.getAttribute("WebFilesRoot"); %>\n',
            u' value="${pageContext.request.servletPath}" var="submitUrl" scope="page"/--%> can use value="${pageContext.request.servletPath}" because this JSP is include()\'ed --%>\n',
            u' or use directly ${pageContext.request.requestURI} --%>\n',
            u" String submitUrl = request.getContextPath() + request.getServletPath(); /* Can use +request.getServletPath() because this JSP is include()'ed */ %>\n",
            u' \n',
            u'     http-equiv="content-type" content="text/html; charset=iso-8859-1 "/> \n',
            u'\t http-equiv="pragma" content="no-cache "/>  HTTP 1.0 -->\n',
            u'\t http-equiv="cache-control" content="no-cache,must-revalidate "/>  HTTP 1.1 -->\n',
            u'\t http-equiv="expires" content="0 "/>  0 is an invalid value and should be treated as \'now\' -->\n',
            u'\t http-equiv="content-language" content="en "/>  fr-FR --%>\n',
            u'\t name="author" content="Cedrik LIME "/> \n',
            u'\t name="copyright" content="copyright 2005-2006 Cedrik LIME "/> \n',
            u'\t name="robots" content="noindex,nofollow,noarchive "/> \n',
            u'\t Server System Informations \n',
            u'\t rel="stylesheet" type="text/css"  =" MessAdmin.css "/> \n',
            u'\t type="text/css">\n',
            u'\t \n',
            u'\t type="text/javascript" src=" js/getElementsBySelector.js"> \n',
            u'\t type="text/javascript" src=" js/behavior.js"> \n',
            u'\t type="text/javascript" src=" js/MessAdmin.js"> \n',
            u'\t type="text/javascript">// ',
            u'\t\tfunction reloadPage() {\n',
            u'\t\t\twindow.location.reload();\n',
            u'\t\t}\n',
            u'\t//]]>\n',
            u'\t \n',
            u' \n',
            u' \n',
            u'\n',
            u' ',
            u' border="0" cellspacing="0" cellpadding="0" width="100%">\n',
            u' \n',
            u' align="right" class="topheading" width="44"> alt="Indus Logo" border="0" height="39" width="44" src=" /MessAdmin/images/logo.gif">  class="topheading">Indus Application Management Console \n',
            u' \n',
            u' \n',
            u' \n',
            u' \n',
            u' border="0" cellspacing="0" cellpadding="0">\n',
            u' \n',
            u' class="backtab"> class="tabs"  ="http://localhost:8083/serverbydomain?querynames=*ias50%3A*">Server view  \n',
            u' width="2">  class="backtab"> class="tabs"  ="http://localhost:8083/empty?template=emptymbean">MBean view   width="2"> \n',
            u' class="backtab"> class="tabs"  ="http://localhost:8083/mbean?objectname=JMImplementation%3Atype%3DMBeanServerDelegate&template=about">About  \n',
            u' width="2">  class="fronttab"> class="tabs"  ="http://localhost:8888/ias50/MessAdmin">Session Admin  \n',
            u' \n',
            u' \n',
            u'------------------------>\n',
            u'\n',
            u' <jsp:include  page="header.jsp "/> \n',
            u'\n',
            u' border="0" cellspacing="0" cellpadding="0" width="100%">\n',
            u' \n',
            u'   class="darker"> \n',
            u' \n',
            u' \n',
            u'   class="lighter">\n',
            u'   id="menu" style="font-size: small;">\n',
            u'  [\n',
            u'  Server Informations\n',
            u'  |\n',
            u'    =" ?action=webAppsList">Web Applications list \n',
            u'  ]\n',
            u'   \n',
            u'   \n',
            u' \n',
            u' \n',
            u' \n',
            u'\n',
            u' \n',
            u'\t <legend> Server Information </legend> \n',
            u' style="text-align: left;" border="0">\n',
            u'\t \n',
            u'\t\t Server name \n',
            u'\t\t title=\'Working directory:  serverInfos.getSystemProperties().get("user.dir") %>\'> getServletConfig().getServletContext().getServerInfo() %> \n',
            u'\t\t Servlet version \n',
            u'\t\t  getServletConfig().getServletContext().getMajorVersion() %>. getServletConfig().getServletContext().getMinorVersion() %> \n',
            u'\t \n',
            u'\t \n',
            u'\t\t Temp file directory \n',
            u'\t\t  value=\' serverInfos.getSystemProperties().get("java.io.tmpdir") %> \'/>  \n',
            u'\t\t Running as \n',
            u'\t\t title=\'Home directory:  serverInfos.getSystemProperties().get("user.home") %>\'> value=\' serverInfos.getSystemProperties().get("user.name") %> \'/>  \n',
            u'\t \n',
            u'\t \n',
            u'\t\t Startup date \n',
            u'\t\t  value=" serverInfos.getStartupTime() %>" type="both" pattern="yyyy-MM-dd HH:mm:ss "/>  \n',
            u'\t\t colspan="2"> \n',
            u'\t \n',
            u' \n',
            u' \n',
            u'\n',
            u' \n',
            u'\t <legend> CPU and Memory </legend> \n',
            u' style="text-align: left;" border="0">\n',
            u' test=" serverInfos.getCpuCount() >= 0 %>">\n',
            u'\t \n',
            u'\t\t title="maximum number of processors available to the Java virtual machine">Number of CPUs \n',
            u'\t\t align="center"> value=" serverInfos.getCpuCount() %>" type="number "/>  \n',
            u'\t \n',
            u' \n',
            u'\t \n',
            u'\t\t title="amount of free memory in the system">Free Memory \n',
            u'\t\t class="number"> value=" serverInfos.getFreeMemory() %>" type="bytes "/>  \n',
            u'\t \n',
            u'\t \n',
            u'\t\t title="total amount of memory in the Java Virtual Machine">Total Memory \n',
            u'\t\t class="number"> value=" serverInfos.getTotalMemory() %>" type="bytes "/>  \n',
            u'\t \n',
            u' test=" serverInfos.getMaxMemory() >= 0 %>">\n',
            u'\t \n',
            u'\t\t title="maximum amount of memory that the Java virtual machine will attempt to use">Max Memory \n',
            u'\t\t class="number"> value=" serverInfos.getMaxMemory() %>" type="bytes "/>  \n',
            u'\t \n',
            u' \n',
            u' \n',
            u' \n',
            u'\n',
            u' \n',
            u'\t <legend> VM Info </legend> \n',
            u' extracted properties from System.getProperties() (see JavaDoc) -->\n',
            u' style="text-align: left;" border="0">\n',
            u'\t VM Info \n',
            u'\t \n',
            u'\t\t Java VM \n',
            u'\t\t \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.vendor") %> \'/> \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.name") %> \'/> \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.version") %> \'/> \n',
            u'\t\t \n',
            u'\t \n',
            u'\t \n',
            u'\t\t Java RE \n',
            u'\t\t \n',
            u'\t\t\t  =" serverInfos.getSystemProperties().get("java.vendor.url") %>"> value=\' serverInfos.getSystemProperties().get("java.vendor") %> \'/>  \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.version") %> \'/>  @  value=\' serverInfos.getSystemProperties().get("java.home") %> \'/> \n',
            u'\t\t \n',
            u'\t \n',
            u'\t \n',
            u'\t\t Platform \n',
            u'\t\t \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("os.name") %> \'/> / value=\' serverInfos.getSystemProperties().get("os.arch") %> \'/> \n',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("os.version") %> \'/> \n',
            u'\t\t \n',
            u'\t \n',
            u' \n',
            u' \n',
            u'\n',
            u' style="text-align: center;"> type="button" onclick="window.location.reload()">Refresh  \n',
            u'\n',
            u' class="error"> value=\' request.getAttribute("error") %> \'/>  \n',
            u' class="message"> value=\' request.getAttribute("message") %> \'/>  \n',
            u'\n',
            u' id="extraServerAttributes">\n',
            u' items=" serverInfos.getServerSpecificData() %>" var="serverSpecificData" varStatus="status">\n',
            u' java.util.Map.Entry serverSpecificData = (java.util.Map.Entry) pageContext.getAttribute("serverSpecificData"); %>\n',
            u'\t \n',
            u'\t\t <legend  > serverSpecificData.getKey() %> </legend> \n',
            u'\t\t serverSpecificData.getValue() %>\n',
            u'\t \n',
            u' \n',
            u' \n',
            u'\n',
            u' <jsp:include  page="footer.jsp "/> \n',
            u'\n',
            u' \n',
            u' '

        ]
        assert expected == result

    def test_php_php(self):
        test_file = self.get_test_loc(u'markup/php.php')
        expected = self.get_test_loc(u'markup_expected/php.php')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_php_highlighted_in_html_html(self):
        # FIXME: the output is still markup. we need a second pass
        test_file = self.get_test_loc(u'markup/php_highlighted_in_html.html')
        expected = self.get_test_loc(u'markup_expected/php_highlighted_in_html.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_rst_highlighted_html(self):
        test_file = self.get_test_loc(u'markup/rst_highlighted.html')
        expected = self.get_test_loc(u'markup_expected/rst_highlighted.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_services_htm(self):
        test_file = self.get_test_loc(u'markup/services.htm')
        expected = self.get_test_loc(u'markup_expected/services.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_sissl_license_html(self):
        test_file = self.get_test_loc(u'markup/sissl_license.html')
        expected = self.get_test_loc(u'markup_expected/sissl_license.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_text_phps(self):
        test_file = self.get_test_loc(u'markup/text.phps')
        expected = self.get_test_loc(u'markup_expected/text.phps')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_us_htm(self):
        test_file = self.get_test_loc(u'markup/us.htm')
        expected = self.get_test_loc(u'markup_expected/us.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

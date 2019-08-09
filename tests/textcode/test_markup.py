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

from textcode import markup

import pytest
pytestmark = pytest.mark.scanpy3  # NOQA


class TestMarkup(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_jsp_is_markup(self):
        test_file = self.get_test_loc(u'markup/java.jsp')
        assert markup.is_markup(test_file)

    def test_jsp_demarkup(self):
        test_file = self.get_test_loc(u'markup/java.jsp')
        result = list(markup.demarkup(test_file))
        expected = [
            u' version="1.0" encoding="ISO-8859-1"?>',
            u' <%@page  session="false" contentType="text/html; charset=ISO-8859-1" %>',
            u' <%@page  import="clime.messadmin.model.IServerInfo" %>',
            u' <%@taglib  prefix="core" uri="messadmin-core" %>',
            u' <%@taglib  prefix="format" uri="messadmin-fmt" %>',
            u' HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"--%>',
            u' HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"--%>',
            u' html ',
            u'     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"',
            u'     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
            u' html ',
            u'     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"',
            u'     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"--%>',
            u' html PUBLIC "-//W3C//DTD XHTML 1.1//EN"',
            u' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"--%>',
            u'',
            u' xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">',
            u' IServerInfo serverInfos = (IServerInfo) request.getAttribute("serverInfos");',
            u'   String webFilesRoot = (String) request.getAttribute("WebFilesRoot"); %>',
            u' value="${pageContext.request.servletPath}" var="submitUrl" scope="page"/--%> can use value="${pageContext.request.servletPath}" because this JSP is include()\'ed --%>',
            u' or use directly ${pageContext.request.requestURI} --%>',
            u" String submitUrl = request.getContextPath() + request.getServletPath(); /* Can use +request.getServletPath() because this JSP is include()'ed */ %>",
            u' ',
            u'     http-equiv="content-type" content="text/html; charset=iso-8859-1 "/> ',
            u'\t http-equiv="pragma" content="no-cache "/>  HTTP 1.0 -->',
            u'\t http-equiv="cache-control" content="no-cache,must-revalidate "/>  HTTP 1.1 -->',
            u'\t http-equiv="expires" content="0 "/>  0 is an invalid value and should be treated as \'now\' -->',
            u'\t http-equiv="content-language" content="en "/>  fr-FR --%>',
            u'\t name="author" content="Cedrik LIME "/> ',
            u'\t name="copyright" content="copyright 2005-2006 Cedrik LIME "/> ',
            u'\t name="robots" content="noindex,nofollow,noarchive "/> ',
            u'\t Server System Informations ',
            u'\t rel="stylesheet" type="text/css"  =" MessAdmin.css "/> ',
            u'\t type="text/css">',
            u'\t ',
            u'\t type="text/javascript" src=" js/getElementsBySelector.js"> ',
            u'\t type="text/javascript" src=" js/behavior.js"> ',
            u'\t type="text/javascript" src=" js/MessAdmin.js"> ',
            u'\t type="text/javascript">// ',
            u'\t\tfunction reloadPage() {',
            u'\t\t\twindow.location.reload();',
            u'\t\t}',
            u'\t//]]>',
            u'\t ',
            u' ',
            u' ',
            u'',
            u' ',
            u' border="0" cellspacing="0" cellpadding="0" width="100%">',
            u' ',
            u' align="right" class="topheading" width="44"> alt="Indus Logo" border="0" height="39" width="44" src=" /MessAdmin/images/logo.gif">  class="topheading">Indus Application Management Console ',
            u' ',
            u' ',
            u' ',
            u' ',
            u' border="0" cellspacing="0" cellpadding="0">',
            u' ',
            u' class="backtab"> class="tabs"  ="http://localhost:8083/serverbydomain?querynames=*ias50%3A*">Server view  ',
            u' width="2">  class="backtab"> class="tabs"  ="http://localhost:8083/empty?template=emptymbean">MBean view   width="2"> ',
            u' class="backtab"> class="tabs"  ="http://localhost:8083/mbean?objectname=JMImplementation%3Atype%3DMBeanServerDelegate&template=about">About  ',
            u' width="2">  class="fronttab"> class="tabs"  ="http://localhost:8888/ias50/MessAdmin">Session Admin  ',
            u' ',
            u' ',
            u'------------------------>',
            u'',
            u' <jsp:include  page="header.jsp "/> ',
            u'',
            u' border="0" cellspacing="0" cellpadding="0" width="100%">',
            u' ',
            u'   class="darker"> ',
            u' ',
            u' ',
            u'   class="lighter">',
            u'   id="menu" style="font-size: small;">',
            u'  [',
            u'  Server Informations',
            u'  |',
            u'    =" ?action=webAppsList">Web Applications list ',
            u'  ]',
            u'   ',
            u'   ',
            u' ',
            u' ',
            u' ',
            u'',
            u' ',
            u'\t <legend> Server Information </legend> ',
            u' style="text-align: left;" border="0">',
            u'\t ',
            u'\t\t Server name ',
            u'\t\t title=\'Working directory:  serverInfos.getSystemProperties().get("user.dir") %>\'> getServletConfig().getServletContext().getServerInfo() %> ',
            u'\t\t Servlet version ',
            u'\t\t  getServletConfig().getServletContext().getMajorVersion() %>. getServletConfig().getServletContext().getMinorVersion() %> ',
            u'\t ',
            u'\t ',
            u'\t\t Temp file directory ',
            u'\t\t  value=\' serverInfos.getSystemProperties().get("java.io.tmpdir") %> \'/>  ',
            u'\t\t Running as ',
            u'\t\t title=\'Home directory:  serverInfos.getSystemProperties().get("user.home") %>\'> value=\' serverInfos.getSystemProperties().get("user.name") %> \'/>  ',
            u'\t ',
            u'\t ',
            u'\t\t Startup date ',
            u'\t\t  value=" serverInfos.getStartupTime() %>" type="both" pattern="yyyy-MM-dd HH:mm:ss "/>  ',
            u'\t\t colspan="2"> ',
            u'\t ',
            u' ',
            u' ',
            u'',
            u' ',
            u'\t <legend> CPU and Memory </legend> ',
            u' style="text-align: left;" border="0">',
            u' test=" serverInfos.getCpuCount() >= 0 %>">',
            u'\t ',
            u'\t\t title="maximum number of processors available to the Java virtual machine">Number of CPUs ',
            u'\t\t align="center"> value=" serverInfos.getCpuCount() %>" type="number "/>  ',
            u'\t ',
            u' ',
            u'\t ',
            u'\t\t title="amount of free memory in the system">Free Memory ',
            u'\t\t class="number"> value=" serverInfos.getFreeMemory() %>" type="bytes "/>  ',
            u'\t ',
            u'\t ',
            u'\t\t title="total amount of memory in the Java Virtual Machine">Total Memory ',
            u'\t\t class="number"> value=" serverInfos.getTotalMemory() %>" type="bytes "/>  ',
            u'\t ',
            u' test=" serverInfos.getMaxMemory() >= 0 %>">',
            u'\t ',
            u'\t\t title="maximum amount of memory that the Java virtual machine will attempt to use">Max Memory ',
            u'\t\t class="number"> value=" serverInfos.getMaxMemory() %>" type="bytes "/>  ',
            u'\t ',
            u' ',
            u' ',
            u' ',
            u'',
            u' ',
            u'\t <legend> VM Info </legend> ',
            u' extracted properties from System.getProperties() (see JavaDoc) -->',
            u' style="text-align: left;" border="0">',
            u'\t VM Info ',
            u'\t ',
            u'\t\t Java VM ',
            u'\t\t ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.vendor") %> \'/> ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.name") %> \'/> ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.vm.version") %> \'/> ',
            u'\t\t ',
            u'\t ',
            u'\t ',
            u'\t\t Java RE ',
            u'\t\t ',
            u'\t\t\t  =" serverInfos.getSystemProperties().get("java.vendor.url") %>"> value=\' serverInfos.getSystemProperties().get("java.vendor") %> \'/>  ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("java.version") %> \'/>  @  value=\' serverInfos.getSystemProperties().get("java.home") %> \'/> ',
            u'\t\t ',
            u'\t ',
            u'\t ',
            u'\t\t Platform ',
            u'\t\t ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("os.name") %> \'/> / value=\' serverInfos.getSystemProperties().get("os.arch") %> \'/> ',
            u'\t\t\t value=\' serverInfos.getSystemProperties().get("os.version") %> \'/> ',
            u'\t\t ',
            u'\t ',
            u' ',
            u' ',
            u'',
            u' style="text-align: center;"> type="button" onclick="window.location.reload()">Refresh  ',
            u'',
            u' class="error"> value=\' request.getAttribute("error") %> \'/>  ',
            u' class="message"> value=\' request.getAttribute("message") %> \'/>  ',
            u'',
            u' id="extraServerAttributes">',
            u' items=" serverInfos.getServerSpecificData() %>" var="serverSpecificData" varStatus="status">',
            u' java.util.Map.Entry serverSpecificData = (java.util.Map.Entry) pageContext.getAttribute("serverSpecificData"); %>',
            u'\t ',
            u'\t\t <legend  > serverSpecificData.getKey() %> </legend> ',
            u'\t\t serverSpecificData.getValue() %>',
            u'\t ',
            u' ',
            u' ',
            u'',
            u' <jsp:include  page="footer.jsp "/> ',
            u'',
            u' ',
            u' '
        ]
        assert expected == result


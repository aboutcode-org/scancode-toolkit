<?xml version="1.0" encoding="ISO-8859-1"?>
<%@page session="false" contentType="text/html; charset=ISO-8859-1" %>
<%@page import="clime.messadmin.model.IServerInfo" %>
<%@taglib prefix="core" uri="messadmin-core" %>
<%@taglib prefix="format" uri="messadmin-fmt" %>
<%--!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"--%>
<%--!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"--%>
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%--!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"--%>
<%--!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
 "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"--%>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<% IServerInfo serverInfos = (IServerInfo) request.getAttribute("serverInfos");
   String webFilesRoot = (String) request.getAttribute("WebFilesRoot"); %>
<%--c:url value="${pageContext.request.servletPath}" var="submitUrl" scope="page"/--%><%-- can use value="${pageContext.request.servletPath}" because this JSP is include()'ed --%>
<%-- or use directly ${pageContext.request.requestURI} --%>
<% String submitUrl = request.getContextPath() + request.getServletPath(); /* Can use +request.getServletPath() because this JSP is include()'ed */ %>
<head>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>
	<meta http-equiv="pragma" content="no-cache"/><!-- HTTP 1.0 -->
	<meta http-equiv="cache-control" content="no-cache,must-revalidate"/><!-- HTTP 1.1 -->
	<meta http-equiv="expires" content="0"/><!-- 0 is an invalid value and should be treated as 'now' -->
	<meta http-equiv="content-language" content="en"/><%-- fr-FR --%>
	<meta name="author" content="Cedrik LIME"/>
	<meta name="copyright" content="copyright 2005-2006 Cedrik LIME"/>
	<meta name="robots" content="noindex,nofollow,noarchive"/>
	<title>Server System Informations</title>
	<link rel="stylesheet" type="text/css" href="<%=webFilesRoot%>MessAdmin.css"/>
	<style type="text/css">
	</style>
	<script type="text/javascript" src="<%=webFilesRoot%>js/getElementsBySelector.js"></script>
	<script type="text/javascript" src="<%=webFilesRoot%>js/behavior.js"></script>
	<script type="text/javascript" src="<%=webFilesRoot%>js/MessAdmin.js"></script>
	<script type="text/javascript">//<![CDATA[
		function reloadPage() {
			window.location.reload();
		}
	//]]>
	</script>
</head>
<body>

<!---------------------
<table border="0" cellspacing="0" cellpadding="0" width="100%">
<tr>
<td align="right" class="topheading" width="44"><img alt="Indus Logo" border="0" height="39" width="44" src="<%=request.getContextPath()%>/MessAdmin/images/logo.gif"></td><td class="topheading">Indus Application Management Console<br>
</td>
</tr>
</table>
<br>
<table border="0" cellspacing="0" cellpadding="0">
<tr>
<td class="backtab"><a class="tabs" href="http://localhost:8083/serverbydomain?querynames=*ias50%3A*">Server view</a></td>
<td width="2"></td><td class="backtab"><a class="tabs" href="http://localhost:8083/empty?template=emptymbean">MBean view</a></td><td width="2"></td>
<td class="backtab"><a class="tabs" href="http://localhost:8083/mbean?objectname=JMImplementation%3Atype%3DMBeanServerDelegate&template=about">About</a></td>
<td width="2"></td><td class="fronttab"><a class="tabs" href="http://localhost:8888/ias50/MessAdmin">Session Admin</a></td>
</tr>
</table>
------------------------>

<jsp:include page="header.jsp"/>

<table border="0" cellspacing="0" cellpadding="0" width="100%">
<tr>
  <td class="darker"></td>
</tr>
<tr>
  <td class="lighter">
  <div id="menu" style="font-size: small;">
  [
  Server Informations
  |
  <a href="<%=submitUrl%>?action=webAppsList">Web Applications list</a>
  ]
  </div>
  </td>
</tr>
</table>
<br>

<fieldset>
	<legend>Server Information</legend>
<table style="text-align: left;" border="0">
	<tr>
		<th>Server name</th>
		<td title='Working directory: <%= serverInfos.getSystemProperties().get("user.dir") %>'><%= getServletConfig().getServletContext().getServerInfo() %></td>
		<th>Servlet version</th>
		<td><%= getServletConfig().getServletContext().getMajorVersion() %>.<%= getServletConfig().getServletContext().getMinorVersion() %></td>
	</tr>
	<tr>
		<th>Temp file directory</th>
		<td><core:out value='<%= serverInfos.getSystemProperties().get("java.io.tmpdir") %>'/></td>
		<th>Running as</th>
		<td title='Home directory: <%= serverInfos.getSystemProperties().get("user.home") %>'><core:out value='<%= serverInfos.getSystemProperties().get("user.name") %>'/></td>
	</tr>
	<tr>
		<th>Startup date</th>
		<td><format:formatDate value="<%= serverInfos.getStartupTime() %>" type="both" pattern="yyyy-MM-dd HH:mm:ss"/></td>
		<td colspan="2"></td>
	</tr>
</table>
</fieldset>

<fieldset>
	<legend>CPU and Memory</legend>
<table style="text-align: left;" border="0">
<core:if test="<%= serverInfos.getCpuCount() >= 0 %>">
	<tr>
		<th title="maximum number of processors available to the Java virtual machine">Number of CPUs</th>
		<td align="center"><format:formatNumber value="<%= serverInfos.getCpuCount() %>" type="number"/></td>
	</tr>
</core:if>
	<tr>
		<th title="amount of free memory in the system">Free Memory</th>
		<td class="number"><format:formatNumber value="<%= serverInfos.getFreeMemory() %>" type="bytes"/></td>
	</tr>
	<tr>
		<th title="total amount of memory in the Java Virtual Machine">Total Memory</th>
		<td class="number"><format:formatNumber value="<%= serverInfos.getTotalMemory() %>" type="bytes"/></td>
	</tr>
<core:if test="<%= serverInfos.getMaxMemory() >= 0 %>">
	<tr>
		<th title="maximum amount of memory that the Java virtual machine will attempt to use">Max Memory</th>
		<td class="number"><format:formatNumber value="<%= serverInfos.getMaxMemory() %>" type="bytes"/></td>
	</tr>
</core:if>
</table>
</fieldset>

<fieldset>
	<legend>VM Info</legend>
<!-- extracted properties from System.getProperties() (see JavaDoc) -->
<table style="text-align: left;" border="0">
	<%--caption>VM Info</caption--%>
	<tr>
		<th>Java VM</th>
		<td>
			<core:out value='<%= serverInfos.getSystemProperties().get("java.vm.vendor") %>'/>
			<core:out value='<%= serverInfos.getSystemProperties().get("java.vm.name") %>'/>
			<core:out value='<%= serverInfos.getSystemProperties().get("java.vm.version") %>'/>
		</td>
	</tr>
	<tr>
		<th>Java RE</th>
		<td>
			<a href="<%= serverInfos.getSystemProperties().get("java.vendor.url") %>"><core:out value='<%= serverInfos.getSystemProperties().get("java.vendor") %>'/></a>
			<core:out value='<%= serverInfos.getSystemProperties().get("java.version") %>'/> @ <core:out value='<%= serverInfos.getSystemProperties().get("java.home") %>'/>
		</td>
	</tr>
	<tr>
		<th>Platform</th>
		<td>
			<core:out value='<%= serverInfos.getSystemProperties().get("os.name") %>'/>/<core:out value='<%= serverInfos.getSystemProperties().get("os.arch") %>'/>
			<core:out value='<%= serverInfos.getSystemProperties().get("os.version") %>'/>
		</td>
	</tr>
</table>
</fieldset>

<p style="text-align: center;"><button type="button" onclick="window.location.reload()">Refresh</button></p>

<div class="error"><core:out value='<%= request.getAttribute("error") %>'/></div>
<div class="message"><core:out value='<%= request.getAttribute("message") %>'/></div>

<div id="extraServerAttributes">
<core:forEach items="<%= serverInfos.getServerSpecificData() %>" var="serverSpecificData" varStatus="status">
<%	java.util.Map.Entry serverSpecificData = (java.util.Map.Entry) pageContext.getAttribute("serverSpecificData"); %>
	<fieldset>
		<legend ><%= serverSpecificData.getKey() %></legend>
		<%= serverSpecificData.getValue() %>
	</fieldset>
</core:forEach>
</div>

<jsp:include page="footer.jsp"/>

</body>
</html>
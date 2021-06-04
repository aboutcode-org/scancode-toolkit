<%@ taglib prefix="c" uri="/WEB-INF/tlds/c.tld" %>
<%@ taglib prefix="tags" tagdir="/WEB-INF/tags" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>Loop Example</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
</head>
<body>
<h1>Even numbers from 1 to 100:</h1>
<c:forEach var="i" begin="1" end="100">
  <c:if test="${i % 2 == 0}">
    ${i}
  </c:if>
</c:forEach>
<tags:a/>
<%= "testProperty=" + System.getProperty("testProperty") %>
</body>
</html>
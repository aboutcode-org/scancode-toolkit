<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>FOSSology - bitfield.h - FOSSology</title>
<meta name="description" content="Redmine" />
<meta name="keywords" content="issue,bug,tracker" />
<meta name="csrf-param" content="authenticity_token"/>
<meta name="csrf-token" content="I9ihGYYID6BhanCmu+QYUK67b8+MmOgL5dc9XI8nCvY="/>
<link rel='shortcut icon' href='/favicon.ico?1200087899' />
<link href="/themes/red-andy/stylesheets/application.css?1317061750" media="all" rel="stylesheet" type="text/css" />

<script src="/javascripts/prototype.js?1317407706" type="text/javascript"></script>
<script src="/javascripts/effects.js?1317407706" type="text/javascript"></script>
<script src="/javascripts/dragdrop.js?1317407706" type="text/javascript"></script>
<script src="/javascripts/controls.js?1317407706" type="text/javascript"></script>
<script src="/javascripts/application.js?1317407742" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[
Event.observe(window, 'load', function(){ new WarnLeavingUnsaved('The current page contains unsaved text that will be lost if you leave this page.'); });
//]]>
</script>

<!--[if IE 6]>
    <style type="text/css">
      * html body{ width: expression( document.documentElement.clientWidth < 900 ? '900px' : '100%' ); }
      body {behavior: url(/stylesheets/csshover.htc?1317407706);}
    </style>
<![endif]-->

<!-- page specific tags -->
    <link href="/stylesheets/scm.css?1317407706" media="screen" rel="stylesheet" type="text/css" /></head>
<body class="theme-Red-andy controller-attachments action-show">
<div id="wrapper">
<div id="wrapper2">
<div id="top-menu">
    <div id="account">
        <ul><li><a href="/login" class="login">Sign in</a></li>
<li><a href="/account/register" class="register">Register</a></li></ul>    </div>
    
    <ul><li><a href="/" class="home">Home</a></li>
<li><a href="/projects" class="projects">Projects</a></li>
<li><a href="http://www.redmine.org/guide" class="help">Help</a></li></ul></div>
      
<div id="header">
    
    <div id="quick-search">
        <form action="/search/index/fossology" method="get">
        
        <a href="/search/index/fossology" accesskey="4">Search</a>:
        <input accesskey="f" class="small" id="q" name="q" size="20" type="text" />
        </form>
        
    </div>
    
    
    <h1>FOSSology</h1>
    
    
    <div id="main-menu">
        <ul><li><a href="/projects/fossology" class="overview">Overview</a></li>
<li><a href="/projects/fossology/activity" class="activity">Activity</a></li>
<li><a href="/projects/fossology/roadmap" class="roadmap">Roadmap</a></li>
<li><a href="/projects/fossology/issues" class="issues">Backlog</a></li>
<li><a href="/projects/fossology/news" class="news">News</a></li>
<li><a href="/projects/fossology/documents" class="documents">Meetings</a></li>
<li><a href="/projects/fossology/wiki" class="wiki">Documentation</a></li>
<li><a href="/projects/fossology/boards" class="boards">Forums</a></li>
<li><a href="/projects/fossology/files" class="files">Files</a></li>
<li><a href="/projects/fossology/repository" class="repository">Repository</a></li></ul>
    </div>
    
</div>

<div class="nosidebar" id="main">
    <div id="sidebar">        
        
        
    </div>
    
    <div id="content">
				
        <h2>bitfield.h</h2>

<div class="attachments">
<p>
   <span class="author">Mary Laser, 09/28/2012 12:23 pm</span></p>
<p><a href="/attachments/download/2391/bitfield.h">Download</a>   <span class="size">(710 Bytes)</span></p>

</div>
&nbsp;
<div class="autoscroll">
<table class="filecontent syntaxhl">
<tbody>


<tr><th class="line-num" id="L1"><a href="#L1">1</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L2"><a href="#L2">2</a></th><td class="line-code"><pre> * linux/arch/unicore32/include/mach/bitfield.h
</pre></td></tr>


<tr><th class="line-num" id="L3"><a href="#L3">3</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L4"><a href="#L4">4</a></th><td class="line-code"><pre> * Code specific to PKUnity SoC and UniCore ISA
</pre></td></tr>


<tr><th class="line-num" id="L5"><a href="#L5">5</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L6"><a href="#L6">6</a></th><td class="line-code"><pre> * Copyright (C) 2001-2010 GUAN Xue-tao
</pre></td></tr>


<tr><th class="line-num" id="L7"><a href="#L7">7</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L8"><a href="#L8">8</a></th><td class="line-code"><pre> * This program is free software; you can redistribute it and/or modify
</pre></td></tr>


<tr><th class="line-num" id="L9"><a href="#L9">9</a></th><td class="line-code"><pre> * it under the terms of the GNU General Public License version 2 as
</pre></td></tr>


<tr><th class="line-num" id="L10"><a href="#L10">10</a></th><td class="line-code"><pre> * published by the Free Software Foundation.
</pre></td></tr>


<tr><th class="line-num" id="L11"><a href="#L11">11</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L12"><a href="#L12">12</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> __MACH_PUV3_BITFIELD_H__
</pre></td></tr>


<tr><th class="line-num" id="L13"><a href="#L13">13</a></th><td class="line-code"><pre><span class="pp">#define</span> __MACH_PUV3_BITFIELD_H__
</pre></td></tr>


<tr><th class="line-num" id="L14"><a href="#L14">14</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L15"><a href="#L15">15</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> __ASSEMBLY__
</pre></td></tr>


<tr><th class="line-num" id="L16"><a href="#L16">16</a></th><td class="line-code"><pre><span class="pp">#define</span> UData(Data)        ((<span class="pt">unsigned</span> <span class="pt">long</span>) (Data))
</pre></td></tr>


<tr><th class="line-num" id="L17"><a href="#L17">17</a></th><td class="line-code"><pre><span class="pp">#else</span>
</pre></td></tr>


<tr><th class="line-num" id="L18"><a href="#L18">18</a></th><td class="line-code"><pre><span class="pp">#define</span> UData(Data)        (Data)
</pre></td></tr>


<tr><th class="line-num" id="L19"><a href="#L19">19</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L20"><a href="#L20">20</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L21"><a href="#L21">21</a></th><td class="line-code"><pre><span class="pp">#define</span> FIELD(val, vmask, vshift)        (((val) &amp; ((UData(<span class="i">1</span>) &lt;&lt; (vmask)) - <span class="i">1</span>)) &lt;&lt; (vshift))
</pre></td></tr>


<tr><th class="line-num" id="L22"><a href="#L22">22</a></th><td class="line-code"><pre><span class="pp">#define</span> FMASK(vmask, vshift)                (((UData(<span class="i">1</span>) &lt;&lt; (vmask)) - <span class="i">1</span>) &lt;&lt; (vshift))
</pre></td></tr>


<tr><th class="line-num" id="L23"><a href="#L23">23</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L24"><a href="#L24">24</a></th><td class="line-code"><pre><span class="pp">#endif</span> <span class="c">/* __MACH_PUV3_BITFIELD_H__ */</span>
</pre></td></tr>


</tbody>
</table>
</div>





        
				<div style="clear:both;"></div>
    </div>
</div>

<div id="ajax-indicator" style="display:none;"><span>Loading...</span></div>
	
<div id="footer">
  <div class="bgl"><div class="bgr">
    Powered by <a href="http://www.redmine.org/">Redmine</a> &copy; 2006-2011 Jean-Philippe Lang
  </div></div>
</div>
</div>
</div>

</body>
</html>

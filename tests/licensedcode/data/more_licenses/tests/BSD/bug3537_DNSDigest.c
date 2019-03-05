<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>FOSSology - DNSDigest.c - FOSSology</title>
<meta name="description" content="Redmine" />
<meta name="keywords" content="issue,bug,tracker" />
<meta name="csrf-param" content="authenticity_token"/>
<meta name="csrf-token" content="BePCBSOB/G9kvDUAeFeQkaceZBTBDjNd6J+u958OcwQ="/>
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
				
        <h2>DNSDigest.c</h2>

<div class="attachments">
<p>Test file - 
   <span class="author">Bob Gobeille, 09/25/2012 07:46 pm</span></p>
<p><a href="/attachments/download/2379/DNSDigest.c">Download</a>   <span class="size">(47.9 kB)</span></p>

</div>
&nbsp;
<div class="autoscroll">
<table class="filecontent syntaxhl">
<tbody>


<tr><th class="line-num" id="L1"><a href="#L1">1</a></th><td class="line-code"><pre><span class="c">/* -*- Mode: C; tab-width: 4 -*-
</pre></td></tr>


<tr><th class="line-num" id="L2"><a href="#L2">2</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L3"><a href="#L3">3</a></th><td class="line-code"><pre> * Copyright (c) 2002-2003 Apple Computer, Inc. All rights reserved.
</pre></td></tr>


<tr><th class="line-num" id="L4"><a href="#L4">4</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L5"><a href="#L5">5</a></th><td class="line-code"><pre> * Licensed under the Apache License, Version 2.0 (the &quot;License&quot;);
</pre></td></tr>


<tr><th class="line-num" id="L6"><a href="#L6">6</a></th><td class="line-code"><pre> * you may not use this file except in compliance with the License.
</pre></td></tr>


<tr><th class="line-num" id="L7"><a href="#L7">7</a></th><td class="line-code"><pre> * You may obtain a copy of the License at
</pre></td></tr>


<tr><th class="line-num" id="L8"><a href="#L8">8</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L9"><a href="#L9">9</a></th><td class="line-code"><pre> *     http://www.apache.org/licenses/LICENSE-2.0
</pre></td></tr>


<tr><th class="line-num" id="L10"><a href="#L10">10</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L11"><a href="#L11">11</a></th><td class="line-code"><pre> * Unless required by applicable law or agreed to in writing, software
</pre></td></tr>


<tr><th class="line-num" id="L12"><a href="#L12">12</a></th><td class="line-code"><pre> * distributed under the License is distributed on an &quot;AS IS&quot; BASIS,
</pre></td></tr>


<tr><th class="line-num" id="L13"><a href="#L13">13</a></th><td class="line-code"><pre> * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
</pre></td></tr>


<tr><th class="line-num" id="L14"><a href="#L14">14</a></th><td class="line-code"><pre> * See the License for the specific language governing permissions and
</pre></td></tr>


<tr><th class="line-num" id="L15"><a href="#L15">15</a></th><td class="line-code"><pre> * limitations under the License.
</pre></td></tr>


<tr><th class="line-num" id="L16"><a href="#L16">16</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L17"><a href="#L17">17</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L18"><a href="#L18">18</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L19"><a href="#L19">19</a></th><td class="line-code"><pre><span class="pp">#ifdef</span> __cplusplus
</pre></td></tr>


<tr><th class="line-num" id="L20"><a href="#L20">20</a></th><td class="line-code"><pre><span class="di">extern</span> <span class="s"><span class="dl">&quot;</span><span class="k">C</span><span class="dl">&quot;</span></span> {
</pre></td></tr>


<tr><th class="line-num" id="L21"><a href="#L21">21</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L22"><a href="#L22">22</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L23"><a href="#L23">23</a></th><td class="line-code"><pre><span class="pp">#include</span> <span class="ic">&quot;mDNSEmbeddedAPI.h&quot;</span>
</pre></td></tr>


<tr><th class="line-num" id="L24"><a href="#L24">24</a></th><td class="line-code"><pre><span class="pp">#include</span> <span class="ic">&quot;DNSCommon.h&quot;</span>
</pre></td></tr>


<tr><th class="line-num" id="L25"><a href="#L25">25</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L26"><a href="#L26">26</a></th><td class="line-code"><pre><span class="c">// Disable certain benign warnings with Microsoft compilers</span>
</pre></td></tr>


<tr><th class="line-num" id="L27"><a href="#L27">27</a></th><td class="line-code"><pre><span class="pp">#if</span>(defined(_MSC_VER))
</pre></td></tr>


<tr><th class="line-num" id="L28"><a href="#L28">28</a></th><td class="line-code"><pre>        <span class="c">// Disable &quot;conditional expression is constant&quot; warning for debug macros.</span>
</pre></td></tr>


<tr><th class="line-num" id="L29"><a href="#L29">29</a></th><td class="line-code"><pre>        <span class="c">// Otherwise, this generates warnings for the perfectly natural construct &quot;while(1)&quot;</span>
</pre></td></tr>


<tr><th class="line-num" id="L30"><a href="#L30">30</a></th><td class="line-code"><pre>        <span class="c">// If someone knows a variant way of writing &quot;while(1)&quot; that doesn't generate warning messages, please let us know</span>
</pre></td></tr>


<tr><th class="line-num" id="L31"><a href="#L31">31</a></th><td class="line-code"><pre>        <span class="pp">#pragma</span> warning(disable:<span class="i">4127</span>)
</pre></td></tr>


<tr><th class="line-num" id="L32"><a href="#L32">32</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L33"><a href="#L33">33</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L34"><a href="#L34">34</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L35"><a href="#L35">35</a></th><td class="line-code"><pre> <span class="c">// ***************************************************************************</span>
</pre></td></tr>


<tr><th class="line-num" id="L36"><a href="#L36">36</a></th><td class="line-code"><pre><span class="pp">#if</span> COMPILER_LIKES_PRAGMA_MARK
</pre></td></tr>


<tr><th class="line-num" id="L37"><a href="#L37">37</a></th><td class="line-code"><pre><span class="pp">#pragma</span> mark - Byte Swapping Functions
</pre></td></tr>


<tr><th class="line-num" id="L38"><a href="#L38">38</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L39"><a href="#L39">39</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L40"><a href="#L40">40</a></th><td class="line-code"><pre>mDNSlocal mDNSu16 NToH16(mDNSu8 * bytes)
</pre></td></tr>


<tr><th class="line-num" id="L41"><a href="#L41">41</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L42"><a href="#L42">42</a></th><td class="line-code"><pre>        <span class="r">return</span> (mDNSu16)((mDNSu16)bytes[<span class="i">0</span>] &lt;&lt; <span class="i">8</span> | (mDNSu16)bytes[<span class="i">1</span>]);
</pre></td></tr>


<tr><th class="line-num" id="L43"><a href="#L43">43</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L44"><a href="#L44">44</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L45"><a href="#L45">45</a></th><td class="line-code"><pre>mDNSlocal mDNSu32 NToH32(mDNSu8 * bytes)
</pre></td></tr>


<tr><th class="line-num" id="L46"><a href="#L46">46</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L47"><a href="#L47">47</a></th><td class="line-code"><pre>        <span class="r">return</span> (mDNSu32)((mDNSu32) bytes[<span class="i">0</span>] &lt;&lt; <span class="i">24</span> | (mDNSu32) bytes[<span class="i">1</span>] &lt;&lt; <span class="i">16</span> | (mDNSu32) bytes[<span class="i">2</span>] &lt;&lt; <span class="i">8</span> | (mDNSu32)bytes[<span class="i">3</span>]);
</pre></td></tr>


<tr><th class="line-num" id="L48"><a href="#L48">48</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L49"><a href="#L49">49</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L50"><a href="#L50">50</a></th><td class="line-code"><pre> <span class="c">// ***************************************************************************</span>
</pre></td></tr>


<tr><th class="line-num" id="L51"><a href="#L51">51</a></th><td class="line-code"><pre><span class="pp">#if</span> COMPILER_LIKES_PRAGMA_MARK
</pre></td></tr>


<tr><th class="line-num" id="L52"><a href="#L52">52</a></th><td class="line-code"><pre><span class="pp">#pragma</span> mark - MD5 Hash Functions
</pre></td></tr>


<tr><th class="line-num" id="L53"><a href="#L53">53</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L54"><a href="#L54">54</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L55"><a href="#L55">55</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L56"><a href="#L56">56</a></th><td class="line-code"><pre><span class="c">/* The source for the has is derived CommonCrypto files CommonDigest.h, md32_common.h, md5_locl.h, md5_locl.h, and openssl/md5.h.
</pre></td></tr>


<tr><th class="line-num" id="L57"><a href="#L57">57</a></th><td class="line-code"><pre> * The following changes have been made to the original sources:
</pre></td></tr>


<tr><th class="line-num" id="L58"><a href="#L58">58</a></th><td class="line-code"><pre> *    replaced CC_LONG w/ mDNSu32
</pre></td></tr>


<tr><th class="line-num" id="L59"><a href="#L59">59</a></th><td class="line-code"><pre> *    replaced CC_MD5* with MD5*
</pre></td></tr>


<tr><th class="line-num" id="L60"><a href="#L60">60</a></th><td class="line-code"><pre> *    replaced CC_LONG w/ mDNSu32, removed conditional #defines from md5.h
</pre></td></tr>


<tr><th class="line-num" id="L61"><a href="#L61">61</a></th><td class="line-code"><pre> *    removed extern decls for MD5_Init/Update/Final from CommonDigest.h
</pre></td></tr>


<tr><th class="line-num" id="L62"><a href="#L62">62</a></th><td class="line-code"><pre> *    removed APPLE_COMMON_DIGEST specific #defines from md5_locl.h
</pre></td></tr>


<tr><th class="line-num" id="L63"><a href="#L63">63</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L64"><a href="#L64">64</a></th><td class="line-code"><pre> * Note: machine archetecure specific conditionals from the original sources are turned off, but are left in the code
</pre></td></tr>


<tr><th class="line-num" id="L65"><a href="#L65">65</a></th><td class="line-code"><pre> * to aid in platform-specific optimizations and debugging.
</pre></td></tr>


<tr><th class="line-num" id="L66"><a href="#L66">66</a></th><td class="line-code"><pre> * Sources originally distributed under the following license headers:
</pre></td></tr>


<tr><th class="line-num" id="L67"><a href="#L67">67</a></th><td class="line-code"><pre> * CommonDigest.h - APSL
</pre></td></tr>


<tr><th class="line-num" id="L68"><a href="#L68">68</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L69"><a href="#L69">69</a></th><td class="line-code"><pre> * md32_Common.h
</pre></td></tr>


<tr><th class="line-num" id="L70"><a href="#L70">70</a></th><td class="line-code"><pre> * ====================================================================
</pre></td></tr>


<tr><th class="line-num" id="L71"><a href="#L71">71</a></th><td class="line-code"><pre> * Copyright (c) 1999-2002 The OpenSSL Project.  All rights reserved.
</pre></td></tr>


<tr><th class="line-num" id="L72"><a href="#L72">72</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L73"><a href="#L73">73</a></th><td class="line-code"><pre> * Redistribution and use in source and binary forms, with or without
</pre></td></tr>


<tr><th class="line-num" id="L74"><a href="#L74">74</a></th><td class="line-code"><pre> * modification, are permitted provided that the following conditions
</pre></td></tr>


<tr><th class="line-num" id="L75"><a href="#L75">75</a></th><td class="line-code"><pre> * are met:
</pre></td></tr>


<tr><th class="line-num" id="L76"><a href="#L76">76</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L77"><a href="#L77">77</a></th><td class="line-code"><pre> * 1. Redistributions of source code must retain the above copyright
</pre></td></tr>


<tr><th class="line-num" id="L78"><a href="#L78">78</a></th><td class="line-code"><pre> *    notice, this list of conditions and the following disclaimer. 
</pre></td></tr>


<tr><th class="line-num" id="L79"><a href="#L79">79</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L80"><a href="#L80">80</a></th><td class="line-code"><pre> * 2. Redistributions in binary form must reproduce the above copyright
</pre></td></tr>


<tr><th class="line-num" id="L81"><a href="#L81">81</a></th><td class="line-code"><pre> *    notice, this list of conditions and the following disclaimer in
</pre></td></tr>


<tr><th class="line-num" id="L82"><a href="#L82">82</a></th><td class="line-code"><pre> *    the documentation and/or other materials provided with the
</pre></td></tr>


<tr><th class="line-num" id="L83"><a href="#L83">83</a></th><td class="line-code"><pre> *    distribution.
</pre></td></tr>


<tr><th class="line-num" id="L84"><a href="#L84">84</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L85"><a href="#L85">85</a></th><td class="line-code"><pre> * 3. All advertising materials mentioning features or use of this
</pre></td></tr>


<tr><th class="line-num" id="L86"><a href="#L86">86</a></th><td class="line-code"><pre> *    software must display the following acknowledgment:
</pre></td></tr>


<tr><th class="line-num" id="L87"><a href="#L87">87</a></th><td class="line-code"><pre> *    &quot;This product includes software developed by the OpenSSL Project
</pre></td></tr>


<tr><th class="line-num" id="L88"><a href="#L88">88</a></th><td class="line-code"><pre> *    for use in the OpenSSL Toolkit. (http://www.OpenSSL.org/)&quot;
</pre></td></tr>


<tr><th class="line-num" id="L89"><a href="#L89">89</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L90"><a href="#L90">90</a></th><td class="line-code"><pre> * 4. The names &quot;OpenSSL Toolkit&quot; and &quot;OpenSSL Project&quot; must not be used to
</pre></td></tr>


<tr><th class="line-num" id="L91"><a href="#L91">91</a></th><td class="line-code"><pre> *    endorse or promote products derived from this software without
</pre></td></tr>


<tr><th class="line-num" id="L92"><a href="#L92">92</a></th><td class="line-code"><pre> *    prior written permission. For written permission, please contact
</pre></td></tr>


<tr><th class="line-num" id="L93"><a href="#L93">93</a></th><td class="line-code"><pre> *    licensing@OpenSSL.org.
</pre></td></tr>


<tr><th class="line-num" id="L94"><a href="#L94">94</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L95"><a href="#L95">95</a></th><td class="line-code"><pre> * 5. Products derived from this software may not be called &quot;OpenSSL&quot;
</pre></td></tr>


<tr><th class="line-num" id="L96"><a href="#L96">96</a></th><td class="line-code"><pre> *    nor may &quot;OpenSSL&quot; appear in their names without prior written
</pre></td></tr>


<tr><th class="line-num" id="L97"><a href="#L97">97</a></th><td class="line-code"><pre> *    permission of the OpenSSL Project.
</pre></td></tr>


<tr><th class="line-num" id="L98"><a href="#L98">98</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L99"><a href="#L99">99</a></th><td class="line-code"><pre> * 6. Redistributions of any form whatsoever must retain the following
</pre></td></tr>


<tr><th class="line-num" id="L100"><a href="#L100">100</a></th><td class="line-code"><pre> *    acknowledgment:
</pre></td></tr>


<tr><th class="line-num" id="L101"><a href="#L101">101</a></th><td class="line-code"><pre> *    &quot;This product includes software developed by the OpenSSL Project
</pre></td></tr>


<tr><th class="line-num" id="L102"><a href="#L102">102</a></th><td class="line-code"><pre> *    for use in the OpenSSL Toolkit (http://www.OpenSSL.org/)&quot;
</pre></td></tr>


<tr><th class="line-num" id="L103"><a href="#L103">103</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L104"><a href="#L104">104</a></th><td class="line-code"><pre> * THIS SOFTWARE IS PROVIDED BY THE OpenSSL PROJECT ``AS IS'' AND ANY
</pre></td></tr>


<tr><th class="line-num" id="L105"><a href="#L105">105</a></th><td class="line-code"><pre> * EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
</pre></td></tr>


<tr><th class="line-num" id="L106"><a href="#L106">106</a></th><td class="line-code"><pre> * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
</pre></td></tr>


<tr><th class="line-num" id="L107"><a href="#L107">107</a></th><td class="line-code"><pre> * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE OpenSSL PROJECT OR
</pre></td></tr>


<tr><th class="line-num" id="L108"><a href="#L108">108</a></th><td class="line-code"><pre> * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
</pre></td></tr>


<tr><th class="line-num" id="L109"><a href="#L109">109</a></th><td class="line-code"><pre> * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
</pre></td></tr>


<tr><th class="line-num" id="L110"><a href="#L110">110</a></th><td class="line-code"><pre> * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
</pre></td></tr>


<tr><th class="line-num" id="L111"><a href="#L111">111</a></th><td class="line-code"><pre> * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
</pre></td></tr>


<tr><th class="line-num" id="L112"><a href="#L112">112</a></th><td class="line-code"><pre> * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
</pre></td></tr>


<tr><th class="line-num" id="L113"><a href="#L113">113</a></th><td class="line-code"><pre> * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
</pre></td></tr>


<tr><th class="line-num" id="L114"><a href="#L114">114</a></th><td class="line-code"><pre> * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
</pre></td></tr>


<tr><th class="line-num" id="L115"><a href="#L115">115</a></th><td class="line-code"><pre> * OF THE POSSIBILITY OF SUCH DAMAGE.
</pre></td></tr>


<tr><th class="line-num" id="L116"><a href="#L116">116</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L117"><a href="#L117">117</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L118"><a href="#L118">118</a></th><td class="line-code"><pre> * md5_dgst.c, md5_locl.h
</pre></td></tr>


<tr><th class="line-num" id="L119"><a href="#L119">119</a></th><td class="line-code"><pre> * ====================================================================
</pre></td></tr>


<tr><th class="line-num" id="L120"><a href="#L120">120</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L121"><a href="#L121">121</a></th><td class="line-code"><pre> * This product includes cryptographic software written by Eric Young
</pre></td></tr>


<tr><th class="line-num" id="L122"><a href="#L122">122</a></th><td class="line-code"><pre> * (eay@cryptsoft.com).  This product includes software written by Tim
</pre></td></tr>


<tr><th class="line-num" id="L123"><a href="#L123">123</a></th><td class="line-code"><pre> * Hudson (tjh@cryptsoft.com).
</pre></td></tr>


<tr><th class="line-num" id="L124"><a href="#L124">124</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L125"><a href="#L125">125</a></th><td class="line-code"><pre> * Copyright (C) 1995-1998 Eric Young (eay@cryptsoft.com)
</pre></td></tr>


<tr><th class="line-num" id="L126"><a href="#L126">126</a></th><td class="line-code"><pre> * All rights reserved.
</pre></td></tr>


<tr><th class="line-num" id="L127"><a href="#L127">127</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L128"><a href="#L128">128</a></th><td class="line-code"><pre> * This package is an SSL implementation written
</pre></td></tr>


<tr><th class="line-num" id="L129"><a href="#L129">129</a></th><td class="line-code"><pre> * by Eric Young (eay@cryptsoft.com).
</pre></td></tr>


<tr><th class="line-num" id="L130"><a href="#L130">130</a></th><td class="line-code"><pre> * The implementation was written so as to conform with Netscapes SSL.
</pre></td></tr>


<tr><th class="line-num" id="L131"><a href="#L131">131</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L132"><a href="#L132">132</a></th><td class="line-code"><pre> * This library is free for commercial and non-commercial use as long as
</pre></td></tr>


<tr><th class="line-num" id="L133"><a href="#L133">133</a></th><td class="line-code"><pre> * the following conditions are aheared to.  The following conditions
</pre></td></tr>


<tr><th class="line-num" id="L134"><a href="#L134">134</a></th><td class="line-code"><pre> * apply to all code found in this distribution, be it the RC4, RSA,
</pre></td></tr>


<tr><th class="line-num" id="L135"><a href="#L135">135</a></th><td class="line-code"><pre> * lhash, DES, etc., code; not just the SSL code.  The SSL documentation
</pre></td></tr>


<tr><th class="line-num" id="L136"><a href="#L136">136</a></th><td class="line-code"><pre> * included with this distribution is covered by the same copyright terms
</pre></td></tr>


<tr><th class="line-num" id="L137"><a href="#L137">137</a></th><td class="line-code"><pre> * except that the holder is Tim Hudson (tjh@cryptsoft.com).
</pre></td></tr>


<tr><th class="line-num" id="L138"><a href="#L138">138</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L139"><a href="#L139">139</a></th><td class="line-code"><pre> * Copyright remains Eric Young's, and as such any Copyright notices in
</pre></td></tr>


<tr><th class="line-num" id="L140"><a href="#L140">140</a></th><td class="line-code"><pre> * the code are not to be removed.
</pre></td></tr>


<tr><th class="line-num" id="L141"><a href="#L141">141</a></th><td class="line-code"><pre> * If this package is used in a product, Eric Young should be given attribution
</pre></td></tr>


<tr><th class="line-num" id="L142"><a href="#L142">142</a></th><td class="line-code"><pre> * as the author of the parts of the library used.
</pre></td></tr>


<tr><th class="line-num" id="L143"><a href="#L143">143</a></th><td class="line-code"><pre> * This can be in the form of a textual message at program startup or
</pre></td></tr>


<tr><th class="line-num" id="L144"><a href="#L144">144</a></th><td class="line-code"><pre> * in documentation (online or textual) provided with the package.
</pre></td></tr>


<tr><th class="line-num" id="L145"><a href="#L145">145</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L146"><a href="#L146">146</a></th><td class="line-code"><pre> * Redistribution and use in source and binary forms, with or without
</pre></td></tr>


<tr><th class="line-num" id="L147"><a href="#L147">147</a></th><td class="line-code"><pre> * modification, are permitted provided that the following conditions
</pre></td></tr>


<tr><th class="line-num" id="L148"><a href="#L148">148</a></th><td class="line-code"><pre> * are met:
</pre></td></tr>


<tr><th class="line-num" id="L149"><a href="#L149">149</a></th><td class="line-code"><pre> * 1. Redistributions of source code must retain the copyright
</pre></td></tr>


<tr><th class="line-num" id="L150"><a href="#L150">150</a></th><td class="line-code"><pre> *    notice, this list of conditions and the following disclaimer.
</pre></td></tr>


<tr><th class="line-num" id="L151"><a href="#L151">151</a></th><td class="line-code"><pre> * 2. Redistributions in binary form must reproduce the above copyright
</pre></td></tr>


<tr><th class="line-num" id="L152"><a href="#L152">152</a></th><td class="line-code"><pre> *    notice, this list of conditions and the following disclaimer in the
</pre></td></tr>


<tr><th class="line-num" id="L153"><a href="#L153">153</a></th><td class="line-code"><pre> *    documentation and/or other materials provided with the distribution.
</pre></td></tr>


<tr><th class="line-num" id="L154"><a href="#L154">154</a></th><td class="line-code"><pre> * 3. All advertising materials mentioning features or use of this software
</pre></td></tr>


<tr><th class="line-num" id="L155"><a href="#L155">155</a></th><td class="line-code"><pre> *    must display the following acknowledgement:
</pre></td></tr>


<tr><th class="line-num" id="L156"><a href="#L156">156</a></th><td class="line-code"><pre> *    &quot;This product includes cryptographic software written by
</pre></td></tr>


<tr><th class="line-num" id="L157"><a href="#L157">157</a></th><td class="line-code"><pre> *     Eric Young (eay@cryptsoft.com)&quot;
</pre></td></tr>


<tr><th class="line-num" id="L158"><a href="#L158">158</a></th><td class="line-code"><pre> *    The word 'cryptographic' can be left out if the rouines from the library
</pre></td></tr>


<tr><th class="line-num" id="L159"><a href="#L159">159</a></th><td class="line-code"><pre> *    being used are not cryptographic related :-).
</pre></td></tr>


<tr><th class="line-num" id="L160"><a href="#L160">160</a></th><td class="line-code"><pre> * 4. If you include any Windows specific code (or a derivative thereof) from 
</pre></td></tr>


<tr><th class="line-num" id="L161"><a href="#L161">161</a></th><td class="line-code"><pre> *    the apps directory (application code) you must include an acknowledgement:
</pre></td></tr>


<tr><th class="line-num" id="L162"><a href="#L162">162</a></th><td class="line-code"><pre> *    &quot;This product includes software written by Tim Hudson (tjh@cryptsoft.com)&quot;
</pre></td></tr>


<tr><th class="line-num" id="L163"><a href="#L163">163</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L164"><a href="#L164">164</a></th><td class="line-code"><pre> * THIS SOFTWARE IS PROVIDED BY ERIC YOUNG ``AS IS'' AND
</pre></td></tr>


<tr><th class="line-num" id="L165"><a href="#L165">165</a></th><td class="line-code"><pre> * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
</pre></td></tr>


<tr><th class="line-num" id="L166"><a href="#L166">166</a></th><td class="line-code"><pre> * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
</pre></td></tr>


<tr><th class="line-num" id="L167"><a href="#L167">167</a></th><td class="line-code"><pre> * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
</pre></td></tr>


<tr><th class="line-num" id="L168"><a href="#L168">168</a></th><td class="line-code"><pre> * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
</pre></td></tr>


<tr><th class="line-num" id="L169"><a href="#L169">169</a></th><td class="line-code"><pre> * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
</pre></td></tr>


<tr><th class="line-num" id="L170"><a href="#L170">170</a></th><td class="line-code"><pre> * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
</pre></td></tr>


<tr><th class="line-num" id="L171"><a href="#L171">171</a></th><td class="line-code"><pre> * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
</pre></td></tr>


<tr><th class="line-num" id="L172"><a href="#L172">172</a></th><td class="line-code"><pre> * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
</pre></td></tr>


<tr><th class="line-num" id="L173"><a href="#L173">173</a></th><td class="line-code"><pre> * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
</pre></td></tr>


<tr><th class="line-num" id="L174"><a href="#L174">174</a></th><td class="line-code"><pre> * SUCH DAMAGE.
</pre></td></tr>


<tr><th class="line-num" id="L175"><a href="#L175">175</a></th><td class="line-code"><pre> * 
</pre></td></tr>


<tr><th class="line-num" id="L176"><a href="#L176">176</a></th><td class="line-code"><pre> * The licence and distribution terms for any publically available version or
</pre></td></tr>


<tr><th class="line-num" id="L177"><a href="#L177">177</a></th><td class="line-code"><pre> * derivative of this code cannot be changed.  i.e. this code cannot simply be
</pre></td></tr>


<tr><th class="line-num" id="L178"><a href="#L178">178</a></th><td class="line-code"><pre> * copied and put under another distribution licence
</pre></td></tr>


<tr><th class="line-num" id="L179"><a href="#L179">179</a></th><td class="line-code"><pre> * [including the GNU Public Licence.]
</pre></td></tr>


<tr><th class="line-num" id="L180"><a href="#L180">180</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L181"><a href="#L181">181</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L182"><a href="#L182">182</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L183"><a href="#L183">183</a></th><td class="line-code"><pre><span class="c">//from CommonDigest.h</span>
</pre></td></tr>


<tr><th class="line-num" id="L184"><a href="#L184">184</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L185"><a href="#L185">185</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_DIGEST_LENGTH        <span class="i">16</span>                        <span class="c">/* digest length in bytes */</span>
</pre></td></tr>


<tr><th class="line-num" id="L186"><a href="#L186">186</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_BLOCK_BYTES                <span class="i">64</span>                        <span class="c">/* block size in bytes */</span>
</pre></td></tr>


<tr><th class="line-num" id="L187"><a href="#L187">187</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_BLOCK_LONG       (MD5_BLOCK_BYTES / <span class="r">sizeof</span>(mDNSu32))
</pre></td></tr>


<tr><th class="line-num" id="L188"><a href="#L188">188</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L189"><a href="#L189">189</a></th><td class="line-code"><pre><span class="r">typedef</span> <span class="r">struct</span> MD5state_st
</pre></td></tr>


<tr><th class="line-num" id="L190"><a href="#L190">190</a></th><td class="line-code"><pre>{
</pre></td></tr>


<tr><th class="line-num" id="L191"><a href="#L191">191</a></th><td class="line-code"><pre>        mDNSu32 A,B,C,D;
</pre></td></tr>


<tr><th class="line-num" id="L192"><a href="#L192">192</a></th><td class="line-code"><pre>        mDNSu32 Nl,Nh;
</pre></td></tr>


<tr><th class="line-num" id="L193"><a href="#L193">193</a></th><td class="line-code"><pre>        mDNSu32 data[MD5_BLOCK_LONG];
</pre></td></tr>


<tr><th class="line-num" id="L194"><a href="#L194">194</a></th><td class="line-code"><pre>        <span class="pt">int</span> num;
</pre></td></tr>


<tr><th class="line-num" id="L195"><a href="#L195">195</a></th><td class="line-code"><pre>} MD5_CTX;
</pre></td></tr>


<tr><th class="line-num" id="L196"><a href="#L196">196</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L197"><a href="#L197">197</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L198"><a href="#L198">198</a></th><td class="line-code"><pre><span class="c">// from openssl/md5.h</span>
</pre></td></tr>


<tr><th class="line-num" id="L199"><a href="#L199">199</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L200"><a href="#L200">200</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_CBLOCK        <span class="i">64</span>
</pre></td></tr>


<tr><th class="line-num" id="L201"><a href="#L201">201</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_LBLOCK        (MD5_CBLOCK/<span class="i">4</span>)
</pre></td></tr>


<tr><th class="line-num" id="L202"><a href="#L202">202</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_DIGEST_LENGTH <span class="i">16</span>
</pre></td></tr>


<tr><th class="line-num" id="L203"><a href="#L203">203</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L204"><a href="#L204">204</a></th><td class="line-code"><pre><span class="pt">int</span> MD5_Init(MD5_CTX *c);
</pre></td></tr>


<tr><th class="line-num" id="L205"><a href="#L205">205</a></th><td class="line-code"><pre><span class="pt">int</span> MD5_Update(MD5_CTX *c, <span class="di">const</span> <span class="di">void</span> *data, <span class="pt">unsigned</span> <span class="pt">long</span> len);
</pre></td></tr>


<tr><th class="line-num" id="L206"><a href="#L206">206</a></th><td class="line-code"><pre><span class="pt">int</span> MD5_Final(<span class="pt">unsigned</span> <span class="pt">char</span> *md, MD5_CTX *c);
</pre></td></tr>


<tr><th class="line-num" id="L207"><a href="#L207">207</a></th><td class="line-code"><pre><span class="di">void</span> MD5_Transform(MD5_CTX *c, <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *b);
</pre></td></tr>


<tr><th class="line-num" id="L208"><a href="#L208">208</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L209"><a href="#L209">209</a></th><td class="line-code"><pre><span class="c">// From md5_locl.h</span>
</pre></td></tr>


<tr><th class="line-num" id="L210"><a href="#L210">210</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L211"><a href="#L211">211</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> MD5_LONG_LOG2
</pre></td></tr>


<tr><th class="line-num" id="L212"><a href="#L212">212</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_LONG_LOG2 <span class="i">2</span> <span class="c">/* default to 32 bits */</span>
</pre></td></tr>


<tr><th class="line-num" id="L213"><a href="#L213">213</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L214"><a href="#L214">214</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L215"><a href="#L215">215</a></th><td class="line-code"><pre><span class="pp">#ifdef</span> MD5_ASM
</pre></td></tr>


<tr><th class="line-num" id="L216"><a href="#L216">216</a></th><td class="line-code"><pre><span class="pp"># if</span> defined(__i386) || defined(__i386__) || defined(_M_IX86) || defined(__INTEL__)
</pre></td></tr>


<tr><th class="line-num" id="L217"><a href="#L217">217</a></th><td class="line-code"><pre><span class="pp">#  define</span> md5_block_host_order md5_block_asm_host_order
</pre></td></tr>


<tr><th class="line-num" id="L218"><a href="#L218">218</a></th><td class="line-code"><pre><span class="pp"># elif</span> defined(__sparc) &amp;&amp; defined(OPENSSL_SYS_ULTRASPARC)
</pre></td></tr>


<tr><th class="line-num" id="L219"><a href="#L219">219</a></th><td class="line-code"><pre>   <span class="di">void</span> md5_block_asm_data_order_aligned (MD5_CTX *c, <span class="di">const</span> mDNSu32 *p,<span class="pt">int</span> num);
</pre></td></tr>


<tr><th class="line-num" id="L220"><a href="#L220">220</a></th><td class="line-code"><pre><span class="pp">#  define</span> HASH_BLOCK_DATA_ORDER_ALIGNED md5_block_asm_data_order_aligned
</pre></td></tr>


<tr><th class="line-num" id="L221"><a href="#L221">221</a></th><td class="line-code"><pre><span class="pp"># endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L222"><a href="#L222">222</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L223"><a href="#L223">223</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L224"><a href="#L224">224</a></th><td class="line-code"><pre><span class="di">void</span> md5_block_host_order (MD5_CTX *c, <span class="di">const</span> <span class="di">void</span> *p,<span class="pt">int</span> num);
</pre></td></tr>


<tr><th class="line-num" id="L225"><a href="#L225">225</a></th><td class="line-code"><pre><span class="di">void</span> md5_block_data_order (MD5_CTX *c, <span class="di">const</span> <span class="di">void</span> *p,<span class="pt">int</span> num);
</pre></td></tr>


<tr><th class="line-num" id="L226"><a href="#L226">226</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L227"><a href="#L227">227</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(__i386) || defined(__i386__) || defined(_M_IX86) || defined(__INTEL__)
</pre></td></tr>


<tr><th class="line-num" id="L228"><a href="#L228">228</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L229"><a href="#L229">229</a></th><td class="line-code"><pre> * *_block_host_order is expected to handle aligned data while
</pre></td></tr>


<tr><th class="line-num" id="L230"><a href="#L230">230</a></th><td class="line-code"><pre> * *_block_data_order - unaligned. As algorithm and host (x86)
</pre></td></tr>


<tr><th class="line-num" id="L231"><a href="#L231">231</a></th><td class="line-code"><pre> * are in this case of the same &quot;endianness&quot; these two are
</pre></td></tr>


<tr><th class="line-num" id="L232"><a href="#L232">232</a></th><td class="line-code"><pre> * otherwise indistinguishable. But normally you don't want to
</pre></td></tr>


<tr><th class="line-num" id="L233"><a href="#L233">233</a></th><td class="line-code"><pre> * call the same function because unaligned access in places
</pre></td></tr>


<tr><th class="line-num" id="L234"><a href="#L234">234</a></th><td class="line-code"><pre> * where alignment is expected is usually a &quot;Bad Thing&quot;. Indeed,
</pre></td></tr>


<tr><th class="line-num" id="L235"><a href="#L235">235</a></th><td class="line-code"><pre> * on RISCs you get punished with BUS ERROR signal or *severe*
</pre></td></tr>


<tr><th class="line-num" id="L236"><a href="#L236">236</a></th><td class="line-code"><pre> * performance degradation. Intel CPUs are in turn perfectly
</pre></td></tr>


<tr><th class="line-num" id="L237"><a href="#L237">237</a></th><td class="line-code"><pre> * capable of loading unaligned data without such drastic side
</pre></td></tr>


<tr><th class="line-num" id="L238"><a href="#L238">238</a></th><td class="line-code"><pre> * effect. Yes, they say it's slower than aligned load, but no
</pre></td></tr>


<tr><th class="line-num" id="L239"><a href="#L239">239</a></th><td class="line-code"><pre> * exception is generated and therefore performance degradation
</pre></td></tr>


<tr><th class="line-num" id="L240"><a href="#L240">240</a></th><td class="line-code"><pre> * is *incomparable* with RISCs. What we should weight here is
</pre></td></tr>


<tr><th class="line-num" id="L241"><a href="#L241">241</a></th><td class="line-code"><pre> * costs of unaligned access against costs of aligning data.
</pre></td></tr>


<tr><th class="line-num" id="L242"><a href="#L242">242</a></th><td class="line-code"><pre> * According to my measurements allowing unaligned access results
</pre></td></tr>


<tr><th class="line-num" id="L243"><a href="#L243">243</a></th><td class="line-code"><pre> * in ~9% performance improvement on Pentium II operating at
</pre></td></tr>


<tr><th class="line-num" id="L244"><a href="#L244">244</a></th><td class="line-code"><pre> * 266MHz. I won't be surprised if the difference will be higher
</pre></td></tr>


<tr><th class="line-num" id="L245"><a href="#L245">245</a></th><td class="line-code"><pre> * on faster systems:-)
</pre></td></tr>


<tr><th class="line-num" id="L246"><a href="#L246">246</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L247"><a href="#L247">247</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L248"><a href="#L248">248</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L249"><a href="#L249">249</a></th><td class="line-code"><pre><span class="pp">#define</span> md5_block_data_order md5_block_host_order
</pre></td></tr>


<tr><th class="line-num" id="L250"><a href="#L250">250</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L251"><a href="#L251">251</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L252"><a href="#L252">252</a></th><td class="line-code"><pre><span class="pp">#define</span> DATA_ORDER_IS_LITTLE_ENDIAN
</pre></td></tr>


<tr><th class="line-num" id="L253"><a href="#L253">253</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L254"><a href="#L254">254</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_LONG                mDNSu32
</pre></td></tr>


<tr><th class="line-num" id="L255"><a href="#L255">255</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_LONG_LOG2        MD5_LONG_LOG2
</pre></td></tr>


<tr><th class="line-num" id="L256"><a href="#L256">256</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_CTX                MD5_CTX
</pre></td></tr>


<tr><th class="line-num" id="L257"><a href="#L257">257</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_CBLOCK                MD5_CBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L258"><a href="#L258">258</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_LBLOCK                MD5_LBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L259"><a href="#L259">259</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L260"><a href="#L260">260</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_UPDATE                MD5_Update
</pre></td></tr>


<tr><th class="line-num" id="L261"><a href="#L261">261</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_TRANSFORM        MD5_Transform
</pre></td></tr>


<tr><th class="line-num" id="L262"><a href="#L262">262</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_FINAL                MD5_Final
</pre></td></tr>


<tr><th class="line-num" id="L263"><a href="#L263">263</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L264"><a href="#L264">264</a></th><td class="line-code"><pre><span class="pp">#define</span>        HASH_MAKE_STRING(c,s)        <span class="r">do</span> {        \
</pre></td></tr>


<tr><th class="line-num" id="L265"><a href="#L265">265</a></th><td class="line-code"><pre>        <span class="pt">unsigned</span> <span class="pt">long</span> ll;                \
</pre></td></tr>


<tr><th class="line-num" id="L266"><a href="#L266">266</a></th><td class="line-code"><pre>        ll=(c)-&gt;A; HOST_l2c(ll,(s));        \
</pre></td></tr>


<tr><th class="line-num" id="L267"><a href="#L267">267</a></th><td class="line-code"><pre>        ll=(c)-&gt;B; HOST_l2c(ll,(s));        \
</pre></td></tr>


<tr><th class="line-num" id="L268"><a href="#L268">268</a></th><td class="line-code"><pre>        ll=(c)-&gt;C; HOST_l2c(ll,(s));        \
</pre></td></tr>


<tr><th class="line-num" id="L269"><a href="#L269">269</a></th><td class="line-code"><pre>        ll=(c)-&gt;D; HOST_l2c(ll,(s));        \
</pre></td></tr>


<tr><th class="line-num" id="L270"><a href="#L270">270</a></th><td class="line-code"><pre>        } <span class="r">while</span> (<span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L271"><a href="#L271">271</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_BLOCK_HOST_ORDER        md5_block_host_order
</pre></td></tr>


<tr><th class="line-num" id="L272"><a href="#L272">272</a></th><td class="line-code"><pre><span class="pp">#if</span> !defined(L_ENDIAN) || defined(md5_block_data_order)
</pre></td></tr>


<tr><th class="line-num" id="L273"><a href="#L273">273</a></th><td class="line-code"><pre><span class="pp">#define</span>        HASH_BLOCK_DATA_ORDER        md5_block_data_order
</pre></td></tr>


<tr><th class="line-num" id="L274"><a href="#L274">274</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L275"><a href="#L275">275</a></th><td class="line-code"><pre> * Little-endians (Intel and Alpha) feel better without this.
</pre></td></tr>


<tr><th class="line-num" id="L276"><a href="#L276">276</a></th><td class="line-code"><pre> * It looks like memcpy does better job than generic
</pre></td></tr>


<tr><th class="line-num" id="L277"><a href="#L277">277</a></th><td class="line-code"><pre> * md5_block_data_order on copying-n-aligning input data.
</pre></td></tr>


<tr><th class="line-num" id="L278"><a href="#L278">278</a></th><td class="line-code"><pre> * But frankly speaking I didn't expect such result on Alpha.
</pre></td></tr>


<tr><th class="line-num" id="L279"><a href="#L279">279</a></th><td class="line-code"><pre> * On the other hand I've got this with egcs-1.0.2 and if
</pre></td></tr>


<tr><th class="line-num" id="L280"><a href="#L280">280</a></th><td class="line-code"><pre> * program is compiled with another (better?) compiler it
</pre></td></tr>


<tr><th class="line-num" id="L281"><a href="#L281">281</a></th><td class="line-code"><pre> * might turn out other way around.
</pre></td></tr>


<tr><th class="line-num" id="L282"><a href="#L282">282</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L283"><a href="#L283">283</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L284"><a href="#L284">284</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L285"><a href="#L285">285</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L286"><a href="#L286">286</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L287"><a href="#L287">287</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L288"><a href="#L288">288</a></th><td class="line-code"><pre><span class="c">// from md32_common.h</span>
</pre></td></tr>


<tr><th class="line-num" id="L289"><a href="#L289">289</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L290"><a href="#L290">290</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L291"><a href="#L291">291</a></th><td class="line-code"><pre> * This is a generic 32 bit &quot;collector&quot; for message digest algorithms.
</pre></td></tr>


<tr><th class="line-num" id="L292"><a href="#L292">292</a></th><td class="line-code"><pre> * Whenever needed it collects input character stream into chunks of
</pre></td></tr>


<tr><th class="line-num" id="L293"><a href="#L293">293</a></th><td class="line-code"><pre> * 32 bit values and invokes a block function that performs actual hash
</pre></td></tr>


<tr><th class="line-num" id="L294"><a href="#L294">294</a></th><td class="line-code"><pre> * calculations.
</pre></td></tr>


<tr><th class="line-num" id="L295"><a href="#L295">295</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L296"><a href="#L296">296</a></th><td class="line-code"><pre> * Porting guide.
</pre></td></tr>


<tr><th class="line-num" id="L297"><a href="#L297">297</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L298"><a href="#L298">298</a></th><td class="line-code"><pre> * Obligatory macros:
</pre></td></tr>


<tr><th class="line-num" id="L299"><a href="#L299">299</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L300"><a href="#L300">300</a></th><td class="line-code"><pre> * DATA_ORDER_IS_BIG_ENDIAN or DATA_ORDER_IS_LITTLE_ENDIAN
</pre></td></tr>


<tr><th class="line-num" id="L301"><a href="#L301">301</a></th><td class="line-code"><pre> *        this macro defines byte order of input stream.
</pre></td></tr>


<tr><th class="line-num" id="L302"><a href="#L302">302</a></th><td class="line-code"><pre> * HASH_CBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L303"><a href="#L303">303</a></th><td class="line-code"><pre> *        size of a unit chunk HASH_BLOCK operates on.
</pre></td></tr>


<tr><th class="line-num" id="L304"><a href="#L304">304</a></th><td class="line-code"><pre> * HASH_LONG
</pre></td></tr>


<tr><th class="line-num" id="L305"><a href="#L305">305</a></th><td class="line-code"><pre> *        has to be at lest 32 bit wide, if it's wider, then
</pre></td></tr>


<tr><th class="line-num" id="L306"><a href="#L306">306</a></th><td class="line-code"><pre> *        HASH_LONG_LOG2 *has to* be defined along
</pre></td></tr>


<tr><th class="line-num" id="L307"><a href="#L307">307</a></th><td class="line-code"><pre> * HASH_CTX
</pre></td></tr>


<tr><th class="line-num" id="L308"><a href="#L308">308</a></th><td class="line-code"><pre> *        context structure that at least contains following
</pre></td></tr>


<tr><th class="line-num" id="L309"><a href="#L309">309</a></th><td class="line-code"><pre> *        members:
</pre></td></tr>


<tr><th class="line-num" id="L310"><a href="#L310">310</a></th><td class="line-code"><pre> *                typedef struct {
</pre></td></tr>


<tr><th class="line-num" id="L311"><a href="#L311">311</a></th><td class="line-code"><pre> *                        ...
</pre></td></tr>


<tr><th class="line-num" id="L312"><a href="#L312">312</a></th><td class="line-code"><pre> *                        HASH_LONG        Nl,Nh;
</pre></td></tr>


<tr><th class="line-num" id="L313"><a href="#L313">313</a></th><td class="line-code"><pre> *                        HASH_LONG        data[HASH_LBLOCK];
</pre></td></tr>


<tr><th class="line-num" id="L314"><a href="#L314">314</a></th><td class="line-code"><pre> *                        int                num;
</pre></td></tr>


<tr><th class="line-num" id="L315"><a href="#L315">315</a></th><td class="line-code"><pre> *                        ...
</pre></td></tr>


<tr><th class="line-num" id="L316"><a href="#L316">316</a></th><td class="line-code"><pre> *                        } HASH_CTX;
</pre></td></tr>


<tr><th class="line-num" id="L317"><a href="#L317">317</a></th><td class="line-code"><pre> * HASH_UPDATE
</pre></td></tr>


<tr><th class="line-num" id="L318"><a href="#L318">318</a></th><td class="line-code"><pre> *        name of &quot;Update&quot; function, implemented here.
</pre></td></tr>


<tr><th class="line-num" id="L319"><a href="#L319">319</a></th><td class="line-code"><pre> * HASH_TRANSFORM
</pre></td></tr>


<tr><th class="line-num" id="L320"><a href="#L320">320</a></th><td class="line-code"><pre> *        name of &quot;Transform&quot; function, implemented here.
</pre></td></tr>


<tr><th class="line-num" id="L321"><a href="#L321">321</a></th><td class="line-code"><pre> * HASH_FINAL
</pre></td></tr>


<tr><th class="line-num" id="L322"><a href="#L322">322</a></th><td class="line-code"><pre> *        name of &quot;Final&quot; function, implemented here.
</pre></td></tr>


<tr><th class="line-num" id="L323"><a href="#L323">323</a></th><td class="line-code"><pre> * HASH_BLOCK_HOST_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L324"><a href="#L324">324</a></th><td class="line-code"><pre> *        name of &quot;block&quot; function treating *aligned* input message
</pre></td></tr>


<tr><th class="line-num" id="L325"><a href="#L325">325</a></th><td class="line-code"><pre> *        in host byte order, implemented externally.
</pre></td></tr>


<tr><th class="line-num" id="L326"><a href="#L326">326</a></th><td class="line-code"><pre> * HASH_BLOCK_DATA_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L327"><a href="#L327">327</a></th><td class="line-code"><pre> *        name of &quot;block&quot; function treating *unaligned* input message
</pre></td></tr>


<tr><th class="line-num" id="L328"><a href="#L328">328</a></th><td class="line-code"><pre> *        in original (data) byte order, implemented externally (it
</pre></td></tr>


<tr><th class="line-num" id="L329"><a href="#L329">329</a></th><td class="line-code"><pre> *        actually is optional if data and host are of the same
</pre></td></tr>


<tr><th class="line-num" id="L330"><a href="#L330">330</a></th><td class="line-code"><pre> *        &quot;endianess&quot;).
</pre></td></tr>


<tr><th class="line-num" id="L331"><a href="#L331">331</a></th><td class="line-code"><pre> * HASH_MAKE_STRING
</pre></td></tr>


<tr><th class="line-num" id="L332"><a href="#L332">332</a></th><td class="line-code"><pre> *        macro convering context variables to an ASCII hash string.
</pre></td></tr>


<tr><th class="line-num" id="L333"><a href="#L333">333</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L334"><a href="#L334">334</a></th><td class="line-code"><pre> * Optional macros:
</pre></td></tr>


<tr><th class="line-num" id="L335"><a href="#L335">335</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L336"><a href="#L336">336</a></th><td class="line-code"><pre> * B_ENDIAN or L_ENDIAN
</pre></td></tr>


<tr><th class="line-num" id="L337"><a href="#L337">337</a></th><td class="line-code"><pre> *        defines host byte-order.
</pre></td></tr>


<tr><th class="line-num" id="L338"><a href="#L338">338</a></th><td class="line-code"><pre> * HASH_LONG_LOG2
</pre></td></tr>


<tr><th class="line-num" id="L339"><a href="#L339">339</a></th><td class="line-code"><pre> *        defaults to 2 if not states otherwise.
</pre></td></tr>


<tr><th class="line-num" id="L340"><a href="#L340">340</a></th><td class="line-code"><pre> * HASH_LBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L341"><a href="#L341">341</a></th><td class="line-code"><pre> *        assumed to be HASH_CBLOCK/4 if not stated otherwise.
</pre></td></tr>


<tr><th class="line-num" id="L342"><a href="#L342">342</a></th><td class="line-code"><pre> * HASH_BLOCK_DATA_ORDER_ALIGNED
</pre></td></tr>


<tr><th class="line-num" id="L343"><a href="#L343">343</a></th><td class="line-code"><pre> *        alternative &quot;block&quot; function capable of treating
</pre></td></tr>


<tr><th class="line-num" id="L344"><a href="#L344">344</a></th><td class="line-code"><pre> *        aligned input message in original (data) order,
</pre></td></tr>


<tr><th class="line-num" id="L345"><a href="#L345">345</a></th><td class="line-code"><pre> *        implemented externally.
</pre></td></tr>


<tr><th class="line-num" id="L346"><a href="#L346">346</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L347"><a href="#L347">347</a></th><td class="line-code"><pre> * MD5 example:
</pre></td></tr>


<tr><th class="line-num" id="L348"><a href="#L348">348</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L349"><a href="#L349">349</a></th><td class="line-code"><pre> *        #define DATA_ORDER_IS_LITTLE_ENDIAN
</pre></td></tr>


<tr><th class="line-num" id="L350"><a href="#L350">350</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L351"><a href="#L351">351</a></th><td class="line-code"><pre> *        #define HASH_LONG                mDNSu32
</pre></td></tr>


<tr><th class="line-num" id="L352"><a href="#L352">352</a></th><td class="line-code"><pre> *        #define HASH_LONG_LOG2        mDNSu32_LOG2
</pre></td></tr>


<tr><th class="line-num" id="L353"><a href="#L353">353</a></th><td class="line-code"><pre> *        #define HASH_CTX                MD5_CTX
</pre></td></tr>


<tr><th class="line-num" id="L354"><a href="#L354">354</a></th><td class="line-code"><pre> *        #define HASH_CBLOCK                MD5_CBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L355"><a href="#L355">355</a></th><td class="line-code"><pre> *        #define HASH_LBLOCK                MD5_LBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L356"><a href="#L356">356</a></th><td class="line-code"><pre> *        #define HASH_UPDATE                MD5_Update
</pre></td></tr>


<tr><th class="line-num" id="L357"><a href="#L357">357</a></th><td class="line-code"><pre> *        #define HASH_TRANSFORM                MD5_Transform
</pre></td></tr>


<tr><th class="line-num" id="L358"><a href="#L358">358</a></th><td class="line-code"><pre> *        #define HASH_FINAL                MD5_Final
</pre></td></tr>


<tr><th class="line-num" id="L359"><a href="#L359">359</a></th><td class="line-code"><pre> *        #define HASH_BLOCK_HOST_ORDER        md5_block_host_order
</pre></td></tr>


<tr><th class="line-num" id="L360"><a href="#L360">360</a></th><td class="line-code"><pre> *        #define HASH_BLOCK_DATA_ORDER        md5_block_data_order
</pre></td></tr>


<tr><th class="line-num" id="L361"><a href="#L361">361</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L362"><a href="#L362">362</a></th><td class="line-code"><pre> *                                        &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L363"><a href="#L363">363</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L364"><a href="#L364">364</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L365"><a href="#L365">365</a></th><td class="line-code"><pre><span class="pp">#if</span> !defined(DATA_ORDER_IS_BIG_ENDIAN) &amp;&amp; !defined(DATA_ORDER_IS_LITTLE_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L366"><a href="#L366">366</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">DATA_ORDER must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L367"><a href="#L367">367</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L368"><a href="#L368">368</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L369"><a href="#L369">369</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_CBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L370"><a href="#L370">370</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_CBLOCK must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L371"><a href="#L371">371</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L372"><a href="#L372">372</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_LONG
</pre></td></tr>


<tr><th class="line-num" id="L373"><a href="#L373">373</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_LONG must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L374"><a href="#L374">374</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L375"><a href="#L375">375</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_CTX
</pre></td></tr>


<tr><th class="line-num" id="L376"><a href="#L376">376</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_CTX must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L377"><a href="#L377">377</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L378"><a href="#L378">378</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L379"><a href="#L379">379</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_UPDATE
</pre></td></tr>


<tr><th class="line-num" id="L380"><a href="#L380">380</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_UPDATE must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L381"><a href="#L381">381</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L382"><a href="#L382">382</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_TRANSFORM
</pre></td></tr>


<tr><th class="line-num" id="L383"><a href="#L383">383</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_TRANSFORM must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L384"><a href="#L384">384</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L385"><a href="#L385">385</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_FINAL
</pre></td></tr>


<tr><th class="line-num" id="L386"><a href="#L386">386</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_FINAL must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L387"><a href="#L387">387</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L388"><a href="#L388">388</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L389"><a href="#L389">389</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_BLOCK_HOST_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L390"><a href="#L390">390</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_BLOCK_HOST_ORDER must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L391"><a href="#L391">391</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L392"><a href="#L392">392</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L393"><a href="#L393">393</a></th><td class="line-code"><pre><span class="c">#if 0
</pre></td></tr>


<tr><th class="line-num" id="L394"><a href="#L394">394</a></th><td class="line-code"><pre>/*
</pre></td></tr>


<tr><th class="line-num" id="L395"><a href="#L395">395</a></th><td class="line-code"><pre> * Moved below as it's required only if HASH_BLOCK_DATA_ORDER_ALIGNED
</pre></td></tr>


<tr><th class="line-num" id="L396"><a href="#L396">396</a></th><td class="line-code"><pre> * isn't defined.
</pre></td></tr>


<tr><th class="line-num" id="L397"><a href="#L397">397</a></th><td class="line-code"><pre> */
</pre></td></tr>


<tr><th class="line-num" id="L398"><a href="#L398">398</a></th><td class="line-code"><pre>#ifndef HASH_BLOCK_DATA_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L399"><a href="#L399">399</a></th><td class="line-code"><pre>#error &quot;HASH_BLOCK_DATA_ORDER must be defined!&quot;
</pre></td></tr>


<tr><th class="line-num" id="L400"><a href="#L400">400</a></th><td class="line-code"><pre>#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L401"><a href="#L401">401</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L402"><a href="#L402">402</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L403"><a href="#L403">403</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_LBLOCK
</pre></td></tr>


<tr><th class="line-num" id="L404"><a href="#L404">404</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_LBLOCK        (HASH_CBLOCK/<span class="i">4</span>)
</pre></td></tr>


<tr><th class="line-num" id="L405"><a href="#L405">405</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L406"><a href="#L406">406</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L407"><a href="#L407">407</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_LONG_LOG2
</pre></td></tr>


<tr><th class="line-num" id="L408"><a href="#L408">408</a></th><td class="line-code"><pre><span class="pp">#define</span> HASH_LONG_LOG2        <span class="i">2</span>
</pre></td></tr>


<tr><th class="line-num" id="L409"><a href="#L409">409</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L410"><a href="#L410">410</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L411"><a href="#L411">411</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L412"><a href="#L412">412</a></th><td class="line-code"><pre> * Engage compiler specific rotate intrinsic function if available.
</pre></td></tr>


<tr><th class="line-num" id="L413"><a href="#L413">413</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L414"><a href="#L414">414</a></th><td class="line-code"><pre><span class="pp">#undef</span> ROTATE
</pre></td></tr>


<tr><th class="line-num" id="L415"><a href="#L415">415</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> PEDANTIC
</pre></td></tr>


<tr><th class="line-num" id="L416"><a href="#L416">416</a></th><td class="line-code"><pre><span class="c"># if 0 /* defined(_MSC_VER) */
</pre></td></tr>


<tr><th class="line-num" id="L417"><a href="#L417">417</a></th><td class="line-code"><pre>#  define ROTATE(a,n)        _lrotl(a,n)
</pre></td></tr>


<tr><th class="line-num" id="L418"><a href="#L418">418</a></th><td class="line-code"><pre># elif defined(__MWERKS__)
</pre></td></tr>


<tr><th class="line-num" id="L419"><a href="#L419">419</a></th><td class="line-code"><pre>#  if defined(__POWERPC__)
</pre></td></tr>


<tr><th class="line-num" id="L420"><a href="#L420">420</a></th><td class="line-code"><pre>#   define ROTATE(a,n)        (unsigned MD32_REG_T)__rlwinm((int)a,n,0,31)
</pre></td></tr>


<tr><th class="line-num" id="L421"><a href="#L421">421</a></th><td class="line-code"><pre>#  elif defined(__MC68K__)
</pre></td></tr>


<tr><th class="line-num" id="L422"><a href="#L422">422</a></th><td class="line-code"><pre>    /* Motorola specific tweak. &lt;appro@fy.chalmers.se&gt; */
</pre></td></tr>


<tr><th class="line-num" id="L423"><a href="#L423">423</a></th><td class="line-code"><pre>#   define ROTATE(a,n)        (n&lt;24 ? __rol(a,n) : __ror(a,32-n))
</pre></td></tr>


<tr><th class="line-num" id="L424"><a href="#L424">424</a></th><td class="line-code"><pre>#  else
</pre></td></tr>


<tr><th class="line-num" id="L425"><a href="#L425">425</a></th><td class="line-code"><pre>#   define ROTATE(a,n)        __rol(a,n)
</pre></td></tr>


<tr><th class="line-num" id="L426"><a href="#L426">426</a></th><td class="line-code"><pre>#  endif
</pre></td></tr>


<tr><th class="line-num" id="L427"><a href="#L427">427</a></th><td class="line-code"><pre># elif defined(__GNUC__) &amp;&amp; __GNUC__&gt;=2 &amp;&amp; !defined(OPENSSL_NO_ASM) &amp;&amp; !defined(OPENSSL_NO_INLINE_ASM)
</pre></td></tr>


<tr><th class="line-num" id="L428"><a href="#L428">428</a></th><td class="line-code"><pre>  /*
</pre></td></tr>


<tr><th class="line-num" id="L429"><a href="#L429">429</a></th><td class="line-code"><pre>   * Some GNU C inline assembler templates. Note that these are
</pre></td></tr>


<tr><th class="line-num" id="L430"><a href="#L430">430</a></th><td class="line-code"><pre>   * rotates by *constant* number of bits! But that's exactly
</pre></td></tr>


<tr><th class="line-num" id="L431"><a href="#L431">431</a></th><td class="line-code"><pre>   * what we need here...
</pre></td></tr>


<tr><th class="line-num" id="L432"><a href="#L432">432</a></th><td class="line-code"><pre>   *
</pre></td></tr>


<tr><th class="line-num" id="L433"><a href="#L433">433</a></th><td class="line-code"><pre>   *                                         &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L434"><a href="#L434">434</a></th><td class="line-code"><pre>   */
</pre></td></tr>


<tr><th class="line-num" id="L435"><a href="#L435">435</a></th><td class="line-code"><pre>  /*
</pre></td></tr>


<tr><th class="line-num" id="L436"><a href="#L436">436</a></th><td class="line-code"><pre>   * LLVM is more strict about compatibility of types between input &amp; output constraints,
</pre></td></tr>


<tr><th class="line-num" id="L437"><a href="#L437">437</a></th><td class="line-code"><pre>   * but we want these to be rotations of 32 bits, not 64, so we explicitly drop the
</pre></td></tr>


<tr><th class="line-num" id="L438"><a href="#L438">438</a></th><td class="line-code"><pre>   * most significant bytes by casting to an unsigned int.
</pre></td></tr>


<tr><th class="line-num" id="L439"><a href="#L439">439</a></th><td class="line-code"><pre>   */
</pre></td></tr>


<tr><th class="line-num" id="L440"><a href="#L440">440</a></th><td class="line-code"><pre>#  if defined(__i386) || defined(__i386__) || defined(__x86_64) || defined(__x86_64__)
</pre></td></tr>


<tr><th class="line-num" id="L441"><a href="#L441">441</a></th><td class="line-code"><pre>#   define ROTATE(a,n)        ({ register unsigned int ret;        \
</pre></td></tr>


<tr><th class="line-num" id="L442"><a href="#L442">442</a></th><td class="line-code"><pre>                                asm (                        \
</pre></td></tr>


<tr><th class="line-num" id="L443"><a href="#L443">443</a></th><td class="line-code"><pre>                                &quot;roll %1,%0&quot;                \
</pre></td></tr>


<tr><th class="line-num" id="L444"><a href="#L444">444</a></th><td class="line-code"><pre>                                : &quot;=r&quot;(ret)                \
</pre></td></tr>


<tr><th class="line-num" id="L445"><a href="#L445">445</a></th><td class="line-code"><pre>                                : &quot;I&quot;(n), &quot;0&quot;((unsigned int)a)        \
</pre></td></tr>


<tr><th class="line-num" id="L446"><a href="#L446">446</a></th><td class="line-code"><pre>                                : &quot;cc&quot;);                \
</pre></td></tr>


<tr><th class="line-num" id="L447"><a href="#L447">447</a></th><td class="line-code"><pre>                           ret;                                \
</pre></td></tr>


<tr><th class="line-num" id="L448"><a href="#L448">448</a></th><td class="line-code"><pre>                        })
</pre></td></tr>


<tr><th class="line-num" id="L449"><a href="#L449">449</a></th><td class="line-code"><pre>#  elif defined(__powerpc) || defined(__ppc)
</pre></td></tr>


<tr><th class="line-num" id="L450"><a href="#L450">450</a></th><td class="line-code"><pre>#   define ROTATE(a,n)        ({ register unsigned int ret;        \
</pre></td></tr>


<tr><th class="line-num" id="L451"><a href="#L451">451</a></th><td class="line-code"><pre>                                asm (                        \
</pre></td></tr>


<tr><th class="line-num" id="L452"><a href="#L452">452</a></th><td class="line-code"><pre>                                &quot;rlwinm %0,%1,%2,0,31&quot;        \
</pre></td></tr>


<tr><th class="line-num" id="L453"><a href="#L453">453</a></th><td class="line-code"><pre>                                : &quot;=r&quot;(ret)                \
</pre></td></tr>


<tr><th class="line-num" id="L454"><a href="#L454">454</a></th><td class="line-code"><pre>                                : &quot;r&quot;(a), &quot;I&quot;(n));        \
</pre></td></tr>


<tr><th class="line-num" id="L455"><a href="#L455">455</a></th><td class="line-code"><pre>                           ret;                                \
</pre></td></tr>


<tr><th class="line-num" id="L456"><a href="#L456">456</a></th><td class="line-code"><pre>                        })
</pre></td></tr>


<tr><th class="line-num" id="L457"><a href="#L457">457</a></th><td class="line-code"><pre>#  endif
</pre></td></tr>


<tr><th class="line-num" id="L458"><a href="#L458">458</a></th><td class="line-code"><pre># endif
</pre></td></tr>


<tr><th class="line-num" id="L459"><a href="#L459">459</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L460"><a href="#L460">460</a></th><td class="line-code"><pre>/*
</pre></td></tr>


<tr><th class="line-num" id="L461"><a href="#L461">461</a></th><td class="line-code"><pre> * Engage compiler specific &quot;fetch in reverse byte order&quot;
</pre></td></tr>


<tr><th class="line-num" id="L462"><a href="#L462">462</a></th><td class="line-code"><pre> * intrinsic function if available.
</pre></td></tr>


<tr><th class="line-num" id="L463"><a href="#L463">463</a></th><td class="line-code"><pre> */
</pre></td></tr>


<tr><th class="line-num" id="L464"><a href="#L464">464</a></th><td class="line-code"><pre># if defined(__GNUC__) &amp;&amp; __GNUC__&gt;=2 &amp;&amp; !defined(OPENSSL_NO_ASM) &amp;&amp; !defined(OPENSSL_NO_INLINE_ASM)
</pre></td></tr>


<tr><th class="line-num" id="L465"><a href="#L465">465</a></th><td class="line-code"><pre>  /* some GNU C inline assembler templates by &lt;appro@fy.chalmers.se&gt; */
</pre></td></tr>


<tr><th class="line-num" id="L466"><a href="#L466">466</a></th><td class="line-code"><pre>#  if (defined(__i386) || defined(__i386__) || defined(__x86_64) || defined(__x86_64__)) &amp;&amp; !defined(I386_ONLY)
</pre></td></tr>


<tr><th class="line-num" id="L467"><a href="#L467">467</a></th><td class="line-code"><pre>#   define BE_FETCH32(a)        ({ register unsigned int l=(a);\
</pre></td></tr>


<tr><th class="line-num" id="L468"><a href="#L468">468</a></th><td class="line-code"><pre>                                asm (                        \
</pre></td></tr>


<tr><th class="line-num" id="L469"><a href="#L469">469</a></th><td class="line-code"><pre>                                &quot;bswapl %0&quot;                \
</pre></td></tr>


<tr><th class="line-num" id="L470"><a href="#L470">470</a></th><td class="line-code"><pre>                                : &quot;=r&quot;(l) : &quot;0&quot;(l));        \
</pre></td></tr>


<tr><th class="line-num" id="L471"><a href="#L471">471</a></th><td class="line-code"><pre>                          l;                                \
</pre></td></tr>


<tr><th class="line-num" id="L472"><a href="#L472">472</a></th><td class="line-code"><pre>                        })
</pre></td></tr>


<tr><th class="line-num" id="L473"><a href="#L473">473</a></th><td class="line-code"><pre>#  elif defined(__powerpc)
</pre></td></tr>


<tr><th class="line-num" id="L474"><a href="#L474">474</a></th><td class="line-code"><pre>#   define LE_FETCH32(a)        ({ register unsigned int l;        \
</pre></td></tr>


<tr><th class="line-num" id="L475"><a href="#L475">475</a></th><td class="line-code"><pre>                                asm (                        \
</pre></td></tr>


<tr><th class="line-num" id="L476"><a href="#L476">476</a></th><td class="line-code"><pre>                                &quot;lwbrx %0,0,%1&quot;                \
</pre></td></tr>


<tr><th class="line-num" id="L477"><a href="#L477">477</a></th><td class="line-code"><pre>                                : &quot;=r&quot;(l)                \
</pre></td></tr>


<tr><th class="line-num" id="L478"><a href="#L478">478</a></th><td class="line-code"><pre>                                : &quot;r&quot;(a));                \
</pre></td></tr>


<tr><th class="line-num" id="L479"><a href="#L479">479</a></th><td class="line-code"><pre>                           l;                                \
</pre></td></tr>


<tr><th class="line-num" id="L480"><a href="#L480">480</a></th><td class="line-code"><pre>                        })
</pre></td></tr>


<tr><th class="line-num" id="L481"><a href="#L481">481</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L482"><a href="#L482">482</a></th><td class="line-code"><pre>#  elif defined(__sparc) &amp;&amp; defined(OPENSSL_SYS_ULTRASPARC)
</pre></td></tr>


<tr><th class="line-num" id="L483"><a href="#L483">483</a></th><td class="line-code"><pre>#  define LE_FETCH32(a)        ({ register unsigned int l;                \
</pre></td></tr>


<tr><th class="line-num" id="L484"><a href="#L484">484</a></th><td class="line-code"><pre>                                asm (                                \
</pre></td></tr>


<tr><th class="line-num" id="L485"><a href="#L485">485</a></th><td class="line-code"><pre>                                &quot;lda [%1]#ASI_PRIMARY_LITTLE,%0&quot;\
</pre></td></tr>


<tr><th class="line-num" id="L486"><a href="#L486">486</a></th><td class="line-code"><pre>                                : &quot;=r&quot;(l)                        \
</pre></td></tr>


<tr><th class="line-num" id="L487"><a href="#L487">487</a></th><td class="line-code"><pre>                                : &quot;r&quot;(a));                        \
</pre></td></tr>


<tr><th class="line-num" id="L488"><a href="#L488">488</a></th><td class="line-code"><pre>                           l;                                        \
</pre></td></tr>


<tr><th class="line-num" id="L489"><a href="#L489">489</a></th><td class="line-code"><pre>                        })
</pre></td></tr>


<tr><th class="line-num" id="L490"><a href="#L490">490</a></th><td class="line-code"><pre>#  endif
</pre></td></tr>


<tr><th class="line-num" id="L491"><a href="#L491">491</a></th><td class="line-code"><pre># endif
</pre></td></tr>


<tr><th class="line-num" id="L492"><a href="#L492">492</a></th><td class="line-code"><pre>#endif /* PEDANTIC */</span>
</pre></td></tr>


<tr><th class="line-num" id="L493"><a href="#L493">493</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L494"><a href="#L494">494</a></th><td class="line-code"><pre><span class="pp">#if</span> HASH_LONG_LOG2==<span class="i">2</span>        <span class="c">/* Engage only if sizeof(HASH_LONG)== 4 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L495"><a href="#L495">495</a></th><td class="line-code"><pre><span class="c">/* A nice byte order reversal from Wei Dai &lt;weidai@eskimo.com&gt; */</span>
</pre></td></tr>


<tr><th class="line-num" id="L496"><a href="#L496">496</a></th><td class="line-code"><pre><span class="pp">#ifdef</span> ROTATE
</pre></td></tr>


<tr><th class="line-num" id="L497"><a href="#L497">497</a></th><td class="line-code"><pre><span class="c">/* 5 instructions with rotate instruction, else 9 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L498"><a href="#L498">498</a></th><td class="line-code"><pre><span class="pp">#define</span> REVERSE_FETCH32(a,l)        (                                        \
</pre></td></tr>


<tr><th class="line-num" id="L499"><a href="#L499">499</a></th><td class="line-code"><pre>                l=*(<span class="di">const</span> HASH_LONG *)(a),                                \
</pre></td></tr>


<tr><th class="line-num" id="L500"><a href="#L500">500</a></th><td class="line-code"><pre>                ((ROTATE(l,<span class="i">8</span>)&amp;<span class="hx">0x00FF00FF</span>)|(ROTATE((l&amp;<span class="hx">0x00FF00FF</span>),<span class="i">24</span>)))        \
</pre></td></tr>


<tr><th class="line-num" id="L501"><a href="#L501">501</a></th><td class="line-code"><pre>                                )
</pre></td></tr>


<tr><th class="line-num" id="L502"><a href="#L502">502</a></th><td class="line-code"><pre><span class="pp">#else</span>
</pre></td></tr>


<tr><th class="line-num" id="L503"><a href="#L503">503</a></th><td class="line-code"><pre><span class="c">/* 6 instructions with rotate instruction, else 8 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L504"><a href="#L504">504</a></th><td class="line-code"><pre><span class="pp">#define</span> REVERSE_FETCH32(a,l)        (                                \
</pre></td></tr>


<tr><th class="line-num" id="L505"><a href="#L505">505</a></th><td class="line-code"><pre>                l=*(<span class="di">const</span> HASH_LONG *)(a),                        \
</pre></td></tr>


<tr><th class="line-num" id="L506"><a href="#L506">506</a></th><td class="line-code"><pre>                l=(((l&gt;&gt;<span class="i">8</span>)&amp;<span class="hx">0x00FF00FF</span>)|((l&amp;<span class="hx">0x00FF00FF</span>)&lt;&lt;<span class="i">8</span>)),        \
</pre></td></tr>


<tr><th class="line-num" id="L507"><a href="#L507">507</a></th><td class="line-code"><pre>                ROTATE(l,<span class="i">16</span>)                                        \
</pre></td></tr>


<tr><th class="line-num" id="L508"><a href="#L508">508</a></th><td class="line-code"><pre>                                )
</pre></td></tr>


<tr><th class="line-num" id="L509"><a href="#L509">509</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L510"><a href="#L510">510</a></th><td class="line-code"><pre> * Originally the middle line started with l=(((l&amp;0xFF00FF00)&gt;&gt;8)|...
</pre></td></tr>


<tr><th class="line-num" id="L511"><a href="#L511">511</a></th><td class="line-code"><pre> * It's rewritten as above for two reasons:
</pre></td></tr>


<tr><th class="line-num" id="L512"><a href="#L512">512</a></th><td class="line-code"><pre> *        - RISCs aren't good at long constants and have to explicitely
</pre></td></tr>


<tr><th class="line-num" id="L513"><a href="#L513">513</a></th><td class="line-code"><pre> *          compose 'em with several (well, usually 2) instructions in a
</pre></td></tr>


<tr><th class="line-num" id="L514"><a href="#L514">514</a></th><td class="line-code"><pre> *          register before performing the actual operation and (as you
</pre></td></tr>


<tr><th class="line-num" id="L515"><a href="#L515">515</a></th><td class="line-code"><pre> *          already realized:-) having same constant should inspire the
</pre></td></tr>


<tr><th class="line-num" id="L516"><a href="#L516">516</a></th><td class="line-code"><pre> *          compiler to permanently allocate the only register for it;
</pre></td></tr>


<tr><th class="line-num" id="L517"><a href="#L517">517</a></th><td class="line-code"><pre> *        - most modern CPUs have two ALUs, but usually only one has
</pre></td></tr>


<tr><th class="line-num" id="L518"><a href="#L518">518</a></th><td class="line-code"><pre> *          circuitry for shifts:-( this minor tweak inspires compiler
</pre></td></tr>


<tr><th class="line-num" id="L519"><a href="#L519">519</a></th><td class="line-code"><pre> *          to schedule shift instructions in a better way...
</pre></td></tr>


<tr><th class="line-num" id="L520"><a href="#L520">520</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L521"><a href="#L521">521</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L522"><a href="#L522">522</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L523"><a href="#L523">523</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L524"><a href="#L524">524</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L525"><a href="#L525">525</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L526"><a href="#L526">526</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> ROTATE
</pre></td></tr>


<tr><th class="line-num" id="L527"><a href="#L527">527</a></th><td class="line-code"><pre><span class="pp">#define</span> ROTATE(a,n)     (((a)&lt;&lt;(n))|(((a)&amp;<span class="hx">0xffffffff</span>)&gt;&gt;(<span class="i">32</span>-(n))))
</pre></td></tr>


<tr><th class="line-num" id="L528"><a href="#L528">528</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L529"><a href="#L529">529</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L530"><a href="#L530">530</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L531"><a href="#L531">531</a></th><td class="line-code"><pre> * Make some obvious choices. E.g., HASH_BLOCK_DATA_ORDER_ALIGNED
</pre></td></tr>


<tr><th class="line-num" id="L532"><a href="#L532">532</a></th><td class="line-code"><pre> * and HASH_BLOCK_HOST_ORDER ought to be the same if input data
</pre></td></tr>


<tr><th class="line-num" id="L533"><a href="#L533">533</a></th><td class="line-code"><pre> * and host are of the same &quot;endianess&quot;. It's possible to mask
</pre></td></tr>


<tr><th class="line-num" id="L534"><a href="#L534">534</a></th><td class="line-code"><pre> * this with blank #define HASH_BLOCK_DATA_ORDER though...
</pre></td></tr>


<tr><th class="line-num" id="L535"><a href="#L535">535</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L536"><a href="#L536">536</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L537"><a href="#L537">537</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L538"><a href="#L538">538</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(B_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L539"><a href="#L539">539</a></th><td class="line-code"><pre><span class="pp">#  if</span> defined(DATA_ORDER_IS_BIG_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L540"><a href="#L540">540</a></th><td class="line-code"><pre><span class="pp">#    if</span> !defined(HASH_BLOCK_DATA_ORDER_ALIGNED) &amp;&amp; HASH_LONG_LOG2==<span class="i">2</span>
</pre></td></tr>


<tr><th class="line-num" id="L541"><a href="#L541">541</a></th><td class="line-code"><pre><span class="pp">#      define</span> HASH_BLOCK_DATA_ORDER_ALIGNED        HASH_BLOCK_HOST_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L542"><a href="#L542">542</a></th><td class="line-code"><pre><span class="pp">#    endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L543"><a href="#L543">543</a></th><td class="line-code"><pre><span class="pp">#  elif</span> defined(DATA_ORDER_IS_LITTLE_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L544"><a href="#L544">544</a></th><td class="line-code"><pre><span class="pp">#    ifndef</span> HOST_FETCH32
</pre></td></tr>


<tr><th class="line-num" id="L545"><a href="#L545">545</a></th><td class="line-code"><pre><span class="pp">#      ifdef</span> LE_FETCH32
</pre></td></tr>


<tr><th class="line-num" id="L546"><a href="#L546">546</a></th><td class="line-code"><pre><span class="pp">#        define</span> HOST_FETCH32(p,l)        LE_FETCH32(p)
</pre></td></tr>


<tr><th class="line-num" id="L547"><a href="#L547">547</a></th><td class="line-code"><pre><span class="pp">#      elif</span> defined(REVERSE_FETCH32)
</pre></td></tr>


<tr><th class="line-num" id="L548"><a href="#L548">548</a></th><td class="line-code"><pre><span class="pp">#        define</span> HOST_FETCH32(p,l)        REVERSE_FETCH32(p,l)
</pre></td></tr>


<tr><th class="line-num" id="L549"><a href="#L549">549</a></th><td class="line-code"><pre><span class="pp">#      endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L550"><a href="#L550">550</a></th><td class="line-code"><pre><span class="pp">#    endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L551"><a href="#L551">551</a></th><td class="line-code"><pre><span class="pp">#  endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L552"><a href="#L552">552</a></th><td class="line-code"><pre><span class="pp">#elif</span> defined(L_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L553"><a href="#L553">553</a></th><td class="line-code"><pre><span class="pp">#  if</span> defined(DATA_ORDER_IS_LITTLE_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L554"><a href="#L554">554</a></th><td class="line-code"><pre><span class="pp">#    if</span> !defined(HASH_BLOCK_DATA_ORDER_ALIGNED) &amp;&amp; HASH_LONG_LOG2==<span class="i">2</span>
</pre></td></tr>


<tr><th class="line-num" id="L555"><a href="#L555">555</a></th><td class="line-code"><pre><span class="pp">#      define</span> HASH_BLOCK_DATA_ORDER_ALIGNED        HASH_BLOCK_HOST_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L556"><a href="#L556">556</a></th><td class="line-code"><pre><span class="pp">#    endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L557"><a href="#L557">557</a></th><td class="line-code"><pre><span class="pp">#  elif</span> defined(DATA_ORDER_IS_BIG_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L558"><a href="#L558">558</a></th><td class="line-code"><pre><span class="pp">#    ifndef</span> HOST_FETCH32
</pre></td></tr>


<tr><th class="line-num" id="L559"><a href="#L559">559</a></th><td class="line-code"><pre><span class="pp">#      ifdef</span> BE_FETCH32
</pre></td></tr>


<tr><th class="line-num" id="L560"><a href="#L560">560</a></th><td class="line-code"><pre><span class="pp">#        define</span> HOST_FETCH32(p,l)        BE_FETCH32(p)
</pre></td></tr>


<tr><th class="line-num" id="L561"><a href="#L561">561</a></th><td class="line-code"><pre><span class="pp">#      elif</span> defined(REVERSE_FETCH32)
</pre></td></tr>


<tr><th class="line-num" id="L562"><a href="#L562">562</a></th><td class="line-code"><pre><span class="pp">#        define</span> HOST_FETCH32(p,l)        REVERSE_FETCH32(p,l)
</pre></td></tr>


<tr><th class="line-num" id="L563"><a href="#L563">563</a></th><td class="line-code"><pre><span class="pp">#      endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L564"><a href="#L564">564</a></th><td class="line-code"><pre><span class="pp">#    endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L565"><a href="#L565">565</a></th><td class="line-code"><pre><span class="pp">#  endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L566"><a href="#L566">566</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L567"><a href="#L567">567</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L568"><a href="#L568">568</a></th><td class="line-code"><pre><span class="pp">#if</span> !defined(HASH_BLOCK_DATA_ORDER_ALIGNED)
</pre></td></tr>


<tr><th class="line-num" id="L569"><a href="#L569">569</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_BLOCK_DATA_ORDER
</pre></td></tr>


<tr><th class="line-num" id="L570"><a href="#L570">570</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_BLOCK_DATA_ORDER must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L571"><a href="#L571">571</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L572"><a href="#L572">572</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L573"><a href="#L573">573</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L574"><a href="#L574">574</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(DATA_ORDER_IS_BIG_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L575"><a href="#L575">575</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L576"><a href="#L576">576</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_c2l(c,l)        (l =(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">24</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L577"><a href="#L577">577</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L578"><a href="#L578">578</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L579"><a href="#L579">579</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))    ),                \
</pre></td></tr>


<tr><th class="line-num" id="L580"><a href="#L580">580</a></th><td class="line-code"><pre>                         l)
</pre></td></tr>


<tr><th class="line-num" id="L581"><a href="#L581">581</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_p_c2l(c,l,n)        {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L582"><a href="#L582">582</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (n) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L583"><a href="#L583">583</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">0</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">24</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L584"><a href="#L584">584</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L585"><a href="#L585">585</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L586"><a href="#L586">586</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">3</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)));                \
</pre></td></tr>


<tr><th class="line-num" id="L587"><a href="#L587">587</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L588"><a href="#L588">588</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_p_c2l_p(c,l,sc,len) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L589"><a href="#L589">589</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (sc) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L590"><a href="#L590">590</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">0</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">24</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L591"><a href="#L591">591</a></th><td class="line-code"><pre>                                <span class="r">if</span> (--len == <span class="i">0</span>) <span class="r">break</span>;                        \
</pre></td></tr>


<tr><th class="line-num" id="L592"><a href="#L592">592</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L593"><a href="#L593">593</a></th><td class="line-code"><pre>                                <span class="r">if</span> (--len == <span class="i">0</span>) <span class="r">break</span>;                        \
</pre></td></tr>


<tr><th class="line-num" id="L594"><a href="#L594">594</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L595"><a href="#L595">595</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L596"><a href="#L596">596</a></th><td class="line-code"><pre><span class="c">/* NOTE the pointer is not incremented at the end of this */</span>
</pre></td></tr>


<tr><th class="line-num" id="L597"><a href="#L597">597</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_c2l_p(c,l,n)        {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L598"><a href="#L598">598</a></th><td class="line-code"><pre>                        l=<span class="i">0</span>; (c)+=n;                                        \
</pre></td></tr>


<tr><th class="line-num" id="L599"><a href="#L599">599</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (n) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L600"><a href="#L600">600</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">3</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L601"><a href="#L601">601</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L602"><a href="#L602">602</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))))&lt;&lt;<span class="i">24</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L603"><a href="#L603">603</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L604"><a href="#L604">604</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_l2c(l,c)        (*((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt;<span class="i">24</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L605"><a href="#L605">605</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt;<span class="i">16</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L606"><a href="#L606">606</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt; <span class="i">8</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L607"><a href="#L607">607</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)    )&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L608"><a href="#L608">608</a></th><td class="line-code"><pre>                         l)
</pre></td></tr>


<tr><th class="line-num" id="L609"><a href="#L609">609</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L610"><a href="#L610">610</a></th><td class="line-code"><pre><span class="pp">#elif</span> defined(DATA_ORDER_IS_LITTLE_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L611"><a href="#L611">611</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L612"><a href="#L612">612</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_c2l(c,l)        (l =(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))    ),                \
</pre></td></tr>


<tr><th class="line-num" id="L613"><a href="#L613">613</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L614"><a href="#L614">614</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L615"><a href="#L615">615</a></th><td class="line-code"><pre>                         l|=(((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">24</span>),                \
</pre></td></tr>


<tr><th class="line-num" id="L616"><a href="#L616">616</a></th><td class="line-code"><pre>                         l)
</pre></td></tr>


<tr><th class="line-num" id="L617"><a href="#L617">617</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_p_c2l(c,l,n)        {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L618"><a href="#L618">618</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (n) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L619"><a href="#L619">619</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">0</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)));                \
</pre></td></tr>


<tr><th class="line-num" id="L620"><a href="#L620">620</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L621"><a href="#L621">621</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L622"><a href="#L622">622</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">3</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">24</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L623"><a href="#L623">623</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L624"><a href="#L624">624</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_p_c2l_p(c,l,sc,len) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L625"><a href="#L625">625</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (sc) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L626"><a href="#L626">626</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">0</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)));                \
</pre></td></tr>


<tr><th class="line-num" id="L627"><a href="#L627">627</a></th><td class="line-code"><pre>                                <span class="r">if</span> (--len == <span class="i">0</span>) <span class="r">break</span>;                        \
</pre></td></tr>


<tr><th class="line-num" id="L628"><a href="#L628">628</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L629"><a href="#L629">629</a></th><td class="line-code"><pre>                                <span class="r">if</span> (--len == <span class="i">0</span>) <span class="r">break</span>;                        \
</pre></td></tr>


<tr><th class="line-num" id="L630"><a href="#L630">630</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*((c)++)))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L631"><a href="#L631">631</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L632"><a href="#L632">632</a></th><td class="line-code"><pre><span class="c">/* NOTE the pointer is not incremented at the end of this */</span>
</pre></td></tr>


<tr><th class="line-num" id="L633"><a href="#L633">633</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_c2l_p(c,l,n)        {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L634"><a href="#L634">634</a></th><td class="line-code"><pre>                        l=<span class="i">0</span>; (c)+=n;                                        \
</pre></td></tr>


<tr><th class="line-num" id="L635"><a href="#L635">635</a></th><td class="line-code"><pre>                        <span class="r">switch</span> (n) {                                        \
</pre></td></tr>


<tr><th class="line-num" id="L636"><a href="#L636">636</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">3</span>: l =((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))))&lt;&lt;<span class="i">16</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L637"><a href="#L637">637</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">2</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))))&lt;&lt; <span class="i">8</span>;        \
</pre></td></tr>


<tr><th class="line-num" id="L638"><a href="#L638">638</a></th><td class="line-code"><pre>                        <span class="r">case</span> <span class="i">1</span>: l|=((<span class="pt">unsigned</span> <span class="pt">long</span>)(*(--(c))));                \
</pre></td></tr>


<tr><th class="line-num" id="L639"><a href="#L639">639</a></th><td class="line-code"><pre>                                } }
</pre></td></tr>


<tr><th class="line-num" id="L640"><a href="#L640">640</a></th><td class="line-code"><pre><span class="pp">#define</span> HOST_l2c(l,c)        (*((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)    )&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L641"><a href="#L641">641</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt; <span class="i">8</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L642"><a href="#L642">642</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt;<span class="i">16</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L643"><a href="#L643">643</a></th><td class="line-code"><pre>                         *((c)++)=(<span class="pt">unsigned</span> <span class="pt">char</span>)(((l)&gt;&gt;<span class="i">24</span>)&amp;<span class="hx">0xff</span>),        \
</pre></td></tr>


<tr><th class="line-num" id="L644"><a href="#L644">644</a></th><td class="line-code"><pre>                         l)
</pre></td></tr>


<tr><th class="line-num" id="L645"><a href="#L645">645</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L646"><a href="#L646">646</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L647"><a href="#L647">647</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L648"><a href="#L648">648</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L649"><a href="#L649">649</a></th><td class="line-code"><pre> * Time for some action:-)
</pre></td></tr>


<tr><th class="line-num" id="L650"><a href="#L650">650</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L651"><a href="#L651">651</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L652"><a href="#L652">652</a></th><td class="line-code"><pre><span class="pt">int</span> HASH_UPDATE (HASH_CTX *c, <span class="di">const</span> <span class="di">void</span> *data_, <span class="pt">unsigned</span> <span class="pt">long</span> len)
</pre></td></tr>


<tr><th class="line-num" id="L653"><a href="#L653">653</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L654"><a href="#L654">654</a></th><td class="line-code"><pre>        <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *data=(<span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *)data_;
</pre></td></tr>


<tr><th class="line-num" id="L655"><a href="#L655">655</a></th><td class="line-code"><pre>        <span class="di">register</span> HASH_LONG * p;
</pre></td></tr>


<tr><th class="line-num" id="L656"><a href="#L656">656</a></th><td class="line-code"><pre>        <span class="di">register</span> <span class="pt">unsigned</span> <span class="pt">long</span> l;
</pre></td></tr>


<tr><th class="line-num" id="L657"><a href="#L657">657</a></th><td class="line-code"><pre>        <span class="pt">int</span> sw,sc,ew,ec;
</pre></td></tr>


<tr><th class="line-num" id="L658"><a href="#L658">658</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L659"><a href="#L659">659</a></th><td class="line-code"><pre>        <span class="r">if</span> (len==<span class="i">0</span>) <span class="r">return</span> <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L660"><a href="#L660">660</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L661"><a href="#L661">661</a></th><td class="line-code"><pre>        l=(c-&gt;Nl+(len&lt;&lt;<span class="i">3</span>))&amp;<span class="hx">0xffffffff</span>L;
</pre></td></tr>


<tr><th class="line-num" id="L662"><a href="#L662">662</a></th><td class="line-code"><pre>        <span class="c">/* 95-05-24 eay Fixed a bug with the overflow handling, thanks to
</pre></td></tr>


<tr><th class="line-num" id="L663"><a href="#L663">663</a></th><td class="line-code"><pre>         * Wei Dai &lt;weidai@eskimo.com&gt; for pointing it out. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L664"><a href="#L664">664</a></th><td class="line-code"><pre>        <span class="r">if</span> (l &lt; c-&gt;Nl) <span class="c">/* overflow */</span>
</pre></td></tr>


<tr><th class="line-num" id="L665"><a href="#L665">665</a></th><td class="line-code"><pre>                c-&gt;Nh++;
</pre></td></tr>


<tr><th class="line-num" id="L666"><a href="#L666">666</a></th><td class="line-code"><pre>        c-&gt;Nh+=(len&gt;&gt;<span class="i">29</span>);
</pre></td></tr>


<tr><th class="line-num" id="L667"><a href="#L667">667</a></th><td class="line-code"><pre>        c-&gt;Nl=l;
</pre></td></tr>


<tr><th class="line-num" id="L668"><a href="#L668">668</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L669"><a href="#L669">669</a></th><td class="line-code"><pre>        <span class="r">if</span> (c-&gt;num != <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L670"><a href="#L670">670</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L671"><a href="#L671">671</a></th><td class="line-code"><pre>                p=c-&gt;data;
</pre></td></tr>


<tr><th class="line-num" id="L672"><a href="#L672">672</a></th><td class="line-code"><pre>                sw=c-&gt;num&gt;&gt;<span class="i">2</span>;
</pre></td></tr>


<tr><th class="line-num" id="L673"><a href="#L673">673</a></th><td class="line-code"><pre>                sc=c-&gt;num&amp;<span class="hx">0x03</span>;
</pre></td></tr>


<tr><th class="line-num" id="L674"><a href="#L674">674</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L675"><a href="#L675">675</a></th><td class="line-code"><pre>                <span class="r">if</span> ((c-&gt;num+len) &gt;= HASH_CBLOCK)
</pre></td></tr>


<tr><th class="line-num" id="L676"><a href="#L676">676</a></th><td class="line-code"><pre>                        {
</pre></td></tr>


<tr><th class="line-num" id="L677"><a href="#L677">677</a></th><td class="line-code"><pre>                        l=p[sw]; HOST_p_c2l(data,l,sc); p[sw++]=l;
</pre></td></tr>


<tr><th class="line-num" id="L678"><a href="#L678">678</a></th><td class="line-code"><pre>                        <span class="r">for</span> (; sw&lt;HASH_LBLOCK; sw++)
</pre></td></tr>


<tr><th class="line-num" id="L679"><a href="#L679">679</a></th><td class="line-code"><pre>                                {
</pre></td></tr>


<tr><th class="line-num" id="L680"><a href="#L680">680</a></th><td class="line-code"><pre>                                HOST_c2l(data,l); p[sw]=l;
</pre></td></tr>


<tr><th class="line-num" id="L681"><a href="#L681">681</a></th><td class="line-code"><pre>                                }
</pre></td></tr>


<tr><th class="line-num" id="L682"><a href="#L682">682</a></th><td class="line-code"><pre>                        HASH_BLOCK_HOST_ORDER (c,p,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L683"><a href="#L683">683</a></th><td class="line-code"><pre>                        len-=(HASH_CBLOCK-c-&gt;num);
</pre></td></tr>


<tr><th class="line-num" id="L684"><a href="#L684">684</a></th><td class="line-code"><pre>                        c-&gt;num=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L685"><a href="#L685">685</a></th><td class="line-code"><pre>                        <span class="c">/* drop through and do the rest */</span>
</pre></td></tr>


<tr><th class="line-num" id="L686"><a href="#L686">686</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L687"><a href="#L687">687</a></th><td class="line-code"><pre>                <span class="r">else</span>
</pre></td></tr>


<tr><th class="line-num" id="L688"><a href="#L688">688</a></th><td class="line-code"><pre>                        {
</pre></td></tr>


<tr><th class="line-num" id="L689"><a href="#L689">689</a></th><td class="line-code"><pre>                        c-&gt;num+=len;
</pre></td></tr>


<tr><th class="line-num" id="L690"><a href="#L690">690</a></th><td class="line-code"><pre>                        <span class="r">if</span> ((sc+len) &lt; <span class="i">4</span>) <span class="c">/* ugly, add char's to a word */</span>
</pre></td></tr>


<tr><th class="line-num" id="L691"><a href="#L691">691</a></th><td class="line-code"><pre>                                {
</pre></td></tr>


<tr><th class="line-num" id="L692"><a href="#L692">692</a></th><td class="line-code"><pre>                                l=p[sw]; HOST_p_c2l_p(data,l,sc,len); p[sw]=l;
</pre></td></tr>


<tr><th class="line-num" id="L693"><a href="#L693">693</a></th><td class="line-code"><pre>                                }
</pre></td></tr>


<tr><th class="line-num" id="L694"><a href="#L694">694</a></th><td class="line-code"><pre>                        <span class="r">else</span>
</pre></td></tr>


<tr><th class="line-num" id="L695"><a href="#L695">695</a></th><td class="line-code"><pre>                                {
</pre></td></tr>


<tr><th class="line-num" id="L696"><a href="#L696">696</a></th><td class="line-code"><pre>                                ew=(c-&gt;num&gt;&gt;<span class="i">2</span>);
</pre></td></tr>


<tr><th class="line-num" id="L697"><a href="#L697">697</a></th><td class="line-code"><pre>                                ec=(c-&gt;num&amp;<span class="hx">0x03</span>);
</pre></td></tr>


<tr><th class="line-num" id="L698"><a href="#L698">698</a></th><td class="line-code"><pre>                                <span class="r">if</span> (sc)
</pre></td></tr>


<tr><th class="line-num" id="L699"><a href="#L699">699</a></th><td class="line-code"><pre>                                        l=p[sw];
</pre></td></tr>


<tr><th class="line-num" id="L700"><a href="#L700">700</a></th><td class="line-code"><pre>                                HOST_p_c2l(data,l,sc);
</pre></td></tr>


<tr><th class="line-num" id="L701"><a href="#L701">701</a></th><td class="line-code"><pre>                                p[sw++]=l;
</pre></td></tr>


<tr><th class="line-num" id="L702"><a href="#L702">702</a></th><td class="line-code"><pre>                                <span class="r">for</span> (; sw &lt; ew; sw++)
</pre></td></tr>


<tr><th class="line-num" id="L703"><a href="#L703">703</a></th><td class="line-code"><pre>                                        {
</pre></td></tr>


<tr><th class="line-num" id="L704"><a href="#L704">704</a></th><td class="line-code"><pre>                                        HOST_c2l(data,l); p[sw]=l;
</pre></td></tr>


<tr><th class="line-num" id="L705"><a href="#L705">705</a></th><td class="line-code"><pre>                                        }
</pre></td></tr>


<tr><th class="line-num" id="L706"><a href="#L706">706</a></th><td class="line-code"><pre>                                <span class="r">if</span> (ec)
</pre></td></tr>


<tr><th class="line-num" id="L707"><a href="#L707">707</a></th><td class="line-code"><pre>                                        {
</pre></td></tr>


<tr><th class="line-num" id="L708"><a href="#L708">708</a></th><td class="line-code"><pre>                                        HOST_c2l_p(data,l,ec); p[sw]=l;
</pre></td></tr>


<tr><th class="line-num" id="L709"><a href="#L709">709</a></th><td class="line-code"><pre>                                        }
</pre></td></tr>


<tr><th class="line-num" id="L710"><a href="#L710">710</a></th><td class="line-code"><pre>                                }
</pre></td></tr>


<tr><th class="line-num" id="L711"><a href="#L711">711</a></th><td class="line-code"><pre>                        <span class="r">return</span> <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L712"><a href="#L712">712</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L713"><a href="#L713">713</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L714"><a href="#L714">714</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L715"><a href="#L715">715</a></th><td class="line-code"><pre>        sw=(<span class="pt">int</span>)(len/HASH_CBLOCK);
</pre></td></tr>


<tr><th class="line-num" id="L716"><a href="#L716">716</a></th><td class="line-code"><pre>        <span class="r">if</span> (sw &gt; <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L717"><a href="#L717">717</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L718"><a href="#L718">718</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(HASH_BLOCK_DATA_ORDER_ALIGNED)
</pre></td></tr>


<tr><th class="line-num" id="L719"><a href="#L719">719</a></th><td class="line-code"><pre>                <span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L720"><a href="#L720">720</a></th><td class="line-code"><pre>                 * Note that HASH_BLOCK_DATA_ORDER_ALIGNED gets defined
</pre></td></tr>


<tr><th class="line-num" id="L721"><a href="#L721">721</a></th><td class="line-code"><pre>                 * only if sizeof(HASH_LONG)==4.
</pre></td></tr>


<tr><th class="line-num" id="L722"><a href="#L722">722</a></th><td class="line-code"><pre>                 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L723"><a href="#L723">723</a></th><td class="line-code"><pre>                <span class="r">if</span> ((((<span class="pt">unsigned</span> <span class="pt">long</span>)data)%<span class="i">4</span>) == <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L724"><a href="#L724">724</a></th><td class="line-code"><pre>                        {
</pre></td></tr>


<tr><th class="line-num" id="L725"><a href="#L725">725</a></th><td class="line-code"><pre>                        <span class="c">/* data is properly aligned so that we can cast it: */</span>
</pre></td></tr>


<tr><th class="line-num" id="L726"><a href="#L726">726</a></th><td class="line-code"><pre>                        HASH_BLOCK_DATA_ORDER_ALIGNED (c,(HASH_LONG *)data,sw);
</pre></td></tr>


<tr><th class="line-num" id="L727"><a href="#L727">727</a></th><td class="line-code"><pre>                        sw*=HASH_CBLOCK;
</pre></td></tr>


<tr><th class="line-num" id="L728"><a href="#L728">728</a></th><td class="line-code"><pre>                        data+=sw;
</pre></td></tr>


<tr><th class="line-num" id="L729"><a href="#L729">729</a></th><td class="line-code"><pre>                        len-=sw;
</pre></td></tr>


<tr><th class="line-num" id="L730"><a href="#L730">730</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L731"><a href="#L731">731</a></th><td class="line-code"><pre>                <span class="r">else</span>
</pre></td></tr>


<tr><th class="line-num" id="L732"><a href="#L732">732</a></th><td class="line-code"><pre><span class="pp">#if</span> !defined(HASH_BLOCK_DATA_ORDER)
</pre></td></tr>


<tr><th class="line-num" id="L733"><a href="#L733">733</a></th><td class="line-code"><pre>                        <span class="r">while</span> (sw--)
</pre></td></tr>


<tr><th class="line-num" id="L734"><a href="#L734">734</a></th><td class="line-code"><pre>                                {
</pre></td></tr>


<tr><th class="line-num" id="L735"><a href="#L735">735</a></th><td class="line-code"><pre>                                mDNSPlatformMemCopy(p=c-&gt;data,data,HASH_CBLOCK);
</pre></td></tr>


<tr><th class="line-num" id="L736"><a href="#L736">736</a></th><td class="line-code"><pre>                                HASH_BLOCK_DATA_ORDER_ALIGNED(c,p,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L737"><a href="#L737">737</a></th><td class="line-code"><pre>                                data+=HASH_CBLOCK;
</pre></td></tr>


<tr><th class="line-num" id="L738"><a href="#L738">738</a></th><td class="line-code"><pre>                                len-=HASH_CBLOCK;
</pre></td></tr>


<tr><th class="line-num" id="L739"><a href="#L739">739</a></th><td class="line-code"><pre>                                }
</pre></td></tr>


<tr><th class="line-num" id="L740"><a href="#L740">740</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L741"><a href="#L741">741</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L742"><a href="#L742">742</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(HASH_BLOCK_DATA_ORDER)
</pre></td></tr>


<tr><th class="line-num" id="L743"><a href="#L743">743</a></th><td class="line-code"><pre>                        {
</pre></td></tr>


<tr><th class="line-num" id="L744"><a href="#L744">744</a></th><td class="line-code"><pre>                        HASH_BLOCK_DATA_ORDER(c,data,sw);
</pre></td></tr>


<tr><th class="line-num" id="L745"><a href="#L745">745</a></th><td class="line-code"><pre>                        sw*=HASH_CBLOCK;
</pre></td></tr>


<tr><th class="line-num" id="L746"><a href="#L746">746</a></th><td class="line-code"><pre>                        data+=sw;
</pre></td></tr>


<tr><th class="line-num" id="L747"><a href="#L747">747</a></th><td class="line-code"><pre>                        len-=sw;
</pre></td></tr>


<tr><th class="line-num" id="L748"><a href="#L748">748</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L749"><a href="#L749">749</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L750"><a href="#L750">750</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L751"><a href="#L751">751</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L752"><a href="#L752">752</a></th><td class="line-code"><pre>        <span class="r">if</span> (len!=<span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L753"><a href="#L753">753</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L754"><a href="#L754">754</a></th><td class="line-code"><pre>                p = c-&gt;data;
</pre></td></tr>


<tr><th class="line-num" id="L755"><a href="#L755">755</a></th><td class="line-code"><pre>                c-&gt;num = (<span class="pt">int</span>)len;
</pre></td></tr>


<tr><th class="line-num" id="L756"><a href="#L756">756</a></th><td class="line-code"><pre>                ew=(<span class="pt">int</span>)(len&gt;&gt;<span class="i">2</span>);        <span class="c">/* words to copy */</span>
</pre></td></tr>


<tr><th class="line-num" id="L757"><a href="#L757">757</a></th><td class="line-code"><pre>                ec=(<span class="pt">int</span>)(len&amp;<span class="hx">0x03</span>);
</pre></td></tr>


<tr><th class="line-num" id="L758"><a href="#L758">758</a></th><td class="line-code"><pre>                <span class="r">for</span> (; ew; ew--,p++)
</pre></td></tr>


<tr><th class="line-num" id="L759"><a href="#L759">759</a></th><td class="line-code"><pre>                        {
</pre></td></tr>


<tr><th class="line-num" id="L760"><a href="#L760">760</a></th><td class="line-code"><pre>                        HOST_c2l(data,l); *p=l;
</pre></td></tr>


<tr><th class="line-num" id="L761"><a href="#L761">761</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L762"><a href="#L762">762</a></th><td class="line-code"><pre>                HOST_c2l_p(data,l,ec);
</pre></td></tr>


<tr><th class="line-num" id="L763"><a href="#L763">763</a></th><td class="line-code"><pre>                *p=l;
</pre></td></tr>


<tr><th class="line-num" id="L764"><a href="#L764">764</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L765"><a href="#L765">765</a></th><td class="line-code"><pre>        <span class="r">return</span> <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L766"><a href="#L766">766</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L767"><a href="#L767">767</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L768"><a href="#L768">768</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L769"><a href="#L769">769</a></th><td class="line-code"><pre><span class="di">void</span> HASH_TRANSFORM (HASH_CTX *c, <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *data)
</pre></td></tr>


<tr><th class="line-num" id="L770"><a href="#L770">770</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L771"><a href="#L771">771</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(HASH_BLOCK_DATA_ORDER_ALIGNED)
</pre></td></tr>


<tr><th class="line-num" id="L772"><a href="#L772">772</a></th><td class="line-code"><pre>        <span class="r">if</span> ((((<span class="pt">unsigned</span> <span class="pt">long</span>)data)%<span class="i">4</span>) == <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L773"><a href="#L773">773</a></th><td class="line-code"><pre>                <span class="c">/* data is properly aligned so that we can cast it: */</span>
</pre></td></tr>


<tr><th class="line-num" id="L774"><a href="#L774">774</a></th><td class="line-code"><pre>                HASH_BLOCK_DATA_ORDER_ALIGNED (c,(HASH_LONG *)data,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L775"><a href="#L775">775</a></th><td class="line-code"><pre>        <span class="r">else</span>
</pre></td></tr>


<tr><th class="line-num" id="L776"><a href="#L776">776</a></th><td class="line-code"><pre><span class="pp">#if</span> !defined(HASH_BLOCK_DATA_ORDER)
</pre></td></tr>


<tr><th class="line-num" id="L777"><a href="#L777">777</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L778"><a href="#L778">778</a></th><td class="line-code"><pre>                mDNSPlatformMemCopy(c-&gt;data,data,HASH_CBLOCK);
</pre></td></tr>


<tr><th class="line-num" id="L779"><a href="#L779">779</a></th><td class="line-code"><pre>                HASH_BLOCK_DATA_ORDER_ALIGNED (c,c-&gt;data,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L780"><a href="#L780">780</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L781"><a href="#L781">781</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L782"><a href="#L782">782</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L783"><a href="#L783">783</a></th><td class="line-code"><pre><span class="pp">#if</span> defined(HASH_BLOCK_DATA_ORDER)
</pre></td></tr>


<tr><th class="line-num" id="L784"><a href="#L784">784</a></th><td class="line-code"><pre>        HASH_BLOCK_DATA_ORDER (c,data,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L785"><a href="#L785">785</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L786"><a href="#L786">786</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L787"><a href="#L787">787</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L788"><a href="#L788">788</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L789"><a href="#L789">789</a></th><td class="line-code"><pre><span class="pt">int</span> HASH_FINAL (<span class="pt">unsigned</span> <span class="pt">char</span> *md, HASH_CTX *c)
</pre></td></tr>


<tr><th class="line-num" id="L790"><a href="#L790">790</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L791"><a href="#L791">791</a></th><td class="line-code"><pre>        <span class="di">register</span> HASH_LONG *p;
</pre></td></tr>


<tr><th class="line-num" id="L792"><a href="#L792">792</a></th><td class="line-code"><pre>        <span class="di">register</span> <span class="pt">unsigned</span> <span class="pt">long</span> l;
</pre></td></tr>


<tr><th class="line-num" id="L793"><a href="#L793">793</a></th><td class="line-code"><pre>        <span class="di">register</span> <span class="pt">int</span> i,j;
</pre></td></tr>


<tr><th class="line-num" id="L794"><a href="#L794">794</a></th><td class="line-code"><pre>        <span class="di">static</span> <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> end[<span class="i">4</span>]={<span class="hx">0x80</span>,<span class="hx">0x00</span>,<span class="hx">0x00</span>,<span class="hx">0x00</span>};
</pre></td></tr>


<tr><th class="line-num" id="L795"><a href="#L795">795</a></th><td class="line-code"><pre>        <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *cp=end;
</pre></td></tr>


<tr><th class="line-num" id="L796"><a href="#L796">796</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L797"><a href="#L797">797</a></th><td class="line-code"><pre>        <span class="c">/* c-&gt;num should definitly have room for at least one more byte. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L798"><a href="#L798">798</a></th><td class="line-code"><pre>        p=c-&gt;data;
</pre></td></tr>


<tr><th class="line-num" id="L799"><a href="#L799">799</a></th><td class="line-code"><pre>        i=c-&gt;num&gt;&gt;<span class="i">2</span>;
</pre></td></tr>


<tr><th class="line-num" id="L800"><a href="#L800">800</a></th><td class="line-code"><pre>        j=c-&gt;num&amp;<span class="hx">0x03</span>;
</pre></td></tr>


<tr><th class="line-num" id="L801"><a href="#L801">801</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L802"><a href="#L802">802</a></th><td class="line-code"><pre><span class="c">#if 0
</pre></td></tr>


<tr><th class="line-num" id="L803"><a href="#L803">803</a></th><td class="line-code"><pre>        /* purify often complains about the following line as an
</pre></td></tr>


<tr><th class="line-num" id="L804"><a href="#L804">804</a></th><td class="line-code"><pre>         * Uninitialized Memory Read.  While this can be true, the
</pre></td></tr>


<tr><th class="line-num" id="L805"><a href="#L805">805</a></th><td class="line-code"><pre>         * following p_c2l macro will reset l when that case is true.
</pre></td></tr>


<tr><th class="line-num" id="L806"><a href="#L806">806</a></th><td class="line-code"><pre>         * This is because j&amp;0x03 contains the number of 'valid' bytes
</pre></td></tr>


<tr><th class="line-num" id="L807"><a href="#L807">807</a></th><td class="line-code"><pre>         * already in p[i].  If and only if j&amp;0x03 == 0, the UMR will
</pre></td></tr>


<tr><th class="line-num" id="L808"><a href="#L808">808</a></th><td class="line-code"><pre>         * occur but this is also the only time p_c2l will do
</pre></td></tr>


<tr><th class="line-num" id="L809"><a href="#L809">809</a></th><td class="line-code"><pre>         * l= *(cp++) instead of l|= *(cp++)
</pre></td></tr>


<tr><th class="line-num" id="L810"><a href="#L810">810</a></th><td class="line-code"><pre>         * Many thanks to Alex Tang &lt;altitude@cic.net&gt; for pickup this
</pre></td></tr>


<tr><th class="line-num" id="L811"><a href="#L811">811</a></th><td class="line-code"><pre>         * 'potential bug' */
</pre></td></tr>


<tr><th class="line-num" id="L812"><a href="#L812">812</a></th><td class="line-code"><pre>#ifdef PURIFY
</pre></td></tr>


<tr><th class="line-num" id="L813"><a href="#L813">813</a></th><td class="line-code"><pre>        if (j==0) p[i]=0; /* Yeah, but that's not the way to fix it:-) */
</pre></td></tr>


<tr><th class="line-num" id="L814"><a href="#L814">814</a></th><td class="line-code"><pre>#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L815"><a href="#L815">815</a></th><td class="line-code"><pre>        l=p[i];
</pre></td></tr>


<tr><th class="line-num" id="L816"><a href="#L816">816</a></th><td class="line-code"><pre><span class="pp">#else</span>
</pre></td></tr>


<tr><th class="line-num" id="L817"><a href="#L817">817</a></th><td class="line-code"><pre>        l = (j==<span class="i">0</span>) ? <span class="i">0</span> : p[i];
</pre></td></tr>


<tr><th class="line-num" id="L818"><a href="#L818">818</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L819"><a href="#L819">819</a></th><td class="line-code"><pre>        HOST_p_c2l(cp,l,j); p[i++]=l; <span class="c">/* i is the next 'undefined word' */</span>
</pre></td></tr>


<tr><th class="line-num" id="L820"><a href="#L820">820</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L821"><a href="#L821">821</a></th><td class="line-code"><pre>        <span class="r">if</span> (i&gt;(HASH_LBLOCK-<span class="i">2</span>)) <span class="c">/* save room for Nl and Nh */</span>
</pre></td></tr>


<tr><th class="line-num" id="L822"><a href="#L822">822</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L823"><a href="#L823">823</a></th><td class="line-code"><pre>                <span class="r">if</span> (i&lt;HASH_LBLOCK) p[i]=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L824"><a href="#L824">824</a></th><td class="line-code"><pre>                HASH_BLOCK_HOST_ORDER (c,p,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L825"><a href="#L825">825</a></th><td class="line-code"><pre>                i=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L826"><a href="#L826">826</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L827"><a href="#L827">827</a></th><td class="line-code"><pre>        <span class="r">for</span> (; i&lt;(HASH_LBLOCK-<span class="i">2</span>); i++)
</pre></td></tr>


<tr><th class="line-num" id="L828"><a href="#L828">828</a></th><td class="line-code"><pre>                p[i]=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L829"><a href="#L829">829</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L830"><a href="#L830">830</a></th><td class="line-code"><pre><span class="pp">#if</span>   defined(DATA_ORDER_IS_BIG_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L831"><a href="#L831">831</a></th><td class="line-code"><pre>        p[HASH_LBLOCK-<span class="i">2</span>]=c-&gt;Nh;
</pre></td></tr>


<tr><th class="line-num" id="L832"><a href="#L832">832</a></th><td class="line-code"><pre>        p[HASH_LBLOCK-<span class="i">1</span>]=c-&gt;Nl;
</pre></td></tr>


<tr><th class="line-num" id="L833"><a href="#L833">833</a></th><td class="line-code"><pre><span class="pp">#elif</span> defined(DATA_ORDER_IS_LITTLE_ENDIAN)
</pre></td></tr>


<tr><th class="line-num" id="L834"><a href="#L834">834</a></th><td class="line-code"><pre>        p[HASH_LBLOCK-<span class="i">2</span>]=c-&gt;Nl;
</pre></td></tr>


<tr><th class="line-num" id="L835"><a href="#L835">835</a></th><td class="line-code"><pre>        p[HASH_LBLOCK-<span class="i">1</span>]=c-&gt;Nh;
</pre></td></tr>


<tr><th class="line-num" id="L836"><a href="#L836">836</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L837"><a href="#L837">837</a></th><td class="line-code"><pre>        HASH_BLOCK_HOST_ORDER (c,p,<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L838"><a href="#L838">838</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L839"><a href="#L839">839</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> HASH_MAKE_STRING
</pre></td></tr>


<tr><th class="line-num" id="L840"><a href="#L840">840</a></th><td class="line-code"><pre><span class="pp">#error</span> <span class="s"><span class="dl">&quot;</span><span class="k">HASH_MAKE_STRING must be defined!</span><span class="dl">&quot;</span></span>
</pre></td></tr>


<tr><th class="line-num" id="L841"><a href="#L841">841</a></th><td class="line-code"><pre><span class="pp">#else</span>
</pre></td></tr>


<tr><th class="line-num" id="L842"><a href="#L842">842</a></th><td class="line-code"><pre>        HASH_MAKE_STRING(c,md);
</pre></td></tr>


<tr><th class="line-num" id="L843"><a href="#L843">843</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L844"><a href="#L844">844</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L845"><a href="#L845">845</a></th><td class="line-code"><pre>        c-&gt;num=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L846"><a href="#L846">846</a></th><td class="line-code"><pre>        <span class="c">/* clear stuff, HASH_BLOCK may be leaving some stuff on the stack
</pre></td></tr>


<tr><th class="line-num" id="L847"><a href="#L847">847</a></th><td class="line-code"><pre>         * but I'm not worried :-)
</pre></td></tr>


<tr><th class="line-num" id="L848"><a href="#L848">848</a></th><td class="line-code"><pre>        OPENSSL_cleanse((void *)c,sizeof(HASH_CTX));
</pre></td></tr>


<tr><th class="line-num" id="L849"><a href="#L849">849</a></th><td class="line-code"><pre>         */</span>
</pre></td></tr>


<tr><th class="line-num" id="L850"><a href="#L850">850</a></th><td class="line-code"><pre>        <span class="r">return</span> <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L851"><a href="#L851">851</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L852"><a href="#L852">852</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L853"><a href="#L853">853</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> MD32_REG_T
</pre></td></tr>


<tr><th class="line-num" id="L854"><a href="#L854">854</a></th><td class="line-code"><pre><span class="pp">#define</span> MD32_REG_T <span class="pt">long</span>
</pre></td></tr>


<tr><th class="line-num" id="L855"><a href="#L855">855</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L856"><a href="#L856">856</a></th><td class="line-code"><pre> * This comment was originaly written for MD5, which is why it
</pre></td></tr>


<tr><th class="line-num" id="L857"><a href="#L857">857</a></th><td class="line-code"><pre> * discusses A-D. But it basically applies to all 32-bit digests,
</pre></td></tr>


<tr><th class="line-num" id="L858"><a href="#L858">858</a></th><td class="line-code"><pre> * which is why it was moved to common header file.
</pre></td></tr>


<tr><th class="line-num" id="L859"><a href="#L859">859</a></th><td class="line-code"><pre> *
</pre></td></tr>


<tr><th class="line-num" id="L860"><a href="#L860">860</a></th><td class="line-code"><pre> * In case you wonder why A-D are declared as long and not
</pre></td></tr>


<tr><th class="line-num" id="L861"><a href="#L861">861</a></th><td class="line-code"><pre> * as mDNSu32. Doing so results in slight performance
</pre></td></tr>


<tr><th class="line-num" id="L862"><a href="#L862">862</a></th><td class="line-code"><pre> * boost on LP64 architectures. The catch is we don't
</pre></td></tr>


<tr><th class="line-num" id="L863"><a href="#L863">863</a></th><td class="line-code"><pre> * really care if 32 MSBs of a 64-bit register get polluted
</pre></td></tr>


<tr><th class="line-num" id="L864"><a href="#L864">864</a></th><td class="line-code"><pre> * with eventual overflows as we *save* only 32 LSBs in
</pre></td></tr>


<tr><th class="line-num" id="L865"><a href="#L865">865</a></th><td class="line-code"><pre> * *either* case. Now declaring 'em long excuses the compiler
</pre></td></tr>


<tr><th class="line-num" id="L866"><a href="#L866">866</a></th><td class="line-code"><pre> * from keeping 32 MSBs zeroed resulting in 13% performance
</pre></td></tr>


<tr><th class="line-num" id="L867"><a href="#L867">867</a></th><td class="line-code"><pre> * improvement under SPARC Solaris7/64 and 5% under AlphaLinux.
</pre></td></tr>


<tr><th class="line-num" id="L868"><a href="#L868">868</a></th><td class="line-code"><pre> * Well, to be honest it should say that this *prevents* 
</pre></td></tr>


<tr><th class="line-num" id="L869"><a href="#L869">869</a></th><td class="line-code"><pre> * performance degradation.
</pre></td></tr>


<tr><th class="line-num" id="L870"><a href="#L870">870</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L871"><a href="#L871">871</a></th><td class="line-code"><pre> * Apparently there're LP64 compilers that generate better
</pre></td></tr>


<tr><th class="line-num" id="L872"><a href="#L872">872</a></th><td class="line-code"><pre> * code if A-D are declared int. Most notably GCC-x86_64
</pre></td></tr>


<tr><th class="line-num" id="L873"><a href="#L873">873</a></th><td class="line-code"><pre> * generates better code.
</pre></td></tr>


<tr><th class="line-num" id="L874"><a href="#L874">874</a></th><td class="line-code"><pre> *                                &lt;appro@fy.chalmers.se&gt;
</pre></td></tr>


<tr><th class="line-num" id="L875"><a href="#L875">875</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L876"><a href="#L876">876</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L877"><a href="#L877">877</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L878"><a href="#L878">878</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L879"><a href="#L879">879</a></th><td class="line-code"><pre><span class="c">// from md5_locl.h (continued)</span>
</pre></td></tr>


<tr><th class="line-num" id="L880"><a href="#L880">880</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L881"><a href="#L881">881</a></th><td class="line-code"><pre><span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L882"><a href="#L882">882</a></th><td class="line-code"><pre>#define        F(x,y,z)        (((x) &amp; (y))  |  ((~(x)) &amp; (z)))
</pre></td></tr>


<tr><th class="line-num" id="L883"><a href="#L883">883</a></th><td class="line-code"><pre>#define        G(x,y,z)        (((x) &amp; (z))  |  ((y) &amp; (~(z))))
</pre></td></tr>


<tr><th class="line-num" id="L884"><a href="#L884">884</a></th><td class="line-code"><pre>*/</span>
</pre></td></tr>


<tr><th class="line-num" id="L885"><a href="#L885">885</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L886"><a href="#L886">886</a></th><td class="line-code"><pre><span class="c">/* As pointed out by Wei Dai &lt;weidai@eskimo.com&gt;, the above can be
</pre></td></tr>


<tr><th class="line-num" id="L887"><a href="#L887">887</a></th><td class="line-code"><pre> * simplified to the code below.  Wei attributes these optimizations
</pre></td></tr>


<tr><th class="line-num" id="L888"><a href="#L888">888</a></th><td class="line-code"><pre> * to Peter Gutmann's SHS code, and he attributes it to Rich Schroeppel.
</pre></td></tr>


<tr><th class="line-num" id="L889"><a href="#L889">889</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L890"><a href="#L890">890</a></th><td class="line-code"><pre><span class="pp">#define</span>        F(b,c,d)        ((((c) ^ (d)) &amp; (b)) ^ (d))
</pre></td></tr>


<tr><th class="line-num" id="L891"><a href="#L891">891</a></th><td class="line-code"><pre><span class="pp">#define</span>        G(b,c,d)        ((((b) ^ (c)) &amp; (d)) ^ (c))
</pre></td></tr>


<tr><th class="line-num" id="L892"><a href="#L892">892</a></th><td class="line-code"><pre><span class="pp">#define</span>        H(b,c,d)        ((b) ^ (c) ^ (d))
</pre></td></tr>


<tr><th class="line-num" id="L893"><a href="#L893">893</a></th><td class="line-code"><pre><span class="pp">#define</span>        I(b,c,d)        (((~(d)) | (b)) ^ (c))
</pre></td></tr>


<tr><th class="line-num" id="L894"><a href="#L894">894</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L895"><a href="#L895">895</a></th><td class="line-code"><pre><span class="pp">#define</span> R0(a,b,c,d,k,s,t) { \
</pre></td></tr>


<tr><th class="line-num" id="L896"><a href="#L896">896</a></th><td class="line-code"><pre>        a+=((k)+(t)+F((b),(c),(d))); \
</pre></td></tr>


<tr><th class="line-num" id="L897"><a href="#L897">897</a></th><td class="line-code"><pre>        a=ROTATE(a,s); \
</pre></td></tr>


<tr><th class="line-num" id="L898"><a href="#L898">898</a></th><td class="line-code"><pre>        a+=b; };\
</pre></td></tr>


<tr><th class="line-num" id="L899"><a href="#L899">899</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L900"><a href="#L900">900</a></th><td class="line-code"><pre><span class="pp">#define</span> R1(a,b,c,d,k,s,t) { \
</pre></td></tr>


<tr><th class="line-num" id="L901"><a href="#L901">901</a></th><td class="line-code"><pre>        a+=((k)+(t)+G((b),(c),(d))); \
</pre></td></tr>


<tr><th class="line-num" id="L902"><a href="#L902">902</a></th><td class="line-code"><pre>        a=ROTATE(a,s); \
</pre></td></tr>


<tr><th class="line-num" id="L903"><a href="#L903">903</a></th><td class="line-code"><pre>        a+=b; };
</pre></td></tr>


<tr><th class="line-num" id="L904"><a href="#L904">904</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L905"><a href="#L905">905</a></th><td class="line-code"><pre><span class="pp">#define</span> R2(a,b,c,d,k,s,t) { \
</pre></td></tr>


<tr><th class="line-num" id="L906"><a href="#L906">906</a></th><td class="line-code"><pre>        a+=((k)+(t)+H((b),(c),(d))); \
</pre></td></tr>


<tr><th class="line-num" id="L907"><a href="#L907">907</a></th><td class="line-code"><pre>        a=ROTATE(a,s); \
</pre></td></tr>


<tr><th class="line-num" id="L908"><a href="#L908">908</a></th><td class="line-code"><pre>        a+=b; };
</pre></td></tr>


<tr><th class="line-num" id="L909"><a href="#L909">909</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L910"><a href="#L910">910</a></th><td class="line-code"><pre><span class="pp">#define</span> R3(a,b,c,d,k,s,t) { \
</pre></td></tr>


<tr><th class="line-num" id="L911"><a href="#L911">911</a></th><td class="line-code"><pre>        a+=((k)+(t)+I((b),(c),(d))); \
</pre></td></tr>


<tr><th class="line-num" id="L912"><a href="#L912">912</a></th><td class="line-code"><pre>        a=ROTATE(a,s); \
</pre></td></tr>


<tr><th class="line-num" id="L913"><a href="#L913">913</a></th><td class="line-code"><pre>        a+=b; };
</pre></td></tr>


<tr><th class="line-num" id="L914"><a href="#L914">914</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L915"><a href="#L915">915</a></th><td class="line-code"><pre><span class="c">// from md5_dgst.c</span>
</pre></td></tr>


<tr><th class="line-num" id="L916"><a href="#L916">916</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L917"><a href="#L917">917</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L918"><a href="#L918">918</a></th><td class="line-code"><pre><span class="c">/* Implemented from RFC1321 The MD5 Message-Digest Algorithm
</pre></td></tr>


<tr><th class="line-num" id="L919"><a href="#L919">919</a></th><td class="line-code"><pre> */</span>
</pre></td></tr>


<tr><th class="line-num" id="L920"><a href="#L920">920</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L921"><a href="#L921">921</a></th><td class="line-code"><pre><span class="pp">#define</span> INIT_DATA_A (<span class="pt">unsigned</span> <span class="pt">long</span>)<span class="hx">0x67452301</span>L
</pre></td></tr>


<tr><th class="line-num" id="L922"><a href="#L922">922</a></th><td class="line-code"><pre><span class="pp">#define</span> INIT_DATA_B (<span class="pt">unsigned</span> <span class="pt">long</span>)<span class="hx">0xefcdab89</span>L
</pre></td></tr>


<tr><th class="line-num" id="L923"><a href="#L923">923</a></th><td class="line-code"><pre><span class="pp">#define</span> INIT_DATA_C (<span class="pt">unsigned</span> <span class="pt">long</span>)<span class="hx">0x98badcfe</span>L
</pre></td></tr>


<tr><th class="line-num" id="L924"><a href="#L924">924</a></th><td class="line-code"><pre><span class="pp">#define</span> INIT_DATA_D (<span class="pt">unsigned</span> <span class="pt">long</span>)<span class="hx">0x10325476</span>L
</pre></td></tr>


<tr><th class="line-num" id="L925"><a href="#L925">925</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L926"><a href="#L926">926</a></th><td class="line-code"><pre><span class="pt">int</span> MD5_Init(MD5_CTX *c)
</pre></td></tr>


<tr><th class="line-num" id="L927"><a href="#L927">927</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L928"><a href="#L928">928</a></th><td class="line-code"><pre>        c-&gt;A=INIT_DATA_A;
</pre></td></tr>


<tr><th class="line-num" id="L929"><a href="#L929">929</a></th><td class="line-code"><pre>        c-&gt;B=INIT_DATA_B;
</pre></td></tr>


<tr><th class="line-num" id="L930"><a href="#L930">930</a></th><td class="line-code"><pre>        c-&gt;C=INIT_DATA_C;
</pre></td></tr>


<tr><th class="line-num" id="L931"><a href="#L931">931</a></th><td class="line-code"><pre>        c-&gt;D=INIT_DATA_D;
</pre></td></tr>


<tr><th class="line-num" id="L932"><a href="#L932">932</a></th><td class="line-code"><pre>        c-&gt;Nl=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L933"><a href="#L933">933</a></th><td class="line-code"><pre>        c-&gt;Nh=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L934"><a href="#L934">934</a></th><td class="line-code"><pre>        c-&gt;num=<span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L935"><a href="#L935">935</a></th><td class="line-code"><pre>        <span class="r">return</span> <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L936"><a href="#L936">936</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L937"><a href="#L937">937</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L938"><a href="#L938">938</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> md5_block_host_order
</pre></td></tr>


<tr><th class="line-num" id="L939"><a href="#L939">939</a></th><td class="line-code"><pre><span class="di">void</span> md5_block_host_order (MD5_CTX *c, <span class="di">const</span> <span class="di">void</span> *data, <span class="pt">int</span> num)
</pre></td></tr>


<tr><th class="line-num" id="L940"><a href="#L940">940</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L941"><a href="#L941">941</a></th><td class="line-code"><pre>        <span class="di">const</span> mDNSu32 *X=(<span class="di">const</span> mDNSu32 *)data;
</pre></td></tr>


<tr><th class="line-num" id="L942"><a href="#L942">942</a></th><td class="line-code"><pre>        <span class="di">register</span> <span class="pt">unsigned</span> MD32_REG_T A,B,C,D;
</pre></td></tr>


<tr><th class="line-num" id="L943"><a href="#L943">943</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L944"><a href="#L944">944</a></th><td class="line-code"><pre>        A=c-&gt;A;
</pre></td></tr>


<tr><th class="line-num" id="L945"><a href="#L945">945</a></th><td class="line-code"><pre>        B=c-&gt;B;
</pre></td></tr>


<tr><th class="line-num" id="L946"><a href="#L946">946</a></th><td class="line-code"><pre>        C=c-&gt;C;
</pre></td></tr>


<tr><th class="line-num" id="L947"><a href="#L947">947</a></th><td class="line-code"><pre>        D=c-&gt;D;
</pre></td></tr>


<tr><th class="line-num" id="L948"><a href="#L948">948</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L949"><a href="#L949">949</a></th><td class="line-code"><pre>        <span class="r">for</span> (;num--;X+=HASH_LBLOCK)
</pre></td></tr>


<tr><th class="line-num" id="L950"><a href="#L950">950</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L951"><a href="#L951">951</a></th><td class="line-code"><pre>        <span class="c">/* Round 0 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L952"><a href="#L952">952</a></th><td class="line-code"><pre>        R0(A,B,C,D,X[ <span class="i">0</span>], <span class="i">7</span>,<span class="hx">0xd76aa478</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L953"><a href="#L953">953</a></th><td class="line-code"><pre>        R0(D,A,B,C,X[ <span class="i">1</span>],<span class="i">12</span>,<span class="hx">0xe8c7b756</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L954"><a href="#L954">954</a></th><td class="line-code"><pre>        R0(C,D,A,B,X[ <span class="i">2</span>],<span class="i">17</span>,<span class="hx">0x242070db</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L955"><a href="#L955">955</a></th><td class="line-code"><pre>        R0(B,C,D,A,X[ <span class="i">3</span>],<span class="i">22</span>,<span class="hx">0xc1bdceee</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L956"><a href="#L956">956</a></th><td class="line-code"><pre>        R0(A,B,C,D,X[ <span class="i">4</span>], <span class="i">7</span>,<span class="hx">0xf57c0faf</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L957"><a href="#L957">957</a></th><td class="line-code"><pre>        R0(D,A,B,C,X[ <span class="i">5</span>],<span class="i">12</span>,<span class="hx">0x4787c62a</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L958"><a href="#L958">958</a></th><td class="line-code"><pre>        R0(C,D,A,B,X[ <span class="i">6</span>],<span class="i">17</span>,<span class="hx">0xa8304613</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L959"><a href="#L959">959</a></th><td class="line-code"><pre>        R0(B,C,D,A,X[ <span class="i">7</span>],<span class="i">22</span>,<span class="hx">0xfd469501</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L960"><a href="#L960">960</a></th><td class="line-code"><pre>        R0(A,B,C,D,X[ <span class="i">8</span>], <span class="i">7</span>,<span class="hx">0x698098d8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L961"><a href="#L961">961</a></th><td class="line-code"><pre>        R0(D,A,B,C,X[ <span class="i">9</span>],<span class="i">12</span>,<span class="hx">0x8b44f7af</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L962"><a href="#L962">962</a></th><td class="line-code"><pre>        R0(C,D,A,B,X[<span class="i">10</span>],<span class="i">17</span>,<span class="hx">0xffff5bb1</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L963"><a href="#L963">963</a></th><td class="line-code"><pre>        R0(B,C,D,A,X[<span class="i">11</span>],<span class="i">22</span>,<span class="hx">0x895cd7be</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L964"><a href="#L964">964</a></th><td class="line-code"><pre>        R0(A,B,C,D,X[<span class="i">12</span>], <span class="i">7</span>,<span class="hx">0x6b901122</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L965"><a href="#L965">965</a></th><td class="line-code"><pre>        R0(D,A,B,C,X[<span class="i">13</span>],<span class="i">12</span>,<span class="hx">0xfd987193</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L966"><a href="#L966">966</a></th><td class="line-code"><pre>        R0(C,D,A,B,X[<span class="i">14</span>],<span class="i">17</span>,<span class="hx">0xa679438e</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L967"><a href="#L967">967</a></th><td class="line-code"><pre>        R0(B,C,D,A,X[<span class="i">15</span>],<span class="i">22</span>,<span class="hx">0x49b40821</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L968"><a href="#L968">968</a></th><td class="line-code"><pre>        <span class="c">/* Round 1 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L969"><a href="#L969">969</a></th><td class="line-code"><pre>        R1(A,B,C,D,X[ <span class="i">1</span>], <span class="i">5</span>,<span class="hx">0xf61e2562</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L970"><a href="#L970">970</a></th><td class="line-code"><pre>        R1(D,A,B,C,X[ <span class="i">6</span>], <span class="i">9</span>,<span class="hx">0xc040b340</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L971"><a href="#L971">971</a></th><td class="line-code"><pre>        R1(C,D,A,B,X[<span class="i">11</span>],<span class="i">14</span>,<span class="hx">0x265e5a51</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L972"><a href="#L972">972</a></th><td class="line-code"><pre>        R1(B,C,D,A,X[ <span class="i">0</span>],<span class="i">20</span>,<span class="hx">0xe9b6c7aa</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L973"><a href="#L973">973</a></th><td class="line-code"><pre>        R1(A,B,C,D,X[ <span class="i">5</span>], <span class="i">5</span>,<span class="hx">0xd62f105d</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L974"><a href="#L974">974</a></th><td class="line-code"><pre>        R1(D,A,B,C,X[<span class="i">10</span>], <span class="i">9</span>,<span class="hx">0x02441453</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L975"><a href="#L975">975</a></th><td class="line-code"><pre>        R1(C,D,A,B,X[<span class="i">15</span>],<span class="i">14</span>,<span class="hx">0xd8a1e681</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L976"><a href="#L976">976</a></th><td class="line-code"><pre>        R1(B,C,D,A,X[ <span class="i">4</span>],<span class="i">20</span>,<span class="hx">0xe7d3fbc8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L977"><a href="#L977">977</a></th><td class="line-code"><pre>        R1(A,B,C,D,X[ <span class="i">9</span>], <span class="i">5</span>,<span class="hx">0x21e1cde6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L978"><a href="#L978">978</a></th><td class="line-code"><pre>        R1(D,A,B,C,X[<span class="i">14</span>], <span class="i">9</span>,<span class="hx">0xc33707d6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L979"><a href="#L979">979</a></th><td class="line-code"><pre>        R1(C,D,A,B,X[ <span class="i">3</span>],<span class="i">14</span>,<span class="hx">0xf4d50d87</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L980"><a href="#L980">980</a></th><td class="line-code"><pre>        R1(B,C,D,A,X[ <span class="i">8</span>],<span class="i">20</span>,<span class="hx">0x455a14ed</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L981"><a href="#L981">981</a></th><td class="line-code"><pre>        R1(A,B,C,D,X[<span class="i">13</span>], <span class="i">5</span>,<span class="hx">0xa9e3e905</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L982"><a href="#L982">982</a></th><td class="line-code"><pre>        R1(D,A,B,C,X[ <span class="i">2</span>], <span class="i">9</span>,<span class="hx">0xfcefa3f8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L983"><a href="#L983">983</a></th><td class="line-code"><pre>        R1(C,D,A,B,X[ <span class="i">7</span>],<span class="i">14</span>,<span class="hx">0x676f02d9</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L984"><a href="#L984">984</a></th><td class="line-code"><pre>        R1(B,C,D,A,X[<span class="i">12</span>],<span class="i">20</span>,<span class="hx">0x8d2a4c8a</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L985"><a href="#L985">985</a></th><td class="line-code"><pre>        <span class="c">/* Round 2 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L986"><a href="#L986">986</a></th><td class="line-code"><pre>        R2(A,B,C,D,X[ <span class="i">5</span>], <span class="i">4</span>,<span class="hx">0xfffa3942</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L987"><a href="#L987">987</a></th><td class="line-code"><pre>        R2(D,A,B,C,X[ <span class="i">8</span>],<span class="i">11</span>,<span class="hx">0x8771f681</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L988"><a href="#L988">988</a></th><td class="line-code"><pre>        R2(C,D,A,B,X[<span class="i">11</span>],<span class="i">16</span>,<span class="hx">0x6d9d6122</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L989"><a href="#L989">989</a></th><td class="line-code"><pre>        R2(B,C,D,A,X[<span class="i">14</span>],<span class="i">23</span>,<span class="hx">0xfde5380c</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L990"><a href="#L990">990</a></th><td class="line-code"><pre>        R2(A,B,C,D,X[ <span class="i">1</span>], <span class="i">4</span>,<span class="hx">0xa4beea44</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L991"><a href="#L991">991</a></th><td class="line-code"><pre>        R2(D,A,B,C,X[ <span class="i">4</span>],<span class="i">11</span>,<span class="hx">0x4bdecfa9</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L992"><a href="#L992">992</a></th><td class="line-code"><pre>        R2(C,D,A,B,X[ <span class="i">7</span>],<span class="i">16</span>,<span class="hx">0xf6bb4b60</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L993"><a href="#L993">993</a></th><td class="line-code"><pre>        R2(B,C,D,A,X[<span class="i">10</span>],<span class="i">23</span>,<span class="hx">0xbebfbc70</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L994"><a href="#L994">994</a></th><td class="line-code"><pre>        R2(A,B,C,D,X[<span class="i">13</span>], <span class="i">4</span>,<span class="hx">0x289b7ec6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L995"><a href="#L995">995</a></th><td class="line-code"><pre>        R2(D,A,B,C,X[ <span class="i">0</span>],<span class="i">11</span>,<span class="hx">0xeaa127fa</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L996"><a href="#L996">996</a></th><td class="line-code"><pre>        R2(C,D,A,B,X[ <span class="i">3</span>],<span class="i">16</span>,<span class="hx">0xd4ef3085</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L997"><a href="#L997">997</a></th><td class="line-code"><pre>        R2(B,C,D,A,X[ <span class="i">6</span>],<span class="i">23</span>,<span class="hx">0x04881d05</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L998"><a href="#L998">998</a></th><td class="line-code"><pre>        R2(A,B,C,D,X[ <span class="i">9</span>], <span class="i">4</span>,<span class="hx">0xd9d4d039</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L999"><a href="#L999">999</a></th><td class="line-code"><pre>        R2(D,A,B,C,X[<span class="i">12</span>],<span class="i">11</span>,<span class="hx">0xe6db99e5</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1000"><a href="#L1000">1000</a></th><td class="line-code"><pre>        R2(C,D,A,B,X[<span class="i">15</span>],<span class="i">16</span>,<span class="hx">0x1fa27cf8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1001"><a href="#L1001">1001</a></th><td class="line-code"><pre>        R2(B,C,D,A,X[ <span class="i">2</span>],<span class="i">23</span>,<span class="hx">0xc4ac5665</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1002"><a href="#L1002">1002</a></th><td class="line-code"><pre>        <span class="c">/* Round 3 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1003"><a href="#L1003">1003</a></th><td class="line-code"><pre>        R3(A,B,C,D,X[ <span class="i">0</span>], <span class="i">6</span>,<span class="hx">0xf4292244</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1004"><a href="#L1004">1004</a></th><td class="line-code"><pre>        R3(D,A,B,C,X[ <span class="i">7</span>],<span class="i">10</span>,<span class="hx">0x432aff97</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1005"><a href="#L1005">1005</a></th><td class="line-code"><pre>        R3(C,D,A,B,X[<span class="i">14</span>],<span class="i">15</span>,<span class="hx">0xab9423a7</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1006"><a href="#L1006">1006</a></th><td class="line-code"><pre>        R3(B,C,D,A,X[ <span class="i">5</span>],<span class="i">21</span>,<span class="hx">0xfc93a039</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1007"><a href="#L1007">1007</a></th><td class="line-code"><pre>        R3(A,B,C,D,X[<span class="i">12</span>], <span class="i">6</span>,<span class="hx">0x655b59c3</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1008"><a href="#L1008">1008</a></th><td class="line-code"><pre>        R3(D,A,B,C,X[ <span class="i">3</span>],<span class="i">10</span>,<span class="hx">0x8f0ccc92</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1009"><a href="#L1009">1009</a></th><td class="line-code"><pre>        R3(C,D,A,B,X[<span class="i">10</span>],<span class="i">15</span>,<span class="hx">0xffeff47d</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1010"><a href="#L1010">1010</a></th><td class="line-code"><pre>        R3(B,C,D,A,X[ <span class="i">1</span>],<span class="i">21</span>,<span class="hx">0x85845dd1</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1011"><a href="#L1011">1011</a></th><td class="line-code"><pre>        R3(A,B,C,D,X[ <span class="i">8</span>], <span class="i">6</span>,<span class="hx">0x6fa87e4f</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1012"><a href="#L1012">1012</a></th><td class="line-code"><pre>        R3(D,A,B,C,X[<span class="i">15</span>],<span class="i">10</span>,<span class="hx">0xfe2ce6e0</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1013"><a href="#L1013">1013</a></th><td class="line-code"><pre>        R3(C,D,A,B,X[ <span class="i">6</span>],<span class="i">15</span>,<span class="hx">0xa3014314</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1014"><a href="#L1014">1014</a></th><td class="line-code"><pre>        R3(B,C,D,A,X[<span class="i">13</span>],<span class="i">21</span>,<span class="hx">0x4e0811a1</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1015"><a href="#L1015">1015</a></th><td class="line-code"><pre>        R3(A,B,C,D,X[ <span class="i">4</span>], <span class="i">6</span>,<span class="hx">0xf7537e82</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1016"><a href="#L1016">1016</a></th><td class="line-code"><pre>        R3(D,A,B,C,X[<span class="i">11</span>],<span class="i">10</span>,<span class="hx">0xbd3af235</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1017"><a href="#L1017">1017</a></th><td class="line-code"><pre>        R3(C,D,A,B,X[ <span class="i">2</span>],<span class="i">15</span>,<span class="hx">0x2ad7d2bb</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1018"><a href="#L1018">1018</a></th><td class="line-code"><pre>        R3(B,C,D,A,X[ <span class="i">9</span>],<span class="i">21</span>,<span class="hx">0xeb86d391</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1019"><a href="#L1019">1019</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1020"><a href="#L1020">1020</a></th><td class="line-code"><pre>        A = c-&gt;A += A;
</pre></td></tr>


<tr><th class="line-num" id="L1021"><a href="#L1021">1021</a></th><td class="line-code"><pre>        B = c-&gt;B += B;
</pre></td></tr>


<tr><th class="line-num" id="L1022"><a href="#L1022">1022</a></th><td class="line-code"><pre>        C = c-&gt;C += C;
</pre></td></tr>


<tr><th class="line-num" id="L1023"><a href="#L1023">1023</a></th><td class="line-code"><pre>        D = c-&gt;D += D;
</pre></td></tr>


<tr><th class="line-num" id="L1024"><a href="#L1024">1024</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1025"><a href="#L1025">1025</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1026"><a href="#L1026">1026</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1027"><a href="#L1027">1027</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1028"><a href="#L1028">1028</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> md5_block_data_order
</pre></td></tr>


<tr><th class="line-num" id="L1029"><a href="#L1029">1029</a></th><td class="line-code"><pre><span class="pp">#ifdef</span> X
</pre></td></tr>


<tr><th class="line-num" id="L1030"><a href="#L1030">1030</a></th><td class="line-code"><pre><span class="pp">#undef</span> X
</pre></td></tr>


<tr><th class="line-num" id="L1031"><a href="#L1031">1031</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1032"><a href="#L1032">1032</a></th><td class="line-code"><pre><span class="di">void</span> md5_block_data_order (MD5_CTX *c, <span class="di">const</span> <span class="di">void</span> *data_, <span class="pt">int</span> num)
</pre></td></tr>


<tr><th class="line-num" id="L1033"><a href="#L1033">1033</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1034"><a href="#L1034">1034</a></th><td class="line-code"><pre>        <span class="di">const</span> <span class="pt">unsigned</span> <span class="pt">char</span> *data=data_;
</pre></td></tr>


<tr><th class="line-num" id="L1035"><a href="#L1035">1035</a></th><td class="line-code"><pre>        <span class="di">register</span> <span class="pt">unsigned</span> MD32_REG_T A,B,C,D,l;
</pre></td></tr>


<tr><th class="line-num" id="L1036"><a href="#L1036">1036</a></th><td class="line-code"><pre><span class="pp">#ifndef</span> MD32_XARRAY
</pre></td></tr>


<tr><th class="line-num" id="L1037"><a href="#L1037">1037</a></th><td class="line-code"><pre>        <span class="c">/* See comment in crypto/sha/sha_locl.h for details. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1038"><a href="#L1038">1038</a></th><td class="line-code"><pre>        <span class="pt">unsigned</span> MD32_REG_T        XX0, XX1, XX2, XX3, XX4, XX5, XX6, XX7,
</pre></td></tr>


<tr><th class="line-num" id="L1039"><a href="#L1039">1039</a></th><td class="line-code"><pre>                                XX8, XX9,XX10,XX11,XX12,XX13,XX14,XX15;
</pre></td></tr>


<tr><th class="line-num" id="L1040"><a href="#L1040">1040</a></th><td class="line-code"><pre><span class="pp"># define</span> X(i)        XX<span class="pp">#</span><span class="pp">#i</span>
</pre></td></tr>


<tr><th class="line-num" id="L1041"><a href="#L1041">1041</a></th><td class="line-code"><pre><span class="pp">#else</span>
</pre></td></tr>


<tr><th class="line-num" id="L1042"><a href="#L1042">1042</a></th><td class="line-code"><pre>        mDNSu32 XX[MD5_LBLOCK];
</pre></td></tr>


<tr><th class="line-num" id="L1043"><a href="#L1043">1043</a></th><td class="line-code"><pre><span class="pp"># define</span> X(i)        XX[i]
</pre></td></tr>


<tr><th class="line-num" id="L1044"><a href="#L1044">1044</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1045"><a href="#L1045">1045</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1046"><a href="#L1046">1046</a></th><td class="line-code"><pre>        A=c-&gt;A;
</pre></td></tr>


<tr><th class="line-num" id="L1047"><a href="#L1047">1047</a></th><td class="line-code"><pre>        B=c-&gt;B;
</pre></td></tr>


<tr><th class="line-num" id="L1048"><a href="#L1048">1048</a></th><td class="line-code"><pre>        C=c-&gt;C;
</pre></td></tr>


<tr><th class="line-num" id="L1049"><a href="#L1049">1049</a></th><td class="line-code"><pre>        D=c-&gt;D;
</pre></td></tr>


<tr><th class="line-num" id="L1050"><a href="#L1050">1050</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1051"><a href="#L1051">1051</a></th><td class="line-code"><pre>        <span class="r">for</span> (;num--;)
</pre></td></tr>


<tr><th class="line-num" id="L1052"><a href="#L1052">1052</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1053"><a href="#L1053">1053</a></th><td class="line-code"><pre>        HOST_c2l(data,l); X( <span class="i">0</span>)=l;                HOST_c2l(data,l); X( <span class="i">1</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1054"><a href="#L1054">1054</a></th><td class="line-code"><pre>        <span class="c">/* Round 0 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1055"><a href="#L1055">1055</a></th><td class="line-code"><pre>        R0(A,B,C,D,X( <span class="i">0</span>), <span class="i">7</span>,<span class="hx">0xd76aa478</span>L);        HOST_c2l(data,l); X( <span class="i">2</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1056"><a href="#L1056">1056</a></th><td class="line-code"><pre>        R0(D,A,B,C,X( <span class="i">1</span>),<span class="i">12</span>,<span class="hx">0xe8c7b756</span>L);        HOST_c2l(data,l); X( <span class="i">3</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1057"><a href="#L1057">1057</a></th><td class="line-code"><pre>        R0(C,D,A,B,X( <span class="i">2</span>),<span class="i">17</span>,<span class="hx">0x242070db</span>L);        HOST_c2l(data,l); X( <span class="i">4</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1058"><a href="#L1058">1058</a></th><td class="line-code"><pre>        R0(B,C,D,A,X( <span class="i">3</span>),<span class="i">22</span>,<span class="hx">0xc1bdceee</span>L);        HOST_c2l(data,l); X( <span class="i">5</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1059"><a href="#L1059">1059</a></th><td class="line-code"><pre>        R0(A,B,C,D,X( <span class="i">4</span>), <span class="i">7</span>,<span class="hx">0xf57c0faf</span>L);        HOST_c2l(data,l); X( <span class="i">6</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1060"><a href="#L1060">1060</a></th><td class="line-code"><pre>        R0(D,A,B,C,X( <span class="i">5</span>),<span class="i">12</span>,<span class="hx">0x4787c62a</span>L);        HOST_c2l(data,l); X( <span class="i">7</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1061"><a href="#L1061">1061</a></th><td class="line-code"><pre>        R0(C,D,A,B,X( <span class="i">6</span>),<span class="i">17</span>,<span class="hx">0xa8304613</span>L);        HOST_c2l(data,l); X( <span class="i">8</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1062"><a href="#L1062">1062</a></th><td class="line-code"><pre>        R0(B,C,D,A,X( <span class="i">7</span>),<span class="i">22</span>,<span class="hx">0xfd469501</span>L);        HOST_c2l(data,l); X( <span class="i">9</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1063"><a href="#L1063">1063</a></th><td class="line-code"><pre>        R0(A,B,C,D,X( <span class="i">8</span>), <span class="i">7</span>,<span class="hx">0x698098d8</span>L);        HOST_c2l(data,l); X(<span class="i">10</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1064"><a href="#L1064">1064</a></th><td class="line-code"><pre>        R0(D,A,B,C,X( <span class="i">9</span>),<span class="i">12</span>,<span class="hx">0x8b44f7af</span>L);        HOST_c2l(data,l); X(<span class="i">11</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1065"><a href="#L1065">1065</a></th><td class="line-code"><pre>        R0(C,D,A,B,X(<span class="i">10</span>),<span class="i">17</span>,<span class="hx">0xffff5bb1</span>L);        HOST_c2l(data,l); X(<span class="i">12</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1066"><a href="#L1066">1066</a></th><td class="line-code"><pre>        R0(B,C,D,A,X(<span class="i">11</span>),<span class="i">22</span>,<span class="hx">0x895cd7be</span>L);        HOST_c2l(data,l); X(<span class="i">13</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1067"><a href="#L1067">1067</a></th><td class="line-code"><pre>        R0(A,B,C,D,X(<span class="i">12</span>), <span class="i">7</span>,<span class="hx">0x6b901122</span>L);        HOST_c2l(data,l); X(<span class="i">14</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1068"><a href="#L1068">1068</a></th><td class="line-code"><pre>        R0(D,A,B,C,X(<span class="i">13</span>),<span class="i">12</span>,<span class="hx">0xfd987193</span>L);        HOST_c2l(data,l); X(<span class="i">15</span>)=l;
</pre></td></tr>


<tr><th class="line-num" id="L1069"><a href="#L1069">1069</a></th><td class="line-code"><pre>        R0(C,D,A,B,X(<span class="i">14</span>),<span class="i">17</span>,<span class="hx">0xa679438e</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1070"><a href="#L1070">1070</a></th><td class="line-code"><pre>        R0(B,C,D,A,X(<span class="i">15</span>),<span class="i">22</span>,<span class="hx">0x49b40821</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1071"><a href="#L1071">1071</a></th><td class="line-code"><pre>        <span class="c">/* Round 1 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1072"><a href="#L1072">1072</a></th><td class="line-code"><pre>        R1(A,B,C,D,X( <span class="i">1</span>), <span class="i">5</span>,<span class="hx">0xf61e2562</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1073"><a href="#L1073">1073</a></th><td class="line-code"><pre>        R1(D,A,B,C,X( <span class="i">6</span>), <span class="i">9</span>,<span class="hx">0xc040b340</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1074"><a href="#L1074">1074</a></th><td class="line-code"><pre>        R1(C,D,A,B,X(<span class="i">11</span>),<span class="i">14</span>,<span class="hx">0x265e5a51</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1075"><a href="#L1075">1075</a></th><td class="line-code"><pre>        R1(B,C,D,A,X( <span class="i">0</span>),<span class="i">20</span>,<span class="hx">0xe9b6c7aa</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1076"><a href="#L1076">1076</a></th><td class="line-code"><pre>        R1(A,B,C,D,X( <span class="i">5</span>), <span class="i">5</span>,<span class="hx">0xd62f105d</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1077"><a href="#L1077">1077</a></th><td class="line-code"><pre>        R1(D,A,B,C,X(<span class="i">10</span>), <span class="i">9</span>,<span class="hx">0x02441453</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1078"><a href="#L1078">1078</a></th><td class="line-code"><pre>        R1(C,D,A,B,X(<span class="i">15</span>),<span class="i">14</span>,<span class="hx">0xd8a1e681</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1079"><a href="#L1079">1079</a></th><td class="line-code"><pre>        R1(B,C,D,A,X( <span class="i">4</span>),<span class="i">20</span>,<span class="hx">0xe7d3fbc8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1080"><a href="#L1080">1080</a></th><td class="line-code"><pre>        R1(A,B,C,D,X( <span class="i">9</span>), <span class="i">5</span>,<span class="hx">0x21e1cde6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1081"><a href="#L1081">1081</a></th><td class="line-code"><pre>        R1(D,A,B,C,X(<span class="i">14</span>), <span class="i">9</span>,<span class="hx">0xc33707d6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1082"><a href="#L1082">1082</a></th><td class="line-code"><pre>        R1(C,D,A,B,X( <span class="i">3</span>),<span class="i">14</span>,<span class="hx">0xf4d50d87</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1083"><a href="#L1083">1083</a></th><td class="line-code"><pre>        R1(B,C,D,A,X( <span class="i">8</span>),<span class="i">20</span>,<span class="hx">0x455a14ed</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1084"><a href="#L1084">1084</a></th><td class="line-code"><pre>        R1(A,B,C,D,X(<span class="i">13</span>), <span class="i">5</span>,<span class="hx">0xa9e3e905</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1085"><a href="#L1085">1085</a></th><td class="line-code"><pre>        R1(D,A,B,C,X( <span class="i">2</span>), <span class="i">9</span>,<span class="hx">0xfcefa3f8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1086"><a href="#L1086">1086</a></th><td class="line-code"><pre>        R1(C,D,A,B,X( <span class="i">7</span>),<span class="i">14</span>,<span class="hx">0x676f02d9</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1087"><a href="#L1087">1087</a></th><td class="line-code"><pre>        R1(B,C,D,A,X(<span class="i">12</span>),<span class="i">20</span>,<span class="hx">0x8d2a4c8a</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1088"><a href="#L1088">1088</a></th><td class="line-code"><pre>        <span class="c">/* Round 2 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1089"><a href="#L1089">1089</a></th><td class="line-code"><pre>        R2(A,B,C,D,X( <span class="i">5</span>), <span class="i">4</span>,<span class="hx">0xfffa3942</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1090"><a href="#L1090">1090</a></th><td class="line-code"><pre>        R2(D,A,B,C,X( <span class="i">8</span>),<span class="i">11</span>,<span class="hx">0x8771f681</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1091"><a href="#L1091">1091</a></th><td class="line-code"><pre>        R2(C,D,A,B,X(<span class="i">11</span>),<span class="i">16</span>,<span class="hx">0x6d9d6122</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1092"><a href="#L1092">1092</a></th><td class="line-code"><pre>        R2(B,C,D,A,X(<span class="i">14</span>),<span class="i">23</span>,<span class="hx">0xfde5380c</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1093"><a href="#L1093">1093</a></th><td class="line-code"><pre>        R2(A,B,C,D,X( <span class="i">1</span>), <span class="i">4</span>,<span class="hx">0xa4beea44</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1094"><a href="#L1094">1094</a></th><td class="line-code"><pre>        R2(D,A,B,C,X( <span class="i">4</span>),<span class="i">11</span>,<span class="hx">0x4bdecfa9</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1095"><a href="#L1095">1095</a></th><td class="line-code"><pre>        R2(C,D,A,B,X( <span class="i">7</span>),<span class="i">16</span>,<span class="hx">0xf6bb4b60</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1096"><a href="#L1096">1096</a></th><td class="line-code"><pre>        R2(B,C,D,A,X(<span class="i">10</span>),<span class="i">23</span>,<span class="hx">0xbebfbc70</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1097"><a href="#L1097">1097</a></th><td class="line-code"><pre>        R2(A,B,C,D,X(<span class="i">13</span>), <span class="i">4</span>,<span class="hx">0x289b7ec6</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1098"><a href="#L1098">1098</a></th><td class="line-code"><pre>        R2(D,A,B,C,X( <span class="i">0</span>),<span class="i">11</span>,<span class="hx">0xeaa127fa</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1099"><a href="#L1099">1099</a></th><td class="line-code"><pre>        R2(C,D,A,B,X( <span class="i">3</span>),<span class="i">16</span>,<span class="hx">0xd4ef3085</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1100"><a href="#L1100">1100</a></th><td class="line-code"><pre>        R2(B,C,D,A,X( <span class="i">6</span>),<span class="i">23</span>,<span class="hx">0x04881d05</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1101"><a href="#L1101">1101</a></th><td class="line-code"><pre>        R2(A,B,C,D,X( <span class="i">9</span>), <span class="i">4</span>,<span class="hx">0xd9d4d039</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1102"><a href="#L1102">1102</a></th><td class="line-code"><pre>        R2(D,A,B,C,X(<span class="i">12</span>),<span class="i">11</span>,<span class="hx">0xe6db99e5</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1103"><a href="#L1103">1103</a></th><td class="line-code"><pre>        R2(C,D,A,B,X(<span class="i">15</span>),<span class="i">16</span>,<span class="hx">0x1fa27cf8</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1104"><a href="#L1104">1104</a></th><td class="line-code"><pre>        R2(B,C,D,A,X( <span class="i">2</span>),<span class="i">23</span>,<span class="hx">0xc4ac5665</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1105"><a href="#L1105">1105</a></th><td class="line-code"><pre>        <span class="c">/* Round 3 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1106"><a href="#L1106">1106</a></th><td class="line-code"><pre>        R3(A,B,C,D,X( <span class="i">0</span>), <span class="i">6</span>,<span class="hx">0xf4292244</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1107"><a href="#L1107">1107</a></th><td class="line-code"><pre>        R3(D,A,B,C,X( <span class="i">7</span>),<span class="i">10</span>,<span class="hx">0x432aff97</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1108"><a href="#L1108">1108</a></th><td class="line-code"><pre>        R3(C,D,A,B,X(<span class="i">14</span>),<span class="i">15</span>,<span class="hx">0xab9423a7</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1109"><a href="#L1109">1109</a></th><td class="line-code"><pre>        R3(B,C,D,A,X( <span class="i">5</span>),<span class="i">21</span>,<span class="hx">0xfc93a039</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1110"><a href="#L1110">1110</a></th><td class="line-code"><pre>        R3(A,B,C,D,X(<span class="i">12</span>), <span class="i">6</span>,<span class="hx">0x655b59c3</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1111"><a href="#L1111">1111</a></th><td class="line-code"><pre>        R3(D,A,B,C,X( <span class="i">3</span>),<span class="i">10</span>,<span class="hx">0x8f0ccc92</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1112"><a href="#L1112">1112</a></th><td class="line-code"><pre>        R3(C,D,A,B,X(<span class="i">10</span>),<span class="i">15</span>,<span class="hx">0xffeff47d</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1113"><a href="#L1113">1113</a></th><td class="line-code"><pre>        R3(B,C,D,A,X( <span class="i">1</span>),<span class="i">21</span>,<span class="hx">0x85845dd1</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1114"><a href="#L1114">1114</a></th><td class="line-code"><pre>        R3(A,B,C,D,X( <span class="i">8</span>), <span class="i">6</span>,<span class="hx">0x6fa87e4f</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1115"><a href="#L1115">1115</a></th><td class="line-code"><pre>        R3(D,A,B,C,X(<span class="i">15</span>),<span class="i">10</span>,<span class="hx">0xfe2ce6e0</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1116"><a href="#L1116">1116</a></th><td class="line-code"><pre>        R3(C,D,A,B,X( <span class="i">6</span>),<span class="i">15</span>,<span class="hx">0xa3014314</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1117"><a href="#L1117">1117</a></th><td class="line-code"><pre>        R3(B,C,D,A,X(<span class="i">13</span>),<span class="i">21</span>,<span class="hx">0x4e0811a1</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1118"><a href="#L1118">1118</a></th><td class="line-code"><pre>        R3(A,B,C,D,X( <span class="i">4</span>), <span class="i">6</span>,<span class="hx">0xf7537e82</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1119"><a href="#L1119">1119</a></th><td class="line-code"><pre>        R3(D,A,B,C,X(<span class="i">11</span>),<span class="i">10</span>,<span class="hx">0xbd3af235</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1120"><a href="#L1120">1120</a></th><td class="line-code"><pre>        R3(C,D,A,B,X( <span class="i">2</span>),<span class="i">15</span>,<span class="hx">0x2ad7d2bb</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1121"><a href="#L1121">1121</a></th><td class="line-code"><pre>        R3(B,C,D,A,X( <span class="i">9</span>),<span class="i">21</span>,<span class="hx">0xeb86d391</span>L);
</pre></td></tr>


<tr><th class="line-num" id="L1122"><a href="#L1122">1122</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1123"><a href="#L1123">1123</a></th><td class="line-code"><pre>        A = c-&gt;A += A;
</pre></td></tr>


<tr><th class="line-num" id="L1124"><a href="#L1124">1124</a></th><td class="line-code"><pre>        B = c-&gt;B += B;
</pre></td></tr>


<tr><th class="line-num" id="L1125"><a href="#L1125">1125</a></th><td class="line-code"><pre>        C = c-&gt;C += C;
</pre></td></tr>


<tr><th class="line-num" id="L1126"><a href="#L1126">1126</a></th><td class="line-code"><pre>        D = c-&gt;D += D;
</pre></td></tr>


<tr><th class="line-num" id="L1127"><a href="#L1127">1127</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1128"><a href="#L1128">1128</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1129"><a href="#L1129">1129</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1130"><a href="#L1130">1130</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1131"><a href="#L1131">1131</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1132"><a href="#L1132">1132</a></th><td class="line-code"><pre> <span class="c">// ***************************************************************************</span>
</pre></td></tr>


<tr><th class="line-num" id="L1133"><a href="#L1133">1133</a></th><td class="line-code"><pre><span class="pp">#if</span> COMPILER_LIKES_PRAGMA_MARK
</pre></td></tr>


<tr><th class="line-num" id="L1134"><a href="#L1134">1134</a></th><td class="line-code"><pre><span class="pp">#pragma</span> mark - base64 -&gt; binary conversion
</pre></td></tr>


<tr><th class="line-num" id="L1135"><a href="#L1135">1135</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1136"><a href="#L1136">1136</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1137"><a href="#L1137">1137</a></th><td class="line-code"><pre><span class="di">static</span> <span class="di">const</span> <span class="pt">char</span> Base64[] = <span class="s"><span class="dl">&quot;</span><span class="k">ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/</span><span class="dl">&quot;</span></span>;
</pre></td></tr>


<tr><th class="line-num" id="L1138"><a href="#L1138">1138</a></th><td class="line-code"><pre><span class="di">static</span> <span class="di">const</span> <span class="pt">char</span> Pad64 = <span class="ch">'='</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1139"><a href="#L1139">1139</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1140"><a href="#L1140">1140</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1141"><a href="#L1141">1141</a></th><td class="line-code"><pre><span class="pp">#define</span> mDNSisspace(x) (x == <span class="ch">'\t'</span> || x == <span class="ch">'\n'</span> || x == <span class="ch">'\v'</span> || x == <span class="ch">'\f'</span> || x == <span class="ch">'\r'</span> || x == <span class="ch">' '</span>)
</pre></td></tr>


<tr><th class="line-num" id="L1142"><a href="#L1142">1142</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1143"><a href="#L1143">1143</a></th><td class="line-code"><pre>mDNSlocal <span class="di">const</span> <span class="pt">char</span> *mDNSstrchr(<span class="di">const</span> <span class="pt">char</span> *s, <span class="pt">int</span> c)
</pre></td></tr>


<tr><th class="line-num" id="L1144"><a href="#L1144">1144</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1145"><a href="#L1145">1145</a></th><td class="line-code"><pre>        <span class="r">while</span> (<span class="i">1</span>)
</pre></td></tr>


<tr><th class="line-num" id="L1146"><a href="#L1146">1146</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1147"><a href="#L1147">1147</a></th><td class="line-code"><pre>                <span class="r">if</span> (c == *s) <span class="r">return</span> s;
</pre></td></tr>


<tr><th class="line-num" id="L1148"><a href="#L1148">1148</a></th><td class="line-code"><pre>                <span class="r">if</span> (!*s) <span class="r">return</span> mDNSNULL;
</pre></td></tr>


<tr><th class="line-num" id="L1149"><a href="#L1149">1149</a></th><td class="line-code"><pre>                s++;
</pre></td></tr>


<tr><th class="line-num" id="L1150"><a href="#L1150">1150</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1151"><a href="#L1151">1151</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1152"><a href="#L1152">1152</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1153"><a href="#L1153">1153</a></th><td class="line-code"><pre><span class="c">// skips all whitespace anywhere.</span>
</pre></td></tr>


<tr><th class="line-num" id="L1154"><a href="#L1154">1154</a></th><td class="line-code"><pre><span class="c">// converts characters, four at a time, starting at (or after)</span>
</pre></td></tr>


<tr><th class="line-num" id="L1155"><a href="#L1155">1155</a></th><td class="line-code"><pre><span class="c">// src from base - 64 numbers into three 8 bit bytes in the target area.</span>
</pre></td></tr>


<tr><th class="line-num" id="L1156"><a href="#L1156">1156</a></th><td class="line-code"><pre><span class="c">// it returns the number of data bytes stored at the target, or -1 on error.</span>
</pre></td></tr>


<tr><th class="line-num" id="L1157"><a href="#L1157">1157</a></th><td class="line-code"><pre><span class="c">// adapted from BIND sources</span>
</pre></td></tr>


<tr><th class="line-num" id="L1158"><a href="#L1158">1158</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1159"><a href="#L1159">1159</a></th><td class="line-code"><pre>mDNSlocal mDNSs32 DNSDigest_Base64ToBin(<span class="di">const</span> <span class="pt">char</span> *src, mDNSu8 *target, mDNSu32 targsize)
</pre></td></tr>


<tr><th class="line-num" id="L1160"><a href="#L1160">1160</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1161"><a href="#L1161">1161</a></th><td class="line-code"><pre>        <span class="pt">int</span> tarindex, state, ch;
</pre></td></tr>


<tr><th class="line-num" id="L1162"><a href="#L1162">1162</a></th><td class="line-code"><pre>        <span class="di">const</span> <span class="pt">char</span> *pos;
</pre></td></tr>


<tr><th class="line-num" id="L1163"><a href="#L1163">1163</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1164"><a href="#L1164">1164</a></th><td class="line-code"><pre>        state = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1165"><a href="#L1165">1165</a></th><td class="line-code"><pre>        tarindex = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1166"><a href="#L1166">1166</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1167"><a href="#L1167">1167</a></th><td class="line-code"><pre>        <span class="r">while</span> ((ch = *src++) != <span class="ch">'\0'</span>) {
</pre></td></tr>


<tr><th class="line-num" id="L1168"><a href="#L1168">1168</a></th><td class="line-code"><pre>                <span class="r">if</span> (mDNSisspace(ch))        <span class="c">/* Skip whitespace anywhere. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1169"><a href="#L1169">1169</a></th><td class="line-code"><pre>                        <span class="r">continue</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1170"><a href="#L1170">1170</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1171"><a href="#L1171">1171</a></th><td class="line-code"><pre>                <span class="r">if</span> (ch == Pad64)
</pre></td></tr>


<tr><th class="line-num" id="L1172"><a href="#L1172">1172</a></th><td class="line-code"><pre>                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1173"><a href="#L1173">1173</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1174"><a href="#L1174">1174</a></th><td class="line-code"><pre>                pos = mDNSstrchr(Base64, ch);
</pre></td></tr>


<tr><th class="line-num" id="L1175"><a href="#L1175">1175</a></th><td class="line-code"><pre>                <span class="r">if</span> (pos == <span class="i">0</span>)                 <span class="c">/* A non-base64 character. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1176"><a href="#L1176">1176</a></th><td class="line-code"><pre>                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1177"><a href="#L1177">1177</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1178"><a href="#L1178">1178</a></th><td class="line-code"><pre>                <span class="r">switch</span> (state) {
</pre></td></tr>


<tr><th class="line-num" id="L1179"><a href="#L1179">1179</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">0</span>:
</pre></td></tr>


<tr><th class="line-num" id="L1180"><a href="#L1180">1180</a></th><td class="line-code"><pre>                        <span class="r">if</span> (target) {
</pre></td></tr>


<tr><th class="line-num" id="L1181"><a href="#L1181">1181</a></th><td class="line-code"><pre>                                <span class="r">if</span> ((mDNSu32)tarindex &gt;= targsize)
</pre></td></tr>


<tr><th class="line-num" id="L1182"><a href="#L1182">1182</a></th><td class="line-code"><pre>                                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1183"><a href="#L1183">1183</a></th><td class="line-code"><pre>                                target[tarindex] = (mDNSu8)((pos - Base64) &lt;&lt; <span class="i">2</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1184"><a href="#L1184">1184</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L1185"><a href="#L1185">1185</a></th><td class="line-code"><pre>                        state = <span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1186"><a href="#L1186">1186</a></th><td class="line-code"><pre>                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1187"><a href="#L1187">1187</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">1</span>:
</pre></td></tr>


<tr><th class="line-num" id="L1188"><a href="#L1188">1188</a></th><td class="line-code"><pre>                        <span class="r">if</span> (target) {
</pre></td></tr>


<tr><th class="line-num" id="L1189"><a href="#L1189">1189</a></th><td class="line-code"><pre>                                <span class="r">if</span> ((mDNSu32)tarindex + <span class="i">1</span> &gt;= targsize)
</pre></td></tr>


<tr><th class="line-num" id="L1190"><a href="#L1190">1190</a></th><td class="line-code"><pre>                                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1191"><a href="#L1191">1191</a></th><td class="line-code"><pre>                                target[tarindex]   |=  (pos - Base64) &gt;&gt; <span class="i">4</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1192"><a href="#L1192">1192</a></th><td class="line-code"><pre>                                target[tarindex+<span class="i">1</span>]  = (mDNSu8)(((pos - Base64) &amp; <span class="hx">0x0f</span>) &lt;&lt; <span class="i">4</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1193"><a href="#L1193">1193</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L1194"><a href="#L1194">1194</a></th><td class="line-code"><pre>                        tarindex++;
</pre></td></tr>


<tr><th class="line-num" id="L1195"><a href="#L1195">1195</a></th><td class="line-code"><pre>                        state = <span class="i">2</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1196"><a href="#L1196">1196</a></th><td class="line-code"><pre>                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1197"><a href="#L1197">1197</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">2</span>:
</pre></td></tr>


<tr><th class="line-num" id="L1198"><a href="#L1198">1198</a></th><td class="line-code"><pre>                        <span class="r">if</span> (target) {
</pre></td></tr>


<tr><th class="line-num" id="L1199"><a href="#L1199">1199</a></th><td class="line-code"><pre>                                <span class="r">if</span> ((mDNSu32)tarindex + <span class="i">1</span> &gt;= targsize)
</pre></td></tr>


<tr><th class="line-num" id="L1200"><a href="#L1200">1200</a></th><td class="line-code"><pre>                                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1201"><a href="#L1201">1201</a></th><td class="line-code"><pre>                                target[tarindex]   |=  (pos - Base64) &gt;&gt; <span class="i">2</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1202"><a href="#L1202">1202</a></th><td class="line-code"><pre>                                target[tarindex+<span class="i">1</span>]  = (mDNSu8)(((pos - Base64) &amp; <span class="hx">0x03</span>) &lt;&lt; <span class="i">6</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1203"><a href="#L1203">1203</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L1204"><a href="#L1204">1204</a></th><td class="line-code"><pre>                        tarindex++;
</pre></td></tr>


<tr><th class="line-num" id="L1205"><a href="#L1205">1205</a></th><td class="line-code"><pre>                        state = <span class="i">3</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1206"><a href="#L1206">1206</a></th><td class="line-code"><pre>                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1207"><a href="#L1207">1207</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">3</span>:
</pre></td></tr>


<tr><th class="line-num" id="L1208"><a href="#L1208">1208</a></th><td class="line-code"><pre>                        <span class="r">if</span> (target) {
</pre></td></tr>


<tr><th class="line-num" id="L1209"><a href="#L1209">1209</a></th><td class="line-code"><pre>                                <span class="r">if</span> ((mDNSu32)tarindex &gt;= targsize)
</pre></td></tr>


<tr><th class="line-num" id="L1210"><a href="#L1210">1210</a></th><td class="line-code"><pre>                                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1211"><a href="#L1211">1211</a></th><td class="line-code"><pre>                                target[tarindex] |= (pos - Base64);
</pre></td></tr>


<tr><th class="line-num" id="L1212"><a href="#L1212">1212</a></th><td class="line-code"><pre>                        }
</pre></td></tr>


<tr><th class="line-num" id="L1213"><a href="#L1213">1213</a></th><td class="line-code"><pre>                        tarindex++;
</pre></td></tr>


<tr><th class="line-num" id="L1214"><a href="#L1214">1214</a></th><td class="line-code"><pre>                        state = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1215"><a href="#L1215">1215</a></th><td class="line-code"><pre>                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1216"><a href="#L1216">1216</a></th><td class="line-code"><pre>                <span class="r">default</span>:
</pre></td></tr>


<tr><th class="line-num" id="L1217"><a href="#L1217">1217</a></th><td class="line-code"><pre>                        <span class="r">return</span> -<span class="i">1</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1218"><a href="#L1218">1218</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1219"><a href="#L1219">1219</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1220"><a href="#L1220">1220</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1221"><a href="#L1221">1221</a></th><td class="line-code"><pre>        <span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L1222"><a href="#L1222">1222</a></th><td class="line-code"><pre>         * We are done decoding Base-64 chars.  Let's see if we ended
</pre></td></tr>


<tr><th class="line-num" id="L1223"><a href="#L1223">1223</a></th><td class="line-code"><pre>         * on a byte boundary, and/or with erroneous trailing characters.
</pre></td></tr>


<tr><th class="line-num" id="L1224"><a href="#L1224">1224</a></th><td class="line-code"><pre>         */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1225"><a href="#L1225">1225</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1226"><a href="#L1226">1226</a></th><td class="line-code"><pre>        <span class="r">if</span> (ch == Pad64) {                <span class="c">/* We got a pad char. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1227"><a href="#L1227">1227</a></th><td class="line-code"><pre>                ch = *src++;                <span class="c">/* Skip it, get next. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1228"><a href="#L1228">1228</a></th><td class="line-code"><pre>                <span class="r">switch</span> (state) {
</pre></td></tr>


<tr><th class="line-num" id="L1229"><a href="#L1229">1229</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">0</span>:                <span class="c">/* Invalid = in first position */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1230"><a href="#L1230">1230</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">1</span>:                <span class="c">/* Invalid = in second position */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1231"><a href="#L1231">1231</a></th><td class="line-code"><pre>                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1232"><a href="#L1232">1232</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1233"><a href="#L1233">1233</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">2</span>:                <span class="c">/* Valid, means one byte of info */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1234"><a href="#L1234">1234</a></th><td class="line-code"><pre>                        <span class="c">/* Skip any number of spaces. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1235"><a href="#L1235">1235</a></th><td class="line-code"><pre>                        <span class="r">for</span> ((<span class="di">void</span>)mDNSNULL; ch != <span class="ch">'\0'</span>; ch = *src++)
</pre></td></tr>


<tr><th class="line-num" id="L1236"><a href="#L1236">1236</a></th><td class="line-code"><pre>                                <span class="r">if</span> (!mDNSisspace(ch))
</pre></td></tr>


<tr><th class="line-num" id="L1237"><a href="#L1237">1237</a></th><td class="line-code"><pre>                                        <span class="r">break</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1238"><a href="#L1238">1238</a></th><td class="line-code"><pre>                        <span class="c">/* Make sure there is another trailing = sign. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1239"><a href="#L1239">1239</a></th><td class="line-code"><pre>                        <span class="r">if</span> (ch != Pad64)
</pre></td></tr>


<tr><th class="line-num" id="L1240"><a href="#L1240">1240</a></th><td class="line-code"><pre>                                <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1241"><a href="#L1241">1241</a></th><td class="line-code"><pre>                        ch = *src++;                <span class="c">/* Skip the = */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1242"><a href="#L1242">1242</a></th><td class="line-code"><pre>                        <span class="c">/* Fall through to &quot;single trailing =&quot; case. */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1243"><a href="#L1243">1243</a></th><td class="line-code"><pre>                        <span class="c">/* FALLTHROUGH */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1244"><a href="#L1244">1244</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1245"><a href="#L1245">1245</a></th><td class="line-code"><pre>                <span class="r">case</span> <span class="i">3</span>:                <span class="c">/* Valid, means two bytes of info */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1246"><a href="#L1246">1246</a></th><td class="line-code"><pre>                        <span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L1247"><a href="#L1247">1247</a></th><td class="line-code"><pre>                         * We know this char is an =.  Is there anything but
</pre></td></tr>


<tr><th class="line-num" id="L1248"><a href="#L1248">1248</a></th><td class="line-code"><pre>                         * whitespace after it?
</pre></td></tr>


<tr><th class="line-num" id="L1249"><a href="#L1249">1249</a></th><td class="line-code"><pre>                         */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1250"><a href="#L1250">1250</a></th><td class="line-code"><pre>                        <span class="r">for</span> ((<span class="di">void</span>)mDNSNULL; ch != <span class="ch">'\0'</span>; ch = *src++)
</pre></td></tr>


<tr><th class="line-num" id="L1251"><a href="#L1251">1251</a></th><td class="line-code"><pre>                                <span class="r">if</span> (!mDNSisspace(ch))
</pre></td></tr>


<tr><th class="line-num" id="L1252"><a href="#L1252">1252</a></th><td class="line-code"><pre>                                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1253"><a href="#L1253">1253</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1254"><a href="#L1254">1254</a></th><td class="line-code"><pre>                        <span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L1255"><a href="#L1255">1255</a></th><td class="line-code"><pre>                         * Now make sure for cases 2 and 3 that the &quot;extra&quot;
</pre></td></tr>


<tr><th class="line-num" id="L1256"><a href="#L1256">1256</a></th><td class="line-code"><pre>                         * bits that slopped past the last full byte were
</pre></td></tr>


<tr><th class="line-num" id="L1257"><a href="#L1257">1257</a></th><td class="line-code"><pre>                         * zeros.  If we don't check them, they become a
</pre></td></tr>


<tr><th class="line-num" id="L1258"><a href="#L1258">1258</a></th><td class="line-code"><pre>                         * subliminal channel.
</pre></td></tr>


<tr><th class="line-num" id="L1259"><a href="#L1259">1259</a></th><td class="line-code"><pre>                         */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1260"><a href="#L1260">1260</a></th><td class="line-code"><pre>                        <span class="r">if</span> (target &amp;&amp; target[tarindex] != <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L1261"><a href="#L1261">1261</a></th><td class="line-code"><pre>                                <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1262"><a href="#L1262">1262</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1263"><a href="#L1263">1263</a></th><td class="line-code"><pre>        } <span class="r">else</span> {
</pre></td></tr>


<tr><th class="line-num" id="L1264"><a href="#L1264">1264</a></th><td class="line-code"><pre>                <span class="c">/*
</pre></td></tr>


<tr><th class="line-num" id="L1265"><a href="#L1265">1265</a></th><td class="line-code"><pre>                 * We ended by seeing the end of the string.  Make sure we
</pre></td></tr>


<tr><th class="line-num" id="L1266"><a href="#L1266">1266</a></th><td class="line-code"><pre>                 * have no partial bytes lying around.
</pre></td></tr>


<tr><th class="line-num" id="L1267"><a href="#L1267">1267</a></th><td class="line-code"><pre>                 */</span>
</pre></td></tr>


<tr><th class="line-num" id="L1268"><a href="#L1268">1268</a></th><td class="line-code"><pre>                <span class="r">if</span> (state != <span class="i">0</span>)
</pre></td></tr>


<tr><th class="line-num" id="L1269"><a href="#L1269">1269</a></th><td class="line-code"><pre>                        <span class="r">return</span> (-<span class="i">1</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1270"><a href="#L1270">1270</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1271"><a href="#L1271">1271</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1272"><a href="#L1272">1272</a></th><td class="line-code"><pre>        <span class="r">return</span> (tarindex);
</pre></td></tr>


<tr><th class="line-num" id="L1273"><a href="#L1273">1273</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1274"><a href="#L1274">1274</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1275"><a href="#L1275">1275</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1276"><a href="#L1276">1276</a></th><td class="line-code"><pre> <span class="c">// ***************************************************************************</span>
</pre></td></tr>


<tr><th class="line-num" id="L1277"><a href="#L1277">1277</a></th><td class="line-code"><pre><span class="pp">#if</span> COMPILER_LIKES_PRAGMA_MARK
</pre></td></tr>


<tr><th class="line-num" id="L1278"><a href="#L1278">1278</a></th><td class="line-code"><pre><span class="pp">#pragma</span> mark - API exported to mDNS Core
</pre></td></tr>


<tr><th class="line-num" id="L1279"><a href="#L1279">1279</a></th><td class="line-code"><pre><span class="pp">#endif</span>
</pre></td></tr>


<tr><th class="line-num" id="L1280"><a href="#L1280">1280</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1281"><a href="#L1281">1281</a></th><td class="line-code"><pre><span class="c">// Constants</span>
</pre></td></tr>


<tr><th class="line-num" id="L1282"><a href="#L1282">1282</a></th><td class="line-code"><pre><span class="pp">#define</span> HMAC_IPAD   <span class="hx">0x36</span>
</pre></td></tr>


<tr><th class="line-num" id="L1283"><a href="#L1283">1283</a></th><td class="line-code"><pre><span class="pp">#define</span> HMAC_OPAD   <span class="hx">0x5c</span>
</pre></td></tr>


<tr><th class="line-num" id="L1284"><a href="#L1284">1284</a></th><td class="line-code"><pre><span class="pp">#define</span> MD5_LEN     <span class="i">16</span>
</pre></td></tr>


<tr><th class="line-num" id="L1285"><a href="#L1285">1285</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1286"><a href="#L1286">1286</a></th><td class="line-code"><pre><span class="pp">#define</span> HMAC_MD5_AlgName (*(<span class="di">const</span> domainname*) <span class="s"><span class="dl">&quot;</span><span class="ch">\010</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="k">hmac-md5</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="ch">\007</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="k">sig-alg</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="ch">\003</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="k">reg</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="ch">\003</span><span class="dl">&quot;</span></span> <span class="s"><span class="dl">&quot;</span><span class="k">int</span><span class="dl">&quot;</span></span>)
</pre></td></tr>


<tr><th class="line-num" id="L1287"><a href="#L1287">1287</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1288"><a href="#L1288">1288</a></th><td class="line-code"><pre><span class="c">// Adapted from Appendix, RFC 2104</span>
</pre></td></tr>


<tr><th class="line-num" id="L1289"><a href="#L1289">1289</a></th><td class="line-code"><pre>mDNSlocal <span class="di">void</span> DNSDigest_ConstructHMACKey(DomainAuthInfo *info, <span class="di">const</span> mDNSu8 *key, mDNSu32 len)                
</pre></td></tr>


<tr><th class="line-num" id="L1290"><a href="#L1290">1290</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1291"><a href="#L1291">1291</a></th><td class="line-code"><pre>        MD5_CTX k;
</pre></td></tr>


<tr><th class="line-num" id="L1292"><a href="#L1292">1292</a></th><td class="line-code"><pre>        mDNSu8 buf[MD5_LEN];
</pre></td></tr>


<tr><th class="line-num" id="L1293"><a href="#L1293">1293</a></th><td class="line-code"><pre>        <span class="pt">int</span> i;
</pre></td></tr>


<tr><th class="line-num" id="L1294"><a href="#L1294">1294</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1295"><a href="#L1295">1295</a></th><td class="line-code"><pre>        <span class="c">// If key is longer than HMAC_LEN reset it to MD5(key)</span>
</pre></td></tr>


<tr><th class="line-num" id="L1296"><a href="#L1296">1296</a></th><td class="line-code"><pre>        <span class="r">if</span> (len &gt; HMAC_LEN)
</pre></td></tr>


<tr><th class="line-num" id="L1297"><a href="#L1297">1297</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1298"><a href="#L1298">1298</a></th><td class="line-code"><pre>                MD5_Init(&amp;k);
</pre></td></tr>


<tr><th class="line-num" id="L1299"><a href="#L1299">1299</a></th><td class="line-code"><pre>                MD5_Update(&amp;k, key, len);
</pre></td></tr>


<tr><th class="line-num" id="L1300"><a href="#L1300">1300</a></th><td class="line-code"><pre>                MD5_Final(buf, &amp;k);
</pre></td></tr>


<tr><th class="line-num" id="L1301"><a href="#L1301">1301</a></th><td class="line-code"><pre>                key = buf;
</pre></td></tr>


<tr><th class="line-num" id="L1302"><a href="#L1302">1302</a></th><td class="line-code"><pre>                len = MD5_LEN;
</pre></td></tr>


<tr><th class="line-num" id="L1303"><a href="#L1303">1303</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1304"><a href="#L1304">1304</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1305"><a href="#L1305">1305</a></th><td class="line-code"><pre>        <span class="c">// store key in pads</span>
</pre></td></tr>


<tr><th class="line-num" id="L1306"><a href="#L1306">1306</a></th><td class="line-code"><pre>        mDNSPlatformMemZero(info-&gt;keydata_ipad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1307"><a href="#L1307">1307</a></th><td class="line-code"><pre>        mDNSPlatformMemZero(info-&gt;keydata_opad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1308"><a href="#L1308">1308</a></th><td class="line-code"><pre>        mDNSPlatformMemCopy(info-&gt;keydata_ipad, key, len);
</pre></td></tr>


<tr><th class="line-num" id="L1309"><a href="#L1309">1309</a></th><td class="line-code"><pre>        mDNSPlatformMemCopy(info-&gt;keydata_opad, key, len);
</pre></td></tr>


<tr><th class="line-num" id="L1310"><a href="#L1310">1310</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1311"><a href="#L1311">1311</a></th><td class="line-code"><pre>        <span class="c">// XOR key with ipad and opad values</span>
</pre></td></tr>


<tr><th class="line-num" id="L1312"><a href="#L1312">1312</a></th><td class="line-code"><pre>        <span class="r">for</span> (i = <span class="i">0</span>; i &lt; HMAC_LEN; i++)
</pre></td></tr>


<tr><th class="line-num" id="L1313"><a href="#L1313">1313</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1314"><a href="#L1314">1314</a></th><td class="line-code"><pre>                info-&gt;keydata_ipad[i] ^= HMAC_IPAD;
</pre></td></tr>


<tr><th class="line-num" id="L1315"><a href="#L1315">1315</a></th><td class="line-code"><pre>                info-&gt;keydata_opad[i] ^= HMAC_OPAD;
</pre></td></tr>


<tr><th class="line-num" id="L1316"><a href="#L1316">1316</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1317"><a href="#L1317">1317</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1318"><a href="#L1318">1318</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1319"><a href="#L1319">1319</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1320"><a href="#L1320">1320</a></th><td class="line-code"><pre>mDNSexport mDNSs32 DNSDigest_ConstructHMACKeyfromBase64(DomainAuthInfo *info, <span class="di">const</span> <span class="pt">char</span> *b64key)
</pre></td></tr>


<tr><th class="line-num" id="L1321"><a href="#L1321">1321</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1322"><a href="#L1322">1322</a></th><td class="line-code"><pre>        mDNSu8 keybuf[<span class="i">1024</span>];
</pre></td></tr>


<tr><th class="line-num" id="L1323"><a href="#L1323">1323</a></th><td class="line-code"><pre>        mDNSs32 keylen = DNSDigest_Base64ToBin(b64key, keybuf, <span class="r">sizeof</span>(keybuf));
</pre></td></tr>


<tr><th class="line-num" id="L1324"><a href="#L1324">1324</a></th><td class="line-code"><pre>        <span class="r">if</span> (keylen &lt; <span class="i">0</span>) <span class="r">return</span>(keylen);
</pre></td></tr>


<tr><th class="line-num" id="L1325"><a href="#L1325">1325</a></th><td class="line-code"><pre>        DNSDigest_ConstructHMACKey(info, keybuf, (mDNSu32)keylen);
</pre></td></tr>


<tr><th class="line-num" id="L1326"><a href="#L1326">1326</a></th><td class="line-code"><pre>        <span class="r">return</span>(keylen);
</pre></td></tr>


<tr><th class="line-num" id="L1327"><a href="#L1327">1327</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1328"><a href="#L1328">1328</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1329"><a href="#L1329">1329</a></th><td class="line-code"><pre>mDNSexport <span class="di">void</span> DNSDigest_SignMessage(DNSMessage *msg, mDNSu8 **end, DomainAuthInfo *info, mDNSu16 tcode)
</pre></td></tr>


<tr><th class="line-num" id="L1330"><a href="#L1330">1330</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1331"><a href="#L1331">1331</a></th><td class="line-code"><pre>        AuthRecord tsig;
</pre></td></tr>


<tr><th class="line-num" id="L1332"><a href="#L1332">1332</a></th><td class="line-code"><pre>        mDNSu8  *rdata, *<span class="di">const</span> countPtr = (mDNSu8 *)&amp;msg-&gt;h.numAdditionals;        <span class="c">// Get existing numAdditionals value</span>
</pre></td></tr>


<tr><th class="line-num" id="L1333"><a href="#L1333">1333</a></th><td class="line-code"><pre>        mDNSu32 utc32;
</pre></td></tr>


<tr><th class="line-num" id="L1334"><a href="#L1334">1334</a></th><td class="line-code"><pre>        mDNSu8 utc48[<span class="i">6</span>];
</pre></td></tr>


<tr><th class="line-num" id="L1335"><a href="#L1335">1335</a></th><td class="line-code"><pre>        mDNSu8 digest[MD5_LEN];
</pre></td></tr>


<tr><th class="line-num" id="L1336"><a href="#L1336">1336</a></th><td class="line-code"><pre>        mDNSu8 *ptr = *end;
</pre></td></tr>


<tr><th class="line-num" id="L1337"><a href="#L1337">1337</a></th><td class="line-code"><pre>        mDNSu32 len;
</pre></td></tr>


<tr><th class="line-num" id="L1338"><a href="#L1338">1338</a></th><td class="line-code"><pre>        mDNSOpaque16 buf;
</pre></td></tr>


<tr><th class="line-num" id="L1339"><a href="#L1339">1339</a></th><td class="line-code"><pre>        MD5_CTX c;
</pre></td></tr>


<tr><th class="line-num" id="L1340"><a href="#L1340">1340</a></th><td class="line-code"><pre>        mDNSu16 numAdditionals = (mDNSu16)((mDNSu16)countPtr[<span class="i">0</span>] &lt;&lt; <span class="i">8</span> | countPtr[<span class="i">1</span>]);
</pre></td></tr>


<tr><th class="line-num" id="L1341"><a href="#L1341">1341</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1342"><a href="#L1342">1342</a></th><td class="line-code"><pre>        <span class="c">// Init MD5 context, digest inner key pad and message</span>
</pre></td></tr>


<tr><th class="line-num" id="L1343"><a href="#L1343">1343</a></th><td class="line-code"><pre>    MD5_Init(&amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1344"><a href="#L1344">1344</a></th><td class="line-code"><pre>    MD5_Update(&amp;c, info-&gt;keydata_ipad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1345"><a href="#L1345">1345</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, (mDNSu8 *)msg, (<span class="pt">unsigned</span> <span class="pt">long</span>)(*end - (mDNSu8 *)msg));
</pre></td></tr>


<tr><th class="line-num" id="L1346"><a href="#L1346">1346</a></th><td class="line-code"><pre>           
</pre></td></tr>


<tr><th class="line-num" id="L1347"><a href="#L1347">1347</a></th><td class="line-code"><pre>        <span class="c">// Construct TSIG RR, digesting variables as apporpriate</span>
</pre></td></tr>


<tr><th class="line-num" id="L1348"><a href="#L1348">1348</a></th><td class="line-code"><pre>        mDNS_SetupResourceRecord(&amp;tsig, mDNSNULL, <span class="i">0</span>, kDNSType_TSIG, <span class="i">0</span>, kDNSRecordTypeKnownUnique, AuthRecordAny, mDNSNULL, mDNSNULL);
</pre></td></tr>


<tr><th class="line-num" id="L1349"><a href="#L1349">1349</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1350"><a href="#L1350">1350</a></th><td class="line-code"><pre>        <span class="c">// key name</span>
</pre></td></tr>


<tr><th class="line-num" id="L1351"><a href="#L1351">1351</a></th><td class="line-code"><pre>        AssignDomainName(&amp;tsig.namestorage, &amp;info-&gt;keyname);
</pre></td></tr>


<tr><th class="line-num" id="L1352"><a href="#L1352">1352</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, info-&gt;keyname.c, DomainNameLength(&amp;info-&gt;keyname));
</pre></td></tr>


<tr><th class="line-num" id="L1353"><a href="#L1353">1353</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1354"><a href="#L1354">1354</a></th><td class="line-code"><pre>        <span class="c">// class</span>
</pre></td></tr>


<tr><th class="line-num" id="L1355"><a href="#L1355">1355</a></th><td class="line-code"><pre>        tsig.resrec.rrclass = kDNSQClass_ANY;
</pre></td></tr>


<tr><th class="line-num" id="L1356"><a href="#L1356">1356</a></th><td class="line-code"><pre>        buf = mDNSOpaque16fromIntVal(kDNSQClass_ANY);
</pre></td></tr>


<tr><th class="line-num" id="L1357"><a href="#L1357">1357</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));
</pre></td></tr>


<tr><th class="line-num" id="L1358"><a href="#L1358">1358</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1359"><a href="#L1359">1359</a></th><td class="line-code"><pre>        <span class="c">// ttl</span>
</pre></td></tr>


<tr><th class="line-num" id="L1360"><a href="#L1360">1360</a></th><td class="line-code"><pre>        tsig.resrec.rroriginalttl = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1361"><a href="#L1361">1361</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, (mDNSu8 *)&amp;tsig.resrec.rroriginalttl, <span class="r">sizeof</span>(tsig.resrec.rroriginalttl));
</pre></td></tr>


<tr><th class="line-num" id="L1362"><a href="#L1362">1362</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1363"><a href="#L1363">1363</a></th><td class="line-code"><pre>        <span class="c">// alg name</span>
</pre></td></tr>


<tr><th class="line-num" id="L1364"><a href="#L1364">1364</a></th><td class="line-code"><pre>        AssignDomainName(&amp;tsig.resrec.rdata-&gt;u.name, &amp;HMAC_MD5_AlgName);
</pre></td></tr>


<tr><th class="line-num" id="L1365"><a href="#L1365">1365</a></th><td class="line-code"><pre>        len = DomainNameLength(&amp;HMAC_MD5_AlgName);
</pre></td></tr>


<tr><th class="line-num" id="L1366"><a href="#L1366">1366</a></th><td class="line-code"><pre>        rdata = tsig.resrec.rdata-&gt;u.data + len;
</pre></td></tr>


<tr><th class="line-num" id="L1367"><a href="#L1367">1367</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, HMAC_MD5_AlgName.c, len);
</pre></td></tr>


<tr><th class="line-num" id="L1368"><a href="#L1368">1368</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1369"><a href="#L1369">1369</a></th><td class="line-code"><pre>        <span class="c">// time</span>
</pre></td></tr>


<tr><th class="line-num" id="L1370"><a href="#L1370">1370</a></th><td class="line-code"><pre>        <span class="c">// get UTC (universal time), convert to 48-bit unsigned in network byte order</span>
</pre></td></tr>


<tr><th class="line-num" id="L1371"><a href="#L1371">1371</a></th><td class="line-code"><pre>        utc32 = (mDNSu32)mDNSPlatformUTC();
</pre></td></tr>


<tr><th class="line-num" id="L1372"><a href="#L1372">1372</a></th><td class="line-code"><pre>        <span class="r">if</span> (utc32 == (<span class="pt">unsigned</span>)-<span class="i">1</span>) { LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_SignMessage - mDNSPlatformUTC returned bad time -1</span><span class="dl">&quot;</span></span>); *end = mDNSNULL; }
</pre></td></tr>


<tr><th class="line-num" id="L1373"><a href="#L1373">1373</a></th><td class="line-code"><pre>        utc48[<span class="i">0</span>] = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1374"><a href="#L1374">1374</a></th><td class="line-code"><pre>        utc48[<span class="i">1</span>] = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1375"><a href="#L1375">1375</a></th><td class="line-code"><pre>        utc48[<span class="i">2</span>] = (mDNSu8)((utc32 &gt;&gt; <span class="i">24</span>) &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1376"><a href="#L1376">1376</a></th><td class="line-code"><pre>        utc48[<span class="i">3</span>] = (mDNSu8)((utc32 &gt;&gt; <span class="i">16</span>) &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1377"><a href="#L1377">1377</a></th><td class="line-code"><pre>        utc48[<span class="i">4</span>] = (mDNSu8)((utc32 &gt;&gt;  <span class="i">8</span>) &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1378"><a href="#L1378">1378</a></th><td class="line-code"><pre>        utc48[<span class="i">5</span>] = (mDNSu8)( utc32        &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1379"><a href="#L1379">1379</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1380"><a href="#L1380">1380</a></th><td class="line-code"><pre>        mDNSPlatformMemCopy(rdata, utc48, <span class="i">6</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1381"><a href="#L1381">1381</a></th><td class="line-code"><pre>        rdata += <span class="i">6</span>;                      
</pre></td></tr>


<tr><th class="line-num" id="L1382"><a href="#L1382">1382</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, utc48, <span class="i">6</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1383"><a href="#L1383">1383</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1384"><a href="#L1384">1384</a></th><td class="line-code"><pre>        <span class="c">// 300 sec is fudge recommended in RFC 2485</span>
</pre></td></tr>


<tr><th class="line-num" id="L1385"><a href="#L1385">1385</a></th><td class="line-code"><pre>        rdata[<span class="i">0</span>] = (mDNSu8)((<span class="i">300</span> &gt;&gt; <span class="i">8</span>)  &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1386"><a href="#L1386">1386</a></th><td class="line-code"><pre>        rdata[<span class="i">1</span>] = (mDNSu8)( <span class="i">300</span>        &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1387"><a href="#L1387">1387</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, rdata, <span class="r">sizeof</span>(mDNSOpaque16));
</pre></td></tr>


<tr><th class="line-num" id="L1388"><a href="#L1388">1388</a></th><td class="line-code"><pre>        rdata += <span class="r">sizeof</span>(mDNSOpaque16);
</pre></td></tr>


<tr><th class="line-num" id="L1389"><a href="#L1389">1389</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1390"><a href="#L1390">1390</a></th><td class="line-code"><pre>        <span class="c">// digest error (tcode) and other data len (zero) - we'll add them to the rdata later</span>
</pre></td></tr>


<tr><th class="line-num" id="L1391"><a href="#L1391">1391</a></th><td class="line-code"><pre>        buf.b[<span class="i">0</span>] = (mDNSu8)((tcode &gt;&gt; <span class="i">8</span>) &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1392"><a href="#L1392">1392</a></th><td class="line-code"><pre>        buf.b[<span class="i">1</span>] = (mDNSu8)( tcode       &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1393"><a href="#L1393">1393</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));  <span class="c">// error</span>
</pre></td></tr>


<tr><th class="line-num" id="L1394"><a href="#L1394">1394</a></th><td class="line-code"><pre>        buf.NotAnInteger = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1395"><a href="#L1395">1395</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));  <span class="c">// other data len</span>
</pre></td></tr>


<tr><th class="line-num" id="L1396"><a href="#L1396">1396</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1397"><a href="#L1397">1397</a></th><td class="line-code"><pre>        <span class="c">// finish the message &amp; tsig var hash</span>
</pre></td></tr>


<tr><th class="line-num" id="L1398"><a href="#L1398">1398</a></th><td class="line-code"><pre>    MD5_Final(digest, &amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1399"><a href="#L1399">1399</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1400"><a href="#L1400">1400</a></th><td class="line-code"><pre>        <span class="c">// perform outer MD5 (outer key pad, inner digest)</span>
</pre></td></tr>


<tr><th class="line-num" id="L1401"><a href="#L1401">1401</a></th><td class="line-code"><pre>        MD5_Init(&amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1402"><a href="#L1402">1402</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, info-&gt;keydata_opad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1403"><a href="#L1403">1403</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, digest, MD5_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1404"><a href="#L1404">1404</a></th><td class="line-code"><pre>        MD5_Final(digest, &amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1405"><a href="#L1405">1405</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1406"><a href="#L1406">1406</a></th><td class="line-code"><pre>        <span class="c">// set remaining rdata fields</span>
</pre></td></tr>


<tr><th class="line-num" id="L1407"><a href="#L1407">1407</a></th><td class="line-code"><pre>        rdata[<span class="i">0</span>] = (mDNSu8)((MD5_LEN &gt;&gt; <span class="i">8</span>)  &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1408"><a href="#L1408">1408</a></th><td class="line-code"><pre>        rdata[<span class="i">1</span>] = (mDNSu8)( MD5_LEN        &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1409"><a href="#L1409">1409</a></th><td class="line-code"><pre>        rdata += <span class="r">sizeof</span>(mDNSOpaque16);
</pre></td></tr>


<tr><th class="line-num" id="L1410"><a href="#L1410">1410</a></th><td class="line-code"><pre>        mDNSPlatformMemCopy(rdata, digest, MD5_LEN);                          <span class="c">// MAC</span>
</pre></td></tr>


<tr><th class="line-num" id="L1411"><a href="#L1411">1411</a></th><td class="line-code"><pre>        rdata += MD5_LEN;
</pre></td></tr>


<tr><th class="line-num" id="L1412"><a href="#L1412">1412</a></th><td class="line-code"><pre>        rdata[<span class="i">0</span>] = msg-&gt;h.id.b[<span class="i">0</span>];                                            <span class="c">// original ID</span>
</pre></td></tr>


<tr><th class="line-num" id="L1413"><a href="#L1413">1413</a></th><td class="line-code"><pre>        rdata[<span class="i">1</span>] = msg-&gt;h.id.b[<span class="i">1</span>];
</pre></td></tr>


<tr><th class="line-num" id="L1414"><a href="#L1414">1414</a></th><td class="line-code"><pre>        rdata[<span class="i">2</span>] = (mDNSu8)((tcode &gt;&gt; <span class="i">8</span>) &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1415"><a href="#L1415">1415</a></th><td class="line-code"><pre>        rdata[<span class="i">3</span>] = (mDNSu8)( tcode       &amp; <span class="hx">0xff</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1416"><a href="#L1416">1416</a></th><td class="line-code"><pre>        rdata[<span class="i">4</span>] = <span class="i">0</span>;                                                         <span class="c">// other data len</span>
</pre></td></tr>


<tr><th class="line-num" id="L1417"><a href="#L1417">1417</a></th><td class="line-code"><pre>        rdata[<span class="i">5</span>] = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1418"><a href="#L1418">1418</a></th><td class="line-code"><pre>        rdata += <span class="i">6</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1419"><a href="#L1419">1419</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1420"><a href="#L1420">1420</a></th><td class="line-code"><pre>        tsig.resrec.rdlength = (mDNSu16)(rdata - tsig.resrec.rdata-&gt;u.data);
</pre></td></tr>


<tr><th class="line-num" id="L1421"><a href="#L1421">1421</a></th><td class="line-code"><pre>        *end = PutResourceRecordTTLJumbo(msg, ptr, &amp;numAdditionals, &amp;tsig.resrec, <span class="i">0</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1422"><a href="#L1422">1422</a></th><td class="line-code"><pre>        <span class="r">if</span> (!*end) { LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_SignMessage - could not put TSIG</span><span class="dl">&quot;</span></span>); *end = mDNSNULL; <span class="r">return</span>; }
</pre></td></tr>


<tr><th class="line-num" id="L1423"><a href="#L1423">1423</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1424"><a href="#L1424">1424</a></th><td class="line-code"><pre>        <span class="c">// Write back updated numAdditionals value</span>
</pre></td></tr>


<tr><th class="line-num" id="L1425"><a href="#L1425">1425</a></th><td class="line-code"><pre>        countPtr[<span class="i">0</span>] = (mDNSu8)(numAdditionals &gt;&gt; <span class="i">8</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1426"><a href="#L1426">1426</a></th><td class="line-code"><pre>        countPtr[<span class="i">1</span>] = (mDNSu8)(numAdditionals &amp;  <span class="hx">0xFF</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1427"><a href="#L1427">1427</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1428"><a href="#L1428">1428</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1429"><a href="#L1429">1429</a></th><td class="line-code"><pre>mDNSexport mDNSBool DNSDigest_VerifyMessage(DNSMessage *msg, mDNSu8 *end, LargeCacheRecord * lcr, DomainAuthInfo *info, mDNSu16 * rcode, mDNSu16 * tcode)
</pre></td></tr>


<tr><th class="line-num" id="L1430"><a href="#L1430">1430</a></th><td class="line-code"><pre>        {
</pre></td></tr>


<tr><th class="line-num" id="L1431"><a href="#L1431">1431</a></th><td class="line-code"><pre>        mDNSu8                        *        ptr = (mDNSu8*) &amp;lcr-&gt;r.resrec.rdata-&gt;u.data;
</pre></td></tr>


<tr><th class="line-num" id="L1432"><a href="#L1432">1432</a></th><td class="line-code"><pre>        mDNSs32                                now;
</pre></td></tr>


<tr><th class="line-num" id="L1433"><a href="#L1433">1433</a></th><td class="line-code"><pre>        mDNSs32                                then;
</pre></td></tr>


<tr><th class="line-num" id="L1434"><a href="#L1434">1434</a></th><td class="line-code"><pre>        mDNSu8                                thisDigest[MD5_LEN];
</pre></td></tr>


<tr><th class="line-num" id="L1435"><a href="#L1435">1435</a></th><td class="line-code"><pre>        mDNSu8                                thatDigest[MD5_LEN];
</pre></td></tr>


<tr><th class="line-num" id="L1436"><a href="#L1436">1436</a></th><td class="line-code"><pre>        mDNSu32                                macsize;
</pre></td></tr>


<tr><th class="line-num" id="L1437"><a href="#L1437">1437</a></th><td class="line-code"><pre>        mDNSOpaque16                 buf;
</pre></td></tr>


<tr><th class="line-num" id="L1438"><a href="#L1438">1438</a></th><td class="line-code"><pre>        mDNSu8                                utc48[<span class="i">6</span>];
</pre></td></tr>


<tr><th class="line-num" id="L1439"><a href="#L1439">1439</a></th><td class="line-code"><pre>        mDNSs32                                delta;
</pre></td></tr>


<tr><th class="line-num" id="L1440"><a href="#L1440">1440</a></th><td class="line-code"><pre>        mDNSu16                                fudge;
</pre></td></tr>


<tr><th class="line-num" id="L1441"><a href="#L1441">1441</a></th><td class="line-code"><pre>        domainname                *        algo;
</pre></td></tr>


<tr><th class="line-num" id="L1442"><a href="#L1442">1442</a></th><td class="line-code"><pre>        MD5_CTX                                c;
</pre></td></tr>


<tr><th class="line-num" id="L1443"><a href="#L1443">1443</a></th><td class="line-code"><pre>        mDNSBool                        ok = mDNSfalse;
</pre></td></tr>


<tr><th class="line-num" id="L1444"><a href="#L1444">1444</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1445"><a href="#L1445">1445</a></th><td class="line-code"><pre>        <span class="c">// We only support HMAC-MD5 for now</span>
</pre></td></tr>


<tr><th class="line-num" id="L1446"><a href="#L1446">1446</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1447"><a href="#L1447">1447</a></th><td class="line-code"><pre>        algo = (domainname*) ptr;
</pre></td></tr>


<tr><th class="line-num" id="L1448"><a href="#L1448">1448</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1449"><a href="#L1449">1449</a></th><td class="line-code"><pre>        <span class="r">if</span> (!SameDomainName(algo, &amp;HMAC_MD5_AlgName))
</pre></td></tr>


<tr><th class="line-num" id="L1450"><a href="#L1450">1450</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1451"><a href="#L1451">1451</a></th><td class="line-code"><pre>                LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_VerifyMessage - TSIG algorithm not supported: %##s</span><span class="dl">&quot;</span></span>, algo-&gt;c);
</pre></td></tr>


<tr><th class="line-num" id="L1452"><a href="#L1452">1452</a></th><td class="line-code"><pre>                *rcode = kDNSFlag1_RC_NotAuth;
</pre></td></tr>


<tr><th class="line-num" id="L1453"><a href="#L1453">1453</a></th><td class="line-code"><pre>                *tcode = TSIG_ErrBadKey;
</pre></td></tr>


<tr><th class="line-num" id="L1454"><a href="#L1454">1454</a></th><td class="line-code"><pre>                ok = mDNSfalse;
</pre></td></tr>


<tr><th class="line-num" id="L1455"><a href="#L1455">1455</a></th><td class="line-code"><pre>                <span class="r">goto</span> exit;
</pre></td></tr>


<tr><th class="line-num" id="L1456"><a href="#L1456">1456</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1457"><a href="#L1457">1457</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1458"><a href="#L1458">1458</a></th><td class="line-code"><pre>        ptr += DomainNameLength(algo);
</pre></td></tr>


<tr><th class="line-num" id="L1459"><a href="#L1459">1459</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1460"><a href="#L1460">1460</a></th><td class="line-code"><pre>        <span class="c">// Check the times</span>
</pre></td></tr>


<tr><th class="line-num" id="L1461"><a href="#L1461">1461</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1462"><a href="#L1462">1462</a></th><td class="line-code"><pre>        now = mDNSPlatformUTC();
</pre></td></tr>


<tr><th class="line-num" id="L1463"><a href="#L1463">1463</a></th><td class="line-code"><pre>        <span class="r">if</span> (now == -<span class="i">1</span>)
</pre></td></tr>


<tr><th class="line-num" id="L1464"><a href="#L1464">1464</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1465"><a href="#L1465">1465</a></th><td class="line-code"><pre>                LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_VerifyMessage - mDNSPlatformUTC returned bad time -1</span><span class="dl">&quot;</span></span>);
</pre></td></tr>


<tr><th class="line-num" id="L1466"><a href="#L1466">1466</a></th><td class="line-code"><pre>                *rcode = kDNSFlag1_RC_NotAuth;
</pre></td></tr>


<tr><th class="line-num" id="L1467"><a href="#L1467">1467</a></th><td class="line-code"><pre>                *tcode = TSIG_ErrBadTime;
</pre></td></tr>


<tr><th class="line-num" id="L1468"><a href="#L1468">1468</a></th><td class="line-code"><pre>                ok = mDNSfalse;
</pre></td></tr>


<tr><th class="line-num" id="L1469"><a href="#L1469">1469</a></th><td class="line-code"><pre>                <span class="r">goto</span> exit;
</pre></td></tr>


<tr><th class="line-num" id="L1470"><a href="#L1470">1470</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1471"><a href="#L1471">1471</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1472"><a href="#L1472">1472</a></th><td class="line-code"><pre>        <span class="c">// Get the 48 bit time field, skipping over the first word</span>
</pre></td></tr>


<tr><th class="line-num" id="L1473"><a href="#L1473">1473</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1474"><a href="#L1474">1474</a></th><td class="line-code"><pre>        utc48[<span class="i">0</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1475"><a href="#L1475">1475</a></th><td class="line-code"><pre>        utc48[<span class="i">1</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1476"><a href="#L1476">1476</a></th><td class="line-code"><pre>        utc48[<span class="i">2</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1477"><a href="#L1477">1477</a></th><td class="line-code"><pre>        utc48[<span class="i">3</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1478"><a href="#L1478">1478</a></th><td class="line-code"><pre>        utc48[<span class="i">4</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1479"><a href="#L1479">1479</a></th><td class="line-code"><pre>        utc48[<span class="i">5</span>] = *ptr++;
</pre></td></tr>


<tr><th class="line-num" id="L1480"><a href="#L1480">1480</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1481"><a href="#L1481">1481</a></th><td class="line-code"><pre>        then  = (mDNSs32)NToH32(utc48 + <span class="r">sizeof</span>(mDNSu16));
</pre></td></tr>


<tr><th class="line-num" id="L1482"><a href="#L1482">1482</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1483"><a href="#L1483">1483</a></th><td class="line-code"><pre>        fudge = NToH16(ptr);
</pre></td></tr>


<tr><th class="line-num" id="L1484"><a href="#L1484">1484</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1485"><a href="#L1485">1485</a></th><td class="line-code"><pre>        ptr += <span class="r">sizeof</span>(mDNSu16);
</pre></td></tr>


<tr><th class="line-num" id="L1486"><a href="#L1486">1486</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1487"><a href="#L1487">1487</a></th><td class="line-code"><pre>        delta = (now &gt; then) ? now - then : then - now;
</pre></td></tr>


<tr><th class="line-num" id="L1488"><a href="#L1488">1488</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1489"><a href="#L1489">1489</a></th><td class="line-code"><pre>        <span class="r">if</span> (delta &gt; fudge)
</pre></td></tr>


<tr><th class="line-num" id="L1490"><a href="#L1490">1490</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1491"><a href="#L1491">1491</a></th><td class="line-code"><pre>                LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_VerifyMessage - time skew &gt; %d</span><span class="dl">&quot;</span></span>, fudge);
</pre></td></tr>


<tr><th class="line-num" id="L1492"><a href="#L1492">1492</a></th><td class="line-code"><pre>                *rcode = kDNSFlag1_RC_NotAuth;
</pre></td></tr>


<tr><th class="line-num" id="L1493"><a href="#L1493">1493</a></th><td class="line-code"><pre>                *tcode = TSIG_ErrBadTime;
</pre></td></tr>


<tr><th class="line-num" id="L1494"><a href="#L1494">1494</a></th><td class="line-code"><pre>                ok = mDNSfalse;
</pre></td></tr>


<tr><th class="line-num" id="L1495"><a href="#L1495">1495</a></th><td class="line-code"><pre>                <span class="r">goto</span> exit;
</pre></td></tr>


<tr><th class="line-num" id="L1496"><a href="#L1496">1496</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1497"><a href="#L1497">1497</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1498"><a href="#L1498">1498</a></th><td class="line-code"><pre>        <span class="c">// MAC size</span>
</pre></td></tr>


<tr><th class="line-num" id="L1499"><a href="#L1499">1499</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1500"><a href="#L1500">1500</a></th><td class="line-code"><pre>        macsize = (mDNSu32) NToH16(ptr);
</pre></td></tr>


<tr><th class="line-num" id="L1501"><a href="#L1501">1501</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1502"><a href="#L1502">1502</a></th><td class="line-code"><pre>        ptr += <span class="r">sizeof</span>(mDNSu16);
</pre></td></tr>


<tr><th class="line-num" id="L1503"><a href="#L1503">1503</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1504"><a href="#L1504">1504</a></th><td class="line-code"><pre>        <span class="c">// MAC</span>
</pre></td></tr>


<tr><th class="line-num" id="L1505"><a href="#L1505">1505</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1506"><a href="#L1506">1506</a></th><td class="line-code"><pre>        mDNSPlatformMemCopy(thatDigest, ptr, MD5_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1507"><a href="#L1507">1507</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1508"><a href="#L1508">1508</a></th><td class="line-code"><pre>        <span class="c">// Init MD5 context, digest inner key pad and message</span>
</pre></td></tr>


<tr><th class="line-num" id="L1509"><a href="#L1509">1509</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1510"><a href="#L1510">1510</a></th><td class="line-code"><pre>        MD5_Init(&amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1511"><a href="#L1511">1511</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, info-&gt;keydata_ipad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1512"><a href="#L1512">1512</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, (mDNSu8*) msg, (<span class="pt">unsigned</span> <span class="pt">long</span>)(end - (mDNSu8*) msg));
</pre></td></tr>


<tr><th class="line-num" id="L1513"><a href="#L1513">1513</a></th><td class="line-code"><pre>           
</pre></td></tr>


<tr><th class="line-num" id="L1514"><a href="#L1514">1514</a></th><td class="line-code"><pre>        <span class="c">// Key name</span>
</pre></td></tr>


<tr><th class="line-num" id="L1515"><a href="#L1515">1515</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1516"><a href="#L1516">1516</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, lcr-&gt;r.resrec.name-&gt;c, DomainNameLength(lcr-&gt;r.resrec.name));
</pre></td></tr>


<tr><th class="line-num" id="L1517"><a href="#L1517">1517</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1518"><a href="#L1518">1518</a></th><td class="line-code"><pre>        <span class="c">// Class name</span>
</pre></td></tr>


<tr><th class="line-num" id="L1519"><a href="#L1519">1519</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1520"><a href="#L1520">1520</a></th><td class="line-code"><pre>        buf = mDNSOpaque16fromIntVal(lcr-&gt;r.resrec.rrclass);
</pre></td></tr>


<tr><th class="line-num" id="L1521"><a href="#L1521">1521</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));
</pre></td></tr>


<tr><th class="line-num" id="L1522"><a href="#L1522">1522</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1523"><a href="#L1523">1523</a></th><td class="line-code"><pre>        <span class="c">// TTL</span>
</pre></td></tr>


<tr><th class="line-num" id="L1524"><a href="#L1524">1524</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1525"><a href="#L1525">1525</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, (mDNSu8*) &amp;lcr-&gt;r.resrec.rroriginalttl, <span class="r">sizeof</span>(lcr-&gt;r.resrec.rroriginalttl));
</pre></td></tr>


<tr><th class="line-num" id="L1526"><a href="#L1526">1526</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1527"><a href="#L1527">1527</a></th><td class="line-code"><pre>        <span class="c">// Algorithm</span>
</pre></td></tr>


<tr><th class="line-num" id="L1528"><a href="#L1528">1528</a></th><td class="line-code"><pre> 
</pre></td></tr>


<tr><th class="line-num" id="L1529"><a href="#L1529">1529</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, algo-&gt;c, DomainNameLength(algo));
</pre></td></tr>


<tr><th class="line-num" id="L1530"><a href="#L1530">1530</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1531"><a href="#L1531">1531</a></th><td class="line-code"><pre>        <span class="c">// Time</span>
</pre></td></tr>


<tr><th class="line-num" id="L1532"><a href="#L1532">1532</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1533"><a href="#L1533">1533</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, utc48, <span class="i">6</span>);
</pre></td></tr>


<tr><th class="line-num" id="L1534"><a href="#L1534">1534</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1535"><a href="#L1535">1535</a></th><td class="line-code"><pre>        <span class="c">// Fudge</span>
</pre></td></tr>


<tr><th class="line-num" id="L1536"><a href="#L1536">1536</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1537"><a href="#L1537">1537</a></th><td class="line-code"><pre>        buf = mDNSOpaque16fromIntVal(fudge);
</pre></td></tr>


<tr><th class="line-num" id="L1538"><a href="#L1538">1538</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));
</pre></td></tr>


<tr><th class="line-num" id="L1539"><a href="#L1539">1539</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1540"><a href="#L1540">1540</a></th><td class="line-code"><pre>        <span class="c">// Digest error and other data len (both zero) - we'll add them to the rdata later</span>
</pre></td></tr>


<tr><th class="line-num" id="L1541"><a href="#L1541">1541</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1542"><a href="#L1542">1542</a></th><td class="line-code"><pre>        buf.NotAnInteger = <span class="i">0</span>;
</pre></td></tr>


<tr><th class="line-num" id="L1543"><a href="#L1543">1543</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));  <span class="c">// error</span>
</pre></td></tr>


<tr><th class="line-num" id="L1544"><a href="#L1544">1544</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, buf.b, <span class="r">sizeof</span>(mDNSOpaque16));  <span class="c">// other data len</span>
</pre></td></tr>


<tr><th class="line-num" id="L1545"><a href="#L1545">1545</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1546"><a href="#L1546">1546</a></th><td class="line-code"><pre>        <span class="c">// Finish the message &amp; tsig var hash</span>
</pre></td></tr>


<tr><th class="line-num" id="L1547"><a href="#L1547">1547</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1548"><a href="#L1548">1548</a></th><td class="line-code"><pre>    MD5_Final(thisDigest, &amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1549"><a href="#L1549">1549</a></th><td class="line-code"><pre>        
</pre></td></tr>


<tr><th class="line-num" id="L1550"><a href="#L1550">1550</a></th><td class="line-code"><pre>        <span class="c">// perform outer MD5 (outer key pad, inner digest)</span>
</pre></td></tr>


<tr><th class="line-num" id="L1551"><a href="#L1551">1551</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1552"><a href="#L1552">1552</a></th><td class="line-code"><pre>        MD5_Init(&amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1553"><a href="#L1553">1553</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, info-&gt;keydata_opad, HMAC_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1554"><a href="#L1554">1554</a></th><td class="line-code"><pre>        MD5_Update(&amp;c, thisDigest, MD5_LEN);
</pre></td></tr>


<tr><th class="line-num" id="L1555"><a href="#L1555">1555</a></th><td class="line-code"><pre>        MD5_Final(thisDigest, &amp;c);
</pre></td></tr>


<tr><th class="line-num" id="L1556"><a href="#L1556">1556</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1557"><a href="#L1557">1557</a></th><td class="line-code"><pre>        <span class="r">if</span> (!mDNSPlatformMemSame(thisDigest, thatDigest, MD5_LEN))
</pre></td></tr>


<tr><th class="line-num" id="L1558"><a href="#L1558">1558</a></th><td class="line-code"><pre>                {
</pre></td></tr>


<tr><th class="line-num" id="L1559"><a href="#L1559">1559</a></th><td class="line-code"><pre>                LogMsg(<span class="s"><span class="dl">&quot;</span><span class="k">ERROR: DNSDigest_VerifyMessage - bad signature</span><span class="dl">&quot;</span></span>);
</pre></td></tr>


<tr><th class="line-num" id="L1560"><a href="#L1560">1560</a></th><td class="line-code"><pre>                *rcode = kDNSFlag1_RC_NotAuth;
</pre></td></tr>


<tr><th class="line-num" id="L1561"><a href="#L1561">1561</a></th><td class="line-code"><pre>                *tcode = TSIG_ErrBadSig;
</pre></td></tr>


<tr><th class="line-num" id="L1562"><a href="#L1562">1562</a></th><td class="line-code"><pre>                ok = mDNSfalse;
</pre></td></tr>


<tr><th class="line-num" id="L1563"><a href="#L1563">1563</a></th><td class="line-code"><pre>                <span class="r">goto</span> exit;
</pre></td></tr>


<tr><th class="line-num" id="L1564"><a href="#L1564">1564</a></th><td class="line-code"><pre>                }
</pre></td></tr>


<tr><th class="line-num" id="L1565"><a href="#L1565">1565</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1566"><a href="#L1566">1566</a></th><td class="line-code"><pre>        <span class="c">// set remaining rdata fields</span>
</pre></td></tr>


<tr><th class="line-num" id="L1567"><a href="#L1567">1567</a></th><td class="line-code"><pre>        ok = mDNStrue;
</pre></td></tr>


<tr><th class="line-num" id="L1568"><a href="#L1568">1568</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1569"><a href="#L1569">1569</a></th><td class="line-code"><pre><span class="la">exit:</span>
</pre></td></tr>


<tr><th class="line-num" id="L1570"><a href="#L1570">1570</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1571"><a href="#L1571">1571</a></th><td class="line-code"><pre>        <span class="r">return</span> ok;
</pre></td></tr>


<tr><th class="line-num" id="L1572"><a href="#L1572">1572</a></th><td class="line-code"><pre>        }
</pre></td></tr>


<tr><th class="line-num" id="L1573"><a href="#L1573">1573</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1574"><a href="#L1574">1574</a></th><td class="line-code"><pre>
</pre></td></tr>


<tr><th class="line-num" id="L1575"><a href="#L1575">1575</a></th><td class="line-code"><pre><span class="pp">#ifdef</span> __cplusplus
</pre></td></tr>


<tr><th class="line-num" id="L1576"><a href="#L1576">1576</a></th><td class="line-code"><pre>}
</pre></td></tr>


<tr><th class="line-num" id="L1577"><a href="#L1577">1577</a></th><td class="line-code"><pre><span class="pp">#endif</span>
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

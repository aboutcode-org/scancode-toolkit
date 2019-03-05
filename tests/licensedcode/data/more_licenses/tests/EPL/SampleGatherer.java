/* *******************************************************************
 * Copyright (c) 2003 Contributors.
 * All rights reserved. 
 * This program and the accompanying materials are made available 
 * under the terms of the Eclipse Public License v1.0 
 * which accompanies this distribution and is available at 
 * http://www.eclipse.org/legal/epl-v10.html 
 *  
 * Contributors: 
 *     Wes Isberg     initial implementation 
 * ******************************************************************/

/*
 * A quickie hack to extract sample code from testable sources.
 * This could reuse a lot of code from elsewhere, 
 * but currently doesn't, 
 * to keep it in the build module which avoids dependencies.
 * (Too bad we can't use scripting languages...)
 */
package org.aspectj.internal.tools.build;

import java.io.*;
import java.text.DateFormat;
import java.util.*;

/**
 * This gathers sample code delimited with [START..END]-SAMPLE
 * from source files under a base directory,
 * along with any <code>@author</code> info.
 *   <pre>// START-SAMPLE {anchorName} {anchorText}
 *    ... sample code ...
 *   // END-SAMPLE {anchorName}
 *   </pre>
 * where {anchorName} need not be unique and might be 
 * hierarchical wrt "-", e.g., "genus-species-individual".
 */
public class SampleGatherer {
    
    /** EOL String for gathered lines */
    public static final String EOL = "\n"; // XXX
    
    static final String START = "START-SAMPLE";
    static final String END = "END-SAMPLE";
    static final String AUTHOR = "@author";
    static final String FLAG = "XXX";

//    private static void test(String[] args){
//        String[] from = new String[] { "<pre>", "</pre>" };
//        String[] to = new String[] { "&lt;pre>", "&lt;/pre>" };
//        String source = "in this <pre> day and </pre> age of <pre and /pre>";
//        System.err.println("from " + source);
//        System.err.println("  to " + SampleUtil.replace(source, from, to));
//        source = "<pre> day and </pre>";
//        System.err.println("from " + source);
//        System.err.println("  to " + SampleUtil.replace(source, from, to));
//        source = "<pre day and </pre";
//        System.err.println("from " + source);
//        System.err.println("  to " + SampleUtil.replace(source, from, to));
//        source = "<pre> day and </pre> age";
//        System.err.println("from " + source);
//        System.err.println("  to " + SampleUtil.replace(source, from, to));
//        source = "in this <pre> day and </pre> age";
//        System.err.println("from " + source);
//        System.err.println("  to " + SampleUtil.replace(source, from, to));
//        
//    }
    /**
     * Emit samples gathered from any input args.
     * @param args the String[] of paths to files or directories to search
     * @throws IOException if unable to read a source file
     */
    public static void main(String[] args) throws IOException {
        if ((null == args) || (0 == args.length)) {
            String cname = SampleGatherer.class.getName();
            System.err.println("java " + cname + " [dir|file]");
            return;
        }
        Samples result = new Samples();
        for (int i = 0; i < args.length; i++) {
            result = gather(new File(args[i]), result);
        }

        StringBuffer sb = HTMLSamplesRenderer.ME.render(result, null);

        File out = new File("../docs/dist/doc/sample-code.html");
        FileOutputStream fos = new FileOutputStream(out);
        fos.write(sb.toString().getBytes());
        fos.close();
        System.out.println("see file:///" + out);
    }
    
    /**
     * Gather samples from a source file or directory
     * @param source the File file or directory to start with
     * @param sink the Samples collection to add to
     * @return sink or a new Samples collection with any samples found
     * @throws IOException if unable to read a source file
     */
    public static Samples gather(File source, Samples sink) 
            throws IOException {
        if (null == sink) {
            sink = new Samples();
        }
        if (null == source) {
            source = new File(".");
        }
        doGather(source, sink);
        return sink;
    }
    private static String trimCommentEnd(String line, int start) {
        if (null == line) {
            return "";
        }
        if ((start > 0) && (start < line.length())) {
            line = line.substring(start);
        }
        line = line.trim();
        if (line.endsWith("*/")) {
            line = line.substring(0, line.length()-2).trim();
        } else if (line.endsWith("-->")) {
            line = line.substring(0, line.length()-3).trim();
        }
        return line;
    }
        
    private static void doGather(File source, Samples sink) 
            throws IOException {
        if (source.isFile()) {
            if (isSource(source)) {
                gatherFromFile(source, sink);
            }
        } else if (source.isDirectory() && source.canRead()) {
            File[] files = source.listFiles();
            for (int i = 0; i < files.length; i++) {
                doGather(files[i], sink);
            }
        }
    }

    private static boolean isSource(File file) {
        if ((null == file) || !file.isFile() || !file.canRead()) {
            return false;
        }
        String path = file.getName().toLowerCase();
        String[] suffixes = Sample.Kind.SOURCE_SUFFIXES;
        for (int i = 0; i < suffixes.length; i++) {
            if (path.endsWith(suffixes[i])) {
                return true;
            }
        }
        return false;
    }
    
    private static void gatherFromFile(final File source, final Samples sink) 
            throws IOException {
        Reader reader = null;
        try {
            String author = null;
            StringBuffer sampleCode = new StringBuffer();
            String anchorName = null;
            String anchorTitle = null;
            ArrayList flags = new ArrayList();
            int startLine = -1; // seeking
            int endLine = Integer.MAX_VALUE; // not seeking
            reader = new FileReader(source);
            LineNumberReader lineReader = new LineNumberReader(reader);
            String line;

            while (null != (line = lineReader.readLine())) { // XXX naive
                // found start?
                int loc = line.indexOf(START);
                if (-1 != loc) {
                    int lineNumber = lineReader.getLineNumber();
                    if (-1 != startLine) {
                        abort("unexpected " + START, source, line, lineNumber);
                    }
                    startLine = lineNumber;
                    endLine = -1;
                    anchorName = trimCommentEnd(line, loc + START.length());
                    loc = anchorName.indexOf(" ");
                    if (-1 == loc) {
                        anchorTitle = null;
                    } else {
                        anchorTitle = anchorName.substring(1+loc).trim();
                        anchorName = anchorName.substring(0, loc);
                    }
                    continue;
                } 

                // found end?
                loc = line.indexOf(END);
                if (-1 != loc) {
                    int lineNumber = lineReader.getLineNumber();
                    if (Integer.MAX_VALUE == endLine) {
                        abort("unexpected " + END, source, line, lineNumber);
                    }
                    String newtag = trimCommentEnd(line, loc + END.length());
                    if ((newtag.length() > 0) && !newtag.equals(anchorName)) {
                        String m = "expected " + anchorName
                            + " got " + newtag;
                        abort(m, source, line, lineNumber);
                    }
                    endLine = lineNumber;
                    Sample sample = new Sample(anchorName,
                            anchorTitle,
                            author, 
                            sampleCode.toString(), 
                            source, 
                            startLine, 
                            endLine,
                            (String[]) flags.toArray(new String[flags.size()]));
                    sink.addSample(sample);

                    // back to seeking start
                    sampleCode.setLength(0);
                    startLine = -1;
                    endLine = Integer.MAX_VALUE;
                    continue;
                } 

                // found author?
                loc = line.indexOf(AUTHOR);
                if (-1 != loc) {
                    author = trimCommentEnd(line, loc + AUTHOR.length());
                }
                // found flag comment?
                loc = line.indexOf(FLAG);
                if (-1 != loc) {
                    flags.add(trimCommentEnd(line, loc + FLAG.length()));
                }
                
                // reading?
                if ((-1 != startLine) && (-1 == endLine)) {
                    sampleCode.append(line);
                    sampleCode.append(EOL);
                }
            }
            if (-1 == endLine) {
                abort("incomplete sample", source, "", lineReader.getLineNumber());
            }
        } finally {
            if (null != reader) {
                reader.close();
            }
        }
    }
    private static void abort(String why, File file, String line, int lineNumber)
            throws Abort {
        throw new Abort(why + " at " + file + ":" + lineNumber + ": " + line);
    }
//    private static void delay(Object toDelay) {
//        synchronized (toDelay) { // XXX sleep instead?
//            toDelay.notifyAll();
//        }
//    }
    static class Abort extends IOException {
        private static final long serialVersionUID = -1l;
        Abort(String s) {
            super(s);
        }
    }
}

/**
 * Data associated with sample code - struct class.
 */
class Sample {
    public static final String ASPECTJ_TEAM = "The AspectJ Team";

    /** sort by anchorName, file path, and start/end location */
    static Comparator NAME_SOURCE_COMPARER = new Comparator() {
        public int compare(Object lhs, Object rhs) {
            Sample left = (Sample) lhs;
            Sample right = (Sample) rhs;
            if (null == left) {
                return (null == right ? 0 : -1);
            } 
            if (null == right) {
                return 1;
            } 
            int result = left.anchorName.compareTo(right.anchorName);
            if (0 != result) {
                return result;                
            }
            result = left.sourcePath.compareTo(right.sourcePath);
            if (0 != result) {
                return result;                
            }
            result = right.startLine - left.startLine;
            if (0 != result) {
                return result;                
            }
            return right.endLine - left.endLine;
        }
    };

    /** sort by author, then NAME_SOURCE_COMPARER */
    static Comparator AUTHOR_NAME_SOURCE_COMPARER = new Comparator() {
        public int compare(Object lhs, Object rhs) {
            Sample left = (Sample) lhs;
            Sample right = (Sample) rhs;
            if (null == left) {
                return (null == right ? 0 : -1);
            } 
            if (null == right) {
                return 1;
            } 
            int result = left.author.compareTo(right.author);
            if (0 != result) {
                return result;                
            }
            return NAME_SOURCE_COMPARER.compare(lhs, rhs);
        }
    };
    
    final String anchorName;
    final String anchorTitle;
    final String author;
    final String sampleCode;
    final File sourcePath;
    final int startLine;
    final int endLine;
    final Kind kind;
    /** List of String flags found in the sample */
    final List flags;
    public Sample(
        String anchorName,
        String anchorTitle,
        String author,
        String sampleCode,
        File sourcePath,
        int startLine,
        int endLine,
        String[] flags) {
        this.anchorName = anchorName;
        this.anchorTitle = anchorTitle;
        this.author = (null != author ? author : ASPECTJ_TEAM);
        this.sampleCode = sampleCode;
        this.sourcePath = sourcePath;
        this.startLine = startLine;
        this.endLine = endLine;
        this.kind = Kind.getKind(sourcePath);
//        List theFlags;
        if ((null == flags) || (0 == flags.length)) {
            this.flags = Collections.EMPTY_LIST;
        } else {
            this.flags = Collections.unmodifiableList(Arrays.asList(flags));
        }
    }

    public String toString() {
        return sampleCode;
    }

    public static class Kind {
        
        /** lowercase source suffixes identify files to gather samples from */
        public static final String[] SOURCE_SUFFIXES = new String[]
        { ".java", ".aj", ".sh", ".ksh", 
        ".txt", ".text", ".html", ".htm", ".xml" };
        static final Kind XML = new Kind();
        static final Kind HTML = new Kind();
        static final Kind PROGRAM = new Kind();
        static final Kind SCRIPT = new Kind();
        static final Kind TEXT = new Kind();
        static final Kind OTHER = new Kind();
        public static Kind getKind(File file) {
            if (null == file) {
                return OTHER;
            }
            String name = file.getName().toLowerCase();
            if ((name.endsWith(".java") || name.endsWith(".aj"))) {
                return PROGRAM;
            }
            if ((name.endsWith(".html") || name.endsWith(".htm"))) {
                return HTML;
            }
            if ((name.endsWith(".sh") || name.endsWith(".ksh"))) {
                return SCRIPT;
            }
            if ((name.endsWith(".txt") || name.endsWith(".text"))) {
                return TEXT;
            }
            if (name.endsWith(".xml")) {
                return XML;
            }
            return OTHER;
        }
        private Kind() {
        }
    }
}

/**
 * type-safe Collection of samples.
 */
class Samples {
    private ArrayList samples = new ArrayList();
    int size() {
        return samples.size();
    }
    void addSample(Sample sample) {
        samples.add(sample);
    }
    /**
     * @return List copy, sorted by Sample.NAME_SOURCE_COMPARER
     */
    List getSortedSamples() {
        return getSortedSamples(Sample.NAME_SOURCE_COMPARER);
    }
    
    List getSortedSamples(Comparator comparer) {
        ArrayList result = new ArrayList();
        result.addAll(samples);
        Collections.sort(result, comparer);
        return result;
    }
}


/**
 * Render samples by using method visitors.
 */
class SamplesRenderer {
    public static SamplesRenderer ME = new SamplesRenderer();
    protected SamplesRenderer() {        
    }
    public static final String EOL = "\n"; // XXX
    public static final String INFO = 
      "<p>This contains contributions from the AspectJ community of "
    + "<ul><li>sample code for AspectJ programs,</li>"
    + "<li>sample code for extensions to AspectJ tools using the public API's,</li>"
    + "<li>sample scripts for invoking AspectJ tools, and </li> "
    + "<li>documentation trails showing how to do given tasks"
    + "    using AspectJ, AJDT, or various IDE or deployment"
    + "    environments.</li></ul></p>"
    + "<p>Find complete source files in the AspectJ CVS repository at "
    + "<code>org.aspectj/modules/docs/sandbox</code>. "
    + "For instructions on downloading code from the CVS repository, "
    + "see the <a href=\"doc/faq.html#q:buildingsource\">FAQ entry "
    + "\"buildingsource\"</a>.</p>";

    public static final String COPYRIGHT = 
        "<p><small>Copyright 2003 Contributors. All Rights Reserved. "
        + "This sample code is made available under the Common Public "        + "License version 1.0 available at "
        + "<a href=\"http://www.eclipse.org/legal/epl-v10.html\">"
        + "http://www.eclipse.org/legal/epl-v10.html</a>."
        + "Contributors are listed in this document as authors. "
        + "Permission to republish portions of this sample code "
        + "is hereby granted if the publication acknowledges "
        + "the author by name and "
        + "the source by reference to the AspectJ project home page "
        + " at http://eclipse.org/aspectj.</small></p>"
        + EOL;
    
    /** template algorithm to render */
    public final StringBuffer render(Samples samples, StringBuffer sink) {
        if (null == sink) {
            sink = new StringBuffer();
        }
        if ((null == samples) || (0 == samples.size())) {
            return sink;
        }
        startList(samples, sink);
        List list = samples.getSortedSamples();
        String anchorName = null;
        for (ListIterator iter = list.listIterator();
            iter.hasNext();) {
            Sample sample = (Sample) iter.next();
            String newAnchorName = sample.anchorName;
            if ((null == anchorName) 
                || (!anchorName.equals(newAnchorName))) {
                endAnchorName(anchorName, sink); 
                startAnchorName(newAnchorName, sample.anchorTitle, sink);
                anchorName = newAnchorName;
            }
            render(sample, sink);
        }
        endAnchorName(anchorName, sink);
        endList(samples, sink);
        return sink;
    }
    protected void startList(Samples samples, StringBuffer sink) {
        sink.append("Printing " + samples.size() + " samples");
        sink.append(EOL);
    }

    protected void startAnchorName(String name, String title, StringBuffer sink) {
        sink.append("anchor " + name);
        sink.append(EOL);
    }

    protected void render(Sample sample, StringBuffer sink) {
        SampleUtil.render(sample, "=", ", ",sink);
        sink.setLength(sink.length()-2);
        sink.append(EOL);
    }

    /**
     * @param name the String name being ended - ignore if null
     * @param sink
     */
    protected void endAnchorName(String name, StringBuffer sink) {
        if (null == name) {
            return;
        }
    }

    protected void endList(Samples samples, StringBuffer sink) {
        sink.append("Printed " + samples.size() + " samples");
        sink.append(EOL);
    }

}

// XXX need DocBookSamplesRenderer

/**
 * Output the samples as a single HTML file, with a table of contents
 * and sorting the samples by their anchor tags.
 */
class HTMLSamplesRenderer extends SamplesRenderer {
    public static SamplesRenderer ME = new HTMLSamplesRenderer();
    // XXX move these
    public static boolean doHierarchical = true;    
    public static boolean doFlags = false;    

        
    final StringBuffer tableOfContents;
    final StringBuffer sampleSection;
    String[] lastAnchor = new String[0];
    String currentAnchor;
    String currentAuthor;

    protected HTMLSamplesRenderer() {        
        sampleSection = new StringBuffer();
        tableOfContents = new StringBuffer();
    }
    
    protected void startAnchorName(String name, String title, StringBuffer sink) {
        if (doHierarchical) {
            doContentTree(name);
        } 
        // ---- now do anchor
        tableOfContents.append("        <li><a href=\"#" + name);
        if ((null == title) || (0 == title.length())) {
            title = name;
        }
        tableOfContents.append("\">" + title + "</a></li>");
        tableOfContents.append(EOL);
        currentAnchor = name;
    }

    protected void startList(Samples samples, StringBuffer sink) {
    }

    protected void render(Sample sample, StringBuffer sink) {
        if (null != currentAnchor) {
            if (!currentAnchor.equals(sample.anchorName)) {
                String m = "expected " + currentAnchor
                    + " got " + sample.anchorName;
                throw new Error(m);
            }
            currentAnchor = null;
        }
    
        // do heading then code
        renderHeading(sample.anchorName, sample.anchorTitle, sampleSection); 
        if (sample.kind == Sample.Kind.HTML) {
            renderHTML(sample);
        } else if (sample.kind == Sample.Kind.XML) {
            renderXML(sample);
        } else {
            renderPre(sample);
        }
    }

    protected boolean doRenderAuthor(Sample sample) {
        return (null != sample.author);
        // && !sample.author.equals(currentAuthor)
    }

    protected void renderStandardHeader(Sample sample) {
        // XXX starting same as pre
        if (doRenderAuthor(sample)) {
            currentAuthor = sample.author;
            sampleSection.append("    <p>| &nbsp; " + currentAuthor);
            sampleSection.append(EOL);
        }
        sampleSection.append(" &nbsp;|&nbsp; "); 
        sampleSection.append(SampleUtil.renderCodePath(sample.sourcePath));
        sampleSection.append(":" + sample.startLine);
        sampleSection.append(" &nbsp;|"); 
        sampleSection.append(EOL);
        sampleSection.append("<p>"); 
        sampleSection.append(EOL);
        if (doFlags) {
            boolean flagHeaderDone = false;
            for (Iterator iter = sample.flags.iterator(); iter.hasNext();) {
                String flag = (String) iter.next();
                if (!flagHeaderDone) {
                    sampleSection.append("<p>Comments flagged:<ul>");
                    sampleSection.append(EOL);
                    flagHeaderDone = true;
                }
                sampleSection.append("<li>");
                sampleSection.append(flag);
                sampleSection.append("</li>");
            }
            if (flagHeaderDone) {
                sampleSection.append("</ul>");
                sampleSection.append(EOL);
            }
        }
    }
    
    protected void renderXML(Sample sample) {
        renderStandardHeader(sample);
        sampleSection.append("    <pre>");
        sampleSection.append(EOL);
        sampleSection.append(prepareXMLSample(sample.sampleCode));
        sampleSection.append(EOL);
        sampleSection.append("    </pre>");
        sampleSection.append(EOL);
    }

    protected void renderHTML(Sample sample) {
        renderStandardHeader(sample);
        sampleSection.append(EOL);
        sampleSection.append(prepareHTMLSample(sample.sampleCode));
        sampleSection.append(EOL);
    }

    protected void renderPre(Sample sample) {
        renderStandardHeader(sample);
        sampleSection.append("    <pre>");
        sampleSection.append(EOL);
        sampleSection.append(prepareCodeSample(sample.sampleCode));
        sampleSection.append("    </pre>");
        sampleSection.append(EOL);
    }

    protected void endAnchorName(String name, StringBuffer sink) {
        if (null == name) {
            return;
        }
        currentAnchor = null;
        currentAuthor = null; // authors don't span anchors
    }

    protected void endList(Samples samples, StringBuffer sink) {
        sink.append("<html>");
        sink.append(EOL);
        sink.append("<title>AspectJ sample code</title>");
        sink.append(EOL);
        sink.append("<body>");
        sink.append(EOL);
        sink.append("    <a name=\"top\"></a>");
        sink.append(EOL);
        sink.append("    <h1>AspectJ sample code</h1>");
        sink.append(INFO);
        sink.append(EOL);
        sink.append(COPYRIGHT);
        sink.append(EOL);
        sink.append("<p><small>Generated on ");
        sink.append(DateFormat.getDateInstance().format(new Date()));
        sink.append(" by SamplesGatherer</small>");
        sink.append(EOL);
        sink.append("    <h2>Contents</h2>");
        sink.append(EOL);
        sink.append("    <ul>");
        sink.append(EOL);
        sink.append(tableOfContents.toString());
        // unwind to common prefix, if necessary
        for (int i = 0; i < lastAnchor.length ; i++) {
            sink.append("        </ul>");
        }

        sink.append("    <li><a href=\"#authorIndex\">Author Index</a></li>");
        sink.append("    </ul>");
        sink.append("    <h2>Listings</h2>");
        sink.append(EOL);
        sink.append(sampleSection.toString());
        renderAuthorIndex(samples, sink);
        sink.append("</body></html>");
        sink.append(EOL);
    }

    protected String prepareXMLSample(String sampleCode) {
        String[] from = new String[] {"\t", "<"};
        String[] to   = new String[] {"    ", "&lt;"};
        return (SampleUtil.replace(sampleCode, from, to));
    }

    protected String prepareHTMLSample(String sampleCode) {
        String[] from = new String[20];
        String[] to   = new String[20];
        for (int i = 0; i < to.length; i++) {
            String h = "h" + i + ">";
            from[i] = "<" + h;
            to[i] = "<p><b>";
            from[++i] = "</" + h;
            to[i] = "</b></p><p>";
        }
        return (SampleUtil.replace(sampleCode, from, to));
    }

    protected String prepareCodeSample(String sampleCode) {
        String[] from = new String[] { "<pre>", "</pre>" };
        String[] to   = new String[] { "&lt;pre>", "&lt;/pre>" };
        return (SampleUtil.replace(sampleCode, from, to));
    }

    protected void renderHeading(String anchor, String title, StringBuffer sink) {
        sink.append("    <a name=\"" + anchor + "\"></a>");
        sink.append(EOL);
        if ((null == title) || (0 == title.length())) {
            title = anchor;
        }
        sink.append("    <h3>" + title + "</h3>");
        sink.append(EOL);
        sink.append("<a href=\"#top\">back to top</a>");
        sink.append(EOL);
    }

    /**
     * Manage headings in both table of contents and listings.
     * @param name the String anchor
     */
    protected void doContentTree(String name) {
        if (name.equals(lastAnchor)) {
            return;
        }
        // ---- handle trees
        String[] parts = SampleUtil.splitAnchorName(name);
        //String[] lastAnchor = (String[]) lastAnchors.peek();
        int firstDiff = SampleUtil.commonPrefix(parts, lastAnchor);
        // unwind to common prefix, if necessary
        if (firstDiff+1 < lastAnchor.length) {
            for (int i = 1; i < lastAnchor.length-firstDiff ; i++) {
                tableOfContents.append("        </ul>");
                tableOfContents.append(EOL);
            }
        }
        // build up prefix
        StringBuffer branchAnchor = new StringBuffer();
        for (int i = 0; i < firstDiff;) {
            branchAnchor.append(parts[i]);
            i++;
            branchAnchor.append("-");
        }
        // emit leading headers, but not anchor itself
        for (int i = firstDiff; i < (parts.length-1); i++) {
            branchAnchor.append(parts[i]);
            String prefixName = branchAnchor.toString();
            branchAnchor.append("-");
            tableOfContents.append("        <li><a href=\"#");
            tableOfContents.append(prefixName);
            tableOfContents.append("\">" + prefixName + "</a></li>");
            tableOfContents.append(EOL);
            tableOfContents.append("        <ul>");
            tableOfContents.append(EOL);
            
            renderHeading(prefixName, prefixName, sampleSection);
        }
        lastAnchor = parts;        
    }

    protected void renderAuthorIndex(Samples samples, StringBuffer sink) {
        sink.append("<h2><a name=\"authorIndex\"></a>Author Index</h2>");
        List list = samples.getSortedSamples(Sample.AUTHOR_NAME_SOURCE_COMPARER);
        String lastAuthor = null;
        for (ListIterator iter = list.listIterator(); iter.hasNext();) {
            Sample sample = (Sample)iter.next();
            String author = sample.author;
            if (!author.equals(lastAuthor)) {
                if (null != lastAuthor) {
                    sink.append("</li></ul>");
                }
                sink.append("<li>");
                sink.append(author);
                sink.append(EOL);
                sink.append("<ul>");
                sink.append(EOL);
                lastAuthor = author;
            }
            sink.append("    <li><a href=\"#");
            sink.append(sample.anchorName);
            sink.append("\">");
            if (null == sample.anchorTitle) {
                sink.append(sample.anchorName);
            } else {
                sink.append(sample.anchorTitle);
            }
            sink.append("</a></li>");
        }
    }
}

class SampleUtil {
    public static final String SAMPLE_BASE_DIR_NAME = "sandbox";

    public static void simpleRender(Samples result, StringBuffer sink) {
        List sortedSamples = result.getSortedSamples();
        int i = 0;
        for (ListIterator iter = sortedSamples.listIterator();
            iter.hasNext();) {
            Sample sample = (Sample) iter.next();
            sink.append(i++ + ": " + sample);
        }        
    }
    
    /** result struct for getPackagePath */
    static class JavaFile {
        /** input File possibly signifying a java file */
        final File path;
        
        /** String java path suffix in form "com/company/Bar.java" 
         *  null if this is not a java file
         */
        final String javaPath;
        
        /** any prefix before java path suffix in the original path */
        final String prefix;
        
        /** error handling */
        final Throwable thrown;
        JavaFile(File path, String javaPath, String prefix, Throwable thrown) {
            this.path = path;
            this.javaPath = javaPath;
            this.prefix = prefix;
            this.thrown = thrown;
        }
    }

    /**
     * Read any package statement in the file to determine
     * the package path of the file
     * @param path the File to seek the package in
     * @return the JavaFile with the components of the path
     */
    public static JavaFile getJavaFile(File path) {
        if (null == path) {
            throw new IllegalArgumentException("null path");
        }
        String result = path.getPath().replace('\\', '/');
        String packag = "";
        String javaPath = null;
        String prefix = null;
        Throwable thrown = null;
        if (result.endsWith(".java") || result.endsWith(".aj")) {
            FileReader reader = null;
            try {
                reader = new FileReader(path);
                BufferedReader br = new BufferedReader(reader);
                String line;
                while (null != (line = br.readLine())) {
                    int loc = line.indexOf("package");
                    if (-1 != loc) {
                        int end = line.indexOf(";");
                        if (-1 == loc) {
                            String m = "unterminated package statement \"";
                            throw new Error(m + line + "\" in " + path);
                        }
                        packag = (line.substring(loc + 7, end) + ".")
                            .trim()
                            .replace('.', '/');
                        break;
                    }
                    loc = line.indexOf("import");
                    if (-1 != loc) {
                        break;
                    }
                }
            } catch (IOException e) {
                thrown = e;
            } finally {
                if (null != reader) {
                    try {
                        reader.close();
                    } catch (IOException e1) { 
                        // ignore
                    }
                }
            }
            if (null == thrown) {
                javaPath = packag + path.getName();
                int loc = result.indexOf(javaPath);
                if (-1 == loc) {
                    String m = "expected suffix " + javaPath + " in ";
                    throw new Error(m + result);
                }
                prefix = result.substring(0, loc);
            }
        }
        return new JavaFile(path, javaPath, prefix, thrown);
    }
    
    /**
     * Extract file path relative to base of package directory
     * and directory in SAMPLE_BASE_DIR_NAME for this file.
     * @param path the File to render from SAMPLE_BASE_DIR_NAME
     * @return String "baseDir {path}"
     */
    public static String renderCodePath(File path) {
        JavaFile javaFile = getJavaFile(path);
        if (javaFile.thrown != null) {
            throw new Error(javaFile.thrown.getClass() 
                + ": " + javaFile.thrown.getMessage());
        }
        
        String file = javaFile.javaPath; // can be null...
        String prefix = javaFile.prefix;
        if (prefix == null) {
            prefix = path.getPath().replace('\\', '/');
        }
        int loc = prefix.lastIndexOf(SAMPLE_BASE_DIR_NAME);
        if (-1 == loc) {
            String m = "not after " + SAMPLE_BASE_DIR_NAME;
            throw new IllegalArgumentException(m + "?: " + path);
        }
        prefix = prefix.substring(loc + 1 + SAMPLE_BASE_DIR_NAME.length());
        
        if (file == null) {
            int slash = prefix.lastIndexOf('/');
            if (-1 == slash) {
                file = prefix;
                prefix = "";
            } else {
                file = prefix.substring(slash+1);
                prefix = prefix.substring(0, slash);
            }
        }
        if (prefix.endsWith("/")) {
            prefix = prefix.substring(0, prefix.length()-1);
        }
        return (prefix + " " + file).trim();
    }

    public static int commonPrefix(String[] lhs, String[] rhs) {
        final int max = smallerSize(lhs, rhs);
        int firstDiff = 0;
        while (firstDiff < max) {
            if (!lhs[firstDiff].equals(rhs[firstDiff])) {
                break;
            }
            firstDiff++;
        }
        return firstDiff;
    }

    private static int smallerSize(Object[] one, Object[] two) {
        if ((null == one) || (null == two)) {
            return 0;
        }
        return (one.length > two.length ? two.length : one.length);
    }
    
    public static String[] splitAnchorName(Sample sample) {
        return splitAnchorName(sample.anchorName);
    }
    
    public static String[] splitAnchorName(String anchorName) {
        ArrayList result = new ArrayList();
        int start = 0;
        int loc = anchorName.indexOf("-", start);
        String next;
        while (loc != -1) {
            next  = anchorName.substring(start, loc);
            result.add(next);
            start = loc+1;
            loc = anchorName.indexOf("-", start);
        }
        next  = anchorName.substring(start);
        result.add(next);
        return (String[]) result.toArray(new String[result.size()]);
    }
    /**
     * Replace literals with literals in source string
     * @param source the String to modify
     * @param from the String[] of literals to replace
     * @param to the String[] of literals to use when replacing
     * @return the String source as modified by the replaces
     */
    public static String replace(String source, String[] from, String[] to) {
        if ((null == source) || (0 == source.length())) {
            return source;
        }
        if (from.length != to.length) {
            throw new IllegalArgumentException("unmatched from/to");
        }
        StringBuffer result = new StringBuffer();
        int LEN = source.length();
        int start = 0;
        for (int i = 0; i < LEN; i++) {
            String suffix = source.substring(i);
            for (int j = 0; j < from.length; j++) {
                if (suffix.startsWith(from[j])) {
                    result.append(source.substring(start, i));
                    result.append(to[j]);
                    start = i + from[j].length();
                    i = start-1;
                    break;
                }
            }
        }
        if (start < source.length()) {
            result.append(source.substring(start));
        }
        return result.toString();
    }

    public static void render(
        Sample sample,
        String fieldDelim, 
        String valueDelim, 
        StringBuffer sink) {
        if ((null == sink) || (null == sample)) {
            return;
        }
        if (null == fieldDelim) {
            fieldDelim = "";
        }
        if (null == valueDelim) {
            valueDelim = "";
        }
        sink.append("anchorName");
        sink.append(valueDelim);
        sink.append(sample.anchorName);
        sink.append(fieldDelim);
        sink.append("author");
        sink.append(valueDelim);
        sink.append(sample.author);
        sink.append(fieldDelim);
        sink.append("sourcePath");
        sink.append(valueDelim);
        sink.append(sample.sourcePath.toString());
        sink.append(fieldDelim);
        sink.append("startLine");
        sink.append(valueDelim);
        sink.append(sample.startLine);
        sink.append(fieldDelim);
        sink.append("endLine");
        sink.append(valueDelim);
        sink.append(sample.endLine);
        sink.append(fieldDelim);
        sink.append("sampleCode");
        sink.append(valueDelim);
        sink.append(sample.sampleCode.toString());
        sink.append(fieldDelim);
    }
    private SampleUtil(){}
}

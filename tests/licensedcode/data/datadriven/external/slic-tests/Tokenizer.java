/*
 * Copyright (c) 2005-2007 Henri Sivonen
 * Copyright (c) 2007-2013 Mozilla Foundation
 * Portions of comments Copyright 2004-2010 Apple Computer, Inc., Mozilla 
 * Foundation, and Opera Software ASA.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a 
 * copy of this software and associated documentation files (the "Software"), 
 * to deal in the Software without restriction, including without limitation 
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 * and/or sell copies of the Software, and to permit persons to whom the 
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in 
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 * DEALINGS IN THE SOFTWARE.
 */

/*
 * The comments following this one that use the same comment syntax as this 
 * comment are quotes from the WHATWG HTML 5 spec as of 2 June 2007 
 * amended as of June 18 2008 and May 31 2010.
 * That document came with this statement:
 * "© Copyright 2004-2010 Apple Computer, Inc., Mozilla Foundation, and 
 * Opera Software ASA. You are granted a license to use, reproduce and 
 * create derivative works of this document."
 */

package nu.validator.htmlparser.impl;

import nu.validator.htmlparser.annotation.Auto;
import nu.validator.htmlparser.annotation.CharacterName;
import nu.validator.htmlparser.annotation.Const;
import nu.validator.htmlparser.annotation.Inline;
import nu.validator.htmlparser.annotation.Local;
import nu.validator.htmlparser.annotation.NoLength;
import nu.validator.htmlparser.common.EncodingDeclarationHandler;
import nu.validator.htmlparser.common.Interner;
import nu.validator.htmlparser.common.TokenHandler;
import nu.validator.htmlparser.common.XmlViolationPolicy;

import org.xml.sax.ErrorHandler;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

/**
 * An implementation of
 * http://www.whatwg.org/specs/web-apps/current-work/multipage/tokenization.html
 * 
 * This class implements the <code>Locator</code> interface. This is not an
 * incidental implementation detail: Users of this class are encouraged to make
 * use of the <code>Locator</code> nature.
 * 
 * By default, the tokenizer may report data that XML 1.0 bans. The tokenizer
 * can be configured to treat these conditions as fatal or to coerce the infoset
 * to something that XML 1.0 allows.
 * 
 * @version $Id$
 * @author hsivonen
 */
public class Tokenizer implements Locator {

    private static final int DATA_AND_RCDATA_MASK = ~1;

    public static final int DATA = 0;

    public static final int RCDATA = 1;

    public static final int SCRIPT_DATA = 2;

    public static final int RAWTEXT = 3;

    public static final int SCRIPT_DATA_ESCAPED = 4;

    public static final int ATTRIBUTE_VALUE_DOUBLE_QUOTED = 5;

    public static final int ATTRIBUTE_VALUE_SINGLE_QUOTED = 6;

    public static final int ATTRIBUTE_VALUE_UNQUOTED = 7;

    public static final int PLAINTEXT = 8;

    public static final int TAG_OPEN = 9;

    public static final int CLOSE_TAG_OPEN = 10;

    public static final int TAG_NAME = 11;

    public static final int BEFORE_ATTRIBUTE_NAME = 12;

    public static final int ATTRIBUTE_NAME = 13;

    public static final int AFTER_ATTRIBUTE_NAME = 14;

    public static final int BEFORE_ATTRIBUTE_VALUE = 15;

    public static final int AFTER_ATTRIBUTE_VALUE_QUOTED = 16;

    public static final int BOGUS_COMMENT = 17;

    public static final int MARKUP_DECLARATION_OPEN = 18;

    public static final int DOCTYPE = 19;

    public static final int BEFORE_DOCTYPE_NAME = 20;

    public static final int DOCTYPE_NAME = 21;

    public static final int AFTER_DOCTYPE_NAME = 22;

    public static final int BEFORE_DOCTYPE_PUBLIC_IDENTIFIER = 23;

    public static final int DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED = 24;

    public static final int DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED = 25;

    public static final int AFTER_DOCTYPE_PUBLIC_IDENTIFIER = 26;

    public static final int BEFORE_DOCTYPE_SYSTEM_IDENTIFIER = 27;

    public static final int DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED = 28;

    public static final int DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED = 29;

    public static final int AFTER_DOCTYPE_SYSTEM_IDENTIFIER = 30;

    public static final int BOGUS_DOCTYPE = 31;

    public static final int COMMENT_START = 32;

    public static final int COMMENT_START_DASH = 33;

    public static final int COMMENT = 34;

    public static final int COMMENT_END_DASH = 35;

    public static final int COMMENT_END = 36;

    public static final int COMMENT_END_BANG = 37;

    public static final int NON_DATA_END_TAG_NAME = 38;

    public static final int MARKUP_DECLARATION_HYPHEN = 39;

    public static final int MARKUP_DECLARATION_OCTYPE = 40;

    public static final int DOCTYPE_UBLIC = 41;

    public static final int DOCTYPE_YSTEM = 42;

    public static final int AFTER_DOCTYPE_PUBLIC_KEYWORD = 43;

    public static final int BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = 44;

    public static final int AFTER_DOCTYPE_SYSTEM_KEYWORD = 45;

    public static final int CONSUME_CHARACTER_REFERENCE = 46;

    public static final int CONSUME_NCR = 47;

    public static final int CHARACTER_REFERENCE_TAIL = 48;

    public static final int HEX_NCR_LOOP = 49;

    public static final int DECIMAL_NRC_LOOP = 50;

    public static final int HANDLE_NCR_VALUE = 51;

    public static final int HANDLE_NCR_VALUE_RECONSUME = 52;

    public static final int CHARACTER_REFERENCE_HILO_LOOKUP = 53;

    public static final int SELF_CLOSING_START_TAG = 54;

    public static final int CDATA_START = 55;

    public static final int CDATA_SECTION = 56;

    public static final int CDATA_RSQB = 57;

    public static final int CDATA_RSQB_RSQB = 58;

    public static final int SCRIPT_DATA_LESS_THAN_SIGN = 59;

    public static final int SCRIPT_DATA_ESCAPE_START = 60;

    public static final int SCRIPT_DATA_ESCAPE_START_DASH = 61;

    public static final int SCRIPT_DATA_ESCAPED_DASH = 62;

    public static final int SCRIPT_DATA_ESCAPED_DASH_DASH = 63;

    public static final int BOGUS_COMMENT_HYPHEN = 64;

    public static final int RAWTEXT_RCDATA_LESS_THAN_SIGN = 65;

    public static final int SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN = 66;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPE_START = 67;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPED = 68;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN = 69;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPED_DASH = 70;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH = 71;

    public static final int SCRIPT_DATA_DOUBLE_ESCAPE_END = 72;

    public static final int PROCESSING_INSTRUCTION = 73;

    public static final int PROCESSING_INSTRUCTION_QUESTION_MARK = 74;

    /**
     * Magic value for UTF-16 operations.
     */
    private static final int LEAD_OFFSET = (0xD800 - (0x10000 >> 10));

    /**
     * UTF-16 code unit array containing less than and greater than for emitting
     * those characters on certain parse errors.
     */
    private static final @NoLength char[] LT_GT = { '<', '>' };

    /**
     * UTF-16 code unit array containing less than and solidus for emitting
     * those characters on certain parse errors.
     */
    private static final @NoLength char[] LT_SOLIDUS = { '<', '/' };

    /**
     * UTF-16 code unit array containing ]] for emitting those characters on
     * state transitions.
     */
    private static final @NoLength char[] RSQB_RSQB = { ']', ']' };

    /**
     * Array version of U+FFFD.
     */
    private static final @NoLength char[] REPLACEMENT_CHARACTER = { '\uFFFD' };

    // [NOCPP[

    /**
     * Array version of space.
     */
    private static final @NoLength char[] SPACE = { ' ' };

    // ]NOCPP]

    /**
     * Array version of line feed.
     */
    private static final @NoLength char[] LF = { '\n' };

    /**
     * Buffer growth parameter.
     */
    private static final int BUFFER_GROW_BY = 1024;

    /**
     * "CDATA[" as <code>char[]</code>
     */
    private static final @NoLength char[] CDATA_LSQB = { 'C', 'D', 'A', 'T',
            'A', '[' };

    /**
     * "octype" as <code>char[]</code>
     */
    private static final @NoLength char[] OCTYPE = { 'o', 'c', 't', 'y', 'p',
            'e' };

    /**
     * "ublic" as <code>char[]</code>
     */
    private static final @NoLength char[] UBLIC = { 'u', 'b', 'l', 'i', 'c' };

    /**
     * "ystem" as <code>char[]</code>
     */
    private static final @NoLength char[] YSTEM = { 'y', 's', 't', 'e', 'm' };

    private static final char[] TITLE_ARR = { 't', 'i', 't', 'l', 'e' };

    private static final char[] SCRIPT_ARR = { 's', 'c', 'r', 'i', 'p', 't' };

    private static final char[] STYLE_ARR = { 's', 't', 'y', 'l', 'e' };

    private static final char[] PLAINTEXT_ARR = { 'p', 'l', 'a', 'i', 'n', 't',
            'e', 'x', 't' };

    private static final char[] XMP_ARR = { 'x', 'm', 'p' };

    private static final char[] TEXTAREA_ARR = { 't', 'e', 'x', 't', 'a', 'r',
            'e', 'a' };

    private static final char[] IFRAME_ARR = { 'i', 'f', 'r', 'a', 'm', 'e' };

    private static final char[] NOEMBED_ARR = { 'n', 'o', 'e', 'm', 'b', 'e',
            'd' };

    private static final char[] NOSCRIPT_ARR = { 'n', 'o', 's', 'c', 'r', 'i',
            'p', 't' };

    private static final char[] NOFRAMES_ARR = { 'n', 'o', 'f', 'r', 'a', 'm',
            'e', 's' };

    /**
     * The token handler.
     */
    protected final TokenHandler tokenHandler;

    protected EncodingDeclarationHandler encodingDeclarationHandler;

    // [NOCPP[

    /**
     * The error handler.
     */
    protected ErrorHandler errorHandler;

    // ]NOCPP]

    /**
     * Whether the previous char read was CR.
     */
    protected boolean lastCR;

    protected int stateSave;

    private int returnStateSave;

    protected int index;

    private boolean forceQuirks;

    private char additional;

    private int entCol;

    private int firstCharKey;

    private int lo;

    private int hi;

    private int candidate;

    private int strBufMark;

    private int prevValue;

    protected int value;

    private boolean seenDigits;

    protected int cstart;

    /**
     * The SAX public id for the resource being tokenized. (Only passed to back
     * as part of locator data.)
     */
    private String publicId;

    /**
     * The SAX system id for the resource being tokenized. (Only passed to back
     * as part of locator data.)
     */
    private String systemId;

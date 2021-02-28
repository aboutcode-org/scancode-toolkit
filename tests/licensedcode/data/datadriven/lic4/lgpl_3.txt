package com.tecnick.htmlutils.xhtmltranscoder;

import java.util.Vector;

import com.tecnick.htmlutils.htmlentities.HTMLEntities;
import com.tecnick.htmlutils.htmlstrings.HTMLStrings;

/**
 * Java class that quickly converts HTML code to XHTML. <br />
 * XHTMLTranscoder is a <em>fast</em> transcoder useful to convert HTML code
 * in real-time. <br />
 * This class do not check headers, it checks only the general rules for tags,
 * attributes and nesting:
 * <ul>
 * <li>tags (elements) names in lowercase</li>
 * <li>attributes names in lowercase</li>
 * <li>elements nesting</li>
 * <li>elements termination</li>
 * <li>unquoted attributes</li>
 * <li>unminimized attributes</li>
 * <li>unterminated empty tags</li>
 * <li>preserve other languages elements (php, asp, jsp, ...)</li>
 * </ul>
 * <br/>Copyright (c) 2004-2005 Tecnick.com S.r.l (www.tecnick.com) Via Ugo
 * Foscolo n.19 - 09045 Quartu Sant'Elena (CA) - ITALY - www.tecnick.com -
 * info@tecnick.com <br/>
 * Project homepage: <a href="http://xhtmltranscoder.sourceforge.net" target="_blank">http://xhtmltranscoder.sourceforge.net</a><br/>
 * License: http://www.gnu.org/copyleft/lesser.html LGPL
 * 
 * @author Nicola Asuni [www.tecnick.com].
 * @version 1.0.007
 */
public class XHTMLTranscoder {
	
	/**
	 * Object container for XHTML elements definitions
	 */
	private static XHTMLElements xhtml_element = null;
	
	/**
	 * Initialize transcoder loading XHTML elements data from default dir or current dir in case of error.
	 */
	public XHTMLTranscoder() {
		// try to get configuration files from JAR archive
		this("/com/tecnick/htmlutils/xhtmltranscoder/config/");
	}
	
	/**
	 * Initialize transcoder loading XHTML elemets data from config_dir.
	 * 
	 * @param config_dir String directory or URL where config files are stored
	 */
	public XHTMLTranscoder(String config_dir) {
		xhtml_element = new XHTMLElements(config_dir);
	}
	
	/**
	 * Returns an XHTMLElements object containing the XHTML elements data.
	 * 
	 * @return XHTMLElements object
	 */
	public XHTMLElements getXHTMLelements() {
		return xhtml_element;
	}
	
	/**
	 * Trancode using default parameters (false, false, "UTF-8")
	 * 
	 * @param code_to_clean String text to transcode
	 * @return String transcoded text
	 */
	public String transcode(String code_to_clean) {
		return transcode(code_to_clean, false, false, "UTF-8");
	}
	
	/**
	 * Get generic HTML and returns XHTML code cleaned up. <br />
	 * XHTMLTranscoder is a <em>fast</em> transcoder useful to convert HTML
	 * code in real-time. <br />
	 * This class do not check headers, it checks only the general rules for
	 * tags, attributes and nesting:
	 * <ul>
	 * <li>tags (elements) names in lowercase</li>
	 * <li>attributes names in lowercase</li>
	 * <li>elements nesting</li>
	 * <li>elements termination</li>
	 * <li>unquoted attributes</li>
	 * <li>unminimized attributes</li>
	 * <li>unterminated empty tags</li>
	 * <li>preserve other languages elements (php, asp, jsp, ...)</li>
	 * </ul>
	 * 
	 * @param code_to_clean String the text to transcode
	 * @param indent boolean if true return the text indented
	 * @param entities_off boolean if true replace htmlentities with extended chars
	 * @param encoding String document encoding (e.g.: "UTF-8")
	 * @return String the transcoded text
	 */
	public String transcode(String code_to_clean, boolean indent, boolean entities_off, String encoding) {
		
		//CRLF to LF (windows to unix style)
		code_to_clean = code_to_clean.replaceAll("\r\n", "\n");
		
		//convert to unicode
		code_to_clean = HTMLStrings.getEncodedString(code_to_clean, encoding, "UTF-8");
		// remove HTML code entities
		code_to_clean = HTMLEntities.unhtmlentities(code_to_clean);
		
		int codelen = code_to_clean.length(); //number of characters in code
		String xhtml_code = ""; //this will contain the return code
		Vector tag_list = new Vector(); //list of open (not closed) tags
		boolean subtag = false; //is true when a subtag is found (php, jsp, asp tags)
		boolean checkindent = true; //check if add indentation before non tag data
		int i = 0;
		int j = -1;
		int k = 0;
		
		String currentchar;
		
		while (i < codelen) {
			currentchar = code_to_clean.substring(i, i + 1);
			// OPEN TAG FOUND =======================================
			if ((currentchar.compareTo("<") == 0) && 
					(code_to_clean.substring(i + 1, i + 2).matches("[a-zA-Z]"))) { //we are inside a tag
				checkindent = true;
				j++;
				tag_list.add(j, "");
				do { //get tag name
					tag_list.set(j, tag_list.elementAt(j).toString()
							+ currentchar.toLowerCase()); //put open tag in a list
					i++;
					currentchar = code_to_clean.substring(i, i + 1);
				} while (currentchar.matches("[a-zA-Z0-9]"));
				
				//clean tabs and newlines from the end of the code
				if (xhtml_code.length() > 0) {
					while (xhtml_code.substring(xhtml_code.length() - 1, xhtml_code.length()).matches("[\t\n]")) {
						xhtml_code = xhtml_code.substring(0, xhtml_code.length() - 1); //remove character
					}
				}
				//check if some special tags has been closed
				if (j > 0) {
					if (tag_list.elementAt(j - 1).toString().compareToIgnoreCase(tag_list.elementAt(j).toString().substring(1)) == 0) {
						String lct_name = (String) tag_list.elementAt(j - 1);
						String tagkey = xhtml_element.getXHTMLTags().getKey("name", lct_name);
						if ((tagkey != null)
								&& (xhtml_element.getXHTMLTags().getInt(tagkey, "endtag", 0) == 2)) {
							if (indent) { //add indentation
								xhtml_code += "\n"; //put tag in a new line
								for (k = 0; k < (j - 1); k++) {
									xhtml_code += "\t"; //indent code
								}
							}
							xhtml_code += "</" + lct_name + ">"; // add closing tag
							tag_list.remove(j); //remove tag from list
							tag_list.set(j - 1, "<" + lct_name + "");
							j--;
						}
					}
				}
				if (indent) { //add indentation
					xhtml_code += "\n"; //put tag in a new line
					for (k = 0; k < j; k++) {
						xhtml_code += "\t"; //indent code
					}
				}
				xhtml_code += (String) tag_list.elementAt(j);
				tag_list.set(j, tag_list.elementAt(j).toString().substring(1)); // remove first "<" from the tag
				String tagkey = xhtml_element.getXHTMLTags().getKey("name", (String) tag_list.elementAt(j));
				boolean emptyelement = false;
				if (tagkey != null) {
					emptyelement = (xhtml_element.getXHTMLTags().getInt(tagkey, "endtag", 0) == 0);
				}
				while ((currentchar.compareTo(">") != 0)
						|| ((currentchar.compareTo(">") == 0) && (subtag))) { // check tag attributes
					if (!subtag) { //we are not inside a subtag
						if (currentchar.matches("[a-zA-Z]")) { // attribute found
							String attributename = "";
							do { //get attribute name
								attributename += currentchar.toLowerCase();
								i++;
								currentchar = code_to_clean.substring(i, i + 1);
							} while (currentchar.matches("[a-zA-Z0-9:-]"));
							xhtml_code += " " + attributename; //get attribute name
							boolean attribdef = false;
							boolean attribquote = false;
							boolean attribvoid = false;
							while (currentchar.matches("[= \t\n\r\f\"]")) {
								// look for attribute data
								if (currentchar.compareTo("=") == 0) {
									attribdef = true;
								}
								if (currentchar.compareTo("\"") == 0) {
									if (attribquote) {
										attribvoid = true; //found void attribute
										break;
									}
									attribquote = true; //attribute start with quotes
								}
								i++;
								currentchar = code_to_clean.substring(i, i + 1);
							}
							if (!attribdef) {
								//fix attribute minimization
								String attribkey = xhtml_element.getXHTMLAttributes().getKey("name", attributename);
								if ((attribkey != null)
										&& (xhtml_element.getXHTMLAttributes().getInt(attribkey, "type", 0) == 1)) {
									xhtml_code += "=\"" + attributename + "\"";
								} else {
									xhtml_code += "=\"\"";
								}
							} else {
								if (attribvoid) {
									xhtml_code += "=\"\"";
								} else { //get attribute data
									String attributedata = "";
									if (attribquote) {
										while (currentchar.compareTo("\"") != 0) {
											// look for attribute data
											attributedata += currentchar;
											i++;
											currentchar = code_to_clean.substring(i, i + 1);
										}
										xhtml_code += "=\"" + attributedata + "\"";
									} else {
										while (currentchar.matches("[^> \t\n\r\f]")
												|| (subtag)) { //look for attribute data
											if (currentchar.compareTo("<") == 0) {
												subtag = true; //we are inside a subtag
											}
											attributedata += currentchar;
											i++;
											currentchar = code_to_clean.substring(i, i + 1);
											if ((currentchar.compareTo(">") == 0) && (subtag)) {
												subtag = false; //the subtag is ended
												attributedata += currentchar;
											}
										}
										xhtml_code += "=\"" + attributedata + "\"";
									}
								}
							} //end get attribute data
						} //end attribute found
						if (currentchar.compareTo(">") != 0) {
							do { //eleminate spaces, tabs, newlines
								i++;
								currentchar = code_to_clean.substring(i, i + 1);
							} while (currentchar.matches("[ \t\n\r\f]"));
						}
					} // end if not subtag
					else { //we are inside a subtag
						xhtml_code += currentchar;
						i++;
						currentchar = code_to_clean.substring(i, i + 1);
					}
					if (currentchar.compareTo("<") == 0) {
						subtag = true; //we are inside a subtag
					} else {
						if ((currentchar.compareTo(">") == 0) && (subtag)) {
							subtag = false; //the subtag is ended
							xhtml_code += currentchar;
							i++;
							currentchar = code_to_clean.substring(i, i + 1);
						}
					}
				} // END check tag attributes
				if ((code_to_clean.substring(i - 2, i).compareTo(" /") == 0)
						|| (code_to_clean.substring(i - 1, i).compareTo("/") == 0)
						|| emptyelement) {
					xhtml_code += " />"; // get close empty element
					tag_list.remove(j); //remove tag from list
					j--;
				} else {
					xhtml_code += ">"; // get open tag
				}
			} // END OPEN TAG FOUND =======================================
			//	 CLOSE TAG FOUND =======================================
			else if ((currentchar.compareTo("<") == 0)
					&& (code_to_clean.substring(i + 1, i + 2).compareTo("/") == 0)) {
				// we are inside a closing tag
				checkindent = true;
				String closetag = "";
				i += 2;
				currentchar = code_to_clean.substring(i, i + 1);
				//get tag name
				do {
					closetag += currentchar.toLowerCase();
					i++;
					currentchar = code_to_clean.substring(i, i + 1);
				} while (currentchar.matches("[a-zA-Z0-9]"));
				//remove white spaces
				while (currentchar.matches("[ \t\n\r\f]")) {
					i++;
					currentchar = code_to_clean.substring(i, i + 1);
				}
				//clean tabs and newlines from the end of the code
				if (xhtml_code.length() > 0) {
					while (xhtml_code.substring(xhtml_code.length() - 1, xhtml_code.length()).matches("[\t\n]")) {
						// remove character
						xhtml_code = xhtml_code.substring(0, xhtml_code.length() - 1);
					}
				}
				
				//check tag nesting
				if (j >= 0) { //check if the open tag list is not empty
					int n = j + 1;
					String closetagcode = "";
					do { //check if tag is nested correctly
						n--;
						if(n>=0) {
							if (indent) { //add indentation
								//make indentation (before closing tag)
								closetagcode += "\n"; //put tag in a new line
								for (k = 0; k < n; k++) {
									closetagcode += "\t"; //indent code
								}
							}
							// add close tag
							closetagcode += "</" + tag_list.elementAt(n) + ">";
						}
					} while ((n >= 0) && (closetag.compareToIgnoreCase((String) tag_list.elementAt(n)) != 0));
					if ((n >= 0) && (closetag.compareToIgnoreCase((String) tag_list.elementAt(n)) == 0)) {
						xhtml_code += closetagcode;
						for (k = j; k < n; k--) {
							tag_list.remove(j); //remove tag from list
						}
						j = n - 1; //remove closed tags from list
					}
				}
			} // END CLOSE TAG FOUND =======================================
			//	NOT TAG DATA FOUND =======================================
			else {
				if (checkindent && ((j < 0) || ((j >= 0) 
						&& (tag_list.elementAt(j).toString().compareTo("pre") != 0)))) {
					// make indentation (before non tag data)
					//ignore tabs and newlines
					if (currentchar.matches("[\t\n]")) {
						while (currentchar.matches("[\t\n]")) {
							i++;
							currentchar = code_to_clean.substring(i, i + 1);
						}
						i--;
						currentchar = "";
					}
					if (indent) { //add indentation
						xhtml_code += "\n"; //put data in a new line
						for (k = 0; k < j; k++) {
							xhtml_code += "\t"; //indent code
						}
					}
					checkindent = false;
				}
				//check for other kind of tags
				if (currentchar.compareTo("<") == 0) { //special char found
					// check if we are inside a tag of a different language (php, asp, jsp...)
					// character that identify the tag (%,?,#)
					String closechar = code_to_clean.substring(i + 1, i + 2); 
					if ((closechar.compareTo("%") == 0)
							|| (closechar.compareTo("?") == 0)
							|| (closechar.compareTo("#") == 0)) {
						//we are inside a subtag
						while (code_to_clean.substring(i, i + 2).compareTo(closechar + ">") != 0) {
							xhtml_code += currentchar;
							i++;
							currentchar = code_to_clean.substring(i, i + 1);
						}
						i++;
						xhtml_code += closechar + ">";
					} else if (code_to_clean.substring(i + 1, i + 4).compareTo("!--") == 0) { //we are inside an HTML comment
						while (code_to_clean.substring(i, i + 3).compareTo("-->") != 0) {
							xhtml_code += currentchar;
							i++;
							currentchar = code_to_clean.substring(i, i + 1);
						}
						i += 2;
						xhtml_code += "-->";
					} else if (code_to_clean.substring(i + 1, i + 2).compareTo("!") == 0) { 
//						we are inside a DOCTYPE DTD or something like this
						while (code_to_clean.substring(i + 1, i + 2).compareTo(
						">") != 0) {
							xhtml_code += currentchar;
							i++;
							currentchar = code_to_clean.substring(i, i + 1);
						}
						i++;
						xhtml_code += ">";
					} else {
						xhtml_code += "&lt;";
					}
				} else {
					if (code_to_clean.length() >= (i + 4)) {
						String temp_entity = code_to_clean.substring(i, i + 4);
						if ((currentchar.compareTo("&") == 0) 
								&& ((temp_entity.compareTo("&lt;") == 0) 
										|| (temp_entity.compareTo("&gt;") == 0)
										|| (code_to_clean.substring(i, i + 2).compareTo("&#") == 0))) {
							xhtml_code += currentchar;
						} else {
							//convert character entity in HTML equivalent
							xhtml_code += HTMLEntities.htmlentities(currentchar);
						}
					} else {
						//convert character entity in HTML equivalent
						xhtml_code += HTMLEntities.htmlentities(currentchar);
					}
				}
			} //END NOT TAG DATA FOUND =======================================
			i++;
		} //end while (html parsing)
		//	close unclosed tags
		if (j >= 0) {
			for (int n = j; n >= 0; n--) {
				String closetagcode = "";
				if (indent) { //add indentation
					closetagcode += "\n"; //put tag in a new line
					for (k = 0; k < n; k++) {
						closetagcode += "\t"; //indent code
					}
				}
				closetagcode += "</" + tag_list.elementAt(n) + ">";
				xhtml_code += closetagcode;
			}
		}
		// fix script comment newline
		xhtml_code = xhtml_code.replaceAll("//<!\\[CDATA\\[", "\n//<![CDATA["); 
		// fix script comment newline
		xhtml_code = xhtml_code.replaceAll("</script>", "\n</script>"); 
		// eliminate newlines from the beginning of document
		xhtml_code = xhtml_code.replaceAll("^[\n]+", ""); 
		if (entities_off) {
			// remove htmlentities
			xhtml_code = HTMLEntities.unhtmlentities(xhtml_code);
		}
		// restore original encoding
		xhtml_code = HTMLStrings.getEncodedString(xhtml_code, "UTF-8", encoding);
		return xhtml_code;
	}
	
}
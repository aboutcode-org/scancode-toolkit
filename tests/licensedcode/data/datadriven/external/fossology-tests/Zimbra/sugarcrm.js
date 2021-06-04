/*
 * ***** BEGIN LICENSE BLOCK *****
 * Version: ZPL 1.2
 * 
 * The contents of this file are subject to the Zimbra Public License
 * Version 1.2 ("License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://www.zimbra.com/license
 * 
 * Software distributed under the License is distributed on an "AS IS"
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
 * the License for the specific language governing rights and limitations
 * under the License.
 * 
 * The Original Code is: Zimbra Collaboration Suite Web Client
 * 
 * The Initial Developer of the Original Code is Zimbra, Inc.
 * Portions created by Zimbra are Copyright (C) 2005, 2006 Zimbra, Inc.
 * All Rights Reserved.
 * 
 * Contributor(s):
 * 
 * ***** END LICENSE BLOCK *****
 */
/*
 * General purpose library for interacting with SugarCRM/SOAP.
 * @author Mihai Bazon
 *
 * START DATE: Sep 13, 2005
 * REQUIRES: AjxStringUtil, AjxCallback, AjxSoapDoc, AjxRpc, AjxMD5
 */

/*
 * @param server -- the fully qualified address of the SugarCRM's soap.php file
 * @param callback -- user defined function that will be called when the
 *                    request is over
 *
 * "callback" may be an AjxCallback in which case it gets called in whatever
 * object environment you specified, or can be a plain function reference which
 * will be called in the context of this object.
 */
function ZmSugarCrm(server, callback) {
	this.server = "/zimbra/zimlets/sugarcrm/sugarcrm.jsp?address=" +
		AjxStringUtil.urlEncode(server);
	if (typeof callback == "function")
		callback = new AjxCallback(this, callback);
	this.userCallback = callback;
	this.callback = new AjxCallback(this, ZmSugarCrm._requestFinished);
};

//* CLASS FUNCTIONS

ZmSugarCrm.NS = "http://www.sugarcrm.com/sugarcrm";

// ZmSugarCrm.RE_ANSWER = /<ns1:(\w+Response)[^>]*>(.*?)<\x2fns1:\1>/; // $2 will deliver results
// ZmSugarCrm.RE_RESULT = /<return\s+xsi:type=([\x22\x27])(.*?)\1>(.*?)<\x2freturn>/;

ZmSugarCrm._getAnArray = function(a) {
	if (!(typeof a == "object" && a instanceof Array))
		a = (typeof a != "undefined") ? [ a ] : [];
	return a;
};

//* INSTANCE FUNCTIONS

ZmSugarCrm.prototype.toString = function() { return "ZmSugarCrm"; };

/// Will be called in the context of the current object, therefore "this" isn't
/// a reference to the ZmSugarCrm class but to one of its instances.
///
/// This function does some method-dependent checks and sets up some
/// attributes, calling userCallback thereafter.
ZmSugarCrm._requestFinished = function(args) {
	// decode the response here
	var answer = AjxXmlDoc.createFromXml(args.text).toJSObject(true, false);
	// skip uninteresting stuff
	this.answer = answer = answer.Body[this.method + "Response"]["return"];
	switch (this.method) {
	    case "login":
		if (answer.error.number == 0)
			// login succeeded
			this.session_id = answer.id;
		else {
			this.session_id = null;
			this.user = this.passwd = "";
		}
		break;

	    case "logout":
		this.session_id = null;
		this.user = this.passwd = "";
		break;

	    case "search":
		// the outside world should expect answer.contacts to be an
		// array after a successful search.
		answer.contacts = ZmSugarCrm._getAnArray(answer.item);
		break;
	}
	this.userCallback.run(args, answer);
};

ZmSugarCrm.prototype._makeEnvelope = function(method) {
	this.method = method;
	return AjxSoapDoc.create(method, ZmSugarCrm.NS, "sugar");
};

ZmSugarCrm.prototype._rpc = function(envelope) {
	return AjxRpc.invoke(envelope.getXml(), this.server, null, this.callback);
};

// This is provided by the SugarCRM SOAP in order to test connectivity
// it should echo the passed string.
ZmSugarCrm.prototype.test = function(str) {
	var env = this._makeEnvelope("test");
	env.set("string", str, null);
	this._rpc(env);
};

// Throws an exception if:
//     mode == true and object isn't logged in, or
//     mode == false and object is logged in.
ZmSugarCrm.prototype._checkLoggedIn = function(mode) {
	if (mode) {
		if (!this.session_id)
			throw new AjxException("Not logged in", "OK", "ZmSugarCrm.logout");
	} else {
		if (this.session_id)
			throw new AjxException("Already logged in", "OK", "ZmSugarCrm.login");
	}
};

ZmSugarCrm.prototype.login = function(user, passwd) {
	this._checkLoggedIn(false);
	var env = this._makeEnvelope("login");
	var auth = {
		user_name : this.user = user,
		password  : this.passwd = AjxMD5.hex_md5(passwd),
		version   : "1.1"
	};
	env.set("user_auth", auth);
	env.set("application", "Zimbra");
	this._rpc(env);
};

ZmSugarCrm.prototype.logout = function() {
	this._checkLoggedIn(true);
	var env = this._makeEnvelope("logout");
	env.set("session", this.session_id);
	this._rpc(env);
};

// The SugarCRM "search" method actually takes an user_name and a password,
// even though we previously logged in and have a session ID.  What a shame.  I
// think this is poor design, therefore I made the function only work if we
// have a session_id and use the object's user and password. [1]
ZmSugarCrm.prototype.search = function(query) {
	this._checkLoggedIn(true);
	var env = this._makeEnvelope("search");
	env.set("user_name", this.user);
	env.set("password", this.passwd);
	env.set("name", query);
	this._rpc(env);
};

// see [1] above
//
// SugarCRM will add a contact even if one with the exact same properties
// already exists.  This may be good or bad, depending on the calling
// application.  I chosen to let this function do what it does--if you want to
// only add a contact when it's not there already, feel free to call "search"
// beforehand and see what it returns.
ZmSugarCrm.prototype.createContactThing = function(args, method) {
	this._checkLoggedIn(true);
	var env = this._makeEnvelope(method);
	env.set("user_name", this.user);
	env.set("password", this.passwd);
	env.set("first_name", args.first_name || '');
	env.set("last_name", args.last_name || '');
	env.set("email_address", args.email_address || '');
	this._rpc(env);
};

// see [1] above
ZmSugarCrm.prototype.createContact = function(args) {
	return this.createContactThing(args, "create_contact");
};

// see [1] above
ZmSugarCrm.prototype.createLead = function(args) {
	return this.createContactThing(args, "create_lead");
};

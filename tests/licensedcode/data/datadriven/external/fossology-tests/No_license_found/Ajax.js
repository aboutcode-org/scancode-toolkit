enyo.kind({
	name: "enyo.Ajax",
	kind: enyo.Async,
	published: {
		cacheBust: true,
		/**
			The URL for the service.  This can be a relative URL if used to fetch resources bundled with the application.
		*/
		url: "",
		/**
			The HTTP method to use for the request, defaults to GET.  Supported values include
			"GET", "POST", "PUT", and "DELETE".
		*/
		method: "GET", // {value: "GET", options: ["GET", "POST", "PUT", "DELETE"]},
		/**
			How the response will be handled. 
			Supported values are: <code>"json", "text", "xml"</code>.
		*/
		handleAs: "json", // {value: "json", options: ["text", "json", "xml"]},
		/**
			The Content-Type header for the request as a String.
		*/
		contentType: "application/x-www-form-urlencoded",
		/**
			If true, makes a synchronous (blocking) call, if supported.  Synchronous requests
			are not supported on HP webOS.
		*/
		sync: false,
		/**
			Optional additional request headers as a JS object, e.g. 
			<code>{ "X-My-Header": "My Value", "Mood": "Happy" }</code>, or null.
		*/
		headers: null,
		/**
			The content for the request body for POST method.  If this is not set, params will be used instead.
		*/
		postBody: "",
		/**
			The optional user name to use for authentication purposes.
		*/
		username: "",
		/**
			The optional password to use for authentication purposes.
		*/
		password: ""
	},
	//* @protected
	constructor: function(inParams) {
		enyo.mixin(this, inParams);
		this.inherited(arguments);
	},
	//* @public
	/**
		Send the ajax request with parameters _inParams_.
	*/
	go: function(inParams) {
		this.startTimer();
		this.xhr(inParams);
		return this;
	},
	//* @protected
	xhr: function(inParams) {
		var parts = this.url.split("?");
		var uri = parts.shift() || "";
		var args = parts.join("?").split("&");
		//
		var body = enyo.isString(inParams) ? inParams : enyo.Ajax.objectToQuery(inParams);
		if (this.method == "GET") {
			if (body) {
				args.push(body);
				body = null;
			}
			if (this.cacheBust) {
				args.push(Math.random());
			}
		}
		//
		var url = [uri, args.join("&")].join("?");
		//
		var xhr_headers = {
			"Content-Type": this.contentType
		};
		enyo.mixin(xhr_headers, this.headers);
		//
		enyo.xhr.request({
			url: url,
			method: this.method,
			callback: enyo.bind(this, "receive"),
			body: body,
			headers: xhr_headers,
			sync: window.PalmSystem ? false : this.sync,
			username: this.username,
			password: this.password
		});
	},
	receive: function(inText, inXhr) {
		if (this.isFailure(inXhr)) {
			this.fail(inXhr.status);
		} else {
			this.respond(this.xhrToResponse(inXhr));
		}
	},
	xhrToResponse: function(inXhr) {
		if (inXhr) {
			return this[(this.handleAs || "text") + "Handler"](inXhr);
		}
	},
	isFailure: function(inXhr) {
		// Usually we will treat status code 0 and 2xx as success.  But in webos, if url is a local file,
		// 200 is returned if the file exists, 0 otherwise.  So we workaround this by treating 0 differently if
		// the app running inside webos and the url is not http.
		//return ((!window.PalmSystem || this.isHttpUrl()) && !inStatus) || (inStatus >= 200 && inStatus < 300);
		return (inXhr.status !== 0) && (inXhr.status < 200 || inXhr.status >= 300);
	},
	xmlHandler: function(inXhr) {
		return inXhr.responseXML;
	},
	textHandler: function(inXhr) {
		return inXhr.responseText;
	},
	jsonHandler: function(inXhr) {
		var r = inXhr.responseText;
		try {
			return r && enyo.json.parse(r);
		} catch (x) {
			console.warn("Ajax request set to handleAs JSON but data was not in JSON format");
			return r;
		}
	},
	statics: {
		objectToQuery: function(/*Object*/ map) {
			var enc = encodeURIComponent;
			var pairs = [];
			var backstop = {};
			for (var name in map){
				var value = map[name];
				if (value != backstop[name]) {
					var assign = enc(name) + "=";
					if (enyo.isArray(value)) {
						for (var i=0; i < value.length; i++) {
							pairs.push(assign + enc(value[i]));
						}
					} else {
						pairs.push(assign + enc(value));
					}
				}
			}
			return pairs.join("&");
		}
	}
});

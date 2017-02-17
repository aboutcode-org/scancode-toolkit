/*
 #
 # Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

 */

// Creates a bar chart given an array of objects with a 'name' and 'val'
// attributes
function ScancodeDataTable(tagId, data){
    var licenseCopyrightData = toLicenseAndCopyrightFormat(data);
    var fileInfoData = toFileInfoFormat(data);
    var pkgInfoData = toPkgInfoFormat(data);

    this.showLicenseAndCopyright = function(){
        table = $(tagId).DataTable();
        table.clear();
        table.columns( '.license_copyright_col' ).visible( true );
        table.columns( '.file_info_col' ).visible( false );
        table.columns( '.pkg_info_col' ).visible( false );
        table.rows.add(licenseCopyrightData);
        table.draw();
    }

    this.showFileInfo = function () {
        table = $(tagId).DataTable();
        table.clear();
        table.columns( '.license_copyright_col' ).visible( false );
        table.columns( '.file_info_col' ).visible( true );
        table.columns( '.pkg_info_col' ).visible( false );
        table.rows.add(fileInfoData);
        table.draw();
    };

    this.showPkgInfo = function () {
        table = $(tagId).DataTable();
        table.clear();
        table.columns( '.license_copyright_col' ).visible( false );
        table.columns( '.file_info_col' ).visible( false );
        table.columns( '.pkg_info_col' ).visible( true );
        table.rows.add(pkgInfoData);
        table.draw();
    };

    // Define a pre-filter
    this.addFilter = function(filter) {
        // Custom Filter on selected tree node
        $.fn.dataTable.ext.search.push(filter);
        return this;
    };

    render(licenseCopyrightData);

    // Render the DataTable by specifying Copyright and License
    function render(data) {
        return $(tagId).DataTable( {
            "scrollX": true,
            "autoWidth": true,
            // data is in format: [[col1, col2], [col1, col2], ...]
            "data": data,
            "order": [[0, 'asc'], [2, 'asc'], [3, 'asc']],
            "columns": [
                { "title": "Path", "data": "path"},
                { "class": "license_copyright_col", "title": "What", "data": "what", width:"50px"},
                { "class": "license_copyright_col", "title": "Start Line", "data": "start_line", width:"50px"},
                { "class": "license_copyright_col",  "title": "End Line", "data": "end_line", width:"50px"},
                { "class": "license_copyright_col",  "orderable": false, "data": null, 'defaultContent': '', "width":"1px"},
                { "class": "license_copyright_col",  "title": "Info", "data": "info"},
                { "class": "file_info_col",  "title": "Type", "data": "type", width:"50px"},
                { "class": "file_info_col",  "title": "Name", "data": "name"},
                { "class": "file_info_col",  "title": "Extension", "data": "extension", width:"50px"},
                { "class": "file_info_col",  "title": "Date", "data": "date", width:"50px"},
                { "class": "file_info_col",  "title": "Size", "data": "size", width:"50px"},
                { "class": "file_info_col",  "title": "SHA1", "data": "sha1"},
                { "class": "file_info_col",  "title": "MD5", "data": "md5"},
                { "class": "file_info_col",  "title": "File count", "data": "files_count", width:"50px"},
                { "class": "file_info_col",  "title": "MIME type", "data": "mime_type"},
                { "class": "file_info_col",  "title": "File Type", "data": "file_type"},
                { "class": "file_info_col",  "title": "Language", "data": "programming_language"},
                { "class": "file_info_col",  "title": "Is binary", "data": "is_binary", width:"30px"},
                { "class": "file_info_col",  "title": "Is text", "data": "is_text", width:"30px"},
                { "class": "file_info_col",  "title": "Is archive", "data": "is_archive", width:"30px"},
                { "class": "file_info_col",  "title": "Is media", "data": "is_media", width:"30px"},
                { "class": "file_info_col",  "title": "Is source", "data": "is_source", width:"30px"},
                { "class": "file_info_col",  "title": "Is script", "data": "is_script", width:"30px"},
                { "class": "pkg_info_col",  "title": "Type", "data": "pkg_type"},
                { "class": "pkg_info_col",  "title": "Packaging", "data": "pkg_packaging"},
                { "class": "pkg_info_col",  "title": "Primary language", "data": "pkg_primary_language"},
            ],
            // This is called just before the row is rendered
            "rowCallback": function( row, data, index ) {
                // Add expansion toggle for license rows
                if ( data['what'] == "License" ) {
                    $('td:eq(4)', row).addClass( 'details-control' );
                }
            },
            "language": {
                "zeroRecords": "No clues found"
            }
        } );
    };

    // Custom row expansion listener
    $(tagId).on( "click", 'td.details-control', function() {
        var table = $(tagId).DataTable();
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        tr.toggleClass('shown');
        if ( row.child.isShown() ) {
            row.child.hide();
        }
        else {
            row.child( format(row.data())).show();
        }
    });

    // Formatting function for row details - modify as you need
    function format( d ) {
        // `d` is the original data object for the row
        return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
            '<tr>'+
            '<td><b>Category:</b></td>'+
            '<td>'+d.category+'</td>'+
            '</tr>'+
            '<tr>'+
            '<td><b>DejaCode URL:</b></td>'+
            '<td><a href="'+d.dejacode_url+'" target="_blank">'+d.dejacode_url+'</a></td>'+
            '</tr>'+
            '</table>';
    }

    // Return license and copyright data in table format
    function toLicenseAndCopyrightFormat(jsonData){
        return $.map(jsonData, function(x){
            // Add all license columns here
            licenseData = [];
            if('licenses' in x && x.licenses != []) {
                licenseData = $.map(x.licenses, function(y){
                    return [$.extend(y, {
                        "path" : x.path,
                        "what": "License",
                        "start_line": y.start_line || "",
                        "end_line": y.end_line || "",
                        "info": y.short_name || "",
                        "type" : "",
                        "name" : "",
                        "extension": "",
                        "date" : "",
                        "size" : "",
                        "sha1" : "",
                        "md5" : "",
                        "files_count" : "",
                        "mime_type" : "",
                        "file_type" : "",
                        "programming_language" : "",
                        "is_binary" : "",
                        "is_text" : "",
                        "is_archive" : "",
                        "is_media" : "",
                        "is_source" : "",
                        "is_script" : "",
                        "pkg_type" : "",
                        "pkg_packaging" : "",
                        "pkg_primary_language" : ""
                    })];
                })};
            // Add all copyright columns here
            copyrightData = [];
            if('copyrights' in x && x.copyrights != []) {
                copyrightData = $.map(x.copyrights, function(y){
                    return [$.extend(y, {
                        "path" : x.path,
                        "what": "Copyright",
                        "start_line": y.start_line || "",
                        "end_line": y.end_line || "",
                        // somehow we return sometimes something else than an Array?
                        // see https://github.com/nexB/scancode-toolkit/issues/362#issuecomment-259942416
                        "info": (y.statements && 
                        			((Array.isArray(y.statements) && y.statements.join("</br>"))
                        			||
                        			(typeof y.statements === "string" && y.statements))
                        		) || "",
                        "type" : "",
                        "name" : "",
                        "extension": "",
                        "date" : "",
                        "size" : "",
                        "sha1" : "",
                        "md5" : "",
                        "files_count" : "",
                        "mime_type" : "",
                        "file_type" : "",
                        "programming_language" : "",
                        "is_binary" : "",
                        "is_text" : "",
                        "is_archive" : "",
                        "is_media" : "",
                        "is_source" : "",
                        "is_script" : "",
                        "pkg_type" : "",
                        "pkg_packaging" : "",
                        "pkg_primary_language" : ""
                    })];
                })};
            emailData = [];
            if('emails' in x && x.emails != []) {
                emailData = $.map(x.emails, function(y){
                    return [$.extend(y, {
                        "path" : x.path,
                        "what": "Email",
                        "start_line": y.start_line || "",
                        "end_line": y.end_line || "",
                        "info": y.email || "",
                        "type" : "",
                        "name" : "",
                        "extension": "",
                        "date" : "",
                        "size" : "",
                        "sha1" : "",
                        "md5" : "",
                        "files_count" : "",
                        "mime_type" : "",
                        "file_type" : "",
                        "programming_language" : "",
                        "is_binary" : "",
                        "is_text" : "",
                        "is_archive" : "",
                        "is_media" : "",
                        "is_source" : "",
                        "is_script" : "",
                        "pkg_type" : "",
                        "pkg_packaging" : "",
                        "pkg_primary_language" : ""
                    })];
                })};
            urlData = [];
            if('urls' in x && x.urls != []) {
                urlData = $.map(x.urls, function(y){
                    return [$.extend(y, {
                        "path" : x.path,
                        "what": "URL",
                        "start_line": y.start_line || "",
                        "end_line": y.end_line || "",
                        "info": y.url || "",
                        "type" : "",
                        "name" : "",
                        "extension": "",
                        "date" : "",
                        "size" : "",
                        "sha1" : "",
                        "md5" : "",
                        "files_count" : "",
                        "mime_type" : "",
                        "file_type" : "",
                        "programming_language" : "",
                        "is_binary" : "",
                        "is_text" : "",
                        "is_archive" : "",
                        "is_media" : "",
                        "is_source" : "",
                        "is_script" : "",
                        "pkg_type" : "",
                        "pkg_packaging" : "",
                        "pkg_primary_language" : ""
                    })];
                })};

            // Return the concatenation of the two data sets
            return licenseData.concat(copyrightData).concat(emailData).concat(urlData);
        })
    };

    // Return files information data in table format
    function toFileInfoFormat(jsonData){
        return $.map(jsonData, function(x){
            return {
                "path" : x.path,
                "what": "File Info",
                "start_line": "",
                "end_line": "",
                "info": "",
                "type" : x.type || "",
                "name" : x.name || "",
                "extension": x.extension || "",
                "date" : x.date || "",
                "size" : x.size || "",
                "sha1" : x.sha1 || "",
                "md5" : x.md5 || "",
                "files_count" : x.files_count || "",
                "mime_type" : x.mime_type || "",
                "file_type" : x.file_type || "",
                "programming_language" : x.programming_language || "",
                "is_binary" : x.is_binary || "",
                "is_text" : x.is_text || "",
                "is_archive" : x.is_archive || "",
                "is_media" : x.is_media || "",
                "is_source" : x.is_source || "",
                "is_script" : x.is_script || "",
                "pkg_type" : "",
                "pkg_packaging" : "",
                "pkg_primary_language" : ""
             }
        });
    };

    // Return packages data in table format
    function toPkgInfoFormat(jsonData){
        return $.map(jsonData, function(x){
            packageInfoData = [];
            if('packages' in x & x.packages != []) {
                packageInfoData = $.map(x.packages, function(y){
                    return [$.extend(y, {
                        "path" : x.path,
                        "what": "Packages",
                        "start_line": "",
                        "end_line": "",
                        "info": "",
                        "type" : "",
                        "name" : "",
                        "extension": "",
                        "date" : "",
                        "size" : "",
                        "sha1" : "",
                        "md5" : "",
                        "files_count" : "",
                        "mime_type" : "",
                        "file_type" : "",
                        "programming_language" : "",
                        "is_binary" : "",
                        "is_text" : "",
                        "is_archive" : "",
                        "is_media" : "",
                        "is_source" : "",
                        "is_script" : "",
                        "pkg_type" : y.type || "",
                        "pkg_packaging" : y.packaging || "",
                        "pkg_primary_language" : y.primary_language  || ""
                    })];
                })};

            // Return the concatenation of the two data sets
            return packageInfoData;
        })
    };
};
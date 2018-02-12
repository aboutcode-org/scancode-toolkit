/*
#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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
function ScancodeJSTree(tagId, data){
    var icon_file        = "glyphicon glyphicon-file";
    var icon_dir_close   = "glyphicon glyphicon-folder-close";
    var icon_dir_open    = "glyphicon glyphicon-folder-open";
    var file_color       = "icon-secondary";
    var file_color_empty = "icon-empty";
    var dir_color        = "icon-primary";
    var dir_color_empty  = "icon-empty";
    var currNodeData;

    var onNodeSelected = function(e, nodeData) {};
    this.onNodeSelected = function(onNodeSelectedFunc) {
        onNodeSelected = onNodeSelectedFunc;
        return this;
    };

    // Render the jstree with data and listeners
    data = toJSTreeFormat(data).reverse();
    $(tagId).jstree({
        // data is in format: {"id": id, "parent": parent, "text": text, ...}
        "core": {
            "themes" : {
                "stripes": true,
                "responsive": true
            },
            "check_callback" : true,
            "data": data
        },
        "plugins": ["wholerow", "sort"],
        "sort": function(a, b) {
            var lengthA = this.get_node(a).children.length;
            var lengthB = this.get_node(b).children.length;
            if(lengthA == 0 && lengthB == 0){
                // both files
                return a.toLowerCase() > b.toLowerCase() ? 1 : -1;
            } else if(lengthA > 0 && lengthB > 0) {
                // both directories
                return a.toLowerCase() > b.toLowerCase() ? 1 : -1;
            } else {
                // a file vs directory
                return lengthA < lengthB ? 1 : -1;
            }
        }
    }).on("select_node.jstree", function(e, nodeData) {
        onNodeSelected(e, nodeData);
    }).on('open_node.jstree', function(e, data) {
        data.instance.set_icon(data.node,  genIconClass(false, true, ""));
    }).on('close_node.jstree', function(e, data) {
        data.instance.set_icon(data.node,  genIconClass(false, false, ""));
    });

    function genIconClass(isLeaf, isOpen, isEmpty){
        icon  = isLeaf  ? icon_file : (isOpen ? icon_dir_open : icon_dir_close);
        color = isEmpty ? file_color_empty : (isLeaf ? file_color : dir_color);
        return [color, icon].join(" ");
    };

    // Returns a row in the format expected by jstree
    function getJSTreeData(parent, id, text, icon_class){
        return {
            "id": id,
            "parent": parent == "" ? '#' : parent,
            // open the root tree
            "state": {"opened": parent == "" ? true : false},
            "text": text,
            "icon": icon_class
        };
    };

    // Renders json data to jsTree format
    function toJSTreeFormat(jsonData){
        // Sort data by file path to ensure files are seen before directories
        jsonData.sort(function (a, b) {
            return a.path.localeCompare( b.path );
        }).reverse();
        // Keeps track of IDs
        var uniqueIDs = {};

        // Loop through each element and find unique IDs in path
        return $.map(jsonData, function(x) {

            // Creates array in format: ["", "path1", "path2", "file"]
            var paths = x.path.split("/");

            // Loop through path elements and return jsTree rows
            return $.map(paths, function(_, i){
                // build parent and id for each unique path, e.g.
                // (1) parent="",             id="/path1
                // (2) parent="/path1",       id="/path1/path2"
                // (3) parent="/path1/path2", id="/path1/path2/file"
                var parent = paths.slice(0,i).join("/");
                var id = paths.slice(0,i+1).join("/");
                var text = paths[i];

                // Add the jsTree row if ID not in uniqueIDs already
                if(id != "" && !(id in uniqueIDs)){
                    uniqueIDs[id] = true;
                    var isLeaf = (i == paths.length - 1);
                    var isEmpty = isLeaf &&
                        (!('licenses' in x) || x.licenses.length == 0) &&
                        (!('copyrights' in x) || x.copyrights.length == 0) &&
                        (!('emails' in x) || x.emails.length == 0) &&
                        (!('urls' in x) || x.urls.length == 0);
                    var iconClass = genIconClass(isLeaf, false, isEmpty);
                    return getJSTreeData(parent, id, text, iconClass);
                }
            });
        });
    };
};
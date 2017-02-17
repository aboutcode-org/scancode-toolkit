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
function BarChart(chartData, chartOptions, chartSelector){
    var margin = {
        left: chartOptions.margin + this.maxNameWidth(chartData),
        top: chartOptions.margin,
        right: chartOptions.margin + this.maxValueWidth(chartData),
        bottom: chartOptions.margin
    }

    // The chart height is bar height * the number of licenses in the data
    var chartHeight = chartOptions.barHeight * chartData.length

    // Build up the chart (Sum of chart + margin top + margin bottom)
    var boundHeight = chartHeight + margin.top + margin.bottom;

    // Create bounds of chart
    var bounds = d3.select(chartSelector).attr('height', boundHeight);

    // The chart sits within the bounds starting at (margin.left , margin.top)
    var chart = bounds.append('g')
        .attr('transform', 'translate('+ margin.left + ',' + margin.top + ')');

    // Create scaling for x that converts chartData values to pixels
    var xScale = d3.scale.linear()
        // Find the max val in chartData
        .domain([0, d3.max(chartData, function(d) { return d.val; })]);

    // Create scaling for y that converts chartData names to pixels
    var yScale = d3.scale.ordinal()
        .domain(chartData.map(function(d) {return d.name; }))
        .rangeRoundBands([0, chartHeight], 0.1 /* white space percentage */);

    // Creates a d3 axis given a scale (takes care of tick marks and labels)
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient('bottom');

    // Creates a d3 axis given a scale (takes care of tick marks and labels)
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient('left')

    // Creates a graphic tag (<g>) for each bar in the chart
    var bars = chart.selectAll('g')
        .data(chartData)
        .enter().append('g');

    var rects = bars.append('rect')
        .attr('y', function(d) { return yScale(d.name); })
        .attr('height', yScale.rangeBand());

    var texts = bars.append('text')
        .attr('y', function(d) { return yScale(d.name); })
        .attr('dy', '1.2em')
        .text(function(d){ return '(' + d.val + ')'; })
        .style('text-anchor', 'start');

    // Adds the y-axis to the chart if data exists
    if (chartData.length > 0) {
        chart.append('g')
            .attr('class', 'y axis')
            .call(yAxis);
    }

    this.remove = function() {
        chart.remove();
    }

    // Redraws chart and sets width based on available chart width.
    // User needs to call this function whenever the width of the chart changes.
    this.draw = function() {
        var boundWidth = $(chartSelector).width()

        var chartWidth = boundWidth - margin.left - margin.right;

        xScale.range([0, chartWidth]);
        rects.attr('width', function(d) { return xScale(d.val); });
        texts.attr('x', function(d) { return xScale(d.val) + 2; });
    }

    this.draw();
};

$.extend(BarChart.prototype, {
    // Appends a span element with that name to the DOM. Gets the width in
    // pixels. Removes the appended span element from the DOM and returns the
    // width.
    strPixelWidth: function(str) {
        var tmp = $('<span></span>').text(str);
        $('body').append(tmp);
        var width = tmp.width();
        tmp.remove();
        return width;
    },
    // Returns the pixel width of the string with the longest length
    maxNameWidth: function(data) {
        var names = data.map(function(d) { return d.name; });

        var maxStr = '';
        $.each(names, function(i, name) {
            if(name.length > maxStr.length){
                maxStr = name;
            }
        });

        return this.strPixelWidth(maxStr);
    },
    // Returns the pixel width of the value with the longest length
    maxValueWidth: function(data) {
        var maxValue = d3.max(data, function(d) { return d.val; });
        return this.strPixelWidth('(' + maxValue + ')');
    }
});
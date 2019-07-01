/*!
 * ddionrails - visualization.js
 * Copyright 2015-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

import * as d3 from "d3";

// Global vars

// Set margin, width, padding for charts and menu
// Height of chart later set by number of data elements
var margin = { top: 30, right: 40, bottom: 40, left: 200 };
var w = 750 - margin.left - margin.right;
var barPadding = 1;

////////////////////////////////////////////////////////////////////////////////
// Univariate CATEGORY CHART
////////////////////////////////////////////////////////////////////////////////

// Render Univariate category chart
function cat_uni(options) {
  d3.selectAll(".chart").remove();
  var rData = rawData;

  var hideMissings;
  var dataType;

  // Flags for options to modify data or not
  if (options.missings === true) {
    hideMissings = true;
  } else {
    hideMissings = false;
  }
  if (options.weighted === true) {
    dataType = "weighted";
  } else {
    dataType = "frequencies";
  }

  // Build data model for chart
  var data = [];

  for (var i = 0; i < rData.uni[dataType].length; i++) {
    if (hideMissings === true && rData.uni.missings[i]) {
      continue;
    }

    var tmp = [
      rData.uni.values[i],
      rData.uni.labels[i],
      rData.uni[dataType][i]
    ];
    data.push(tmp);
  }
  // Compute height of chart by number of data elements
  var h = 100 + 20 * data.length - margin.top - margin.bottom;

  // Create SVG ELement and append to #chart
  var svg = d3
    .select("#chart")
    .append("svg")
    .attr(
      "viewBox",
      "0 0 " +
        (w + margin.left + margin.right) +
        " " +
        (h + margin.top + margin.bottom)
    )
    .attr("perserveAspectRatio", "xMinYMid")
    .attr("class", "chart")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Color Scale
  var colors = d3.scale.category20c();
  colors.domain(rData.uni.labels);

  // Append rect elements and map with data
  var rects = svg
    .selectAll("rect")
    .data(data)
    .enter()
    .append("rect")
    .style("fill", function(d) {
      return colors(d[1]);
    })
    .attr("class", "rects");

  var text = svg
    .selectAll("text")
    .data(data)
    .enter()
    .append("text")
    .attr("class", "text");

  // Define text labels
  var format;
  if (options.percent === true) {
    var sum = d3.sum(
      data.map(function(d) {
        return d[2];
      })
    );
    format = d3.format("0.1%");
    text.text(function(d) {
      return format(d[2] / sum);
    });
  } else {
    format = d3.format("");
    text.text(function(d) {
      return d[2];
    });
  }

  // X-Scale
  var xScale = d3.scale
    .linear()
    .domain([
      0,
      d3.max(data, function(d) {
        return d3.max(
          d.filter(function(value) {
            return typeof value === "number";
          })
        );
      })
    ])
    .range([0, w]);

  // Y-Scale
  var yScale = d3.scale
    .ordinal()
    .domain(
      data.map(function(d) {
        return d[1];
      })
    )
    .rangeRoundBands([h, 0]);

  // X-Axis
  var xAxis = d3.svg
    .axis()
    .scale(xScale)
    .orient("bottom");

  svg
    .append("g")
    .call(xAxis)
    .attr("class", "axis")
    .attr("transform", "translate(0," + h + ")");

  // Y-Axis
  var str;
  var yAxis = d3.svg
    .axis()
    .scale(yScale)
    .orient("left")
    .tickFormat(function(d) {
      if (d.length > 30) {
        str = d.substr(0, 30) + "...";
      } else {
        str = d;
      }
      return str;
    });

  svg
    .append("g")
    .call(yAxis)
    .attr("class", "axis");

  // Tooltip: on mouseover show label and values
  var tip = d3
    .select("body")
    .append("tip")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // Draw bars
  rects
    .attr("x", 0)
    .attr("y", function(d) {
      return yScale(d[1]);
    })
    .attr("width", function(d) {
      return xScale(d[2]);
    })
    .attr("height", h / data.length - barPadding)
    .on("mouseover", function(d) {
      tip.transition().style("opacity", 1);
      tip.html(function() {
        if (options.percent === true) {
          return "<strong>" + d[1] + ": </strong>" + format(d[2] / sum);
        } else {
          return "<strong>" + d[1] + ": </strong>" + format(d[2]);
        }
      });
      tip
        .style("left", d3.event.pageX + "px")
        .style("top", d3.event.pageY + "px");
    })
    .on("mouseout", function(d) {
      tip.transition().style("opacity", 0);
    });

  //Append Labels
  var barHeight = h / data.length - barPadding;
  text
    .attr("x", function(d) {
      return xScale(d[2]) + 3;
    })
    .attr("y", function(d) {
      return yScale(d[1]) + barHeight / 2 + 2;
    });
}

function render(rawData) {
  if (rawData.scale !== "cat") {
    $("#vis_menu").hide();
    return false;
  }
  ////////////////////////////////////////////////////////////////////////////////
  // Menu
  ////////////////////////////////////////////////////////////////////////////////

  // Create Array of available options from data modell
  var menu2_data = [];
  for (var i in rawData.bi) {
    menu2_data.push(i);
  }

  // Append dropdown menu if bivariate data available
  if (menu2_data.length > 0) {
    var opt_bi = "";
    menu2_data.forEach(function(i, d) {
      opt_bi += "<li><a class='opt_bi chart_nav' href='#'>" + i + "</a></li>";
    });

    d3.select("#chart_nav_dropdown").html(
      "<button type='button' class='btn btn-default dropdown-toggle chart_nav' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>More Options " +
        "<span class='caret '></span>" +
        "</button>" +
        "<ul class='dropdown-menu chart_nav'>" +
        "<li><a class='opt_bi chart_nav' href='#'>Univariate (default)</a></li>" +
        "<li role='separator' class='divider'></li>" +
        "<li class='dropdown-header'>Bivariate Options</li>" +
        opt_bi +
        "</ul>"
    );
  }

  d3.selectAll(".opt_bi").on("click", function() {
    menu2_active = this.innerHTML;
    if (menu2_active === "Univariate (default)") {
      menu2_active = "uni";
    }

    try {
      if (menu2_active === "uni") {
        if (rawData.scale === "cat") {
          cat_uni(options);
        }
      }
    } catch (error) {
      d3.selectAll(".chart").remove();
      d3.select("#chart")
        .append("svg")
        .attr("width", w)
        .attr("height", 300)
        .attr("class", "chart")
        .append("text")
        .text("Not available.")
        .attr("x", 300)
        .attr("y", 100);
    }
  });

  // Control active option in menu 2, default is 'Univariate'
  var menu2_active = "uni";

  // Add option 'weighted' to menu 3 if available in data modell
  if (!("weighted" in rawData.uni)) {
    d3.select("#weighted").attr("disabled", "disabled");
  }

  // Control active options in menu 3
  var options = {
    missings: false, // hide missings
    percent: false, // show in percentages
    weighted: false // use weighted data
  };

  // Choose diagram type by scale
  if (rawData.scale === "cat") {
    cat_uni(options);
  }

  d3.selectAll(".opt").on("click", function() {
    if (d3.select(this).classed("active")) {
      d3.select(this).classed("active", false);
    } else {
      d3.select(this).classed("active", true);
    }

    if (options[this.id] === false) {
      options[this.id] = true;
      if (menu2_active === "uni") {
        if (rawData.scale === "cat") {
          cat_uni(options);
        }
      }
    } else {
      options[this.id] = false;
      if (menu2_active === "uni") {
        if (rawData.scale === "cat") {
          cat_uni(options);
        }
      }
    }
  });
}

function resize() {
  $(window)
    .on("resize", function() {
      charts = $(".chart .chart_missings");
      aspect = charts.width() / charts.height();
      targetWidth = charts.parent().width();

      charts.attr("width", targetWidth);
      charts.attr("height", Math.round(targetWidth / aspect));
    })
    .trigger("resize");
}

window.margin = margin;
window.w = w;
window.barPadding = barPadding;
window.render = render;
window.resize = resize;

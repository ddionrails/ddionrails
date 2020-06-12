/* !
 * ddionrails - visualization.js
 * Copyright 2015-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

import * as d3 from "d3";

// Global vars

// Set margin, width, padding for charts and menu
// Height of chart later set by number of data elements

const context = JSON.parse($("#context_data").text());
const margin = {top: 30, right: 40, bottom: 40, left: 200};
const w = 750 - margin.left - margin.right;
const barPadding = 1;

//
// Univariate CATEGORY CHART
//


/**
 * Shortens all passed axis labels longer than 30 and appends an ellipsis.
 * @param {*} axisLabels
 */
function shortenLabels(axisLabels) {
  axisLabels.each(function() {
    // eslint-disable-next-line no-invalid-this
    const text = d3.select(this);
    if (text.text().length >= 30) {
      text.text(text.text().substr(0, 30) + "...");
    }
  });
}

/**
 * Render Univariate category chart
 * @param {*} options Display options
 */
function catUni(options) {
  d3.selectAll(".chart").remove();
  const rData = context.variable.data;

  const hideMissings = options.missings;
  let dataType;

  // Flags for options to modify data or not
  if (options.weighted === true) {
    dataType = "weighted";
  } else {
    dataType = "frequencies";
  }

  // Build data model for chart
  const data = [];

  for (let i = 0; i < rData.uni[dataType].length; i++) {
    if (hideMissings === true && rData.uni.missings[i]) {
      continue;
    }

    const tmp = [
      rData.uni.values[i],
      rData.uni.labels[i],
      rData.uni[dataType][i],
    ];
    data.push(tmp);
  }
  // Compute height of chart by number of data elements
  const h = 100 + 20 * data.length - margin.top - margin.bottom;

  // Create SVG ELement and append to #chart
  const svg = d3
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
  const colors = d3.scaleOrdinal(d3.schemeCategory10);
  colors.domain(rData.uni.labels);

  // Append rect elements and map with data
  const rects = svg
    .selectAll("rect")
    .data(data)
    .enter()
    .append("rect")
    .style("fill", function(d) {
      return colors(d[1]);
    })
    .attr("class", "rects");

  const text = svg
    .selectAll("text")
    .data(data)
    .enter()
    .append("text")
    .attr("class", "text");

  // Define text labels
  let format;
  if (options.percent === true) {
    const sum = d3.sum(
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
  const xScale = d3.scaleLinear()
    .domain([
      0,
      d3.max(data, function(d) {
        return d3.max(
          d.filter(function(value) {
            return typeof value === "number";
          })
        );
      }),
    ])
    .range([0, w]);

  // Y-Scale
  const yScale = d3.scaleBand()
    .range([h, 0])
    .domain(
      data.map(function(d) {
        return d[1];
      })
    );

  // X-Axis
  const xAxis = d3.axisBottom(xScale);

  svg
    .append("g")
    .call(xAxis)
    .attr("class", "axis")
    .attr("transform", "translate(0," + h + ")");

  const yAxis = d3.axisLeft(yScale);

  svg
    .append("g")
    .call(yAxis)
    .attr("class", "axis")
    .selectAll(".tick text")
    .call(shortenLabels);

  // Tooltip: on mouseover show label and values
  const tip = d3
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

  // Append Labels
  const barHeight = h / data.length - barPadding;
  text
    .attr("x", function(d) {
      return xScale(d[2]) + 3;
    })
    .attr("y", function(d) {
      return yScale(d[1]) + barHeight / 2 + 2;
    });
}

/**
 * Render Chart
 */
function render() {
  if (context.variable.data.scale !== "cat") {
    $("#vis_menu").hide();
    return;
  }
  //
  // Menu
  //

  // Create Array of available options from data model
  const menu2Data = [];
  for (const i in context.variable.data.bi) {
    menu2Data.push(i);
  }


  // Control active option in menu 2, default is 'Univariate'
  const menu2Active = "uni";

  // Add option 'weighted' to menu 3 if available in data modell
  if (!("weighted" in context.variable.data.uni)) {
    d3.select("#weighted").attr("disabled", "disabled");
  }

  // Control active options in menu 3
  const options = {
    missings: false, // hide missings
    percent: false, // show in percentages
    weighted: false, // use weighted data
  };

  // Choose diagram type by scale
  if (context.variable.data.scale === "cat") {
    catUni(options);
  }

  d3.selectAll(".opt").on("click", function() {
    d3.select(this)
      .classed("active", !!d3.select(this).classed("active"));

    if (options[this.id] === false) {
      options[this.id] = true;
      if (menu2Active === "uni") {
        if (context.variable.data.scale === "cat") {
          catUni(options);
        }
      }
    } else {
      options[this.id] = false;
      if (menu2Active === "uni") {
        if (context.variable.data.scale === "cat") {
          catUni(options);
        }
      }
    }
  });
}

$("document").ready(
  function() {
    render();
  }
);

/*!
 * ddionrails - visualization.js
 * Copyright 2015-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

import "d3";

// Global vars

// Set margin, width, padding for charts and menu
// Height of chart later set by number of data elements
var margin = { top: 30, right: 40, bottom: 40, left: 200 };
var w = 750 - margin.left - margin.right;
var h_menu = 40;
var barPadding = 1;

function render(rawData) {
  if (rawData.scale !== "cat") {
    $("#vis_menu").hide();
    return false;
  }
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // Menu
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // Create Array of available options from data modell
  var menu2_data = [];
  for (i in rawData.bi) {
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
        } else if (rawData.scale === "num") {
          density(options);
        }
      } else {
        if (rawData.scale === "cat") {
          draw_biCatChart(options, menu2_active);
        }
        if (rawData.scale === "num") {
          density_bi(options, menu2_active);
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
  } else if (rawData.scale === "num") {
    density(options);
  } else {
    console.log("Error. Not defined.");
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
        if (rawData.scale === "num") {
          density(options);
        }
      } else {
        if (rawData.scale === "cat") {
          draw_biCatChart(options, menu2_active);
        }
        if (rawData.scale === "num") {
          density_bi(options, menu2_active);
        }
      }
    } else {
      options[this.id] = false;
      if (menu2_active === "uni") {
        if (rawData.scale === "cat") {
          cat_uni(options);
        }
        if (rawData.scale === "num") {
          density(options);
        }
      } else {
        if (rawData.scale === "cat") {
          draw_biCatChart(options, menu2_active);
        }
        if (rawData.scale === "num") {
          density_bi(options, menu2_active);
        }
      }
    }
  });

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // Univariate CATEGORY CHART
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

    // Build data modell for chart
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

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // BIVARIATE CATEGORY CHART
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

  function draw_biCatChart(options, menu2_active) {
    var stacked;
    var hideMissings;
    var colors;
    var format;
    var format_axis;

    var rData = JSON.parse(JSON.stringify(rawData));

    // Color Scale
    var colors = d3.scale.category20c().domain(rData.bi[menu2_active].labels);

    // Show missings / hide missings
    if (options.missings === true) {
      hideMissings = true;
    } else {
      hideMissings = false;
    }

    // Show percentages or not
    if (options.percent === true) {
      offset = "expand";
      format = d3.format("0.1%");
      format_axis = d3.format("%");
    } else {
      offset = "";
      format = d3.format("");
      format_axis = d3.format("");
    }

    // unweighted or weighted data
    if (options.weighted === true) {
      dataType = "weighted";
    } else {
      dataType = "frequencies";
    }

    var data = [];
    var indices = [];
    for (var i = 0; i < rData.bi[menu2_active].missings.length; i++) {
      if (rData.bi[menu2_active].missings[i] === true) {
        indices.unshift(i);
      }
    }

    // Build data model for chart
    for (i in rData.bi[menu2_active].categories) {
      id = rData.bi[menu2_active].categories[i].label;
      var freqs = rData.bi[menu2_active].categories[i][dataType];

      if (hideMissings === true) {
        for (i in indices) {
          freqs.splice(indices[i], 1);
        }
      }

      freqs.unshift(id);
      data.push(freqs);
    }

    // Get Value codes and labels
    var labels = rData.bi[menu2_active].labels;
    var values = rData.bi[menu2_active].values;

    if (hideMissings === true) {
      for (var i in indices) {
        labels.splice(indices[i], 1);
      }
    }

    // Map labels with data
    var mapped = labels.map(function(dat, i) {
      return data.map(function(d) {
        return { x: d[0], y: d[i + 1], label: dat, code: values[i] };
      });
    });

    // Stack data (normalized or not)
    stacked = d3.layout.stack().offset(offset)(mapped);

    // Remove current chart
    d3.selectAll(".chart").remove();

    // Set height for chart
    var h = 300 - margin.top - margin.bottom;

    barPadding = 0.2;
    barOutPadding = 0.1;

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

    // X-Scale
    var xScale = d3.scale
      .ordinal()
      .domain(
        stacked[0].map(function(d) {
          return d.x;
        })
      )
      .rangeRoundBands([0, w], barPadding, barOutPadding);

    // Y-Scale
    var yScale = d3.scale
      .linear()
      .domain([
        0,
        d3.max(stacked[stacked.length - 1], function(d) {
          return d.y0 + d.y;
        })
      ])
      .range([h, 0]);

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
    var yAxis = d3.svg
      .axis()
      .scale(yScale)
      .tickFormat(format_axis)
      .orient("left");

    svg
      .append("g")
      .call(yAxis)
      .attr("class", "axis");

    // Draw Bars
    var layer = svg
      .selectAll("layer")
      .data(stacked)
      .enter()
      .append("g")
      .attr("class", "layer")
      .style("fill", function(d) {
        for (i in d) {
          return colors(d[i].label);
        }
      });

    // Tooltip: on mouseover show label and values
    var tip = d3
      .select("body")
      .append("tip")
      .attr("class", "tooltip")
      .style("opacity", 0);

    var rect = layer
      .selectAll("rect")
      .data(function(d) {
        return d;
      })
      .enter()
      .append("rect")
      .attr("x", function(d) {
        return xScale(d.x);
      })
      .attr("y", function(d) {
        return yScale(d.y + d.y0);
      })
      .attr("height", function(d) {
        return yScale(d.y0) - yScale(d.y + d.y0);
      })
      .attr("width", xScale.rangeBand())
      .attr("class", "rect")
      .on("mouseover", function(d, i) {
        tip.transition().style("opacity", 1);
        tip
          .html("<strong>" + d.label + ":</strong> " + format(d.y))
          .style("left", d3.event.pageX + "px")
          .style("top", d3.event.pageY + "px");
      })
      .on("mouseout", function(d) {
        tip.transition().style("opacity", 0);
      });
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // Univariate DENSITY CHART
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // Density draws to charts: density chart + missings chart
  function density(options) {
    // Remove current charts
    d3.selectAll(".chart").remove();
    d3.select(".chart_missings").remove();

    var rData = JSON.parse(JSON.stringify(rawData));

    if (options.weighted === true) {
      dataType = "weighted";
    } else {
      dataType = "density";
    }

    if (options.weighted === true) {
      dataType_missings = "weighted";
    } else {
      dataType_missings = "frequencies";
    }

    // Build data model for density chart
    var data = [];
    var range = d3.range(rData.uni.min, rData.uni.max + 1, rData.uni.by);
    range.map(function(d, i) {
      var tmp = [range[i], rData.uni[dataType][i]];
      data.push(tmp);
    });

    // Set height for chart
    var h = 300 - margin.top - margin.bottom;

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

    // X-Scale
    var xScale = d3.scale
      .ordinal()
      .domain(range)
      .rangePoints([0, w], 0.5);

    // Y-Scale
    var yScale = d3.scale
      .linear()
      .domain([0, d3.max(rData.uni[dataType])])
      .range([h, 0]);

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

    // Apend path
    var path = d3.svg
      .line()
      .x(function(d) {
        return xScale(d[0]);
      })
      .y(function(d) {
        return yScale(d[1]);
      })
      .interpolate("linear");

    svg
      .append("path")
      .attr("class", "line")
      .attr("d", path(data));

    // Missings Chart //

    if (options.missings === false) {
      var rData = rawData;

      // Prepare data
      var dataMissings = [];
      for (var i = 0; i < rData.uni.missings[dataType_missings].length; i++) {
        var tmp = [
          rData.uni.missings.values[i],
          rData.uni.missings.labels[i],
          rData.uni.missings[dataType_missings][i]
        ];
        dataMissings.push(tmp);
      }

      // Add category for vaild cases
      sumValidData = d3.sum(
        data.map(function(d) {
          return d[1];
        })
      );
      dataMissings.push([" ", "valid cases", sumValidData]);

      // Set height for chart
      var h = 80 + 10 * dataMissings.length - margin.top - margin.bottom;

      // Append SVG-Element for missings chart
      var svg2 = d3
        .select("#chart_missings")
        .append("svg")
        .attr(
          "viewBox",
          "0 0 " +
            (w + margin.left + margin.right) +
            " " +
            (h + margin.top + margin.bottom)
        )
        .attr("perserveAspectRatio", "xMinYMid")
        .attr("class", "chart_missings")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // Color Scale (grey)
      var colors = [
        "#d9d9d9",
        "#969696",
        "#000000",
        "#ffffff",
        "#f0f0f0",
        "#bdbdbd",
        "#525252",
        "#737373",
        "#252525",
        "#d9d9d9",
        "#969696",
        "#000000",
        "#ffffff",
        "#f0f0f0",
        "#bdbdbd",
        "#525252",
        "#737373",
        "#252525"
      ];

      // Append rect elements
      var rects = svg2
        .selectAll("rect")
        .data(dataMissings)
        .enter()
        .append("rect")
        .style("fill", function(d, i) {
          if (d[1] === "valid cases") {
            return "steelblue";
          } else {
            return colors[i];
          }
        })
        .attr("class", "rects");

      // Append labels
      var text = svg2
        .selectAll("text")
        .data(dataMissings)
        .enter()
        .append("text")
        .attr("class", "text");

      // Show missings  in % or not
      sumAllData = sumValidData + d3.sum(rData.uni.missings[dataType_missings]);
      if (options.percent === true) {
        format = d3.format("0.1%");
        text.text(function(d) {
          return format(d[2] / sumAllData);
        });
      } else {
        format = d3.format("");
        text.text(function(d) {
          return d[2];
        });
      }

      // X-Scale missings
      var xScale = d3.scale
        .linear()
        .domain([
          0,
          d3.max(dataMissings, function(d) {
            return d3.max(
              d.filter(function(value) {
                return typeof value === "number";
              })
            );
          })
        ])
        .range([0, w]);

      // Y-Scale missings
      var yScale = d3.scale
        .ordinal()
        .domain(
          dataMissings.map(function(d) {
            return d[1];
          })
        )
        .rangeRoundBands([h, 0]);

      // X-Axis missings
      var xAxis = d3.svg
        .axis()
        .scale(xScale)
        .orient("bottom");

      svg2
        .append("g")
        .call(xAxis)
        .attr("class", "axis")
        .attr("transform", "translate(0," + h + ")");

      // Y-Axis missings
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

      svg2
        .append("g")
        .call(yAxis)
        .attr("class", "axis");

      // Tooltip: on mouseover show label and values
      var tip = d3
        .select("body")
        .append("tip")
        .attr("class", "tooltip")
        .style("opacity", 0);

      // Draw bars and append labels
      rects
        .attr("x", 0)
        .attr("y", function(d) {
          return yScale(d[1]);
        })
        .attr("width", function(d) {
          return xScale(d[2]);
        })
        .attr("height", h / dataMissings.length - 1)
        .on("mouseover", function(d) {
          tip.transition().style("opacity", 1);
          tip.html(function() {
            if (options.percent === true) {
              return (
                "<strong>" + d[1] + ": </strong>" + format(d[2] / sumAllData)
              );
            } else {
              return "<strong>" + d[1] + ": </strong>" + format(d[2]);
            }
          });
          tip.style("left", d3.event.pageX + "px");
          tip.style("top", d3.event.pageY + "px");
        })
        .on("mouseout", function(d) {
          tip.transition().style("opacity", 0);
        });

      var barHeight = h / dataMissings.length - 1;
      text
        .attr("x", function(d) {
          return xScale(d[2]) + 3;
        })
        .attr("y", function(d) {
          return yScale(d[1]) + barHeight / 2 + 2;
        });
    }

    if (options.missings === true) {
      d3.select(".chart_missings").remove();
    }
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // BIVARIATE DENSITY CHART
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

  function density_bi(options, menu2_active) {
    // Remove current chart
    d3.selectAll(".chart").remove();
    d3.select(".chart_missings").remove();

    var rData = JSON.parse(JSON.stringify(rawData));
    var data = [];
    var labels = [];

    // Unweighted / weighted
    if (options.weighted === true) {
      dataType = "weighted";
    } else {
      dataType = "density";
    }

    // Prepare Data
    var range = d3.range(rData.uni.min, rData.uni.max + 1, rData.uni.by);
    for (i in rData.bi[menu2_active].categories) {
      id = rData.bi[menu2_active].categories[i].label;
      freqs = rData.bi[menu2_active].categories[i][dataType];

      //freqs.unshift(id);
      data.push(freqs);
      labels.push(id);
    }

    // Set height for chart
    var h = 300 - margin.top - margin.bottom;

    // Append SVG-Element to #chart
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

    // X-Scale
    var xScale = d3.scale
      .ordinal()
      .domain(labels)
      .rangeRoundBands([0, w], 0, 0);

    // Y-Scale
    var yScale = d3.scale
      .ordinal()
      .domain(range)
      .rangeRoundBands([h, 0], 0, 0.5);

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
    var yAxis = d3.svg
      .axis()
      .scale(yScale)
      .orient("left");

    svg
      .append("g")
      .call(yAxis)
      .attr("class", "axis");

    var gAxis = svg
      .append("g")
      .attr("class", "axis")
      .call(yAxis);

    // Calculate maximum length of axis ticks in order to avoid an overlap with axis label
    var maxLabelWidth = 0;
    gAxis.selectAll("text").each(function() {
      var width = this.getBBox().width;
      if (width > maxLabelWidth) {
        maxLabelWidth = width;
      }
    });

    // Append y-Axis Label
    var yAxisLabel = svg
      .append("text")
      .attr(
        "transform",
        "translate(" + (-maxLabelWidth - 15) + "," + h / 2 + ")rotate(-90)"
      )
      .attr("class", "labels")
      .attr("text-anchor", "middle")
      .text(rData.label);

    // Add a minified, mirrored path diagram for each category
    for (i = 0; i < data.length; i++) {
      var xScale2 = d3.scale
        .ordinal()
        .domain(d3.range(rData.uni.min, rData.uni.max + 1, rData.uni.by))
        .rangeRoundBands([0, h], 0, 0.5);

      var yScale2 = d3.scale
        .linear()
        .domain([
          0,
          d3.max(data, function(d) {
            return d3.max(d);
          })
        ])
        .range([
          xScale.rangeBand() * i + xScale.rangeBand() / 2,
          xScale.rangeBand() * (i + 1) - 5
        ]);

      var path = d3.svg
        .area()
        .x(function(d, i) {
          return xScale2(range[i]);
        })
        .y(function(d) {
          return yScale2(d);
        })
        .y0(function(d) {
          return yScale2(-d);
        })
        .interpolate("linear");

      svg
        .append("path")
        .attr("class", "line")
        .attr("d", path(data[i]))
        .attr("transform", "rotate(-90)")
        .style("fill", "steelblue")
        .attr("transform", "translate(0," + h + ") rotate(-90)");
    }

    // Missings Chart //

    if (options.missings === false) {
      var format;
      if (options.percent === true) {
        offset = "expand";
        format = d3.format("0.1%");
        format_axis = d3.format("%");
      } else {
        offset = "";
        format = d3.format("");
        format_axis = d3.format("");
      }
      if (options.weighted === true) {
        dataType_missings = "weighted";
      } else {
        dataType_missings = "frequencies";
      }

      var data = [];
      for (var i in rData.bi[menu2_active].categories) {
        id = rData.bi[menu2_active].categories[i].label;

        sumValidCases = d3.sum(rData.bi[menu2_active].categories[i][dataType]);
        freqs =
          rData.bi[menu2_active].categories[i].missings[dataType_missings];

        freqs.unshift(id);
        freqs.push(sumValidCases);
        data.push(freqs);
      }

      // Sum valid Cases (in all categories)
      var sumValidData = d3.sum(data);

      labels = rData.bi[menu2_active].categories[0].missings.labels;
      values = rData.bi[menu2_active].categories[0].missings.values;

      // Add category for valid cases
      labels.push("valid cases");
      values.push(" "); // no code for valid cases

      // Map labels with data
      var mapped = labels.map(function(dat, i) {
        return data.map(function(d) {
          return { x: d[0], y: d[i + 1], label: dat, code: values[i] };
        });
      });

      // Stack data (normalized or not)
      var stacked = d3.layout.stack().offset(offset)(mapped);

      // Set height and padding for missings chart
      var h2 = 150 - margin.top - margin.bottom;
      var barPadding = 0.2;
      var barOutPadding = 0.1;

      // Append SVG Element to #chart_missings
      var svg2 = d3
        .select("#chart_missings")
        .append("svg")
        .attr(
          "viewBox",
          "0 0 " +
            (w + margin.left + margin.right) +
            " " +
            (h + margin.top + margin.bottom)
        )
        .attr("perserveAspectRatio", "xMinYMid")
        .attr("class", "chart_missings")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // X-Scale
      var xScale = d3.scale
        .ordinal()
        .domain(
          stacked[0].map(function(d) {
            return d.x;
          })
        )
        .rangeRoundBands([0, w], barPadding, barOutPadding);

      // Y-Scale
      var yScale = d3.scale
        .linear()
        .domain([
          0,
          d3.max(stacked[stacked.length - 1], function(d) {
            return d.y0 + d.y;
          })
        ])
        .range([h2, 0]);

      // X-Axis
      var xAxis = d3.svg
        .axis()
        .scale(xScale)
        .orient("bottom");

      svg2
        .append("g")
        .call(xAxis)
        .attr("class", "axis")
        .attr("transform", "translate(0 ," + h2 + ")");

      // Y-Axis
      var yAxis = d3.svg
        .axis()
        .scale(yScale)
        .ticks(3)
        .tickFormat(format_axis)
        .orient("left");

      svg2
        .append("g")
        .call(yAxis)
        .attr("class", "axis");

      // Color Scale (grey)
      var colors = [
        "#d9d9d9",
        "#969696",
        "#000000",
        "#ffffff",
        "#f0f0f0",
        "#bdbdbd",
        "#525252",
        "#737373",
        "#252525",
        "#d9d9d9",
        "#969696",
        "#000000",
        "#ffffff",
        "#f0f0f0",
        "#bdbdbd",
        "#525252",
        "#737373",
        "#252525"
      ];

      // Append bars
      var layer = svg2
        .selectAll("layer")
        .data(stacked)
        .enter()
        .append("g")
        .attr("class", "layer")
        .style("fill", function(d, i) {
          if (d[0].label === "valid cases") {
            return "steelblue";
          } else {
            return colors[i];
          }
        });

      // Tooltip: on mouseover show label and values
      var tip = d3
        .select("body")
        .append("tip")
        .attr("class", "tooltip")
        .style("opacity", 0);

      var rect = layer
        .selectAll("rect")
        .data(function(d) {
          return d;
        })
        .enter()
        .append("rect")
        .attr("x", function(d) {
          return xScale(d.x);
        })
        .attr("y", function(d) {
          return yScale(d.y + d.y0);
        })
        .attr("height", function(d) {
          return yScale(d.y0) - yScale(d.y + d.y0);
        })
        .attr("width", xScale.rangeBand())
        .attr("class", "rect")
        .on("mouseover", function(d) {
          tip.transition().style("opacity", 1);
          tip
            .html("<strong>" + d.label + ": </strong>" + format(d.y))
            .style("left", d3.event.pageX + "px")
            .style("top", d3.event.pageY + "px");
        })
        .on("mouseout", function(d) {
          tip.transition().style("opacity", 0);
        });
    }

    if (options.missings === true) {
      d3.select(".chart_missings").remove();
    }
  }
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
window.h_menu = h_menu;
window.barPadding = barPadding;
window.render = render;
window.resize = resize;
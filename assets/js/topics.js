/* !
 * ddionrails - topics.js
 * Copyright 2018-2019
 * Licensed under AGPL
 * (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 *
 * Topic List
 *
 * This script visualizes a tree structure of topics and their concepts,
 * questions and variables using the fancytree library.
 * Make sure you set study and language variable in template,
 * else api calls will not work.
 *
 * @author cstolpe
 *
 *
 */

// Credit to https://github.com/mar10/fancytree/issues/793
import "jquery.fancytree";
import "jquery.fancytree/dist/modules/jquery.fancytree.filter";
import "jquery.fancytree/dist/modules/jquery.fancytree.glyph";

$.ui.fancytree.debugLevel = 0; // set debug level; 0:quiet, 1:info, 2:debug

const context = JSON.parse($("#context_data").text());
const study = context["study"];
const language = context["language"];

// Get current URL to read 'open' Parameter for opening specified node
const urlString = window.location.href;
let url = new URL(urlString);
const open = url.searchParams.get("open");

// Define buttons, which are shown when you hover over a topic or concept
// This buttons will be append to the nodes defined by fancytree
let filterOptionsString = `
<span class='btn-group btn-group-sm filter-options' data-container='body'
  role='group'>
    <button type='button' data-tooltip='tooltip' data-container='body'
      title='Show all related variables' onclick='filter(this, \"variable\")'
      class='btn btn-link filter-option-variable' >
        <span class='fas fa-chart-bar' aria-hidden='true'></span>
    </button>
    <button type='button' class='btn btn-link filter-option-question'
      data-tooltip='tooltip' data-container='body'
      title='Show all related questions' onclick='filter(this, \"question\")'>
        <span class='fas fa-tasks' aria-hidden='true'></span>
    </button>
    <button type='button' data-tooltip='tooltip' data-container='body'
      title='Add all related variables to one of your baskets'
      onclick='addToBasket(this)' class='btn btn-link' data-toggle='modal'
      data-target='#topic-list-add-to-basket'>
        <span class='fas fa-shopping-cart' aria-hidden='true'></span>
    </button>
`;
const clipboard = `
<button type='button' data-tooltip='tooltip' data-container='body'
  title='Copy URL' onclick='copyUrlToClipboard(this)' class='btn btn-link'>
    <span class='fas fa-copy' aria-hidden='true'></span>
</button>
`;
const filterAndClipboard = filterOptionsString + clipboard + "</span>";
filterOptionsString = filterOptionsString + "</span>";
const newApiUrl = new URL("api/basket-variables/", window.location.origin);
const apiUrl =
  location.protocol +
  "//" +
  window.location.host +
  "/api/topics/" +
  study +
  "/" +
  language;
const baseUrl =
  location.protocol +
  "//" +
  window.location.host +
  "/" +
  study +
  "/topics/" +
  language;

// Define what the tree structure will look like, for more information and
// options see https://github.com/mar10/fancytree.
// Build and append tree to #tree.
$(function() {
  $("#tree").fancytree({
    extensions: ["filter", "glyph"],
    types: {
      topic: {
        icon: "fas fa-cogs",
      },
      concept: {
        icon: "fas fa-cog",
      },
      variable: {
        icon: "fas fa-chart-bar",
      },
      question: {
        icon: "fas fa-tasks",
      },
    },
    filter: {
      counter: false,
      mode: "hide",
    },
    icon(event, data) {
      return data.typeInfo.icon;
    },
    glyph: {
      preset: "awesome5",
      map: {
        _addClass: "",
        checkbox: "fas fa-square",
        checkboxSelected: "fas fa-check-square",
        checkboxUnknown: "fas fa-square",
        radio: "fas fa-circle",
        radioSelected: "fas fa-circle",
        radioUnknown: "fas fa-dot-circle",
        dragHelper: "fas fa-arrow-right",
        dropMarker: "fas fa-long-arrow-right",
        error: "fas fa-exclamation-triangle",
        expanderClosed: "fas fa-caret-right",
        expanderLazy: "fas fa-angle-right",
        expanderOpen: "fas fa-caret-down",
        loading: "fas fa-spinner fa-pulse",
        nodata: "fas fa-meh",
        noExpander: "",
        /** Default node icons.
         * (Use tree.options.icon callback to define
         * custom icons based on node data)
         */
        doc: "fas fa-file",
        docOpen: "fas fa-file",
        folder: "fas fa-folder",
        folderOpen: "fas fa-folder-open",
      },
    },
    source: {
      url: apiUrl, // load data from api (topic and concepts only)
      cache: false,
    },
    renderNode(event, data) {
      const node = data.node;
      const $spanTitle = $(node.span).find("span.fancytree-title");
      if ($(node.span).find("span.filter-options").length === 0) {
        if (node.type === "topic") {
          // insert additional copy_to_clipboard button to button group
          $spanTitle.after(filterAndClipboard);
        }
        if (node.type === "concept") {
          $spanTitle.after(filterOptionsString);
        }
      }
    },
    // When tree fully loaded:
    // if parameter 'open' is set in URL open specified node
    init(event, data) {
      if (open != null) {
        const node = $("#tree").fancytree("getNodeByKey", open);
        node.makeVisible();
        node.setActive(true);
      }
    },
  });

  // Search the tree for search string
  $("#btn-search").on("click", function() {
    $("#tree")
      .fancytree("getTree")
      .filterBranches($("#search").val(), {
        autoExpand: true,
      });
  });

  // Trigger search on enter
  $(".search-bar").keypress(function(e) {
    if (e.which === 13) {
      // Enter key pressed
      $("#btn-search").click();
    }
  });
});

// On click on a topic or concept show all variables oder questions
function filter(node, type) {
  // show spinner while loading
  $("#tree_variables").empty();
  $(".sk-flow").show();
  $("#tree")
    .find("button[class*='-btn-active']")
    .removeClass("variable-btn-active question-btn-active");
  $(node).toggleClass(type + "-btn-active");

  const activeNode = $.ui.fancytree.getNode(node);

  let url = apiUrl + "/" + activeNode.key;
  if (type === "variable") {
    url += "?variable_html=true";
  }
  if (type === "question") {
    url += "?question_html=true";
  }
  jQuery
    .get(url, function(data) {
      $(".sk-flow").hide(); // hide the loading message
      $("#tree_variables").html(data);
      $("#variable_table").DataTable();
    })
    .fail(function() {
      $(".sk-flow").hide(); // hide the loading message
      $("#tree_variables").html(
        "<p><span class='fas fa-exclamation-triangle'" +
        " aria-hidden='true'></span> Load Error!</p>"
      );
    });
}

// Remove all variables and questions from active node
function removeAsyncLoadedData(activeNode, type) {
  const children = activeNode.getChildren();
  const tmp = [];
  if (children) {
    for (let i = 0; i < children.length; i++) {
      // eslint-disable-next-line security/detect-object-injection
      const node = $.ui.fancytree.getNode(children[i]);
      const extraClasses = node.extraClasses || "";
      if (extraClasses.includes("async-data-" + type)) {
        tmp.push(node);
      }
    }
    for (let i = 0; i < tmp.length; i++) {
      // eslint-disable-next-line security/detect-object-injection
      tmp[i].remove();
    }
  }
}

// Remove all child nodes from active node
function removeAllChildren(activeNode, type) {
  const tmp = [];
  activeNode.visit(function(node) {
    if (node.type === type) {
      tmp.push(node);
    }
  }, true);

  for (let i = 0; i < tmp.length; i++) {
    // eslint-disable-next-line security/detect-object-injection
    tmp[i].remove();
  }
}

// Show more information for adding an elment to
// the basket (how many variables will be added to the basket) and render
// a list of the user's baskets
/** */
function addToBasket(el) {
  const node = $.ui.fancytree.getNode(el);
  let url = apiUrl + "/" + node.key + "?variable_list=false";
  $("#basket_list").empty();
  let numVariables = "?";
  if (node.type === "variable") {
    numVariables = 1;
    // Set number of variables in add to basket modal
    $("#number_of_variables").text(numVariables);
  } else {
    jQuery.getJSON(url, function(data) {
      numVariables = data.variable_count || "?";
      // Set number of variables in add to basket modal
      $("#number_of_variables").text(numVariables);
    });
  }

  url = new URL(`api/topics/${study}/baskets`, window.location.origin);
  jQuery.getJSON(url, function(data) {
    if (data.user_logged_in) {
      if (data.baskets.length === 0) {
        const redirectCreateBasketUrl =
          location.protocol +
          "//" +
          window.location.host +
          "/workspace/baskets";
        $("#basket_list").append(
          "<p><a class='btn btn-primary' href='" +
          redirectCreateBasketUrl +
          "'>Create a basket</a></p>"
        );
      }
      for (let i = 0; i < data.baskets.length; i++) {
        const addToBasketFunction =
          // eslint-disable-next-line security/detect-object-injection
          "addToBasketRequest('" + node.key + "'," + data.baskets[i].id + ")";
        $("#basket_list").append(
          "<p><button class='btn btn-primary' onclick=" +
          addToBasketFunction +
          ">Add to basket <strong>" +
          // eslint-disable-next-line security/detect-object-injection
          data.baskets[i].name +
          "</strong></button></p>"
        );
      }
    } else {
      const redirectLoginUrl =
        location.protocol + "//" + window.location.host + "/workspace/login";
      $("#basket_list").append(
        "<p><a class='btn btn-primary' href='" +
        redirectLoginUrl +
        "'>Please log in to use this function.</a></p>"
      );
    }
  });
}

/**
 * Call basket variable API to add variables via their topic or concept.
 *
 * Note: This module is somewhat convoluted.
 *       The obscurity of the code makes this somewhat blackbox like.
 *       There is no guarantee that this comment is 100% accurate
 *
 * There are two ways to add variables here, by topic and by concept.
 * We can identify the type by the prefix of the nodekey.
 * It is either topic_ or concept_.
 * Following the underscore (_) is the name of the topic/concept.
 * @author Dominique Hansen
 *
 * @param {string} nodeKey The key attribute of a FancyTreeNode. Will probably
 *                         be in the form of (topic|concept)_name
 * @param {number} basketId The id of the basket, to which to add the variables.
 */
function addToBasketRequest(nodeKey, basketId) {
  const regexp = /^(\w*?)_(_?\w*)$/;
  const typeNameArray = nodeKey.match(regexp);
  const type = typeNameArray[1];
  const name = typeNameArray[2];
  const postData = {
    basket: basketId,
  };
  // eslint-disable-next-line security/detect-object-injection
  postData[type + "_name"] = name;

  const client = new XMLHttpRequest();
  client.open("POST", newApiUrl, true);
  client.setRequestHeader("Content-type", "application/json");

  const csrfToken = $("[name=csrfmiddlewaretoken]").val();
  client.withCredentials = true;
  client.setRequestHeader("X-CSRFToken", csrfToken);
  client.setRequestHeader("Accept", "application/json");

  client.onreadystatechange = function() {
    if (client.readyState === XMLHttpRequest.DONE) {
      const status = client.status;
      const _response = JSON.parse(client.responseText);
      if (200 <= status <= 201) {
        $("#basket_success").text(_response["detail"]);

        $("#basket_success").removeClass("hidden");
      }
      if (status >= 400) {
        $("#basket_error").text(_response["detail"]);
        $("#basket_error").removeClass("hidden");
      }
    }
  };
  client.send(JSON.stringify(postData));
}

// Remove status alerts from modal after modal was closed
$("#topic-list-add-to-basket").on("hidden.bs.modal", function() {
  $("#basket_success").addClass("hidden");
  $("#basket_error").addClass("hidden");
});

// Copy the URL of selected topic to clipboard
function copyUrlToClipboard(el) {
  const activeNode = $.ui.fancytree.getNode(el);

  // URL need to be selectable to be copied to clipboard,
  // append temporary element
  url = baseUrl + "?open=" + activeNode.key;
  const tmp = document.createElement("textarea");
  tmp.value = url;
  document.body.appendChild(tmp);
  tmp.select();
  document.execCommand("copy");
  document.body.removeChild(tmp);

  // Show feedback message (url copied)
  $(el)
    .attr("title", "Copied URL")
    .tooltip("fixTitle")
    .tooltip("show");
  setTimeout(function() {
    $(el)
      .attr("title", "Copy URL")
      .tooltip("fixTitle");
  }, 1000);
}

window.filter = filter;
window.removeAsyncLoadedData = removeAsyncLoadedData;
window.removeAllChildren = removeAllChildren;
window.addToBasket = addToBasket;
window.addToBasketRequest = addToBasketRequest;
window.copyUrlToClipboard = copyUrlToClipboard;

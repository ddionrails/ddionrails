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


const context = JSON.parse($("#context_data")[0].textContent);
const study = context["study"];

const newApiUrl = new URL("api/basket-variables/", window.location.origin);
const apiUrl =
  location.protocol +
  "//" +
  window.location.host +
  "/api/topics/" +
  context["study"] +
  "/" +
  context["language"];
const baseUrl =
  location.protocol +
  "//" +
  window.location.host +
  "/" +
  context["study"] +
  "/topics/" +
  context["language"];


/**
 * Retrieve and display related questions or variables for a topic or concept.
 *
 * @param {HTMLButtonElement} node A button Element associated with a topic or concept
 */
function filter(node) {
  // show spinner while loading
  const relatedVariableSection = document.querySelector("#tree_variables > div");
  relatedVariableSection.innerHTML = "";

  const loadingErrorIcon = document.getElementById("loading-error");
  loadingErrorIcon.classList.add("hidden");

  const loadingIcon = document.getElementById("loading-icon");
  loadingIcon.classList.remove("hidden");

  node = $(node);
  node.removeClass("variables-btn-active questions-btn-active");


  const activeNode = $.ui.fancytree.getNode(node);

  let url = apiUrl + "/" + activeNode.key;
  if (node.hasClass("variables")) {
    url += "?variable_html=true";
    node.toggleClass("variables-btn-active");
  }
  if (node.hasClass("questions")) {
    url += "?question_html=true";
    node.toggleClass("questions-btn-active");
  }
  // This should be switched to the new API so we can retrieve JSON
  // and build the Table ourselves.
  fetch(url).then(
    function(response) {
      loadingIcon.classList.add("hidden");
      response.text().then(
        function(data) {
          const parser = new DOMParser();
          const parsed = parser.parseFromString(data, "text/html");
          const nodes = parsed.querySelectorAll("body > *");
          nodes.forEach(function(node) {
            relatedVariableSection.appendChild(node);
          });
        }
      );
    }
  ).catch( function(_error) {
    loadingIcon.classList.add("hidden");
    loadingErrorIcon.classList.remove("hidden");
  }
  );
}

/**
 * Prompt to add all variables of a topic or concept to a basket.
 * TODO: Needs refactoring
 * @param {HTMLButtonElement} node A button Element associated with a topic or concept
 */
function addToBasket(node) {
  const treeNode = $.ui.fancytree.getNode(node);
  let url = apiUrl + "/" + treeNode.key + "?variable_list=false";
  $("#basket_list").empty();
  let numVariables = "?";
  const numberNode = document.getElementById("number_of_variables");
  if (treeNode.type === "variable") {
    numVariables = 1;
    // Set number of variables in add to basket modal
    numberNode.textContent = numVariables;
  } else {
    jQuery.getJSON(url, function(data) {
      numVariables = data.variable_count || "?";
      // Set number of variables in add to basket modal
      numberNode.textContent = numVariables;
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
          "addToBasketRequest('" + treeNode.key + "'," + data.baskets[i].id + ")";
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
 * Copy the URL of selected topic to clipboard
 *
* @param {HTMLButtonElement} node - The button node inside the fancytree node
 */
function copyUrlToClipboard(node) {
  const activeNode = $.ui.fancytree.getNode(node);

  // URL need to be selectable to be copied to clipboard,
  // append temporary element
  const text = $("<textarea />", {
    "text": baseUrl + "?open=" + activeNode.key,
  });

  text.appendTo(document.body);
  text[0].select();
  document.execCommand("copy");
  text.remove();
}


$.ui.fancytree.debugLevel = 0; // set debug level; 0:quiet, 1:info, 2:debug


// Get current URL to read 'open' Parameter for opening specified node
const urlString = window.location.href;
const url = new URL(urlString);
const open = url.searchParams.get("open");


// Define what the tree structure will look like, for more information and
// options see https://github.com/mar10/fancytree.
// Build and append tree to #tree.
$(window).on("load", function() {
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
    icon(_event, data) {
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
    createNode(_event, data) {
      const filterOptionsString = $("<span />",
        {
          "class": "btn-group btn-group-sm filter-options",
          "data-container": "body",
          "role": "group",
        }
      );

      let displayButtons = [$("<button />",
        {
          "class": "btn btn-link filter-option-variable",
          "type": "button",
          "data-tooltip": "tooltip",
          "data-container": "body",
          "title": "Show all related variables",
        }
      )];

      displayButtons[1] = displayButtons[0].clone();
      const basketButton = displayButtons[0].clone();

      displayButtons[1].attr("title", "Show all related questions");
      displayButtons[0].html("<span class='fas fa-chart-bar' aria-hidden='true'></span>");
      displayButtons[0].addClass("variables");
      displayButtons[1].addClass("questions");
      displayButtons[1].html("<span class='fas fa-tasks' aria-hidden='true'></span>");

      basketButton.attr("title", "Add all related variables to one of your baskets");
      basketButton.attr("data-toggle", "modal");
      basketButton.attr("data-target", "#topic-list-add-to-basket");
      basketButton.html("<span class='fas fa-shopping-cart' aria-hidden='true'></span>");

      displayButtons = displayButtons.map(function(target) {
        return target.on("click", function(event) {
          filter(event.target);
        });
      });
      basketButton.on("click", function(event) {
        addToBasket(event.target);
      });
      filterOptionsString.append(displayButtons, basketButton);

      if ($(data.node)[0]["type"] === "topic") {
        const clipboard = $("<button />", {
          "type": "button",
          "data-tooltip": "tooltip",
          "data-container": "body",
          "title": "Copy URL",
          "class": "btn btn-link",
        });
        clipboard.html("<span class='fas fa-copy' aria-hidden='true'></span>");
        clipboard.on("click", function(event) {
          copyUrlToClipboard(event.target);
        });
        filterOptionsString.append(clipboard);
      }

      data.node.span.querySelector(".fancytree-title").insertAdjacentElement(
        "afterend", filterOptionsString[0]);
    },
    // When tree fully loaded:
    // if parameter 'open' is set in URL open specified node
    init(_event, _data) {
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
      .filterBranches(document.getElementById("search").value, {
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
  const successMessage = document.getElementById("basket_success");
  const errorMessage = document.getElementById("basket_error");
  successMessage.classList.add("hidden");
  errorMessage.classList.add("hidden");

  const typeNameArray = nodeKey.split("_");
  const type = typeNameArray[0];
  const name = typeNameArray[1];
  const postData = {
    basket: basketId,
  };
  // eslint-disable-next-line security/detect-object-injection
  postData[type + "_name"] = name;

  const client = new XMLHttpRequest();
  client.open("POST", newApiUrl, true);
  client.setRequestHeader("Content-type", "application/json");

  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  client.withCredentials = true;
  client.setRequestHeader("X-CSRFToken", csrfToken);
  client.setRequestHeader("Accept", "application/json");

  client.onreadystatechange = function() {
    if (client.readyState === XMLHttpRequest.DONE) {
      const status = client.status;
      const _response = JSON.parse(client.responseText);
      if (200 <= status <= 201) {
        successMessage.textContent = _response["detail"];

        successMessage.classList.remove("hidden");
      }
      if (status >= 400) {
        errorMessage.textContent = _response["detail"];
        errorMessage.removeClass("hidden");
      }
    }
  };
  client.send(JSON.stringify(postData));
}

/**
 * When basket modal is closed, hide old alert messages.
 * A closed modal can be identified by the lack of a `show`.
 * This is why we check for changes in the class list.
 */
const modalObserver = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.attributeName === "class") {
      if (!mutation.target.classList.contains("show")) {
        mutation.target.querySelectorAll(".modal-body > .alert").forEach(
          function(node) {
            node.classList.add("hidden");
          }
        );
      }
    }
  });
});
modalObserver.observe(document.getElementById("topic-list-add-to-basket"), {
  attributes: true,
});


window.filter = filter;
window.addToBasket = addToBasket;
window.addToBasketRequest = addToBasketRequest;
window.copyUrlToClipboard = copyUrlToClipboard;

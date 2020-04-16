/* !
 * ddionrails - basket_button.js
 * Copyright 2015-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */
const BasketVariableAPI = new URL(
  "api/basket-variables/",
  window.location.origin
);

const basketButton = (function() {
  const addVariable = function($button, $count) {
    addBasketVariable(
      $button.attr("basket_id"),
      $button.attr("variable_id"),
      null
    );
    $button.toggleClass("btn-success btn-default");
  };

  const removeVariable = function($button, $count) {
    removeBasketVariable(
      $button.attr("basket_id"),
      $button.attr("variable_id"),
      null
    );
    $button.toggleClass("btn-success btn-default");
  };

  const handleButton = function() {
    // eslint-disable-next-line no-invalid-this
    const $button = $(this);
    const $count = $("#basket-count").first();
    if ($button.hasClass("btn-success")) {
      removeVariable($button, $count);
    } else {
      addVariable($button, $count);
    }
  };

  return function() {
    $("body").on("click", "button.basket-button", handleButton);
  };
}());

/**
 * License 3-BSD
 * @author Dominique Hansen
 * @copyright 2019
 */

/**
 * Button onclick event to add a single variable to a Basket.
 * Changes the Button onlcick event to removeBasketVariable after adding
 * the variable.
 * @param {number} basket The internal id of the basket
 * @param {string} variable The internal id of the variable
 * @param {string} basketButton The html node of the basket button
 */
function addBasketVariable(basket, variable, basketButton) {
  const postData = {
    basket,
  };
  // eslint-disable-next-line security/detect-object-injection
  postData["variables"] = [variable];

  const client = new XMLHttpRequest();
  client.open("POST", BasketVariableAPI, true);
  client.setRequestHeader("Content-type", "application/json");

  const csrfTokenRegExp = new RegExp("csrftoken=(\\w+)(?:; )?", "g");
  const csrfMatch = csrfTokenRegExp.exec(document.cookie);

  const csrfToken = csrfMatch[1];
  client.withCredentials = true;
  client.setRequestHeader("X-CSRFToken", csrfToken);
  client.setRequestHeader("Accept", "application/json");

  client.onreadystatechange = function() {
    if (client.readyState === XMLHttpRequest.DONE) {
      const status = client.status;
      const _response = JSON.parse(client.responseText);
      if (200 <= status <= 201) {
        if (basketButton) {
          basketButton.toggleClass("btn-success btn-danger add-var rm-var");
        }
      }
      if (status >= 400) {
        window.alert(_response["detail"]);
      }
    }
  };
  client.send(JSON.stringify(postData));
}

/**
 * Button onclick event to remove a single variable from a Basket.
 * Changes the Button onlcick event to addBasketVariable after removing
 * the variable.
 * @param {number} basket The internal id of the basket
 * @param {string} variable The internal id of the variable
 * @param {string} basketButton The html node of the basket button
 */
function removeBasketVariable(basket, variable, basketButton) {
  const url = new URL(BasketVariableAPI);
  url.searchParams.append("variable", variable);
  url.searchParams.append("basket", basket);

  const getClient = new XMLHttpRequest();
  getClient.open("GET", url, true);
  getClient.setRequestHeader("Content-type", "application/json");

  const csrfTokenRegExp = new RegExp("csrftoken=(\\w+)(?:; )?", "g");
  const csrfMatch = csrfTokenRegExp.exec(document.cookie);

  const csrfToken = csrfMatch[1];
  getClient.withCredentials = true;
  getClient.setRequestHeader("X-CSRFToken", csrfToken);
  getClient.onreadystatechange = function() {
    if (getClient.readyState === XMLHttpRequest.DONE) {
      try {
        const _response = JSON.parse(getClient.responseText);
        const basketVariableURL = _response["results"][0]["id"];

        const client = new XMLHttpRequest();
        client.open("DELETE", basketVariableURL, true);
        client.setRequestHeader("Content-type", "application/json");
        client.withCredentials = true;
        client.setRequestHeader("X-CSRFToken", csrfToken);
        client.send();
      } catch (SyntaxError) {
        window.alert("Variable is not part of this Basket.");
      }

      if (basketButton) {
        basketButton.toggleClass("btn-success btn-danger add-var rm-var");
      }
    }
  };

  getClient.send();
}


/**
 * List all baskets on a VariableDetailView with buttons.
 * The Buttons are tied to onclick events to either remove or
 * add the variable from/to the basket.
 * @return {null}
 */
function createBasketList() {
  const basketList = $("#basket-list");
  if ($("#context_data").length == 0) {
    return null;
  }
  const context = JSON.parse($("#context_data").text());
  // list-group-item
  for (const [name, data] of Object.entries(context["baskets"])) {
    const element = $("<div />", {
      class: "list-group-item",
    });
    const basketButton = $("<button />", {
      type: "button",
      class: "float-right",
    });

    const basketLink = $("<a />", {
      href: `/workspace/baskets/${data["id"]}`,
    });
    basketLink.text(`${name} `);

    element.append(basketLink);
    element.append(basketButton);

    const toggleFunction = function() {
      if (basketButton.hasClass("add-var")) {
        addBasketVariable(data["id"], context["variable"]["id"], basketButton);
      } else if (basketButton.hasClass("rm-var")) {
        removeBasketVariable(
          data["id"],
          context["variable"]["id"],
          basketButton
        );
      }
    };

    if (data["basket_variable"]) {
      basketButton.toggleClass("btn btn-danger rm-var");
    } else {
      basketButton.toggleClass("btn btn-success add-var");
    }
    basketButton.click(toggleFunction);
    element.append(basketButton);
    basketList.append(element);
  }
  return null;
}

$(document).ready(createBasketList());
$(document).ready(basketButton());

export {basketButton};

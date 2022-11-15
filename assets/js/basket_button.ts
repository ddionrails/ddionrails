/* !
 * License 3-BSD
 * @author Dominique Hansen
 * @copyright 2019
 */

const BasketVariableAPI = new URL(
  "api/basket-variables/",
  window.location.origin
);

/**
 *
 */
class BasketPostData {
  basket: number;
  variables: Array<string>;

  // eslint-disable-next-line require-jsdoc
  constructor(basket: number, variables: Array<string>) {
    this.basket = basket;
    this.variables = variables;
  }
}

/**
 * Button onclick event to add a single variable to a Basket.
 * Changes the Button onlcick event to removeBasketVariable after adding
 * the variable.
 * @param {number} basket The internal id of the basket
 * @param {string} variable The internal id of the variable
 * @param {string} basketButton The html node of the basket button
 */
export function addBasketVariable(
  basket: number,
  variable: string,
  basketButton: HTMLElement
) {
  const postData = new BasketPostData(basket, [variable]);

  const client = new XMLHttpRequest();
  client.open("POST", BasketVariableAPI, true);
  client.setRequestHeader("Content-type", "application/json");

  const csrfToken = document.querySelector(
    "input[name=csrfmiddlewaretoken]"
  ) as HTMLInputElement;

  client.withCredentials = true;
  client.setRequestHeader("X-CSRFToken", csrfToken.value);
  client.setRequestHeader("Accept", "application/json");

  client.onreadystatechange = function () {
    if (client.readyState === XMLHttpRequest.DONE) {
      const status = client.status;
      const _response = JSON.parse(client.responseText);
      if ([200, 201].includes(status)) {
        if (basketButton) {
          basketButton.classList.add("btn-danger", "rm-var");
          basketButton.classList.remove("btn-success", "add-var");
        }
      }
      if (status >= 400) {
        window.alert(_response["detail"]);
      }
    }
    return true;
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
export function removeBasketVariable(
  basket: number,
  variable: string,
  basketButton: HTMLElement
) {
  const url = new URL(BasketVariableAPI);
  url.searchParams.append("variable", variable);
  url.searchParams.append("basket", String(basket));

  const getClient = new XMLHttpRequest();
  getClient.open("GET", url, true);
  getClient.setRequestHeader("Content-type", "application/json");

  const csrfToken = document.querySelector(
    "input[name=csrfmiddlewaretoken]"
  ) as HTMLInputElement;
  getClient.withCredentials = true;
  getClient.setRequestHeader("X-CSRFToken", csrfToken.value);
  getClient.onreadystatechange = function () {
    if (getClient.readyState === XMLHttpRequest.DONE) {
      try {
        const _response = JSON.parse(getClient.responseText);
        const basketVariableURL = _response["results"][0]["id"];

        const client = new XMLHttpRequest();
        client.open("DELETE", basketVariableURL, true);
        client.setRequestHeader("Content-type", "application/json");
        client.withCredentials = true;
        client.setRequestHeader("X-CSRFToken", csrfToken.value);
        client.send();
      } catch (SyntaxError) {
        window.alert("Variable is not part of this Basket.");
      }

      if (basketButton) {
        basketButton.classList.add("btn-success", "add-var");
        basketButton.classList.remove("btn-danger", "rm-var");
      }
    }
    return true;
  };

  getClient.send();
}

/**
 * List all baskets on a VariableDetailView with buttons.
 * The Buttons are tied to onclick events to either remove or
 * add the variable from/to the basket.
 * @return {null}
 */
export function createBasketList(): null {
  const basketList = document.getElementById("basket-list");
  const contextData = document.getElementById("context_data");
  if (contextData.textContent === "") {
    return null;
  }
  const context = JSON.parse(
    document.getElementById("context_data").textContent
  );
  if (!context.hasOwnProperty("baskets")) {
    return null;
  }
  // list-group-item
  for (const basket of context["baskets"]) {
    const element = document.createElement("div");
    element.classList.add("list-group-item");
    const basketButton = document.createElement("button");
    basketButton.type = "button";
    basketButton.classList.add("float-right");
    basketButton.classList.add("btn");

    const basketLink = document.createElement("a");
    basketLink.href = `/workspace/baskets/${basket["id"]}`;
    basketLink.textContent = `${basket["name"]} `;

    element.append(basketLink);
    element.append(basketButton);

    // Call either addBasketVariable or removeBasketVariable
    // Dependant on the classes rm-var add-var
    // Text content of the button is also determined by rm-var and add-var
    // via index.scss.
    const addOrRemoveVariable = function () {
      if (basketButton.classList.contains("add-var")) {
        addBasketVariable(
          basket["id"],
          context["variable"]["id"],
          basketButton
        );
      } else if (basketButton.classList.contains("rm-var")) {
        removeBasketVariable(
          basket["id"],
          context["variable"]["id"],
          basketButton
        );
      }
    };

    if (basket["variableIsInBasket"]) {
      basketButton.classList.add("btn-danger", "rm-var");
      basketButton.classList.remove("btn-success", "add-var");
    } else {
      basketButton.classList.add("btn-success", "add-var");
      basketButton.classList.remove("btn-danger", "rm-var");
    }
    basketButton.addEventListener("click", () => addOrRemoveVariable());
    element.append(basketButton);
    basketList.append(element);
  }
  return null;
}

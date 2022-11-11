import {addBasketVariable} from "./basket_button";
import {removeBasketVariable} from "./basket_button";

const basketIconClass = "fa-shopping-cart";
const removeIconClass = "fa-times";

/**
 * Add or remove variable when button is clicked.
 * @param {EventTarget} buttonEvent The Event target
 */
function handleVariableButton(buttonEvent: Event): void {
  const button = buttonEvent.currentTarget as HTMLButtonElement;
  if (button.classList.contains("btn-success")) {
    addBasketVariable(
      Number(button.getAttribute("basket_id")),
      button.getAttribute("variable_id"),
      button
    );
    button.querySelector("span").classList.remove(basketIconClass);
    button.querySelector("span").classList.add(removeIconClass);
  }
  if (button.classList.contains("btn-danger")) {
    removeBasketVariable(
      Number(button.getAttribute("basket_id")),
      button.getAttribute("variable_id"),
      button
    );
    button.querySelector("span").classList.remove(removeIconClass);
    button.querySelector("span").classList.add(basketIconClass);
  }
}

/**
 * Add event Listeners to all variable Buttons
 */
function setUpButtons(): void {
  for (const button of document.querySelectorAll(".basket-button")) {
    button.addEventListener("click", handleVariableButton);
  }
}

window.addEventListener("load", setUpButtons);

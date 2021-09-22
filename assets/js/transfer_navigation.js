
/**
 *
 * @param {*} event
 */
function toggleNavigationButtons(event) {
  const buttonContainer = document.getElementById("transfer-button-container");
  buttonContainer.classList.toggle("justify-content-left");
  buttonContainer.classList.toggle("justify-content-center");
  const buttons = buttonContainer.querySelectorAll("button");
  let button = event.target;
  if (button.tagName != "BUTTON" ) {
    button = button.closest("button");
  }
  buttons.forEach((loopButton)=> {
    if (loopButton != button) {
      loopButton.classList.toggle("hidden");
    }
  });
  const topics = document.getElementById("sub-topics");
  topics.classList.toggle("hidden");
  topics.querySelector("h3").textContent = button.getAttribute("title");
}

window.addEventListener("load", function() {
  const buttonContainer = document.getElementById("transfer-button-container");
  const buttons = buttonContainer.querySelectorAll("button");
  buttons.forEach((button) => {
    button.addEventListener("click", toggleNavigationButtons);
  });
  document.getElementById("sub-topics").classList.toggle("hidden");
});

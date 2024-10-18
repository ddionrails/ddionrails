import {Variable} from "./types";
import {renderVariableStatisticsLink} from "./statistics_navigation_utils";
import {setUpSubTopics} from "./statistics_navigation_utils";

const topicMetadata = JSON.parse(document.getElementById("topics").textContent);
const apiMetadata = JSON.parse(
  document.getElementById("api-metadata").textContent
);
const navSwitch = document.getElementById("navigation-view-switch");
const buttonNavContainer = document.getElementById(
  "statistics-button-container"
);
const allVariablesContainer = document.getElementById(
  "all-variables-container"
);
const topicVariablesContainer = document.querySelector(".variables-container");

const sortVariables = (first: Variable, second: Variable): number => {
  if (first["label_de"] < second["label_de"]) {
    return -1;
  }
  return 1;
};

/**
 * Get Statistics Variables for a Topic and add them to a node.
 * @param {*} topicName
 */
function matchVariablesToTopic(topicName: string, containerNode: HTMLElement) {
  const apiCall: URL = new URL(apiMetadata["url"]);

  const request = new XMLHttpRequest();
  apiCall.searchParams.append("topic", topicName);
  apiCall.searchParams.append("study", apiMetadata["study"]);
  apiCall.searchParams.append("statistics", "True");
  apiCall.searchParams.append("paginate", "False");
  request.open("GET", apiCall, true);
  request.responseType = "json";
  request.onload = async (_) => {
    if (request.readyState === 4 && request.status === 200) {
      const sortedVariables: Variable[] = request.response.sort(sortVariables);
      if (sortedVariables.length > 10) {
        await setUpSubTopics(sortedVariables, topicName, containerNode);

        containerNode.parentElement
          .querySelector(".loading-spinner")
          .classList.add("hidden");
        return;
      }
      for (const variable of sortedVariables) {
        const listElement = document.createElement("li");
        containerNode.appendChild(listElement);
        listElement.appendChild(
          renderVariableStatisticsLink(variable, variable["statistics_type"])
        );
      }
      containerNode.parentElement
        .querySelector(".loading-spinner")
        .classList.add("hidden");
    }
  };
  request.send(null);
}

/**
 * Manage display of navigation buttons and associated content
 * @param {PointerEvent} event
 */
function toggleNavigationButtons(
  event: MouseEvent,
  button: HTMLElement = null
) {
  const buttonContainer = document.getElementById(
    "statistics-button-container"
  );
  const buttons: NodeList = buttonContainer.querySelectorAll(
    ".one-button > button"
  );

  if (button === null) {
    button = event.currentTarget as HTMLElement;
    if (button.classList.contains("disabled")) {
      return;
    }
    navSwitch.classList.toggle("hidden");
    buttonContainer.classList.toggle("justify-content-left");
    buttonContainer.classList.toggle("justify-content-center");
    button.classList.toggle("active-button");
    button.querySelector(".fa-arrow-left").classList.toggle("hidden");
    button.querySelector(":first-child").classList.toggle("hidden");

    buttons.forEach((loopButton: HTMLElement) => {
      if (loopButton != button) {
        loopButton.classList.toggle("hidden");
      }
    });
  }

  const topicVariablesContainer = button.parentElement.querySelector(
    ".variables-container"
  );
  topicVariablesContainer.classList.toggle("hidden");
  if (!topicVariablesContainer.classList.contains("hidden")) {
    const variableList = topicVariablesContainer.querySelector("ul");
    if (variableList.textContent.trim() === "") {
      topicVariablesContainer
        .querySelector(".loading-spinner")
        .classList.remove("hidden");
      const heading = topicVariablesContainer.querySelector("h3");
      for (const langAttr of ["data-en", "data-de"]) {
        heading.setAttribute(
          langAttr,
          button.querySelector("p").getAttribute(langAttr)
        );
      }
      heading.innerHTML = button.querySelector("p").textContent;
      matchVariablesToTopic(button.id, variableList);
    }
  }
}

window.addEventListener("load", function () {
  const buttonContainer = buttonNavContainer;
  const buttonContainers = Array.from(
    buttonContainer.getElementsByClassName("one-button")
  );
  for (const container of buttonContainers) {
    container.appendChild(topicVariablesContainer.cloneNode(true));
    const button = container.querySelector("button");
    button.addEventListener("click", toggleNavigationButtons);
  }

  navSwitch.addEventListener("click", () => {
    buttonContainer.classList.toggle("flex-column");
    buttonContainer.classList.toggle("flex-row");
    const buttons = document.querySelectorAll(
      "#statistics-button-container >* button"
    );
    for (const button of Array.from(buttons)) {
      button.classList.toggle("disabled");
      toggleNavigationButtons(null, button as HTMLElement);
    }
  });
});


type Variable = {
  id: string,
  name: string,
  label: string,
  label_de: string,
  dataset_name: string,
  study_name: string
  study_label: string,
  dataset: string,
  study: string,
  statistics_type: string
}


const topicMetadata = JSON.parse(document.getElementById("topics").textContent);
const apiMetadata = JSON.parse(
  document.getElementById("api-metadata").textContent
);
const navSwitch = document.getElementById("navigation-view-switch")
const buttonNavContainer = document.getElementById("statistics-button-container")
const allVariablesContainer = document.getElementById("all-variables-container")
const topicVariablesContainer = document.querySelector(".variables-container")

function renderVariableStatisticsLink(variable: any, type: string): HTMLElement {
  const linkElement = document.createElement("a")
  linkElement.textContent = variable["label_de"] + ` ${type}`.toUpperCase()
  const url = new URL(window.location + `${type}/`)
  url.searchParams.append("variable", variable["id"])

  linkElement.href = url.toString()
  return linkElement
}

/**
 * Get Statistics Variables for a Topic and add them to a node.
 * @param {*} topicName
 */
function matchVariablesToTopic(topicName: string, containerNode: HTMLElement) {
  const apiCall: URL = new URL(apiMetadata["url"]);


  const request = new XMLHttpRequest();
  apiCall.searchParams.append("topic", topicName)
  apiCall.searchParams.append("study", apiMetadata["study"])
  apiCall.searchParams.append("statistics", "True")
  apiCall.searchParams.append("paginate", "False")
  request.open("GET", apiCall, true);
  request.responseType = "json";
  request.onload = (_) => {
    if (request.readyState === 4 && request.status === 200) {
      for (const variable of request.response as Variable[]) {
        const listElement = document.createElement("li")
        containerNode.appendChild(listElement)
        if (variable["statistics_type"] === "ordinal") {
          listElement.appendChild(renderVariableStatisticsLink(variable, "categorical"))
          const nextListNode = document.createElement("li")
          containerNode.appendChild(nextListNode)
          nextListNode.appendChild(
            renderVariableStatisticsLink(variable, "numerical")
          )
        }
        else {
          listElement.appendChild(renderVariableStatisticsLink(
            variable, variable["statistics_type"])
          )
        }


      }
      containerNode.parentElement.querySelector(".loading-spinner").classList.add("hidden")
    }
  }
  request.send(null)
}

/**
 * Manage display of navigation buttons and associated content
 * @param {PointerEvent} event
 */
function toggleNavigationButtons(event: MouseEvent, button: HTMLElement = null) {
  const buttonContainer = document.getElementById("statistics-button-container");
  const buttons: NodeList = buttonContainer.querySelectorAll(".one-button > button");

  if (button === null) {
    button = event.currentTarget as HTMLElement;
    if (button.classList.contains("disabled")) {
      return
    }
    navSwitch.classList.toggle("hidden")
    buttonContainer.classList.toggle("justify-content-left");
    buttonContainer.classList.toggle("justify-content-center");

    buttons.forEach((loopButton: HTMLElement) => {
      if (loopButton != button) {
        loopButton.classList.toggle("hidden");
      }
    });

  }

  const topicVariablesContainer = button.parentElement.querySelector(".variables-container");
  topicVariablesContainer.classList.toggle("hidden");
  if (!topicVariablesContainer.classList.contains("hidden")) {
    const variableList = topicVariablesContainer.querySelector("ul")
    if (variableList.textContent.trim() === '') {
      topicVariablesContainer.querySelector(".loading-spinner").classList.remove("hidden")
      topicVariablesContainer.querySelector("h3").textContent = button.getAttribute("title");
      matchVariablesToTopic(button.id, variableList)

    }

  }
}


window.addEventListener("load", function () {
  const buttonContainer = buttonNavContainer;
  const buttonContainers = Array.from(buttonContainer.getElementsByClassName("one-button"));
  for (const container of buttonContainers) {
    container.appendChild(topicVariablesContainer.cloneNode(true))
    const button = container.querySelector("button")
    button.addEventListener("click", (toggleNavigationButtons));
  }

  navSwitch.addEventListener("click", () => {

    const buttonsContainer = document.querySelectorAll("#statistics-button-container")
    buttonContainer.classList.toggle("flex-column")
    buttonContainer.classList.toggle("flex-row")
    const buttons = document.querySelectorAll("#statistics-button-container >* button")
    for (const button of Array.from(buttons)) {
      button.classList.toggle("disabled")
      toggleNavigationButtons(null, button as HTMLElement)
    }
  })
});


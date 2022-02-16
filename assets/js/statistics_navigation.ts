
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
const loadingSpinnerNav = document.getElementById("loading-spinner")

function renderVariableStatisticsLink(variable: any, type: string): HTMLElement {
  const linkElement = document.createElement("a")
  linkElement.textContent = variable["label_de"] + ` ${type}`.toUpperCase()
  const url = new URL(window.location + `${type}/`)
  url.searchParams.append("variable", variable["id"])

  linkElement.href = url.toString()
  return linkElement
}

/**
 *
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
      loadingSpinnerNav.classList.add("hidden")
    }
  }
  request.send(null)
}

/**
 *
 * @param {PointerEvent} event
 */
function toggleNavigationButtons(event: MouseEvent) {
  const buttonContainer = document.getElementById("statistics-button-container");
  buttonContainer.classList.toggle("justify-content-left");
  buttonContainer.classList.toggle("justify-content-center");
  const buttons: NodeList = buttonContainer.querySelectorAll("button");
  let button = event.target as HTMLElement;
  if (button.tagName != "BUTTON") {
    button = button.closest("button");
  }

  buttons.forEach((loopButton: HTMLElement) => {
    if (loopButton != button) {
      loopButton.classList.toggle("hidden");
    }
  });

  const topicVariablesContainer = document.getElementById("sub-topics");
  topicVariablesContainer.classList.toggle("hidden");
  if (!topicVariablesContainer.classList.contains("hidden")) {
    loadingSpinnerNav.classList.remove("hidden")
    topicVariablesContainer.querySelector("h3").textContent = button.getAttribute("title");
    const variableList = topicVariablesContainer.querySelector("ul")
    variableList.innerHTML = ""
    matchVariablesToTopic(button.id, variableList)

  }
}

window.addEventListener("load", function () {
  const buttonContainer = document.getElementById("statistics-button-container");
  const buttons = buttonContainer.querySelectorAll("button");
  buttons.forEach((button) => {
    button.addEventListener("click", (toggleNavigationButtons));
  });
  document.getElementById("sub-topics").classList.toggle("hidden");
});


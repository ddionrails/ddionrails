import { variableType } from "../variable_labels";

const languageSwitch = document.getElementById("language-switch");

const language = languageSwitch.getAttribute("data-current-language");

async function fillValueLabels() {
  const variableIDContainer = document.querySelector('meta[name="id"]');
  const variableID =
    variableIDContainer instanceof HTMLMetaElement
      ? variableIDContainer.content
      : "";
  const tableBody = document.getElementById("value-labels-table-body");
  const apiURL = new URL(
    `${window.location.origin}/api/variable_labels/${variableID}`,
  );
  const response = await fetch(apiURL, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });
  const variable_data: variableType = (await response.json()) as variableType;
  const label_data = variable_data["labels"];
  for (let index = 0; index < label_data.labels.length; index++) {
    const row = document.createElement("tr");
    const value = document.createElement("td");
    value.innerHTML = String(label_data.values[index]);
    value.classList.add("bold")
    const label = document.createElement("td");
    label.setAttribute("data-en", label_data.labels[index]);
    label.setAttribute("data-de", label_data.labels_de[index]);
    if(language == "de"){
      label.innerHTML = label_data.labels_de[index]
    }else{
      label.innerHTML = label_data.labels[index]
    }
    row.appendChild(value);
    row.appendChild(label);
    tableBody.appendChild(row);
  }
}

window.addEventListener("load", () => {
  fillValueLabels();
});

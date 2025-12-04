const longVariableConainerID = "long-variable-info-container";

const outputIcon = document.createElement("i")
outputIcon.classList.add("fa-solid", "fa-arrow-right-from-bracket", "output-icon")

const inputIcon = document.createElement("i")
inputIcon.classList.add("fa-solid", "fa-arrow-right-to-bracket", "input-icon")

function getApiUrl() {
  const studyMeta = document.querySelector('meta[name="study"]');
  const variableMeta = document.querySelector('meta[name="variable"]');
  const variableName =
    variableMeta instanceof HTMLMetaElement ? variableMeta.content : "";
  const datasetMeta = document.querySelector('meta[name="dataset"]');
  const datasetName =
    datasetMeta instanceof HTMLMetaElement ? datasetMeta.content : "";
  const studyName =
    studyMeta instanceof HTMLMetaElement ? studyMeta.content : "";

  if (variableName == "" || datasetName == "" || studyName == "") {
    return "";
  }
  const query = `?dataset=${datasetName}&variable=${variableName}&study=${studyName}`;

  return `${window.location.origin}/api/related_variables/${query}`;
}

function parseRelatedJSON(json: any) {
  const content = json;
  if (!content?.["count"]) {
    return;
  }
  const longVariables = [];
  for (const result of content?.["results"]) {
    if (result?.["period_name"] == "0") {
      longVariables.push(result);
    }
  }
  const container = document.getElementById(longVariableConainerID);
  if(longVariables.length == 1){
    container.appendChild(document.createTextNode("Long Variable: "))
  } else if (longVariables.length > 1){
    container.appendChild(document.createTextNode("Harmonized from: "))
  }
  for (const variable of longVariables) {
    let element = document.createElement("div");
    element.appendChild(document.createTextNode(variable?.["name"]));
    element.appendChild(inputIcon.cloneNode())
    container.appendChild(element);
  }
}

function loadRelationData() {
  const apiUrl = getApiUrl();
  if (apiUrl == "") {
    return;
  }

  let apiRequest = new Request(apiUrl);
  fetch(apiRequest).then((response) => {
    response.json().then((json) => {
      parseRelatedJSON(json);
    });
  });
}

window.addEventListener("load", () => {
  loadRelationData();
});

type VariableRelation = {
  id: string;
  name: string;
  label: string;
  label_de: string;
  dataset_name: string;
  dataset: string;
  relation: "input_variable" | "output_variable";
  period_name: string;
};

type RelatedVariablesAPIResponse = {
  count: number;
  next: any;
  previous: any;
  results: Array<VariableRelation>;
};

const variableRerouteUrl = `${window.location.origin}/variable/`;

const longVariableConainerID = "long-variable-info-container";

function createIcon(
  classNames: Array<string>,
  languageLabels: Map<languageCode, string>,
) {
  const languageSwitch = document.getElementById("language-switch");
  let language = languageSwitch.getAttribute(
    "data-current-language",
  ) as languageCode;

  const inputIcon = document.createElement("i");
  inputIcon.classList.add(...classNames);
  inputIcon.title = languageLabels.get(language);

  const mutationCallback = (mutationList: Array<any>, _: any) => {
    for (const mutation of mutationList) {
      if (mutation.type == "attributes") {
        language = languageSwitch.getAttribute(
          "data-current-language",
        ) as languageCode;
        inputIcon.title = languageLabels.get(language);
      }
    }
  };

  const observer = new MutationObserver(mutationCallback);
  observer.observe(languageSwitch, { attributes: true });

  return inputIcon;
}

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

function createVariableElement(variable: VariableRelation) {
  const variableContainer = document.createElement("div");
  variableContainer.classList.add("related-variable-container");
  const variableLink = document.createElement("a");
  variableLink.innerText = variable.name;
  variableLink.href = variableRerouteUrl + variable.id;
  variableContainer.appendChild(variableLink);

  if (variable.relation == "input_variable") {
    variableContainer.appendChild(
      createIcon(
        ["fa-solid", "fa-arrow-right-to-bracket", "input-icon"],
        new Map([
          ["en", "The current variable is generated using this variable"],
          ["de", "Die aktuelle variable wird aus dieser generiert"],
        ]),
      ),
    );
  }

  if (variable.relation == "output_variable") {
    variableContainer.prepend(
      createIcon(
        ["fa-solid", "fa-arrow-right-from-bracket", "input-icon"],
        new Map([
          ["en", "The current variable is used to generate this variable"],
          [
            "de",
            "Die aktuelle Variable wird zur Generierung dieser Variable genutzt",
          ],
        ]),
      ),
    );
  }

  return variableContainer;
}

function createInfoHeader(label: Map<languageCode, string>) {
  const outputElement = document.createElement("span");
  const language = document
    .getElementById("language-switch")
    .getAttribute("data-current-language") as languageCode;
  outputElement.setAttribute("data-de", label.get("de"));
  outputElement.setAttribute("data-en", label.get("en"));
  outputElement.textContent = label.get(language);
  outputElement.classList.add("related-infobox-header");
  return outputElement;
}

function parseRelatedJSON(json: RelatedVariablesAPIResponse) {
  const content = json;
  if (!content?.["count"]) {
    return;
  }
  const longInputVariables = [];
  const longOutputVariables = [];
  for (const result of content?.["results"]) {
    if (result?.["period_name"] == "0") {
      if (result.relation == "input_variable") {
        longInputVariables.push(result);
      }
      if (result.relation == "output_variable") {
        longOutputVariables.push(result);
      }
    }
  }
  const container = document.getElementById(longVariableConainerID);
  if (longOutputVariables.length) {
    container.appendChild(
      createInfoHeader(
        new Map([
          ["en", "Long variables:"],
          ["de", "Längsschnittvariablen:"],
        ]),
      ),
    );
    for (const variable of longOutputVariables) {
      const element = createVariableElement(variable);
      container.appendChild(element);
    }
  }
  if (longInputVariables.length) {
    container.appendChild(
      createInfoHeader(
        new Map([
          ["de", "Harmonisiert von:"],
          ["en", "Harmonized from:"],
        ]),
      ),
    );
    for (const variable of longInputVariables) {
      const element = createVariableElement(variable);
      container.appendChild(element);
    }
  }
}

function loadRelationData() {
  const apiUrl = getApiUrl();
  if (apiUrl == "") {
    return;
  }

  let apiRequest = new Request(apiUrl);
  fetch(apiRequest).then((response) => {
    response.json().then((json: RelatedVariablesAPIResponse) => {
      parseRelatedJSON(json);
    });
  });
}

window.addEventListener("load", () => {
  loadRelationData();
});

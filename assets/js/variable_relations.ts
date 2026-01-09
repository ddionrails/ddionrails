import {
  addConceptToVariables,
  createIcon,
  enableToggle,
} from "./variable_relations_concepts";
import { addClickEventHandler } from "./variable_relations_toggle";

type VariableRelationType =
  | "input_variable"
  | "output_variable"
  | "sibling_variable";

type LongVariablePeriodType = "0";
const LongVariablePeriod: LongVariablePeriodType = "0";

type VariableRelation = {
  id: string;
  name: string;
  label: string;
  label_de: string;
  dataset_name: string;
  dataset: string;
  relation: VariableRelationType;
  period_name: string;
};

type RelatedVariablesAPIResponse = {
  count: number;
  next: any;
  previous: any;
  results: Array<VariableRelation>;
};

type InputOutputMap = Map<VariableRelationType, Array<VariableRelation>>;

type PeriodInputOutputMap = Map<string, InputOutputMap>;

const variableRerouteUrl = `${window.location.origin}/variable/`;

const longVariableConainerID = "long-variable-info-container";

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
  variableContainer.setAttribute("data-variable-name", variable.name);

  if (variable.relation == "sibling_variable") {
    variableContainer.appendChild(
      createIcon(
        ["fa-solid", "fa-handshake", "sibling-icon"],
        new Map([
          ["en", "Is related to the same long variable"],
          ["de", "Fließt in die selbe Langzeitvariable"],
        ]),
      ),
    );
    variableContainer.classList.add("sibling-relation-toggle")
  }

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
    variableContainer.classList.add("input-relation-toggle")
  }

  if (variable.relation == "output_variable") {
    variableContainer.prepend(
      createIcon(
        ["fa-solid", "fa-arrow-right-from-bracket", "output-icon"],
        new Map([
          ["en", "The current variable is used to generate this variable"],
          [
            "de",
            "Die aktuelle Variable wird zur Generierung dieser Variable genutzt",
          ],
        ]),
      ),
    );
    variableContainer.classList.add("output-relation-toggle")
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

function appendLongOutputVariables(
  container: HTMLElement,
  longOutputVariables: Array<VariableRelation>,
) {
  container.appendChild(
    createInfoHeader(
      new Map([
        ["en", "Harmonized long variables:"],
        ["de", "Hamonisierte Längsschnittvariablen:"],
      ]),
    ),
  );
  for (const variable of longOutputVariables) {
    container.appendChild(createVariableElement(variable));
  }
}

function appendLongInputVariables(
  container: HTMLElement,
  longInputVariables: Array<VariableRelation>,
) {
  container.appendChild(
    createInfoHeader(
      new Map([
        ["de", "Harmonisiert von:"],
        ["en", "Harmonized from:"],
      ]),
    ),
  );
  for (const variable of longInputVariables) {
    container.appendChild(createVariableElement(variable));
  }
}

function fillInfoContainer(
  longVariablesMap: Map<VariableRelationType, Array<VariableRelation>>,
) {
  const container = document.getElementById(longVariableConainerID);
  if (longVariablesMap.has("output_variable")) {
    appendLongOutputVariables(
      container,
      longVariablesMap.get("output_variable"),
    );
  }
  if (longVariablesMap.has("input_variable")) {
    appendLongInputVariables(container, longVariablesMap.get("input_variable"));
  }
}

/**
 * Sort numerical strings and strings
 * Sort:
 * Numerical strings in front of non-numerical strings
 * Two non-numerical strings as strings
 * Two numerical strings as numbers
 * */
function comparePotentialNumeric(a: string | number, b: string | number) {
  const aInt = typeof a == "string" ? parseInt(a) : a;
  const bInt = typeof b == "string" ? parseInt(b) : b;

  if (!isNaN(aInt) && isNaN(bInt)) {
    return -1;
  }
  if (isNaN(aInt) && !isNaN(bInt)) {
    return 1;
  }

  if (isNaN(aInt) && isNaN(bInt)) {
    if (a < b) {
      return -1;
    }
    if (a > b) {
      return 1;
    }
    return 0;
  }
  if (aInt < bInt) {
    return -1;
  }
  if (aInt > bInt) {
    return 1;
  }
  return 0;
}

function fillVariablesContainer(periodInputOutputMap: PeriodInputOutputMap) {
  const variableRelationsCard = document.getElementById("variable-relations");
  const variableRelationsCardBody =
    variableRelationsCard.getElementsByClassName("card-body")["0"];

  const periods = Array.from(periodInputOutputMap.keys()).sort(
    comparePotentialNumeric,
  );

  for (const period of periods) {
    const periodContainer = document.createElement("div");
    periodContainer.classList.add("period-container");
    periodContainer.setAttribute("data-period-name", period);
    const periodHeader = document.createElement("div");
    periodHeader.classList.add("related-period-header");
    periodHeader.textContent = period + ":";
    periodContainer.appendChild(periodHeader);
    if (periodInputOutputMap.get(period).has("sibling_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("sibling_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableToggle("sibling");
    }
    if (periodInputOutputMap.get(period).has("input_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("input_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableToggle("input");
    }
    if (periodInputOutputMap.get(period).has("output_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("output_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableToggle("output");
    }
    variableRelationsCardBody.appendChild(periodContainer);
  }
}

function parseRelatedJSON(json: RelatedVariablesAPIResponse) {
  const content = json;
  if (!content?.["count"]) {
    return;
  }
  const periodInputOutputMap: PeriodInputOutputMap = new Map();

  for (const result of content?.["results"]) {
    if (!periodInputOutputMap.has(result.period_name)) {
      periodInputOutputMap.set(result.period_name, new Map());
    }
    if (!periodInputOutputMap.get(result.period_name).get(result.relation)) {
      periodInputOutputMap.get(result.period_name).set(result.relation, []);
    }
    periodInputOutputMap
      .get(result.period_name)
      .get(result.relation)
      .push(result);
  }

  if (periodInputOutputMap.has(LongVariablePeriod)) {
    fillInfoContainer(periodInputOutputMap.get(LongVariablePeriod));
  }
  if (periodInputOutputMap.size) {
    fillVariablesContainer(periodInputOutputMap);
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
      addConceptToVariables();
      addClickEventHandler()
    });
  });
}

window.addEventListener("load", () => {
  loadRelationData();
});

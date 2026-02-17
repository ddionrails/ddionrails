import {
  addConceptVariables,
  sortPotentialNumeric,
  createIcon,
  createVariableContainer,
  enableRelationToggleButton,
  initPeriodContainer,
} from "./variable_relations_concepts";
import { addClickEventHandler } from "./variable_relations_toggle";

type LongVariablePeriodType = "0";
const LongVariablePeriod: LongVariablePeriodType = "0";

type VariableRelationType =
  | "input_variable"
  | "output_variable"
  | "sibling_variable";

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

type RelationMap = Map<VariableRelationType, Array<VariableRelation>>;

type RelationByPeriodMap = Map<string, RelationMap>;

const InfoHeaderText: Map<languageCode, string> = new Map([
  ["en", "Harmonized long variables:"],
  ["de", "Hamonisierte Längsschnittvariablen:"],
]);

const SiblingIcon = createIcon(
  ["fa-solid", "fa-handshake", "sibling-icon", "sibling-relation-toggle"],
  new Map([
    ["en", "The current variable is indirectly or directly related to the same harmonized variable"],
    ["de", "Die aktuelle Variable ist indirekt oder direkt mit der gleichen harmonisierten variable verwandt"],
  ]),
);

const InputIcon = createIcon(
  ["fa-solid", "fa-circle-right", "input-icon", "input-relation-toggle"],
  new Map([
    ["en", "This variable is an input to the current variable"],
    ["de", "Diese Variable ist der input der aktuellen Variable"],
  ]),
);

const OutputIcon = createIcon(
  ["fa-solid", "fa-circle-left", "output-icon", "output-relation-toggle"],
  new Map([
    ["en", "This variable is an output of the current variable"],
    [
      "de",
      "Diese Variable ist der output der aktuellen Variable",
    ],
  ]),
);

const longVariableConainerID = "long-variable-info-container";

function getRelationsApiUrl() {
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
  const variableContainer = createVariableContainer(variable);

  if (variable.relation == "sibling_variable") {
    variableContainer.appendChild(SiblingIcon.cloneNode());
    variableContainer.classList.add("sibling-relation-toggle");
  }
  if (variable.relation == "input_variable") {
    variableContainer.appendChild(InputIcon.cloneNode());
    variableContainer.classList.add("input-relation-toggle");
  }
  if (variable.relation == "output_variable") {
    variableContainer.appendChild(OutputIcon.cloneNode());
    variableContainer.classList.add("output-relation-toggle");
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
  container.appendChild(createInfoHeader(InfoHeaderText));
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

function fillVariablesContainer(periodInputOutputMap: RelationByPeriodMap) {
  const variableRelationsCard = document.getElementById("variable-relations");
  const variableRelationsCardBody =
    variableRelationsCard.getElementsByClassName("card-body")["0"];

  const periods = Array.from(periodInputOutputMap.keys()).sort(
    sortPotentialNumeric,
  );

  for (const period of periods) {
    const periodContainer = initPeriodContainer(period);

    if (periodInputOutputMap.get(period).has("sibling_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("sibling_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableRelationToggleButton("sibling");
    }
    if (periodInputOutputMap.get(period).has("input_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("input_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableRelationToggleButton("input");
    }
    if (periodInputOutputMap.get(period).has("output_variable")) {
      for (const variable of periodInputOutputMap
        .get(period)
        .get("output_variable")) {
        periodContainer.appendChild(createVariableElement(variable));
      }
      enableRelationToggleButton("output");
    }
    variableRelationsCardBody.appendChild(periodContainer);
  }
}

function parseRelatedJSON(json: RelatedVariablesAPIResponse) {
  const content = json;
  if (!content?.["count"]) {
    return;
  }
  const periodInputOutputMap: RelationByPeriodMap = new Map();

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
  const apiUrl = getRelationsApiUrl();
  if (apiUrl == "") {
    return;
  }

  let apiRequest = new Request(apiUrl);
  fetch(apiRequest).then((response) => {
    response.json().then((json: RelatedVariablesAPIResponse) => {
      parseRelatedJSON(json);
      addConceptVariables();
      addClickEventHandler();
    });
  });
}

window.addEventListener("load", () => {
  loadRelationData();
});

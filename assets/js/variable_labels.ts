import {filter} from "vue/types/umd";

const VariableName: string = document.getElementById("variable-name").innerHTML;

const labelRegex = /^\[.*?\]\s/;

/**
 *
 * @returns
 */
export async function getAPIData() {
  const apiURL = new URL(`${window.location.origin}/api/variable_labels/`);

  const concept = document
    .querySelector("[data-concept-name]")
    .getAttribute("data-concept-name");

  apiURL.searchParams.append("concept", concept);
  const response = await fetch(apiURL, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });
  return response.json();
}

type labelsContainer = {
  labels: Array<string>;
  labels_de: Array<string>;
  values: Array<number>;
};

type variableType = {
  variable: string;
  dataset: string;
  period: string;
  labels: labelsContainer;
};

type labelContainerType = {
  labels: Map<string, number>;
  labelsDE: Map<string, number>;
}

/**
 *
 * @param labels
 * @returns
 */
export function removeCodesFromLabelsMap(labels: labelsContainer): labelContainerType {
  const out: Map<string, number> = new Map();
  const outDE: Map<string, number> = new Map();
  let indexWithoutMissings = 0;
  labels["labels"].forEach((label, index) => {
    if (label.match(/\[-\d+\]/)) {
      return;
    }
    out.set(label.replace(labelRegex, ""), indexWithoutMissings);
    outDE.set(
      labels["labels_de"][Number(index)].replace(labelRegex, ""),
      indexWithoutMissings
    );
    indexWithoutMissings = indexWithoutMissings + 1;
  });
  return {labels: out, labelsDE: outDE};
}

/**
 *
 * @param labels
 * @returns
 */
export function removeCodesFromLabelsArray(labels: labelsContainer): {
  labels: Array<string>;
  labelsDE: Array<string>;
} {
  const out: Array<string> = [];
  const outDE: Array<string> = [];
  labels["labels"].forEach((label, index) => {
    if (label.match(/\[-\d+\]/)) {
      return;
    }
    out.push(label.replace(labelRegex, ""));
    outDE.push(labels["labels_de"][Number(index)].replace(labelRegex, ""));
  });
  return {labels: out, labelsDE: outDE};
}

/**
 * 
 * @param label 
 * @param index 
 * @param labelContainer 
 */
function addNewLabel(
  label: string,
  labelDE: string,
  labelContainer: labelContainerType) {
  if (labelContainer["labels"].has(label)) {
  } else {
    labelContainer["labels"].set(label, labelContainer["labels"].size);
    labelContainer["labelsDE"].set(
      labelDE,
      labelContainer["labelsDE"].size
    );
  }

}

/**
 * 
 * @param variables 
 * @param labelMapping 
 */
function fillValues(variables: Array<variableType>, labelMapping: labelContainerType) {
  const variableValues: Map<string, Array<number>> = new Map();
  const labelCount = labelMapping.labels.size;
  variables.forEach((variable) => {
    const values = Array(labelCount).fill(null);
    variable.labels.labels.forEach((label, index) => {
      if (labelMapping.labels.has(label)) {
        const labelPosition: number = labelMapping.labels.get(label);
        values[Number(labelPosition)] = variable.labels.values[Number(index)];
      };
    });
    variableValues.set(variable.variable, values);
  });
  return variableValues;
}

function removeMissings(value: number) {
  return Number(value) >= 0;
}

/**
 *
 * @param variables
 */
export function parseVariables(apiResponse: {results: Array<variableType>}) {
  const periods = new Map();
  const variables: Array<variableType> = apiResponse["results"];
  const mainVariable = variables.find(
    (variable) => variable["variable"] == VariableName
  );
  periods.set(mainVariable["variable"], mainVariable["period"]);

  variables.splice(variables.indexOf(mainVariable), 1);

  const mainLabels = removeCodesFromLabelsMap(mainVariable["labels"]);
  mainVariable.labels.labels = Array.from(mainLabels.labels.keys());
  mainVariable.labels.labels_de = Array.from(mainLabels.labelsDE.keys());
  mainVariable["labels"]["values"] = mainVariable["labels"]["values"].filter(
    removeMissings
  );
  variables.forEach((variable) => {
    variable.labels.values = variable.labels.values.filter(removeMissings);
    periods.set(variable["variable"], variable["period"]);
    const labels = removeCodesFromLabelsArray(variable["labels"]);
    variable.labels.labels = labels.labels;
    variable.labels.labels_de = labels.labelsDE;
    labels["labels"].forEach((label, index) => {
      addNewLabel(label, labels["labelsDE"][Number(index)], mainLabels);
    });
  });
  variables.push(mainVariable);
  const values = fillValues(variables, mainLabels);
  return {
    labels: new Map([
      ["labels", Array.from(mainLabels["labels"].keys())],
      ["labels_de", Array.from(mainLabels["labelsDE"].keys())],
    ]),
    periods,
    values,
  };
}

/**
 *
 */
async function getLabelData() {
  parseVariables(await getAPIData());
}

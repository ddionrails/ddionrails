const VariableName: string = document.getElementById("variable-name").innerHTML;

const labelRegex = /^\[.*?\]\s/;

type labelsContainerType = {
  labels: Array<string>;
  labels_de: Array<string>;
  values: Array<number>;
};

type variableType = {
  variable: string;
  dataset: string;
  period: string;
  labels: labelsContainerType;
};

type APIResponse = {results: Array<variableType>}

type labelsMappingType = {
  labels: Map<string, number>;
  labelsDE: Map<string, number>;
}

type labelsArrayType = {
  labels: Array<string>;
  labelsDE: Array<string>;
}

type parsedVariables = {
  labels: Map<string, Array<string>>,
  periods: Map<string, string>,
  values: Map<string, Array<number>>
}

/**
 * Request variable label data from API
 * @return {Promise<APIResponse>}
 */
export async function getAPIData(): Promise<APIResponse> {
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


/**
 * Remove label codes in [] from labels and store in Map with index as value.
 * @param {labelsContainerType} labels
 * @return {labelsMappingType}
 */
export function removeCodesFromLabelsMap(labels: labelsContainerType): labelsMappingType {
  const out: Map<string, number> = new Map();
  const outDE: Map<string, number> = new Map();
  let indexWithoutMissings = 0;
  labels["labels"].forEach((label, index) => {
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
 * Remove label codes in [] from labels and store in Array.
 * @param {labelsMappingType} labels
 * @return {labelsArrayType}
 */
export function removeCodesFromLabelsArray(labels: labelsContainerType):
  labelsArrayType {
  const out: Array<string> = [];
  const outDE: Array<string> = [];
  labels["labels"].forEach((label, index) => {
    out.push(label.replace(labelRegex, ""));
    outDE.push(labels["labels_de"][Number(index)].replace(labelRegex, ""));
  });
  return {"labels": out, "labelsDE": outDE};
}

/**
 * Add new labels to labelContainer in place
 * @param {string} label
 * @param {string} labelDE
 * @param {labelsMappingType} labelContainer
 */
function addNewLabel(
  label: string,
  labelDE: string,
  labelContainer: labelsMappingType) {
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
 * Fills array of values according to all possible labels
 * @param {Array<variableType>} variables
 * @param {labelsMappingType} labelMapping
 * @return {Map<string, Array<number>>} a
 */
function fillValues(variables: Array<variableType>, labelMapping: labelsMappingType):
  Map<string, Array<number>> {
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


/**
 * Remove all labels and values from variables where values are 0 or less.
 * @param {Array<variableType>} variables
 * @return {Array<variableType>}
 */
function removeMissings(variables: Array<variableType>) {
  variables.forEach((variable) => {
    const labelsCopy = variable.labels.values.slice()
    labelsCopy.reverse().forEach((element, index) => {
      if (element <= 0) {
        const reversePosition = labelsCopy.length - index - 1;
        variable.labels.labels.splice(reversePosition, 1);
        variable.labels.labels_de.splice(reversePosition, 1);
        variable.labels.values.splice(reversePosition, 1);
      }
    });
  });
  return variables;
}

/**
 * Parse information from API response to display in table.
 * @param {APIResponse} apiResponse
 * @return {parsedVariables}
 */
export function parseVariables(apiResponse: APIResponse):
  parsedVariables {
  const periods = new Map();
  const variables: Array<variableType> = removeMissings(apiResponse["results"]);


  const mainVariable = variables.find(
    (variable) => variable["variable"] == VariableName
  );
  periods.set(mainVariable["variable"], mainVariable["period"]);

  variables.splice(variables.indexOf(mainVariable), 1);

  const mainLabels = removeCodesFromLabelsMap(mainVariable["labels"]);
  mainVariable.labels.labels = Array.from(mainLabels.labels.keys());
  mainVariable.labels.labels_de = Array.from(mainLabels.labelsDE.keys());
  variables.forEach((variable) => {
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

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

type APIResponse = { results: Array<variableType> };

type labelsMappingType = {
  labels: Set<string>;
  labelsDE: Set<string>;
};

type labelsArrayType = {
  labels: Array<string>;
  labelsDE: Array<string>;
};

type parsedVariables = {
  labels: Map<string, Array<string>>;
  periods: Map<string, string>;
  datasets: Map<string, string>;
  values: Array<Map<string, string>>;
};

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
export function removeCodesFromLabelsSet(
  labels: labelsContainerType,
): labelsMappingType {
  const out: Set<string> = new Set();
  const outDE: Set<string> = new Set();
  let indexWithoutMissings = 0;
  for (const [index, label] of labels.labels.entries()) {
    out.add(label.replace(labelRegex, ""));
    outDE.add(labels["labels_de"][Number(index)].replace(labelRegex, ""));
    indexWithoutMissings = indexWithoutMissings + 1;
  }
  return { labels: out, labelsDE: outDE };
}

/**
 * Sometimes labels are "empty".
 * Cleaning them up with the labelRegex will cause their value to be "".
 * DataTables reports errors when a cell is "" but is OK with it being " ".
 * That's why this function safeguards against ""
 */
function labelSaveguard(label: string) {
  if (label === "") {
    return " ";
  }
  return label;
}

/**
 * Remove label codes in [] from labels and store in Array.
 * @param {labelsMappingType} labels
 * @return {labelsArrayType}
 */
export function removeCodesFromLabelsArray(
  labels: labelsContainerType,
): labelsArrayType {
  const out: Array<string> = [];
  const outDE: Array<string> = [];
  labels["labels"].forEach((label, index) => {
    out.push(labelSaveguard(label.replace(labelRegex, "")));
    outDE.push(
      labelSaveguard(
        labels["labels_de"][Number(index)].replace(labelRegex, ""),
      ),
    );
  });
  return { labels: out, labelsDE: outDE };
}

/**
 * Fills array of values according to all possible labels
 * @param {Array<variableType>} variables
 * @param {labelsMappingType} labelMapping
 * @return {Map<string, Array<number>>} a
 */
function fillRows(
  variables: Array<variableType>,
  labelMapping: labelsMappingType,
): Array<Map<string, string>> {
  const labels = labelMapping.labels.keys();
  const labelsDE = labelMapping.labelsDE.keys();
  const rows: Array<Map<string, string>> = [];

  let labelIteration = labels.next();
  let labelDEIteration = labelsDE.next();
  let done = labelIteration.done;
  while (!done) {
    const label = labelIteration.value;
    const labelDE = labelDEIteration.value;

    const row = new Map();
    row.set("label", label);
    row.set("label_de", labelDE);
    variables.forEach((variable) => {
      const labelIndex: number = variable.labels.labels.indexOf(label);
      if (labelIndex >= 0) {
        row.set(variable.variable, variable.labels.values[Number(labelIndex)]);
      } else {
        row.set(variable.variable, null);
      }
    });
    rows.push(row);
    labelIteration = labels.next();
    labelDEIteration = labelsDE.next();
    done = labelIteration.done;
  }
  return rows;
}

/**
 * Remove all labels and values from variables where values are 0 or less.
 * @param {Array<variableType>} variables
 * @return {Array<variableType>}
 */
function removeMissings(variables: Array<variableType>) {
  for (const variable of variables) {
    if (variable.labels.values == null) {
      continue;
    }
    const labelsCopy = variable.labels.values.slice();
    labelsCopy.reverse().forEach((element, index) => {
      if (element <= 0) {
        const reversePosition = labelsCopy.length - index - 1;
        variable.labels.labels.splice(reversePosition, 1);
        variable.labels.labels_de.splice(reversePosition, 1);
        variable.labels.values.splice(reversePosition, 1);
      }
    });
  }
  return variables;
}

/**
 *
 * @param {variableType} variable
 * @param {any} _
 * @param {any} __
 * @return {boolean}
 */
function filterEmptyMetadata(variable: variableType, _: any, __: any): boolean {
  if (variable.labels.values == null) {
    return false;
  }
  if (variable.labels.values.length == 0) {
    return false;
  }
  return true;
}

/**
 * Parse information from API response to display in table.
 * @param {APIResponse} apiResponse
 * @return {parsedVariables}
 */
export function parseVariables(apiResponse: APIResponse): parsedVariables {
  const periods = new Map();
  const datasets = new Map();
  const variables: Array<variableType> = removeMissings(
    apiResponse["results"],
  ).filter(filterEmptyMetadata);
  if (variables.length <= 1) {
    return null;
  }

  const mainVariable = variables.find(
    (variable) => variable["variable"] == VariableName,
  );
  periods.set(mainVariable["variable"], mainVariable["period"]);
  datasets.set(mainVariable["variable"], mainVariable["dataset"]);

  variables.splice(variables.indexOf(mainVariable), 1);

  const mainLabels = removeCodesFromLabelsSet(mainVariable["labels"]);
  mainVariable.labels.labels = Array.from(mainLabels.labels.keys());
  mainVariable.labels.labels_de = Array.from(mainLabels.labelsDE.keys());
  for (const variable of variables) {
    periods.set(variable["variable"], variable["period"]);
    datasets.set(variable["variable"], variable["dataset"]);
    const labels = removeCodesFromLabelsArray(variable["labels"]);
    variable.labels.labels = labels.labels;
    variable.labels.labels_de = labels.labelsDE;
    for (const [index, label] of labels.labels.entries()) {
      mainLabels["labels"].add(label);
      mainLabels["labelsDE"].add(labels["labelsDE"][Number(index)]);
    }
  }
  variables.push(mainVariable);
  const values = fillRows(variables, mainLabels);
  return {
    labels: new Map([
      ["labels", Array.from(mainLabels.labels)],
      ["labels_de", Array.from(mainLabels.labelsDE)],
    ]),
    periods: new Map(
      [...periods.entries()].sort((left, right) => left[1] - right[1]),
    ),
    datasets,
    values,
  };
}

const VariableName: string = document.getElementById("variable-name").innerHTML;

/**
 *
 */
async function getLabelData() {
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
  parseVariables(await response.json());
}

type variableType = {
  variable: string;
  dataset: string;
  labels: {
    labels: Array<string>;
    labels_de: Array<string>;
    values: Array<number>;
  };
};

/**
 *
 * @param labels
 * @returns
 */
function removeCodesFromLabelsSet(labels: Array<string>): Set<string> {
  const out: Set<string> = new Set();
  labels.forEach((label) => {
    out.add(label.replace(/^\[.*?\]\s/, ""));
  });
  return out;
}

/**
 *
 * @param labels
 * @returns
 */
function removeCodesFromLabelsArray(labels: Array<string>): Array<string> {
  const out: Array<string> = [];
  labels.forEach((label) => {
    out.push(label.replace(/^\[.*?\]\s/, ""));
  });
  return out;
}

/**
 *
 * @param variables
 */
function parseVariables(apiResponse: {results: Array<variableType>}) {
  const variables: Array<variableType> = apiResponse["results"];
  const mainVariable = variables.find(
    (variable) => variable["variable"] == VariableName
  );
  variables.splice(variables.indexOf(mainVariable), 1);
  console.log(variables);
  const mainLabels = removeCodesFromLabelsSet(mainVariable["labels"]["labels"]);
  const mainValues = mainVariable["labels"]["values"];
  const table = new Map();
  table.set("labels", mainLabels);
  table.set(mainVariable["variable"], mainValues);
  variables.forEach((variable) => {
    const labels = removeCodesFromLabelsArray(variable["labels"]["labels"]);
    labels.forEach((label, index) => {
      if (mainLabels.has(label)) {
      }
    });
  });
}

getLabelData();

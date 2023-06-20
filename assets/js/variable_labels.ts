const VariableName: string = document.getElementById("variable-name").innerHTML;

const labelRegex = /^\[.*?\]\s/;

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
export function removeCodesFromLabelsMap(
  labels: Array<string>
): Map<string, number> {
  const out: Map<string, number> = new Map();
  labels.forEach((label, index) => {
    out.set(label.replace(labelRegex, ""), index);
  });
  return out;
}

/**
 *
 * @param labels
 * @returns
 */
export function removeCodesFromLabelsArray(
  labels: Array<string>
): Array<string> {
  const out: Array<string> = [];
  labels.forEach((label) => {
    out.push(label.replace(labelRegex, ""));
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
  const mainLabels = removeCodesFromLabelsMap(mainVariable["labels"]["labels"]);
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

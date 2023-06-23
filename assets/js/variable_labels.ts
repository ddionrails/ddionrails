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
  labels: labelsContainer
};

/**
 *
 * @param labels
 * @returns
 */
export function removeCodesFromLabelsMap(
  labels: labelsContainer
): {"labels": Map<string, number>, "labelsDE": Map<string, number>} {
  const out: Map<string, number> = new Map();
  const outDE: Map<string, number> = new Map();
  labels["labels"].forEach((label, index) => {
    if (labels["values"][Number(index)] < 0) {
      return;
    }
    out.set(label.replace(labelRegex, ""), index);
    outDE.set(labels["labels_de"][Number(index)].replace(labelRegex, ""), index);
  });
  return {"labels": out, "labelsDE": outDE};
}

/**
 *
 * @param labels
 * @returns
 */
export function removeCodesFromLabelsArray(
  labels: labelsContainer
): {"labels": Array<string>, "labelsDE": Array<string>} {
  const out: Array<string> = [];
  const outDE: Array<string> = [];
  labels["labels"].forEach((label, index) => {
    if (labels["values"][Number(index)] < 0) {
      return;
    }
    out.push(label.replace(labelRegex, ""));
    outDE.push(labels["labels_de"][Number(index)].replace(labelRegex, ""));
  });
  return {"labels": out, "labelsDE": outDE};
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
  const mainValues = mainVariable["labels"]["values"];
  const table = new Map();
  table.set("labels", mainLabels);
  table.set(mainVariable["variable"], mainValues);
  variables.forEach((variable) => {
    periods.set(variable["variable"], variable["period"]);
    const labels = removeCodesFromLabelsArray(
      variable["labels"]
    );
    labels["labels"].forEach((label, index) => {
      if (mainLabels["labels"].has(label)) {
      } else {
        mainLabels["labels"].set(label, mainLabels["labels"].size - 1);
        mainLabels["labelsDE"].set(
          labels["labelsDE"][Number(index)], mainLabels["labelsDE"].size - 1
        );
      }
    });
  });
  return {
    "labels": new Map(
      [
        ["labels", Array.from(mainLabels["labels"].keys())],
        ["labels_de", Array.from(mainLabels["labelsDE"].keys())],
      ]
    ),
    periods,
  };
}

/**
 *
 */
async function getLabelData() {
  parseVariables(await getAPIData());
}

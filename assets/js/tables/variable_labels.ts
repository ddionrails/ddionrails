import * as $ from "jquery";
import "datatables.net-bs5";
import "datatables.net-responsive-bs5";
import "datatables.net-fixedcolumns";
import "datatables.net-fixedcolumns-bs5";

import { getTable } from "./table_language_management";
import { languageCode, languageConfig } from "../language_management";

import { getAPIData, parseVariables } from "../variable_labels";

const TableElement = getTable().cloneNode(true) as HTMLElement;

// Also in ../visualization.js
const LabelLimit = 100;

const study = document
  .querySelector("meta[name=study]")
  .getAttribute("content");
const datasetBaseURL = new URL(`${study}/datasets`, window.location.origin);

/**
 *
 */
async function initTable(): Promise<null> {
  const variableData = parseVariables(await getAPIData());
  if (variableData == null) {
    return;
  }
  if(variableData.labels.get("labels").length  > LabelLimit){
    return;
  }
  const columns = [];
  columns.push({
    title: "Label",
    data: "label",
    render(_data: any, _type: any, row: any) {
      if (languageCode() == "de") {
        if (row.get("label_de")) {
          return row.get("label_de");
        }
      }
      return row.get("label") ? row.get("label") : row.get("name");
    },
  });
  for (const variableName of variableData.periods.keys()) {
    const datasetURL = new URL(
      `datasets/${variableData.datasets.get(variableName)}/`,
      datasetBaseURL,
    );
    const variableURL = new URL(variableName, datasetURL);
    const header = document.createElement("div");
    const periodElement = document.createElement("p");
    let period = variableData.periods.get(variableName);
    if (period == "0") {
      period = "Long";
    }
    periodElement.innerHTML = period;
    header.appendChild(periodElement);

    const datasetLink = document.createElement("a");
    const variableLink = document.createElement("a");
    variableLink.href = variableURL.toString();
    variableLink.innerHTML = variableName;
    datasetLink.href = datasetBaseURL.toString();
    datasetLink.innerHTML = variableData.datasets.get(variableName);
    header.appendChild(datasetLink);
    header.appendChild(document.createElement("hr"));
    header.appendChild(variableLink);

    columns.push({
      title: String(header.outerHTML),
      render(_data: any, _type: any, row: any) {
        return row.get(variableName) || "";
      },
    });
  }
  const modifiedLanguageConfig = languageConfig();
  modifiedLanguageConfig.info = "";
  document.getElementById("label-table").classList.remove("hidden");
  // FixedColumns does not work well with tables that are filled during creation.
  const table = $("#value-labels-table").DataTable({
    language: modifiedLanguageConfig,
    scrollX: true,
    scrollY: "40em",
    scrollCollapse: true,
    data: variableData.values,
    ordering: false,
    paging: false,
    columns,
  });
  table.destroy();
  // Thats why the filled table is reinitialized with fixedColumns.
  $("#value-labels-table").DataTable({
    language: modifiedLanguageConfig,
    scrollX: true,
    scrollY: "40em",
    scrollCollapse: true,
    ordering: false,
    paging: false,
    fixedColumns: { start: 1 },
  });
}

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    if (record.type == "attributes") {
      const target = record.target as Element;
      if (
        target.nodeName == "BUTTON" &&
        target.hasAttribute("data-current-language")
      ) {
        const tableContainer = document.getElementById("table-container");
        tableContainer.innerHTML = "";
        tableContainer.appendChild(TableElement.cloneNode(true));
        initTable();
      }
    }
  });
});

const languageElement = document.getElementById("language-switch") as Node;
languageObserver.observe(languageElement, {
  attributes: true,
});

window.addEventListener("load", () => {
  initTable();
});

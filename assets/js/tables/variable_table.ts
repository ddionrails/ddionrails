import "datatables.net-bs5";
import "datatables.net-responsive-bs5";
import * as $ from "jquery";
import initSearchEventHandler from "./search_input_handling";
import {languageCode, languageConfig} from "../language_management";
import {switchTableLanguage} from "./table_language_management";

const variableApiURL = new URL("api/variables/", window.location.origin);
const urlPart = "variable";
const study = document.head
  .querySelector('meta[name="study"]')
  .getAttribute("content");
const dataset = document.head
  .querySelector('meta[name="dataset"]')
  .getAttribute("content");
const variableTableId = "variable-table";

variableApiURL.searchParams.append("dataset", dataset);
variableApiURL.searchParams.append("study", study);

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

const TableElement = document
  .getElementById(variableTableId)
  .cloneNode(true) as HTMLElement;

/**
 * Renders a table of datasets.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderVariableTable(table: any, url: string) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    language: languageConfig(),
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [[2, "asc"]],
    columns: [
      {
        data: "name", // Human readable label.
        orderable: false,
        render(_data: any, _type: any, row: any) {
          const link = document.createElement("a");
          link.href =
            window.location.protocol +
            "//" +
            window.location.hostname +
            `/${urlPart}/${row["id"]}`;
          link.textContent = row["name"];
          return link.outerHTML;
        },
      },
      {
        data: "label", // Human readable label.
        orderable: false,
        render(_data: any, _type: any, row: any) {
          if (languageCode() == "de") {
            return row["label_de"] ? row["label_de"] : row["name"];
          }
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "position",
        render(_data: any, _type: any, row: any) {
          return row["position"];
        },
        visible: false,
      },
    ],
  });
}

document
  .getElementById("table-container")
  .setAttribute("data-bs-type", variableTableId);

window.addEventListener("load", () => {
  initSearchEventHandler(
    variableApiURL,
    renderVariableTable,
    `#${variableTableId}`
  );
});

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    switchTableLanguage(
      record,
      renderVariableTable,
      TableElement,
      variableApiURL
    );
  });
});

const languageElement = document.getElementById("language-switch") as Node;
languageObserver.observe(languageElement, {
  attributes: true,
});

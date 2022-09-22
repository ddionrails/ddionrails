import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";
import $ from "jquery";
import initSearchEventHandler from "./search_input_handling";

const variableApiURL = new URL("api/variables/", window.location.origin);
const urlPart = "variable";
const study = document.head
  .querySelector('meta[name="study"]')
  .getAttribute("content");
const dataset = document.head
  .querySelector('meta[name="dataset"]')
  .getAttribute("content");

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

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
    language: {
      searchPlaceholder: "Search all columns",
    },
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
        render(_data, _type, row) {
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
        render(_data, _type, row) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "position",
        render(_data, _type, row) {
          return row["position"];
        },
        visible: false,
      },
    ],
  });
}

window.addEventListener("load", () => {
  variableApiURL.searchParams.append("dataset", dataset);
  initSearchEventHandler(
    variableApiURL,
    study,
    renderVariableTable,
    "#variable-table"
  );
});
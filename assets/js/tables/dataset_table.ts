import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";
import $ from "jquery";
import initSearchEventHandler from "./search_input_handling";

const datasetsApiURL = new URL("api/datasets/", window.location.origin);
const urlPart = "datasets";
const study = document.head
  .querySelector('meta[name="study"]')
  .getAttribute("content");

/**
 * Renders a table of datasets.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderDatasetTable(table: string, url: string) {
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
    order: [[3, "desc"]],
    columns: [
      {
        data: "dataset",
        render(_data: any, _type: any, row: any) {
          const link = document.createElement("a");
          link.href =
            window.location.protocol +
            "//" +
            window.location.hostname +
            `/${row["study_name"]}/${urlPart}/${row["name"]}`;
          link.textContent = row["name"];
          return link.outerHTML;
        },
      },
      {
        data: "label",
        render(_data: any, _type: any, row: any) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "conceptual-dataset",
        render(_data: any, _type: any, row: any) {
          return row["conceptual_dataset_label"];
        },
      },
      {
        data: "period",
        render(_data: any, _type: any, row: any) {
          if (row["period_label"] !== "") {
            return row["period_label"];
          }
          return row["period_name"];
        },
      },
      {
        data: "analysis_unit_name",
        render(_data: any, _type: any, row: any) {
          return row["analysis_unit_label"];
        },
      },
      {
        data: "folder",
        render(_data: any, _type: any, row: any) {
          return row["folder"];
        },
      },
      {
        data: "primary-key",
        render(_data: any, _type: any, row: any) {
          const keyParts = row["primary_key"];
          const linkContainer = document.createElement("p");

          for (const variable of keyParts) {
            const link = document.createElement("a");
            link.href =
              window.location.protocol +
              "//" +
              window.location.hostname +
              `/${row["study_name"]}/${urlPart}/${row["name"]}/${variable}`;
            link.textContent = variable;
            linkContainer.appendChild(link);
            linkContainer.append(" ");
          }

          return linkContainer.outerHTML;
        },
      },
    ],
  });
}

window.addEventListener("load", () => {
  initSearchEventHandler(
    datasetsApiURL,
    study,
    renderDatasetTable,
    "#dataset-table"
  );
});

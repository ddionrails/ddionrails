import "datatables.net-bs5";
import "datatables.net-responsive-bs5";
import * as $ from "jquery";
import initSearchEventHandler from "./search_input_handling";
import {switchTableLanguage} from "./table_language_management";
import {languageCode, languageConfig} from "../language_management";

const datasetsApiURL = new URL("api/datasets/", window.location.origin);
const urlPart = "datasets";
const study = document.head
  .querySelector('meta[name="study"]')
  .getAttribute("content");

const attachmentIcon = document.createElement("i");
attachmentIcon.classList.add("fa-solid", "fa-file-lines");
const attachmentLinkTemplate = document.createElement("a");
attachmentLinkTemplate.appendChild(attachmentIcon);

datasetsApiURL.searchParams.append("study", study);

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
    language: languageConfig(),
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [[0, "asc"]],
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
          if (languageCode() == "de") {
            if (row["label_de"]) {
              return row["label_de"];
            }
          }
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "conceptual-dataset",
        render(_data: any, _type: any, row: any) {
          if (languageCode() == "de") {
            if (row["conceptual_dataset_label_de"]) {
              return row["conceptual_dataset_label_de"];
            }
          }
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
          if (languageCode() == "de") {
            if (row["analysis_unit_label_de"]) {
              return row["analysis_unit_label_de"];
            }
          }
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
      {
        data: "attachments", // Actual name of the entity.
        className: "attachment",
        orderable: false,
        render(_data: any, _type: any, row: any) {
          const linkContainer = document.createElement("div");
          for (const attachment of row["attachments"]) {
            const link = attachmentLinkTemplate.cloneNode(
              true
            ) as HTMLLinkElement;
            link.href = attachment["url"];
            link.title = attachment["url_text"];
            linkContainer.appendChild(link);
            const text = document.createElement("text");
            text.classList.add("hidden");
            text.textContent = attachment["url_text"];
            linkContainer.appendChild(text);
          }
          return linkContainer.outerHTML;
        },
      },
    ],
  });
}

const datasetTableId = "dataset-table";

const TableElement = document
  .getElementById(datasetTableId)
  .cloneNode(true) as HTMLElement;
document
  .getElementById("table-container")
  .setAttribute("data-type", datasetTableId);

window.addEventListener("load", () => {
  initSearchEventHandler(
    datasetsApiURL,
    renderDatasetTable,
    `#${datasetTableId}`
  );
});

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    switchTableLanguage(
      record,
      renderDatasetTable,
      TableElement,
      datasetsApiURL
    );
  });
});

const languageElement = document.getElementById("language-switch") as Node;
languageObserver.observe(languageElement, {
  attributes: true,
});

import "datatables.net-bs5";
import "datatables.net-responsive-bs5";
import * as $ from "jquery";
import initSearchEventHandler from "./search_input_handling";
import {switchTableLanguage, getTable} from "./table_language_management";
import {languageCode, languageConfig} from "../language_management";

const instrumentApiURL = new URL("api/instruments/", window.location.origin);
const urlPart = "inst";
const study = document.querySelector("#study-name").getAttribute("value");
instrumentApiURL.searchParams.append("study", study);

const TableElement = getTable().cloneNode(true) as HTMLElement;

const hasExtendedMetadata = document
  .querySelector("#study-name")
  .getAttribute("has-extended-metadata");

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

const attachmentIcon = document.createElement("i");
attachmentIcon.classList.add("fa-solid", "fa-file-lines");
const attachmentLinkTemplate = document.createElement("a");
attachmentLinkTemplate.appendChild(attachmentIcon);

/**
 * Renders a table of instruments.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderFullInstrumentTable(table: any, url: string) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    language: languageConfig(),
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [
      [2, "desc"],
      [3, "asc"],
      [5, "asc"],
    ],
    columns: [
      {
        data: "instrument", // Human readable label.
        render(_data: any, _type: any, row: any) {
          if (row["has_questions"] === true) {
            const link = document.createElement("a");
            link.href =
              window.location.protocol +
              "//" +
              window.location.hostname +
              `/${row["study_name"]}/${urlPart}/${row["name"]}`;
            link.textContent = row["name"];
            return link.outerHTML;
          }
          return row["name"];
        },
      },
      {
        data: "label",
        render(_data: any, _type: any, row: any) {
          if (languageCode() == "de" && row["label_de"]) {
            return row["label_de"];
          }
          return row["label"] ? row["label"] : row["name"];
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
        data: "type_position",
        render(_data: any, _type: any, row: any) {
          return row["type"]["position"];
        },
        visible: false,
      },
      {
        data: "type",
        render(_data: any, _type: any, row: any) {
          return row["type"][languageCode()];
        },
      },
      {
        data: "mode",
        render(_data: any, _type: any, row: any) {
          return row["mode"];
        },
      },
      {
        data: "attachments",
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

/**
 * Renders a table of instruments.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderInstrumentTable(table: any, url: string) {
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
    order: [[2, "desc"]],
    columns: [
      {
        data: "instrument",
        render(_data: any, _type: any, row: any) {
          if (row["has_questions"] === true) {
            const link = document.createElement("a");
            link.href =
              window.location.protocol +
              "//" +
              window.location.hostname +
              `/${row["study_name"]}/${urlPart}/${row["name"]}`;
            link.textContent = row["name"];
            return link.outerHTML;
          }
          return row["name"];
        },
      },
      {
        data: "label",
        render(_data: any, _type: any, row: any) {
          if (languageCode() == "de" && row["label_de"]) {
            return row["label_de"];
          }
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "period",
        render(_data: any, _type: any, row: any) {
          return row["period_name"];
        },
      },
      {
        data: "analysis_unit",
        render(_data: any, _type: any, row: any) {
          return row["analysis_unit_name"];
        },
      },
      {
        data: "attachments",
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

const instrumentTableRenderer: CallableFunction =
  hasExtendedMetadata == "True"
    ? renderFullInstrumentTable
    : renderInstrumentTable;

window.addEventListener("load", () => {
  initSearchEventHandler(
    instrumentApiURL,
    instrumentTableRenderer,
    "#instrument-table"
  );
});

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    switchTableLanguage(
      record,
      instrumentTableRenderer,
      TableElement,
      instrumentApiURL
    );
  });
});

const languageElement = document.getElementById("language-switch") as Node;
languageObserver.observe(languageElement, {
  attributes: true,
});

import "datatables.net-bs5";
import "datatables.net-buttons-bs5";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs5";
import * as $ from "jquery";
import initSearchEventHandler from "./search_input_handling";
import {languageCode, languageConfig} from "../language_management";
import {getTable, switchTableLanguage} from "./table_language_management";

const questionsApiURL = new URL("api/questions/", window.location.origin);
const urlPart = "question";
const study = document.head
  .querySelector('meta[name="study"]')
  .getAttribute("content");
const instrument = document.head
  .querySelector('meta[name="instrument"]')
  .getAttribute("content");

const TableElement = getTable().cloneNode(true) as HTMLElement;

questionsApiURL.searchParams.append("instrument", instrument);
questionsApiURL.searchParams.append("study", study);

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

/**
 * Renders a table of questions.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderQuestionTable(table: string, url: string) {
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
          if (languageCode() == "de" && row["label_de"]) {
            return row["label_de"];
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

const questionTableId = "question-table";

window.addEventListener("load", () => {
  initSearchEventHandler(
    questionsApiURL,
    renderQuestionTable,
    `#${questionTableId}`
  );
});

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    switchTableLanguage(
      record,
      renderQuestionTable,
      TableElement,
      questionsApiURL
    );
  });
});

const languageElement = document.getElementById("language-switch") as Node;
languageObserver.observe(languageElement, {
  attributes: true,
});

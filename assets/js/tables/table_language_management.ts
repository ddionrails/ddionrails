import initSearchEventHandler from "./search_input_handling";
import {languageCode, switchLanguage} from "../language_management";

/**
 *
 * @param {MutationRecord} record
 * @param {CallableFunction} tableRenderFunction
 * @param {HTMLElement} emptyTableElement
 */
function switchTableLanguage(
  record: MutationRecord,
  tableRenderFunction: CallableFunction,
  emptyTableElement: HTMLElement,
  apiURL: URL
) {
  if (record.type == "attributes") {
    const target = record.target as Element;
    if (
      target.nodeName == "BUTTON" &&
      target.hasAttribute("data-current-language")
    ) {
      const tableContainer = document.getElementById("table-container");
      const tableId = tableContainer.getAttribute("data-type");
      tableContainer.innerHTML = "";
      tableContainer.appendChild(emptyTableElement.cloneNode(true));
      initSearchEventHandler(apiURL, tableRenderFunction, `#${tableId}`);
      switchLanguage(document, languageCode());
    }
  }
}

/**
 * Get DataTable
 * @return {HTMLTableElement}
 */
function getTable() {
  return document.querySelector("#table-container > table");
}

export {switchTableLanguage};
export {getTable};

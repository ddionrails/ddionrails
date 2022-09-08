import type DataTable from "datatables.net";

const inputTemplate = document.createElement("input") as HTMLInputElement;
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

interface SearchInputs {
  [details: string]: HTMLInputElement;
}

/**
 * Generate text input field for every column in the DataTable
 *
 * @param {*} table    DOM element object of the table.
 * @return {object}    Maps column names to input elements.
 */
function addSearchInput(table: HTMLTableElement): SearchInputs {
  const header: NodeListOf<HTMLTableCellElement> =
    table.querySelectorAll(".header > th");
  const searchInputs: SearchInputs = {};
  for (const headerColumn of header) {
    const columnName = headerColumn.getAttribute("title") as string;
    const searchHead = table.querySelector(`.search-header > .${columnName}`);
    const searchInput = inputTemplate.cloneNode() as HTMLInputElement;
    searchInput.setAttribute("placeholder", "Search");
    searchHead.appendChild(searchInput);
    searchInputs[columnName.toString()] = searchInput;
  }
  return searchInputs;
}

/**
 *
 * @param {string} searchInput
 * @param {string} columnName
 * @param {any} tableAPI
 */
function performSearch(
  searchInput: string,
  columnName: string,
  tableAPI: any
): void {
  tableAPI.column(`.${columnName}`).search(searchInput, true, false).draw();
}

/**
 *
 * @param {URL} metadataApiUrl
 * @param {string} study
 * @param {CallableFunction} tableRenderer
 * @param {string}tableSelector
 */
function initSearchEventHandler(
  metadataApiUrl: URL,
  study: string,
  tableRenderer: CallableFunction,
  tableSelector: string
): void {
  const datasetsTable = document.querySelector(
    tableSelector
  ) as HTMLTableElement;

  const datasetsAPI = new URL(metadataApiUrl.toString());
  datasetsAPI.searchParams.append("study", study);
  datasetsAPI.searchParams.append("paginate", "False");
  const tableAPI = tableRenderer(datasetsTable, datasetsAPI) as DataTable<any>;
  const columnInputMapping = addSearchInput(datasetsTable);
  for (const columnName of Object.keys(columnInputMapping)) {
    columnInputMapping[columnName.toString()].addEventListener(
      "input",
      (event) => {
        const searchInputField = event.currentTarget as HTMLInputElement;
        performSearch(searchInputField.value, columnName, tableAPI);
      }
    );
  }
}

export default initSearchEventHandler;

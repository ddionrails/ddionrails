import type DataTable from "datatables.net";

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

interface SearchInputs {
  [details: string]: HTMLElement;
}

/**
 *
 * @param {*} table    DOM element object of the table.
 * @param {*} tableAPI dataTable object of the table with full API.
 * @return {object}    Maps column names to input elements.
 */
function addSearchInput(table: HTMLTableElement) {
  const header: NodeListOf<HTMLTableCellElement> =
    table.querySelectorAll(".header > th");
  const searchInputs: SearchInputs = {};
  for (const headerColumn of header) {
    const columnName = headerColumn.getAttribute("title") as string;
    const searchHead = table.querySelector(`.search-header > .${columnName}`);
    const searchInput = inputTemplate.cloneNode() as HTMLElement;
    searchInput.setAttribute("placeholder", "Search");
    searchHead.appendChild(searchInput);
    searchInputs[columnName.toString()] = searchInput;
  }
  return searchInputs;
}

/**
 *
 * @param {*} event
 * @param {*} columnName
 * @param {*} tableAPI
 */
function addSearchEvent(event: Event, columnName: string, tableAPI: any) {
  const target = event.currentTarget as HTMLInputElement;
  tableAPI.column(`.${columnName}`).search(target.value, true, false).draw();
}

/**
 *
 * @param {URL} metadataApiUrl
 * @param {string} study
 * @param {CallableFunction} tableRenderer
 * @param {string}tableSelector
 */
function searchInitEventHandler(
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
        addSearchEvent(event, columnName, tableAPI);
      }
    );
  }
}

export default searchInitEventHandler;

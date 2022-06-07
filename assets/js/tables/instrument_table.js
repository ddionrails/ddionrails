import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

const instrumentApiURL = new URL("api/instruments/", window.location.origin);
const urlPart = "inst";
const study = document.querySelector("#study-name").getAttribute("value");

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
function renderInstrumentTable(table, url) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
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
        render(_data, _type, row) {
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
        data: "label", // Human readable label.
        render(_data, _type, row) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "period", // Actual name of the entity.
        render(_data, _type, row) {
          return row["period_name"];
        },
      },
      {
        data: "type_position", // Actual name of the entity.
        render(_data, _type, row) {
          return row["type"]["position"];
        },
        visible: false,
      },
      {
        data: "type", // Actual name of the entity.
        render(_data, _type, row) {
          return row["type"]["en"];
        },
      },
      {
        data: "mode", // Actual name of the entity.
        render(_data, _type, row) {
          return row["mode"];
        },
      },
      {
        data: "attachments", // Actual name of the entity.
        className: "attachment",
        orderable: false,
        render(_data, _type, row) {
          const linkContainer = document.createElement("div");
          for (const attachment of row["attachments"]) {
            const link = attachmentLinkTemplate.cloneNode(true);
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
 *
 * @param {*} table    DOM element object of the table.
 * @param {*} tableAPI dataTable object of the table with full API.
 * @return {object}    Maps column names to input elements.
 */
function addSearchInput(table) {
  const header = table.querySelectorAll(".header > th");
  const searchInputs = {};
  for (const headerColumn of header) {
    const columnName = headerColumn.getAttribute("title");
    const searchHead = table.querySelector(`.search-header > .${columnName}`);
    const searchInput = inputTemplate.cloneNode();
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
function addSearchEvent(event) {
  event.currentTarget.tableAPI
    .column(`.${event.currentTarget.column}`)
    .search(event.currentTarget.value)
    .draw();
}

window.addEventListener("load", function() {
  const instrumentTable = document.querySelector("#instrument-table");

  const instrumentAPI = new URL(instrumentApiURL.toString());
  instrumentAPI.searchParams.append("study", study);
  instrumentAPI.searchParams.append("paginate", "False");
  const tableAPI = renderInstrumentTable(instrumentTable, instrumentAPI);
  const columnInputMapping = addSearchInput(instrumentTable);
  for (const columnName of Object.keys(columnInputMapping)) {
    columnInputMapping[columnName.toString()].column = columnName;
    columnInputMapping[columnName.toString()].tableAPI = tableAPI;
    columnInputMapping[columnName.toString()].addEventListener(
      "input",
      addSearchEvent
    );
  }
});

import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

const datasetsApiURL = new URL("api/datasets/", window.location.origin);
const urlPart = "datasets";
const study = document.querySelector("#study-name").getAttribute("value");

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

const attachmentIcon = document.createElement("i");
attachmentIcon.classList.add("fa-solid", "fa-file-lines");
const attachmentLinkTemplate = document.createElement("a");
attachmentLinkTemplate.appendChild(attachmentIcon);

/**
 * Renders a table of datasets.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderDatasetTable(table, url) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [[3, "desc"]],
    columns: [
      {
        data: "dataset", // Human readable label.
        render(_data, _type, row) {
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
        data: "label", // Human readable label.
        render(_data, _type, row) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "conceptual-dataset", // Actual name of the entity.
        render(_data, _type, row) {
          return row["conceptual_dataset_label"];
        },
      },
      {
        data: "period", // Actual name of the entity.
        render(_data, _type, row) {
          return row["period_name"];
        },
      },
      {
        data: "analysis_unit_name", // Actual name of the entity.
        render(_data, _type, row) {
          return row["analysis_unit_label"];
        },
      },
      {
        data: "folder", // Actual name of the entity.
        render(_data, _type, row) {
          return row["folder"];
        },
      },
      {
        data: "primary-key", // Actual name of the entity.
        render(_data, _type, row) {
          // http://localhost/soep-core/datasets/bipluecke/cid
          const keyParts = row["primary_key"];
          const linkContainer = document.createElement("p");

          for ( const variable of keyParts) {
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
  const datasetsTable = document.querySelector("#dataset-table");

  const datasetsAPI = new URL(datasetsApiURL.toString());
  datasetsAPI.searchParams.append("study", study);
  datasetsAPI.searchParams.append("paginate", "False");
  const tableAPI = renderDatasetTable(datasetsTable, datasetsAPI);
  const columnInputMapping = addSearchInput(datasetsTable);
  for (const columnName of Object.keys(columnInputMapping)) {
    columnInputMapping[columnName.toString()].column = columnName;
    columnInputMapping[columnName.toString()].tableAPI = tableAPI;
    columnInputMapping[columnName.toString()].addEventListener(
      "input",
      addSearchEvent
    );
  }
});

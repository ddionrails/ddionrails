import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

const instrumentApiURL = new URL("api/instruments/", window.location.origin);
const urlPart = "inst";
const study = document.querySelector("#study-name").getAttribute("value");


/**
 * Renders a table of instruments.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 */
function renderEntityTable(table, url) {
  $(table).dataTable(
    {
      "ajax":
      {
        url,
        "dataSrc":
          "",
        "cache": true,
      },
      "order": [[2, "desc"]],
      "columns": [
        {
          data: "instrument", // Human readable label.
          render(_data, _type, row) {
            if (row["question_count"] > 0) {
              const link = document.createElement("a");
              link.href = window.location.protocol + "//" +
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
            return (row["label"] ? row["label"] : row["name"]);
          },
        },
        {
          data: "period", // Actual name of the entity.
          render(_data, _type, row) {
            return row["period_name"];
          },
        },
      ],
    }
  );
};

window.addEventListener("load", function() {
  const instrumentTable = document.querySelector("#instrument-table");

  const instrumentAPI = new URL(instrumentApiURL.toString());
  instrumentAPI.searchParams.append("study", study);
  instrumentAPI.searchParams.append("paginate", "False");
  renderEntityTable(instrumentTable, instrumentAPI);
});



import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

const variablesApiUrl = new URL("api/variables/", window.location.origin);
const questionsApiUrl = new URL("api/questions/", window.location.origin);
const concept = document.querySelector("#concept-name").getAttribute("value");


/**
 * Renders a table of either variables or questions related through a concept.
 *
 * Displays the entities(variable/question) themselves and their immediate
 * parents (dataset/instrument) in the model hierarchy.
 * Entity and parent names are enclosed by a link to their representation on the site.
 *
 * @param {Object} entity Metadata about the type of related entities to render.
 *                        Can be of type variable or question.
 *                        Further contains information about how to retrieve and
 *                        display the entities immediate parent model.
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 */
function renderEntityTable(entity, table, url) {
  $(table).dataTable(
    {
      "ajax":
      {
        url,
        "dataSrc":
         "",
      },
      "columns": [
        {
          data: "study", // Human readable label.
          render(_data, _type, row) {
            const link = document.createElement("a");
            link.href = window.location.protocol + "//" + window.location.hostname +
              `/${row["study_name"]}`;
            link.textContent = row["study_label"];

            return link.outerHTML;
          },
        },
        {
          data: "label", // Human readable label.
          render(_data, _type, row) {
            return (row["label"] ? row["label"] : row["name"] );
          },
        },
        {
          data: "entity", // Actual name of the entity.
          render(_data, _type, row) {
            const link = document.createElement("a");
            link.href = window.location.protocol + "//" + window.location.hostname +
              `/${row["study_name"]}/${entity.parentURL}/` +
              row[entity.parentType] + "/" + row["name"];
            link.textContent = row["name"];

            return link.outerHTML;
          },
        },
        {data: "parent",
          render(_data, _type, row) {
            const link = document.createElement("a");
            link.href = window.location.protocol + "//" + window.location.hostname +
              `/${row["study_name"]}/${entity.parentURL}/` + row[entity.parentType];
            link.textContent = row[entity.parentType];

            return link.outerHTML;
          },
        },
      ],
    }
  );
};

window.addEventListener("load", function() {
  const questionTable = document.querySelector("#question-table");

  const question = {
    type: "question",
    parentURL: "inst",
    parentType: "instrument_name",
  };
  const questionsAPI = new URL(questionsApiUrl.toString());
  questionsAPI.searchParams.append("concept", concept);
  renderEntityTable(question, questionTable, questionsAPI);

  const variableTable = document.querySelector("#variable-table");

  const variable = {
    type: "variable",
    parentURL: "data",
    parentType: "dataset_name",
  };
  const variablesAPI = new URL(variablesApiUrl.toString());
  variablesAPI.searchParams.append("concept", concept);
  renderEntityTable(variable, variableTable, variablesAPI);
});



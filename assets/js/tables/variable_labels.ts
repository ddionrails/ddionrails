import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";
import * as $ from "jquery";
import {switchTableLanguage, getTable} from "./table_language_management";
import {languageCode, languageConfig} from "../language_management";

import {getAPIData, parseVariables} from "../variable_labels";

/**
 *
 */
async function initTable() {
  const variableData = parseVariables(await getAPIData());
  const columns = [];
  columns.push({
    title: "label",
    data: "label",
    render(_data: any, _type: any, row: any) {
      if (languageCode() == "de") {
        if (row.get("label_de")) {
          return row.get("label_de");
        }
      }
      return row.get("label") ? row.get("label") : row.get("name");
    },
  });
  for (const variableName of variableData.periods.keys()) {
    columns.push({
      title: variableName,
      render(_data: any, _type: any, row: any) {
        return row.get(variableName) || "";
      },
    });
  }
  $("#value-labels-table").DataTable({
    language: languageConfig(),
    data: variableData.values,
    ordering: false,
    paging: false,
    columns,
  });
}

initTable();

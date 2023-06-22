import {NONE} from "../../../docker/transfer.server/renv/library/R-4.1/x86_64-pc-linux-gnu/DT/htmlwidgets/lib/datatables-extensions/Buttons/js/pdfmake";
import {
  getAPIData,
  removeCodesFromLabelsArray,
  removeCodesFromLabelsMap,
} from "../variable_labels";
const apiResponse = require("./testdata/response.json");

global.fetch = jest.fn(() => Promise.resolve(
  {json: () => Promise.resolve(apiResponse)}
)) as jest.Mock;


describe("Test function to remove codes from labels", () => {
  test("Result should be a Map with former indices as values", () => {
    const input = ["[-1] Test", "[2] Test2"];
    const expected = new Map();
    expected.set("Test", 0);
    expected.set("Test2", 1);
    expect(removeCodesFromLabelsMap(input)).toEqual(expected);
  });
  test("Result should be an Array", () => {
    const input = ["[-1] Test", "[2] Test2"];
    const expected = ["Test", "Test2"];
    expect(removeCodesFromLabelsArray(input)).toEqual(expected);
  });
});

describe("Test API call", () => {
  test("Function should return test file content", async () => {
    expect(await getAPIData()).toEqual(apiResponse);
  });
});


const expectedParsedOutput = [
  ["one", "two", "three", "four", "five", "six", "for"],
  [NONE, NONE, NONE, NONE, NONE, NONE],
  [1, 2, 3, NONE, 5, NONE],
  [1, 2, 3, 4, 5, 6, NONE],
];

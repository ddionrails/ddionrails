import {removeCodesFromLabelsMap} from "../variable_labels";

describe("Test function to remove codes from labels", () => {
  test("Result should be a Map with former indices as values", () => {
    const input = ["[-1] Test", "[2] Test2"];
    const expected = new Map();
    expected.set("Test", 0);
    expected.set("Test2", 1);
    expect(removeCodesFromLabelsMap(input)).toEqual(expected);
  });
});

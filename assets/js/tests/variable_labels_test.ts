import {
  getAPIData,
  parseVariables,
  removeCodesFromLabelsArray,
  removeCodesFromLabelsMap,
} from "../variable_labels";
const apiResponse = require("./testdata/response.json");

global.fetch = jest.fn(() =>
  Promise.resolve({json: () => Promise.resolve(apiResponse)})
) as jest.Mock;

const labelsWithoutMissings = {
  labels: ["[1] Test", "[2] Test2"],
  labels_de: ["[1] TestDE", "[2] TestDE2"],
  values: [1, 2],
};

describe("Test function to remove codes from labels", () => {
  test("Result should be a Map with former indices as values", () => {
    const labels = new Map();
    labels.set("Test", 0);
    labels.set("Test2", 1);
    const labelsDE = new Map();
    labelsDE.set("TestDE", 0);
    labelsDE.set("TestDE2", 1);
    const expected = {labels, labelsDE};
    expect(removeCodesFromLabelsMap(labelsWithoutMissings)).toEqual(expected);
  });
  test("Result should be an Array", () => {
    const expected = {
      labels: ["Test", "Test2"],
      labelsDE: ["TestDE", "TestDE2"],
    };
    expect(removeCodesFromLabelsArray(labelsWithoutMissings)).toEqual(expected);
  });
});

describe("Test API call", () => {
  test("Function should return test file content", async () => {
    expect(await getAPIData()).toEqual(apiResponse);
  });
});

const expectedVariables = new Map([
  ["third_variable_name", [null, null, null, null, null, null, null]],
  ["other_variable_name", [1, 2, 3, null, 5, null, 4]],
  ["variable_name", [1, 2, 3, 4, 5, 6, null]],
]);

const expectedRows: Array<{
  label: string;
  label_de: string;
  variable_name: number;
  other_variable_name: number;
  third_variable_name: number;
}> = [
  {
    label: "one",
    label_de: "eins",
    variable_name: 1,
    other_variable_name: 1,
    third_variable_name: null,
  },
  {
    label: "two",
    label_de: "zwei",
    variable_name: 2,
    other_variable_name: 2,
    third_variable_name: null,
  },
  {
    label: "three",
    label_de: "drei",
    variable_name: 3,
    other_variable_name: 3,
    third_variable_name: null,
  },
  {
    label: "four",
    label_de: "vier",
    variable_name: 4,
    other_variable_name: null,
    third_variable_name: null,
  },
  {
    label: "five",
    label_de: "fünf",
    variable_name: 5,
    other_variable_name: 5,
    third_variable_name: null,
  },
  {
    label: "six",
    label_de: "sechs",
    variable_name: 6,
    other_variable_name: null,
    third_variable_name: null,
  },
  {
    label: "for",
    label_de: "vair",
    variable_name: null,
    other_variable_name: 4,
    third_variable_name: null,
  },
];

const expectedRowsMaps: Array<Map<string, any>> = [];

for (const element of expectedRows) {
  const toMap = new Map(Object.entries(element));
  expectedRowsMaps.push(toMap);
}

const expectedPeriods = new Map([
  ["third_variable_name", "1990"],
  ["other_variable_name", "1992"],
  ["variable_name", "1993"],
]);

const expectedParsedLabels = new Map([
  ["labels", ["one", "two", "three", "four", "five", "six", "for"]],
  ["labels_de", ["eins", "zwei", "drei", "vier", "fünf", "sechs", "vair"]],
]);

const expectedParsedOutput = {
  values: expectedRows,
  labels: expectedParsedLabels,
  periods: expectedPeriods,
};

describe("Test Parsing of API call content", () => {
  const result = parseVariables(apiResponse);
  test("Test period output", async () => {
    expect(result["periods"]).toEqual(expectedPeriods);
  });
  test("Test labels output", async () => {
    expect(result["labels"]).toEqual(expectedParsedLabels);
  });
  test("Test values output", async () => {
    for (const [index, row] of expectedRowsMaps.entries()) {
      // eslint-disable-next-line guard-for-in
      for (const key in row.keys()) {
        expect(result["values"][Number(index)].get(key) == row.get(key)).toBe(
          true
        );
      }
    }
  });
});

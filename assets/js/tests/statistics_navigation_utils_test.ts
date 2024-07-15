import {setUpSubTopics} from "../statistics_navigation_utils";

const apiResponse = require("./testdata/topic_leaves_response.json");

global.fetch = jest.fn(() =>
  Promise.resolve({json: () => Promise.resolve(apiResponse)})
) as jest.Mock;

describe("Test function to set up child topics display", () => {
  test("TODO: Set up proper test", async () => {
    const result = await setUpSubTopics();
    expect(result).toHaveProperty("dp");
  });
});

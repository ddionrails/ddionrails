import {setUpSubTopics} from "../statistics_navigation_utils";

const apiResponse = require("./testdata/topic_leaves_response.json");
const variableApiResponse = require("./testdata/topic_leaves_response.json");

const origin = "http://localhost";
const urn = "api/topic-leaves/?study=soep-core&language=en";
const topicRequestURL = `${origin}/${urn}`;
const variableUrn =
  "api/variables/?topic=tu&study=soep-core&statistics=True&paginate=False";

global.window = Object.create(window);
Object.defineProperty(window, "location", {
  value: {
    origin,
  },
  writable: true,
});

global.fetch = jest.fn((request) => {
  if (request === topicRequestURL) {
    return Promise.resolve({json: () => Promise.resolve(apiResponse)});
  }
  if (request === "") {
  }
}) as jest.Mock;

global.document = Object.create(document);

global.document.body.innerHTML =
  "<html>" +
  "<head> <meta name='study' content='soep-core'> </head>" +
  "<button id='language-switch' data-current-language='en' type='button' class='btn btn-outline-dark'></button>" +
  "</html>";

describe("Test function to set up child topics display", () => {
  test("TODO: Set up proper test", async () => {
    const result = await setUpSubTopics();
    expect(result).toHaveProperty("dp");
  });
});

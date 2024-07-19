import {setUpSubTopics} from "../statistics_navigation_utils";

const topicLeafsApiResponse = require("./testdata/topic_leafs_response.json");
const variableApiResponse = require("./testdata/variables_response.json");

const origin = "http://localhost";

global.window = Object.create(window);
Object.defineProperty(window, "location", {
  value: {
    origin,
    href: origin + "/soep-core/statistics/"
  },
  writable: true,
});

global.fetch = jest.fn(() => {
  return Promise.resolve({json: () => Promise.resolve({"tu": topicLeafsApiResponse["tu"]}), ok: true});
}) as jest.Mock;

global.document = Object.create(document);

global.document.body.innerHTML =
  "<html lang='en'>" +
  "<head> <meta name='study' content='soep-core'> </head>" +
  "<button id='language-switch' data-current-language='en' type='button' class='btn btn-outline-dark'></button>" +
  "</html>";

const expected = document.createElement("ul")

//TODO: Refactor and implement usage; Mind that this should only be used if variables.length > 10

expected.innerHTML = "<li>" +
  "<h4 data-de='Zeitverwendung' data-en='time use'>time use</h4>" +
  "</li>" +
  "<li><a data-en='hours of sleep, normal workday' data-de='' href='http://localhost/soep-core/statistics/numerical/?variable=a96ec9fb-eeb6-517c-9c5a-51776c58a5f5'>hours of sleep, normal workday</a></li>" +
  "<li>" +
  "<h4 data-de='Freizeit' data-en='leisure time'>leisure time</h4>" +
  "</li>" +
  "<li><a data-en='Frequency going to church, attending religious events' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=35c7bced-8bbc-5760-9159-5863cc42287e'>Frequency going to church, attending religious events</a></li>" +
  "<li><a data-en='Visit Sport Events' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=4a232a90-4cb8-5713-a91c-9c38e4752b5b'>Visit Sport Events</a></li>" +
  "<li><a data-en='Visit Family, Relatives' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=5e1885da-6dee-5d5f-b93b-721b4ae7e3fa'>Visit Family, Relatives</a></li>" +
  "<li><a data-en='Frequency visiting the cinema, pop or jazz concerts, dance events / discos' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=672e6557-45ad-5d53-a332-179f120479f3'>Frequency visiting the cinema, pop or jazz concerts, dance events / discos</a></li>" +
  "<li><a data-en='Watch Television, Video' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=687e84cc-5b72-5e2d-8382-10f85772b08c'>Watch Television, Video</a></li>" +
  "<li><a data-en='Visit Neighbors, Friends' data-de='' href='http://localhost/soep-core/statistics/categorical/?variable=837ed65a-0df5-5b97-988c-d5519729e75d'>Visit Neighbors, Friends</a></li>"



describe("Test function to set up child topics display", () => {
  test("TODO: Set up proper test", async () => {
    const result = document.createElement("ul")
    await setUpSubTopics(variableApiResponse, "tu", result);
    expect(result).toEqual(expected);

  });
});

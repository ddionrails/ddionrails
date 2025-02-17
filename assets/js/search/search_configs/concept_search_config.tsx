/* eslint-disable require-jsdoc */

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {LanguageCode} from "../language_state";
import {studyFacet} from "../search_components/facets";

function sorting(): JSX.Element {
  return <></>;
}

function facetFactory(language: LanguageCode): JSX.Element {
  return <>{studyFacet(language)}</>;
}
const facets = new Map();
facets.set("en", () => {
  return facetFactory("en");
});
facets.set("de", () => {
  return facetFactory("de");
});

const connector = new ElasticsearchAPIConnector({
  host: "/elastic",
  index: "concepts",
});

function config(language: LanguageCode) {
  let disjunctiveFacets = ["study_name"];
  let facets: any = {
    study_name: {type: "value"},
  };

  if (language === "de") {
    disjunctiveFacets = ["study_name_de"];
    facets = {
      study_name_de: {type: "value"},
    };
  }
  return {
    searchQuery: {
      search_fields: {
        name: {
          weight: 3,
        },
        label: {},
        label_de: {},
      },
      result_fields: {
        name: {
          snippet: {},
        },
        label: {
          snippet: {
            size: 200,
            fallback: true,
          },
        },
        label_de: {
          snippet: {
            size: 200,
            fallback: true,
          },
        },
        study: {
          snippet: {
            fallback: true,
          },
        },
      },
      disjunctiveFacets,
      facets,
    },
    autocompleteQuery: {
      results: {
        resultsPerPage: 10,
        search_fields: {
          name: {
            weight: 3,
          },
          label: {
            weight: 1,
          },
        },
        result_fields: {
          name: {
            snippet: {
              size: 100,
              fallback: true,
            },
          },
          label: {
            snippet: {
              size: 100,
              fallback: true,
            },
          },
        },
      },
    },
    apiConnector: connector,
    alwaysSearchOnInitialLoad: true,
  };
}

export {config as conceptConfig};
export {facets as conceptFacets};
export {sorting as conceptSorting};

/* eslint-disable require-jsdoc */

import {Facet} from "@elastic/react-search-ui";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";
import {LanguageCode} from "../language_state";

function sorting(): JSX.Element {
  return <></>;
}

function facetFactory(language: LanguageCode): JSX.Element {
  if (language === "de") {
    return (
      <Facet
        key={"1"}
        field={"study_name_de"}
        label={"Studie"}
        view={SortedMultiCheckboxFacet}
      />
    );
  }
  return (
    <Facet
      key={"1"}
      field={"study_name"}
      label={"Study"}
      view={SortedMultiCheckboxFacet}
    />
  );
}
const facets = new Map();
facets.set("en", () => {
  return facetFactory("en");
});
facets.set("de", () => {
  return facetFactory("de");
});

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
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

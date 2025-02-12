import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {Sorting} from "@elastic/react-search-ui";
import {LanguageCode} from "../language_state";
import {facetConfig, unlabeledFacet, studyFacet} from "../search_components/facets";
import {facetFactoryMapper} from "../factory_mappers";

/**
 *
 * @return {Element}
 */
function sorting() {
  return (
    <Sorting
      label={"Sort by"}
      sortOptions={[
        {
          name: "Relevance",
          value: [],
        },
        {
          name: "Period (ascending)",
          value: [
            {
              field: "year",
              direction: {order: "asc"},
            },
          ],
        },
        {
          name: "Period (descending)",
          value: [
            {
              field: "year",
              direction: {order: "desc"},
            },
          ],
        },
      ]}
    />
  );
}

/**
 *
 * @return { Element }
 */
function facetFactory(language: LanguageCode) {
  return (
    <>
      {studyFacet(language)}
      {unlabeledFacet(language, "year", ["Year", "Jahr"], "2")}
      {unlabeledFacet(language, "type", ["Typ", "Typ"], "3")}
    </>
  );
}

const facets = facetFactoryMapper(facetFactory);

const connector = new ElasticsearchAPIConnector({
  host: "/elastic",
  index: "publications",
});

// eslint-disable-next-line require-jsdoc
function config(language: LanguageCode) {
  return {
    searchQuery: {
      search_fields: {
        title: {weight: 3},
        abstract: {weight: 0.7},
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
        title: {
          snippet: {
            size: 100,
            fallback: true,
          },
        },
        author: {
          snippet: {
            size: 100,
            fallback: true,
          },
        },
        year: {
          snippet: {
            size: 100,
            fallback: true,
          },
        },
        abstract: {
          snippet: {
            size: 50,
            fallback: true,
          },
        },
      },
      disjunctiveFacets: ["year", "type", "study_name"],
      facets: {
        "year": {type: "value"},
        "type": {type: "value"},
        "study_name": {type: "value"},
      },

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
          title: {
            snippet: {
              size: 100,
              fallback: true,
            },
          },
          author: {
            snippet: {
              size: 100,
              fallback: true,
            },
          },
          year: {
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

export {config as publicationConfig};
export {facets as publicationFacets};
export {sorting as publicationSorting};

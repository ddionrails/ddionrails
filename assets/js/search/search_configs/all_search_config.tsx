import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {getLanguageState, LanguageCode} from "../language_state";
import {facetConfig, studyFacet} from "../search_components/facets";
import { facetFactoryMapper } from "../factory_mappers";

/**
 *
 * @return {Element}
 */
function sorting() {
  return <></>;
}

/**
 *
 * @return { Element }
 */
function facetFactory(language: LanguageCode): JSX.Element {
  return studyFacet(language);
}

const facets = facetFactoryMapper(facetFactory);


const connector = new ElasticsearchAPIConnector({
  host: "/elastic",
  index: "*",
});

// eslint-disable-next-line require-jsdoc
function config(language: LanguageCode) {
  const [disjunctiveFacets, facets] = facetConfig(language);
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
        instrument: {
          snippet: {},
        },
        dataset: {
          snippet: {},
        },
        period: {
          snippet: {},
        },
	title: {
	  snippet: {},
	},
	author: {
	  snippet: {},
	},
	abstract: {
	  snippet: {},
	},
	year: {
	  snippet: {},
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

export {config as allConfig};
export {facets as allFacets};
export {sorting as allSorting};

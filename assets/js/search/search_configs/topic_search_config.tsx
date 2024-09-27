/* eslint-disable require-jsdoc */

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {facetConfig, studyFacet} from "../search_components/facets";
import {LanguageCode} from "../language_state";
import {facetFactoryMapper} from "../factory_mappers";

function sorting(): JSX.Element {
  return <></>;
}

function facetFactory(language: LanguageCode): JSX.Element {
  return (
    <>{studyFacet(language)}</>
  );
}

const facets = facetFactoryMapper(facetFactory);

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "topics",
});

function config(language: LanguageCode) {
  const [disjunctiveFacets, facets] = facetConfig(language, [
    "study",
  ]);
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

export {config as topicConfig};
export {facets as topicFacets};
export {sorting as topicSorting};

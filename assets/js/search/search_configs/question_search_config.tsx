/* eslint-disable require-jsdoc */
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {facetConfig, genericFacet, studyFacet} from "../search_components/facets";
import {LanguageCode} from "../language_state";
import {facetFactoryMapper} from "../factory_mappers";
import {sortBy} from "./sort_by";

const sorting = sortBy;

function facetFactory(language: LanguageCode): JSX.Element {
  return (
    <>
      {studyFacet(language)}
      {genericFacet(language, "analysis_unit", ["Analysis Unit", "Analyseeinheit"], "2")}
      {genericFacet(language, "period", ["Period", "Zeitraum"], "3")}
    </>
  );
}

const facets = facetFactoryMapper(facetFactory);

const connector = new ElasticsearchAPIConnector({
  host: "/elastic",
  index: "questions",
});

function config(language: languageCode) {
  const [disjunctiveFacets, facets] = facetConfig(language, [
    "study",
    "analysis_unit",
    "period",
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
          raw: {},
          snippet: {
            size: 500,
            fallback: true,
          },
        },
        label_de: {
          raw: {},
          snippet: {
            size: 500,
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
        period: {
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

export {config as questionConfig};
export {facets as questionFacets};
export {sorting as questionSorting};

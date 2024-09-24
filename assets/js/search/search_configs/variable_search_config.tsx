import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {facetConfig, genericFacet, studyFacet} from "../search_components/facets";
import { facetFactoryMapper } from "../factory_mappers";
import { LanguageCode } from "../language_state";
import { sortBy } from "./sort_by";


const sorting = sortBy;

/**
 *
 * @return { Element }
 */
function facetFactory(language: LanguageCode) {
  return (
    <>
      {studyFacet(language)}
      {genericFacet(language, "analysis_unit", ["Analysis Unit", "Analyseeinheit"], "2")}
      {genericFacet(language, "period", ["Period", "Zeitraum"], "3")}
      {genericFacet(
        language,
        "conceptual_dataset",
        ["Conceptual Dataset", "Konzeptioneller Datensatz"],
        "4"
      )}
    </>
  );
}
const facets = facetFactoryMapper(facetFactory);

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "variables",
});

// eslint-disable-next-line require-jsdoc
function config(language: LanguageCode) {
  const [disjunctiveFacets, facets] = facetConfig(language, [
    "study",
    "analysis_unit",
    "period",
    "conceptual_dataset",
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
        dataset: {
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

export {config as variableConfig};
export {facets as variableFacets};
export {sorting as variableSorting};

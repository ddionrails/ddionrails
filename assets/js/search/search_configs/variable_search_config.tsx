import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {Facet, Sorting} from "@elastic/react-search-ui";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";
import {getLanguageState} from "../language_state";
import {facetConfig, genericFacet, studyFacet} from "../search_components/facets";

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
              field: "period.label",
              direction: {order: "asc"},
            },
          ],
        },
        {
          name: "Period (descending)",
          value: [
            {
              field: "period.label",
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
function facets() {
  const language = getLanguageState();
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

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "variables",
});

const config = () => {
  const language = getLanguageState();
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
};

export {config as variableConfig};
export {facets as variableFacets};
export {sorting as variableSorting};

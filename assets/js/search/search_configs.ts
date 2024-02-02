import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "variables",
});

const minimalSearchFields = {
  name: {
    weight: 3,
  },
  label: {},
  label_de: {},
};

const variableResultFields = {
  name: {
    snippet: {},
  },
  label: {
    snippet: {},
  },
  study: {
    snippet: {},
  },
  dataset: {
    snippet: {},
  },
  period: {
    snippet: {},
  },
};

const variableFacetConfig = {
  disjunctiveFacets: ["analysis_unit.label", "period.label"],
  facets: {
    "analysis_unit.label": {type: "value"},
    "period.label": {type: "value"},
  },
};


const variableSearchConfig = {
  searchQuery: {
    search_fields: minimalSearchFields,
    result_fields: variableResultFields,
    disjunctiveFacets: variableFacetConfig["disjunctiveFacets"],
    facets: variableFacetConfig["facets"],
  },
  autocompleteQuery: {
    results: {
      resultsPerPage: 5,
      search_fields: {
        label: {
          weight: 3,
        },
      },
      result_fields: {
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


/**
 * 
 * @returns 
 */
export function VariableSearchConfig() {
  return (variableSearchConfig);
}

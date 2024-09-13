
import {Facet, Sorting} from "@elastic/react-search-ui";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet_view";

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
      ]}
    />
  );
}

/**
 *
 * @return { Element }
 */
function facets() {
  return (
    <Facet
      key={"1"}
      field={"study_name"}
      label={"Study"}
      view={SortedMultiCheckboxFacet}
    />
  );
}

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "*",
});

const config = {
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
    },
    disjunctiveFacets: ["study_name"],
    facets: {
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
      },
    },
  },
  apiConnector: connector,
  alwaysSearchOnInitialLoad: true,
};

export {config as allConfig};
export {facets as allFacets};
export {sorting as allSorting};

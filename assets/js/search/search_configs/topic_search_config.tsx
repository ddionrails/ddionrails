/* eslint-disable require-jsdoc */

import {Facet} from "@elastic/react-search-ui";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";

function sorting(): JSX.Element {
  return (
    <></>
  );
}

function facets(): JSX.Element {
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
  index: "topics",
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

export {config as topicConfig};
export {facets as topicFacets};
export {sorting as topicSorting};

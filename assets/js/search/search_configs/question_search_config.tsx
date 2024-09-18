/* eslint-disable require-jsdoc */
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {Facet, Sorting} from "@elastic/react-search-ui";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";

function sorting(): JSX.Element {
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

function facets(): JSX.Element {
  return (
    <>
      <Facet
        key={"3"}
        field={"study_name"}
        label={"Study"}
        view={SortedMultiCheckboxFacet}
      />
      <Facet
        key={"1"}
        field={"analysis_unit.label"}
        label={"analysis unit"}
        view={SortedMultiCheckboxFacet}
      />
      <Facet
        key={"2"}
        field={"period.label"}
        label={"period"}
        view={SortedMultiCheckboxFacet}
      />
    </>
  );
}

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "questions",
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
      period: {
        snippet: {},
      },
    },
    disjunctiveFacets: ["analysis_unit.label", "period.label", "study_name"],
    facets: {
      "analysis_unit.label": {type: "value"},
      "period.label": {type: "value"},
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

export {config as questionConfig};
export {facets as questionFacets};
export {sorting as questionSorting};

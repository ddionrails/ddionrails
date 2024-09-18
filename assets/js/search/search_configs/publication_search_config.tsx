import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {Facet, Sorting} from "@elastic/react-search-ui";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";

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
        field={"year"}
        label={"Year"}
        view={SortedMultiCheckboxFacet}
      />
      <Facet
        key={"2"}
        field={"type"}
        label={"Type"}
        view={SortedMultiCheckboxFacet}
      />
    </>
  );
}

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "publications",
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

export {config as publicationConfig};
export {facets as publicationFacets};
export {sorting as publicationSorting};

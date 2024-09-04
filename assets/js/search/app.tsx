import React from "react";

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

import {
  ErrorBoundary,
  Facet,
  SearchBox,
  SearchProvider,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch,
} from "@elastic/react-search-ui";
import {Layout} from "@elastic/react-search-ui-views";

import {VariableResultView} from "./view_customisations/variable_result_view";
import SortedMultiCheckboxFacet from "./view_customisations/sorted_facet_view";
import Autocomplete from "./view_customisations/autocomplete_view";

const connector = new ElasticsearchAPIConnector({
  host: "/elastic/",
  index: "variables",
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
    },
    disjunctiveFacets: [
      "analysis_unit.label",
      "period.label",
      "study_name",
      "conceptual_dataset.label",
    ],
    facets: {
      "analysis_unit.label": {type: "value"},
      "period.label": {type: "value"},
      "study_name": {type: "value"},
      "conceptual_dataset.label": {type: "value"},
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

/**
 *
 * @returns
 */
export default function App() {
  return (
    <SearchProvider config={config}>
      <WithSearch
        mapContextToProps={({wasSearched}: {wasSearched: boolean}) => ({
          wasSearched,
        })}
      >
        {({wasSearched}: {wasSearched: boolean}) => {
          return (
            <div className="App">
              <ErrorBoundary>
                <Layout
                  header={
                    <SearchBox
                      autocompleteMinimumCharacters={3}
                      autocompleteResults={{
                        linkTarget: "_blank",
                        sectionTitle: "Results",
                        urlField: "",
                        titleField: "name",
                        shouldTrackClickThrough: false,
                      }}
                      autocompleteSuggestions={true}
                      debounceLength={0}
                      autocompleteView={Autocomplete}
                    />
                  }
                  sideContent={
                    <div>
                      {wasSearched && (
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
                      )}
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
                      <Facet
                        key={"4"}
                        field={"conceptual_dataset.label"}
                        label={"Conceptual Dataset"}
                        view={SortedMultiCheckboxFacet}
                      />
                    </div>
                  }
                  bodyContent={
                    <Results
                      resultView={VariableResultView}
                      titleField="name"
                      shouldTrackClickThrough={false}
                    />
                  }
                  bodyHeader={
                    <React.Fragment>
                      {wasSearched && <PagingInfo />}
                      {wasSearched && <ResultsPerPage />}
                    </React.Fragment>
                  }
                  bodyFooter={<Paging />}
                />
              </ErrorBoundary>
            </div>
          );
        }}
      </WithSearch>
    </SearchProvider>
  );
}

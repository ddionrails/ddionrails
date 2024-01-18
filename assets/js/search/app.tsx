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
import SortedMultiCheckboxFacet from "./view_customisations/SortedFacet_view";

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
    },
    disjunctiveFacets: ["analysis_unit.label", "period.label"],
    facets: {
      "analysis_unit.label": {type: "value"},
      "period.label": {type: "value"},
    },
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
                        shouldTrackClickThrough: true,
                      }}
                      autocompleteSuggestions={true}
                      debounceLength={0}
                    />
                  }
                  sideContent={
                    <div>
                      <Sorting
                        label={"Sort by"}
                        sortOptions={[
                          {name: "Name", value: "name.raw", direction: "asc"},
                          {name: "Label", value: "label.raw", direction: "asc"},
                        ]}
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

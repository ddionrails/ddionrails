import React from "react";

import {Route, NavLink, BrowserRouter, Routes} from "react-router-dom";

import {
  ErrorBoundary,
  SearchBox,
  SearchProvider,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  WithSearch,
} from "@elastic/react-search-ui";
import {Layout} from "@elastic/react-search-ui-views";

// import {VariableResultView} from "./view_customisations/variable_result_view";
import {QuestionResultView} from "./view_customisations/question_result_view";
import {VariableResultView} from "./view_customisations/variable_result_view";
import Autocomplete from "./view_customisations/autocomplete_view";
import {
  questionConfig,
  questionSorting,
  questionFacets,
} from "./search_variants/question_search";

import {
  variableConfig,
  variableSorting,
  variableFacets,
} from "./search_variants/variable_search";

/**
 *
 * @param config
 * @param Sorting
 * @param Facets
 * @returns
 */
function searchRouter(config: any, sorting: any, facets: any, resultView: any) {
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
                      {wasSearched && sorting()}
                      {facets()}
                    </div>
                  }
                  bodyContent={
                    <Results
                      resultView={resultView}
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

/**
 *
 */
function Questions() {
  return searchRouter(
    questionConfig,
    questionSorting,
    questionFacets,
    QuestionResultView
  );
}

/**
 *
 */
function Variables() {
  return searchRouter(
    variableConfig,
    variableSorting,
    variableFacets,
    VariableResultView
  );
}

/**
 *
 * @returns
 */
export default function App() {
  return (
    <>
      <BrowserRouter basename="/search">
        <NavLink
          to="/variables"
          className={({isActive, isPending}) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          Variables
        </NavLink>
        <NavLink
          to="/questions"
          className={({isActive, isPending}) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          Questions
        </NavLink>
        <Routes>
          <Route path="/" element={<Questions />} />
          <Route path="/all" element={<Questions />} />
          <Route path="/variables" element={<Variables />} />
          <Route path="/questions" element={<Questions />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

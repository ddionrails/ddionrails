import React from "react";
import {BrowserRouter, Route, Routes, useNavigate} from "react-router-dom";

import {
  ErrorBoundary,
  Paging,
  PagingInfo,
  Results,
  ResultsPerPage,
  SearchBox,
  SearchProvider,
  WithSearch,
} from "@elastic/react-search-ui";
import {Layout} from "@elastic/react-search-ui-views";
import {SearchDriverOptions} from "@elastic/search-ui";

import {conceptResult} from "./result_customisations/concept_result";

import {
  conceptConfig,
  conceptFacets,
  conceptSorting,
} from "./search_configs/concept_search_config";

import {AllResult} from "./result_customisations/all_result";
import {allConfig, allFacets, allSorting} from "./search_configs/all_search_config";

import Autocomplete from "./search_components/autocomplete";
import {
  questionConfig,
  questionFacets,
  questionSorting,
} from "./search_configs/question_search_config";
import {
  variableConfig,
  variableFacets,
  variableSorting,
} from "./search_configs/variable_search_config";
// import {variableResult} from "./view_customisations/variable_result_view";
import {questionResult} from "./result_customisations/question_result";
import {variableResult} from "./result_customisations/variable_result";

export const LinkWithQuery = ({children, to, ...props}: any) => {
  const navigate = useNavigate();

  const handleNavigate = (path: string) => {
    const queryParams = new URLSearchParams(window.location.search).toString();
    navigate(`${path}?${queryParams.toString()}`);
  };

  return (
    <button
      to=""
      {...props}
      onClick={() => {
        handleNavigate(to);
      }}
    >
      {children}
    </button>
  );
};

/**
 *
 * @param config
 * @param Sorting
 * @param Facets
 * @returns
 */
function searchRouter(
  config: SearchDriverOptions,
  sorting: any,
  facets: any,
  resultView: any
) {
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

/** */
function All() {
  return searchRouter(allConfig, allSorting, allFacets, AllResult);
}

/**
 *
 */
function Concepts() {
  return searchRouter(conceptConfig, conceptSorting, conceptFacets, conceptResult);
}

/**
 *
 */
function Questions() {
  return searchRouter(questionConfig, questionSorting, questionFacets, questionResult);
}

/**
 *
 */
function Variables() {
  return searchRouter(variableConfig, variableSorting, variableFacets, variableResult);
}

/**
 *
 * @returns
 */
function App() {
  return (
    <>
      <BrowserRouter basename="/search">
        <LinkWithQuery
          to="/all"
          className={({isActive, isPending}: any) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          All
        </LinkWithQuery>
        <LinkWithQuery
          to="/variables"
          className={({isActive, isPending}: any) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          Variables
        </LinkWithQuery>
        <LinkWithQuery
          to="/questions"
          className={({isActive, isPending}: any) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          Questions
        </LinkWithQuery>
        <LinkWithQuery
          to="/concepts"
          className={({isActive, isPending}: any) =>
            isPending ? "pending" : isActive ? "active" : ""
          }
        >
          Concepts
        </LinkWithQuery>
        <Routes>
          <Route path="/" element={<All />} />
          <Route path="/all" element={<All />} />
          <Route path="/variables" element={<Variables />} />
          <Route path="/questions" element={<Questions />} />
          <Route path="/concepts" element={<Concepts />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;

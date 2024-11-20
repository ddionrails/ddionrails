import React from "react";
import { BrowserRouter, Route, Routes, useNavigate } from "react-router-dom";

import { getLanguageState, LanguageCode } from "./language_state";

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
import { Layout } from "@elastic/react-search-ui-views";
import { SearchDriverOptions } from "@elastic/search-ui";

import { conceptResult } from "./result_customizations/concept_result";

import {
  conceptConfig,
  conceptFacets,
  conceptSorting,
} from "./search_configs/concept_search_config";

import { topicResult } from "./result_customizations/topic_result";

import {
  topicConfig,
  topicFacets,
  topicSorting,
} from "./search_configs/topic_search_config";

import { AllResult } from "./result_customizations/all_result";
import {
  allConfig,
  allFacets,
  allSorting,
} from "./search_configs/all_search_config";

import Autocomplete from "./search_components/autocomplete";

import { publicationResult } from "./result_customizations/publications_result";
import {
  publicationConfig,
  publicationFacets,
  publicationSorting,
} from "./search_configs/publication_search_config";

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
import { questionResult } from "./result_customizations/question_result";
import { variableResult } from "./result_customizations/variable_result";

import { resultIconMap } from "./search_components/result_header";

function filterQueryParams(queryParams: URLSearchParams): URLSearchParams {
  const filteredParams = new URLSearchParams();
  for (const paramGroup of queryParams.entries()) {
    if (paramGroup[0] === "size") {
      filteredParams.append(paramGroup[0], paramGroup[1]);
    }
  }

  return filteredParams;
}

export const LinkWithQuery = ({ children, to, ...props }: any) => {
  const navigate = useNavigate();

  const handleNavigate = (path: string) => {
    const queryParams = filterQueryParams(
      new URLSearchParams(window.location.search),
    );
    navigate(`${path}?${queryParams.toString()}`);
  };

  let icon: any = (): any => null;
  const iconType = to.split("/").pop().slice(0, -1);
  if (resultIconMap.has(iconType)) {
    icon = resultIconMap.get(iconType);
  }

  if (document.location.toString().includes(to)) {
    return (
      <button {...props} className="active-search">
        {icon()} {children}
      </button>
    );
  }
  return (
    <button
      {...props}
      className=""
      onClick={() => {
        handleNavigate(to);
      }}
    >
      {icon()} {children}
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
  resultView: any,
  language: LanguageCode = "en",
) {
  let placeholder = "Search";
  if (language === "de") {
    placeholder = "Suche";
  }
  return (
    <SearchProvider config={config}>
      <WithSearch
        mapContextToProps={({ wasSearched }: { wasSearched: boolean }) => ({
          wasSearched,
        })}
      >
        {({ wasSearched }: { wasSearched: boolean }) => {
          return (
            <div className="App">
              <ErrorBoundary>
                <Layout
                  header={
                    <SearchBox
                      autocompleteMinimumCharacters={3}
                      inputProps={{ placeholder }}
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
function All({ language }: { language: LanguageCode }) {
  return searchRouter(
    allConfig(language),
    allSorting,
    allFacets.get(language),
    AllResult.get(language),
    language,
  );
}

/**
 *
 */
function Concepts({ language }: { language: LanguageCode }) {
  return searchRouter(
    conceptConfig(language),
    conceptSorting,
    conceptFacets.get(language),
    conceptResult.get(language),
    language,
  );
}

/**
 *
 */
function Topics({ language }: { language: LanguageCode }) {
  return searchRouter(
    topicConfig(language),
    topicSorting,
    topicFacets.get(language),
    topicResult.get(language),
    language,
  );
}

/**
 *
 */
function Publications({ language }: { language: LanguageCode }) {
  return searchRouter(
    publicationConfig(language),
    publicationSorting,
    publicationFacets.get(language),
    publicationResult.get(language),
    language,
  );
}

/**
 *
 */
function Questions({ language }: { language: LanguageCode }) {
  return searchRouter(
    questionConfig(language),
    questionSorting.get(language),
    questionFacets.get(language),
    questionResult.get(language),
    language,
  );
}

/**
 *
 */
function Variables({ language }: { language: LanguageCode }) {
  return searchRouter(
    variableConfig(language),
    variableSorting.get(language),
    variableFacets.get(language),
    variableResult.get(language),
    language,
  );
}

// eslint-disable-next-line complexity, require-jsdoc
function App() {
  const language = getLanguageState();
  return (
    <>
      <BrowserRouter basename="/search">
        <div className="search-menu">
          <LinkWithQuery to="/all">
            {language === "de" ? "Alles durchsuchen" : "Search all"}
          </LinkWithQuery>
          <LinkWithQuery to="/variables">
            {language === "de" ? "Variablen" : "Variables"}
          </LinkWithQuery>
          <LinkWithQuery to="/questions">
            {language === "de" ? "Fragen" : "Questions"}
          </LinkWithQuery>
          <LinkWithQuery to="/concepts">
            {language === "de" ? "Konzepte" : "Concepts"}
          </LinkWithQuery>
          <LinkWithQuery to="/topics">
            {language === "de" ? "Themen" : "Topics"}
          </LinkWithQuery>
          <LinkWithQuery to="/publications">
            {language === "de" ? "Publikationen" : "Publications"}
          </LinkWithQuery>
        </div>
        <Routes>
          <Route path="/" element={<All language={language} />} />
          <Route path="/all" element={<All language={language} />} />
          <Route
            path="/variables"
            element={<Variables language={language} />}
          />
          <Route
            path="/questions"
            element={<Questions language={language} />}
          />
          <Route path="/concepts" element={<Concepts language={language} />} />
          <Route path="/topics" element={<Topics language={language} />} />
          <Route
            path="/publications"
            element={<Publications language={language} />}
          />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;

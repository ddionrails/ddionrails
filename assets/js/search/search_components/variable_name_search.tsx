import React, { useState } from "react";

const PAGE_START = 0;
const PAGE_SIZE = 20;

export function VariableNames({ language }: { language: string }) {
  const [results, setResults] = useState([<li key={1} />]);
  const [startResult, setStartResult] = useState(PAGE_START);
  return (
    <div>
      <SearchBox
        language={language}
        resultSetter={setResults}
        setStartResult={setStartResult}
      />
      <ContentBox
        language={language}
        results={results}
        startResult={startResult}
        setResult={setResults}
        setStartResult={setStartResult}
      />
    </div>
  );
}

function SearchBox({
  language,
  resultSetter,
  setStartResult,
}: {
  language: string;
  resultSetter: any;
  setStartResult: any;
}) {
  return (
    <div className="sui-layout-header">
      <div className="sui-search-box">
        <input
          className="sui-search-box__text-input"
          id="downshift-2-input"
          placeholder={language == "en" ? "Search" : "Suche"}
          onKeyDown={(event) => {
            setStartResult(PAGE_START);
            searchWithEnter(event, resultSetter, PAGE_START, language);
          }}
        ></input>
        <input
          data-transaction-name="search submit"
          type="submit"
          className="button sui-search-box__submit"
          value="Search"
          onClick={() => {
            setStartResult(PAGE_START);
            search(resultSetter, PAGE_START, language);
          }}
        />
      </div>
    </div>
  );
}

function ContentBox({
  language,
  results,
  startResult,
  setResult,
  setStartResult,
}: {
  language: string;
  results: any;
  startResult: number;
  setResult: any;
  setStartResult: any;
}) {
  return (
    <div className="sui-layout-main">
      <ul className="sui-results-container" id="results-container">
        {results}
      </ul>
      <div className="sui-layout-main-footer">
        <ul className="rc-pagination sui-paging">
          <li
            className={
              startResult === PAGE_START
                ? "rc-pagination-prev rc-pagination-disabled"
                : "rc-pagination-prev "
            }
            aria-disabled="true"
          >
            <button
              type="button"
              aria-label="prev page"
              className="rc-pagination-item-link"
              disabled={false}
              onClick={() => {
                if (startResult > PAGE_START) {
                  setStartResult(startResult - PAGE_SIZE);
                  search(setResult, startResult - PAGE_SIZE, language);
                }
              }}
            ></button>
          </li>
          <li
            title="1"
            className="rc-pagination-item rc-pagination-item-1 rc-pagination-item-active hidden"
          >
            <a rel="nofollow">1</a>
          </li>
          <li className="rc-pagination-next" aria-disabled="false">
            <button
              type="button"
              aria-label="next page"
              className="rc-pagination-item-link"
              onClick={() => {
                if (startResult + PAGE_SIZE <= 10000) {
                  setStartResult(startResult + PAGE_SIZE);
                  search(setResult, startResult + PAGE_SIZE, language);
                }
              }}
            ></button>
          </li>
          <li className="rc-pagination-options"></li>
        </ul>
      </div>
    </div>
  );
}

function searchWithEnter(
  event: React.KeyboardEvent<HTMLInputElement>,
  resultSetter: any,
  startResult: any,
  language: string,
) {
  if (event.key === "Enter") {
    search(resultSetter, startResult, language);
  }
}

function RenderResults(searchResults: any, language: string) {
  if (!searchResults?.hits) {
    return [<li key={0} />];
  }
  const output: Array<any> = [];
  const currentLabel = language === "en" ? "label" : "label_de";
  for (const item of searchResults?.hits?.hits) {
    const metadata = item._source;
    output.push(
      <li className="sui-result" key={metadata.id}>
        <div className="sui-result__header">
          <h3>
            <i className="fa fa-chart-bar"></i>
            <a href={"/variable/" + metadata.id}>
              {metadata.name}:{" "}
              <span data-en={metadata.label} data-de={metadata.label_de}>
                {metadata[currentLabel]}
              </span>
            </a>
          </h3>
        </div>
        <div className="sui-result__body">
          <p>
            Study: {metadata.study.label} | Dataset:{" "}
            <span
              data-en={metadata.dataset.label}
              data-de={metadata.dataset.label_de}
            >
              {metadata.dataset[currentLabel]}
            </span>{" "}
            | Period:
            <span
              data-en={metadata.period.label}
              data-de={metadata.period.label_de}
            >
              {metadata.period[currentLabel]}
            </span>
            
          </p>
        </div>
      </li>,
    );
  }

  return output;
}

async function search(resultSetter: any, startResult: any, language: string) {
  const inputElement = document.getElementById(
    "downshift-2-input",
  ) as HTMLInputElement;
  const inputText = inputElement.value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (inputText.trim() === "") {
    resultSetter(<></>);
    return;
  }
  const response = await fetch("/elastic/variables/_search", {
    method: "POST",
    body: JSON.stringify({
      from: startResult,
      size: PAGE_SIZE,
      sort: [{ name: "asc" }],
      query: {
        regexp: {
          name: {
            value: ".*" + inputText,
            flags: "ALL",
            case_insensitive: true,
            max_determinized_states: 10000,
          },
        },
      },
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8",
    },
  });
  response
    .json()
    .then((content: any) => resultSetter(RenderResults(content, language)));
}

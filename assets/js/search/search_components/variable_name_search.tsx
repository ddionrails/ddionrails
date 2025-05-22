import React, { useState } from "react";

export function VariableNames({ language }: { language: string }) {
  const [results, setResults] = useState([<li key={1}/>]);
  return (
    <div>
      <SearchBox language={language} resultSetter={setResults} />
      <ContentBox language={language} results={results} />
    </div>
  );
}

function SearchBox({
  language,
  resultSetter,
}: {
  language: string;
  resultSetter: any;
}) {
  return (
    <div className="sui-layout-header">
      <div className="sui-search-box">
        <input
          className="sui-search-box__text-input"
          id="downshift-2-input"
          placeholder={language == "en" ? "Search" : "Suche"}
          onKeyDown={(event) => {
            searchWithEnter(event, resultSetter);
          }}
        ></input>
        <input
          data-transaction-name="search submit"
          type="submit"
          className="button sui-search-box__submit"
          value="Search"
          onClick={() => {
            search(resultSetter);
          }}
        />
      </div>
    </div>
  );
}

function ContentBox({ language, results }: { language: string; results: any }) {
  return (
    <div className="sui-layout-main">
      <ul className="sui-results-container" id="results-container">
        { results }
      </ul>
      <div className="sui-layout-main-footer">
        <ul className="rc-pagination sui-paging hidden">
          <li
            className="rc-pagination-prev rc-pagination-disabled"
            aria-disabled="true"
          >
            <button
              type="button"
              aria-label="prev page"
              className="rc-pagination-item-link"
              disabled={false}
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
) {
  if (event.key === "Enter") {
    search(resultSetter);
  }
}

function RenderResults(searchResults: any) {
  const output: Array<any> = [];
  if (!searchResults?.hits) {
    return [<li key={0} />];
  }
  for (const item of searchResults?.hits?.hits) {
      const metadata = item._source;
      output.push(
        <li className="sui-result" key={metadata.id}>
          <div className="sui-result__header">
            <h3>
              <i className="fa fa-chart-bar"></i>
              <a href={"/variable/" + metadata.id}>
                {metadata.name}: {metadata.label}
              </a>
            </h3>
          </div>
          <div className="sui-result__body">
            <p>
              Study: {metadata.study.label} | Dataset: {metadata.dataset.label} | Period:
              {metadata.period.label}
            </p>
          </div>
        </li>,
      );
  }

  return output;
}

async function search(resultSetter: any) {
  const inputElement = document.getElementById(
    "downshift-2-input",
  ) as HTMLInputElement;
  const inputText = inputElement.value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (inputText.trim() === "") {
    return;
  }
  const response = await fetch("/elastic/variables/_search", {
    method: "POST",
    body: JSON.stringify({
      from: 0,
      size: 20,
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
  response.json().then((content: any) => resultSetter(RenderResults(content)));
}

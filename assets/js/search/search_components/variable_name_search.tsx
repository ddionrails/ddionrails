import React, { Dispatch, ReactNode, SetStateAction, useState } from "react";

const PAGE_START = 0;
const PAGE_SIZE = 20;
const ELASTIC_MAX_SIZE = 10000;

export function VariableNames({ language }: { language: string }) {
  const [results, setResults] = useState<Array<ReactNode>>([<li key={1} />]);
  const [startResult, setStartResult] = useState<number>(PAGE_START);
  const [endResult, setEndResult] = useState<number>(ELASTIC_MAX_SIZE);
  return (
    <div>
      <SearchBox
        language={language}
        setResult={setResults}
        setStartResult={setStartResult}
        setEndResult={setEndResult}
      />
      <ContentBox
        language={language}
        results={results}
        startResult={startResult}
        endResult={endResult}
        setResult={setResults}
        setStartResult={setStartResult}
        setEndResult={setEndResult}
      />
    </div>
  );
}

function TruncatedCheckbox({
  language,
  side,
  setResult,
  setStartResult,
  setEndResult,
}: {
  language: string;
  side: string;
  setResult: Dispatch<SetStateAction<Array<ReactNode>>>;
  setStartResult: Dispatch<SetStateAction<number>>;
  setEndResult: Dispatch<SetStateAction<number>>;
}) {
  const [checked, setChecked] = useState(true);
  const germanSide = side === "left" ? "linken" : "rechten";
  const englishLabel = `Extend search on the ${side} side`;
  const germanLabel = `Erweitere Suchwort auf der ${germanSide} Seite`;
  return (
    <div className="truncate-checkbox">
      <input
        id={"truncate-checkbox-" + side}
        type="checkbox"
        className="sui-multi-checkbox-facet__checkbox"
        checked={checked}
        onClick={() => {
          setChecked(!checked);
        }}
        onChange={() => {
          setStartResult(PAGE_START);
          search(setResult, setEndResult, PAGE_START, language);
        }}
      />
      <span
        className="sui-multi-checkbox-facet__input-text"
        data-en={englishLabel}
        date-de={germanLabel}
      >
        {language === "en" ? englishLabel : germanLabel}
      </span>
    </div>
  );
}

function SearchBox({
  language,
  setResult,
  setStartResult,
  setEndResult,
}: {
  language: string;
  setResult: any;
  setStartResult: any;
  setEndResult: Dispatch<SetStateAction<number>>;
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
            searchWithEnter(
              event,
              setResult,
              setEndResult,
              PAGE_START,
              language,
            );
          }}
        ></input>
        <input
          data-transaction-name="search submit"
          type="submit"
          className="button sui-search-box__submit"
          value="Search"
          onClick={() => {
            setStartResult(PAGE_START);
            search(setResult, setEndResult, PAGE_START, language);
          }}
        />
      </div>
      <div id="truncate-checkbox-container">
        <TruncatedCheckbox
          language={language}
          side="left"
          setResult={setResult}
          setStartResult={setStartResult}
          setEndResult={setEndResult}
        />
        <TruncatedCheckbox
          language={language}
          side="right"
          setResult={setResult}
          setStartResult={setStartResult}
          setEndResult={setEndResult}
        />
      </div>
    </div>
  );
}

function ContentBox({
  language,
  results,
  startResult,
  endResult,
  setResult,
  setStartResult,
  setEndResult,
}: {
  language: string;
  results: any;
  startResult: number;
  endResult: number;
  setResult: Dispatch<SetStateAction<Array<ReactNode>>>;
  setStartResult: Dispatch<SetStateAction<number>>;
  setEndResult: Dispatch<SetStateAction<number>>;
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
                  search(
                    setResult,
                    setEndResult,
                    startResult - PAGE_SIZE,
                    language,
                  );
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
          <li
            className={
              endResult - startResult > PAGE_SIZE
                ? "rc-pagination-next"
                : "rc-pagination-next rc-pagination-disabled"
            }
            aria-disabled="false"
          >
            <button
              type="button"
              aria-label="next page"
              className="rc-pagination-item-link"
              onClick={() => {
                if (endResult - (startResult + PAGE_SIZE) > 0) {
                  setStartResult(startResult + PAGE_SIZE);
                  search(
                    setResult,
                    setEndResult,
                    startResult + PAGE_SIZE,
                    language,
                  );
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
  setResult: Dispatch<SetStateAction<Array<ReactNode>>>,
  setEndResult: Dispatch<SetStateAction<number>>,
  startResult: number,
  language: string,
) {
  if (event.key === "Enter") {
    search(setResult, setEndResult, startResult, language);
  }
}

/**
 * Using string replace and split because 
 * its easier to implement than something that uses substring indices.
 * Not just using just replace to <em>searchTerm</em> to avoid
 * using dangerouslySetHTML with user input.
 */
function emphasize(name: string, searchTerm: string) {
  const emphasizedName = name.replaceAll(searchTerm, `|${searchTerm}|`);
  return emphasizedName
    .split("|")
    .map((term, index) =>
      term === searchTerm ? (
        <em key={index}>{term}</em>
      ) : (
        <span key={index}>{term}</span>
      ),
    );
}

function RenderResults(
  searchResults: any,
  language: string,
  searchTerm: string,
) {
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
              {emphasize(metadata.name, searchTerm)}:{" "}
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

async function search(
  setResult: Dispatch<SetStateAction<Array<ReactNode>>>,
  setEndResult: Dispatch<SetStateAction<number>>,
  startResult: number,
  language: string,
) {
  const inputElement = document.getElementById(
    "downshift-2-input",
  ) as HTMLInputElement;

  const truncate_left = (
    document.getElementById("truncate-checkbox-left") as HTMLInputElement
  ).checked;
  const truncate_right = (
    document.getElementById("truncate-checkbox-right") as HTMLInputElement
  ).checked;

  const inputText = inputElement.value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (inputText.trim() === "") {
    setResult([<></>]);
    return;
  }

  let searchString = inputText;
  if (truncate_left) {
    searchString = ".*" + searchString;
  }
  if (truncate_right) {
    searchString = searchString + ".*";
  }

  const response = await fetch("/elastic/variables/_search", {
    method: "POST",
    body: JSON.stringify({
      from: startResult,
      size: PAGE_SIZE,
      sort: [{ name_keyword: "asc" }],
      query: {
        regexp: {
          name: {
            value: searchString,
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
  response.json().then((content: any) => {
    setEndResult(content["hits"]["total"]["value"]);
    setResult(RenderResults(content, language, inputText));
  });
}

import {SearchResult} from "@elastic/search-ui";
import {resultIconMap} from "../search_components/result_header";
import {sep} from "./result_field_separator";

import {getLanguageState} from "../language_state";
import {resultFactoryMapper} from "../factory_mappers";
import {ReactElement} from "react";

// eslint-disable-next-line require-jsdoc
function setCursorCords(event: any) {
  document.body.style.setProperty("--x", String(event.pageX) + "px");
  document.body.style.setProperty(
    "--y",
    String(event.pageY - window.scrollY) + "px"
  );
}

function createTooltipContent(
  result: SearchResult,
  fieldsToInclude: Map<string, string>
): [ReactElement, string] {
  const snippetText = [];
  let tooltipClass = "no-tooltip";
  for (const [fieldName, fieldText] of fieldsToInclude.entries()) {
    const fieldValue = result[fieldName];

    if (fieldValue?.snippet) {
      tooltipClass = "raw-tooltip";
			snippetText.push(`${fieldText}:`);
			snippetText.push(fieldValue.snippet.join(" &hellip; "));
    }
  }
  let categoriesContainer = <></>;
  if (snippetText.length > 0) {
    tooltipClass = "raw-tooltip";
    categoriesContainer = (
      <span
        className="raw-tooltiptext"
        dangerouslySetInnerHTML={{
          __html: snippetText.join(" "),
        }}
      ></span>
    );
  }
  return [categoriesContainer, tooltipClass];
}

// TODO: Refactor
// eslint-disable-next-line require-jsdoc
function header(
  result: SearchResult,
  onClickLink: () => void,
  resultType: any,
  language: string = "en"
) {
  let labelName = "label";
  let otherLabelName = "label_de";
  let otherLanguageText = "Hit in german label: ";
  if (language == "de") {
    labelName = "label_de";
    otherLabelName = "label";
    otherLanguageText = "Treffer in englischem label: ";
  }
  let label = result[labelName].snippet;
  const otherLanguageSnippet = result[otherLabelName].snippet;
  let searchHitOtherLanguage = <></>;

  const fieldsInTooltip = new Map();
  if(language === "de"){
    fieldsInTooltip.set("categories.labels_de", "Treffer in Kategorie Wertelabeln");
  } else {
    fieldsInTooltip.set("categories.labels", "Match in category value labels");
	}

  const [categoriesContainer, tooltipClass] = createTooltipContent(result, fieldsInTooltip);

  if (
    otherLanguageSnippet instanceof Array &&
    otherLanguageSnippet[0].includes("<em>")
  ) {
    searchHitOtherLanguage = (
      <div
        className="other-search-hit-container"
        dangerouslySetInnerHTML={{
          __html: otherLanguageText + otherLanguageSnippet.join(""),
        }}
      ></div>
    );
  }
  if (!label) {
    label = result[labelName].raw;
  }
  return (
    <div className="header-subdivider">
      <h3>
        {resultIconMap.get(resultType)()}
        <a
          onMouseOver={setCursorCords}
          onClick={onClickLink}
          href={"/" + resultType + "/" + result._meta.id}
        >
          <span className="result-name">{result.name.raw}:</span>
          <span className={tooltipClass}>
            <span dangerouslySetInnerHTML={{__html: label}}></span>
            {categoriesContainer}
          </span>
        </a>
      </h3>
      {searchHitOtherLanguage}
    </div>
  );
}

/**
 * Render variable result body
 * @param result
 * @returns
 */
function variableBody(result: SearchResult) {
  const language = getLanguageState();
  if (language === "de") {
    return (
      <p>
        Studie: {result.study.raw.label_de}
        {sep()}Datensatz: {result.dataset.raw.name}
        {sep()}Zeitraum: {result.period.raw.label_de}
      </p>
    );
  }
  return (
    <p>
      Study: {result.study.raw.label}
      {sep()}Dataset: {result.dataset.raw.name}
      {sep()}Period: {result.period.raw.label}
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function variableResultFactory({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "variable", getLanguageState())}
      </div>
      <div className="sui-result__body">
        {variableBody(result)}
        <div className="sui-result__image">
          <img src={""} alt="" />
        </div>
        <div
          className="sui-result__details"
          dangerouslySetInnerHTML={{__html: result.description}}
        ></div>
      </div>
    </li>
  );
}

const variableResult = resultFactoryMapper(variableResultFactory);

export {variableResult};

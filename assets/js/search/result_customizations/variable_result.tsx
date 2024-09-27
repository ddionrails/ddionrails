import {SearchResult} from "@elastic/search-ui";
import {resultIconMap} from "../search_components/result_header";
import {sep} from "./result_field_separator";

import {getLanguageState} from "../language_state";
import {resultFactoryMapper} from "../factory_mappers";


// eslint-disable-next-line require-jsdoc
function setCursorCords(event: any) {
  console.log("x");
  console.log(event.pageX);
  console.log("y");
  console.log(event.pageY);
  document.body.style.setProperty("--x", String(event.pageX)+"px");
  document.body.style.setProperty("--y", String(event.pageY - window.scrollY)+"px");
}

// TODO: Refactor
// eslint-disable-next-line require-jsdoc
function header(result: SearchResult, onClickLink: () => void, resultType: any, language: string = "en") {
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


  const categories = result["categories.labels"];

  let categoriesContainer = <></>;
  let tooltipClass = "no-tooltip";
  if (typeof categories !== "undefined") {
    tooltipClass = "raw-tooltip";
    categories.snippet.push("");
    categoriesContainer = (
      <span
        className="raw-tooltiptext"
        dangerouslySetInnerHTML={{__html: categories.snippet.join(" &hellip; ")}}
      ></span>
    );
  }


  if (otherLanguageSnippet instanceof Array && otherLanguageSnippet[0].includes("<em>")) {
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
        <a onMouseOver={setCursorCords}
          onClick={onClickLink} href={"/" + resultType + "/" + result._meta.id}>
          [{result.name.raw}]
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
  console.log(JSON.stringify(result.categories.labels));
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
      <div className="sui-result__header">{header(result, onClickLink, "variable")}</div>
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

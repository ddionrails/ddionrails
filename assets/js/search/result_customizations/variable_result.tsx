import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import {sep} from "./result_field_separator";

import {getLanguageState} from "../language_state";

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
function variableResult({
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

export {variableResult};

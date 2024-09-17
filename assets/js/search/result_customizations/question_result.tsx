import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import {sep} from "./result_field_separator";

/**
 * Render variable result body
 * @param result
 * @returns
 */
function questionBody(result: SearchResult) {
  return (
    <p>
      Study: {result.study.raw.label}
      {sep()}Instrument: {result.instrument.raw.label}
      {sep()}Period: {result.period.raw.label}
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function questionResult({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">{header(result, onClickLink, "question")}</div>
      <div className="sui-result__body">
        {questionBody(result)}
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

export {questionResult};

import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import {sep} from "./result_field_separator";

import {LanguageCode} from "../language_state";
import {resultFactoryMapper} from "../factory_mappers";

/**
 * Render variable result body
 * @param result
 * @returns
 */
function questionBody(result: SearchResult, language: LanguageCode) {
  if (language === "de") {
    return (
      <p>
        Studie: {result.study.raw.name}
        {sep()}Instrument: {result.instrument.raw.label_de}
        {sep()}Zeitraum: {result.period.raw.label_de}
      </p>
    );
  }
  return (
    <p>
      Study: {result.study.raw.label}
      {sep()}Period: {result.period.raw.label}
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function questionResultFactory({
  result,
  onClickLink,
  language,
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "question", language)}
      </div>
      <div className="sui-result__body">
        {questionBody(result, language)}
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

const questionResult = resultFactoryMapper(questionResultFactory);

export {questionResult};

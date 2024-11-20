import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import {LanguageCode} from "../language_state";
import { resultFactoryMapper } from "../factory_mappers";

/**
 * Render variable result body
 * @param result
 * @returns
 */
function topicBody(result: SearchResult, language: LanguageCode) {
  if (language === "de") {
    return <p>Thema in Studie {result.study.raw.label}</p>;
  }
  return <p>Topic in study {result.study.raw.label}</p>;
}

/**
 *
 * @param param0
 * @returns
 */
function topicResultFactory({
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
        {header(result, onClickLink, "topic", language)}
      </div>
      <div className="sui-result__body">
        {topicBody(result, language)}
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

const topicResult = resultFactoryMapper(topicResultFactory);

export {topicResult};

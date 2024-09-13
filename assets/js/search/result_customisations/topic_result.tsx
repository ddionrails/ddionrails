import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";


/**
 * Render variable result body
 * @param result
 * @returns
 */
function topicBody(result: SearchResult) {
  return (
    <p>
          Topic in study {result.study_name}
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function topicResult({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "question")}
      </div>
      <div className="sui-result__body">
        {topicBody(result)}
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

export {topicResult};

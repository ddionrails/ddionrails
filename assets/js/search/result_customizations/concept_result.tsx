import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";


/**
 * Render variable result body
 * @param result
 * @returns
 */
function conceptBody(result: SearchResult) {
  return (
    <p>
          Concept in study {result.study_name}
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function conceptResult({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "concept")}
      </div>
      <div className="sui-result__body">
        {conceptBody(result)}
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

export {conceptResult};

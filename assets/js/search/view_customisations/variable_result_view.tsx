import {SearchResult} from "@elastic/search-ui";

/**
 * Render header for variable result
 * @param result
 * @returns
 */
function variableHeader(result: SearchResult, onClickLink: () => void) {
  return (
    <h3>
      <i className="fa fa-cog"></i>
      <a onClick={onClickLink} href={"/variable/" + result._meta.id}>
            [{result.name.raw}]{" "}
        <span
          dangerouslySetInnerHTML={{__html: result.label.snippet}}
        ></span>
      </a>
    </h3>

  );
}

/**
 * Render variable result body
 * @param result
 * @returns
 */
function variableBody(result: SearchResult) {
  return (
    <p>
          Study: {result.study.raw.name} | Dataset: {result.dataset.raw.name}
          | Period: {result.period.raw.label}
    </p>
  );
}

const mapDisplayFunctionsToIndex = (result: SearchResult) => {
  if (result._meta.rawHit._index === "variables") {
    return ({header: variableHeader, body: variableBody});
  }
  return (null);
};

/**
 *
 * @param param0
 * @returns
 */
export function VariableResultView({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  const displayFunctions = mapDisplayFunctionsToIndex(result);
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {displayFunctions.header(result, onClickLink)}
      </div>
      <div className="sui-result__body">
        {displayFunctions.body(result)}
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

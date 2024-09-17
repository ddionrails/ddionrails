import {SearchResult} from "@elastic/search-ui";


/**
 * Render header for variable result
 * @param result
 * @returns
 */
export function header(
  result: SearchResult,
  onClickLink: () => void
) {
  let label = result.title.snippet;
  if (!label) {
    label = result.title.raw;
  }
  return (
    <h3>
      {<i className="fa fa-newspaper"></i>}
      <a onClick={onClickLink} href={"/publication/" + result._meta.id}>
        <span dangerouslySetInnerHTML={{__html: label}}></span>
      </a>
    </h3>
  );
}

/**
 * Render publication result body
 * @param result
 * @returns
 */
function publicationBody(result: SearchResult) {
  return (
    <p>
        Publication by {result.author.raw} ({result.year.raw})
    </p>
  );
}


/**
 *
 * @param param0
 * @returns
 */
function publicationResult({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink)}
      </div>
      <div className="sui-result__body">
        {publicationBody(result)}
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

export {publicationResult};

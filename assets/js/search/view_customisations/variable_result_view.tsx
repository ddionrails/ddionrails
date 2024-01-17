import {SearchResult} from "@elastic/search-ui";

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
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        <h3>
          {/* Maintain onClickLink to correct track click throughs for analytics*/}
          <i className="fa fa-cog"></i>
          <a onClick={onClickLink} href={"/variable/" + result._meta.id}>
            {result.name.raw}
          </a>
        </h3>
      </div>
      <div className="sui-result__body">
        {/* use 'raw' values of fields to access values without snippets */}
        <p>
            Study: {result.study.raw.name} | Dataset: {result.dataset.raw.name}
        </p>
        <div className="sui-result__image">
          <img src={""} alt="" />
        </div>
        {/* Use the 'snippet' property of fields with dangerouslySetInnerHtml to render snippets */}
        <div
          className="sui-result__details"
          dangerouslySetInnerHTML={{__html: result.description}}
        ></div>
      </div>
    </li>);
};

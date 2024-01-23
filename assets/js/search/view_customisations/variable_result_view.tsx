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
          <i className="fa fa-cog"></i>
          <a onClick={onClickLink} href={"/variable/" + result._meta.id}>
            [{result.name.raw}]{" "}
            <span
              dangerouslySetInnerHTML={{__html: result.label.snippet}}
            ></span>
          </a>
        </h3>
      </div>
      <div className="sui-result__body">
        <p>
          Period: {result.period.raw.label} | Study: {result.study.raw.name} |
          Dataset: {result.dataset.raw.name}
        </p>
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

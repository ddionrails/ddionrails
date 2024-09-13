import {SearchResult} from "@elastic/search-ui";

type result = "question" | "variable" | "concept" | "topic" | "publication";

const resultIconMap: Map<result, Function> = new Map();
resultIconMap.set("question", () => {
  return <i className="fa fa-tasks"></i>;
});
resultIconMap.set("concept", () => {
  return <i className="fa fa-cog"></i>;
});
resultIconMap.set("topic", () => {
  return <i className="fa fa-cogs"></i>;
});
resultIconMap.set("variable", () => {
  return <i className="fa fa-chart-bar"></i>;
});
resultIconMap.set("publication", () => {
  return <i className="fa fa-newspaper"></i>;
});

/**
 * Render header for variable result
 * @param result
 * @returns
 */
export function header(
  result: SearchResult,
  onClickLink: () => void,
  resultType: result
) {
  let label = result.label.snippet;
  if (!label) {
    label = result.label.raw;
  }
  return (
    <h3>
      {resultIconMap.get(resultType)()}
      <a onClick={onClickLink} href={"/" + resultType + "/" + result._meta.id}>
        [{result.name.raw}] <span dangerouslySetInnerHTML={{__html: label}}></span>
      </a>
    </h3>
  );
}

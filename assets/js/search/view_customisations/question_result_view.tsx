
import {SearchResult} from "@elastic/search-ui";

type result = "question" | "variable" | "concept" | "topic" | "publication"

const resultIconMap: Map<result, Function> = new Map();
resultIconMap.set("question", ()=>{
  return (<i className="fa fa-tasks"></i>);
});
resultIconMap.set("concept", ()=>{
  return (<i className="fa fa-cog"></i>);
});
resultIconMap.set("topic", ()=>{
  return (<i className="fa fa-cogs"></i>);
});
resultIconMap.set("variable", ()=>{
  return (<i className="fa fa-chart-bar"></i>);
});
resultIconMap.set("publication", ()=>{
  return (<i className="fa fa-newspaper"></i>);
});


/**
 * Render header for variable result
 * @param result
 * @returns
 */
function resultHeader(result: SearchResult, onClickLink: () => void, resultType: result) {
  let label = result.label.snippet;
  if (!label) {
    label = result.label.raw;
  }
  return (
    <h3>
      {resultIconMap.get(resultType)()}
      <a onClick={onClickLink} href={"/" + resultType + "/" + result._meta.id}>
            [{result.name.raw}]{" "}
        <span
          dangerouslySetInnerHTML={{__html: label}}
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
function questionBody(result: SearchResult) {
  return (
    <p>
          Study: {result.study.raw.label} | Instrument: {result.instrument.raw.label}
          | Period: {result.period.raw.label}
    </p>
  );
}

const mapDisplayFunctionsToIndex = (resultType: result) => {
  if (resultType === "question") {
    return ({header: resultHeader, body: questionBody});
  }
  return (null);
};

/**
 *
 * @param param0
 * @returns
 */
export function QuestionResultView({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  const displayFunctions = mapDisplayFunctionsToIndex("question");
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {displayFunctions.header(result, onClickLink, "question")}
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

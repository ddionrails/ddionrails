import {SearchResult} from "@elastic/search-ui";
import {getLanguageState} from "../language_state";

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
function header(result: SearchResult, onClickLink: () => void, resultType: result, language: string = "en") {
  let labelName = "label";
  let otherLabelName = "label_de";
  let otherLanguageText = "Hit in german label: ";
  if (language == "de") {
    labelName = "label_de";
    otherLabelName = "label";
    otherLanguageText = "Treffer in englischem label: ";
  }
  let label = result[labelName].snippet;
  const otherLanguageSnippet = result[otherLabelName].snippet;
  let searchHitOtherLanguage = <></>;

  if (otherLanguageSnippet instanceof Array && otherLanguageSnippet[0].includes("<em>")) {
    searchHitOtherLanguage = (
      <div
        className="other-search-hit-container"
        dangerouslySetInnerHTML={{
          __html: otherLanguageText + otherLanguageSnippet.join(""),
        }}
      ></div>
    );
  }
  if (!label) {
    label = result[labelName].raw;
  }
  return (
    <div className="header-subdivider">
      <h3>
        {resultIconMap.get(resultType)()}
        <a onClick={onClickLink} href={"/" + resultType + "/" + result._meta.id}>
          [{result.name.raw}] <span dangerouslySetInnerHTML={{__html: label}}></span>
        </a>
      </h3>
      {searchHitOtherLanguage}
    </div>
  );
}

export {header, resultIconMap};

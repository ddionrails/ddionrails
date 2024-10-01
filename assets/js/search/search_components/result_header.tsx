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

// eslint-disable-next-line valid-jsdoc
/**
 * Normally you would specify snippet length with an API call to elasticsearch
 * but the elasticsearch UI does not seem to do that properly and Snippets are
 * always the same length.
 * This function cuts the highlights from the snippets and applies them
 * to the raw label.
 */
function applySnippetToFullLabel(rawLabel: string, snippets: string[]): string {
  if (!snippets) {
    return rawLabel;
  }
  const snippet = snippets.join("");

  const highlights: Set<string> = new Set();
  const matches = [...snippet.matchAll(/<em>(.*?)<\/em>/g)];
  for (const match of matches) {
    highlights.add(match[1]);
  }
  for (const highlight of highlights) {
    rawLabel = rawLabel.replaceAll(highlight, `<em>${highlight}</em>`);
  }
  return rawLabel;
}

/**
 * Render header for variable result
 * @param result
 * @returns
 */
function header(
  result: SearchResult,
  onClickLink: () => void,
  resultType: result,
  language: string = "en"
) {
  let labelName = "label";
  let otherLabelName = "label_de";
  let otherLanguageText = "Hit in german label: ";
  if (language == "de") {
    labelName = "label_de";
    otherLabelName = "label";
    otherLanguageText = "Treffer in englischem label: ";
  }
  const label = applySnippetToFullLabel(result[labelName].raw, result[labelName].snippet);
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
  return (
    <div className="header-subdivider">
      <h3>
        {resultIconMap.get(resultType)()}
        <a onClick={onClickLink} href={"/" + resultType + "/" + result._meta.id}>
          <span className="result-name">{result.name.raw}:</span>
          <span dangerouslySetInnerHTML={{__html: label}}></span>
        </a>
      </h3>
      {searchHitOtherLanguage}
    </div>
  );
}

export {header, resultIconMap};

import { SearchResult } from "@elastic/search-ui";
import { header } from "../search_components/result_header";
import { sep } from "./result_field_separator";

import { LanguageCode } from "../language_state";
import { resultFactoryMapper } from "../factory_mappers";

/**
 * Render variable result body
 * @param result
 * @returns
 */
function questionBody(result: SearchResult, language: LanguageCode) {
  if (language === "de") {
    return (
      <p>
        Studie: {result.study.raw.label}
        {sep()}Instrument: {result.instrument.raw.label_de}
        {sep()}Zeitraum: {result.period.raw.label_de}
      </p>
    );
  }
  return (
    <p>
      Study: {result.study.raw.label}
      {sep()}Period: {result.period.raw.label}
    </p>
  );
}

function getQuestionItemResultText(
  result: SearchResult,
  language: LanguageCode,
) {
  let itemText = " Result in question item: ";
  if (language == "de") {
    itemText = " Treffer in Frageitem: ";
  }

  let itemSnippet = result?.["question_items.de"]?.snippet.join(" ");
  itemSnippet = itemSnippet + result?.["question_items.en"]?.snippet.join(" ");
  let fullItemText = "";
  if (itemSnippet) {
    const matches = itemSnippet.matchAll(/(<em>.*?<\/em>)/g);
    const results = Array.from(
      matches,
      (match: RegExpMatchArray) => match[1] ?? match[0],
    );
    const uniqueResults = [...new Set(results)];
    fullItemText = itemText + uniqueResults.join(" ... ");
  }
  if (fullItemText) {
    return (
      <div>
        <div
          className="other-search-hit-container"
          dangerouslySetInnerHTML={{ __html: fullItemText }}
        ></div>
      </div>
    );
  }
  return <div></div>;
}

/**
 *
 * @param param0
 * @returns
 */
function questionResultFactory({
  result,
  onClickLink,
  language,
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode;
}) {
  let itemSection = getQuestionItemResultText(result, language);

  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "question", language)}
      </div>
      <div className="sui-result__body">
        {questionBody(result, language)}
        {itemSection}
        <div
          className="sui-result__details"
          dangerouslySetInnerHTML={{ __html: result.description }}
        ></div>
      </div>
    </li>
  );
}

const questionResult = resultFactoryMapper(questionResultFactory);

export { questionResult };

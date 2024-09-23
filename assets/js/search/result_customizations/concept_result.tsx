import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import { resultFactoryMapper } from "../factory_mappers";

/**
 * Render variable result body
 * @param result
 * @returns
 */
function conceptBody(result: SearchResult, language: "en" | "de" = "en") {
  let outputText = "";
  if (language === "de") {
    if (result.study.raw.label_de === "") {
      outputText = "Konzept ist keiner Studie zugeordnet";
    } else {
      outputText = `Konzept in Studie ${result.study.raw.label_de}`;
    }
    return <p>{outputText}</p>;
  }
  if (result.study.raw.label === "") {
    outputText = "Concept not associated with any study";
  } else {
    outputText = `Concept in study ${result.study.raw.label}`;
  }
  return <p>{outputText}</p>;
}

/**
 *
 * @param param0
 * @returns
 */
function conceptResultFactory({
  result,
  onClickLink,
  language = "en",
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: "en" | "de";
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "concept", language)}
      </div>
      <div className="sui-result__body">
        {conceptBody(result, language)}
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

const conceptResult = resultFactoryMapper(conceptResultFactory);


export {conceptResult};

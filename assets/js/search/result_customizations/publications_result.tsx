import {SearchResult} from "@elastic/search-ui";
import {header} from "../search_components/result_header";
import {LanguageCode} from "../language_state";
import { resultFactoryMapper } from "../factory_mappers";

/**
 * Render publication result body
 * @param result
 * @returns
 */
function publicationBody(result: SearchResult, language: LanguageCode) {
  let text = "Publication by";
  if (language === "de") {
    text = "Publikation von";
  }
  return (
    <p>
      {text} {result.author.raw} ({result.year.raw})
    </p>
  );
}

/**
 *
 * @param param0
 * @returns
 */
function publicationResultFactory({
  result,
  onClickLink,
  language,
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode;
}) {
  return (
    <li className="sui-result">
      <div className="sui-result__header">
        {header(result, onClickLink, "publication", language)}
      </div>
      <div className="sui-result__body">
        {publicationBody(result, language)}
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

const publicationResult = resultFactoryMapper(publicationResultFactory);

export {publicationResult};

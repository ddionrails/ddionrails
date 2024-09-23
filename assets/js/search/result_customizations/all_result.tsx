import {SearchResult} from "@elastic/search-ui";

import {conceptResult} from "./concept_result";
import {questionResult} from "./question_result";
import {topicResult} from "./topic_result";
import {variableResult} from "./variable_result";
import { resultFactoryMapper } from "../factory_mappers";
import { LanguageCode } from "../language_state";


/**
 *
 * @param param0
 * @returns
 */
function AllResultFactory({
  result,
  onClickLink,
  language,
}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode
}) {
  if (result._meta.rawHit._index === "concepts") {
    return conceptResult.get(language)({result, onClickLink});
  }
  if (result._meta.rawHit._index === "topics") {
    return topicResult.get(language)({result, onClickLink});
  }
  if (result._meta.rawHit._index === "questions") {
    return questionResult.get(language)({result, onClickLink});
  }
  if (result._meta.rawHit._index === "variables") {
    return variableResult.get(language)({result, onClickLink});
  }
  return null;
}

const AllResult = resultFactoryMapper(AllResultFactory);

export {AllResult};

import {SearchResult} from "@elastic/search-ui";

import {conceptResult} from "./concept_result";
import {questionResult} from "./question_result";
import {topicResult} from "./topic_result";
import {variableResult} from "./variable_result";


/**
 *
 * @param param0
 * @returns
 */
function AllResult({
  result,
  onClickLink,
}: {
  result: SearchResult;
  onClickLink: () => void;
}) {
  if (result._meta.rawHit._index === "concepts") {
    return conceptResult({result, onClickLink});
  }
  if (result._meta.rawHit._index === "topics") {
    return topicResult({result, onClickLink});
  }
  if (result._meta.rawHit._index === "questions") {
    return questionResult({result, onClickLink});
  }
  if (result._meta.rawHit._index === "variables") {
    return variableResult({result, onClickLink});
  }
  return null;
}

export {AllResult};

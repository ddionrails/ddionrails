import {SearchResult} from "@elastic/search-ui";

import {variableResult} from "./variable_result";
import {questionResult} from "./question_result";


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
  if (result._meta.rawHit._index === "variables") {
    return variableResult({result, onClickLink});
  }
  if (result._meta.rawHit._index === "questions") {
    return questionResult({result, onClickLink});
  }
  return null;
}

export {AllResult};

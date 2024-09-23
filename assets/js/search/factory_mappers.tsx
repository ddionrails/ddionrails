import {SearchResult} from "@elastic/search-ui";
import {LanguageCode} from "./language_state";

/**
 * Creates a map from each language to its corresponding factory function call
 * @param factoryFunction
 */
function facetFactoryMapper(factoryFunction: (language: LanguageCode) => any) {
  const facets = new Map();
  facets.set("en", () => {
    return factoryFunction("en");
  });
  facets.set("de", () => {
    return factoryFunction("de");
  });
  return facets;
}

/**
 * Creates a map from each language to its corresponding factory function call
 * @param factoryFunction
 */
function resultFactoryMapper(factoryFunction: ({result, onClickLink, language}: {
  result: SearchResult;
  onClickLink: () => void;
  language: LanguageCode;
}) => any ) {
  const result = new Map();
  result.set(
    "en",
    ({result, onClickLink}: {result: SearchResult; onClickLink: () => void}) => {
      return factoryFunction({result, onClickLink, language: "en"});
    }
  );
  result.set(
    "de",
    ({result, onClickLink}: {result: SearchResult; onClickLink: () => void}) => {
      return factoryFunction({result, onClickLink, language: "de"});
    }
  );
  return result;
}

export {facetFactoryMapper, resultFactoryMapper};

import type {
  AutocompletedResult,
  AutocompletedResultSuggestion,
  AutocompletedSuggestion,
  AutocompletedSuggestions,
  AutocompleteResult,
  AutocompleteSuggestion,
} from "@elastic/search-ui";

function getNewClassName(newClassName: string | string[]) {
  if (!Array.isArray(newClassName)) return newClassName;

  return newClassName.filter((name) => name).join(" ");
}

function appendClassName(
  baseClassName?: string | string[] | undefined,
  newClassName?: string | string[] | undefined,
): string {
  if (!newClassName) {
    return (
      (Array.isArray(baseClassName)
        ? baseClassName.join(" ")
        : baseClassName) || ""
    );
  }
  if (!baseClassName) return getNewClassName(newClassName) || "";
  return `${baseClassName} ${getNewClassName(newClassName)}`;
}

function getRaw(result: any, value: any) {
  if (!result[value] || !result[value].raw) return;
  return result[value].raw;
}

function getSnippet(result: any, value: any) {
  if (!result[value] || !result[value].snippet) return;
  return result[value].snippet;
}

export type SearchBoxAutocompleteViewProps = {
  allAutocompletedItemsCount: number;
  autocompleteResults?: boolean | AutocompleteResult;
  autocompletedResults: AutocompletedResult[];
  autocompletedSuggestions: AutocompletedSuggestions;
  autocompletedSuggestionsCount: number;
  autocompleteSuggestions?: boolean | AutocompleteSuggestion;
  getItemProps: any;
  getMenuProps: (className: any) => any;
  className?: string;
};

/**
 *
 * @param result
 * @param index
 * @param autocompleteResults
 * @returns
 */
function renderResults(result: any, index: any, autocompleteResults: any) {
  let titleField = null;
  if (autocompleteResults.hasOwnProperty("titleField")) {
    titleField = autocompleteResults.titleField;
  }
  let labelSnippet = getSnippet(result, "label");
  if (labelSnippet === undefined) {
    labelSnippet = result.label.raw;
  }
  let titleSnippet = getSnippet(result, "name");
  if (titleSnippet === undefined) {
    titleSnippet = getRaw(result, titleField);
  }
  titleSnippet = `${titleSnippet} | ${labelSnippet}`;

  const indexName = `${result._meta.rawHit._index}`;
  let entityName = indexName;
  if (indexName.endsWith("s")) {
    entityName = indexName.slice(0, -1);
  }

  return (
    <a href={`/${entityName}/` + result.id.raw} key={result.id.raw}>
      <li>
        <span
          dangerouslySetInnerHTML={{
            __html: titleSnippet,
          }}
        />
      </li>
    </a>
  );
}

// eslint-disable-next-line require-jsdoc, complexity
function Autocomplete({
  autocompleteResults,
  autocompletedResults,
  autocompleteSuggestions,
  autocompletedSuggestions,
  className,
  getItemProps,
  getMenuProps,
}: SearchBoxAutocompleteViewProps) {
  return (
    <div
      {...getMenuProps({
        className: appendClassName(
          "sui-search-box__autocomplete-container",
          className,
        ),
      })}
    >
      <div>
        {!!autocompleteResults &&
          !!autocompletedResults &&
          typeof autocompleteResults !== "boolean" &&
          autocompletedResults.length > 0 &&
          autocompleteResults.sectionTitle && (
            <div className="sui-search-box__section-title">
              {autocompleteResults.sectionTitle}
            </div>
          )}
        {!!autocompleteResults &&
          !!autocompletedResults &&
          autocompletedResults.length > 0 && (
            <ul className="sui-search-box__results-list">
              {autocompletedResults.map((result, index: number) => {
                return renderResults(result, index, autocompleteResults);
              })}
            </ul>
          )}
      </div>
    </div>
  );
}

export default Autocomplete;

import React from "react";

import {MultiCheckboxFacet} from "@elastic/react-search-ui-views";

import {getFilterValueDisplay} from "@elastic/react-search-ui-views/lib/cjs/view-helpers/";
import {FacetViewProps} from "@elastic/react-search-ui-views/lib/cjs/types/";
import type {FacetValue} from "@elastic/search-ui";

/**
 * Sort Facet groups by label
 * @param a
 * @param b
 * @returns
 */
function sortByDisplayedLabel(a: FacetValue, b: FacetValue): number {
  if (getFilterValueDisplay(a.value) > getFilterValueDisplay(b.value)) {
    return 1;
  }
  return -1;
}

/**
 *
 * @param param0
 * @returns
 */
function SortedMultiCheckboxFacet({
  className,
  label,
  onMoreClick,
  onRemove,
  onSelect,
  options,
  showMore,
  showSearch,
  onSearch,
  searchPlaceholder,
  values,
  onChange,
}: FacetViewProps) {
  options.sort(sortByDisplayedLabel);
  // eslint-disable-next-line new-cap
  return MultiCheckboxFacet({
    className,
    label,
    onMoreClick,
    onRemove,
    onSelect,
    options,
    showMore,
    showSearch,
    onSearch,
    searchPlaceholder,
    values,
    onChange,
  });
}

export default SortedMultiCheckboxFacet;

import {
  Facet,
  Sorting,
} from "@elastic/react-search-ui";
import SortedMultiCheckboxFacet from "../view_customisations/sorted_facet_view";

/**
 *
 * @return {Element}
*/
export function sorting() {
  return <Sorting
    label={"Sort by"}
    sortOptions={[
      {
        name: "Relevance",
        value: [],
      },
      {
        name: "Period (ascending)",
        value: [
          {
            field: "period.label",
            direction: {order: "asc"},
          },
        ],
      },
      {
        name: "Period (descending)",
        value: [
          {
            field: "period.label",
            direction: {order: "desc"},
          },
        ],
      },
    ]}
  />;
};

/**
 *
 * @return { Element }
 */
export function facets() {
  return <><Facet
    key={"3"}
    field={"study_name"}
    label={"Study"}
    view={SortedMultiCheckboxFacet}
  />
  <Facet
    key={"1"}
    field={"analysis_unit.label"}
    label={"analysis unit"}
    view={SortedMultiCheckboxFacet}
  />
  <Facet
    key={"2"}
    field={"period.label"}
    label={"period"}
    view={SortedMultiCheckboxFacet}
  />
  </>;
}

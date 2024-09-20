import {Facet} from "@elastic/react-search-ui";
import SortedMultiCheckboxFacet from "../search_components/sorted_facet";

// eslint-disable-next-line require-jsdoc
function studyFacet(language: string) {
  if (language === "de") {
    return (
      <Facet
        key={"1"}
        field={"study_name_de"}
        label={"Studie"}
        view={SortedMultiCheckboxFacet}
      />
    );
  }
  return (
    <Facet
      key={"1"}
      field={"study_name"}
      label={"Study"}
      view={SortedMultiCheckboxFacet}
    />
  );
}

// eslint-disable-next-line require-jsdoc
function facetConfig(language: string): [any, any] {
  let disjunctiveFacets = ["study_name"];
  let facets: any = {
    study_name: {type: "value"},
  };

  if (language === "de") {
    disjunctiveFacets = ["study_name_de"];
    facets = {
      study_name_de: {type: "value"},
    };
  }
  return ([disjunctiveFacets, facets]);
}

export {facetConfig, studyFacet};

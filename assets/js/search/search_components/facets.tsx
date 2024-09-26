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
function genericFacet(
  language: string,
  name: string,
  labels: [string, string],
  key: string
) {
  if (language === "de") {
    return (
      <Facet
        key={key}
        field={`${name}.label_de`}
        label={labels[1]}
        view={SortedMultiCheckboxFacet}
      />
    );
  }
  return (
    <Facet
      key={key}
      field={`${name}.label`}
      label={labels[0]}
      view={SortedMultiCheckboxFacet}
    />
  );
}

// eslint-disable-next-line require-jsdoc
function unlabeledFacet(
  language: string,
  name: string,
  labels: [string, string],
  key: string
) {
  if (language === "de") {
    return (
      <Facet
        key={key}
        field={name}
        label={labels[1]}
        view={SortedMultiCheckboxFacet}
      />
    );
  }
  return (
    <Facet
      key={key}
      field={name}
      label={labels[0]}
      view={SortedMultiCheckboxFacet}
    />
  );
}

// eslint-disable-next-line require-jsdoc
function studyFacetConfig(language: string): [any, any] {
  let disjunctiveFacets = "study_name";
  let facets: any = {
    study_name: {type: "value"},
  };

  if (language === "de") {
    disjunctiveFacets = "study_name_de";
    facets = {
      study_name_de: {type: "value"},
    };
  }
  return [disjunctiveFacets, facets];
}

// eslint-disable-next-line require-jsdoc
function facetConfig(
  language: string,
  facetNames: Array<string> = ["study"]
): [any, any] {
  const disjunctiveFacets = [];
  let facets = {};
  for (const name of facetNames) {
    if (name === "study") {
      const [disjunctiveFacet, facet] = studyFacetConfig(language);
      disjunctiveFacets.push(disjunctiveFacet);
      facets = {...facets, ...facet};
      continue;
    }
    if (language === "de") {
      disjunctiveFacets.push(`${name}.label_de`);
      const facet = new Map([[`${name}.label_de`, {type: "value"}]]);
      facets = {...facets, ...Object.fromEntries(facet)};
      continue;
    }
    disjunctiveFacets.push(`${name}.label`);
    const facet = new Map([[`${name}.label`, {type: "value"}]]);
    facets = {...facets, ...Object.fromEntries(facet)};
  }
  return [disjunctiveFacets, facets];
}

export {facetConfig, genericFacet, studyFacet, unlabeledFacet};

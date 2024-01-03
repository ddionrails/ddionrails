<template>
  <multi-list
    componentId="AnalysisUnit"
    :data-field="$language =='en' ? 'analysis_unit.label' : 'analysis_unit.label_de' "
    :title="$language =='en' ? 'Analysis Unit' : 'Analyseeinheit'"
    :showSearch="false"
    :placeholder="$language == 'en' ? 'Search' : 'Suche'"
    :selectAllLabel="$language =='en' ? 'Select all' : 'Alle auswählen'"
    :size="100"
    :URLParams="true"
    :react="react"
    class="card facet"
    :innerClass="{
        title: 'card-header',
    }"
    showMissing="true"
    missingLabel="None"
  />
</template>

<script>
import {setLanguageObserver} from "../../helpers.js";

export default {
  name: "AnalysisUnitFacet",
  props: ["react"],
  async mounted(_) {
    await setLanguageObserver(this);
  },
};
</script>

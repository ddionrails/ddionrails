<template>
  <multi-list
    componentId="ConceptualDataset"
    data-field="conceptual_dataset"
    :data-field="$language == 'en' ? 'conceptual_dataset.label' : 'conceptual_dataset.label_de'"
    :title="$language == 'en' ? 'Conceptual Dataset' : 'Konzeptioneller Datensatz'"
    :showSearch="false"
    :placeholder="$language == 'en' ? 'Search' : 'Suche'"
    :selectAllLabel="$language =='en' ? 'Select all' : 'Alle auswählen'"
    :size="100"
    :URLParams="true"
    defaultValue={[]}
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
  name: "ConceptualDatasetFacet",
  props: ["react"],
  async mounted(_) {
    await setLanguageObserver(this);
  },
};
</script>

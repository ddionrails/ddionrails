<template>
  <div>
  <multi-list
    componentId="Period"
    :data-field="$language =='en' ? 'period.label' : 'period.label_de'"
    :title="$language =='en' ? 'Period': 'Zeitraum'"
    :showSearch="true"
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
    sortBy="asc"
  />
  </div>
</template>

<script>
import {setLanguageObserver} from "../../helpers.js";

export default {
  name: "PeriodFacet",
  props: ["react"],
  async mounted(props) {
    await setLanguageObserver(this);
  },
};
</script>

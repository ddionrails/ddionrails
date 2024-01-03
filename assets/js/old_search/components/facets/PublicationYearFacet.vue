<template>
  <dynamic-range-slider
    dataField="year"
    componentId="Year"
    :title="$language == 'en' ? 'Year': 'Jahr'"
    :showFilter="true"
    :size="100"
    :URLParams="true"
    :rangeLabels="function(min, max){
      return {
        start: min,
        end: max,
      }
    }"
    class="card facet"
    :innerClass="{
      title: 'card-header'
    }"
/>
</template>

<script>
import {setLanguageObserver} from "../../helpers.js";

export default {
  name: "PublicationYearFacet",
  async mounted(_) {
    await setLanguageObserver(this);
  },
};
</script>

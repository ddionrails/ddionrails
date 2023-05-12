<template>
  <multi-list
    componentId="Study"
    dataField="study_name"
    :title="$language =='en' ? 'Study' : 'Studie'"
    :showSearch="false"
    :size="100"
    :selectAllLabel="$language =='en' ? 'Select all' : 'Alle auswählen'"
    :URLParams="true"
    :react="react"
    class="card facet"
    :innerClass="{
        title: 'card-header',
    }"
  />
</template>

<script>
import {setLanguageObserver} from "../../helpers.js";

export default {
  name: "StudyFacet",
  props: ["react"],
  async mounted(_) {
    await setLanguageObserver(this);
  },
};
</script>

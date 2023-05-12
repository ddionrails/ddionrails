<template>
  <multi-list
    componentId="Type"
    data-field="sub_type"
    :title="$language =='en' ? 'Type' : 'Typ'"
    :showSearch="false"
    :selectAllLabel="$language =='en' ? 'Select all' : 'Alle auswählen'"
    :size="100"
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
  name: "PublicationTypeFacet",
  props: ["react"],
  async mounted(_) {
    await setLanguageObserver(this);
  },
};
</script>

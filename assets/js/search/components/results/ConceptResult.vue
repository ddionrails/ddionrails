<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-cog"></i>
      <a :href="baseUrl + '/concept/' + item._id">
        [
        <span v-html="item.name"></span>]
        {{ getLabelWithFallback(item, $language) }}
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language == 'en'">Concept in study</span>
      <span v-if="$language == 'de'">Konzept in Studie</span>
      {{ item.study_name.join(', ') }}</p>
  </div>
</template>

<script>
import {getLabelWithFallback} from "../../helpers";

export default {
  name: "ConceptResult",
  props: ["item"],
  methods: {
    getLabelWithFallback,
  },
  data() {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

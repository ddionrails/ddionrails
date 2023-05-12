<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-cog"></i>
      <a :href="baseUrl + '/concept/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-if="$language == 'en'" v-html="item.label"></span>
        <span v-if="$language == 'de'" v-html="item.label_de"></span>
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language == 'en'">Concept in study</span>
      <span v-if="$language == 'de'">Konzept in Studie</span>
      {{ item.study_name.join(', ') }}</p>
  </div>
</template>

<script>
export default {
  name: "ConceptResult",
  props: ["item"],
  data() {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

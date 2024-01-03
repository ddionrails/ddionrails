<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-tasks"></i>
      <a :href="'/question/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="getLabelWithFallback(item, $language)"></span>]
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language == 'en'">Question in study:</span>
      <span v-if="$language == 'de'">Frage Teil von Studie</span>
      <a :href="'/' + item.study.name">
        {{ item.study.label }}
      </a>
      |
      <span v-if="$language == 'en'">instrument:</span>
      <span v-if="$language == 'de'">Instrumente:</span>
      <a :href="'/' + item.study.name + '/instruments/' + item.instrument.name">
        <span v-if="$language == 'de'"> {{ item.instrument.label_de }} </span>
        <span v-html="getLabelWithFallback(item.instrument, $language)"></span>
      </a>
      |
      <span v-if="$language == 'en'">period:</span>
      <span v-if="$language == 'de'">Zeitraum:</span>
      {{ getLabelWithFallback(item.period, $language) }}
      |
      <span v-if="$language == 'en'">analysis unit:</span>
      <span v-if="$language == 'de'">Analyseeinheit:</span>
      <span v-html="getLabelWithFallback(item.analysis_unit, $language)"></span>
    </p>
  </div>
</template>

<script>
import {getLabelWithFallback} from "../../helpers";

export default {
  name: "QuestionResult",
  props: ["item"],
  methods: {
    getLabelWithFallback,
  },
  data: () => {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

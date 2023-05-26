<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-chart-bar"></i>
      <a :href="baseUrl + '/variable/' + item._id">
        [
        <span v-html="item.name"></span>]
        {{ getLabelWithFallback(item, $language) }}
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language == 'de'">Variable Teil von Studie</span>
      <span v-if="$language == 'en'">Variable in study:</span>
      <a :href="'/' + item.study.name" v-html="item.study.label"> </a>
      | <span v-if="$language == 'en'">dataset</span
      ><span v-if="$language == 'de'">Datensatz</span>:
      <a
        :href="'/' + item.study.name + '/data/' + item.dataset.name"
        :title="item.dataset.label"
        v-html="item.dataset.name"
      >
      </a>
      | <span v-if="$language == 'en'">period:</span>
      <span v-if="$language == 'de'">Zeitraum:</span>
      {{ getLabelWithFallback(item.period, $language ) }}
      |
      <span v-if="$language == 'en'">analysis unit:</span
      ><span v-if="$language == 'de'">Analyseeinheit:</span>
        {{ getLabelWithFallback(item.analysis_unit, $language) }}
    </p>
  </div>
</template>

<script>
import {getLabelWithFallback} from "../../helpers";
export default {
  name: "VariableResult",
  props: ["item"],
  data: () => {
    return {
      baseUrl: window.location.origin,
    };
  },
  methods: {
    getLabelWithFallback,
  },
};
</script>

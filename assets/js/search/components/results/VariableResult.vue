<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-chart-bar"></i>
      <a :href="baseUrl + '/variable/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-if="$language == 'en'" v-html="item.label"></span>
        <span v-if="$language == 'de'" v-html="item.label_de"></span>
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
      | <span v-if="$language == 'en'">period: {{ item.period.label }}</span>
      <span v-if="$language == 'de'">Zeitraum: {{ item.period.label_de }}</span>
      |
      <span v-if="$language == 'en'">analysis unit:
        {{ item.analysis_unit.label }}</span
      ><span v-if="$language == 'de'">Analyseeinheit:
        {{ item.analysis_unit.label_de }}</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "VariableResult",
  props: ["item"],
  data: () => {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

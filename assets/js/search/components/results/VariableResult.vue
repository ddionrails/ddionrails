<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-chart-bar"></i>
      <a :href="baseUrl + '/variable/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-if="language == 'de'" v-html="item.label_de"></span>
        <span v-if="language == 'en'" v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">
        <span v-if="language == 'de'">Variable Teil von Studie</span>
        <span v-if="language == 'en'">Variable in study:</span>
      <a
        :href="'/' + item.study.name"
        v-html="item.study.label">
      </a>
      |
      dataset:
      <a
        :href="'/' + item.study.name + '/data/' + item.dataset.name"
        :title="item.dataset.label"
        v-html="item.dataset.name">
      </a>
      |
      period:
      <span v-if="item.period">{{ item.period }}</span>
      <span v-else>None</span> |
      analysis unit:
      <span v-if="item.analysis_unit">{{ item.analysis_unit }}</span>
      <span v-else>None</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "VariableResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin,
      language: document.getElementById("language-switch").getAttribute("data-current-language")
    };
  }
};
</script>

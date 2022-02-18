<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-chart-line"></i>
      <span v-if="item.statistics_type ===  'ordinal'">
        <span v-html="item.label_de"></span>
      <a :href="baseUrl + '/' + item.study.name + '/statistics/categorical/?variable=' + item._id">
      categorical
      </a>
      <a :href="baseUrl + '/' + item.study.name + '/statistics/numerical/?variable=' + item._id">
      numerical
      </a>
      </span>
      <span v-else>
        <span v-html="item.label_de"></span>
      <a :href="baseUrl + '/' + item.study.name + '/statistics/' + item.statistics_type +'/?variable=' + item._id">
        <span v-html="item.statistics_type"></span>
      </a>
      </span>
    </p>
    <p class="card-text">
      Variable in study: {{ item.study.label }} | 
      period:
      <span v-if="item.period"> {{ item.period }}</span>
      <span v-else>None</span> |
      analysis unit:
      <span v-if="item.analysis_unit"> {{ item.analysis_unit }}</span>
      <span v-else>None</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "StatisticsResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin
    };
  }
};
</script>

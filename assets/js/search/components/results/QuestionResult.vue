<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-tasks"></i>
      <a :href="'/question/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">
      Question in study:
      <a :href="'/' + item.study.name">
        {{ item.study.label }}
      </a>
      |
      instrument:
      <a :href="'/' + item.study.name + '/instruments/' + item.instrument.name">
        {{ item.instrument.label }}
      </a>
      |
      period:
      <span
        v-if="item.period"
      >{{ item.period }}</span>
      <span v-else>None</span> |
      analysis unit:
      <span v-if="item.analysis_unit">{{ item.analysis_unit }}</span>
      <span v-else>None</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "QuestionResult",
  props: ["item"],
  data: () => {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

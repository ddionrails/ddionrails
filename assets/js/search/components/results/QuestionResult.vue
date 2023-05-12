<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-tasks"></i>
      <a :href="'/question/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-if="$language == 'en'"  v-html="item.label"></span>
        <span v-if="$language == 'de'"  v-html="item.label_de"></span>
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language == 'en'">Question in study:</span>
      <span v-if="$language == 'de'">Frage Teil von Studie</span>
      <a :href="'/' + item.study.name">
        {{ item.study.label }}
      </a>
      |
      <span v-if="$language =='en'">instrument:</span>
      <span v-if="$language == 'de'">Messwerkzeuge:</span>
      <a :href="'/' + item.study.name + '/instruments/' + item.instrument.name">
        <span v-if="$language == 'en'"> {{ item.instrument.label }} </span>
        <span v-if="$language == 'de'"> {{ item.instrument.label_de }} </span>
      </a>
      |
      <span v-if="$language == 'en'" >period: {{ item.period.label }}</span>
      <span v-if="$language == 'de'" >Zeitraum: {{ item.period.label_de }}</span>
      |
      <span v-if="$language == 'en'">analysis unit: {{ item.analysis_unit.label }}</span>
      <span v-if="$language == 'de'">
        Analyseeinheit: {{ item.analysis_unit.label_de }}
      </span>
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

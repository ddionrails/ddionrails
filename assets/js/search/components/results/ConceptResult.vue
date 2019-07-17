<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-cog"></i>
      <a :href="baseUrl + '/' + item._type + '/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">Concept in study {{ item.study.join(', ') }}</p>
  </div>
</template>

<script>
export default {
  name: "ConceptResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin
    };
  }
};
</script>
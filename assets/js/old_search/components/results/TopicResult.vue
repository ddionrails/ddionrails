<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-cogs"></i>
      <a :href="baseUrl + '/topic/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">Topic in study:
      <a
        :href="'/' + item.study.name"
        v-html="item.study.label">
      </a>
    </p>
  </div>
</template>

<script>
export default {
  name: "TopicResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin
    };
  }
};
</script>

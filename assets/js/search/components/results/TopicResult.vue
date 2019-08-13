<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-cogs"></i>
      <a :href="baseUrl + '/' + item.type + '/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">Topic in study {{ item.study }}</p>
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
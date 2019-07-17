<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-newspaper"></i>
      <a :href="baseUrl + '/' + item._type + '/' + item._id">
        <span v-html="item.title"></span>
      </a>
    </p>
    <p class="card-text">Publication by: <span v-html="item.author"></span> ({{ item.year }})</p>
  </div>
</template>

<script>
export default {
  name: "PublicationResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin
    };
  }
};
</script>
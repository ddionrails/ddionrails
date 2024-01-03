<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-newspaper"></i>
      <a :href="baseUrl + '/publication/' + item._id">
        <span v-html="item.title"></span>
      </a>
    </p>
    <p class="card-text">
      <span v-if="$language =='en'">Publication by:</span>
      <span v-if="$language =='de'">Publikation von:</span>
      <span v-html="item.author"></span> ({{ item.year }})
    </p>
  </div>
</template>

<script>
export default {
  name: "PublicationResult",
  props: ["item"],
  data() {
    return {
      baseUrl: window.location.origin,
    };
  },
};
</script>

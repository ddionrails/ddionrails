<template>
  <multi-list
    componentId="Study"
    data-field="study"
    title="Study"
    :showSearch="false"
    selectAllLabel="Select all"
    :URLParams="true"
    :react="react"
    class="card facet"
    :innerClass="{
        title: 'card-header',
    }"
  />
</template>

<script>
export default {
  name: "StudyFacet",
  props: ["react"]
};
</script>
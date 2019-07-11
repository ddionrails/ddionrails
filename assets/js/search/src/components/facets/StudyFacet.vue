<template>
  <multi-list
    componentId="Studies"
    data-field="study"
    class="filter"
    :showSearch="false"
    title="Studies"
    selectAllLabel="Select all"
    :URLParams="true"
    :react="react"
  />
</template>
<script>
export default {
  name: "StudyFacet",
  props: ["react"]
};
</script>
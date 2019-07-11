<template>
  <multi-list
    componentId="Years"
    data-field="year"
    class="filter"
    :showSearch="false"
    title="Years"
    selectAllLabel="Select all"
    :URLParams="true"
    :react="react"
  />
</template>
<script>
export default {
  name: "PublicationYearFacet",
  props: ["react"]
};
</script>
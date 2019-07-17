<template>
  <multi-list
    componentId="Year"
    data-field="year"
    title="Year"
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
  name: "PublicationYearFacet",
  props: ["react"]
};
</script>
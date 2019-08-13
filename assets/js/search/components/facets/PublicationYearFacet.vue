<template>
  <dynamic-range-slider
    dataField="year"
    componentId="Year"
    title="Year"
    :showFilter="true"
    :URLParams="true"
    :rangeLabels="function(min, max){
      return {
        start: min,
        end: max,
      }
    }"
    class="card facet"
    :innerClass="{
      title: 'card-header'
    }"
/>
</template>

<script>
export default {
  name: "PublicationYearFacet"
};
</script>
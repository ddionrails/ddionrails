<template>
  <multi-list
    componentId="Period"
    data-field="period"
    title="Period"
    :showSearch="true"
    selectAllLabel="Select all"
    :size="100"
    :URLParams="true"
    :react="react"
    class="card facet"
    :innerClass="{
        title: 'card-header',
    }"
    showMissing="true"
    missingLabel="None"
    sortBy="asc"
  />
</template>

<script>
export default {
  name: "PeriodFacet",
  props: ["react"]
};
</script>

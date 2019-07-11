<template>
  <multi-list
    componentId="Periods"
    data-field="period"
    title="Periods"
    :showSearch="false"
    selectAllLabel="Select all"
    :URLParams="true"
    :react="react"
    class="card facet"
    :innerClass="{
        title: 'card-header',
    }"
    showMissing="true"
    missingLabel="None"
  />
</template>

<script>
export default {
  name: "PeriodFacet",
  props: ["react"]
};
</script>
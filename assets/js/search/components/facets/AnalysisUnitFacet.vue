<template>
  <multi-list
    componentId="AnalysisUnits"
    data-field="analysis_unit"
    title="Analysis Units"
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
  name: "AnalysisUnitFacet",
  props: ["react"]
};
</script>
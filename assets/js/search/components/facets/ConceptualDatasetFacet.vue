<template>
  <multi-list
    componentId="ConceptualDatasets"
    data-field="conceptual_dataset"
    title="Conceptual Datasets"
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
  name: "ConceptualDatasetFacet",
  props: ["react"]
};
</script>
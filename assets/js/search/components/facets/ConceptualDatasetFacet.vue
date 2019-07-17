<template>
  <multi-list
    componentId="ConceptualDataset"
    data-field="conceptual_dataset"
    title="Conceptual Dataset"
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
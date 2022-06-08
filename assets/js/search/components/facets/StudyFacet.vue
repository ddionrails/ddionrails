<template>
  <multi-list
    componentId="Study"
    dataField="study_name"
    title="Study"
    :showSearch="false"
    :size="100"
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
  props: ["react"],
};
</script>

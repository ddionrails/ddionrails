<template>
  <multi-list
    componentId="Type"
    data-field="sub_type"
    title="Type"
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
  name: "PublicationTypeFacet",
  props: ["react"]
};
</script>
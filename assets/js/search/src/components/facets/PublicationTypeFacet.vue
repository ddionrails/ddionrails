<template>
  <multi-list
    componentId="Types"
    data-field="sub_type"
    class="filter"
    :showSearch="false"
    title="Types"
    selectAllLabel="Select all"
    :URLParams="true"
    :react="react"
  />
</template>
<script>
export default {
  name: "PublicationTypeFacet",
  props: ["react"]
};
</script>
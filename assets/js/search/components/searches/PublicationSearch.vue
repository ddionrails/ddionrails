<template>
  <div class="d-flex">
    <reactive-base :url="this.$parent.searchUrl" :app="index">
      <div class="navbar m-0 px-0">
        <!-- search bar -->
        <data-search
          componentId="Search"
          :dataField="dataField"
          iconPosition="left"
          :autosuggest="true"
          :highlight="true"
          :URLParams="true"
          :showClear="true"
          placeholder="Search for publications"
        />
        <selected-filters />
      </div>

      <div class="facet-container col-lg-3 my-2 float-left">
        <!-- begin facets -->
        <study-facet :react="{ and: ['Search', 'Type', 'Year'] }" />
        <publication-year-facet />
        <publication-type-facet :react="{ and: ['Search', 'Study', 'Year'] }" />
        <!-- end facets -->
      </div>
      <div class="col-lg-8 m-0 p-0 float-right">
        <reactive-list
          componentId="SearchResult"
          data-field="_score"
          :pagination="true"
          URLParams="true"
          :from="0"
          :size="10"
          :showResultStats="true"
          class="result-list-container"
          :react="{ and: ['Search', 'Study', 'Type', 'Year'] }"
          renderNoResults="No Publications found. Try to change your search query or filter options."
          :sortOptions="[
              {'label': 'Relevance', 'dataField': '_score', 'sortBy': 'desc'},
              {'label': 'Year (descending)', 'dataField': 'year', 'sortBy': 'desc'},
              {'label': 'Year (ascending)', 'dataField': 'year', 'sortBy': 'asc'}
          ]"
        >
          <div slot="renderData" class="card" slot-scope="{ item }">
            <publication-result :item="item" />
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import StudyFacet from "../facets/StudyFacet.vue";
import PublicationTypeFacet from "../facets/PublicationTypeFacet.vue";
import PublicationYearFacet from "../facets/PublicationYearFacet.vue";
import PublicationResult from "../results/PublicationResult.vue";
const helpers = require("./helpers.js");

export default {
  name: "PublicationSearch",
  data: function() {
    return {
      index: helpers.indexNameSwitch("publications"),
      dataField: ["name", "title", "author", "abstract", "cite", "doi"]
    };
  },
  components: {
    StudyFacet,
    PublicationTypeFacet,
    PublicationYearFacet,
    PublicationResult
  }
};
</script>

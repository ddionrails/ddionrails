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
          :placeholder="placeholder()"
        />
        <selected-filters />
      </div>

      <div class="facet-container col-lg-3 my-2 float-left">
        <!-- begin facets -->
        <study-facet :react="{ and: ['Search'] }" />
        <!-- end facets -->
      </div>

      <!-- navbar -->
      <div class="col-lg-8 m-0 p-0 float-right">
        <reactive-list
          componentId="SearchResult"
          data-field="_score"
          :pagination="true"
          URLParams="true"
          :from="0"
          :size="10"
          :showResultStats="true"
          :renderResultStats="customRenderStats"
          class="result-list-container"
          :react="{ and: ['Search', 'Study'] }"
          :renderNoResults="noResults($language, entityPluralNames)"
        >
          <div slot="renderItem" class="card" slot-scope="{ item }">
            <topic-result :item="item" />
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import StudyFacet from "../facets/StudyFacet.vue";
import TopicResult from "../results/TopicResult.vue";
const helpers = require("./helpers.js");

export default {
  name: "TopicSearch",
  data() {
    return {
      index: helpers.indexNameSwitch("topics"),
      dataField: ["name", "label", "label_de", "description", "description_de"],
      entityPluralNames: {en: "topics", de: "Themen"},
    };
  },
  components: {
    StudyFacet,
    TopicResult,
  },
  methods: {
    customRenderStats(stats) {
      return helpers.customRenderStats(this, stats);
    },
    placeholder() {
      return helpers.placeholderTemplate(this.$language, this.entityPluralNames);
    },
    noResults(language, entityPluralNames) {
      return helpers.noResultsTemplate(language, entityPluralNames);
    },
  },
};
</script>

<template>
  <div class="d-flex">
    <reactive-base :url="this.$parent.searchUrl" :app="index">
      <div class="navbar m-0 px-0">
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
          :react="{ and: ['Search', 'Study'] }"
          :renderNoResults="noResults()"
          class="result-list-container m-0 p-0 col-12"
        >
          <div slot="renderItem" class="card" slot-scope="{ item }">
            <concept-result :item="item" />
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import StudyFacet from "../facets/StudyFacet.vue";
import ConceptResult from "../results/ConceptResult.vue";
const helpers = require("./helpers.js");

export default {
  name: "ConceptSearch",
  data() {
    return {
      index: helpers.indexNameSwitch("concepts"),
      dataField: ["name", "label", "label_de", "description", "description_de"],
      entityPluralNames: {"en": "concepts", "de": "Konzepte"},
    };
  },
  components: {
    StudyFacet,
    ConceptResult,
  },
  methods: {
    customRenderStats(stats) {
      return helpers.customRenderStats(this, stats);
    },
    placeholder() {
      return helpers.placeholderTemplate(this.$language, this.entityPluralNames);
    },
    noResults() {
      return helpers.noResultsTemplate(this.$language, this.entityPluralNames);
    },
  },
};
</script>

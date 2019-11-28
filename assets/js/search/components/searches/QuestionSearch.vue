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
          placeholder="Search for questions"
        />
        <selected-filters />
      </div>
      <!-- navbar -->
      <div class="facet-container col-lg-3 my-2 float-left">
        <!-- begin facets -->
        <study-facet :react="{ and: ['AnalysisUnit', 'Period', 'Search'] }" />
        <analysis-unit-facet :react="{ and: ['Period', 'Search', 'Study'] }" />
        <period-facet :react="{ and: ['AnalysisUnit', 'Search', 'Study'] }" />
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
          class="result-list-container"
          :react="{ and: ['AnalysisUnit', 'Period', 'Search', 'Study'] }"
          renderNoResults="No Results found. Try to change your search query or filter options."
          :sortOptions="[
              {'label': 'Relevance', 'dataField': '_score', 'sortBy': 'desc'},
              {'label': 'Period (descending)', 'dataField': 'period', 'sortBy': 'desc'},
              {'label': 'Period (ascending)', 'dataField': 'period', 'sortBy': 'asc'}
          ]"
        >
          <div slot="renderData" class="card" slot-scope="{ item }">
            <question-result :item="item" />
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import AnalysisUnitFacet from "../facets/AnalysisUnitFacet.vue";
import PeriodFacet from "../facets/PeriodFacet.vue";
import StudyFacet from "../facets/StudyFacet.vue";
import QuestionResult from "../results/QuestionResult.vue";
const helpers = require("./helpers.js");

export default {
  name: "QuestionSearch",
  data: function() {
    return {
      index: helpers.indexNameSwitch("questions"),
      dataField: [
        "name",
        "label",
        "label_de",
        "description",
        "description_de",
        "items.en",
        "items.de"
      ]
    };
  },
  components: {
    AnalysisUnitFacet,
    PeriodFacet,
    StudyFacet,
    QuestionResult
  },
  methods: {
    customRenderStats(stats) {
      return helpers.customRenderStats(this, stats);
    }
  }
};
</script>

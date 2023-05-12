<template>
  <div class="d-flex">
    <reactive-base :url="this.$parent.searchUrl" :app="index">
      <div class="navbar m-0 px-0">
        <!-- search bar -->
        <data-search
          componentId="Search"
          :dataField="dataField"
          highlightField="label"
          iconPosition="left"
          :autosuggest="true"
          :highlight="true"
          :URLParams="true"
          :showClear="true"
          :fieldWeights="fieldWeights"
          :fuzziness="0"
          :searchOperators="true"
          :placeholder="$language == 'en' ? 'Search for variables' : 'Variablen durchsuchen'"
        />
        <selected-filters />
      </div>
      <!-- navbar -->
      <div class="facet-container col-lg-3 my-2 float-left">
        <!-- begin facets -->
        <study-facet
          :react="{
            and: ['AnalysisUnit', 'ConceptualDataset', 'Period', 'Search']
          }"
        />
        <conceptual-dataset-facet
          :react="{ and: ['AnalysisUnit', 'Period', 'Search', 'Study'] }"
        />
        <analysis-unit-facet
          :react="{ and: ['ConceptualDataset', 'Period', 'Search', 'Study'] }"
        />
        <period-facet
          :react="{
            and: ['AnalysisUnit', 'ConceptualDataset', 'Search', 'Study']
          }"
        />
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
          :showResultStats="false"
          :renderResultStats="customRenderStats"
          class="result-list-container"
          :react="{
            and: [
              'AnalysisUnit',
              'ConceptualDataset',
              'Period',
              'Search',
              'Study'
            ]
          }"
          renderNoResults=
            "No Variables found. Try to change your search query or filter options."
          :sortOptions="_sortOptions($language)"
        >
          <div slot="renderItem" class="card" slot-scope="{ item }">
            <variable-result :item="item" />
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import AnalysisUnitFacet from "../facets/AnalysisUnitFacet.vue";
import ConceptualDatasetFacet from "../facets/ConceptualDatasetFacet.vue";
import PeriodFacet from "../facets/PeriodFacet.vue";
import StudyFacet from "../facets/StudyFacet.vue";
import VariableResult from "../results/VariableResult.vue";
const helpers = require("./helpers.js");
import {setLanguageObserver} from "../../helpers.js";

export default {
  name: "VariableSearch",
  data() {
    return {
      index: helpers.indexNameSwitch("variables"),
      dataField: [
        "name",
        "label",
        "label_de",
        "dataset",
      ],
      fieldWeights: [1, 2, 2, 1.5],
    };
  },
  async mounted(_) {
    await setLanguageObserver(this);
  },
  components: {
    AnalysisUnitFacet,
    ConceptualDatasetFacet,
    PeriodFacet,
    StudyFacet,
    VariableResult,
  },
  methods: {
    customRenderStats(stats) {
      return helpers.customRenderStats(this, stats, this.$language);
    },
    _sortOptions(language) {
      return helpers.sortOptions(language);
    },
  },
};
</script>

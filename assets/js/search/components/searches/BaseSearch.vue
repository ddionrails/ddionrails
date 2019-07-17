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
          placeholder="Search for concepts, publications, questions, topics and variables"
        />
        <selected-filters />
      </div>
      <div class="facet-container col-lg-3 my-2 float-left">
        <!-- begin facets -->
        <study-facet :react="{ and: ['Search'] }" />
        <!-- end facets -->
      </div>
      <!-- search results -->
      <div class="col-lg-8 m-0 p-0 float-right">
        <reactive-list
          componentId="SearchResult"
          data-field="_score"
          :pagination="true"
          :from="0"
          :size="10"
          :showResultStats="true"
          class="result-list-container"
          :react="{ and: ['Search', 'Study'] }"
          renderNoResults="No Concepts found. Try to change your search query or filter options."
        >
          <div slot="renderData" class="card" slot-scope="{ item }">
            <div v-if="item._type === 'variable'">
              <variable-result :item="item" />
            </div>
            <div v-else-if="item._type === 'concept'">
              <concept-result :item="item" />
            </div>
            <div v-else-if="item._type === 'question'">
              <question-result :item="item" />
            </div>
            <div v-else-if="item._type === 'publication'">
              <publication-result :item="item" />
            </div>
            <div v-else-if="item._type === 'topic'">
              <topic-result :item="item" />
            </div>
          </div>
        </reactive-list>
      </div>
    </reactive-base>
  </div>
</template>

<script>
import StudyFacet from "../facets/StudyFacet.vue";
import ConceptResult from "../results/ConceptResult.vue";
import QuestionResult from "../results/QuestionResult.vue";
import PublicationResult from "../results/PublicationResult.vue";
import TopicResult from "../results/TopicResult.vue";
import VariableResult from "../results/VariableResult.vue";
const helpers = require("./helpers.js");

export default {
  name: "BaseSearch",
  data: function() {
    return {
      index:
        helpers.indexNameSwitch("concepts,") +
        helpers.indexNameSwitch("publications,") +
        helpers.indexNameSwitch("questions,") +
        helpers.indexNameSwitch("topics,") +
        helpers.indexNameSwitch("variables"),
      dataField: [
        /* Fields from all indices */
        "name",
        "label",
        "label_de",
        "description",
        "description_de",
        /* Fields from Publications index */
        "title",
        "author",
        "abstract",
        "cite",
        "doi",
        /* Fields from Questions index */
        "items.en",
        "items.de",
        /* Fields from Variables index */
        "description_long",
        "categories.labels",
        "categories.labels_de",
        "dataset"
      ]
    };
  },
  components: {
    StudyFacet,
    ConceptResult,
    QuestionResult,
    PublicationResult,
    TopicResult,
    VariableResult
  }
};
</script>
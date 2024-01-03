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
      <!-- search results -->
      <div class="col-lg-8 m-0 p-0 float-right">
        <reactive-list
          componentId="SearchResult"
          data-field="_score"
          :pagination="true"
          :from="0"
          :size="10"
          :showResultStats="true"
          :renderResultStats="customRenderStats"
          class="result-list-container"
          :react="{ and: ['Search', 'Study'] }"
          :renderNoResults="
            $language == 'en' ?
            'Nothing found. Try to change your search query or filter options.':
            'Keine Suchtreffer. Versuchen Sie Ihre Suchanfrage oder Filter anzupassen.'"
        >
          <div slot="renderItem" class="card" slot-scope="{ item }">
            <div v-if="item._index === 'variables'">
              <variable-result :item="item" />
            </div>
            <div v-else-if="item._index === 'concepts'">
              <concept-result :item="item" />
            </div>
            <div v-else-if="item._index === 'questions'">
              <question-result :item="item" />
            </div>
            <div v-else-if="item._index === 'publications'">
              <publication-result :item="item" />
            </div>
            <div v-else-if="item._index === 'topics'">
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
  data() {
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
        "dataset",
      ],
      entityPluralNames: {
        "en": "concepts, publications, questions, topics and variables",
        "de": "Konzepte, Publikationen, Fragen, Themen und Variablen",

      },
    };
  },
  components: {
    StudyFacet,
    ConceptResult,
    QuestionResult,
    PublicationResult,
    TopicResult,
    VariableResult,
  },
  methods: {
    customRenderStats(stats) {
      return helpers.customRenderStats(this, stats);
    },
    placeholder() {
      return helpers.placeholderTemplate(this.$language, this.entityPluralNames);
    },
  },
};
</script>

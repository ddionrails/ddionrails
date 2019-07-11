<template>
  <div class="row">
    <reactive-base :url=searchUrl :app=index>
      <div class="col-md-4">
        <!-- begin facets -->
        <study-facet :react="{ and: ['Search', 'Types', 'Years'] }" />
        <publication-type-facet :react="{ and: ['Search', 'Studies', 'Years'] }" />
        <publication-year-facet :react="{ and: ['Search', 'Studies', 'Types'] }" />
        <!-- end facets -->
      </div>

      <div class="col-md-8">
        <div class="navbar">
          <!-- search bar -->
          <data-search
            componentId="Search"
            :dataField="['name', 'title', 'author', 'abstract']"
            iconPosition="right"
            :autosuggest="true"
            :highlight="true"
            :URLParams="true"
            :showClear="true"
            placeholder="Search for publications"
          />
          <selected-filters />
        </div>
        <!-- navbar -->

        <reactive-list
          componentId="SearchResult"
          data-field="_score"
          :pagination="true"
          URLParams="true"
          :from="0"
          :size="10"
          :showResultStats="false"
          class="result-list-container"
          :react="{ and: ['Studies', 'Search', 'Types', 'Years'] }"
        >
          <div slot="renderData" class="book-content" slot-scope="{ item }">
            <div class="card">
              <div class="card-body">
                <p class="card-title"><i class="fa fa-book"></i>
                <a :href="baseUrl + '/' + item._type + '/' + item._id">
                {{ item.title }}
                </a>
                </p>
                <p class="card-text">Publication by: {{ item.author }} ({{ item.year }})</p>
              </div>
            </div>
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

export default {
  name: "PublicationSearch",
  data: function() {
    return {
      baseUrl: window.location.origin,
      /* workaround until nginx proxy is ready */

      /* This is in development mode */
      // searchUrl: "http://localhost:9200",
      // index: "publications",

      /* This is used in test cases */
      searchUrl: "http://elasticsearch:9200",
      index: "testing_publications",
    };
  },
  components: {
    StudyFacet,
    PublicationTypeFacet,
    PublicationYearFacet,
  }
};
</script>

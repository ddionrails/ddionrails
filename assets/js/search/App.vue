<template>
  <div id="app">
    <section>
      <h1>Search</h1>
      <ul class="nav nav-tabs">
        <li>
          <router-link class="nav-link" to="/all">All</router-link>
        </li>
        <li>
          <router-link class="nav-link" to="/variables">
            <i class="fa fa-chart-bar"></i>
            Variables
          </router-link>
        </li>
        <li>
          <router-link class="nav-link" to="/concepts">
            <i class="fa fa-cog"></i>
            Concepts
          </router-link>
        </li>
        <li>
          <router-link class="nav-link" to="/questions">
            <i class="fa fa-tasks"></i>
            Questions
          </router-link>
        </li>
        <li>
          <router-link class="nav-link" to="/publications">
            <i class="fa fa-newspaper"></i>
            Publications
          </router-link>
        </li>
        <li>
          <router-link class="nav-link" to="/topics">
            <i class="fa fa-cogs"></i>
            Topics
          </router-link>
        </li>
        <li v-if="showStatistics">
          <router-link class="nav-link" to="/statistics">
            <i class="fa fa-chart-line"></i>
            Statistics
          </router-link>
        </li>
      </ul>
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
const searchUrl = window.location.origin + "/elastic/";
const showStatistics = process.env.SHOW_STATISTICS === "True";

export default {
  data() {
    return {
      searchUrl,
      showStatistics,
    };
  },
  async mounted(props) {
    await this.$nextTick();
    this.languageObserver = new MutationObserver((mutations) => {
      mutations.forEach((record) => {
        if (record.type == "attributes") {
          const target = record.target;
          if (
            target.nodeName == "BUTTON" &&
            target.hasAttribute("data-current-language")
          ) {
            this.$language = target.getAttribute("data-current-language");
            this.$forceUpdate();
          }
        }
      });
    });

    this.languageElement = document.getElementById("language-switch");
    this.languageObserver.observe(this.languageElement, {
      attributes: true,
    });
  },
  watch: {
    $language() {
      console.log("BBBBBBBBBBBBBBBBB");
      this.$forceUpdate();
    },
  },
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.css-m1gst5 {
  margin-top: 1em;
  width: 100%;
  padding: 0;
}

.card {
  margin-top: 0.5em;
}

p.card-title {
  font-size: 1.2em;
}

.result-list-container {
}

.css-bbs1vb {
  margin: 0 0.5em 0 0.5em;
  padding: 0 0 0.5em 0;
}

/* Search bar */
.css-5xkrhe {
  height: 3em;
}

/* Navigation tabs */
.nav-tabs .nav-link {
  border: 1px solid #dedede;
  border-top-left-radius: 1rem;
  border-top-right-radius: 1rem;
  background-color: #f8f9fa;
  color: grey;
  border-bottom: none;
}

/* Active router link */
.router-link-active {
  border-top-color: #656464 !important;
  border-right-color: #656464 !important;
  border-bottom-color: #e8e7e7 !important;
  border-left-color: #656464 !important;
  border-bottom-color: #dee2e6 !important;
  background-color: white !important;
  color: black !important;
  border-width: 0.1rem !important;
}

/* Highlighting */
mark {
  background-color: #ffeb00 !important;
  border: 1px solid #e0ca00;
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

/* Aligns the search icon vertically */
.css-1fkcgpx {
  top: 0.5em !important;
}

.facet-container {
  padding-left: 0;
}

.facet-container > .facet > .css-bbs1vb {
  margin-left: 0.5em;
}

/* Scroll horizontally when facets contain long labels */
ul.css-bbs1vb {
  white-space: nowrap;
}
.css-xn4gp3 + label::before {
  min-width: 15px;
}
</style>

/**
 * Router for search user interface.
 *
 * @author: Heinz-Alexander Fütterer, Dominique Hansen
 * @copyright: 2019 Heinz-Alexander Fütterer, Dominique Hansen (DIW Berlin)
 * @license: AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0.
 *  See LICENSE at the Github
 *  [reporitory](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 *  or at
 *  https://www.gnu.org/licenses/agpl-3.0.txt
 */

import Vue from "vue";
import Router from "vue-router";
import BaseSearch from "./components/searches/BaseSearch.vue";
import ConceptSearch from "./components/searches/ConceptSearch.vue";
import PublicationSearch from "./components/searches/PublicationSearch.vue";
import QuestionSearch from "./components/searches/QuestionSearch.vue";
import TopicSearch from "./components/searches/TopicSearch.vue";
import VariableSearch from "./components/searches/VariableSearch.vue";
import StatisticsSearch from "./components/searches/StatisticsSearch.vue";

Vue.use(Router);

const language = Vue.observable({
  language: document
    .getElementById("language-switch")
    .getAttribute("data-current-language"),
});

Vue.prototype.$language = document
  .getElementById("language-switch")
  .getAttribute("data-current-language");

Object.defineProperty(Vue.prototype, "$language", {
  get() {
    return language.language;
  },
  set(value) {
    language.language = value;
  },
});

const languageObserver = new MutationObserver((mutations) => {
  mutations.forEach((record) => {
    if (record.type == "attributes") {
      const target = record.target;
      if (
        target.nodeName == "BUTTON" &&
        target.hasAttribute("data-current-language")
      ) {
        Vue.prototype.$language = target.getAttribute("data-current-language");
      }
    }
  });
});

const languageElement = document.getElementById("language-switch");
languageObserver.observe(languageElement, {
  attributes: true,
});


const router = new Router({
  mode: "history",
  base: "/search/",
  routes: [
    {
      path: "/",
      redirect: {name: "base"},
    },
    {
      path: "/all",
      name: "base",
      component: BaseSearch,
    },
    {
      path: "/variables",
      name: "variables",
      component: VariableSearch,
    },
    {
      path: "/concepts",
      name: "concepts",
      component: ConceptSearch,
    },
    {
      path: "/publications",
      name: "publications",
      component: PublicationSearch,
    },
    {
      path: "/questions",
      name: "questions",
      component: QuestionSearch,
    },
    {
      path: "/topics",
      name: "topics",
      component: TopicSearch,
    },
    {
      path: "/statistics",
      name: "statistics",
      component: StatisticsSearch,
    },
  ],
});

/**
 * beforeEach is implemented to retain query parameters between routes.
 */
router.beforeEach((to, _from, next) => {
  // window.location.search has spaces encoded using +
  // to.fullPath has them encoded with %20.
  // To avoid chaining decode encode, we just replace + with the proper
  // encoding.
  const reroute = to.path + window.location.search
    .replace(/\+/g, "%20").replace(/%2C/g, ",");

  // We don't want to go where we are already going.
  // This would cause an infinite regress.
  if (decodeURI(to.fullPath) !== decodeURI(reroute)) {
    next(reroute);
    return null;
  }
  next();
});

export default router;

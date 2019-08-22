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

Vue.use(Router);

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
  const reroute = to.path + window.location.search.replace(/\+/g, "%20");

  // We don't want to go where we are already going.
  // This would cause an infinite regress.
  if (to.fullPath != reroute) {
    next(reroute);
    return null;
  }
  next();
});

export default router;

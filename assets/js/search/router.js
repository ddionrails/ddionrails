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

router.beforeEach((to, _from, next) => {
  const isEqual = require("lodash.isequal");
  const clone = require("lodash.clone");

  const urlParams = new URLSearchParams(window.location.search);

  const query = {};

  // Save the current query and pass it to the next search
  for (const key of urlParams.keys()) {
    // eslint-disable-next-line security/detect-object-injection
    query[key] = urlParams.get(key);
  }

  const reroute = clone(to);
  reroute.query = query;

  if (
    !isEqual(to, reroute)
  ) {
    next(reroute);
    return null;
  }
  next();
});

export default router;

import Vue from "vue";
import Router from "vue-router";
import PublicationSearch from "./components/searches/PublicationSearch.vue";

Vue.use(Router);

export default new Router({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      name: "base",
    },
    {
      path: "/search/publications",
      name: "publications",
      component: PublicationSearch
    }
  ]
});

import Vue from "vue";
import ReactiveSearch from "@appbaseio/reactivesearch-vue";
import App from "./App.vue";
import router from "./router";

Vue.use(ReactiveSearch);
Vue.config.productionTip = false;

new Vue({
  router,
  render: (h) => h(App),
}).$mount("#app");

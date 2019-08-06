/**
 * Entrypoint for search user interface.
 *
 * @author: Heinz-Alexander Fütterer
 * @copyright: 2019 Heinz-Alexander Fütterer (DIW Berlin)
 * @license: AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0.
 *  See LICENSE at the Github
 *  [reporitory](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 *  or at
 *  https://www.gnu.org/licenses/agpl-3.0.txt
 */
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

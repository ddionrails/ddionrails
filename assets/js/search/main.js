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

/**
 * The result-list container of a search page contains a p node with text like:
 * "x results found in yms". Elasticsearch 7 by default only returns
 * 10,000 as result count if the number of results exceeds 10,000.
 * To avoid confusion for users, it should be indicated, that the actual number
 * above 10,000. The following observer is supposed to watch the text node and
 * add "Over " to the start of it if displays "10000".
 * The message should display a message like "Over 10000 results found in yms".
 */
const resultObserver = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.target.data.includes("10000")) {
      if (! mutation.target.data.includes("Over")) {
        mutation.target.data = "Over " + mutation.target.data;
      }
    }
  });
});

window.onload = function() {
  // Observe the result text, after page is loaded.
  resultObserver.observe(document.querySelector("p.css-1e7votj"), {
    attributes: true,
    characterData: true,
    childList: true,
    subtree: true,
    attributeOldValue: true,
    characterDataOldValue: true,
  });
};
// End of observer declaration.

new Vue({
  router,
  render: (h) => h(App),
}).$mount("#app");

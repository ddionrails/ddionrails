/**
 * @author: Dominique Hansen
 * @copyright: 2019 Dominique Hansen (DIW Berlin)
 * @license: AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0.
 *  See LICENSE at the Github
 *  [reporitory](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 *  or at
 *  https://www.gnu.org/licenses/agpl-3.0.txt
*/


/**
 * Returns the index name depending on the state of the PREFIX envvar.
 *
 * This is used to separate standard use indices from test indices.
 * It is intended to be altered during the build by webpack.
 *
 * @param {string} baseName Base part of the index name
 * @return {string} Full name of the index to be used.
 */
export function indexNameSwitch(baseName) {
  if (typeof process.env.ELASTICSEARCH_DSL_INDEX_PREFIX !== "undefined") {
    return process.env.ELASTICSEARCH_DSL_INDEX_PREFIX + baseName;
  } else {
    return baseName;
  }
}


/**
 * Customizes the result text displayed after a search.
 *
 * Elasticsearch by default only returns 10000 results.
 * Other sections of the UI do however show numbers greater than 10000
 * for the number of entities inside the search index.
 * This dissonance in numbers could be confusing.
 * To make it more clear, that more than 10000 results exist, the message
 * is customized here to say "More than 10000 results found ...", instead of
 * "10000 results found ...".
 *
 * The Vue instance passes itself to this function in order to create a VueNode.
 * This is needed since the content returned by this function is left as is.
 * It's not wrapped into the same DOM, element the standard text is wrapped in.
 * So we need to create this VueNode ourselves to keep the original styling
 * given to the class `css-1e7votj`.
 *
 * @param {object} vueInstance Vue instance from which this function is called.
 * @param {object} stats Contains quantitative data about the search results.
 * @return {VNode} A paragraph VNode with the result text.
 */
export function customRenderStats(vueInstance, stats) {
  return vueInstance.$createElement("p", {
    "class": "css-1e7votj",
  },
  [
    stats.totalResults>=10000?"More than ":"",
    stats.totalResults,
    " results found in ",
    stats.time,
    "ms",
  ]);
};

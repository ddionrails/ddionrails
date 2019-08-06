/**
 * Returns the index name depending on the state of the PREFIX envvar.
 *
 * This is used to separate standard use indices from test indices.
 * It is intended to be altered during the build by webpack.
 *
 * @author: Dominique Hansen
 * @copyright: 2019 Dominique Hansen (DIW Berlin)
 * @license: AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0.
 *  See LICENSE at the Github
 *  [reporitory](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 *  or at
 *  https://www.gnu.org/licenses/agpl-3.0.txt
 *
 * @param {string} baseName base part of the index name
 * @return {string} Full name of the index to be used.
 */
export function indexNameSwitch(baseName) {
  if (typeof process.env.ELASTICSEARCH_DSL_INDEX_PREFIX !== "undefined") {
    return process.env.ELASTICSEARCH_DSL_INDEX_PREFIX + baseName;
  } else {
    return baseName;
  }
}

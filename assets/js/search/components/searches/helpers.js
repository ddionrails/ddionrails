/**
 * Returns the index name depending on the state of the PREFIX envvar.
 *
 * @author: Dominique Hansen
 * @param {string} baseName base part of the index name
 * @return {object} Containing index attribute
 */
export function indexNameSwitch(baseName) {
  if (typeof process.env.ELASTICSEARCH_DSL_INDEX_PREFIX !== "undefined") {
    return process.env.ELASTICSEARCH_DSL_INDEX_PREFIX + baseName;
  } else {
    return baseName;
  }
}

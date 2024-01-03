

/**
 * Set up observer to switch language content
 * @param {HTMLElement} component
 */
async function setLanguageObserver(component) {
  const languageObserver = new MutationObserver((mutations) => {
    mutations.forEach((record) => {
      if (record.type == "attributes") {
        const target = record.target;
        if (
          target.nodeName == "BUTTON" &&
            target.hasAttribute("data-current-language")
        ) {
          component.$language = target.getAttribute("data-current-language");
          component.$forceUpdate();
        }
      }
    });
  });

  const languageElement = document.getElementById("language-switch");
  languageObserver.observe(languageElement, {
    attributes: true,
  });
}

/**
 * Return label or fallback according to language
 * @param {object} item
 * @param {str} language
 * @return {str}
 */
function getLabelWithFallback(item, language) {
  let label = item.label;
  if (item.label_de != "") {
    if (language == "de" || label =="") {
      label = item.label_de;
    }
  }
  if (label == "") {
    if (language == "de") {
      label = "Nicht angegeben";
    } else {
      label = "Not defined";
    }
  }
  return label;
}

export {getLabelWithFallback, setLanguageObserver};

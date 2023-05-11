

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

export {setLanguageObserver};

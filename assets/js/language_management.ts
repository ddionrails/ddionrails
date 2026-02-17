/**
 *
 * @returns
 */
function languageCode() {
  const language = document
    .getElementById("language-switch")
    .getAttribute("data-current-language");
  if (language) {
    return language;
  }
  return "en";
}

/**
 *
 * @returns
 */
function languageConfig() {
  const language = languageCode();
  if (language == "de") {
    return {
      lengthMenu: "Zeige _MENU_ Einträge pro Seite",
      emptyTable: "Tabelle ist leer",
      search: "Suche:",
      zeroRecords: "Keine Suchergebnisse",
      info: "Zeige Einträge _START_ bis _END_ von _TOTAL_",
      infoEmpty: "Keine Einträge vorhanden",
      infoFiltered: "(Auswahl von insgesamt _MAX_ Einträgen)",
      searchPlaceholder: "Alle Spalten durchsuchen",
      paginate: {
        first: "Anfang",
        last: "Ende",
        next: "Weiter",
        previous: "Zurück",
      },
    };
  }

  return {
    searchPlaceholder: "Search all columns",
  };
}

/**
 * Switch language of content.
 */
function switchLanguage(content: HTMLElement, language = "en") {
  const nodes = content.querySelectorAll(`[data-${language}]`);
  nodes.forEach((node) => {
    node.innerHTML = node.getAttribute(`data-${language}`);
  });
  const titleNodes = content.querySelectorAll(`[data-title-${language}]`);
  titleNodes.forEach((node) => {
    node.setAttribute("title", node.getAttribute(`data-title-${language}`));
  });
  content.querySelectorAll(".lang").forEach((node) => {
    node.classList.add("hidden");
  });
  content.querySelectorAll(`.lang.${language}`).forEach((node) => {
    node.classList.remove("hidden");
  });
  document.querySelector("html").setAttribute("lang", language)
}

export {languageCode};
export {languageConfig};
export {switchLanguage};

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
      info: "Zeige Seite _PAGE_ von _PAGES_",
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

export {languageCode};
export {languageConfig};

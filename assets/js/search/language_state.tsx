import {useState} from "react";

// eslint-disable-next-line require-jsdoc
export function getLanguageState() {
  const languageSwitch = document.getElementById("language-switch");

  const [languageState, setLanguage] = useState(
    languageSwitch.getAttribute("data-current-language")
  );

  const languageHandling = (mutationList: MutationRecord[], _: MutationObserver) => {
    for (const mutation of mutationList) {
      if (mutation.type === "attributes") {
        const target: Element = mutation.target as Element;
        setLanguage(target.getAttribute("data-current-language"));
      }
    }
  };
  const observer = new MutationObserver(languageHandling);
  observer.observe(languageSwitch, {attributes: true});
  return languageState;
}

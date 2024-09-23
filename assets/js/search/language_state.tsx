import {useState} from "react";

type LanguageCode = "en" | "de";

// eslint-disable-next-line require-jsdoc
function getLanguageState(): LanguageCode {
  const languageSwitch = document.getElementById("language-switch");

  const [languageState, setLanguage] = useState(
    languageSwitch.getAttribute("data-current-language") as LanguageCode
  );

  const languageHandling = (mutationList: MutationRecord[], _: MutationObserver) => {
    for (const mutation of mutationList) {
      if (mutation.type === "attributes") {
        const target: Element = mutation.target as Element;
        setLanguage(target.getAttribute("data-current-language") as LanguageCode);
      }
    }
  };
  const observer = new MutationObserver(languageHandling);
  observer.observe(languageSwitch, {attributes: true});
  return languageState;
}

export {getLanguageState, LanguageCode}
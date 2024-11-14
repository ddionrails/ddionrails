/* !
 * ddionrails - index.js
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../favicon.ico");

import "bootstrap";
import {switchLanguage} from "./language_management";

// Unhide Warning when using Internet Explorer
const userAgent = window.navigator.userAgent;
const ieTen = userAgent.indexOf("MSIE");
const ieEleven = userAgent.indexOf("Trident/");

if (ieTen > 0 || ieEleven > 0) {
  const warning = document.getElementById("windowsWarning") as HTMLElement;
  warning.classList.remove("hidden");
}

const cardsToHideChildren = document.getElementsByClassName("hide-card");

for (const cardChild of cardsToHideChildren) {
  cardChild.closest(".card").classList.add("hidden");
}

window.addEventListener("load", () => {
  const namespace = document.head.querySelector(
    'meta[name="namespace"]'
  ) as HTMLMetaElement;
  if (namespace !== null) {
    const activeNavLink = document.getElementById(
      `${namespace.content}-nav-link`
    ) as HTMLElement;
    activeNavLink.classList.add("active-nav-link");
  }
  const language = document.getElementById("language-switch");
  switchLanguage(
    document.documentElement,
    language ? language.getAttribute("data-current-language") : "en"
  );
});

const languageSwitch = document.getElementById("language-switch");
languageSwitch.addEventListener("click", (button) => {
  const _switch = button.currentTarget as HTMLElement;
  let language = _switch.getAttribute("data-current-language");
  if (language == "en") {
    language = "de";
  } else {
    language = "en";
  }
  _switch.setAttribute("data-current-language", language);
  switchLanguage(document.documentElement, language);
  document.cookie = `paneldata_language=${language}; path=/`;
});

// BOOTSTRAP 5 tmp fixes:
const navContent = document.querySelector(".navbar-collapse");
navContent.classList.toggle("hidden");

const menueToggle = document.querySelector(".navbar-toggler");
menueToggle.addEventListener("click", (_) => {
  navContent.classList.toggle("hidden");
});

const resizeObserver = new ResizeObserver((entries) => {
  if (entries[0].target.clientWidth < 1200) {
    navContent.classList.add("hidden");
  }
});

// start observing a DOM node
resizeObserver.observe(document.body);

if (window.innerWidth < 1200) {
  navContent.classList.add("hidden");
}



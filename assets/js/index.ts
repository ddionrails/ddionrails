/* !
 * ddionrails - index.js
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../favicon.ico");

// Unhide Warning when using Internet Explorer
const userAgent = window.navigator.userAgent;
const ieTen = userAgent.indexOf("MSIE");
const ieEleven = userAgent.indexOf("Trident/");

if (ieTen > 0 || ieEleven > 0) {
  const warning = document.getElementById("windowsWarning") as HTMLElement;
  warning.classList.remove("hidden");
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
});

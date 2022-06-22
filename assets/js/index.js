/* !
 * ddionrails - index.js
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../scss/index.scss");
require("../favicon.ico");

import "bootstrap";

import {basketButton} from "./basket_button.js";
window.basketButton = basketButton;

// Unhide Warning when using Internet Explorer
const userAgent = window.navigator.userAgent;
const ieTen = userAgent.indexOf("MSIE");
const ieEleven = userAgent.indexOf("Trident/");

if (ieTen > 0 || ieEleven > 0) {
  const warning = document.getElementById("windowsWarning");
  warning.classList.remove("hidden");
}

window.addEventListener("load", function() {
  const namespace = document.head.querySelector('meta[name="namespace"]');
  if (namespace !== null ) {
    const activeNavLink = document.getElementById(`${namespace.content}-nav-link`);
    activeNavLink.classList.add("active-nav-link");
  }
}
);

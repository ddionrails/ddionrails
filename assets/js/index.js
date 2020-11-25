/* !
 * ddionrails - index.js
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../scss/index.scss");
require("../favicon.ico");

import "bootstrap";
import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

// Credit to https://stackoverflow.com/q/44484469
window["jQuery"] = window["$"] = require("jquery");

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
$(window).on("load", function() {
  $(".datatable").dataTable();
}
);

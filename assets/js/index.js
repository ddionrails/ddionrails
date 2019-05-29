/*!
 * ddionrails - index.js
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../scss/index.scss");

import "bootstrap";
import "datatables.net";
import "datatables.net-bs";
import "datatables.net-responsive";
import "datatables.net-responsive-bs";

// Credit to https://stackoverflow.com/q/44484469
window["jQuery"] = window["$"] = require("jquery");

import { basketButton } from "./basket_button.js";
window.basketButton = basketButton;
/*!
 * ddionrails - index.js
 * Copyright 2015-2018
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

require("../scss/index.scss");

import "bootstrap";
import "datatables.net";
import "datatables.net-bs";
import "datatables.net-responsive";
import "datatables.net-responsive-bs";

// Credit to https://github.com/mar10/fancytree/issues/793
import "jquery.fancytree";
import "jquery.fancytree/dist/modules/jquery.fancytree.filter";
import "jquery.fancytree/dist/modules/jquery.fancytree.glyph";

// Credit to https://stackoverflow.com/questions/44484469/access-jquery-when-loaded-via-webpack
window["jQuery"] = window["$"] = require("jquery");

import { basketButton } from "./main.js";
window.basketButton = basketButton;

import "d3";

import {
  margin,
  w,
  h_menu,
  barPadding,
  render,
  resize
} from "ddionrails-visualization";
window.margin = margin;
window.w = w;
window.h_menu = h_menu;
window.barPadding = barPadding;
window.render = render;
window.resize = resize;

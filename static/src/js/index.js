/*!
 * ddionrails - index.js
 * Copyright 2015-2018
 * Licensed under AGPL (https://github.com/mhebing/ddionrails2/blob/master/LICENSE)
*/

require("../scss/index.scss")

import 'bootstrap'
import 'datatables.net';
import 'datatables.net-bs';
import 'datatables.net-responsive';
import 'datatables.net-responsive-bs';

import { basketButton } from './main.js';
window.basketButton = basketButton;

import 'd3';

import { margin, w, h_menu, barPadding, render, resize } from 'ddionrails-visualization';
window.margin = margin;
window.w = w;
window.h_menu = h_menu;
window.barPadding = barPadding;
window.render = render;
window.resize = resize;

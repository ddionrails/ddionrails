/*!
 * ddionrails - main.js
 * Copyright 2015-2018
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

var basketButton = (function() {
  var addVariable = function($button, $count) {
    $.ajax({
      url:
        "/workspace/baskets/" +
        $button.attr("basket_id") +
        "/add/" +
        $button.attr("variable_id"),
      success: function() {
        $button.removeClass("btn-default");
        $button.addClass("btn-success");
      }
    });
  };

  var removeVariable = function($button, $count) {
    $.ajax({
      url:
        "/workspace/baskets/" +
        $button.attr("basket_id") +
        "/remove/" +
        $button.attr("variable_id"),
      success: function() {
        $button.removeClass("btn-success");
        $button.addClass("btn-default");
      }
    });
  };

  var handleButton = function() {
    console.log("hi");
    var $button = $(this);
    var $count = $("#basket-count").first();
    if ($button.hasClass("btn-success")) {
      removeVariable($button, $count);
    } else {
      addVariable($button, $count);
    }
  };

  return function() {
    $("body").on("click", "button.basket-button", handleButton);
  };
})();

$(function() {
  basketButton();
  $(".datatable").DataTable();
});

export { basketButton };

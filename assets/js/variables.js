/**
 * Hide description info card if no description text is present.
 * Copy full description content into a modal otherwise.
 */
$(window).on("load", function() {
  const description=$("#description-card-content");
  if (description.text().trim()==="") {
    description.parent().hide();
    return;
  }
  if (
    description.prop("scrollHeight") - description.prop("clientHeight") <= 1
  ) {
    $("#description-footer").hide();
    return;
  }
  description.clone().appendTo("#description-modal-content");
}

);

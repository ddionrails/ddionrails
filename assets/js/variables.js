/**
 * Hide description info card if no description text is present.
 * Copy full description content into a modal otherwise.
 */
$(function() {
  const description=$("#description-card-content").clone();
  if (description.text().trim()==="") {
    $("#description-card-content").parent().hide();
    return;
  }
  const descriptionModal=$("#description-modal-content");
  description.clone().appendTo(descriptionModal);
}

);

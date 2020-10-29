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

/**
 * When URL contains an anchor:
 * Open tab content of the anchor and focus on the content.
 */
$(window).on("load", function() {
  const href = window.location.href;
  const anchor =href.substr(href.indexOf("#"));
  if ( anchor.length === 1 ) {
    return;
  }
  const anchorLink = $(`a[href$="${anchor}"]`);
  anchorLink[0].click();
  $([document.documentElement, document.body]).animate({
    scrollTop: anchorLink.offset().top - $("#paneldata-navbar").outerHeight(),
  }, 800);
});

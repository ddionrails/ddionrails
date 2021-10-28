
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
  document.querySelector("#relation-tables").scrollIntoView(true);
  window.scrollBy(0, -document.documentElement.clientHeight/4);
});

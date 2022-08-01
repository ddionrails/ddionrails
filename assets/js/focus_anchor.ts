/**
 * When URL contains an anchor:
 * Open tab content of the anchor and focus on the content.
 */
window.addEventListener("load", () => {
  const anchor = window.top.location.hash;
  if (anchor.length === 1) {
    return;
  }
  const anchorLink = document.querySelector(
    `a[href$="${anchor}"]`
  ) as HTMLLinkElement;
  anchorLink.click();
  document.querySelector("#relation-tables").scrollIntoView(true);
  window.scrollBy(0, -document.documentElement.clientHeight / 4);
});

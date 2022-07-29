/**
 * Hide description info card if no description text is present.
 * Copy full description content into a modal otherwise.
 */
window.addEventListener("load", () => {
  const description = document.getElementById("description-card-content");
  if (description.textContent.trim() === "") {
    const parent = description.parentNode as HTMLElement;
    parent.classList.add("hidden");
    return;
  }
  if (
    description.scrollHeight - description.clientHeight <= 1
  ) {
    document.getElementById("description-footer").style.display = "none";
    return;
  }
  const modalDescription = description.cloneNode(true) as HTMLElement;
  modalDescription.removeAttribute("id");
  modalDescription.removeAttribute("class");
  document.getElementById(
    "description-modal-content").append(modalDescription);
});

import {switchLanguage, languageCode} from "./language_management";

/**
 * Hide description info card if no description text is present.
 * Copy full description content into a modal otherwise.
 */
window.addEventListener("load", () => {
  const description = document.getElementById("description-card-content");
  switchLanguage(description, languageCode());
  const modalDescription = document
    .getElementById("description-card-content")
    .cloneNode(true) as HTMLElement;
  const descriptionText = [...description.querySelectorAll(".lang")]
    .map((node) => {
      return node.textContent;
    })
    .join("");
  if (descriptionText === "") {
    return;
  }

  const parent = document.getElementById("description-card") as HTMLElement;
  parent.classList.remove("hidden");
  if (description.scrollHeight - description.clientHeight <= 2) {
    document.getElementById("description-footer").classList.add("hidden");
    return;
  }
  modalDescription.removeAttribute("id");
  modalDescription.removeAttribute("class");
  document.getElementById("description-modal-content").append(modalDescription);
});

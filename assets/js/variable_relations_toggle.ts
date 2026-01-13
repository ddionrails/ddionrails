export type ToggleType = "input" | "output" | "sibling" | "concept";
type ToggleId =
  | "input-relation-toggle"
  | "output-relation-toggle"
  | "sibling-relation-toggle"
  | "sibling-relation-toggle"
  | "concept-relation-toggle";
const toggleClasses: Set<ToggleId> = new Set([
  "input-relation-toggle",
  "output-relation-toggle",
  "sibling-relation-toggle",
  "sibling-relation-toggle",
  "concept-relation-toggle",
]);

function hideToggleClass() {
  const activeButtons = document.querySelectorAll(
    "#relations-buttons-container > .active.btn:not([disabled])",
  );
  const activeIDs = [...activeButtons].map((button) => `.${button.id}`);
  const activeSelector = `:is(${activeIDs.join(", ")})`;
  for (const relatedVariable of document.querySelectorAll(
    ".related-variable-container",
  )) {
    relatedVariable.classList.add("invisible");
  }
  for (const relatedVariableIcon of document.querySelectorAll(
    ".related-variable-container > i",
  )) {
    relatedVariableIcon.classList.add("invisible");
  }

  for (const active of document.querySelectorAll(activeSelector)) {
    active.classList.remove("invisible");
  }
}

export function addClickEventHandler() {
  for (const toggleClass of toggleClasses) {
    const button = document.getElementById(toggleClass);
    button.addEventListener("click", (target) => {
      (target.currentTarget as HTMLElement).classList.toggle("active");
      hideToggleClass();
    });
  }
}

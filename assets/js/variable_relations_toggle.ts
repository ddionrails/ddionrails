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
  const activeSelector =
    `.related-variable-container` +
    `:is(${activeIDs.join(", ")})`
  for (const relataedVariable of document.querySelectorAll(".related-variable-container")) {
    relataedVariable.classList.add("hidden");
  }
  for (const active of document.querySelectorAll(activeSelector)) {
    active.classList.remove("hidden");
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

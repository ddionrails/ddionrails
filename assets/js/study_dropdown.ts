function createStudyDropdownClickListener() {
  const studyDropdown = document.getElementById("study-dropdown");
  studyDropdown.addEventListener("click", () => {
    studyDropdown.parentElement.classList.toggle("clicked")
    document.addEventListener(
      "click",
      (event) => {
        if (event.target != studyDropdown) {
          studyDropdown.parentElement.classList.remove("clicked");
        }
      },
      { once: true, capture: true},
    );
  });
}

document.addEventListener("DOMContentLoaded", () => {
  createStudyDropdownClickListener();
});

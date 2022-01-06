
const oursQuestion = document.getElementById("ours-question");
const theirsQuestion = document.getElementById("theirs-question");
/**
 * Duplicate primary dropdown to select both ours and theirs in diff.
 */
function duplicateDropdown() {
  const primaryQuestionDropdown = document.getElementById("primary-dropdown-menu");
  const secondaryQuestionDropdown = primaryQuestionDropdown.cloneNode(true);
  secondaryQuestionDropdown.id = "secondary-dropdown-menu";
  const questionItems = secondaryQuestionDropdown.querySelectorAll(
    ".ours-question-dropdown-item"
  );
  for (
    const questionItem of questionItems
  ) {
    questionItem.classList.replace(
      "ours-question-dropdown-item", "theirs-question-dropdown-item"
    );
  }
  primaryQuestionDropdown.parentElement.appendChild(secondaryQuestionDropdown);
}

/**
 *
 * @param {*} listenerTarget
 * @param {*} changedQuestion
 */
function setEventListener(listenerTarget, changedQuestion) {
  listenerTarget.addEventListener("click", (event) => {
    const questionDiffModalContent = document.getElementById(
      "diff-table-container");
    const apiURL = new URL(`${window.location.origin}/api/question-comparison`);
    const request = new XMLHttpRequest();
    const diffApiUrl = new URL(apiURL);
    changedQuestion.textContent = event.currentTarget.getAttribute("data-id");

    diffApiUrl.searchParams.append(
      "questions",
      `${oursQuestion.textContent},${theirsQuestion.textContent}`
    );

    request.open("GET", diffApiUrl, true);

    request.onload = (_) => {
      if (request.readyState ===4) {
        if (request.status === 200) {
          questionDiffModalContent.innerHTML = request.responseText;

          questionDiffModalContent.querySelector(".diff").classList.add("table");
        }
      }
    };

    request.send(null);
  });
}

export {duplicateDropdown, setEventListener, oursQuestion, theirsQuestion};

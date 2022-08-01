const oursQuestion = document.getElementById("ours-question");
const theirsQuestion = document.getElementById("theirs-question");

const compareButton = document.createElement("button") as HTMLButtonElement;
const compareIcon = document.createElement("i");
compareIcon.classList.add("fa");
compareIcon.classList.add("fa-exchange-alt");
compareButton.appendChild(compareIcon);
compareButton.classList.add("btn");
compareButton.classList.add("btn-link");
compareButton.title = "Compare Question";

const mainQuestion = document.getElementById("question-id").textContent;

/**
 * Duplicate primary dropdown to select both ours and theirs in diff.
 */
function duplicateDropdown() {
  const primaryQuestionDropdown = document.getElementById(
    "primary-dropdown-menu"
  ) as HTMLElement;
  const secondaryQuestionDropdown = primaryQuestionDropdown.cloneNode(
    true
  ) as HTMLElement;
  secondaryQuestionDropdown.id = "secondary-dropdown-menu";
  const questionItems = Array.from(
    secondaryQuestionDropdown.querySelectorAll(".ours-question-dropdown-item")
  ) as Array<HTMLElement>;
  for (const questionItem of questionItems) {
    questionItem.classList.replace(
      "ours-question-dropdown-item",
      "theirs-question-dropdown-item"
    );
  }
  primaryQuestionDropdown.parentElement.appendChild(secondaryQuestionDropdown);
}

/**
 *
 * @param {*} eventListenerTarget
 * @param {*} changedQuestion
 */
function setComparisonDropdownEventListener(
  eventListenerTarget: HTMLElement,
  changedQuestion: HTMLElement
) {
  eventListenerTarget.addEventListener("click", (event) => {
    const questionDiffModalContent = document.getElementById(
      "diff-table-container"
    );
    const apiURL = new URL(`${window.location.origin}/api/question-comparison`);
    const request = new XMLHttpRequest();
    const diffApiUrl = new URL(apiURL);
    const targetDropdown = event.currentTarget as HTMLButtonElement;
    changedQuestion.textContent = targetDropdown.getAttribute("data-id");

    diffApiUrl.searchParams.append(
      "questions",
      `${oursQuestion.textContent},${theirsQuestion.textContent}`
    );

    request.open("GET", diffApiUrl, true);

    request.onload = (_) => {
      if (request.readyState === 4) {
        if (request.status === 200) {
          questionDiffModalContent.innerHTML = request.responseText;
          // Pythons difflib replaces all spaces with non breakable spaces.
          // This cannot be changed in the difflib function.
          // It is reverted here to make the text wrap properly.
          // Iteration through cells is necessary.
          // Substitution in responseText breaks the diff.
          const textCells =
            questionDiffModalContent.querySelectorAll("td[nowrap=nowrap]");
          textCells.forEach((cell) => {
            cell.innerHTML = cell.innerHTML.replace(/&nbsp;/g, " ");
          });

          questionDiffModalContent
            .querySelector(".diff")
            .classList.add("table");
        }
      }
    };

    request.send(null);
  });
}

const oursQuestionDropdownItems = Array.from(
  document.getElementsByClassName("ours-question-dropdown-item")
) as Array<HTMLElement>;
const theirsQuestionDropdownItems = Array.from(
  document.getElementsByClassName("theirs-question-dropdown-item")
) as Array<HTMLElement>;
const relatedQuestionLinks = Array.from(
  document.getElementsByClassName("related-question-link")
) as Array<HTMLLinkElement>;

duplicateDropdown();

for (const questionLink of Array.from(relatedQuestionLinks)) {
  const relatedQuestionLinkDiff = compareButton.cloneNode(
    true
  ) as HTMLButtonElement;
  questionLink.parentNode.insertBefore(
    relatedQuestionLinkDiff,
    questionLink.nextSibling
  );
  const id = questionLink.href.substring(
    questionLink.href.lastIndexOf("/") + 1
  );
  relatedQuestionLinkDiff.setAttribute("data-id", id);

  oursQuestion.textContent = mainQuestion;

  relatedQuestionLinkDiff.addEventListener("click", (event) => {
    document.getElementById("show-question-diff").click();
  });
  setComparisonDropdownEventListener(relatedQuestionLinkDiff, theirsQuestion);
}

for (const questionItem of oursQuestionDropdownItems) {
  setComparisonDropdownEventListener(questionItem, oursQuestion);
}

for (const questionItem of theirsQuestionDropdownItems) {
  setComparisonDropdownEventListener(questionItem, theirsQuestion);
}

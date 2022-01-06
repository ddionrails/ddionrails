import {
  duplicateDropdown,
  oursQuestion,
  setEventListener,
  theirsQuestion,
} from "./question_comparison_functions";

const compareButton = document.createElement("button");
const compareIcon = document.createElement("i");
compareIcon.classList.add("fa");
compareIcon.classList.add("fa-exchange-alt");
compareButton.appendChild(compareIcon);
compareButton.classList.add("btn");
compareButton.classList.add("btn-link");
compareButton.title = "Compare Question";

const mainQuestion = document.getElementById("question-id").textContent;

const oursQuestionDropdownItems = document.getElementsByClassName(
  "ours-question-dropdown-item"
);
const theirsQuestionDropdownItems = document.getElementsByClassName(
  "theirs-question-dropdown-item"
);
const relatedQuestionLinks = document.getElementsByClassName("related-question-link");

duplicateDropdown();

for ( const questionLink of relatedQuestionLinks) {
  const relatedQuestionLinkDiff = compareButton.cloneNode(true);
  questionLink.parentNode.insertBefore(relatedQuestionLinkDiff, questionLink.nextSibling);
  const id = questionLink.href.substring(questionLink.href.lastIndexOf("/")+1);
  relatedQuestionLinkDiff.setAttribute("data-id", id);

  oursQuestion.textContent = mainQuestion;

  relatedQuestionLinkDiff.addEventListener("click", (event) => {
    document.getElementById("show-question-diff").click();
  });
  setEventListener(relatedQuestionLinkDiff, theirsQuestion);
}

for ( const questionItem of oursQuestionDropdownItems) {
  setEventListener(questionItem, oursQuestion);
}


for ( const questionItem of theirsQuestionDropdownItems) {
  setEventListener(questionItem, theirsQuestion);
}

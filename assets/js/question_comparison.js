/**
 * Add event listeners to compare the question of this page to related questions.
 */

const compareButton = document.createElement("button");
const compareIcon = document.createElement("i");
compareIcon.classList.add("fa");
compareIcon.classList.add("fa-not-equal");
compareButton.appendChild(compareIcon);
compareButton.classList.add("btn");
compareButton.classList.add("btn-link");
compareButton.title = "Compare Question";


const apiURL = new URL(`${window.location.origin}/api/question-comparison`);
const questionDiffModalContent = document.getElementById(
  "question-diff-modal-content");

const thisQuestion = document.getElementById("question-id").textContent;

const relatedQuestionItems = document.getElementsByClassName("related-question-item");

for ( questionItem of relatedQuestionItems) {
  questionItem.addEventListener("click", (target) => {
    // document.getElementById("show-question-diff").click();

    const request = new XMLHttpRequest();
    const diffApiUrl = new URL(apiURL);
    diffApiUrl.searchParams.append(
      "questions",
      `${thisQuestion},${target.srcElement.id}`
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


const relatedQuestionLinks = document.getElementsByClassName("related-question-link");

for ( questionLink of relatedQuestionLinks) {
  const relatedQuestionLinkDiff = compareButton.cloneNode(true);
  questionLink.parentNode.insertBefore(relatedQuestionLinkDiff, questionLink.nextSibling);
  const id = questionLink.href.substring(questionLink.href.lastIndexOf("/")+1);
  relatedQuestionLinkDiff.id = id;

  relatedQuestionLinkDiff.addEventListener("click", (target) => {
    document.getElementById("show-question-diff").click();

    const request = new XMLHttpRequest();
    const diffApiUrl = new URL(apiURL);
    diffApiUrl.searchParams.append(
      "questions",
      `${thisQuestion},${target.currentTarget.id}`
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

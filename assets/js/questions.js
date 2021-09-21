
const itemBlocks = JSON.parse(document.getElementById("question-meta").textContent);
const itemHTMLContainer = document.getElementById("question-items");

console.log(itemBlocks);

/**
 * Render an item block containing simple text.
 * @param {*} itemBlock item block object
 * @return {document.blockNode} A p node with the item text
 */
function renderTXT(itemBlock) {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const text = document.createElement("p");
  element.appendChild(text);
  element.classList.add("question-item-text");
  let content = itemBlock[0]["label"];
  content = content.replace(/\n/g, "<br />");
  text.innerHTML = content;
  return (element);
}

/**
 * Render a categorical block with only a single item
 * @param {*} itemBlock
 * @return {document.blockNode}
 */
function renderCATSingle(itemBlock) {
  const element = document.createElement("div");
  element.classList.add("item-block");
  questionText = document.createElement("p");
  questionText.classList.add("question-item-text");
  questionText.textContent = itemBlock["label"];
  element.appendChild(questionText);
  const answers = document.createElement("div");
  answers.classList.add("form-check");
  element.appendChild(answers);
  for ( const answer of itemBlock["answers"]) {
    const answerElement = document.createElement("label");
    answers.appendChild(answerElement);
    const radioButton = document.createElement("input");
    answerElement.appendChild(radioButton);
    radioButton.type = "radio";
    radioButton.disabled = true;
    const answerText = document.createElement("text");
    answerElement.appendChild(answerText);
    answerText.textContent = answer["label"];
    answerText.classList.add("item-answer-text");
  }


  return (element);
}

/**
 * Render a categorical block with only a multiple items
 * @param {*} itemBlock
 * @return {document.blockNode}
 */
function renderCATMultiple(itemBlock) {
  const element = document.createElement("div");
  element.classList.add("item-block");

  return (element);
}


for (const itemBlock of itemBlocks) {
  let blockNode;
  if (itemBlock[0]["scale"] === "txt") {
    blockNode = renderTXT(itemBlock);
  }
  if (itemBlock[0]["scale"] === "cat") {
    if (itemBlock.length === 1 ) {
      blockNode = renderCATSingle(itemBlock[0]);
    } else {
      blockNode = renderCATMultiple(itemBlock);
    }
  }
  itemHTMLContainer.appendChild(blockNode);
  itemHTMLContainer.appendChild(document.createElement("hr"));
}

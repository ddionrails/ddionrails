const itemBlocks = JSON.parse(
  document.getElementById("question-meta").textContent
);
const itemHTMLContainers = {
  en: document.getElementById("question-items"),
  de: document.getElementById("question-items-de"),
};

console.log(itemBlocks);

/**
 *
 * @return {document.Node} Font awesome icon for input information.
 */
function inputFilterIcon() {
  const icon = document.createElement("i");
  icon.classList.add("far");
  icon.classList.add("fa-sign-in-alt");
  return icon;
}

/**
 *
 * @return {document.Node} Font awesome icon for goto information.
 */
function gotoIcon() {
  const icon = document.createElement("i");
  icon.classList.add("far");
  icon.classList.add("fa-sign-out-alt");
  return icon;
}

/**
 *
 * @param {*} item One element of an itemBlock
 * @param {*} language Language of the label to retrieve
 * @return {document.Node}
 */
function getLabel(item, language = "en") {
  let labelKey = "label";
  if (language === "de") {
    labelKey = "label_de";
  }
  const labelContainer = document.createElement("text");
  const labelContent = document.createElement("text");
  labelContent.innerHTML = item[`${labelKey}`].replace(/\n/g, "<br />");

  if ("input_filter" in item && item["input_filter"] != "") {
    const inputFilter = inputFilterIcon();
    inputFilter.setAttribute("title", item["input_filter"]);
    labelContainer.appendChild(inputFilterIcon());
  }
  labelContainer.appendChild(labelContent);
  if ("goto" in item && item["goto"] != "") {
    const goto = gotoIcon();
    goto.setAttribute("title", item["goto"]);
    labelContainer.appendChild(goto);
  }
  return labelContainer;
}

/**
 * Render an item block containing simple text.
 * @param {*} itemBlock item block object
 * @param {*} language language of the item to create
 * @return {document.Node} A p node with the item text
 */
function renderTXT(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const text = document.createElement("p");
  element.appendChild(text);
  element.classList.add("question-item-text");
  text.appendChild(getLabel(itemBlock[0], language));
  return element;
}

/**
 * Render a categorical block with only a single item
 * @param {*} itemBlock
 * @param {*} language language of the item to create
 * @return {document.blockNode}
 */
function renderCATSingle(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  questionText = document.createElement("p");
  questionText.classList.add("question-item-text");
  questionText.appendChild(getLabel(itemBlock[0], language));
  element.appendChild(questionText);
  const answers = document.createElement("div");
  answers.classList.add("form-check");
  element.appendChild(answers);
  for (const answer of itemBlock[0]["answers"]) {
    const answerElement = document.createElement("label");
    answers.appendChild(answerElement);
    const radioButton = document.createElement("input");
    answerElement.appendChild(radioButton);
    radioButton.type = "radio";
    radioButton.disabled = true;
    const answerText = document.createElement("text");
    answerElement.appendChild(answerText);
    answerText.appendChild(getLabel(answer, language));
    answerText.classList.add("item-answer-text");
  }

  return element;
}

/**
 * Create a table row from an array
 * @param {*} content Cell content.
 * @param {*} header If row should be a header row
 * @return {document.Node} A table row.
 */
function renderTableRow(content, header = false) {
  const row = document.createElement("tr");
  let baseCell = undefined;
  if (header) {
    baseCell = document.createElement("th");
  } else {
    baseCell = document.createElement("td");
  }

  for (const data of content) {
    const cell = baseCell.cloneNode();
    if (typeof data == "string") {
      cell.innerHTML = data;
    } else {
      cell.appendChild(data);
    }
    row.appendChild(cell);
  }
  return row;
}

/**
 * Render a categorical block with only a multiple items
 * @param {*} itemBlock
 * @param {*} language language of the item to create
 * @return {document.blockNode}
 */
function renderCATMultiple(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const answers = itemBlock[0].answers;
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  let row = [""].concat(answers.map((answer) => getLabel(answer, language)));
  table.appendChild(renderTableRow(row, (header = true)));

  const radioButton = document.createElement("input");
  radioButton.type = "radio";
  radioButton.disabled = true;

  for (const item of itemBlock) {
    row = [getLabel(item, language)];
    for (
      let answerPosition = 0;
      answerPosition < answers.length;
      answerPosition++
    ) {
      row.push(radioButton.cloneNode());
    }
    table.appendChild(renderTableRow(row));
  }

  return element;
}

/**
 * Render a numerical block with multiple items
 * @param {*} itemBlock
 * @param {*} language language of the item to create
 * @return {document.blockNode}
 */
function renderINT(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  const intContainer = document.createElement("div");
  intContainer.classList.add("item-input-container");
  const itemInput = document.createElement("input");
  itemInput.type = "number";
  itemInput.placeholder = "123";
  itemInput.disabled = true;
  const icon = document.createElement("i");
  icon.classList.add("fas");
  icon.classList.add("fa-hashtag");
  intContainer.appendChild(itemInput);
  intContainer.appendChild(icon);

  for (const item of itemBlock) {
    row = [getLabel(item, language), intContainer.cloneNode(true)];
    table.appendChild(renderTableRow(row));
  }

  return element;
}

/**
 * Render a numerical block with multiple items
 * @param {*} itemBlock
 * @param {*} language language of the item to create
 * @return {document.blockNode}
 */
function renderCHR(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  const chrContainer = document.createElement("div");
  chrContainer.classList.add("item-input-container");
  const itemInput = document.createElement("input");
  itemInput.type = "text";
  itemInput.placeholder = "abc";
  itemInput.disabled = true;
  const icon = document.createElement("i");
  icon.classList.add("fas");
  icon.classList.add("fa-pencil-alt");
  chrContainer.appendChild(itemInput);
  chrContainer.appendChild(icon);

  for (const item of itemBlock) {
    row = [getLabel(item, language), chrContainer.cloneNode(true)];
    table.appendChild(renderTableRow(row));
  }

  return element;
}

/**
 * Render a numerical block with multiple items
 * @param {*} itemBlock
 * @param {*} language language of the item to create
 * @return {document.blockNode}
 */
function renderBIN(itemBlock, language = "en") {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  const container = document.createElement("div");
  container.classList.add("item-checkbox-container");
  const itemInput = document.createElement("input");
  itemInput.type = "checkbox";
  itemInput.disabled = true;
  container.appendChild(itemInput);

  for (const item of itemBlock) {
    row = [getLabel(item, language), container.cloneNode(true)];
    table.appendChild(renderTableRow(row));
  }

  return element;
}

for (const itemBlock of itemBlocks) {
  let blockNode;
  for (const language of ["en", "de"]) {
    if (itemBlock[0]["scale"] === "txt") {
      blockNode = renderTXT(itemBlock, language);
    }
    if (itemBlock[0]["scale"] === "cat") {
      if (itemBlock.length === 1) {
        blockNode = renderCATSingle(itemBlock, language);
      } else {
        blockNode = renderCATMultiple(itemBlock, language);
      }
    }
    if (itemBlock[0]["scale"] === "int") {
      blockNode = renderINT(itemBlock, language);
    }
    if (itemBlock[0]["scale"] === "chr") {
      blockNode = renderCHR(itemBlock, language);
    }
    if (itemBlock[0]["scale"] === "bin") {
      blockNode = renderBIN(itemBlock, language);
    }
    if (["en", "de"].includes(language)) {
      itemHTMLContainers[`${language}`].appendChild(blockNode);
      itemHTMLContainers[`${language}`].appendChild(
        document.createElement("hr")
      );
    }
  }
}

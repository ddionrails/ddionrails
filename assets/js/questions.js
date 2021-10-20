let language = "en";
const itemBlocks = JSON.parse(
  document.getElementById("question-meta").textContent
);
const itemHTMLContainers = {
  en: document.getElementById("question-items"),
  de: document.getElementById("question-items-de"),
};

const hashIcon = document.createElement("i");
hashIcon.classList.add("fas");
hashIcon.classList.add("fa-hashtag");

const pencilIcon = document.createElement("i");
pencilIcon.classList.add("fas");
pencilIcon.classList.add("fa-pencil-alt");

const scaleMetadata = {
  int: {
    inputAttributes: {type: "number", placeholder: "123"},
    icon: hashIcon,
  },
  chr: {
    inputAttributes: {type: "text", placeholder: "abc"},
    icon: pencilIcon,
  },
  bin: {inputAttributes: {type: "checkbox"}},
};

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

const getLabelString = (item, labelKey) => {
  let prefix = item["value"] || "";
  if (prefix !== "") {
    prefix = `[${prefix}] `;
  }
  const label =item[`${labelKey}`].replace(/\n/g, "<br />");
  return `${prefix}${label}`;
};

const addLabelIcons = (item, labelContainer, languageKey) => {
  const instructionKey = `instruction${languageKey}`;
  if (Boolean(item["input_filter"])) {
    const inputFilter = inputFilterIcon();
    inputFilter.setAttribute("title", item["input_filter"]);
    labelContainer.prepend(inputFilter);
  }
  if (Boolean(item[`${instructionKey}`])) {
    const infoIcon = document.createElement("i");
    infoIcon.classList.add("fas");
    infoIcon.classList.add("fa-info-circle");
    infoIcon.setAttribute("title", item[`${instructionKey}`]);
    labelContainer.appendChild(infoIcon);
  }
  if (Boolean(item["goto"])) {
    const goto = gotoIcon();
    goto.setAttribute("title", item["goto"]);
    labelContainer.appendChild(goto);
  }
};

/**
 *
 * @param {*} item One element of an itemBlock
 * @return {document.Node}
 */
function getLabel(item) {
  let languageKey = "";
  if (language === "de") {
    languageKey = "_de";
  }
  const labelContainer = document.createElement("text");
  const labelContent = document.createElement("text");
  labelText = item["value"] || "";
  labelContent.innerHTML = getLabelString(item, `label${languageKey}`);

  labelContainer.appendChild(labelContent);
  addLabelIcons(item, labelContainer, languageKey);
  return labelContainer;
}


/**
 * Render an item block containing simple text.
 * @param {*} itemBlock item block object
 * @return {document.Node} A p node with the item text
 */
function renderTXT(itemBlock) {
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
 * @return {document.blockNode}
 */
function renderCATSingle(itemBlock) {
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
    const table = document.createElement("table");
    table.classList.add("answers-table");
    const radioButton = document.createElement("input");
    const inputContainer = document.createElement("div");
    inputContainer.classList.add("item-input-container");
    radioButton.type = "radio";
    radioButton.disabled = true;
    inputContainer.appendChild(radioButton);
    const answerText = document.createElement("text");
    answerText.appendChild(getLabel(answer, language));
    answerText.classList.add("item-answer-text");
    table.appendChild(renderTableRow([answerText, inputContainer]));
    answers.appendChild(table);
  }

  return element;
}


/**
 * Render a categorical block with only a multiple items
 * @param {*} itemBlock
 * @return {document.blockNode}
 */
function renderCATMultiple(itemBlock) {
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
 * @param {*} itemBlock Array of question items
 * @param {*} inputAttributes object with subset of input element attributes
 * @param {*} inputIcon icon to put into the input field
 * @return {document.blockNode}
 */
function renderLines(itemBlock, inputAttributes, inputIcon) {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  const itemContainer = document.createElement("div");
  itemContainer.classList.add("item-input-container");
  const itemInput = Object.assign(
    document.createElement("input"),
    inputAttributes,
    {
      disabled: true,
    }
  );
  itemContainer.appendChild(itemInput);
  if (typeof inputIcon !== "undefined") {
    itemContainer.appendChild(inputIcon);
  }

  for (const item of itemBlock) {
    row = [getLabel(item, language), itemContainer.cloneNode(true)];
    table.appendChild(renderTableRow(row));
  }

  return element;
}

for (const itemBlock of itemBlocks) {
  let blockNode;
  const blockScale = itemBlock[0]["scale"];
  for (const code of ["en", "de"]) {
    language = code;
    if (blockScale === "txt") {
      blockNode = renderTXT(itemBlock);
    } else if (blockScale === "cat") {
      if (itemBlock.length === 1) {
        blockNode = renderCATSingle(itemBlock);
      } else {
        blockNode = renderCATMultiple(itemBlock);
      }
    } else {
      blockNode = renderLines(
        itemBlock,
        scaleMetadata[`${blockScale}`]["inputAttributes"],
        scaleMetadata[`${blockScale}`]["icon"]
      );
    }
    if (["en", "de"].includes(language)) {
      itemHTMLContainers[`${language}`].appendChild(blockNode);
      itemHTMLContainers[`${language}`].appendChild(
        document.createElement("hr")
      );
    }
  }
}

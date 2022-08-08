type Answer = {
  value: number;
  label: string;
  label_de: string;
};

type QuestionItem = {
  name: string;
  scale: string;
  label: string;
  label_de: string;
  text: string;
  text_de: string;
  description: string;
  description_de: string;
  instruction: string;
  instruction_de: string;
  position: number;
  input_filter: string;
  goto: string;
  answers: Array<Answer>;
};
type QuestionItemBlocks = Array<Array<QuestionItem>>;
type languageCode = "en" | "de";

const languageSpecificContainers = [
  {
    language: "en" as languageCode,
    container: document.getElementById("question-items"),
  },
  {
    language: "de" as languageCode,
    container: document.getElementById("question-items-de"),
  },
];

/**
 * Read question item data from the page.
 * @return {QuestionItemBlocks}
 */
function readItemBlockData(): QuestionItemBlocks {
  const questionMeta = document.getElementById("question-meta");
  if (questionMeta === null || questionMeta.textContent === null) {
    return [[{}]] as QuestionItemBlocks;
  }
  return JSON.parse(questionMeta.textContent) as QuestionItemBlocks;
}

const createGotoIcon = (): HTMLElement => {
  const icon = document.createElement("i");
  icon.classList.add("fa-solid");
  icon.classList.add("fa-right-from-bracket");
  return icon;
};

const createHashIcon = (): HTMLElement => {
  const icon = document.createElement("i");
  icon.classList.add("fas");
  icon.classList.add("fa-hashtag");
  return icon;
};

const createPencilIcon = (): HTMLElement => {
  const icon = document.createElement("i");
  icon.classList.add("fas");
  icon.classList.add("fa-pencil-alt");
  return icon;
};

const createInputFilterIcon = (): HTMLElement => {
  const icon = document.createElement("i");
  icon.classList.add("fas");
  icon.classList.add("fa-right-to-bracket");
  return icon;
};

const createRadioButton = (): HTMLInputElement => {
  const radioButton = document.createElement("input");
  radioButton.type = "radio";
  radioButton.disabled = true;
  return radioButton;
};

enum RowType {
  Header = "th",
  Row = "td",
}

/**
 * Create a table row from an array
 * @param {*} content Cell content.
 * @param {*} rowType If row should be a header or normal row
 * @return {document.Node} A table row.
 */
function renderTableRow(
  content: Array<HTMLElement>,
  rowType: "th" | "td" = RowType.Row
): HTMLTableRowElement {
  const row = document.createElement("tr");

  for (const data of content) {
    const cell = document.createElement(rowType);
    if (typeof data == "string") {
      cell.innerHTML = data;
    } else {
      cell.appendChild(data);
    }
    row.appendChild(cell);
  }
  return row;
}

const getLabelWithValue = (item: Answer, labelKey: string): string => {
  const labelPart = labelKey === "de" ? item.label_de : item.label;
  if (labelPart === "") {
    return "";
  }
  let prefix = "";
  if (typeof item["value"] === "number") {
    prefix = `[${item["value"]}] `;
  }
  const label = prefix + labelPart.replace(/\n/g, "<br />");
  return label;
};

const addInputAndGotoIcons = (
  item: QuestionItem,
  labelContainer: HTMLElement,
  languageCode: string
) => {
  let instruction = item["instruction"];
  if (languageCode === "de") {
    instruction = item["instruction_de"];
  }

  if (Boolean(item["input_filter"])) {
    const thisInputFilter = createInputFilterIcon();
    thisInputFilter.setAttribute("title", item["input_filter"]);
    labelContainer.prepend(thisInputFilter);
  }
  if (Boolean(instruction)) {
    const infoIcon = document.createElement("i");
    infoIcon.classList.add("fas");
    infoIcon.classList.add("fa-info-circle");
    infoIcon.setAttribute("title", instruction);
    labelContainer.appendChild(infoIcon);
  }
  if (Boolean(item["goto"])) {
    const goto = createGotoIcon();
    goto.setAttribute("title", item["goto"]);
    labelContainer.appendChild(goto);
  }
};

/**
 *
 * @param {Answer} item One element of an itemBlock
 * @param {languageCode} itemLanguage
 * @return {HTMLElement}
 */
function getMinimalLabel(
  item: Answer,
  itemLanguage: languageCode
): HTMLElement {
  const labelContainer = document.createElement("text");
  const labelContent = document.createElement("text");
  labelContent.innerHTML = getLabelWithValue(item, itemLanguage);

  labelContainer.appendChild(labelContent);
  return labelContainer;
}

const createLabelContainer = (text: string) => {
  const labelContainer = document.createElement("text");
  const labelContent = document.createElement("text");
  labelContent.innerHTML = text;

  labelContainer.appendChild(labelContent);
  return labelContainer;
};

/**
 *
 * @param {QuestionItem} item
 * @param {languageCode} itemLanguage
 * @return {HTMLElement}
 */
function getLabelWithInputAndGoto(
  item: QuestionItem,
  itemLanguage: languageCode
): HTMLElement {
  const label = itemLanguage === "de" ? item.label_de : item.label;

  const labelContainer = createLabelContainer(label.replace(/\n/g, "<br />"));

  addInputAndGotoIcons(item, labelContainer, itemLanguage);
  return labelContainer;
}

/**
 * Render an item block containing simple text.
 * @param {Array<QuestionItem>} itemBlock item block object
 * @param {languageCode} language
 * @return {Node} A p node with the item text
 */
function renderTXT(
  itemBlock: Array<QuestionItem>,
  language: languageCode
): HTMLDivElement {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const text = document.createElement("p");
  element.appendChild(text);
  element.classList.add("question-item-text");
  text.appendChild(getLabelWithInputAndGoto(itemBlock[0], language));
  return element;
}

/**
 * Render a categorical block with only a single item
 * @param {Array<QuestionItem>} itemBlock
 * @param {languageCode} language
 * @return {HTMLDivElement}
 */
function renderCATSingle(
  itemBlock: Array<QuestionItem>,
  language: languageCode
) {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const questionText = document.createElement("p");
  questionText.classList.add("question-item-text");
  questionText.appendChild(getLabelWithInputAndGoto(itemBlock[0], language));
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
    answerText.appendChild(getMinimalLabel(answer, language));
    answerText.classList.add("item-answer-text");
    table.appendChild(renderTableRow([answerText, inputContainer]));
    answers.appendChild(table);
  }

  return element;
}

/**
 * Render a categorical block with only a multiple items
 * @param {Array<QuestionItem>} itemBlock
 * @param {languageCode} language
 * @return {HTMLDivElement}
 */
function renderCATMultiple(
  itemBlock: Array<QuestionItem>,
  language: languageCode
): HTMLDivElement {
  const blockContainer = document.createElement("div");
  blockContainer.classList.add("item-block");
  const answerCategories = itemBlock[0].answers;
  const table = document.createElement("table");
  table.classList.add("answers-table");
  blockContainer.appendChild(table);

  // Upper left corner of the matrix has no text
  const header = [document.createElement("text")];
  header.push(
    ...answerCategories.map((category) => getMinimalLabel(category, language))
  );
  table.appendChild(renderTableRow(header, RowType.Header));

  for (const item of itemBlock) {
    let labelContainer;
    if (language === "de") {
      labelContainer = createLabelContainer(item["label_de"]);
    } else {
      labelContainer = createLabelContainer(item["label"]);
    }

    const row = [labelContainer];
    for (
      let answerPosition = 0;
      answerPosition < answerCategories.length;
      answerPosition++
    ) {
      row.push(createRadioButton());
    }
    table.appendChild(renderTableRow(row));
  }

  return blockContainer;
}

/**
 * Create a disabled Input field to visualize the type of a QuestionItem
 * @param {string} type
 * @return {HTMLInputElement}
 */
function createInputTypeVisualization(type: string): Array<HTMLElement> {
  const inputElement = document.createElement("input");
  inputElement.setAttribute("disabled", "");
  const typeVisualizationElements = new Array<HTMLElement>(2);
  typeVisualizationElements.push(inputElement);

  if (type === "int") {
    inputElement.setAttribute("type", "number");
    inputElement.setAttribute("placeholder", "123");
    typeVisualizationElements.push(createHashIcon());
  }
  if (type === "chr") {
    inputElement.setAttribute("type", "text");
    inputElement.setAttribute("placeholder", "abc");
    typeVisualizationElements.push(createPencilIcon());
  }
  if (type === "bin") {
    inputElement.setAttribute("type", "checkbox");
  }
  return typeVisualizationElements;
}

/**
 * Render lines of a Block of items of type chr, bin or int
 * @param {Array} itemBlock Array of question items
 * @param {string} blockScaleType object with subset of input element attributes
 * @param {string} blockLanguage icon to put into the input field
 * @return {document.blockNode}
 */
function renderLines(
  itemBlock: Array<QuestionItem>,
  blockScaleType: "bin" | "chr" | "int",
  blockLanguage: languageCode
) {
  const element = document.createElement("div");
  element.classList.add("item-block");
  const table = document.createElement("table");
  table.classList.add("answers-table");
  element.appendChild(table);

  const inputTypeVisualization = () => {
    const typeVisualizationElements = document.createElement("div");
    typeVisualizationElements.classList.add("item-input-container");

    for (const element of createInputTypeVisualization(blockScaleType)) {
      typeVisualizationElements.appendChild(element);
    }
    return typeVisualizationElements;
  };

  for (const item of itemBlock) {
    const row = [
      getLabelWithInputAndGoto(item, blockLanguage),
      inputTypeVisualization(),
    ];
    table.appendChild(renderTableRow(row));
  }
  return element;
}

const renderAllItems = () => {
  for (const itemBlock of readItemBlockData()) {
    let blockContentElement;
    const blockScale = itemBlock[0]["scale"];
    for (const languageContainer of languageSpecificContainers) {
      if (blockScale === "txt") {
        blockContentElement = renderTXT(itemBlock, languageContainer.language);
      }
      if (blockScale === "cat") {
        if (itemBlock.length === 1) {
          blockContentElement = renderCATSingle(
            itemBlock,
            languageContainer.language
          );
        } else {
          blockContentElement = renderCATMultiple(
            itemBlock,
            languageContainer.language
          );
        }
      }
      if (["chr", "int", "bin"].includes(blockScale)) {
        blockContentElement = renderLines(
          itemBlock,
          blockScale as "bin" | "chr" | "int",
          languageContainer.language
        );
      }
      languageContainer.container.appendChild(blockContentElement);
      languageContainer.container.appendChild(document.createElement("hr"));
      const hideMissingLanguageContent = (container: HTMLElement) => {
        if (container.textContent.trim() === "") {
          container.parentElement.classList.add("hidden");
        }
      };
      hideMissingLanguageContent(languageContainer.container);
    }
  }
};

renderAllItems();

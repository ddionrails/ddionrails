interface RelatedQuestionItem {
  id: string;
  name: string;
  label: string;
  label_de: string;
  question: string;
  question_name: string;
  question_label: string;
  question_label_de: string;
  instrument: string;
  instrument_name: string;
  study_name: string;
  study_label: string;
  period_name: string;
  study: string;
}

const API_ENDPOINT = `${window.location.origin}/api/question_items/`;
const SIDEBAR_LIMIT = 10;

const VARIABLE_ID =
  document.head.querySelector<HTMLMetaElement>('meta[name="id"]')!.content;

async function getRelatedQuestionItems(): Promise<RelatedQuestionItem[]> {
  var url: URL = new URL(API_ENDPOINT);
  if (!VARIABLE_ID) {
    return [];
  }
  url.searchParams.set("variable_id", VARIABLE_ID);
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  const content = await response.json();
  if (!content?.count || !content?.results || content?.count == 0) {
    return [];
  }
  return content.results;
}

async function fillRelatedQuestionItems() {
  const content = await getRelatedQuestionItems();
  if (content.length == 0) {
    return;
  }
  const listContainer = document.getElementById("related-questions-short-list");
  content.sort(sortElementByPeriodDesc);

  let sidebarLimiter = 0;

  for (const element of content) {
    if (sidebarLimiter < SIDEBAR_LIMIT) {
      const listElement = document.createElement("li");
      listElement.appendChild(createQuestionItemLink(element));
      listContainer.appendChild(listElement);
    }
    sidebarLimiter = sidebarLimiter + 1;
    createTableRow(element);
  }
  if (sidebarLimiter > SIDEBAR_LIMIT) {
    listContainer.appendChild(document.createTextNode("..."));
  }
}

function sortElementByPeriodDesc(
  a: RelatedQuestionItem,
  b: RelatedQuestionItem,
) {
  if (!isNaN(parseInt(a.period_name)) && !isNaN(parseInt(b.period_name))) {
    let diff = parseInt(b.period_name) - parseInt(a.period_name);
    if (diff != 0) {
      return diff;
    }
    return subSortByInstrumentName(a, b);
  }
  if (a.period_name < b.period_name) {
    return 1;
  }
  if (a.period_name > b.period_name) {
    return -1;
  }
  return subSortByInstrumentName(a, b);
}

function subSortByInstrumentName(
  a: RelatedQuestionItem,
  b: RelatedQuestionItem,
) {
  if (a.instrument_name < b.instrument_name) {
    return -1;
  }
  if (a.instrument_name > b.instrument_name) {
    return 1;
  }
  return 0;
}

//TODO: Handle the question_label == item_label situation in a more central way, by

function selectLanguageLabel(
  item: RelatedQuestionItem,
  language: string,
): string[] {
  if (language == "de") {
    if (item.label_de != item.question_label_de) {
      return [item.label_de, item.question_label_de];
    }
    return [item.label_de];
  }
  if (item.label != item.question_label) {
    return [item.label, item.question_label];
  }
  return [item.label];
}

function createQuestionItemLink(item: RelatedQuestionItem) {
  const loadingLanguage = document
    .getElementById("language-switch")
    .getAttribute("data-current-label");
  const linkContainer = document.createElement("a");
  const url = `${window.location.origin}/question/${item.question}`;
  linkContainer.href = url;
  var linkText = `${item.period_name}: `;
  const innerText =
    linkText + selectLanguageLabel(item, loadingLanguage).join(" - ");
  linkContainer.innerText = innerText;
  linkContainer.setAttribute(
    "data-en",
    linkText + selectLanguageLabel(item, "en").join(" - "),
  );
  linkContainer.setAttribute(
    "data-de",
    linkText + selectLanguageLabel(item, "de").join(" - "),
  );
  return linkContainer;
}

function createQuestionLink(
  item: RelatedQuestionItem,
  loadingLanguage: string,
) {
  const linkContainer = document.createElement("a");
  const url = `${window.location.origin}/question/${item.question}`;
  linkContainer.href = url;
  if (loadingLanguage === "de") {
    linkContainer.innerText = item.question_label_de;
  } else {
    linkContainer.innerText = item.question_label;
  }
  linkContainer.setAttribute("data-en", item.question_label);
  linkContainer.setAttribute("data-de", item.question_label_de);
  return linkContainer;
}

function createTableRow(item: RelatedQuestionItem) {
  const rowCell = document.createElement("th");
  rowCell.setAttribute("scope", "row");
  const loadingLanguage = document
    .getElementById("language-switch")
    .getAttribute("data-current-label");

  const tableBody = document.getElementById("question-item-table-body");
  const tableRow = document.createElement("tr");
  tableBody.appendChild(tableRow);

  const periodCell = rowCell.cloneNode() as HTMLElement;
  periodCell.innerText = item.period_name;

  const instrumentCell = rowCell.cloneNode() as HTMLElement;
  instrumentCell.appendChild(instrumentLink(item));

  const itemCell = rowCell.cloneNode() as HTMLElement;
  const itemLabel = selectLanguageLabel(item, loadingLanguage);
  const itemLabelContainer = document.createElement("span");
  if (itemLabel.length == 1) {
    itemLabelContainer.innerHTML = "&horbar;";
  } else {
    itemLabelContainer.innerHTML = itemLabel[0];
    itemLabelContainer.setAttribute("data-en", item.label);
    itemLabelContainer.setAttribute("data-de", item.label_de);
  }
  itemCell.appendChild(itemLabelContainer);

  const questionCell = rowCell.cloneNode() as HTMLElement;
  questionCell.appendChild(createQuestionLink(item, loadingLanguage));

  tableRow.append(...[periodCell, instrumentCell, itemCell, questionCell]);
}

function instrumentLink(question: RelatedQuestionItem) {
  const link = document.createElement("a");
  link.innerText = question.instrument_name;
  link.href = `${window.location.origin}/instrument/${question.instrument}`;
  return link;
}

window.addEventListener("load", () => {
  fillRelatedQuestionItems();
});

import { ToggleType } from "./variable_relations_toggle";

type Variable = {
  id: string;
  name: string;
  period_name: string;
};

type ConceptVariables = Array<Variable>;

const variableRerouteUrl = `${window.location.origin}/variable/`;

const ConceptIconClasses = [
  "fa",
  "fa-cog",
  "concept-icon",
  "concept-relation-toggle",
];

const ConceptIconTooltipText: Map<languageCode, string> = new Map([
  ["en", "Is part of the same concept"],
  ["de", "Gehört zum selben Konzept"],
]);

export function createIcon(
  classNames: Array<string>,
  languageLabels: Map<languageCode, string>,
): HTMLElement {
  const languageSwitch = document.getElementById("language-switch");
  let language = languageSwitch.getAttribute(
    "data-current-language",
  ) as languageCode;

  const inputIcon = document.createElement("i");
  inputIcon.classList.add(...classNames);
  inputIcon.title = languageLabels.get(language);

  const mutationCallback = (mutationList: Array<any>, _: any) => {
    for (const mutation of mutationList) {
      if (mutation.type == "attributes") {
        language = languageSwitch.getAttribute(
          "data-current-language",
        ) as languageCode;
        inputIcon.title = languageLabels.get(language);
      }
    }
  };
  const observer = new MutationObserver(mutationCallback);
  observer.observe(languageSwitch, { attributes: true });

  return inputIcon;
}

export function enableRelationToggleButton(relationType: ToggleType) {
  let buttonID = `${relationType}-relation-toggle`;
  document.getElementById(buttonID).removeAttribute("disabled");
}

function getConceptAPIURL() {
  const studyMeta = document.querySelector('meta[name="study"]');
  const studyName =
    studyMeta instanceof HTMLMetaElement ? studyMeta.content : "";

  const conceptMeta = document.querySelector('meta[name="concept"]');
  const conceptName =
    conceptMeta instanceof HTMLMetaElement ? conceptMeta.content : "";
  if (conceptName == "") {
    return "";
  }
  enableRelationToggleButton("concept");

  const query = `?study=${studyName}&concept=${conceptName}`;
  return `${window.location.origin}/api/variables/${query}`;
}

/**
 * Sort numerical strings and strings
 * Sort:
 * Numerical strings in front of non-numerical strings
 * Two non-numerical strings as strings
 * Two numerical strings as numbers
 * */
export function sortPotentialNumeric(a: string | number, b: string | number) {
  const aInt = typeof a == "string" ? parseInt(a) : a;
  const bInt = typeof b == "string" ? parseInt(b) : b;

  if (!isNaN(aInt) && isNaN(bInt)) {
    return -1;
  }
  if (isNaN(aInt) && !isNaN(bInt)) {
    return 1;
  }

  if (isNaN(aInt) && isNaN(bInt)) {
    if (a < b) {
      return -1;
    }
    if (a > b) {
      return 1;
    }
    return 0;
  }
  if (aInt < bInt) {
    return -1;
  }
  if (aInt > bInt) {
    return 1;
  }
  return 0;
}

export function initPeriodContainer(period: string) {
  const periodContainer = document.createElement("div");
  periodContainer.classList.add("period-container");
  periodContainer.setAttribute("data-period-name", period);
  const periodHeader = document.createElement("div");
  periodHeader.classList.add("related-period-header");
  periodHeader.textContent = period + ":";
  periodContainer.appendChild(periodHeader);
  return periodContainer;
}

/**
 * Add period containers coming in from the concept variables
 */
function insertMissingPeriodContainersToDOM(variables: ConceptVariables) {
  const conceptPeriods = new Set(
    variables.map((entry) => {
      return entry.period_name;
    }),
  );

  const existingPeriodContainers = [
    ...document.querySelectorAll(".period-container"),
  ];
  const existingPeriods = new Set(
    existingPeriodContainers.map((entry) => {
      return entry.getAttribute("data-period-name");
    }),
  );

  // Uses Set to remove potential duplicates
  const allPeriods = [...new Set([...existingPeriods, ...conceptPeriods])];
  const allPeriodsSorted = allPeriods.sort(sortPotentialNumeric);

  const relationsContainer = document.querySelector(
    "#variable-relations > .card-body",
  ) as HTMLElement;

  // Check if period container exists and
  // if it doesn't exists insert it after existing container
  // Handle first element separately since we cannot insert it after anything
  if (!existingPeriods.has(allPeriodsSorted[0])) {
    relationsContainer.prepend(initPeriodContainer(allPeriodsSorted[0]));
    existingPeriods.add(allPeriodsSorted[0]);
  }
  for (let index = 1; index < allPeriodsSorted.length; index++) {
    const period = allPeriodsSorted[index];
    const lastPeriod = allPeriodsSorted[index - 1];
    if (!existingPeriods.has(period)) {
      document
        .querySelector(`div[data-period-name='${lastPeriod}']`)
        .after(initPeriodContainer(period));
    }
  }
}

export function createVariableContainer(variable: Variable) {
  const variableContainer = document.createElement("div");
  variableContainer.classList.add("related-variable-container");

  const variableLink = document.createElement("a");
  variableLink.innerText = variable.name;
  variableLink.href = variableRerouteUrl + variable.id;

  variableContainer.appendChild(variableLink);
  variableContainer.setAttribute("data-variable-name", variable.name);
  return variableContainer;
}

const ConceptIcon = createIcon(ConceptIconClasses, ConceptIconTooltipText);
/**
 * Add concept icon to existing variables and add concept-only variables
 */
export async function addConceptVariables() {
  const apiURL = getConceptAPIURL();

  fetch(apiURL).then((response) => {
    response.json().then((json: ConceptVariables) => {
      insertMissingPeriodContainersToDOM(json);

      for (const variable of json) {
        const periodContainer = document.querySelector(
          `div[data-period-name='${variable.period_name}']`,
        ) as HTMLElement;
        let variableContainer = document.querySelector(
          `div[data-period-name='${variable.period_name}']` +
            ` > div[data-variable-name='${variable.name}']`,
        );

        if (!variableContainer) {
          variableContainer = createVariableContainer(variable);
          periodContainer.appendChild(variableContainer);
        }

        variableContainer.classList.add("concept-relation-toggle");
        enableRelationToggleButton("concept");
        variableContainer.appendChild(ConceptIcon.cloneNode());
      }
    });
  });
}

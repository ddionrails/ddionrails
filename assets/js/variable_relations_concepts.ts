import { ToggleType } from "./variable_relations_toggle";

type Variable = {
  id: string;
  name: string;
  period_name: string;
};

type VariableList = Array<Variable>;

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

export function enableToggle(relationType: ToggleType) {
  let buttonID = `${relationType}-relation-toggle`;
  document.getElementById(buttonID).removeAttribute("disabled");
}

function getAPIURL() {
  const studyMeta = document.querySelector('meta[name="study"]');
  const studyName =
    studyMeta instanceof HTMLMetaElement ? studyMeta.content : "";

  const conceptMeta = document.querySelector('meta[name="concept"]');
  const conceptName =
    conceptMeta instanceof HTMLMetaElement ? conceptMeta.content : "";
  if (conceptName == "") {
    return "";
  }
  enableToggle("concept");

  const query = `?study=${studyName}&concept=${conceptName}`;
  return `${window.location.origin}/api/variables/${query}`;
}

export async function addConceptToVariables() {
  const apiURL = getAPIURL();

  fetch(apiURL).then((response) => {
    response.json().then((json: VariableList) => {
      for (const variable of json) {
        const variableContainer = document.querySelector(
          `div[data-period-name='${variable.period_name}']` +
            ` > div[data-variable-name='${variable.name}']`,
        );
        if (!variableContainer) {
          continue;
        }
        variableContainer.classList.add("concept-relation-toggle");
        enableToggle("concept");
        const conceptIcon = createIcon(
          ["fa", "fa-cog", "concept-icon"],
          new Map([
            ["en", "Is part of the same concept"],
            ["de", "Gehört zum selben Konzept"],
          ]),
        );
        variableContainer.appendChild(conceptIcon);
      }
    });
  });
}

import {Variable} from "./types";

type topicLeaveMetadata = {
  label: string;
  children: Array<string>;
  children_de: Array<string>;
};

type topicLeaveResponse = {
  [id: string]: topicLeaveMetadata;
};

export function renderVariableStatisticsLink(
  variable: any,
  type: string,
): HTMLElement {
  const linkElement = document.createElement("a");
  linkElement.setAttribute("data-en", variable["label"])
  linkElement.setAttribute("data-de", variable["label_de"])
  if (document.querySelector("html").getAttribute("lang") === "de") {
    linkElement.textContent = variable["label_de"];
  } else {
    linkElement.textContent = variable["label"];
  }
  const url = new URL(window.location.href + `${type}/`);
  url.searchParams.append("variable", variable["id"]);

  linkElement.href = url.toString();
  return linkElement;
}

function nestIntoList(element: Element) {
  const listElement = document.createElement("li")
  listElement.appendChild(element)
  return listElement
}


//TODO: Look into refactoring language handling
/**
 * 
 */
export async function setUpSubTopics(
  variableMetadata: Array<Variable>,
  topicName: string,
  containerNode: Element
) {
  const language = document.querySelector("html").getAttribute("lang");
  const study: string = variableMetadata[0]["study_name"];
  const apiURL = new URL(window.location.origin + "/api/topic-leaves");
  apiURL.searchParams.append("study", study);
  apiURL.searchParams.append("topic", topicName);

  const response = await fetch(apiURL);
  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }
  const data: topicLeaveResponse =
    (await response.json()) as topicLeaveResponse;
  const topicToVariableMap: Map<string, Array<Element>> = new Map();
  const translationMap: Map<string, string> = new Map();
  let index = 0;
  for (const child of data[topicName]["children"]) {
    topicToVariableMap.set(child, new Array());
    translationMap.set(child, data[topicName]["children_de"][index])
    index = index + 1;
  }
  for (const variable of variableMetadata) {
    for (const topic of variable["topics"]) {
      if (topicToVariableMap.has(topic)) {
        topicToVariableMap
          .get(topic)
          .push(
            renderVariableStatisticsLink(variable, variable["statistics_type"]),
          );
      }
    }
  }


  for (const topicKey of topicToVariableMap.keys()) {
    if (topicToVariableMap.get(topicKey).length === 0) {
      continue
    }
    const subTopicHeaderListElement = document.createElement("li")
    const subTopicHeader = document.createElement("h4")

    subTopicHeader.textContent = topicKey
    if (language === "de") {
      subTopicHeader.textContent = translationMap.get(topicKey)
    }
    subTopicHeader.setAttribute("data-de", translationMap.get(topicKey))
    subTopicHeader.setAttribute("data-en", topicKey)

    subTopicHeaderListElement.appendChild(subTopicHeader)
    containerNode.appendChild(subTopicHeaderListElement)
    const variableLinks = topicToVariableMap.get(topicKey).map((variableLink) => nestIntoList(variableLink))
    variableLinks.map((element) => containerNode.appendChild(element))



  }

  return containerNode;
}

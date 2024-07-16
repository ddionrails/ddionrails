/**
 *
 */
export async function setUpSubTopics() {
  const apiCall: URL = new URL(window.location.origin);
  let value: string | undefined = "";

  const request = new XMLHttpRequest();
  // apiCall.searchParams.append("topic", topicName);
  // apiCall.searchParams.append("study", apiMetadata["study"]);
  // apiCall.searchParams.append("statistics", "True");
  // apiCall.searchParams.append("paginate", "False");
  request.open("GET", apiCall, true);
  request.responseType = "json";

  const response = await fetch(apiCall);
  return await response.json();
}

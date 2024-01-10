import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

document.getElementById("app").innerHTML = "SEARCH";


const connector = new ElasticsearchAPIConnector({
  host: window.location.hostname + "/elastic/",
  index: "variables",
});

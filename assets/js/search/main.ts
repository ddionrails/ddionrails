import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {createElement} from "react";
import ReactDOM from "react-dom";

const connector = new ElasticsearchAPIConnector({
  host: window.location.hostname + "/elastic/",
  index: "variables",
});

ReactDOM.render(
  createElement("h1", {className: "HEADER"}, "SEARCH"),
  document.getElementById("app")
);

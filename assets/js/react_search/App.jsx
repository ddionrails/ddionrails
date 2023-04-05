import React from "react";
import { ReactiveBase, DataSearch } from "@appbaseio/reactivesearch";

function SearchApp() {
  return (
    <ReactiveBase
      url={window.location.origin + "/elastic/"}
      app="elasticsearch"
      credentials="viewer_anonymous:"
      enableAppbase={false}
    >
      Hello Placeholder 👋
    </ReactiveBase>
  );
}

export default SearchApp;

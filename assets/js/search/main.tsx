import {createRoot} from "react-dom/client";
import ReactDOM from "react-dom";

import App from "./app";

const domNode = document.getElementById("app");
const root = createRoot(domNode);
ReactDOM.render(<App />, document.getElementById("app"));

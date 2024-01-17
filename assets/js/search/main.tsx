import {createRoot} from "react-dom/client";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

import App from "./app";

const domNode = document.getElementById("app");
const root = createRoot(domNode);
root.render(<App />);

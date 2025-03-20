import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// Resources importing

import "./css/index.css";
import App from "./App.tsx";

// Setup the react dom root

const container = document.getElementById("root");

if (container) {
    const root = createRoot(container);
    root.render(
        <StrictMode>
            <App />
        </StrictMode>,
    );
} else {
    console.error("Root container missing in HTML.");
}

// As per:
// https://vite.dev/guide/backend-integration.html

if (import.meta.env.MODE !== "development") {
    // @ts-expect-error
    import("vite/modulepreload-polyfill");
}

import { useState, type FC } from "react";

// Resources importing

import websiteLogo from "/favicon.svg?url";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./css/App.css";

// Component definition

const App: FC = () => {
    const [count, setCount] = useState(0);

    return (
        <>
            <meta name="description" content="Music Analyser created using react, vite and django." />
            <link rel="icon" type="image/svg+xml" href={websiteLogo} />
            <div>
                <a href="https://vite.dev" target="_blank">
                    <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank">
                    <img src={reactLogo} className="logo react" alt="React logo" />
                </a>
            </div>
            <h1>Vite + React</h1>
            <div className="card">
                <button onClick={() => setCount((count) => count + 1)}>count is {count}</button>
                <p>
                    Edit <code>src/App.tsx</code> and save to test HMR
                </p>
            </div>
            <p className="read-the-docs">Click on the Vite and React logos to learn more</p>
        </>
    );
};

export default App;

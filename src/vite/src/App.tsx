// As per:
// https://vite.dev/guide/backend-integration.html

if (import.meta.env.MODE !== "development") {
    // @ts-expect-error
    import("vite/modulepreload-polyfill");
}

import { FormEvent, useEffect, useState, type FC } from "react";

// Resources importing

import websiteLogo from "/favicon.svg?url";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./css/App.css";

// Component definition

const App: FC = () => {
    const [name, setName] = useState("");
    const [welcomeText, setWelcomeText] = useState("");

    const [displaced, setDisplaced] = useState(true);

    const fullText = "Bienvenue";

    useEffect(() => {
        let i = 0;

        const blinkingUnderscoreFoo = () => {
            if (name !== "") {
                clearInterval(interval);
                return;
            }

            setWelcomeText(fullText + (i % 2 == 0 ? "_" : ""));
            i++;
        };

        let interval = setInterval(() => {
            if (name !== "") {
                clearInterval(interval);
                return;
            }

            i++;

            setWelcomeText(fullText.slice(0, i));

            if (i >= fullText.length) {
                clearInterval(interval);
                i = 0;
                interval = setInterval(blinkingUnderscoreFoo, 500);
            }
        }, 100);

        return () => clearInterval(interval);
    }, [name]);

    useEffect(() => {
        if (!name) return;

        const fullTextPlusName = `${fullText} ${name}!`;
        const initialText = welcomeText; // strings are imutable so editing them will create a new copy anyways

        let i = initialText.length;

        const retypeWelcome = () => {
            i++;

            setWelcomeText(fullTextPlusName.slice(0, i));

            if (i >= fullTextPlusName.length) {
                clearInterval(interval);
            }
        };

        let interval = setInterval(() => {
            i--;

            let newText = initialText.slice(0, i);
            if (newText == "") {
                newText = "‎ ";
                setDisplaced((old) => !old);
            }

            setWelcomeText(newText);

            if (i == 0) {
                clearInterval(interval);
                setTimeout(() => {
                    interval = setInterval(retypeWelcome, 100);
                }, 500);
            }
        }, 100);

        return () => clearInterval(interval);
        // we don't want to recalculate useEffect when welcomeText changes because we are actively changing it, it'd create an unwanted loop.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [name]);

    const onSubmitNameHandler = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const name = formData.get("name") as string;

        try {
            const response = await fetch("/api/send-name", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name,
                }),
            });

            if (!response.ok) {
                throw new Error("Erreur lors de la requête");
            }

            const data = await response.json();

            console.log(data);

            //setName(name);
        } catch (error) {
            console.error(error);
        }

        setName(name);
    };

    const onSubmitSongHandler = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const song = formData.get("song") as string;

        console.log(song);
    };

    return (
        <>
            <meta name="description" content="Music Analyser created using React, Vite and Django." />
            <link rel="icon" type="image/svg+xml" href={websiteLogo} />
            <header className="header-top">
                <a>placeholder</a>
            </header>
            <div className="main-container">
                <div className="header-container">
                    <h1 id="topmost-title">Music Audiolyser</h1>
                    <p id="title-desc">L'analyse musicale par excellence</p>
                    <h1
                        id="welcome-text"
                        className={displaced ? "displaced-right-text text-align-start" : "text-align-center"}
                    >
                        {welcomeText}
                    </h1>
                </div>
                <div className="input-container">
                    {!name ? (
                        <form onSubmit={onSubmitNameHandler} id="name-form">
                            <label>Entrez votre prénom</label>
                            <input
                                name="name"
                                type="text"
                                id="input-name"
                                className="input-box"
                                placeholder="François"
                                required
                            />
                            <button type="submit" className="button-29">
                                Envoyer
                            </button>
                        </form>
                    ) : null}
                    {name ? (
                        <form onSubmit={onSubmitSongHandler} id="song-form">
                            <label>Entrez les musiques que vous écoutez</label>
                            <p>Seuls les liens YouTube sont acceptés (vidéo ou playlist)</p>
                            <input
                                name="song"
                                type="text"
                                id="input-song"
                                className="input-box"
                                placeholder="https://www.youtube.com/watch?v=ZHwVBirqD2s"
                                required
                            />
                            <button type="submit" className="button-29">
                                Envoyer
                            </button>
                        </form>
                    ) : null}
                </div>
            </div>
            <div className="footer-container">
                <footer className="footer">
                    <a href="https://vite.dev" target="_blank">
                        <img src={viteLogo} className="logo vite" alt="Vite logo" />
                        Vite
                    </a>
                    <a href="https://react.dev" target="_blank">
                        <img src={reactLogo} className="logo react" alt="React logo" />
                        React
                    </a>
                </footer>
                <p className="read-the-docs">Les outils utilisés</p>
            </div>
        </>
    );
};

export default App;

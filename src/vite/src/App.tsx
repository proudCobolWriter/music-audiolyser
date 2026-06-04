// As per:
// https://vite.dev/guide/backend-integration.html

if (import.meta.env.MODE !== "development") {
    // @ts-expect-error
    import("vite/modulepreload-polyfill");
}

type FixedString<N extends number> = { 0: string; length: N } & string;

interface IUserData {
    created: boolean;
    name: string;
    student_id: number;
    success: boolean;
}

interface IVideoData {
    id: FixedString<11>;
    title: string;
    duration: number;
    view_count: number;
    too_long: boolean;
}

type VideoDownloadList = Array<IVideoData>;

import { FormEvent, useEffect, useState, type FC } from "react";

// Resources importing

import GithubCornerLogo from "./assets/github-corner-right.svg?react";
import websiteLogo from "/favicon.svg?url";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./css/App.css";

// CONSTANTS

const IMAGE_THUMBNAIL_PREFIX = "https://img.youtube.com/vi/";

// Component definition

const App: FC = () => {
    const [name, setName] = useState("");
    const [welcomeText, setWelcomeText] = useState("‎ ");
    const [displaced, setDisplaced] = useState(true);
    const [previewLink, setPreviewLink] = useState(IMAGE_THUMBNAIL_PREFIX);

    const fullText = "Bienvenue";

    const [userData, setUserData] = useState<IUserData | object>({});
    const [videoDataList, setVideoDataList] = useState<VideoDownloadList>([]);

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

    useEffect(() => {
        const interval = setInterval(async () => {
            if (videoDataList.length > 0) {
                const videoIds = videoDataList.map((x) => x.id);

                let index = 0,
                    found = false;
                while (index < videoDataList.length) {
                    if (videoDataList[index]["title"] === "") {
                        found = true;
                        break;
                    }
                    index++;
                }

                if (!found) return;

                const id = videoIds[index];

                try {
                    const response = await fetch("/api/check-song/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            "youtube-id": id,
                        }),
                    });

                    if (!response.ok) {
                        throw new Error("An error occurred during the check song API POST request");
                    }

                    const updatedData: IVideoData = await response.json();

                    setVideoDataList((prev) => prev.map((item) => (item.id === id ? updatedData : item)));
                } catch (error) {
                    console.error(error);
                }
            }
        }, 1e3);

        return () => clearInterval(interval);
    });

    const parseVideoId = (url_string: string): string | false => {
        const regExp = /.*(?:youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=)([^#\\&\\?]*).*/;
        const match = url_string.match(regExp);

        if (match && match.length >= 2 && match[1].length == 11) {
            return match[1];
        }

        return false;
    };

    const onSubmitNameHandler = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const name = formData.get("name") as string;

        try {
            const response = await fetch("/api/send-name/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name,
                }),
            });

            if (!response.ok) {
                throw new Error("An error occurred during the name API POST request");
            }

            const data = await response.json();
            setUserData(data);

            console.log(`Identified as user of id ${(data as IUserData).student_id}`);

            setName(name);
        } catch (error) {
            console.error(error);
        }
    };

    const onSubmitSongHandler = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const song = formData.get("song") as string;

        const songId = parseVideoId(song);

        if (songId === false) {
            console.error("Unable to retrieve the song id");
            return;
        }

        setPreviewLink(IMAGE_THUMBNAIL_PREFIX + songId + "/maxresdefault.jpg");

        try {
            const response = await fetch("/api/send-song/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "youtube-id": songId,
                    id: (userData as IUserData).student_id,
                }),
            });

            if (!response.ok) {
                throw new Error("An error occurred during the song API POST request");
            }

            if (songId.length !== 11) {
                throw new Error("Found a video id longer or shorter than 11 alphanumerical characters");
            }

            const data = await response.json();

            setVideoDataList((prev) => [
                ...prev,
                {
                    id: songId as FixedString<11>,
                    title: "",
                    duration: 0,
                    view_count: 0,
                    too_long: false,
                },
            ]);

            console.log(data);
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <>
            <meta name="description" content="Music Analyser created using React, Vite and Django." />
            <link rel="icon" type="image/svg+xml" href={websiteLogo} />
            <div className="header-container">
                <header>
                    <a>MUSIC AUDIOLYSER</a>
                </header>
                <div className="gradient-white" />
                <div className="github-icon-container">
                    <a
                        href="https://github.com/proudCobolWriter/music-audiolyser"
                        className="github-corner"
                        aria-label="View source on GitHub"
                        target="_blank"
                    >
                        <GithubCornerLogo />
                    </a>
                </div>
            </div>
            <div className={"main-container" + (name === "" ? " tenvh-margin-top" : "")}>
                <div className={"intro-container " + (name !== "" ? "hidden" : "")}>
                    <h1 id="topmost-title">Music Audiolyser</h1>
                    <p id="title-desc">L'analyse musicale par excellence</p>
                </div>
                <h1
                    id="welcome-text"
                    className={"no-wrap " + (displaced ? "displaced-right-text text-align-start" : "text-align-center")}
                >
                    {welcomeText}
                </h1>
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
                            <div className="video-preview">
                                <img src={previewLink} />
                                <p className="video-preview-stat video-title">
                                    {videoDataList.length > 0 ? videoDataList[0].title : "Titre de la vidéo"}
                                </p>
                                <p className="video-preview-stat video-duration">
                                    {videoDataList.length > 0
                                        ? `${Math.trunc(videoDataList[0].duration / 60)}:${videoDataList[0].duration % 60}`
                                        : "00:00"}
                                </p>
                            </div>
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

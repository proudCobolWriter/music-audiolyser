CREATE TABLE IF NOT EXISTS music_app_student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS music_app_song (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_id TEXT,
    title TEXT,
    artist TEXT,
    genre TEXT,
    bpm INTEGER,
    danceability REAL,
    key TEXT,
    scale TEXT CHECK(scale IN ('minor', 'major')),
    mood TEXT
);

CREATE TABLE IF NOT EXISTS music_app_song_listeners (
    student_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (student_id, song_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
);
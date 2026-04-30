CREATE TABLE individuals (
    id SERIAL PRIMARY KEY,
    ig_handle TEXT NOT NULL UNIQUE,
    followers INTEGER,
    bio TEXT,
    is_private BOOLEAN DEFAULT false
);
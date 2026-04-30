CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    website TEXT,
    emails TEXT[],
    phone TEXT,
    industry TEXT
);
const { Client } = require('pg');

const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'leads_db',
  user: 'postgres',
  password: 'your_password',
  ssl: false
});

client.connect()
  .then(() => console.log('Connected to PostgreSQL'))
  .catch(err => console.error('Connection error', err.stack));
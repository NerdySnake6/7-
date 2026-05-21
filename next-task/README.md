# Practical Assignment 7

## Run

```bash
npm install
npm start
```

The app listens on `127.0.0.1:3000` by default. Set `PORT` or `HOST` to use a different address.

## Deploy to Vercel

Import the repository in Vercel and deploy it as a Node.js project. The `vercel.json` file routes all requests to the Express app exported from `api/index.js`.

## Routes

- `GET /login/` returns `1167133` as plain text.
- `POST /insert/` accepts `application/x-www-form-urlencoded` fields `login`, `password`, and `URL`, then inserts `{ login, password }` into the `users` MongoDB collection.

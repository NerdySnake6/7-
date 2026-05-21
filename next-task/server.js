'use strict';

const express = require('express');
const mongoose = require('mongoose');

const app = express();
const port = process.env.PORT || 3000;
const host = process.env.HOST || '127.0.0.1';
const systemLogin = '1167133';

app.use(express.urlencoded({ extended: false }));

const userSchema = new mongoose.Schema(
  {
    login: String,
    password: String,
  },
  {
    collection: 'users',
    versionKey: false,
  }
);

/**
 * Waits until a Mongoose connection is open.
 *
 * @param {mongoose.Connection} connection MongoDB connection.
 * @returns {Promise<mongoose.Connection>} Open MongoDB connection.
 */
function waitForConnection(connection) {
  return new Promise((resolve, reject) => {
    connection.once('open', () => resolve(connection));
    connection.once('error', reject);
  });
}

app.get('/login/', (request, response) => {
  response.type('text/plain').send(systemLogin);
});

app.post('/insert/', async (request, response) => {
  const { login, password, URL } = request.body;
  const hasRequiredFields =
    Object.prototype.hasOwnProperty.call(request.body, 'login') &&
    Object.prototype.hasOwnProperty.call(request.body, 'password') &&
    Object.prototype.hasOwnProperty.call(request.body, 'URL');

  if (!hasRequiredFields || !URL) {
    response.status(400).type('text/plain').send('Missing login, password, or URL');
    return;
  }

  const connection = mongoose.createConnection(URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });

  try {
    const User = connection.model('User', userSchema);

    await waitForConnection(connection);
    await User.create({ login, password });

    response.type('text/plain').send('OK');
  } catch (error) {
    response.status(500).type('text/plain').send(error.message);
  } finally {
    await connection.close().catch(() => {});
  }
});

app.listen(port, host, () => {
  console.log(`Server is listening on http://${host}:${port}`);
});

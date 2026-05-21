'use strict';

const express = require('express');
const mongoose = require('mongoose');

const app = express();
const systemLogin = '1167133';

app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use((request, response, next) => {
  const origin = request.get('Origin');
  const requestedHeaders = request.get('Access-Control-Request-Headers');

  response.set('Access-Control-Allow-Origin', origin || '*');
  response.set('Access-Control-Allow-Credentials', 'true');
  response.set('Access-Control-Allow-Methods', 'GET,HEAD,POST,OPTIONS');
  response.set(
    'Access-Control-Allow-Headers',
    requestedHeaders || 'Content-Type, Accept, Origin, X-Requested-With'
  );
  response.set('Access-Control-Max-Age', '86400');
  response.set('Vary', 'Origin, Access-Control-Request-Headers');

  if (request.method === 'OPTIONS') {
    response.sendStatus(204);
    return;
  }

  next();
});

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

app.get(['/', '/login', '/login/'], (request, response) => {
  response.type('text/plain').send(systemLogin);
});

app.post(['/insert', '/insert/'], async (request, response) => {
  const { login, password } = request.body;
  const URL = request.body.URL || request.body.url;
  const hasRequiredFields =
    Object.prototype.hasOwnProperty.call(request.body, 'login') &&
    Object.prototype.hasOwnProperty.call(request.body, 'password') &&
    (Object.prototype.hasOwnProperty.call(request.body, 'URL') ||
      Object.prototype.hasOwnProperty.call(request.body, 'url'));

  if (!hasRequiredFields || !URL) {
    response.status(400).type('text/plain').send('Missing login, password, or URL');
    return;
  }

  const connection = mongoose.createConnection(URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000,
    connectTimeoutMS: 5000,
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

module.exports = app;

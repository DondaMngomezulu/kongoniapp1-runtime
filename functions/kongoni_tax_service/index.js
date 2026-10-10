'use strict';

const { createApplication } = require('./src/application');
const { UnconfiguredRuleRepository } = require('./src/rule-repository');

const MAX_BODY_BYTES = 64 * 1024;
const application = createApplication({
  ruleRepository: new UnconfiguredRuleRepository()
});

function writeJson(response, statusCode, body) {
  response.statusCode = statusCode;
  response.setHeader('content-type', 'application/json; charset=utf-8');
  response.setHeader('cache-control', 'no-store');
  response.setHeader('x-content-type-options', 'nosniff');
  response.end(JSON.stringify(body));
}

function readJson(request) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];

    request.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        const error = new Error('Request body exceeds 65536 bytes.');
        error.code = 'BODY_TOO_LARGE';
        reject(error);
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });

    request.on('end', () => {
      if (chunks.length === 0) {
        resolve(undefined);
        return;
      }
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch {
        const error = new Error('Request body must contain valid JSON.');
        error.code = 'INVALID_JSON';
        reject(error);
      }
    });

    request.on('error', reject);
  });
}

module.exports = async (request, response) => {
  try {
    const contentType = String(request.headers['content-type'] || '');
    const hasBody = request.method === 'POST';
    if (hasBody && !contentType.toLowerCase().startsWith('application/json')) {
      writeJson(response, 415, {
        error: 'UNSUPPORTED_MEDIA_TYPE',
        message: 'Use application/json for this request.'
      });
      return;
    }

    const body = hasBody ? await readJson(request) : undefined;
    const result = await application.handle({
      method: request.method,
      path: new URL(request.url, 'https://service.invalid').pathname,
      headers: request.headers,
      body
    });
    writeJson(response, result.statusCode, result.body);
  } catch (error) {
    const statusCode = error.code === 'BODY_TOO_LARGE' ? 413 : 400;
    writeJson(response, statusCode, {
      error: error.code || 'INVALID_REQUEST',
      message: error.message
    });
  }
};


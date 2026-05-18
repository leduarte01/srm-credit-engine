import { describe, expect, it } from 'vitest';
import MockAdapter from 'axios-mock-adapter';

import { ApiClientError, createApiClient } from './client';

describe('apiClient interceptor', () => {
  it('wraps backend ErrorResponse payloads in ApiClientError', async () => {
    const client = createApiClient('http://example.test');
    const mock = new MockAdapter(client);
    mock.onGet('/boom').reply(404, {
      code: 'RECEIVABLE_NOT_FOUND',
      message: 'Receivable abc not found.',
    });

    await expect(client.get('/boom')).rejects.toMatchObject({
      name: 'ApiClientError',
      status: 404,
      code: 'RECEIVABLE_NOT_FOUND',
    });
  });

  it('passes through unrelated errors unchanged', async () => {
    const client = createApiClient('http://example.test');
    const mock = new MockAdapter(client);
    mock.onGet('/raw').reply(500, 'plain string');

    await expect(client.get('/raw')).rejects.not.toBeInstanceOf(ApiClientError);
  });
});

import axios, { type AxiosInstance } from 'axios';

import type { ApiError } from '../types/domain';

const DEFAULT_BASE_URL = 'http://localhost:8000/api/v1';

export const apiBaseUrl: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE_URL;

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: ApiError['details'];

  constructor(status: number, payload: ApiError) {
    super(payload.message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = payload.code;
    this.details = payload.details ?? undefined;
  }
}

export function createApiClient(baseURL: string = apiBaseUrl): AxiosInstance {
  const instance = axios.create({
    baseURL,
    timeout: 15_000,
    headers: { 'Content-Type': 'application/json' },
  });

  instance.interceptors.response.use(
    (response) => response,
    (error: unknown) => {
      if (axios.isAxiosError(error) && error.response) {
        const data = error.response.data as Partial<ApiError> | undefined;
        if (data?.code && data.message) {
          return Promise.reject(
            new ApiClientError(error.response.status, {
              code: data.code,
              message: data.message,
              details: data.details ?? null,
            }),
          );
        }
      }
      return Promise.reject(error);
    },
  );

  return instance;
}

export const apiClient = createApiClient();

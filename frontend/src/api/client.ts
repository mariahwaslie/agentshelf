import createClient from "openapi-fetch";

import type { components, paths } from "./types.gen";

/** The only gateway from the UI to the backend. Paths and bodies are typed from FastAPI's schema. */
export const api = createClient<paths>({ baseUrl: window.location.origin });

type Schemas = components["schemas"];
export type AppConfig = Schemas["AppConfig"];
export type AppMode = Schemas["AppMode"];

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, path: string) {
    super(`${path} answered ${String(status)}`);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function fetchConfig(): Promise<AppConfig> {
  const { data, response } = await api.GET("/api/config");
  if (!data) throw new ApiError(response.status, "/api/config");
  return data;
}

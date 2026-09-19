import type {
  BackendProfile,
  ProfileUpdatePayload,
  ScenarioParseResult,
  SimulationRequest,
  SimulationResponse,
} from "@/services/types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  const data = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? (data as { detail: string }).detail
        : `Request failed (${response.status})`;
    throw new ApiError(detail, response.status);
  }

  return data as T;
}

export async function getProfile(): Promise<BackendProfile | null> {
  try {
    return await request<BackendProfile>("/profile");
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function updateProfile(
  payload: ProfileUpdatePayload
): Promise<BackendProfile> {
  return request<BackendProfile>("/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function parseScenario(query: string): Promise<ScenarioParseResult> {
  return request<ScenarioParseResult>("/scenario/parse", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function runSimulation(
  payload: SimulationRequest
): Promise<SimulationResponse> {
  return request<SimulationResponse>("/simulate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

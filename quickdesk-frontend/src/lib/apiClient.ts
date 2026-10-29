const API_BASE_URL = "/api/v1";

export class ApiError extends Error {
  public readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type ApiOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

function getErrorMessage(data: unknown): string {
  if (typeof data === "object" && data !== null && "detail" in data) {
    const detail = data.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item?.msg === "string" ? item.msg : "Validation error",
        )
        .join(", ");
    }
  }

  return "Something went wrong. Please try again.";
}

export async function apiClient<T>(
  endpoint: string,
  options: ApiOptions = {},
): Promise<T> {
  const { body, headers, ...rest } = options;

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...rest,
      credentials: "include",
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  } catch {
    throw new ApiError("Unable to connect to the server. Please try again.", 0);
  }

  const contentType = response.headers.get("content-type") ?? "";

  let data: unknown = null;

  if (response.status !== 204) {
    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  }

  if (!response.ok) {
    throw new ApiError(getErrorMessage(data), response.status);
  }

  return data as T;
}

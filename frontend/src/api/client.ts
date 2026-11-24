import {
  ApiError,
  type ApiErrorBody,
  type LoginBody,
  type RegisterBody,
  type User,
} from "./types";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const BASE = "/api/v1";

// ---------- Real API ----------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(0, "NETWORK", "Network error");
  }

  if (!response.ok) {
    let code = "GENERIC";
    let message = "Request failed";
    let details: unknown = null;
    try {
      const body = (await response.json()) as ApiErrorBody;
      code = body.error.code;
      message = body.error.message;
      details = body.error.details;
    } catch {
      // Response was not in the agreed error shape; keep the defaults.
    }
    throw new ApiError(response.status, code, message, details);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

// ---------- Mock API (fake data only) ----------

interface MockAccount {
  user: User;
  password: string;
}

const mockAccounts = new Map<string, MockAccount>();
let mockSession: User | null = null;

function delay(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 400));
}

async function mockRegister(body: RegisterBody): Promise<User> {
  await delay();
  const key = body.email.trim().toLowerCase();
  if (mockAccounts.has(key)) {
    throw new ApiError(409, "EMAIL_IN_USE", "Email already used");
  }
  const user: User = {
    id: String(mockAccounts.size + 1),
    email: key,
    full_name: body.full_name,
    role: body.role,
  };
  mockAccounts.set(key, { user, password: body.password });
  return user;
}

async function mockLogin(body: LoginBody): Promise<User> {
  await delay();
  const account = mockAccounts.get(body.email.trim().toLowerCase());
  if (!account || account.password !== body.password) {
    throw new ApiError(401, "INVALID_CREDENTIALS", "Wrong email or password");
  }
  mockSession = account.user;
  return account.user;
}

async function mockLogout(): Promise<void> {
  await delay();
  mockSession = null;
}

async function mockMe(): Promise<User> {
  await delay();
  if (!mockSession) {
    throw new ApiError(401, "UNAUTHORIZED", "Not logged in");
  }
  return mockSession;
}

// ---------- Public API (used by the screens) ----------

export function register(body: RegisterBody): Promise<User> {
  if (USE_MOCK) return mockRegister(body);
  return request<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function login(body: LoginBody): Promise<User> {
  if (USE_MOCK) return mockLogin(body);
  return request<User>("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function logout(): Promise<void> {
  if (USE_MOCK) return mockLogout();
  return request<void>("/auth/logout", { method: "POST" });
}

export function me(): Promise<User> {
  if (USE_MOCK) return mockMe();
  return request<User>("/me");
}

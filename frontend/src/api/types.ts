export type Role = "patient" | "student";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
}

export interface RegisterBody {
  email: string;
  password: string;
  full_name: string;
  role: Role;
}

export interface LoginBody {
  email: string;
  password: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(
    status: number,
    code: string,
    message: string,
    details: unknown = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

import { useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import FormField from "../components/FormField";
import LanguageSwitcher from "../components/LanguageSwitcher";

interface FieldErrors {
  email?: string;
  password?: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered =
    (location.state as { registered?: boolean } | null)?.registered === true;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const validate = (): FieldErrors => {
    const errors: FieldErrors = {};
    if (!email.trim()) errors.email = t("validation.required");
    else if (!EMAIL_PATTERN.test(email.trim()))
      errors.email = t("validation.invalidEmail");
    if (!password) errors.password = t("validation.required");
    return errors;
  };

  const errorMessage = (error: unknown): string => {
    if (error instanceof ApiError) {
      if (error.code === "NETWORK") return t("errors.NETWORK");
      if (error.status === 401) return t("errors.INVALID_CREDENTIALS");
      if (error.status === 429) return t("errors.RATE_LIMITED");
    }
    return t("errors.GENERIC");
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setServerError("");
    const errors = validate();
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      await login({ email: email.trim(), password });
      navigate("/", { replace: true });
    } catch (error) {
      setServerError(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-8">
      <section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold text-slate-950">
            {t("login.title")}
          </h1>
          <LanguageSwitcher />
        </div>

        {justRegistered ? (
          <p
            role="status"
            className="mb-4 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-800"
          >
            {t("login.accountCreated")}
          </p>
        ) : null}

        {serverError ? (
          <p
            role="alert"
            className="mb-4 rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700"
          >
            {serverError}
          </p>
        ) : null}

        <form
          onSubmit={handleSubmit}
          noValidate
          className="flex flex-col gap-4"
        >
          <FormField
            label={t("fields.email")}
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldErrors.email}
          />
          <FormField
            label={t("fields.password")}
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
          />
          <button
            type="submit"
            disabled={submitting}
            className="rounded-xl bg-emerald-600 px-4 py-3 text-base font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {submitting ? t("login.submitting") : t("login.submit")}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-600">
          {t("login.noAccount")}{" "}
          <Link
            to="/register"
            className="font-medium text-emerald-700 hover:underline"
          >
            {t("login.registerLink")}
          </Link>
        </p>
      </section>
    </main>
  );
}

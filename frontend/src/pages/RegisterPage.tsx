import { useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";

import * as api from "../api/client";
import { ApiError, type RegisterRole } from "../api/types";
import FormField from "../components/FormField";
import LanguageSwitcher from "../components/LanguageSwitcher";

interface FieldErrors {
  fullName?: string;
  email?: string;
  password?: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<RegisterRole>("patient");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const validate = (): FieldErrors => {
    const errors: FieldErrors = {};
    if (!fullName.trim()) errors.fullName = t("validation.required");
    if (!email.trim()) errors.email = t("validation.required");
    else if (!EMAIL_PATTERN.test(email.trim()))
      errors.email = t("validation.invalidEmail");
    if (!password) errors.password = t("validation.required");
    else if (password.length < 8)
      errors.password = t("validation.passwordTooShort");
    return errors;
  };

  const errorMessage = (error: unknown): string => {
    if (error instanceof ApiError) {
      if (error.code === "NETWORK") return t("errors.NETWORK");
      if (error.status === 409) return t("errors.EMAIL_IN_USE");
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
      await api.register({
        email: email.trim(),
        password,
        full_name: fullName.trim(),
        role,
      });
      navigate("/login", { replace: true, state: { registered: true } });
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
            {t("register.title")}
          </h1>
          <LanguageSwitcher />
        </div>

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
            label={t("fields.fullName")}
            type="text"
            autoComplete="name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            error={fieldErrors.fullName}
          />
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
          />
          <div className="flex flex-col gap-1">
            <label
              htmlFor="role"
              className="text-sm font-medium text-slate-700"
            >
              {t("fields.role")}
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as RegisterRole)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-base text-slate-950 outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="patient">{t("roles.patient")}</option>
              <option value="student">{t("roles.student")}</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-xl bg-emerald-600 px-4 py-3 text-base font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {submitting ? t("register.submitting") : t("register.submit")}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-600">
          {t("register.haveAccount")}{" "}
          <Link
            to="/login"
            className="font-medium text-emerald-700 hover:underline"
          >
            {t("register.loginLink")}
          </Link>
        </p>
      </section>
    </main>
  );
}

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function HomePage() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const handleLogout = async () => {
    setSubmitting(true);
    try {
      await logout();
    } finally {
      setSubmitting(false);
      navigate("/login", { replace: true });
    }
  };

  if (!user) return null;

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-8">
      <section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold text-slate-950">
            {t("home.welcome", { name: user.full_name })}
          </h1>
          <LanguageSwitcher />
        </div>

        <dl className="flex flex-col gap-3 rounded-2xl bg-slate-50 p-4 text-sm">
          <div className="flex items-center justify-between gap-3">
            <dt className="font-medium text-slate-500">
              {t("home.emailLabel")}
            </dt>
            <dd className="text-slate-900" dir="ltr">
              {user.email}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-3">
            <dt className="font-medium text-slate-500">
              {t("home.roleLabel")}
            </dt>
            <dd className="text-slate-900">{t(`roles.${user.role}`)}</dd>
          </div>
        </dl>

        <button
          type="button"
          onClick={handleLogout}
          disabled={submitting}
          className="mt-6 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-base font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
        >
          {t("home.logout")}
        </button>
      </section>
    </main>
  );
}

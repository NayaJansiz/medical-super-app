import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "./auth/AuthContext";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

type HealthStatus = "checking" | "connected" | "unavailable";

function StatusPage() {
  const [status, setStatus] = useState<HealthStatus>("checking");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch("/health");
        if (!response.ok) {
          throw new Error("Health check failed");
        }
        const result: { status: string } = await response.json();
        setStatus(result.status === "ok" ? "connected" : "unavailable");
      } catch {
        setStatus("unavailable");
      }
    };

    void checkHealth();
  }, []);

  const isConnected = status === "connected";
  const isChecking = status === "checking";
  const message = isChecking
    ? "Checking the service and database"
    : isConnected
      ? "API and database are connected"
      : "The API or database is unavailable";

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <div className="mb-8 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
          <span aria-hidden="true" className="text-xl font-semibold">
            +
          </span>
        </div>
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-700">
          Medical Records
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
          Project status
        </h1>
        <div
          aria-live="polite"
          className="mt-8 flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-4"
        >
          <span
            aria-hidden="true"
            className={`h-3 w-3 rounded-full ${
              isChecking
                ? "animate-pulse bg-amber-500"
                : isConnected
                  ? "bg-emerald-500"
                  : "bg-rose-500"
            }`}
          />
          <p className="text-sm font-medium text-slate-700">{message}</p>
        </div>
        <p className="mt-6 text-sm leading-6 text-slate-500">
          This starter page confirms that the API can reach its configured
          PostgreSQL database.
        </p>
      </section>
    </main>
  );
}

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const { t } = useTranslation();

  if (loading) {
    return <p className="p-6 text-sm text-slate-600">{t("loading")}</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function RedirectIfLoggedIn({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const { t } = useTranslation();

  if (loading) {
    return <p className="p-6 text-sm text-slate-600">{t("loading")}</p>;
  }
  if (user) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <RequireAuth>
            <HomePage />
          </RequireAuth>
        }
      />
      <Route
        path="/login"
        element={
          <RedirectIfLoggedIn>
            <LoginPage />
          </RedirectIfLoggedIn>
        }
      />
      <Route
        path="/register"
        element={
          <RedirectIfLoggedIn>
            <RegisterPage />
          </RedirectIfLoggedIn>
        }
      />
      <Route path="/status" element={<StatusPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

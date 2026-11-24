import { useTranslation } from "react-i18next";

import { setLanguage } from "../i18n";

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const isArabic = i18n.language === "ar";

  return (
    <button
      type="button"
      onClick={() => setLanguage(isArabic ? "en" : "ar")}
      className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      aria-label={t("common.language")}
    >
      {isArabic ? t("common.english") : t("common.arabic")}
    </button>
  );
}

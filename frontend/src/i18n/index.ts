import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import ar from "./ar.json";
import en from "./en.json";

export type Language = "en" | "ar";

const STORAGE_KEY = "lang";

function getInitialLanguage(): Language {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === "en" || saved === "ar") {
      return saved;
    }
  } catch {
    // Storage may be unavailable; fall back to English.
  }
  return "en";
}

export function applyDocumentLanguage(lang: Language): void {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
}

export function setLanguage(lang: Language): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // Ignore storage errors; the language still changes for this session.
  }
  void i18n.changeLanguage(lang);
}

const initialLanguage = getInitialLanguage();

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ar: { translation: ar },
  },
  lng: initialLanguage,
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

applyDocumentLanguage(initialLanguage);

i18n.on("languageChanged", (lng) => {
  applyDocumentLanguage(lng === "ar" ? "ar" : "en");
});

export default i18n;

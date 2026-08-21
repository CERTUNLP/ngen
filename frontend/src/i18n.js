import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import Backend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";
import { getSettingLanguage } from "api/services/setting";

const options = {
  order: ["querystring", "navigator"],
  lookupQuerystring: "lng"
};

const initializeI18n = async () => {
  let lang;
  try {
    lang = await getSettingLanguage();
  } catch (error) {
    console.error("Error obteniendo el idioma del backend:", error);
    lang = localStorage.getItem("NGEN_LANG") || "en";
  }

  i18n
    .use(Backend)
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
      lng: lang,
      fallbackLng: "en",
      debug: import.meta.env.VITE_APP_ENV === "development",
      detection: options,
      interpolation: {
        escapeValue: false // not needed for react as it escapes by default
      }
    });
};

export default initializeI18n;

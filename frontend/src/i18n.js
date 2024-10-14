import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import Backend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";
import apiInstance from "./api/api";
import { COMPONENT_URL } from "./config/constant";

const options = {
  order: ["querystring", "navigator"],
  lookupQuerystring: "lng"
};

const fetchLanguageSetting = async () => {
  // Verificar primero si el idioma está en localStorage
  const localStorageLang = localStorage.getItem("ngen_lang");
  if (localStorageLang) {
    return localStorageLang;
  }

  // Si no está en localStorage, obtenerlo del backend
  try {
    const response = await apiInstance.get(COMPONENT_URL.configPublic);

    const langSetting = response.data.results.find((item) => item.key === "NGEN_LANG");
    const lang = langSetting ? langSetting.value : "en";

    // Guardar el idioma en localStorage
    localStorage.setItem("ngen_lang", lang);
    return lang;
  } catch (error) {
    console.error("Error fetching language setting:", error);
    // Devolver "en" como idioma predeterminado en caso de error
    return "en";
  }
};

const initializeI18n = async () => {
  const lang = await fetchLanguageSetting();

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

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

const options = {
  order: ['querystring', 'navigator'],
  lookupQuerystring: 'lng'
};

const fetchLanguageSetting = async () => {
  const localStorageLang = localStorage.getItem('ngen_lang');
  if (localStorageLang) {
    return localStorageLang;
  }

  try {
    const response = await fetch('http://localhost:8000/api/ngenconfig/');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    const langSetting = data.results.find((item) => item.key === 'NGEN_LANG');
    const lang = langSetting ? langSetting.value : 'en';

    localStorage.setItem('ngen_lang', lang);
    return lang;
  } catch (error) {
    console.error('Error fetching language setting:', error);
    return 'en'; // default to 'en' on error
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
      fallbackLng: 'en',
      debug: true,
      detection: options,
      interpolation: {
        escapeValue: false // not needed for react as it escapes by default
      }
    });
};

initializeI18n();

export default i18n;

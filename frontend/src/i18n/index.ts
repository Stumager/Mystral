import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import es from "./locales/es.json";
import pt from "./locales/pt.json";
import ru from "./locales/ru.json";
import tr from "./locales/tr.json";
import uk from "./locales/uk.json";

i18n.use(initReactI18next).init({
  resources: {
    ru: { translation: ru },
    en: { translation: en },
    es: { translation: es },
    pt: { translation: pt },
    tr: { translation: tr },
    uk: { translation: uk },
  },
  lng: "ru",
  fallbackLng: "ru",
  interpolation: { escapeValue: false },
});

export default i18n;

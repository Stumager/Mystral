import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./i18n";
import "./index.css";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

const twa = (window as any).Telegram?.WebApp;
if (twa) {
  twa.ready();
  twa.expand();
  // Referral deep link: t.me/<bot>/<app>?startapp=CODE delivers CODE here,
  // not via a URL path — bridge it into the same key App.tsx's /ref/CODE
  // capture uses so both origins share one apply mechanism.
  const startParam = twa.initDataUnsafe?.start_param;
  if (startParam) localStorage.setItem("mystral_ref_code", startParam);
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

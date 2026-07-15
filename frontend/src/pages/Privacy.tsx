import { useTranslation } from "react-i18next";
import { Link } from "./Terms";
import { Logo } from "../components/Logo";

export function Privacy() {
  const { i18n, t } = useTranslation();
  const ru = i18n.language === "ru";

  return (
    <div style={{ minHeight: "100vh", background: "radial-gradient(130% 60% at 50% -5%,#0F0A26 0%,#07060F 55%)" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "18px 24px", maxWidth: 900, margin: "0 auto" }}>
        <a href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <Logo size={24} />
          <span className="font-cinzel" style={{ fontSize: 14, letterSpacing: ".28em", color: "#E8CD7E" }}>MYSTRAL</span>
        </a>
        <a href="/" style={{ fontSize: 13, color: "#C9A84C", textDecoration: "none", padding: "8px 20px", borderRadius: 10, border: "1px solid rgba(201,168,76,.25)" }}>
          {ru ? "Войти" : "Sign in"}
        </a>
      </header>

      <main style={{ maxWidth: 800, margin: "0 auto", padding: "40px 24px" }}>
        <h1 className="font-cormorant" style={{ fontSize: 38, color: "#F0E9DA", marginBottom: 8 }}>
          {ru ? "Политика конфиденциальности" : "Privacy Policy"}
        </h1>
        <p style={{ fontSize: 13, color: "#6E6757", marginBottom: 40 }}>
          {ru ? "Последнее обновление: 27 июня 2026" : "Last updated: June 27, 2026"}
        </p>

        <Section title={ru ? "1. Общие положения" : "1. General provisions"}>
          {ru ? (<>
            Настоящая Политика конфиденциальности определяет порядок обработки и защиты персональных данных пользователей сервиса Mystral (далее — «Сервис»), доступного по адресу mystral.space и через Telegram Mini App.
            <br /><br />
            Оператором персональных данных является Самозанятый Нечунаев Александр Вячеславович (далее — «Оператор»).
            <br /><br />
            Обработка персональных данных осуществляется в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных» и иными нормативными актами Российской Федерации.
            <br /><br />
            Используя Сервис, вы даёте согласие на обработку ваших персональных данных в соответствии с настоящей Политикой.
          </>) : (<>
            This Privacy Policy defines the procedures for processing and protecting personal data of users of the Mystral service (hereinafter referred to as the "Service"), available at mystral.space and via Telegram Mini App.
            <br /><br />
            The personal data controller is the sole proprietor Alexander Nechunaev (hereinafter referred to as the "Controller").
            <br /><br />
            Personal data processing is carried out in accordance with Federal Law No. 152-FZ of July 27, 2006 "On Personal Data" and other regulatory acts of the Russian Federation.
            <br /><br />
            By using the Service, you consent to the processing of your personal data in accordance with this Policy.
          </>)}
        </Section>

        <Section title={ru ? "2. Какие данные мы собираем" : "2. Data we collect"}>
          {ru ? (<>
            Мы собираем следующие категории данных:
            <br /><br />
            <B>Данные учётной записи:</B> адрес электронной почты, имя пользователя, дата рождения, время рождения, место рождения.
            <br /><br />
            <B>Данные Telegram:</B> Telegram ID, имя пользователя Telegram, язык интерфейса — при авторизации через Telegram.
            <br /><br />
            <B>Технические данные:</B> IP-адрес, тип браузера, данные об использовании Сервиса, время посещений.
            <br /><br />
            <B>Данные подписки:</B> информация о статусе подписки, история платежей (без данных карт).
          </>) : (<>
            We collect the following categories of data:
            <br /><br />
            <B>Account data:</B> email address, username, date of birth, time of birth, place of birth.
            <br /><br />
            <B>Telegram data:</B> Telegram ID, Telegram username, interface language — when authenticating via Telegram.
            <br /><br />
            <B>Technical data:</B> IP address, browser type, Service usage data, visit timestamps.
            <br /><br />
            <B>Subscription data:</B> subscription status, payment history (no card details).
          </>)}
        </Section>

        <Section title={ru ? "3. Как мы используем данные" : "3. How we use data"}>
          {ru ? (<>
            Собранные данные используются для:
            <br /><br />
            — предоставления услуг Сервиса (составление гороскопов, натальных карт, нумерологических расчётов);<br />
            — персонализации контента на основе даты, времени и места рождения;<br />
            — отправки ежедневных гороскопов и уведомлений о лунных событиях;<br />
            — обработки платежей и управления подпиской;<br />
            — улучшения качества Сервиса и устранения ошибок;<br />
            — обеспечения безопасности аккаунта и предотвращения злоупотреблений.
          </>) : (<>
            Collected data is used for:
            <br /><br />
            — providing Service features (horoscopes, natal charts, numerological calculations);<br />
            — personalizing content based on date, time and place of birth;<br />
            — sending daily horoscopes and lunar event notifications;<br />
            — processing payments and managing subscriptions;<br />
            — improving Service quality and fixing bugs;<br />
            — ensuring account security and preventing abuse.
          </>)}
        </Section>

        <Section title={ru ? "4. Хранение данных" : "4. Data storage"}>
          {ru ? (<>
            Персональные данные хранятся на защищённых серверах в Европейском Союзе (VPS-хостинг в Швеции). Передача данных между клиентом и сервером защищена шифрованием TLS/SSL.
            <br /><br />
            Пароли хранятся в захешированном виде (bcrypt) и не могут быть восстановлены Оператором.
            <br /><br />
            Данные хранятся в течение всего срока использования Сервиса и удаляются по запросу пользователя или через 30 дней после удаления аккаунта.
          </>) : (<>
            Personal data is stored on secure servers in the European Union (VPS hosting in Sweden). Data transfer between client and server is protected by TLS/SSL encryption.
            <br /><br />
            Passwords are stored in hashed form (bcrypt) and cannot be recovered by the Controller.
            <br /><br />
            Data is retained for the duration of Service usage and deleted upon user request or 30 days after account deletion.
          </>)}
        </Section>

        <Section title={ru ? "5. Передача данных третьим лицам" : "5. Data sharing with third parties"}>
          {ru ? (<>
            Мы передаём данные следующим сервисам исключительно для оказания услуг:
            <br /><br />
            <B>Groq AI</B> — генерация астрологических интерпретаций. Передаются астрологические данные (знак зодиака, позиции планет), но не персональные идентификаторы.
            <br /><br />
            <B>Resend</B> — отправка email-уведомлений (верификация, сброс пароля). Передаётся email-адрес.
            <br /><br />
            <B>Telegram</B> — авторизация и отправка уведомлений. Используется Telegram ID.
            <br /><br />
            Мы не продаём, не сдаём в аренду и не передаём персональные данные третьим лицам в маркетинговых целях.
          </>) : (<>
            We share data with the following services solely for providing our features:
            <br /><br />
            <B>Groq AI</B> — generating astrological interpretations. We share astrological data (zodiac sign, planet positions), not personal identifiers.
            <br /><br />
            <B>Resend</B> — sending email notifications (verification, password reset). Email address is shared.
            <br /><br />
            <B>Telegram</B> — authentication and notifications. Telegram ID is used.
            <br /><br />
            We do not sell, rent, or share personal data with third parties for marketing purposes.
          </>)}
        </Section>

        <Section title={ru ? "6. Права пользователя" : "6. User rights"}>
          {ru ? (<>
            Вы имеете право:
            <br /><br />
            — получить информацию о том, какие данные мы храним;<br />
            — исправить или обновить свои персональные данные;<br />
            — запросить полное удаление своих данных;<br />
            — отозвать согласие на обработку данных;<br />
            — получить копию своих данных в машиночитаемом формате.
            <br /><br />
            Для реализации этих прав отправьте запрос на адрес: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>.
            Запрос будет обработан в течение 30 дней.
          </>) : (<>
            You have the right to:
            <br /><br />
            — request information about what data we store;<br />
            — correct or update your personal data;<br />
            — request complete deletion of your data;<br />
            — withdraw consent for data processing;<br />
            — obtain a copy of your data in a machine-readable format.
            <br /><br />
            To exercise these rights, send a request to: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>.
            Requests will be processed within 30 days.
          </>)}
        </Section>

        <Section title={ru ? "7. Cookies" : "7. Cookies"}>
          {ru ? (<>
            Сервис использует файлы cookies и localStorage для:
            <br /><br />
            — хранения токена авторизации (JWT);<br />
            — сохранения языковых предпочтений;<br />
            — обеспечения корректной работы Сервиса.
            <br /><br />
            Мы не используем сторонние рекламные cookies.
          </>) : (<>
            The Service uses cookies and localStorage for:
            <br /><br />
            — storing authorization tokens (JWT);<br />
            — saving language preferences;<br />
            — ensuring proper Service operation.
            <br /><br />
            We do not use third-party advertising cookies.
          </>)}
        </Section>

        <Section title={ru ? "8. Push-уведомления" : "8. Push notifications"}>
          {ru
            ? "Push-уведомления отправляются только с вашего явного согласия. Вы можете включить или отключить их в любой момент в разделе «Профиль» Сервиса. Отключение push-уведомлений не влияет на работу остальных функций Сервиса."
            : "Push notifications are sent only with your explicit consent. You can enable or disable them at any time in the Profile section. Disabling push notifications does not affect other Service features."}
        </Section>

        <Section title={ru ? "9. Изменения политики" : "9. Policy changes"}>
          {ru
            ? "Мы оставляем за собой право вносить изменения в настоящую Политику. При существенных изменениях пользователи будут уведомлены по электронной почте. Продолжение использования Сервиса после публикации изменений означает согласие с обновлённой Политикой."
            : "We reserve the right to modify this Policy. Users will be notified by email of significant changes. Continued use of the Service after changes are published constitutes acceptance of the updated Policy."}
        </Section>

        <Section title={ru ? "10. Контакты" : "10. Contact"}>
          {ru ? (<>
            По всем вопросам, связанным с обработкой персональных данных, обращайтесь:
            <br /><br />
            Самозанятый Нечунаев Александр Вячеславович
            <br />
            ИНН: 230307450300
            <br />
            Email: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>
          </>) : (<>
            For all questions related to personal data processing, contact us:
            <br /><br />
            Alexander Nechunaev, sole proprietor
            <br />
            TIN: 230307450300
            <br />
            Email: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>
          </>)}
        </Section>

        <footer style={{ marginTop: 60, paddingTop: 24, borderTop: "1px solid rgba(255,255,255,.08)", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12, fontSize: 13, color: "#6E6757" }}>
          <span>&copy; 2026 Mystral</span>
          <div style={{ display: "flex", gap: 16 }}>
            <span style={{ color: "#8A8170" }}>{t("legal.privacy")}</span>
            <Link href="/terms">{t("legal.terms")}</Link>
          </div>
        </footer>
      </main>
    </div>
  );
}

function B({ children }: { children: React.ReactNode }) {
  return <b style={{ color: "#E8CD7E" }}>{children}</b>;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", margin: "32px 0 12px", paddingBottom: 8, borderBottom: "1px solid rgba(201,168,76,.15)" }}>
        {title}
      </h2>
      <div style={{ fontSize: 15, lineHeight: 1.8, color: "#B6AC98" }}>
        {children}
      </div>
    </section>
  );
}

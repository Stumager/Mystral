import { useTranslation } from "react-i18next";
import { Logo } from "../components/Logo";

export function Link({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a href={href} style={{ color: "#C9A84C" }} onMouseEnter={e => (e.currentTarget.style.color = "#E8CD7E")} onMouseLeave={e => (e.currentTarget.style.color = "#C9A84C")}>
      {children}
    </a>
  );
}

export function Terms() {
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
          {ru ? "Пользовательское соглашение и Оферта" : "Terms of Use and Service Agreement"}
        </h1>
        <p style={{ fontSize: 13, color: "#827A69", marginBottom: 40 }}>
          {ru ? "Последнее обновление: 27 июня 2026" : "Last updated: June 27, 2026"}
        </p>

        <Section title={ru ? "1. Предмет соглашения" : "1. Subject of agreement"}>
          {ru ? (<>
            Настоящее Пользовательское соглашение (далее — «Соглашение») регулирует отношения между Самозанятым Нечунаевым Александром Вячеславовичем (далее — «Исполнитель») и пользователем сервиса Mystral (далее — «Пользователь»).
            <br /><br />
            Сервис Mystral предоставляет информационно-развлекательные услуги в сфере астрологии, Таро, нумерологии, рунологии и лунного календаря.
            <br /><br />
            <B>Все материалы и прогнозы Сервиса носят исключительно развлекательный характер и не являются предсказаниями, медицинскими рекомендациями или финансовыми советами.</B>
            <br /><br />
            Использование Сервиса означает полное принятие условий настоящего Соглашения.
          </>) : (<>
            This Terms of Use Agreement (hereinafter referred to as the "Agreement") governs the relationship between the sole proprietor Alexander Nechunaev (hereinafter referred to as the "Provider") and the user of the Mystral service (hereinafter referred to as the "User").
            <br /><br />
            Mystral provides informational and entertainment services in the fields of astrology, Tarot, numerology, runology, and lunar calendar.
            <br /><br />
            <B>All materials and forecasts provided by the Service are for entertainment purposes only and do not constitute predictions, medical advice, or financial recommendations.</B>
            <br /><br />
            By using the Service, you fully accept the terms of this Agreement.
          </>)}
        </Section>

        <Section title={ru ? "2. Условия использования" : "2. Terms of use"}>
          {ru ? (<>
            Для использования Сервиса необходимо:
            <br /><br />
            — зарегистрироваться, указав действительный адрес электронной почты, либо авторизоваться через Telegram;<br />
            — быть старше 18 лет или иметь согласие законного представителя;<br />
            — использовать только один аккаунт на одного пользователя;<br />
            — предоставить достоверные данные при регистрации.
            <br /><br />
            Исполнитель оставляет за собой право заблокировать аккаунт при нарушении условий Соглашения.
          </>) : (<>
            To use the Service, you must:
            <br /><br />
            — register with a valid email address or authenticate via Telegram;<br />
            — be at least 18 years old or have parental/guardian consent;<br />
            — use only one account per person;<br />
            — provide accurate information during registration.
            <br /><br />
            The Provider reserves the right to block accounts that violate these terms.
          </>)}
        </Section>

        <Section title={ru ? "3. Бесплатный и платный доступ" : "3. Free and paid access"}>
          {ru ? (<>
            Сервис работает по модели Freemium:
            <br /><br />
            <B>Free (бесплатный доступ):</B> ежедневный гороскоп, 1 расклад Таро в день, руна дня, базовый нумерологический профиль, лунный календарь.
            <br /><br />
            <B>Pro (платный доступ):</B> безлимитные расклады Таро и рун, полная натальная карта с AI-интерпретацией, глубокая совместимость (синастрия), персональные нумерологические прогнозы, расширенный лунный календарь с AI-рекомендациями, push-уведомления.
          </>) : (<>
            The Service operates on a Freemium model:
            <br /><br />
            <B>Free access:</B> daily horoscope, 1 Tarot spread per day, rune of the day, basic numerology profile, lunar calendar.
            <br /><br />
            <B>Pro access:</B> unlimited Tarot and rune spreads, full natal chart with AI interpretation, deep compatibility (synastry), personal numerology forecasts, extended lunar calendar with AI recommendations, push notifications.
          </>)}
        </Section>

        <Section title={ru ? "4. Оплата и подписка" : "4. Payment and subscription"}>
          {ru ? (<>
            Стоимость подписки Mystral Pro:
            <br /><br />
            — 399 ₽ / месяц<br />
            — 2 999 ₽ / год (экономия ~37%)<br />
            — 199 Telegram Stars / месяц<br />
            — 1 599 Telegram Stars / год
            <br /><br />
            Оплата через банковскую карту (ЮKassa) или Telegram Stars.
            <br /><br />
            Автопродление подписки отсутствует. По истечении оплаченного периода доступ к Pro-функциям приостанавливается.
            <br /><br />
            <B>Возврат средств:</B> возврат возможен в течение 24 часов с момента оплаты при условии, что Pro-функции не были использованы. Для возврата обратитесь на email, указанный в разделе «Реквизиты», или кнопку «Запросить возврат» в разделе Профиль → Подписка.
          </>) : (<>
            Mystral Pro subscription pricing:
            <br /><br />
            — 399 ₽ / month<br />
            — 2,999 ₽ / year (~37% savings)<br />
            — 199 Telegram Stars / month<br />
            — 1,599 Telegram Stars / year
            <br /><br />
            Payment via bank card (YuKassa) or Telegram Stars.
            <br /><br />
            There is no auto-renewal. After the paid period expires, access to Pro features is suspended.
            <br /><br />
            <B>Refunds:</B> refunds are available within 24 hours of payment, provided Pro features have not been used. To request a refund, contact the email listed in the "Details" section, or the "Request refund" button in Profile → Subscription.
          </>)}
        </Section>

        <Section title={ru ? "5. Запрещённые действия" : "5. Prohibited actions"}>
          {ru ? (<>
            Пользователю запрещено:
            <br /><br />
            — перепродавать или передавать доступ к платным функциям третьим лицам;<br />
            — осуществлять автоматический сбор данных (парсинг, скрейпинг) Сервиса;<br />
            — копировать, воспроизводить или распространять контент Сервиса без письменного разрешения;<br />
            — использовать Сервис для любых противоправных целей;<br />
            — создавать множественные аккаунты для обхода ограничений бесплатного плана;<br />
            — намеренно нарушать работоспособность Сервиса.
          </>) : (<>
            Users are prohibited from:
            <br /><br />
            — reselling or sharing access to paid features with third parties;<br />
            — automated data collection (parsing, scraping) of the Service;<br />
            — copying, reproducing, or distributing Service content without written permission;<br />
            — using the Service for any unlawful purposes;<br />
            — creating multiple accounts to circumvent free plan limitations;<br />
            — intentionally disrupting Service operations.
          </>)}
        </Section>

        <Section title={ru ? "6. Ответственность" : "6. Liability"}>
          {ru ? (<>
            Сервис не несёт ответственности за решения, принятые Пользователем на основе астрологических прогнозов, толкований Таро, нумерологических расчётов или иных материалов Сервиса.
            <br /><br />
            Весь контент носит информационно-развлекательный характер. Исполнитель не гарантирует точность или достоверность астрологических прогнозов.
            <br /><br />
            Исполнитель прилагает разумные усилия для обеспечения бесперебойной работы Сервиса, но не гарантирует его доступность 24/7 и не несёт ответственности за временные перебои.
          </>) : (<>
            The Service is not liable for decisions made by the User based on astrological forecasts, Tarot interpretations, numerological calculations, or other Service materials.
            <br /><br />
            All content is for informational and entertainment purposes only. The Provider does not guarantee the accuracy or reliability of astrological forecasts.
            <br /><br />
            The Provider makes reasonable efforts to ensure uninterrupted Service operation but does not guarantee 24/7 availability and is not liable for temporary outages.
          </>)}
        </Section>

        <Section title={ru ? "7. Интеллектуальная собственность" : "7. Intellectual property"}>
          {ru ? (<>
            Дизайн, тексты, программный код, графические элементы, логотип и торговое наименование «Mystral» являются интеллектуальной собственностью Исполнителя и защищены законодательством об авторском праве.
            <br /><br />
            AI-генерированный контент (интерпретации, прогнозы) создаётся индивидуально для каждого Пользователя и предоставляется в рамках лицензии на личное использование.
          </>) : (<>
            The design, text, source code, graphic elements, logo, and trade name "Mystral" are the intellectual property of the Provider and are protected by copyright law.
            <br /><br />
            AI-generated content (interpretations, forecasts) is created individually for each User and is provided under a personal use license.
          </>)}
        </Section>

        <Section title={ru ? "8. Расторжение" : "8. Termination"}>
          {ru ? (<>
            Пользователь может удалить свой аккаунт в любой момент через раздел «Профиль» → «Безопасность» → «Удалить аккаунт».
            <br /><br />
            При удалении аккаунта все персональные данные удаляются безвозвратно в течение 30 дней. Средства за неиспользованный период оплаченной подписки не возвращаются, за исключением случаев, предусмотренных в разделе «Оплата и подписка».
          </>) : (<>
            Users can delete their account at any time via Profile → Security → Delete account.
            <br /><br />
            Upon account deletion, all personal data is permanently removed within 30 days. Funds for unused portions of paid subscriptions are not refunded, except as specified in the "Payment and subscription" section.
          </>)}
        </Section>

        <Section title={ru ? "9. Применимое право" : "9. Governing law"}>
          {ru ? (<>
            Настоящее Соглашение регулируется и толкуется в соответствии с законодательством Российской Федерации.
            <br /><br />
            Все споры и разногласия, возникающие в связи с настоящим Соглашением, разрешаются путём переговоров. При невозможности достижения согласия споры передаются на рассмотрение в суд по месту нахождения Исполнителя.
          </>) : (<>
            This Agreement is governed by and construed in accordance with the laws of the Russian Federation.
            <br /><br />
            All disputes arising in connection with this Agreement shall be resolved through negotiation. If no agreement can be reached, disputes shall be submitted to the court at the location of the Provider.
          </>)}
        </Section>

        <Section title={ru ? "10. Реквизиты" : "10. Details"}>
          {ru ? (<>
            Самозанятый Нечунаев Александр Вячеславович
            <br />
            ИНН: 230307450300
            <br />
            Email: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>
          </>) : (<>
            Alexander Nechunaev, sole proprietor
            <br />
            TIN: 230307450300
            <br />
            Email: <a href="mailto:sasha.nechunaev1234@gmail.com" style={{ color: "#C9A84C" }}>sasha.nechunaev1234@gmail.com</a>
          </>)}
        </Section>

        <footer style={{ marginTop: 60, paddingTop: 24, borderTop: "1px solid rgba(255,255,255,.08)", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12, fontSize: 13, color: "#827A69" }}>
          <span>&copy; 2026 Mystral</span>
          <div style={{ display: "flex", gap: 16 }}>
            <Link href="/privacy">{t("legal.privacy")}</Link>
            <span style={{ color: "#8A8170" }}>{t("legal.terms")}</span>
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

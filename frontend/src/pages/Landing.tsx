import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Logo } from "../components/Logo";
import { ReviewsBlock } from "../components/ReviewsBlock";
import {
  CheckIcon, CompatibilityIcon, MatrixIcon, MoonIcon, NatalIcon,
  NumerologyIcon, PlusIcon, RuneIcon, SparkIcon, SunIcon, TarotIcon, TelegramIcon, ZodiacIcon,
} from "../components/icons/AstroIcons";
import { BirthReading } from "../components/landing/BirthReading";
import { LunarToday } from "../components/landing/LunarToday";
import { ScrollNatalWheel } from "../components/landing/ScrollNatalWheel";
import { StarField } from "../components/landing/StarField";
import { StickyCta } from "../components/landing/StickyCta";
import { TarotDraw } from "../components/landing/TarotDraw";
import { ZodiacMarquee } from "../components/landing/ZodiacMarquee";

const BOT_APP_URL = "https://t.me/Mystrallbot/app";
const BOT_SUPPORT_URL = "https://t.me/Mystrallbot?start=support";
const CONTACT_EMAIL = "sasha.nechunaev1234@gmail.com";

type IconComponent = (p: { size?: number; strokeWidth?: number }) => JSX.Element;

interface Item { Icon: IconComponent; title: string; desc: string; }
interface Step { n: string; title: string; desc: string; }
interface Faq { q: string; a: string; }
interface Advantage { value: string; label: string; desc: string; }

interface Copy {
  pageTitle: string;
  nav: { features: string; pricing: string; reviews: string; faq: string; signIn: string; cta: string };
  hero: {
    eyebrow: string; title: string; titleAccent: string; sub: string;
    ctaPrimary: string; ctaSecondary: string; note: string;
    demoLabel: string; demoSign: string; demoSignKey: string; demoDate: string; demoText: string;
    demoLove: string; demoCareer: string; demoHealth: string;
  };
  reading: { eyebrow: string; title: string; sub: string };
  features: { title: string; sub: string; items: Item[] };
  advantages: { eyebrow: string; title: string; sub: string; items: Advantage[] };
  tarot: { eyebrow: string; title: string };
  steps: { title: string; sub: string; items: Step[] };
  pricing: {
    title: string; sub: string;
    freeLabel: string; freeName: string; freePrice: string; freeItems: string[]; freeCta: string;
    proLabel: string; proName: string; proBadge: string; proPriceMonthly: string; proPriceYearly: string;
    proPriceNote: string; proItems: string[]; proCta: string; starsNote: string;
  };
  reviews: { title: string; sub: string };
  faq: { title: string; items: Faq[] };
  final: { title: string; sub: string; cta: string; ctaSecondary: string };
  footer: { tagline: string; product: string; support: string; legal: string; disclaimer: string; copyright: string };
}

const COPY_RU: Copy = {
  pageTitle: "Mystral — эзотерическая платформа. Гороскопы, Таро, натальная карта",
  nav: { features: "Возможности", pricing: "Тарифы", reviews: "Отзывы", faq: "Вопросы", signIn: "Войти", cta: "Открыть Mystral" },
  hero: {
    eyebrow: "Эзотерическая платформа",
    title: "Узнай, что говорят звёзды —",
    titleAccent: "каждый день",
    sub: "Натальная карта, расклады Таро, нумерология, руны и лунный календарь — персонально для вас, с AI-интерпретацией на русском языке.",
    ctaPrimary: "Открыть в Telegram",
    ctaSecondary: "Войти через email",
    note: "Бесплатно начать · без банковской карты",
    demoLabel: "Пример разбора",
    demoSign: "Дева", demoSignKey: "virgo",
    demoDate: "сегодня",
    demoText: "Звёзды благоволят решительным шагам — Меркурий поддерживает переговоры и важные разговоры. Доверьтесь интуиции во второй половине дня.",
    demoLove: "Любовь", demoCareer: "Карьера", demoHealth: "Здоровье",
  },
  reading: {
    eyebrow: "Попробуйте прямо здесь",
    title: "Ваш знак и число судьбы — за пять секунд",
    sub: "Без регистрации и без карты. Введите дату рождения и посмотрите, как это работает.",
  },
  features: {
    title: "Всё, что нужно для вашего пути",
    sub: "Восемь разделов классической эзотерики в одном приложении — с расчётами и AI-трактовкой на живом русском.",
    items: [
      { Icon: SunIcon,           title: "Гороскоп дня",     desc: "Персональный прогноз по знаку с оценками любви, карьеры и здоровья" },
      { Icon: TarotIcon,         title: "Таро",             desc: "Расклады на 78 картах с подробной AI-трактовкой каждой позиции" },
      { Icon: NatalIcon,         title: "Натальная карта",  desc: "Дома, аспекты, большая тройка и глубокий разбор характера" },
      { Icon: CompatibilityIcon, title: "Совместимость",    desc: "Синастрия для пары по датам, времени и месту рождения" },
      { Icon: NumerologyIcon,    title: "Нумерология",      desc: "Число судьбы, кармические числа и разбор по имени" },
      { Icon: MoonIcon,          title: "Лунный календарь", desc: "Лунный день, фаза, знак Луны и рекомендации на сегодня" },
      { Icon: RuneIcon,          title: "Руны",             desc: "Расклады на рунах Elder Futhark для ответа на важный вопрос" },
      { Icon: MatrixIcon,        title: "Матрица судьбы",   desc: "Матрица по дате рождения — предназначение и энергии" },
    ],
  },
  advantages: {
    eyebrow: "Почему Mystral",
    title: "Глубина, а не общие фразы",
    sub: "Там, где большинство сервисов ограничивается одним абзацем на весь знак, Mystral считает вашу карту целиком.",
    items: [
      { value: "78", label: "карт в колоде", desc: "Полная колода со Старшими и Младшими Арканами — там, где обычно доступны только 22 карты" },
      { value: "10 · 12", label: "планет и домов", desc: "Расчёт по эфемеридам с аспектами и домами, а не один текст на весь знак зодиака" },
      { value: "30", label: "лунных дней", desc: "Своя трактовка и рекомендации на каждый лунный день, а не одна строчка про фазу" },
      { value: "8", label: "разделов в одном месте", desc: "Таро, астрология, нумерология, руны и матрица — вместо пяти разных приложений" },
    ],
  },
  tarot: { eyebrow: "Карта дня", title: "Колода уже перед вами" },
  steps: {
    title: "Как это работает",
    sub: "От первого касания до персонального разбора — меньше минуты.",
    items: [
      { n: "01", title: "Откройте Mystral", desc: "В Telegram одним тапом или через email на сайте — регистрация займёт полминуты" },
      { n: "02", title: "Укажите дату рождения", desc: "Дата, время и место — точность важна для натальной карты и матрицы судьбы" },
      { n: "03", title: "Получайте разборы каждый день", desc: "Персональный гороскоп, лунные подсказки и push-уведомления о важных днях" },
    ],
  },
  pricing: {
    title: "Простые тарифы",
    sub: "Начните бесплатно. Обновитесь до PRO, когда захотите больше глубины.",
    freeLabel: "БЕСПЛАТНО", freeName: "Старт", freePrice: "0 ₽",
    freeItems: ["Гороскоп дня с оценками", "Таро — 1 расклад в день", "Лунный календарь", "Базовая натальная карта"],
    freeCta: "Начать бесплатно",
    proLabel: "MYSTRAL PRO", proName: "Полный доступ", proBadge: "ВЫГОДНО −37% на год",
    proPriceMonthly: "или 399 ₽/мес помесячно", proPriceYearly: "2 999 ₽/год", proPriceNote: "≈ 250 ₽/мес при годовой оплате",
    proItems: ["Безлимитные расклады Таро", "Полная натальная карта с AI-интерпретацией", "Глубокая совместимость — синастрия по всем планетам", "Персональные прогнозы и уведомления каждый день", "Лунный календарь Pro с детальными рекомендациями"],
    proCta: "Оформить PRO",
    starsNote: "В Telegram доступна оплата Telegram Stars — от 199 в месяц",
  },
  reviews: { title: "Что говорят пользователи", sub: "Реальные отзывы из приложения" },
  faq: {
    title: "Частые вопросы",
    items: [
      { q: "Это бесплатно?", a: "Да. Гороскоп дня, лунный календарь и один расклад Таро в день доступны бесплатно без ограничения по времени. PRO снимает лимиты и открывает полную натальную карту, совместимость и безлимитные расклады." },
      { q: "Нужен ли Telegram?", a: "Нет. Mystral работает и как Telegram Mini App, и как обычный сайт с входом по email — доступ и подписка синхронизируются между ними." },
      { q: "Насколько точны прогнозы?", a: "Mystral использует классические астрологические расчёты (эфемериды, дома, аспекты) и AI для интерпретации. Все материалы носят информационно-развлекательный характер и не заменяют профессиональную консультацию." },
      { q: "Как отменить подписку?", a: "В любой момент в разделе «Профиль» → «Подписка» — без обращения в поддержку и без скрытых условий." },
      { q: "Что с моими данными?", a: "Данные хранятся на защищённых серверах в ЕС с шифрованием TLS и не передаются третьим лицам в рекламных целях. Подробнее — в Политике конфиденциальности." },
    ],
  },
  final: { title: "Твои звёзды ждут", sub: "Открой Mystral и получи первый разбор — бесплатно, за минуту.", cta: "Открыть в Telegram", ctaSecondary: "Войти через email" },
  footer: {
    tagline: "Эзотерическая платформа для вашего пути.",
    product: "Продукт", support: "Поддержка", legal: "Документы",
    disclaimer: "Материалы сервиса носят информационно-развлекательный характер и не являются предсказаниями, медицинскими, юридическими или финансовыми консультациями.",
    copyright: "© 2026 Mystral",
  },
};

const COPY_EN: Copy = {
  pageTitle: "Mystral — esoteric platform. Horoscopes, Tarot, natal chart",
  nav: { features: "Features", pricing: "Pricing", reviews: "Reviews", faq: "FAQ", signIn: "Sign in", cta: "Open Mystral" },
  hero: {
    eyebrow: "Esoteric platform",
    title: "Know what the stars are saying —",
    titleAccent: "every day",
    sub: "Natal chart, Tarot spreads, numerology, runes and a lunar calendar — personalized for you, with AI interpretation.",
    ctaPrimary: "Open in Telegram",
    ctaSecondary: "Sign in with email",
    note: "Free to start · no card required",
    demoLabel: "Sample reading",
    demoSign: "Virgo", demoSignKey: "virgo",
    demoDate: "today",
    demoText: "The stars favor decisive moves — Mercury supports negotiations and important conversations. Trust your intuition later in the day.",
    demoLove: "Love", demoCareer: "Career", demoHealth: "Health",
  },
  reading: {
    eyebrow: "Try it right here",
    title: "Your sign and life path in five seconds",
    sub: "No sign-up, no card. Enter your birth date and see how it works.",
  },
  features: {
    title: "Everything you need for your path",
    sub: "Eight sections of classical esoteric practice in one app — with real calculations and AI interpretation.",
    items: [
      { Icon: SunIcon,           title: "Daily horoscope",  desc: "Personal forecast for your sign with love, career and health scores" },
      { Icon: TarotIcon,         title: "Tarot",            desc: "Spreads across 78 cards with a detailed AI reading for every position" },
      { Icon: NatalIcon,         title: "Natal chart",      desc: "Houses, aspects, the big three and a deep personality breakdown" },
      { Icon: CompatibilityIcon, title: "Compatibility",    desc: "Synastry for a couple based on birth date, time and place" },
      { Icon: NumerologyIcon,    title: "Numerology",       desc: "Life path number, karmic numbers and a name-based reading" },
      { Icon: MoonIcon,          title: "Lunar calendar",   desc: "Lunar day, phase, moon sign and recommendations for today" },
      { Icon: RuneIcon,          title: "Runes",            desc: "Elder Futhark rune spreads for answers to important questions" },
      { Icon: MatrixIcon,        title: "Destiny matrix",   desc: "A birth-date matrix — purpose and inner energies" },
    ],
  },
  advantages: {
    eyebrow: "Why Mystral",
    title: "Depth, not generic lines",
    sub: "Where most services stop at one paragraph for your whole sign, Mystral calculates your entire chart.",
    items: [
      { value: "78", label: "cards in the deck", desc: "The full deck with Major and Minor Arcana — where most apps offer only the 22 Majors" },
      { value: "10 · 12", label: "planets and houses", desc: "An ephemeris-based chart with aspects and houses, not one text for a whole sign" },
      { value: "30", label: "lunar days", desc: "Its own reading and guidance for every lunar day, not a single line about the phase" },
      { value: "8", label: "sections in one place", desc: "Tarot, astrology, numerology, runes and the matrix — instead of five separate apps" },
    ],
  },
  tarot: { eyebrow: "Card of the day", title: "The deck is already in front of you" },
  steps: {
    title: "How it works",
    sub: "From the first tap to a personal reading — under a minute.",
    items: [
      { n: "01", title: "Open Mystral", desc: "One tap in Telegram, or sign up with email on the website — takes half a minute" },
      { n: "02", title: "Add your birth details", desc: "Date, time and place — precision matters for the natal chart and destiny matrix" },
      { n: "03", title: "Get daily readings", desc: "A personal horoscope, lunar tips and push notifications for important days" },
    ],
  },
  pricing: {
    title: "Simple pricing",
    sub: "Start for free. Upgrade to PRO whenever you want more depth.",
    freeLabel: "FREE", freeName: "Starter", freePrice: "$0",
    freeItems: ["Daily horoscope with scores", "Tarot — one spread a day", "Lunar calendar", "Basic natal chart"],
    freeCta: "Start for free",
    proLabel: "MYSTRAL PRO", proName: "Full access", proBadge: "SAVE −37% yearly",
    proPriceMonthly: "or $5/mo billed monthly", proPriceYearly: "$32/yr", proPriceNote: "≈ $2.7/mo billed yearly",
    proItems: ["Unlimited Tarot spreads", "Full natal chart with AI interpretation", "Deep compatibility — synastry across all planets", "Personal forecasts and daily notifications", "Lunar calendar Pro with detailed guidance"],
    proCta: "Get PRO",
    starsNote: "Telegram Stars payment available in-app — from 199 a month",
  },
  reviews: { title: "What users say", sub: "Real reviews from inside the app" },
  faq: {
    title: "Frequently asked questions",
    items: [
      { q: "Is it free?", a: "Yes. The daily horoscope, lunar calendar and one Tarot spread a day are free with no time limit. PRO removes the limits and unlocks the full natal chart, compatibility and unlimited spreads." },
      { q: "Do I need Telegram?", a: "No. Mystral works both as a Telegram Mini App and as a regular website with email sign-in — access and subscription sync between the two." },
      { q: "How accurate are the readings?", a: "Mystral uses classical astrological calculations (ephemeris, houses, aspects) plus AI for interpretation. All content is for entertainment and informational purposes and does not replace professional advice." },
      { q: "How do I cancel?", a: "Any time, in Profile → Subscription — no need to contact support, no hidden conditions." },
      { q: "What about my data?", a: "Data is stored on secured EU servers with TLS encryption and is never shared with third parties for advertising. See the Privacy Policy for details." },
    ],
  },
  final: { title: "Your stars are waiting", sub: "Open Mystral and get your first reading — free, in a minute.", cta: "Open in Telegram", ctaSecondary: "Sign in with email" },
  footer: {
    tagline: "An esoteric platform for your path.",
    product: "Product", support: "Support", legal: "Legal",
    disclaimer: "Service content is for entertainment and informational purposes and does not constitute predictions, medical, legal or financial advice.",
    copyright: "© 2026 Mystral",
  },
};

function Reveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { setVisible(true); io.disconnect(); }
    }, { threshold: 0.15 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div ref={ref} style={{
      opacity: visible ? 1 : 0,
      transform: visible ? "translateY(0)" : "translateY(22px)",
      transition: `opacity .7s ease ${delay}s, transform .7s ease ${delay}s`,
    }}>
      {children}
    </div>
  );
}

function Container({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 24px", ...style }}>{children}</div>;
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-cinzel" style={{
      display: "inline-flex", alignItems: "center", gap: 8,
      fontSize: 11.5, letterSpacing: ".28em", color: "#C9A84C", textTransform: "uppercase",
    }}>
      <SparkIcon size={13} strokeWidth={1.4} />
      {children}
    </span>
  );
}

function PrimaryButton({ href, children, big, icon }: { href: string; children: React.ReactNode; big?: boolean; icon?: React.ReactNode }) {
  return (
    <a href={href} target={href.startsWith("http") ? "_blank" : undefined} rel="noopener noreferrer" className="ml-btn-primary"
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 9, textDecoration: "none",
        height: big ? 56 : 48, padding: big ? "0 30px" : "0 24px", borderRadius: 14,
        background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206",
        fontWeight: 600, fontSize: big ? 16 : 14.5, whiteSpace: "nowrap",
        boxShadow: "0 14px 34px -10px rgba(201,168,76,.55)",
      }}>
      {icon}
      {children}
    </a>
  );
}

function SecondaryButton({ href, children, big }: { href: string; children: React.ReactNode; big?: boolean }) {
  return (
    <a href={href} className="ml-btn-secondary"
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8, textDecoration: "none",
        height: big ? 56 : 48, padding: big ? "0 28px" : "0 22px", borderRadius: 14,
        background: "rgba(255,255,255,.04)", color: "#F0E9DA", border: "1px solid rgba(201,168,76,.28)",
        fontWeight: 500, fontSize: big ? 16 : 14.5, whiteSpace: "nowrap",
      }}>
      {children}
    </a>
  );
}

function SectionTitle({ eyebrow, title, sub }: { eyebrow?: string; title: string; sub?: string }) {
  return (
    <div style={{ textAlign: "center", maxWidth: 640, margin: "0 auto 48px" }}>
      {eyebrow && <div style={{ marginBottom: 12 }}><Eyebrow>{eyebrow}</Eyebrow></div>}
      <h2 className="font-cormorant" style={{ fontSize: "clamp(28px,4vw,40px)", color: "#F0E9DA", lineHeight: 1.15 }}>{title}</h2>
      {sub && <p style={{ fontSize: 15.5, color: "#A89E8B", marginTop: 12, lineHeight: 1.6 }}>{sub}</p>}
    </div>
  );
}

export function Landing() {
  const { i18n } = useTranslation();
  const ru = i18n.language === "ru";
  const c = ru ? COPY_RU : COPY_EN;
  const heroRef = useRef<HTMLElement>(null);

  useEffect(() => { document.title = c.pageTitle; }, [c.pageTitle]);

  const openApp = () => window.open(BOT_APP_URL, "_blank", "noopener,noreferrer");

  return (
    // No `overflow-x` here on purpose: any overflow value other than
    // `visible` turns this div into a scroll container, and `position: sticky`
    // descendants then anchor to it instead of the viewport — which silently
    // breaks both the header and the natal-wheel section. The sections that
    // can actually bleed sideways (hero starfield, marquee, final CTA) clip
    // themselves instead.
    <div className="mystral-landing" style={{ minHeight: "100vh", background: "#07060F" }}>
      <style>{`
        .ml-btn-primary:hover { filter: brightness(1.08); transform: translateY(-1px); }
        .ml-btn-secondary:hover { border-color: rgba(201,168,76,.55); background: rgba(255,255,255,.07); }
        .ml-card { transition: transform .25s ease, border-color .25s ease, background .25s ease; }
        .ml-card:hover { transform: translateY(-4px); border-color: rgba(201,168,76,.34); }
        .ml-nav-link { color: #B6AC98; text-decoration: none; font-size: 14px; transition: color .2s ease; }
        .ml-nav-link:hover { color: #E8CD7E; }
        .ml-faq summary { cursor: pointer; list-style: none; }
        .ml-faq summary::-webkit-details-marker { display: none; }
        .ml-faq .chev { transition: transform .25s ease; }
        .ml-faq[open] .chev { transform: rotate(45deg); }
      `}</style>

      <Header c={c} />
      <Hero c={c} heroRef={heroRef} />
      <ZodiacMarquee ru={ru} />
      <ReadingSection c={c} ru={ru} onOpenApp={openApp} />
      <Features c={c} />
      <Advantages c={c} />
      <ScrollNatalWheel ru={ru} />
      <TarotSection c={c} ru={ru} onOpenApp={openApp} />
      <LunarSection ru={ru} />
      <Steps c={c} />
      <Pricing c={c} />
      <ReviewsSection c={c} />
      <FaqSection c={c} />
      <FinalCta c={c} />
      <Footer c={c} />
      <StickyCta ru={ru} watchRef={heroRef} appUrl={BOT_APP_URL} />
    </div>
  );
}

function Header({ c }: { c: Copy }) {
  return (
    <header style={{ position: "sticky", top: 0, zIndex: 40, background: "rgba(7,6,15,.78)", backdropFilter: "blur(14px)", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
      <Container style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 68 }}>
        <a href="/landing" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <Logo size={26} />
          <span className="font-cinzel" style={{ fontSize: 14, letterSpacing: ".3em", color: "#E8CD7E" }}>MYSTRAL</span>
        </a>
        <nav className="hidden lg:flex" style={{ gap: 32, alignItems: "center" }}>
          <a className="ml-nav-link" href="#features">{c.nav.features}</a>
          <a className="ml-nav-link" href="#pricing">{c.nav.pricing}</a>
          <a className="ml-nav-link" href="#reviews">{c.nav.reviews}</a>
          <a className="ml-nav-link" href="#faq">{c.nav.faq}</a>
        </nav>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <a href="/" className="hidden lg:inline-flex ml-nav-link" style={{ padding: "8px 16px", borderRadius: 10, border: "1px solid rgba(201,168,76,.25)" }}>
            {c.nav.signIn}
          </a>
          <PrimaryButton href={BOT_APP_URL}>{c.nav.cta}</PrimaryButton>
        </div>
      </Container>
    </header>
  );
}

function Hero({ c, heroRef }: { c: Copy; heroRef: React.RefObject<HTMLElement> }) {
  return (
    <section ref={heroRef} style={{ position: "relative", padding: "76px 0 56px", overflow: "hidden" }}>
      <div aria-hidden style={{ position: "absolute", inset: 0, background: "radial-gradient(120% 55% at 50% -10%, #1C1650 0%, #0F0A26 42%, #07060F 78%)", pointerEvents: "none" }} />
      <StarField />

      <Container style={{ position: "relative" }}>
        <div className="grid lg:grid-cols-2" style={{ gap: 48, alignItems: "center" }}>
          <div>
            <div style={{ marginBottom: 18 }}><Eyebrow>{c.hero.eyebrow}</Eyebrow></div>
            <h1 className="font-cormorant" style={{ fontSize: "clamp(38px,5.5vw,60px)", lineHeight: 1.08, color: "#F0E9DA" }}>
              {c.hero.title}{" "}
              <span style={{ background: "linear-gradient(100deg,#A9882F,#E8CD7E)", WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>
                {c.hero.titleAccent}
              </span>
            </h1>
            <p style={{ fontSize: 17, lineHeight: 1.65, color: "#A89E8B", marginTop: 20, maxWidth: 480 }}>{c.hero.sub}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 14, marginTop: 30 }}>
              <PrimaryButton href={BOT_APP_URL} big icon={<TelegramIcon size={19} strokeWidth={1.6} />}>{c.hero.ctaPrimary}</PrimaryButton>
              <SecondaryButton href="/" big>{c.hero.ctaSecondary}</SecondaryButton>
            </div>
            <p style={{ fontSize: 12.5, color: "#6E6757", marginTop: 16 }}>{c.hero.note}</p>
          </div>

          <Reveal>
            <div style={{ position: "relative", padding: 26, borderRadius: 24, background: "linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.015))", border: "1px solid rgba(201,168,76,.2)", backdropFilter: "blur(12px)", boxShadow: "0 30px 80px -30px rgba(75,60,134,.5)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".26em", color: "#C9A84C" }}>{c.hero.demoLabel}</span>
                <span style={{ fontSize: 11, color: "#827A69" }}>{c.hero.demoDate}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 16 }}>
                <div style={{ width: 52, height: 52, flexShrink: 0, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", display: "flex", alignItems: "center", justifyContent: "center", color: "#0C0A18" }}>
                  <ZodiacIcon sign={c.hero.demoSignKey} size={28} strokeWidth={1.6} />
                </div>
                <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA" }}>{c.hero.demoSign}</p>
              </div>
              <p style={{ marginTop: 16, fontSize: 14.5, lineHeight: 1.72, color: "#D7CFBE" }}>{c.hero.demoText}</p>
              <div className="grid grid-cols-3" style={{ gap: 10, marginTop: 20 }}>
                {[
                  { label: c.hero.demoLove, value: 82, color: "#C9A84C" },
                  { label: c.hero.demoCareer, value: 65, color: "#8A7FC0" },
                  { label: c.hero.demoHealth, value: 74, color: "#6E9A8A" },
                ].map(b => (
                  <div key={b.label}>
                    <div className="flex justify-between" style={{ fontSize: 11, marginBottom: 4 }}>
                      <span style={{ color: "#8A8170" }}>{b.label}</span>
                      <span style={{ color: b.color }}>{b.value}%</span>
                    </div>
                    <div style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,.07)", overflow: "hidden" }}>
                      <div style={{ width: `${b.value}%`, height: "100%", borderRadius: 99, background: `linear-gradient(90deg,${b.color}99,${b.color})`, boxShadow: `0 0 10px ${b.color}80` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </Container>
    </section>
  );
}

function ReadingSection({ c, ru, onOpenApp }: { c: Copy; ru: boolean; onOpenApp: () => void }) {
  return (
    <section style={{ padding: "88px 0 40px" }}>
      <Container style={{ maxWidth: 900 }}>
        <Reveal><SectionTitle eyebrow={c.reading.eyebrow} title={c.reading.title} sub={c.reading.sub} /></Reveal>
        <Reveal delay={0.08}><BirthReading ru={ru} onOpenApp={onOpenApp} /></Reveal>
      </Container>
    </section>
  );
}

function Features({ c }: { c: Copy }) {
  return (
    <section id="features" style={{ padding: "88px 0 40px" }}>
      <Container>
        <Reveal><SectionTitle title={c.features.title} sub={c.features.sub} /></Reveal>
        <div className="grid grid-cols-2 lg:grid-cols-4" style={{ gap: 16 }}>
          {c.features.items.map((f, i) => (
            <Reveal key={f.title} delay={(i % 4) * 0.06}>
              <div className="ml-card" style={{ height: "100%", padding: 22, borderRadius: 18, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.07)" }}>
                <div style={{ width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 12, background: "rgba(201,168,76,.1)", border: "1px solid rgba(201,168,76,.26)", color: "#C9A84C", marginBottom: 14 }}>
                  <f.Icon size={22} strokeWidth={1.4} />
                </div>
                <p className="font-cormorant" style={{ fontSize: 19, color: "#F0E9DA" }}>{f.title}</p>
                <p style={{ fontSize: 13, lineHeight: 1.6, color: "#8A8170", marginTop: 6 }}>{f.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}

function Advantages({ c }: { c: Copy }) {
  return (
    <section style={{ padding: "88px 0 40px" }}>
      <Container>
        <Reveal><SectionTitle eyebrow={c.advantages.eyebrow} title={c.advantages.title} sub={c.advantages.sub} /></Reveal>
        <div className="grid grid-cols-2 lg:grid-cols-4" style={{ gap: 16 }}>
          {c.advantages.items.map((a, i) => (
            <Reveal key={a.label} delay={(i % 4) * 0.07}>
              <div style={{
                height: "100%", padding: 24, borderRadius: 20, textAlign: "center",
                background: "radial-gradient(120% 100% at 50% 0%, rgba(28,22,80,.5) 0%, rgba(255,255,255,.012) 60%)",
                border: "1px solid rgba(201,168,76,.16)",
              }}>
                <p className="font-cormorant" style={{
                  fontSize: 44, lineHeight: 1,
                  background: "linear-gradient(100deg,#A9882F,#E8CD7E)",
                  WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
                }}>{a.value}</p>
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", marginTop: 8 }}>{a.label}</p>
                <p style={{ fontSize: 13, lineHeight: 1.6, color: "#8A8170", marginTop: 10 }}>{a.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}

function TarotSection({ c, ru, onOpenApp }: { c: Copy; ru: boolean; onOpenApp: () => void }) {
  return (
    <section style={{ padding: "60px 0 40px" }}>
      <Container>
        <Reveal><SectionTitle eyebrow={c.tarot.eyebrow} title={c.tarot.title} /></Reveal>
        <Reveal delay={0.08}>
          <div style={{
            padding: "34px 30px", borderRadius: 26,
            background: "radial-gradient(120% 100% at 50% 0%, #16103C 0%, #0B0920 60%, transparent 100%)",
            border: "1px solid rgba(201,168,76,.2)",
          }}>
            <TarotDraw ru={ru} onOpenApp={onOpenApp} />
          </div>
        </Reveal>
      </Container>
    </section>
  );
}

function LunarSection({ ru }: { ru: boolean }) {
  return (
    <section style={{ padding: "60px 0 40px" }}>
      <Container style={{ maxWidth: 900 }}>
        <Reveal><LunarToday ru={ru} /></Reveal>
      </Container>
    </section>
  );
}

function Steps({ c }: { c: Copy }) {
  return (
    <section style={{ padding: "80px 0 40px" }}>
      <Container>
        <Reveal><SectionTitle title={c.steps.title} sub={c.steps.sub} /></Reveal>
        <div className="grid lg:grid-cols-3" style={{ gap: 20 }}>
          {c.steps.items.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.08}>
              <div style={{ padding: 26, borderRadius: 20, background: "linear-gradient(160deg,rgba(255,255,255,.04),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.14)", height: "100%" }}>
                <span className="font-cormorant" style={{ fontSize: 40, color: "rgba(201,168,76,.4)" }}>{s.n}</span>
                <p className="font-cormorant" style={{ fontSize: 21, color: "#F0E9DA", marginTop: 4 }}>{s.title}</p>
                <p style={{ fontSize: 14, lineHeight: 1.6, color: "#8A8170", marginTop: 8 }}>{s.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}

function Pricing({ c }: { c: Copy }) {
  return (
    <section id="pricing" style={{ padding: "88px 0 40px" }}>
      <Container>
        <Reveal><SectionTitle title={c.pricing.title} sub={c.pricing.sub} /></Reveal>
        <div className="grid lg:grid-cols-2" style={{ gap: 22, maxWidth: 860, margin: "0 auto" }}>
          <Reveal>
            <div style={{ height: "100%", padding: 30, borderRadius: 22, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.08)" }}>
              <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".24em", color: "#8A8170" }}>{c.pricing.freeLabel}</span>
              <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", marginTop: 6 }}>{c.pricing.freeName}</p>
              <p className="font-cormorant" style={{ fontSize: 42, color: "#F0E9DA", marginTop: 10 }}>{c.pricing.freePrice}</p>
              <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 22 }}>
                {c.pricing.freeItems.map(item => (
                  <div key={item} style={{ display: "flex", alignItems: "flex-start", gap: 9, fontSize: 13.5, color: "#B6AC98" }}>
                    <span style={{ color: "#6E9A8A", flexShrink: 0, marginTop: 1 }}><CheckIcon size={15} strokeWidth={1.8} /></span>{item}
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 24 }}><SecondaryButton href={BOT_APP_URL}>{c.pricing.freeCta}</SecondaryButton></div>
            </div>
          </Reveal>

          <Reveal delay={0.08}>
            <div style={{ position: "relative", height: "100%", padding: 30, borderRadius: 22, background: "radial-gradient(120% 100% at 50% 0%, #1C1650 0%, #0F0A2E 55%, transparent 100%)", border: "1px solid rgba(201,168,76,.4)", boxShadow: "0 0 60px rgba(201,168,76,.1)" }}>
              <span style={{ position: "absolute", top: -12, left: 26, fontSize: 10, letterSpacing: ".1em", fontWeight: 600, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", padding: "4px 12px", borderRadius: 99 }}>
                {c.pricing.proBadge}
              </span>
              <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".24em", color: "#C9A84C" }}>{c.pricing.proLabel}</span>
              <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", marginTop: 6 }}>{c.pricing.proName}</p>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 10 }}>
                <span className="font-cormorant" style={{ fontSize: 42, color: "#F0E9DA" }}>{c.pricing.proPriceYearly}</span>
              </div>
              <p style={{ fontSize: 12, color: "#827A69", marginTop: 2 }}>{c.pricing.proPriceNote} · {c.pricing.proPriceMonthly}</p>
              <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 22 }}>
                {c.pricing.proItems.map(item => (
                  <div key={item} style={{ display: "flex", alignItems: "flex-start", gap: 9, fontSize: 13.5, color: "#D7CFBE" }}>
                    <span style={{ color: "#E8CD7E", flexShrink: 0, marginTop: 1 }}><SparkIcon size={15} strokeWidth={1.4} /></span>{item}
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 24 }}><PrimaryButton href={BOT_APP_URL}>{c.pricing.proCta}</PrimaryButton></div>
              <p style={{ fontSize: 11.5, color: "#6E6757", marginTop: 12 }}>{c.pricing.starsNote}</p>
            </div>
          </Reveal>
        </div>
      </Container>
    </section>
  );
}

function ReviewsSection({ c }: { c: Copy }) {
  return (
    <section id="reviews" style={{ padding: "88px 0 40px" }}>
      <Container style={{ maxWidth: 760 }}>
        <Reveal><SectionTitle title={c.reviews.title} sub={c.reviews.sub} /></Reveal>
        <Reveal delay={0.1}><ReviewsBlock /></Reveal>
      </Container>
    </section>
  );
}

function FaqSection({ c }: { c: Copy }) {
  return (
    <section id="faq" style={{ padding: "88px 0 40px" }}>
      <Container style={{ maxWidth: 760 }}>
        <Reveal><SectionTitle title={c.faq.title} /></Reveal>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {c.faq.items.map((item, i) => (
            <Reveal key={item.q} delay={i * 0.05}>
              <details className="ml-faq" style={{ padding: "18px 22px", borderRadius: 16, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.07)" }}>
                <summary style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                  <span className="font-cormorant" style={{ fontSize: 18, color: "#F0E9DA" }}>{item.q}</span>
                  <span className="chev" style={{ flexShrink: 0, color: "#C9A84C", display: "flex" }}><PlusIcon size={17} strokeWidth={1.6} /></span>
                </summary>
                <p style={{ fontSize: 14, lineHeight: 1.65, color: "#A89E8B", marginTop: 12 }}>{item.a}</p>
              </details>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}

function FinalCta({ c }: { c: Copy }) {
  return (
    <section style={{ padding: "40px 0 100px" }}>
      <Container>
        <Reveal>
          <div style={{ position: "relative", overflow: "hidden", textAlign: "center", padding: "64px 24px", borderRadius: 28, background: "radial-gradient(120% 140% at 50% 0%, #1C1650 0%, #0F0A2E 55%, #07060F 100%)", border: "1px solid rgba(201,168,76,.28)" }}>
            <div aria-hidden style={{ position: "absolute", top: -60, left: "50%", transform: "translateX(-50%)", width: 300, height: 300, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.18),transparent 68%)" }} />
            <div style={{ position: "relative" }}>
              <div style={{ display: "inline-block", filter: "drop-shadow(0 0 30px rgba(201,168,76,.5))", animation: "mystral-float 7s ease-in-out infinite" }}>
                <Logo size={64} />
              </div>
              <h2 className="font-cormorant" style={{ fontSize: "clamp(28px,4.5vw,42px)", color: "#F0E9DA", marginTop: 18 }}>{c.final.title}</h2>
              <p style={{ fontSize: 15.5, color: "#A89E8B", marginTop: 10 }}>{c.final.sub}</p>
              <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 14, marginTop: 30 }}>
                <PrimaryButton href={BOT_APP_URL} big icon={<TelegramIcon size={19} strokeWidth={1.6} />}>{c.final.cta}</PrimaryButton>
                <SecondaryButton href="/" big>{c.final.ctaSecondary}</SecondaryButton>
              </div>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  );
}

function Footer({ c }: { c: Copy }) {
  return (
    // The sticky CTA bar floats over the page bottom; without this the last
    // footer line sits underneath it on short viewports.
    <footer style={{ borderTop: "1px solid rgba(255,255,255,.06)", padding: "48px 0 120px" }}>
      <Container>
        <div className="grid lg:grid-cols-4" style={{ gap: 32 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Logo size={24} />
              <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".28em", color: "#E8CD7E" }}>MYSTRAL</span>
            </div>
            <p style={{ fontSize: 13, color: "#827A69", marginTop: 12, maxWidth: 220 }}>{c.footer.tagline}</p>
          </div>
          <FooterCol title={c.footer.product} links={[
            { label: c.nav.features, href: "#features" },
            { label: c.nav.pricing, href: "#pricing" },
            { label: c.nav.reviews, href: "#reviews" },
          ]} />
          <FooterCol title={c.footer.support} links={[
            { label: c.nav.faq, href: "#faq" },
            { label: "Telegram", href: BOT_SUPPORT_URL, external: true },
            { label: CONTACT_EMAIL, href: `mailto:${CONTACT_EMAIL}` },
          ]} />
          <FooterCol title={c.footer.legal} links={[
            { label: "Privacy Policy", href: "/privacy" },
            { label: "Terms", href: "/terms" },
          ]} />
        </div>
        <p style={{ fontSize: 11.5, lineHeight: 1.6, color: "#5A5347", marginTop: 40, maxWidth: 720 }}>{c.footer.disclaimer}</p>
        <p style={{ fontSize: 12.5, color: "#6E6757", marginTop: 16 }}>{c.footer.copyright}</p>
      </Container>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: { label: string; href: string; external?: boolean }[] }) {
  return (
    <div>
      <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".2em", color: "#8A8170" }}>{title}</span>
      <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 14 }}>
        {links.map(l => (
          <a key={l.label} href={l.href} target={l.external ? "_blank" : undefined} rel={l.external ? "noopener noreferrer" : undefined} className="ml-nav-link">
            {l.label}
          </a>
        ))}
      </div>
    </div>
  );
}

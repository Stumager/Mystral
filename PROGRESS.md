# Mystral — прогресс разработки

## 2026-06-18 — TZ-001: Инициализация проекта

- **Сделано:**
  - Создана полная структура проекта (43 файла)
  - `backend/` — FastAPI + SQLModel + Alembic + asyncpg + redis
    - `app/models/user.py` — User, AuthProvider, UserProfile, UserPartner (UUID PK, SQLModel)
    - `app/core/` — config (pydantic-settings), database (async engine + session), redis (asyncio client)
    - `app/api/v1/health.py` — GET /health → {"status": "ok", "service": "mystral"}
    - `app/api/v1/auth.py` — заглушки /auth/telegram, /refresh, /logout
    - `app/migrations/` — Alembic env.py с async engine, script.py.mako
    - `backend/Dockerfile` — запуск: alembic upgrade head → uvicorn
  - `frontend/` — React 18 + Vite + TypeScript + Tailwind + i18next
    - `src/i18n/` — ru.json + en.json, initReactI18next
    - `src/utils/telegram.ts` — isTMA(): boolean
    - `package.json` — все зависимости прописаны
  - `bot/` — aiogram 3.x skeleton, /start команда с WebApp кнопкой
  - `nginx/nginx.conf` — proxy → backend:8000, frontend:5173, WebSocket upgrade
  - `docker-compose.yml` — postgres:16 + redis:7 + backend + frontend + bot + nginx
    - healthcheck на postgres и redis, depends_on с condition: service_healthy
  - `.env.example` + `.env` (скопирован из example)
  - `.gitignore` — Python, Node, env, IDE

- **Найдено проблем:**
  - Нет. Структура чистая, нет circular imports.

- **Следующий шаг:**
  - TZ-002 (дизайн-система): см. ниже

## 2026-06-18 — TZ-002: Дизайн-система Mystral (фикс Dockerfile + дизайн-токены)

- **Сделано:**
  - `backend/Dockerfile` — Python 3.11-slim, добавлены build-essential/gcc/libssl-dev для pyswisseph
  - `tailwind.config.ts` — кастомная палитра: bg/violet/gold/text/border + шрифты display/sans
  - `src/styles/globals.css` — CSS-переменные, Google Fonts (Cormorant Garamond), body стили
  - `src/components/ui/Button.tsx` — variant: primary/gold/ghost, size: sm/md
  - `src/components/ui/Card.tsx` — glassmorphism карточка с border-subtle
  - `src/components/ui/Badge.tsx` — FREE (violet) / PRO (gold)
  - `src/components/ui/BottomNav.tsx` — фикс. навигация, 4 пункта, активный элемент с точкой (lucide-react)
  - `src/components/ui/index.ts` — реэкспорт всех UI компонентов
  - `src/App.tsx` — тёмный фон, "✦ Mystral" Cormorant Garamond, max-w-[390px], BottomNav
  - `package.json` — добавлен lucide-react

- **Найдено проблем:**
  - TS ошибка: кастомный тип иконки не совместим с LucideIcon (size: string|number vs number) — исправлен импортом LucideIcon напрямую

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `vite build` — ✓ 1538 modules, 3.11s

- **Следующий шаг:**
  - TZ-003 (Three.js + Home): см. ниже

## 2026-06-18 — TZ-003: Главный экран — Three.js орба + layout

- **Сделано:**
  - `package.json` — добавлены three@^0.167.0 + @types/three@^0.167.0
  - `src/components/three/ZodiacOrb.tsx` — Three.js орба:
    - 120 звёзд (PointsMaterial opacity 0.6)
    - SphereGeometry orb (violet-600, emissive)
    - 2 кольца TorusGeometry с точками-спутниками
    - AmbientLight 0.3 + PointLight violet
    - requestAnimationFrame с camera.position.y oscillation
    - renderer.dispose() cleanup
    - HTML overlay: символ знака по центру canvas (font-display 56px)
  - `src/components/ui/BottomNav.tsx` — добавлен optional `active` prop (controlled/uncontrolled)
  - `src/pages/Home.tsx` — полный главный экран:
    - Header 46px с backdrop-blur, пульсирующая точка
    - Приветствие с font-display
    - ZodiacOrb (Скорпион ♏) по центру
    - Карточка гороскопа с AI-бейджем
    - Сетка 2×3 инструментов (Таро/Луна/Натальная/Совместимость/Нумерология/Руны)
  - `src/App.tsx` — рендерит <Home />

- **Найдено проблем:**
  - Предупреждение Vite: чанк 667KB (Three.js). Не ошибка, ожидаемо. При необходимости — dynamic import().

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `vite build` — ✓ 1541 modules, 5.22s

- **Следующий шаг:**
  - TZ-004 (Таро): см. ниже

## 2026-06-18 — TZ-004: Экран Таро — 3D flip + расклад

- **Сделано:**
  - `src/data/tarot.ts` — 22 карты Старших Арканов + тип TarotCardData + drawCards()
  - `src/components/tarot/TarotCard.tsx` — CSS 3D flip (perspective/preserve-3d/backfaceVisibility):
    - Рубашка: gradient #1B0C4A→#080316, золотой ✦ + MYSTRAL 8px
    - Лицевая: gradient #1E0E50→#0D0520, номер/символ/название, инсет-рамка
    - Transition 0.7s ease с поддержкой delay prop
  - `src/pages/Tarot.tsx` — полный экран расклада:
    - 3 карты с rotations [-8,0,8]°, клик по карте открывает её
    - Кнопка "Получить толкование" появляется после открытия всех 3
    - Имитация стриминга (посимвольно, 30ms задержка)
    - Кнопка "Новый расклад" — перетасовка и сброс
  - `src/components/ui/BottomNav.tsx` — добавлен `onNavigate` prop
  - `src/pages/Home.tsx` — клик по тулам вызывает onNavigate(tool.id)
  - `src/App.tsx` — useState роутинг: home | tarot | moon | profile

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `vite build` — ✓ 64 modules, 2.92s

- **Следующий шаг:**
  - TZ-005 (Groq): см. ниже

## 2026-06-18 — TZ-005: Groq horoscope endpoint

- **Сделано:**
  - `backend/requirements.txt` — добавлен groq==0.9.0
  - `backend/app/api/v1/horoscope.py` — SSE стриминг endpoint:
    - POST /v1/horoscope/stream
    - Модель: llama-3.3-70b-versatile
    - Поддержка lang: ru/en с разным tone prompt
    - 22 знака зодиака (en→ru маппинг)
    - StreamingResponse, media_type text/event-stream
    - Формат чанков: `data: {"text": "..."}` + `data: [DONE]`
  - `backend/app/api/router.py` — подключён horoscope_router с prefix="/v1"
  - `.env` — плейсхолдер GROQ_API_KEY= уже был, Саша заполнит вручную

- **Найдено нюансов:**
  - Health endpoint остался на `/health` (без `/v1`). Через nginx: `GET /api/health`.
    Задача упоминала `/api/v1/health` — это опечатка, реальный путь `/api/health`.
  - Groq streaming использует sync iterator внутри async generator — корректно для
    данного объёма запросов, при необходимости можно обернуть в run_in_executor.

- **Следующий шаг:**
  - TZ-006 (Groq фронтенд): см. ниже

## 2026-06-18 — TZ-006: Подключение реального Groq к фронтенду

- **Сделано:**
  - `frontend/src/utils/api.ts` — SSE хелпер streamRequest():
    - fetch + ReadableStream reader, TextDecoder
    - Парсинг `data: {...}` / `data: [DONE]`
    - VITE_API_URL из import.meta.env (пустая строка = same origin)
  - `frontend/src/vite-env.d.ts` — добавлен (не было), `/// <reference types="vite/client" />`
  - `backend/app/api/v1/tarot.py` — POST /v1/tarot/interpret, SSE стриминг, 80-100 слов
  - `backend/app/api/router.py` — подключён tarot_router с prefix="/v1"
  - `frontend/src/pages/Tarot.tsx` — handleInterpret теперь вызывает реальный API
  - `frontend/src/pages/Home.tsx` — useEffect загружает гороскоп при монтировании,
    статус "Звёзды говорят..." → стриминг → финальный текст; дата из new Date()
  - `frontend/.env` — создан, VITE_API_URL= (пустая строка, same origin)

- **Найдено проблем:**
  - TS2339: `import.meta.env` не типизирован — исправлен добавлением `vite-env.d.ts`

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `vite build` — ✓ 65 modules, 2.72s

- **Следующий шаг:**
  - TZ-007 (Auth): см. ниже

## 2026-06-18 — TZ-007: Авторизация — Telegram TMA + Email + JWT

- **Сделано:**
  - `backend/app/core/security.py` — hash/verify password (bcrypt), create/decode JWT (30 дней),
    validate_telegram_hash (HMAC-SHA256 по Telegram WebApp spec)
  - `backend/app/core/deps.py` — get_current_user (HTTPBearer → JWT → User)
  - `backend/app/core/database.py` — переключён на sqlmodel.ext.asyncio.session.AsyncSession
    (поддержка session.exec(select(...)))
  - `backend/app/models/user.py` — добавлен password_hash: Optional[str] в AuthProvider
  - `backend/app/api/v1/auth.py` — 4 эндпоинта:
    POST /v1/auth/telegram, POST /v1/auth/register, POST /v1/auth/login, GET /v1/auth/me
  - `backend/app/api/router.py` — auth router перенесён под prefix="/v1"
  - `backend/app/main.py` — lifespan вызывает create_db_and_tables() при старте
  - `frontend/src/context/AuthContext.tsx` — TMA auto-login → localStorage → LoginScreen
  - `frontend/src/pages/LoginScreen.tsx` — переключатель Войти/Регистрация, email+pass
  - `frontend/src/App.tsx` — AuthProvider wrapper, loading splash, !user → LoginScreen
  - `frontend/src/pages/Home.tsx` — user?.name вместо хардкода "Александра"

- **Найдено нюансов:**
  - `Redis.aclose()` не существует в redis-py 5.x — ошибка при shutdown, не при старте.
    Фикс: заменить на `await redis_client.close()` в redis.py (не критично сейчас)

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `docker-compose restart backend` — Application startup complete ✓
  - Таблицы создаются автоматически через create_db_and_tables() при старте

- **Следующий шаг:**
  - Открыть localhost:5173 → LoginScreen → зарегистрироваться → главный экран
  - TZ-009: Лунный календарь (страница Moon)

## 2026-06-18 — TZ-008: Redis кэш + Натальная карта

- **Сделано:**
  - `frontend/src/pages/Home.tsx` — добавлен `useRef(false)` guard в useEffect (StrictMode fix)
  - `backend/app/api/v1/natal.py` — два эндпоинта:
    - POST /v1/natal/calculate — геокодинг Nominatim → kerykeion AstrologicalSubject(online=False)
      → JSON: sun/moon/rising (sign + degree), mercury/venus/mars (sign)
    - POST /v1/natal/interpret — то же + SSE стриминг Groq (100-120 слов, мягкий тон)
    - SIGNS_RU: 3-буквенные и полные названия (Ari/Aries → Овен и т.д.)
  - `backend/app/api/router.py` — natal_router подключён с prefix="/v1"
  - `frontend/src/pages/NatalChart.tsx` — двухшаговый экран:
    - Шаг 1: форма (имя, дата 3-в-ряд, время 2-в-ряд, город)
    - Шаг 2: "Большая тройка" (gold) + планеты + SSE интерпретация
  - `frontend/src/App.tsx` — тип Page: добавлен 'natal', рендер NatalChart
  - `backend/app/core/redis.py` — исправлен `aclose()` → `close()` (redis-py 5.x)

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `docker-compose restart backend` — Application startup complete ✓
  - aclose() ошибка при shutdown устранена

- **Следующий шаг:**
  - TZ-009: Профиль пользователя ✓ (выполнен ниже)
  - TZ-010: Лунный календарь (страница Moon)
  - Alembic миграции (вместо create_all)

## 2026-06-18 — TZ-009: Профиль пользователя + сохранение данных рождения

- **Сделано:**
  - `backend/app/api/v1/profile.py` — GET /v1/profile + PUT /v1/profile:
    - GET: возвращает UserProfile + completion_percent (filled/4 * 100)
    - PUT: birth_date (str→date), birth_time (str→time), birth_city, birth_name→birth_name_enc, lang→User.lang
    - `_get_or_create`: создаёт пустой профиль если не существует
  - `backend/app/api/router.py` — profile_router подключён
  - `frontend/src/pages/Profile.tsx` — экран профиля:
    - Аватар с первой буквой имени (violet bg)
    - Знак зодиака из birth_date (getZodiacSign helper)
    - Прогресс-бар (completion_percent из API)
    - Форма данных рождения (день/месяц/год, час/мин, город, имя)
    - Переключатель языка RU/EN → PUT /profile {lang}
    - Кнопка "Выйти" → logout()
    - Toast "Сохранено ✦" (2.5 сек)
  - `frontend/src/pages/NatalChart.tsx` — интеграция с профилем:
    - useEffect: GET /profile при открытии → auto-fill полей
    - Чекбокс "Сохранить в профиль" (default true)
    - После расчёта: PUT /profile если checked
  - `frontend/src/App.tsx` — Profile добавлен в импорт и маршрут

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `docker-compose restart backend` — Application startup complete ✓

- **Следующий шаг:**
  - TZ-010: Монетизация ✓ (выполнен ниже)
  - TZ-011: Лунный календарь (страница Moon)
  - Alembic миграции (вместо create_all)

## 2026-06-18 — TZ-010: Монетизация — лимиты + Telegram Stars + ЮKassa

- **Сделано:**
  - `backend/app/api/v1/tarot.py` — requires auth + daily limit:
    - `tarot_daily:{user_id}:{today}` TTL 86400 → free:1/день, >1 → 402 FREE_LIMIT_REACHED
  - `backend/app/api/v1/natal.py` — requires auth + total limit:
    - `natal_count:{user_id}` (no TTL) → free:3 total, >3 → 402 FREE_LIMIT_REACHED
  - `backend/app/api/v1/payments.py` — 4 эндпоинта:
    - POST /v1/payments/stars/create — createInvoiceLink через Telegram Bot API (XTR)
    - POST /v1/payments/stars/confirm — обновляет subscription_tier='pro'
    - POST /v1/payments/yukassa/create — создаёт платёж YuKassa, возвращает payment_url
    - POST /v1/payments/yukassa/webhook — обрабатывает payment.succeeded
  - `backend/app/core/config.py` + `.env` — YUKASSA_SHOP_ID, YUKASSA_SECRET_KEY
  - `backend/app/api/v1/auth.py` — tier добавлен в _user_response и /auth/me
  - `backend/app/api/router.py` — payments_router подключён
  - `frontend/src/utils/api.ts` — streamRequest: 5й аргумент token, 402→{code}; apiRequest<T>
  - `frontend/src/context/AuthContext.tsx` — UserData.tier; updateUser()
  - `frontend/src/components/PaywallSheet.tsx` — bottom sheet, Stars/YuKassa flow
  - `frontend/src/pages/Tarot.tsx` — token в streamRequest; FREE_LIMIT_REACHED → paywall
  - `frontend/src/pages/NatalChart.tsx` — то же для интерпретации
  - `frontend/src/pages/Profile.tsx` — free→кнопка Pro; pro→бейдж

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `docker-compose restart backend` — Application startup complete ✓

- **Следующий шаг:**
  - TZ-011: Production deploy ✓ (выполнен ниже)
  - TZ-012: Лунный календарь (страница Moon)
  - Alembic миграции (вместо create_all)

## 2026-06-18 — TZ-011: Production деплой

- **Сделано:**
  - `docker-compose.prod.yml` — external network shared_infra (sweetsin_default), nginx 8080:80
  - `frontend/Dockerfile.prod` — node:20-alpine build → nginx:alpine serve
  - `frontend/nginx.conf` — SPA routing + /api/ → backend:8000
  - `nginx/nginx.prod.conf` — /api/ → backend, / → frontend
  - `nginx/mystral.conf` — референс конфиг для главного VPS nginx
  - `.env.prod` — шаблон с CHANGE_ME плейсхолдерами (в .gitignore)
  - `.gitignore` — добавлен .env.prod
  - `deploy.sh` — git pull → build → up -d; chmod +x

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок

- **Саша делает на VPS:**
  - Купить домен, A-запись → VPS IP
  - `git clone` + заполнить `.env.prod`
  - `docker network ls` → обновить `shared_infra.name` в docker-compose.prod.yml
  - `sudo certbot --nginx -d mystral.app`
  - `bash deploy.sh`

## 2026-06-19 — TZ-012: Связывание аккаунтов email ↔ Telegram

- **Сделано:**
  - `backend/app/core/security.py` — добавлен `validate_telegram_widget()`:
    - Telegram Login Widget использует SHA256(bot_token) как ключ (в отличие от TMA: HMAC nested)
  - `backend/app/api/v1/auth.py` — полная доработка:
    - `TelegramAuthRequest` — поддержка `init_data` (TMA) и `widget_data` (Login Widget)
    - `_resolve_tg_id()` — хелпер: валидирует любой формат, возвращает tg_id
    - POST /auth/telegram — добавлен `is_new: bool` в ответ
    - GET /auth/me — добавлен `providers: list[str]` (запрос к AuthProvider)
    - POST /auth/link-email — привязывает email к текущему аккаунту (requires auth)
    - POST /auth/link-telegram — привязывает TG к текущему аккаунту через widget (requires auth)
    - POST /auth/merge — без auth: валидирует TG + email/pass, переносит TG-провайдер на email-аккаунт
  - `frontend/src/context/AuthContext.tsx` — добавлены `pendingMerge` и `dismissMerge`:
    - После TMA логина: если `is_new === true` → setPendingMerge(true)
  - `frontend/src/App.tsx` — рендерит `<MergeAccountPrompt>` когда `pendingMerge === true`
  - `frontend/src/pages/LoginScreen.tsx` — кнопка "Войти через Telegram":
    - Открывает popup oauth.telegram.org/auth?bot_id=...
    - Слушает window.message с origin https://oauth.telegram.org
    - POST /auth/telegram с widget_data → login()
  - `frontend/src/components/MergeAccountPrompt.tsx` — новый компонент:
    - Bottom sheet с формой email + пароль
    - POST /auth/merge с init_data из TMA → login() → dismissMerge()
  - `frontend/src/pages/Profile.tsx` — раздел "Связанные аккаунты":
    - useEffect: Promise.all([GET /profile, GET /auth/me]) → заполняет providers[]
    - Email: кнопка "Добавить" → инлайн-форма (email + пароль + подтверждение) → POST /auth/link-email
    - Telegram: кнопка "Привязать" → handleTelegramWebLogin → POST /auth/link-telegram
    - Статусные бейджи "Привязан" (фиолетовый/голубой) когда provider в списке

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок

## 2026-06-19 — TZ-013: Официальный Telegram Login Widget (замена popup)

- **Проблема:** popup oauth.telegram.org/auth давал "Bot domain invalid"
- **Решение:** официальный `<script>` виджет от Telegram

- **Сделано:**
  - `backend/app/core/security.py` — добавлен `validate_telegram_widget_hash(data: dict) -> bool`
    (bool-обёртка над `validate_telegram_widget`, для удобства)
  - `frontend/src/pages/LoginScreen.tsx` — заменён popup на script-виджет:
    - `tgBtnRef = useRef<HTMLDivElement>()` — контейнер для виджета
    - useEffect: регистрирует `window.onTelegramWidgetAuth` → POST /auth/telegram (widget_data)
    - Динамически вставляет `<script data-telegram-login="Mystrallbot" data-size="large" ...>`
    - Cleanup: `delete window.onTelegramWidgetAuth`
    - Убрана кнопка-заглушка, вместо неё `<div ref={tgBtnRef} />`

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено в main

- **На VPS:**
  - `git pull && docker compose -f docker-compose.prod.yml up --build -d frontend && docker compose -f docker-compose.prod.yml restart nginx`

- **Следующий шаг:**
  - TZ-014: Онбординг + динамический знак + EN ✓ (выполнен ниже)

## 2026-06-19 — TZ-014: Онбординг + динамический знак + EN локализация

- **Сделано:**
  - **БЛОК А — Онбординг:**
    - `backend/app/api/v1/auth.py` — `_user_response` теперь async, включает `has_birth_date: bool`
      (запрос UserProfile из БД). GET /auth/me тоже возвращает поле.
    - `frontend/src/context/AuthContext.tsx` — `has_birth_date` в UserData,
      `i18n.changeLanguage()` при login/updateUser
    - `frontend/src/components/OnboardingModal.tsx` — bottom sheet при первом входе:
      День/Месяц/Год → PUT /profile → updateUser({has_birth_date:true})
    - `frontend/src/App.tsx` — рендерит OnboardingModal когда user && !has_birth_date
  - **БЛОК Б — Динамический знак:**
    - `frontend/src/utils/zodiac.ts` — getZodiacSign(date) → { sign, symbol, en }
      12 знаков с русскими/английскими названиями + Unicode символами
    - `frontend/src/pages/Home.tsx` — убран хардкод "Скорпион ♏":
      GET /profile при монтировании → getZodiacSign → передаётся в ZodiacOrb и streamRequest.
      Приветствие на основе времени суток (greeting_morning/afternoon/evening/night)
    - `frontend/src/pages/Profile.tsx` — zodiac из zodiac.ts (убран дублирующий getZodiacSign)
  - **БЛОК В — EN локализация:**
    - `frontend/src/i18n/locales/ru.json` — ~100 ключей по 9 неймспейсам
    - `frontend/src/i18n/locales/en.json` — полный английский перевод
    - 8 компонентов с `useTranslation() + t('key')`:
      Home, Tarot, NatalChart, Profile, LoginScreen,
      BottomNav, PaywallSheet, MergeAccountPrompt, OnboardingModal
    - Profile: переключатель языка вызывает `updateUser({lang}) + i18n.changeLanguage()`

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (15 файлов, +691 –298)

- **Следующий шаг:**
  - TZ-015: Недостающие экраны ✓ (выполнен ниже)

## 2026-06-19 — TZ-015: Недостающие экраны — Луна, Совместимость, Нумерология, Руны

- **Сделано:**
  - **Backend — 4 новых API модуля:**
    - `lunar.py` — GET /lunar/today (лунный день, фаза, знак луны, рекомендации, энергия),
      GET /lunar/month (массив дней с фазами). Чистая математика от новолуния 2000-01-06.
    - `compatibility.py` — POST /compatibility/calculate (совместимость по стихиям,
      процент + описание), POST /compatibility/interpret (Pro, SSE Groq)
    - `numerology.py` — POST /numerology/calculate (Life Path, Expression, Soul Urge,
      Personality). Таблицы Пифагора для латиницы и кириллицы. Free: только Life Path.
      POST /numerology/interpret (Pro, SSE Groq)
    - `runes.py` — 24 руны Elder Futhark с RU/EN значениями. POST /runes/draw
      (1 или 3, 30% вероятность переворота, free: 1/день через Redis).
      POST /runes/interpret (SSE Groq)
    - `router.py` — подключены все 4 новых роутера
  - **Frontend — 4 новых страницы:**
    - `LunarCalendar.tsx` — Орба луны (CSS), инфо дня, 3 рекомендации,
      календарь месяца (grid 7 колонок, сегодня подсвечен)
    - `Compatibility.tsx` — 2 шага form→result. Автозаполнение из профиля.
      Процент + прогресс-бар + описание. Pro: SSE интерпретация. Free: paywall.
    - `Numerology.tsx` — Форма с автозаполнением. Life Path крупно + gold.
      Free: остальные числа заблюрены с замком. Pro: все числа + интерпретация.
    - `Runes.tsx` — 3 режима idle→drawing→result. Выбор 1/3 руны (3 = Pro).
      Анимация появления. Карточки с символом, позицией, значением.
    - `App.tsx` — роуты: moon/lunar → LunarCalendar, compat → Compatibility,
      numerology/numero → Numerology, runes → Runes
    - i18n: ~50 новых ключей в ru.json + en.json

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (12 файлов, +1511)

- **Следующий шаг:**
  - TZ-016: Groq промпты ✓ (выполнен ниже)

## 2026-06-20 — TZ-016: Улучшение Groq промптов — качество AI текстов

- **Проблема:** AI генерировал общие поэтические тексты без конкретики

- **Сделано:**
  - `backend/app/core/prompts.py` — новый модуль с system_prompt(lang):
    - RU: "опытный астролог, пишешь точно, без 'нежных ветерков', конкретно о знаке/планете"
    - EN: "experienced astrologer, no vague phrases, specific about sign/planet/aspect"
  - Все 6 Groq-вызовов обновлены:
    - horoscope.py: сфера жизни + конкретный совет + время дня
    - tarot.py: значение каждой карты + связь между ними + практический вывод
    - natal.py: черта характера (Солнце) + эмоции (Луна) + восприятие (Асцендент) + вызов
    - compatibility.py: сила пары + источник конфликтов + практический совет
    - numerology.py: жизненная задача + сильные стороны + вызовы + сфера реализации
    - runes.py: значение каждой руны + общий посыл + рекомендация
  - Каждый вызов теперь: `messages=[{role: "system", ...}, {role: "user", ...}]`
  - Все промпты двуязычные (RU/EN ветвление)

- **Проверено:**
  - `git push` — запушено (7 файлов, +187 –62)
  - На VPS: `docker compose restart backend` (пересборка не нужна)

- **Следующий шаг:**
  - TZ-017: Адаптивный дизайн ✓ (выполнен ниже)

## 2026-06-20 — TZ-017: Адаптивный дизайн под ПК

- **Сделано:**
  - `frontend/src/components/layout/AppLayout.tsx` — обёртка с 3-колоночным layout:
    - Левая панель (220px, sticky, hidden <768px): логотип gold, вертикальная навигация
      (8 пунктов с emoji, active = violet bg), статус подписки внизу
    - Центр (390px fixed): рендерит children, бордеры по бокам
    - Правая панель (220px, sticky, hidden <768px): лунный день, знак зодиака, tier
  - `frontend/src/components/layout/RightPanel.tsx` — правая панель:
    - GET /lunar/today → лунная карточка (фаза, знак, энергия)
    - GET /profile → getZodiacSign() → карточка знака
    - Pro/Free бейдж
  - `frontend/src/components/ui/BottomNav.tsx` — добавлен `md:hidden`
  - `frontend/src/App.tsx` — оборачивает весь контент в `<AppLayout>`
  - 8 страниц: убран `max-w-[390px] mx-auto` (AppLayout контролирует ширину)
  - i18n: добавлены nav ключи для compat/natal/numerology/runes

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (14 файлов, +224)

- **Следующий шаг:**
  - TZ-018: Валидация + защита TMA ✓ (выполнен ниже)

## 2026-06-20 — TZ-018: Валидация форм + защита TMA аккаунта

- **Сделано:**
  - **БЛОК А — Валидация (frontend/src/utils/validate.ts):**
    - validateEmail, validatePassword, validateName, validateCity
    - validateDay/Month/Year (диапазоны), validateDateExists (Date roundtrip)
  - **БЛОК Б — Применение в 6 формах:**
    - LoginScreen: email + password (+ name при register)
    - OnboardingModal: day/month/year + validateDateExists
    - NatalChart: name + date + city, per-field ошибки
    - Profile: date поля при сохранении
    - MergeAccountPrompt: email + password
    - Compatibility: оба блока дат
    - Паттерн: Record<string, string> errors, красный текст под полем, очистка при onChange
  - **БЛОК В — Backend email-validator:**
    - requirements.txt: email-validator==2.1.0
    - auth.py register(): validate_email(check_deliverability=False)
  - **БЛОК Г — Защита TMA:**
    - AuthContext.logout(): isTMA() → WebApp.close() вместо logout
    - Profile: вместо "Выйти" → "Аккаунт привязан к Telegram ✓"
    - i18n: profile.tg_account ключ (RU/EN)

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (12 файлов, +286 –100)

- **На VPS:**
  - `docker compose -f docker-compose.prod.yml up --build -d frontend backend`
  - `docker compose -f docker-compose.prod.yml restart nginx`

- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование на VPS

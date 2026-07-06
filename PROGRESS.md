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
  - TZ-019: Rider-Waite карты ✓ (выполнен ниже)

## 2026-06-20 — TZ-019: Rider-Waite карты Таро — реальные изображения

- **Сделано:**
  - `backend/scripts/download_tarot.py` — скрипт скачивания 22 карт с Wikimedia Commons
    - Rider-Waite 1909 (public domain)
    - Исправлены URL для Magician (#1) и Lovers (#6) через Wikipedia API
  - `frontend/public/tarot/0-21.jpg` — 22 изображений Старших Арканов
  - `frontend/src/components/tarot/TarotCard.tsx` — лицевая сторона:
    - `<img src="/tarot/{id}.jpg" objectFit="cover">` вместо emoji+текст
    - Полупрозрачная подпись с названием карты внизу
    - Fallback: скрывает img при ошибке загрузки (onError)
    - Рубашка (✦ MYSTRAL) без изменений

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (24 файла: 22 jpg + script + component)

- **Следующий шаг:**
  - TZ-021: Уведомления ✓ (выполнен ниже)

## 2026-06-20 — TZ-021: Telegram-уведомления — ежедневный гороскоп в 9:00

- **Сделано:**
  - **Модель + миграция:**
    - UserProfile: `notifications_enabled: bool = False`
    - database.py: `ALTER TABLE IF NOT EXISTS` + `get_session_context()` async CM
  - **Scheduler (APScheduler):**
    - scheduler.py: каждые 5 минут проверяет кому сейчас 9:00 в их таймзоне
    - Генерирует гороскоп через services/horoscope.py (zodiac_from_date + Groq non-streaming)
    - Отправляет через aiogram Bot, Redis dedup (25h TTL)
    - main.py: scheduler.start() в lifespan
  - **Profile API:**
    - ProfileUpdate: + notifications_enabled, timezone (с валидацией zoneinfo)
    - POST /profile/toggle-notifications — для бота (без JWT, по telegram_id)
  - **Bot:**
    - /notifications команда: toggle через HTTP к backend
  - **Frontend:**
    - OnboardingModal: 2 шага — дата рождения → уведомления (timezone selector)
    - Profile: карточка "Уведомления" с toggle + dropdown таймзоны
    - constants/timezones.ts: 21 таймзона (Россия, СНГ, мир)
    - i18n: все ключи (RU/EN)

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок
  - `git push` — запушено (14 файлов, +461)

- **На VPS:**
  - `docker compose -f docker-compose.prod.yml up --build -d`

- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-052: SVG натальное колесо

- **Сделано:**
  - `backend/app/api/v1/natal.py` — `build_full_chart()`: куспиды домов теперь содержат
    `abs_pos` (абсолютный градус 0-360), вычисленный через уже существующий `_get_abs_pos()`
    (раньше в объекте дома был только `degree` — позиция внутри знака). Планеты уже
    отдавали `abs_pos` и раньше, но во фронтовом типе `PlanetData` это поле не было объявлено.
  - `frontend/src/components/NatalWheel.tsx` — новый компонент, полностью на SVG,
    без canvas и сторонних либ:
    - Слой 1: пояс из 12 знаков зодиака (сектора-дуги, заливка по стихии, символы)
    - Слой 2: линии домов (угловые 1/4/7/10 — золотые, остальные — белые), номера домов
    - Слой 3: линии аспектов внутри R_inner (только орб < 5°, цвет/толщина по типу аспекта)
    - Слой 4: планеты на R_planet с `resolveCollisions()` — раздвигает символы планет
      ближе 7° друг к другу по радиусу; ретроградные помечены "R"; линия-коннектор к домам
    - Слой 5: градусные метки каждые 10° по внешнему краю
    - Слой 6: декоративный центральный круг
    - Hover-тултип по планете (обычный `div` поверх SVG, не foreignObject):
      "{планета} в {знак} {градус}° · {дом} дом"
    - Анимации: планеты — `mystral-fadeup .6s` с лёгким сдвигом по времени,
      аспекты — новый keyframe `mystral-fadein` (добавлен в `index.css`) с задержкой 0.4s
  - `frontend/src/pages/NatalChart.tsx` — интеграция:
    - `PlanetData`/`HouseData`/`AspectData` дополнены полями `abs_pos`, `planet1`/`planet2`
    - `wheelPlanets`/`wheelHouses`/`wheelAspects` (useMemo) конвертируют данные `chart`
      в формат `NatalWheel` (planet.name намеренно на англ. ключах — так `NatalWheel`
      сопоставляет планеты в аспектах с `planet1`/`planet2` из бэкенда)
    - `wheelSize`: 480px на десктопе (≥768px), иначе `min(innerWidth-48, 520)`, слушает resize
    - Колесо вставлено над табами AI-интерпретации; на десктопе — grid
      `480px 1fr` (колесо слева, AI-интерпретация справа), на мобиле — одна колонка.
      Старый статичный SVG от kerykeion (`/natal/svg`) не трогали — оставлен как есть.

- **Проверено:**
  - `python -m py_compile backend/app/api/v1/natal.py` — 0 ошибок
  - `tsc --noEmit` — 0 ошибок
  - Визуально в браузере (моковые данные, временный harness, не закоммичен):
    геометрия секторов/домов сверена программно через DOM (все линии аспектов
    ровно на радиусе R_inner*0.95, 4 золотые угловые линии домов + 8 обычных,
    12 подписанных домов, центр-круг радиуса R_inner*0.15), коллизии планет
    (Sun/Mercury 5° друг от друга) раздвигаются корректно, hover-тултип
    показывает верный дом по градусу.

- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-053: Фикс натального колеса и AI-интерпретации

- **Найдено (внешний аудит + баг-репорт):**
  - AI-интерпретация "смещалась в сторону, отображалась криво" при переключении
    табов — причина: `handleInterpret` в `NatalChart.tsx` не имел защиты от гонки
    запросов (тот же класс бага, что чинили в `CompositeChart.tsx` ранее);
    отдельно — колесо визуально "смещено вниз", т.к. рендерилось ПОСЛЕ 7 других
    карточек и дублирующей статичной SVG-картинки от kerykeion.
  - Ретроградность планет не отображалась на самом кольце (только в таблице).
  - Коллизия глифов при близких градусах превращалась в нечитаемое пятно.

- **Сделано:**
  - `frontend/src/pages/NatalChart.tsx`:
    - Убрана статичная SVG-картинка от kerykeion (`svgContent`, fetch `/natal/svg`,
      `dangerouslySetInnerHTML`) — дублировала функциональность `NatalWheel`.
    - Блок "Натальное колесо + AI-интерпретация" перенесён в начало результата
      (сразу после расчёта), остальные карточки (Стеллиумы/Большая тройка/Планеты/
      Дома/Стихии/Аспекты) идут ниже — устраняет "пустое пространство сверху".
    - AI-интерпретация переведена на явный клик: `selectSection()` только
      переключает таб, `fetchInterpretation()` запускается по кнопке
      "Получить интерпретацию" (gold `#C9A84C`). Состояния: спиннер + "Генерируем
      интерпретацию…" (disabled), готовый текст, либо ошибка с текстом
      "Не удалось сгенерировать интерпретацию, попробуйте снова" и повторной кнопкой.
    - Кеш интерпретаций по разделам на весь просмотр карты: `interpretations:
      Partial<Record<Section,string>>` (React state, без persist в БД).
    - `requestIdRef`-guard в `fetchInterpretation` (тот же паттерн, что и в
      `CompositeChart.tsx`) — чанки устаревшего стрима больше не дописываются
      поверх новой секции.
  - `frontend/src/components/NatalWheel.tsx`:
    - Ретроградный маркер: `R` (красный) → `℞` (`#A89E8B`, приглушённый, как в ТЗ).
    - `resolveCollisions()` переписан: константы `COLLISION_THRESHOLD_DEG = 4`,
      `RADIAL_STEP_PX = 15`; планеты сортируются по градусу, группируются по
      порогу (с учётом перехода через 360°/0° — кластер на стыке склеивается
      в одну группу), каждая планета внутри группы отодвигается на
      `RADIAL_STEP_PX` ближе к центру относительно предыдущей (было: только
      2 уровня радиуса без учёта wraparound).
    - Для каждой раздвинутой (collided) планеты — тонкая линия-указатель
      (0.5px, `#6E6757`) от глифа до её истинного градуса на внешней шкале.

- **Проверено:**
  - `tsc --noEmit` — 0 ошибок (backend не менялся в этом ТЗ)
  - `python -m pytest` — 86/86 (регрессий нет)
  - Визуально (моковые данные, временный harness, не закоммичен): 3-плане́тный
    кластер (Sun/Mercury/Venus, 12-17°) и wraparound-кластер (Neptune 359°/
    Pluto 1°) дают ровно 5 линий-указателей на радиусах 156/141/126px (шаг
    ровно 15px); ретро-маркеры (Mars, Uranus) — `℞` цвета `#A89E8B`.

- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-053 доп. фикс: layout колеса и AI-интерпретации на десктопе

- **Найдено (скриншот с прода):** side-by-side grid (`480px 1fr`: колесо слева,
  AI-интерпретация справа) выглядел криво — панель интерпретации слишком узкая,
  текст визуально обрезался у правого края колонки.
- **Сделано:** `frontend/src/pages/NatalChart.tsx` — убрал grid-обёртку
  `grid-cols-1 md:grid-cols-[480px_1fr]`. Теперь колесо и карточка
  AI-интерпретации — простые последовательные блоки на всю ширину в общем
  вертикальном потоке (как остальные карточки страницы): колесо сверху,
  ниже — Стеллиумы/Большая тройка/Планеты/Дома/Стихии/Аспекты, и в самом
  низу — AI-интерпретация. Одинаково для desktop и mobile.
- **Проверено:** `tsc --noEmit` — 0 ошибок; backend не менялся.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-055: Критический баг — таймзона не учитывалась при расчёте домов/асцендента

- **Причина (подтверждено чтением исходников kerykeion 4.14.0):** kerykeion
  умеет верно конвертировать местное время рождения в UTC —
  `pytz.timezone(self.tz_str).localize(naive_datetime)` в
  `astrological_subject.py`, с учётом исторических переходов на летнее время.
  Но во ВСЕХ местах приложения, где строится `AstrologicalSubject` из
  реальных данных рождения, было жёстко `tz_str="UTC"` — то есть local time
  проходило как «уже UTC» без какой-либо конвертации. Отсюда неверные
  Асцендент/MC/куспиды домов (а значит и распределение планет по домам)
  почти у всех пользователей; сами планеты (знак/градус) искажались
  минимально.
  - `backend/app/api/v1/natal.py` — `_build_subject()`
  - `backend/app/api/v1/compatibility.py` — 4 места: `compat_moon`,
    `compat_synastry`, `compat_composite`, `composite_interpret`
  - **Не трогал:** `backend/app/api/v1/lunar.py` — там `tz_str="UTC"` с
    `lat=0, lng=0` используется для расчёта сегодняшнего ретрограда Меркурия
    (глобальная проверка, не привязана к чьему-то рождению) — там всё верно.
- **Кэширование карты (уточнено перед фиксом):** натальная карта считается
  ДИНАМИЧЕСКИ на каждый запрос из `birth_date/birth_time/birth_city`,
  ничего не кэшируется в БД/Redis — отдельная миграция/скрипт инвалидации
  не нужны, все карты пересчитаются верно автоматически.
- **Сделано:**
  - `backend/requirements.txt` — добавлен `timezonefinder==8.2.4` (offline
    lookup IANA-таймзоны по координатам, без внешних API и рейт-лимитов).
  - `backend/app/api/v1/natal.py` — новая `resolve_timezone(lat, lon) -> str`
    (глобальный `TimezoneFinder()`, инстанцируется один раз). `_build_subject`
    теперь передаёт `tz_str=resolve_timezone(lat, lon)` вместо хардкода —
    дальше конвертацию в UTC делает сам kerykeion через pytz.
  - `backend/app/api/v1/compatibility.py` — тот же `resolve_timezone`
    прокинут во все 4 места построения `AstrologicalSubject` (по одному
    вызову на каждого из пары).
  - `backend/tests/test_natal_timezone.py` — 2 новых теста с точными
    значениями из ТЗ (Асцендент/MC/все 10 планет для Белореченска,
    Асцендент/MC/Солнце/Луна для Тулы), плюс проверка `subj.tz_str ==
    "Europe/Moscow"`. Пропускаются (`skip`) при отсутствии `pyswisseph`
    (Windows) — реально считают только там, где есть настоящий kerykeion
    (Docker/Linux), как и остальной проект.
- **Проверено:**
  - Оба контрольных кейса — **точное совпадение** со значениями из ТЗ,
    посчитано вручную в Docker (`docker compose run backend python -c
    "..."`) и через сами pytest-тесты:
    - Белореченск 18.11.2003 02:30 → `tz=Europe/Moscow`, Асцендент Дева
      29.2°, MC Близнецы 29.1°, Солнце Скорпион 25.2°, Луна Дева 4.9°,
      Меркурий Стрелец 8.6°, Венера Стрелец 18.7°, Марс Рыбы 14.7°,
      Юпитер Дева 15.6°, Сатурн Рак 12.8° ℞, Уран Водолей 28.9°, Нептун
      Водолей 10.6°, Плутон Стрелец 18.9° — всё сошлось.
    - Тула 28.03.2005 18:30 (день после перехода на летнее время в РФ) →
      `tz=Europe/Moscow`, offset правильно UTC+4 (не хардкод +3): Асцендент
      Дева 24.0°, MC Близнецы 21.9°, Солнце Овен 8.0°, Луна Скорпион 11.1°.
  - Доп. города (offset меняется предсказуемо для каждого): Владивосток
    2015 → Asia/Vladivostok +10; Новосибирск 1998 → Asia/Novosibirsk +6
    (до реформы поясов); Нью-Йорк июль 2020 → America/New_York EDT −4;
    Токио → Asia/Tokyo +9 без DST; Екатеринбург 2003 → Asia/Yekaterinburg
    +6 (историческое значение до реформы 2010/2011).
  - `python -m py_compile` — 0 ошибок (natal.py, compatibility.py,
    test_natal_timezone.py).
  - `pytest` в Docker (реальный kerykeion): **86 passed** (84 старых + 2
    новых), **2 failed** — но это `test_horoscope_scores_valid` и
    `test_logout_blacklists_token`, никак не связанные с натальной картой;
    оба проходят по отдельности, падают только в полном прогоне и только
    на Linux (на Windows тот же прогон — все 86 зелёные). Похоже на утечку
    event loop между тестами в связке pytest-asyncio+fakeredis на Linux —
    предсуществующая проблема тестовой инфраструктуры, не регрессия от
    этого фикса. Стоит завести отдельный тикет.
  - `pytest` локально на Windows: 86 passed, 2 skipped (новые тесты
    корректно пропускаются без pyswisseph).
  - Frontend не менялся, `tsc` не требовался.
- **Следующий шаг:**
  - Отдельно разобраться с падением `test_horoscope_scores_valid` /
    `test_logout_blacklists_token` на Linux в полном прогоне (не блокирует
    этот фикс, но стоит поймать до следующего CI на Linux)
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-056: Утечка event loop в тестах на Linux

- **Причина (подтверждено чтением исходников pytest-asyncio 1.4.0):**
  `tests/conftest.py` держал старую `@pytest.fixture(scope="session") def
  event_loop(): ...` — механизм переопределения event loop из старых версий
  pytest-asyncio. В установленной версии (1.4.0) этот механизм полностью
  убран: плагин больше даже не ищет фикстуру с именем `event_loop`, только
  `event_loop_policy`. Реально использовавшееся значение —
  `asyncio_default_test_loop_scope=function` (дефолт библиотеки), то есть
  **каждый тест получал собственный новый event loop**, а старая
  session-фикстура была мёртвым кодом, молча проглоченным
  `filterwarnings = ignore::DeprecationWarning` в `pytest.ini`.
  Модульные singleton-клиенты Redis (`app_redis.redis_client` в
  `app/core/redis.py`, отдельный `redis_client` в `horoscope.py` и т.д.)
  создаются один раз при импорте и живут на весь прогон. Внутреннее
  соединение/очередь fakeredis при первом реальном использовании
  привязывается к тому event loop, что активен в этот момент. В полном
  прогоне более ранние тесты успевали "закрепить" соединение за своим
  (уже закрытым к этому моменту) loop, и следующий тест, попадающий на то
  же соединение под новым loop, падал с `RuntimeError: ... is bound to a
  different event loop`. В изоляции первый же вызов создавал соединение
  под "правильным" (текущим) loop — поэтому тесты проходили по отдельности.
- **Сделано:**
  - `backend/pytest.ini` — добавлены `asyncio_default_fixture_loop_scope
    = session` и `asyncio_default_test_loop_scope = session`: теперь все
    тесты и async-фикстуры в рамках прогона используют один и тот же
    event loop, как и предполагала (но больше не реализовывала) старая
    фикстура.
  - `backend/tests/conftest.py` — убрана мёртвая фикстура `event_loop` и
    ставший неиспользуемым `import asyncio`.
- **Проверено:**
  - Docker/Linux, полный прогон `pytest` (86 старых + 2 из ТЗ-055) —
    **88 passed, 0 failed**, повторено 3 раза подряд (без этого фикса
    было стабильно 86 passed + 2 failed в каждом полном прогоне).
  - Прогон с `-W error::DeprecationWarning` — 88 passed, других
    предупреждений, которые мог маскировать `ignore::DeprecationWarning`,
    не всплыло.
  - Windows локально: 86 passed, 2 skipped — без регрессий.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS

## 2026-07-05 — TZ-054: Пререндер публичных SEO-страниц — узкий фикс после ревизии посылки ТЗ

- **Посылка ТЗ не подтвердилась при проверке прода:** ТЗ исходило из того,
  что все 126 публичных SEO-страниц отдают пустой `<div id="root">` и
  требуют выполнения JS. Проверка `curl https://mystral.space/zodiac/aries`
  (и /tarot/*, /runes/*, /numerology/*) показала, что эти страницы уже
  ПОЛНОСТЬЮ рендерятся сервером: `backend/app/api/v1/seo_pages.py` отдаёт
  готовый Jinja2 HTML (`h1`, абзацы, JSON-LD Article/FAQPage/BreadcrumbList,
  canonical, hreflang) без единой строки JS, а `nginx/nginx.prod.conf` уже
  явно проксирует `/zodiac`, `/tarot`, `/runes`, `/numerology`,
  `/sitemap.xml` на backend в обход SPA-фолбэка. Плюс во фронтенде вообще
  нет `react-router-dom` (роутинг — `useState` в `App.tsx`), так что
  `vite-react-ssg` из Модуля 2 ТЗ было физически не к чему подключать для
  этих страниц.
  - Реальная пустая SPA-оболочка — только у главной `/` (в sitemap с
    приоритетом 1.0, отдаёт `<title>Mystral</title>` и дальше пустой
    `#root`).
  - Отдельно нашёл: `?lang=es/pt/tr/uk` на SEO-страницах отдаёт тот же
    русский контент (`<html lang="ru">`) — hreflang-альтернативы сейчас
    битые. Не чинил — это релевантно TZ-037c (615 страниц, 5 языков), не
    этому тикету.
  - Согласовал с Сашей: узкий фикс — пререндерить только `/`, не трогая
    роутинг/сборку/nginx.
- **Сделано:** `frontend/index.html` —
  - Добавлены `<meta name="description">`, `<link rel="canonical">`,
    JSON-LD `WebSite`.
  - Внутрь `<div id="root">` положен настоящий статический HTML (`h1`,
    два абзаца, ссылки на `/zodiac`, `/tarot`, `/runes`) вместо пустого
    контейнера — виден в сыром HTML-ответе любому краулеру без JS.
  - Никакого cloaking: контент одинаков для всех (ботов и людей).
    `ReactDOM.createRoot(...).render(<App/>)` в `main.tsx` не менялся —
    при монтировании React **полностью заменяет** содержимое `#root`
    (не hydrate, а чистый mount), поэтому статический контент
    автоматически и чисто исчезает для реальных пользователей — доп. код
    на очистку не понадобился.
  - Инлайновые стили под тёмную/золотую тему — чтобы не было некрасивой
    незастилизованной вспышки в момент до монтирования React.
- **Проверено:**
  - `curl http://localhost:5173/` (dev-сервер) — статический контент
    присутствует в сыром HTML.
  - Визуально в браузере: страница монтируется в реальный `LoginScreen`
    без визуальных артефактов/мигания, ошибок в консоли нет.
  - `npm run build` — успешно, `dist/index.html` (3.59 kB) содержит
    статический контент.
  - `tsc --noEmit` — 0 ошибок.
  - `pytest` (backend не менялся, прогнан для регрессии) — 86 passed,
    2 skipped.
- **Не делал (сознательно, вне узкого фикса):**
  - Миграция на `react-router-dom` + `vite-react-ssg`/SSG-пайплайн —
    не нужна, целевые 126 страниц уже server-rendered.
  - Правка nginx — `/` и так корректно фолбэчится на `index.html`.
  - Починка hreflang/`?lang=` — отдельная задача, см. TZ-037c.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - При планировании TZ-037c — учесть, что hreflang-альтернативы сейчас
    битые (см. выше), понадобится реальная генерация контента на 5 языках
    с разными URL, а не просто `?lang=` без изменения ответа

## 2026-07-05 — TZ-057: Баг в генерации share-карточек — Натальная карта и Composite Chart без контента

- **Найдено:**
  - **Натальная карта (Problem 1):** `NatalChart.tsx` вызывал `<ShareCard
    type="natal" title=... onClose=.../>` — вообще без данных карты. И даже
    если бы данные передавались, рендер-блок `type==="natal"` в
    `ShareCard.tsx` показывал только один проп `sign` одним большим
    символом — никакой "большой тройки" там не было предусмотрено в принципе.
  - **Composite Chart (Problem 2):** в `ShareCardProps.type` не было
    варианта `"composite"` вообще — `CompositeChart.tsx` вызывал карточку с
    `type="natal"` и `sign="∞"`, поэтому показывался только символ
    бесконечности без результата (нет числового процента для composite —
    это другая техника, у неё есть "главный аспект" и текстовое AI-описание,
    но не показывались и они).
  - **"Stumager" вместо имени (Problem 3):** `userName = user?.name` брал
    `display_name` аккаунта (в данном случае похожий на логин), а не имя,
    введённое для расчётов. Бэкенд для этой же карты сам использует
    приоритет `prof.full_name or current_user.display_name` (см.
    `compatibility.py::composite_interpret`) — фронтенд этот приоритет не
    повторял и брал только `display_name`. Обычная карточка совместимости
    вообще не показывает "моё" имя в заголовке (только `result.partner_name`),
    поэтому сравнение с "Оксана" из ТЗ было не совсем яблоки-к-яблокам, но
    сама причина подтвердилась.
  - **Руна "Феху" другим цветом (Problem 4):** подтверждено — это
    осознанная фича, не баг. `rune.reversed` красит подпись руны в
    `#D98A8A` (обратная) вместо `#8A7FC0` (прямая) — Феху в конкретном
    раскладе была перевёрнута, остальные 4 — нет. На основной странице
    Рун это дублируется текстовым бейджем "Перевёрнутая"/"Прямая", а в
    самой share-карточке текстового пояснения не было — только цвет.
  - `"Composite Chart"` нигде в интерфейсе не был переведён на русский
    (ни в `typeLabels` на странице Совместимости, ни в самом
    `CompositeChart.tsx`) — использовал "Композитная карта" везде.
- **Сделано:**
  - `frontend/src/components/ShareCard.tsx`:
    - `type` union: добавлен `"composite"`. Убран мёртвый проп `sign`
      (использовался только багованным composite-вызовом).
    - Новые пропы: `natalName`, `bigThree` (массив `{label, sign, degree}`),
      `aspectLabel`, `description`.
    - Блок `natal`: имя (если есть) + 3 строки Солнце/Луна/Асцендент со
      знаком и градусом — как на самой странице.
    - Новый блок `composite`: главный аспект (`aspectLabel`) + текстовое
      описание (`description`).
    - Блок `runes`: добавлена легенда под рунами — если хоть одна
      перевёрнута, показывается строка-пояснение (что именно значит
      цвет), новый ключ `share.reversed_hint`.
  - `frontend/src/pages/NatalChart.tsx`: вычисляется `bigThreeForShare` из
    `chart.planets[0..1]` + `chart.ascendant` (тот же источник, что и
    видимый на странице блок "Большая тройка"); в `ShareCard` передаются
    `natalName={form.name}` и `bigThree`.
  - `frontend/src/components/CompositeChart.tsx`:
    - Добавлен fetch `/api/v1/profile` → `profileFullName`; `userName =
      profileFullName || user?.name || "?"` — тот же приоритет, что уже
      использует бэкенд для этой фичи.
    - `type="composite"`, `aspectLabel` — главный (наименьший орб) аспект
      композитной карты, `description` — обрезанный до 140 символов текст
      уже сгенерированной AI-интерпретации (если пользователь её открывал).
    - `subtitle`, "Планеты Composite" и "Расчёт composite chart..."
      переведены на "Композитная карта" / "Планеты композитной карты" /
      "Расчёт композитной карты...".
  - `frontend/src/pages/Compatibility.tsx`: `typeLabels.composite` —
    "Composite Chart" → "Композитная карта" (RU).
  - `frontend/src/i18n/locales/{ru,en,es,pt,tr,uk}.json`: добавлены
    `share.type_composite` и `share.reversed_hint` во все 6 языков.
- **Проверено:**
  - `tsc --noEmit` — 0 ошибок.
  - Визуально (моковые данные, временный harness, не закоммичен) — все
    7 типов карточек (`tarot`, `runes`, `numerology`, `natal`, `compat`,
    `composite`, `lunar`) отрендерены и проверены через DOM: натальная
    показывает имя + 3 строки Большой тройки с градусами; composite
    показывает оба имени, переведённый подзаголовок, главный аспект и
    описание; руны — Феху `rgb(217,138,138)` (перевёрнута), остальные 4
    `rgb(138,127,192)` (прямые), плюс легенда под рядом рун; остальные
    4 типа не сломались (регрессии нет).
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Имя PNG-файла при экспорте (сейчас всегда `mystral-reading.png`) —
    в бэклог, не блокирует

## 2026-07-05 — TZ-057 доп. фикс: сырой markdown в AI-тексте (`**bold**` виден как есть)

- **Найдено:** после фикса composite-карточки Саша заметил на скриншоте
  буквальные `**...**` в тексте AI-интерпретации внутри карточки. Причина
  системная, не только в ShareCard: `{interpretation}` (или `{aiText}`)
  рендерится как обычный React-текст без markdown-парсера в 6 местах —
  `Tarot.tsx`, `Compatibility.tsx`, `Runes.tsx`, `Numerology.tsx`,
  `NatalChart.tsx`, `CompositeChart.tsx` (плюс попадает в `ShareCard`
  через `description`). LLM (deepseek через OpenRouter) периодически
  сам генерирует markdown-разметку (`**жирный**`), хотя раньше в system
  prompt это явно не запрещалось.
- **Сделано (два уровня защиты):**
  - `frontend/src/utils/markdown.ts` — новая `stripMarkdown()`: убирает
    `**bold**`, `*italic*`, markdown-заголовки `#`, буллеты `- `,
    инлайн-код `` ` `` через regex (не полноценный парсер, просто
    зачистка спецсимволов, которые LLM иногда добавляет).
    Применена во всех 6 местах отображения AI-текста, а в
    `CompositeChart.tsx` — и в `shareDescription` (зачистка ДО обрезки
    до 140 символов, чтобы не резать посреди `**`).
  - `backend/app/core/groq_client.py` — в `_QUALITY_DIRECTIVE`
    (универсальный system prompt, добавляется ко всем роутерам) для
    всех 6 языков добавлена строка с явным запретом markdown-разметки
    (`**`, `*`, `#`, обратные кавычки, списки через дефис) — снижает
    частоту проблемы на источнике, не заменяя фронтовую зачистку.
- **Проверено:**
  - `stripMarkdown` протестирован на точном примере со скриншота
    (`**Солнце в Водолее (1.6°)**...`) — звёздочки убраны, текст читается
    нормально.
  - `tsc --noEmit` — 0 ошибок.
  - `python -m py_compile app/core/groq_client.py` — 0 ошибок.
  - `pytest` — 86 passed, 2 skipped (регрессий нет, backend-логика не
    менялась, только текст промпта).
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Имя PNG-файла при экспорте (сейчас всегда `mystral-reading.png`) —
    в бэклог, не блокирует

## 2026-07-05 — Фикс кнопок "Поделиться" (скачивание/отправка в Telegram)

- **Жалоба:** "Скачать PNG" работает неудобно, а кнопка "Telegram"
  говорит, что картинка скопирована, но вставить её в чат не получается.
- **Причина:** обе кнопки в `useShareCard.ts` делали одно и то же —
  пытались `navigator.share({files:[file]})`, и только если API
  недоступен, откатывались на скачивание. Внутри Telegram Mini App
  (in-app WebView) `navigator.share` для файлов обрабатывается самим
  Telegram нестабильно: может отрапортовать успех и показать "скопировано",
  но фактически передать что-то, что не вставляется как изображение.
  Ни разу не было прямого управления буфером обмена с нашей стороны —
  весь "copy" происходил где-то внутри чужого API.
- **Сделано:** `frontend/src/hooks/useShareCard.ts`:
  - `share()` ("Скачать PNG") — убран `navigator.share` полностью,
    теперь всегда прямое скачивание файла. Кнопка называется "скачать" —
    теперь она буквально просто скачивает, без обходного share-sheet.
  - `shareToTelegram()` ("Telegram") — теперь сама пишет PNG в буфер
    обмена через `navigator.clipboard.write([new ClipboardItem({"image/png": file})])`
    (мы сами гарантируем корректный MIME-тип, а не полагаемся на то, как
    Telegram под капотом обрабатывает `navigator.share`). При успехе —
    подсказка "Скопировано! Открой чат в Telegram и вставь изображение
    (Ctrl+V...)". Если Clipboard API недоступен — откат на
    `navigator.share` (работает в обычных браузерах вне Telegram), если и
    это недоступно — прямое скачивание с подсказкой "прикрепи вручную".
  - `ShareCard.tsx` — новое поле `feedback` из хука показывается под
    кнопками как текстовая подсказка.
  - Новые i18n-ключи `share.copied_hint` / `share.download_hint` во всех
    6 языках.
- **Проверено:**
  - `tsc --noEmit` — 0 ошибок.
  - Визуально (harness, не закоммичен): клик по "Telegram" — при
    недоступности Clipboard API (в этом окружении) корректно откатился
    на скачивание с подсказкой "Изображение сохранено — прикрепи его в
    Telegram вручную", ошибок в консоли нет; клик по "Скачать PNG" —
    кнопка возвращается в обычное состояние без зависаний.
  - На реальном устройстве (не проверено мной физически, т.к. нужен
    настоящий пользовательский клик — синтетические клики через JS не
    всегда дают "trusted" activation, нужный Clipboard API) ожидается,
    что `clipboard.write` сработает и вставка в Telegram будет работать
    напрямую — стоит перепроверить на проде после деплоя.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Имя PNG-файла при экспорте (сейчас всегда `mystral-reading.png`) —
    в бэклог, не блокирует
  - Перепроверить `shareToTelegram` на реальном телефоне (в самом
    Telegram Mini App и в обычном мобильном браузере) после деплоя

## 2026-07-05 — ТЗ-038b: реальная интеграция ЮKassa (замена заглушки)

- **Найдено:** ТЗ предполагало, что вся интеграция ЮKassa — заглушка.
  На деле бэкенд (`payments.py`) уже делал реальный вызов создания
  платежа и реально верифицировал вебхук обратным запросом к API
  ЮKassa (сделано ранее в рамках QA-аудита). Настоящая заглушка была
  во фронтенде: `PaywallSheet.tsx` для НЕ-Telegram пользователей просто
  показывала "напишите нам на почту", ни разу не обращаясь к
  существующему эндпоинту. Помимо этого — платежи нигде не сохранялись
  в БД, вебхук игнорировал `payment.canceled`, `return_url` вёл в
  Telegram, а не на страницу результата, и не было обработки возврата
  пользователя после оплаты.
- **Сделано (бэкенд):**
  - `app/models/user.py` — новая таблица `Payment` (id, user_id,
    provider, provider_payment_id, product, amount, currency, status,
    created_at/updated_at); экспортирована из `app/models/__init__.py`
    (миграция не нужна — `create_all()` подхватит при рестарте).
  - `config.py` — новый `frontend_url` (return_url больше не ведёт в
    Telegram; `telegram_webapp_url` не переиспользован — он занят
    другим уведомлением в `scheduler.py`).
  - `yukassa_create` — теперь создаёт свою `Payment(status="pending")`
    ДО вызова ЮKassa (id платежа генерируется у нас, т.к. id из ответа
    ЮKassa физически не может попасть в `return_url` того же запроса,
    который этот ответ produces), после ответа ЮKassa — заполняет
    `provider_payment_id` и коммитит. Обёрнуто в try/except на
    `httpx.HTTPError` → 502 вместо необработанного исключения.
  - Новый общий helper `_verify_and_sync_payment(payment_id, session)`
    — переиспользуется вебхуком и статус-эндпоинтом: обратный GET-запрос
    к API ЮKassa (never trust webhook body/params alone), синхронизация
    локальной строки, активация Pro строго один раз на платёж (guard
    `was_succeeded` — иначе повторная доставка вебхука от ЮKassa
    бесплатно продлевала бы `subscription_expires_at` при каждом ретрае,
    реальный денежный баг).
  - `yukassa_webhook` — теперь принимает `payment.succeeded` И
    `payment.canceled` (раньше `canceled` молча игнорировался), вся
    логика верификации — через общий helper.
  - Новый `GET /payments/yukassa/status/{payment_id}` — статус по
    НАШЕМУ id платежа (из `return_url`), с проверкой владельца (403 на
    чужой платёж), при `status="pending"` — живая доверификация через
    тот же helper (не ждать вебхук, если пользователь уже вернулся на
    страницу).
  - Секретный ключ ЮKassa нигде не логируется и не попадает в ответы
    API — используется только внутри `base64.b64encode(...)` для
    заголовка `Authorization`; все `HTTPException.detail` — статичные
    строки, сырой JSON от ЮKassa клиенту не возвращается.
- **Сделано (фронтенд):**
  - `PaywallSheet.tsx` — `handleBuy()` для не-Telegram пользователей
    теперь реально вызывает `/payments/yukassa/create` и делает
    `window.location.href = data.payment_url`; убран мёртвый код
    заглушки (`showYukassaStub` state, сброс в `PlanCard`, JSX-блок
    "напишите нам").
  - `utils/api.ts` — новый `apiGet<T>()` (GET-версия существующего
    `apiRequest`, тот же паттерн парсинга ошибок).
  - Новая страница `pages/PaymentReturn.tsx` — читает `payment_id` из
    URL, поллит статус-эндпоинт (до 5 раз, 2с пауза — тот же ритм, что
    уже использует Stars-флоу в `PaywallSheet`), показывает
    успех/отмену/pending-таймаут, при успехе — `updateUser({tier:"pro"})`
    и очистка URL.
  - `App.tsx` — `if (window.location.search.includes("payment_id=")) return <PaymentReturn />;`
    добавлено ПОСЛЕ проверки `!user` (в отличие от `ResetPassword`,
    возврат с оплаты требует авторизации).
- **Тесты:** новый класс `TestYukassaFlow` в `test_payments.py` (11
  кейсов) — создание платежа и персист строки, вебхук
  succeeded/canceled/неизвестное событие, **регрессионный тест на
  повторную доставку вебхука** (проверяет, что `subscription_expires_at`
  не сдвигается второй раз), статус-эндпоинт (401/403/404, живая
  доверификация pending). При мокании `httpx.AsyncClient.post/.get`
  словил тонкий баг: `conftest.py`'s `client`-фикстура сама является
  `httpx.AsyncClient` (ASGITransport) — бланкет-патч класса перехватывал
  и собственные запросы теста к приложению, а не только исходящий вызов
  к ЮKassa. Исправлено URL-дискриминирующей обёрткой (фейковый ответ
  только если домен — `api.yookassa.ru`, иначе — реальный метод,
  захваченный до патча).
- **Проверено:**
  - `tsc --noEmit` — 0 ошибок.
  - `pytest` — 97 passed, 2 skipped (2 skip — те же, что раньше,
    `pyswisseph` недоступен на Windows вне Docker; к этому тикету не
    относится, платежи не используют kerykeion).
- **Не входит / отложено:**
  - Rate-limit на `/yukassa/webhook` — публичный, без авторизации,
    сейчас без лимита (как и раньше). Не блокирует критерии готовности.
  - Тестирование через тестовый магазин ЮKassa / реальная оплата —
    Саша решил разобраться с этим сам после деплоя.
  - **Ручной шаг для Саши после деплоя:** в личном кабинете ЮKassa
    указать webhook URL — `https://mystral.space/api/v1/payments/yukassa/webhook`
    (или актуальный домен) для событий `payment.succeeded` и
    `payment.canceled`. Без этого шага активация Pro всё ещё сработает
    (статус-эндпоинт делает живую доверификацию при возврате
    пользователя на страницу), но с задержкой до захода пользователя на
    `PaymentReturn`, а не мгновенно по вебхуку.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Перепроверить `shareToTelegram` на реальном телефоне после деплоя
  - Настроить webhook URL ЮKassa в личном кабинете (см. выше)

## 2026-07-05 — ТЗ-058: фикс бинарных байтов в regex (api.ts)

- **Найдено:** во время работы над ТЗ-038b обнаружилось, что
  `frontend/src/utils/api.ts` содержит буквальные управляющие байты
  (сырой NUL `0x00` и DEL `0x7F`) прямо внутри исходников — внутри
  regex-паттерна `cleanChunk` (`[^\x00-\x7f...]`), а не текстовые
  escape-последовательности. Скорее всего попало туда ещё во время
  более раннего фикса `clean_chunk` (первый тикет в этой сессии).
  Поведение это не меняло (JS парсит сырой control-байт в regex-литерале
  идентично экранированной записи `\x00`), но `git diff` показывал
  "Binary files differ" вместо обычного текстового diff — читать/ревьюить
  файл было невозможно.
- **Сделано:** оба байта (`0x00` и `0x7F`) заменены на буквальный текст
  `\x00` / `\x7f` (4 ASCII-символа каждый: `\`, `x`, `0`, `0`). Правка
  сделана на уровне байтов через отдельный Python-скрипт (не через
  обычный текстовый редактор — сырые control-байты не всегда надёжно
  проходят через обычные текстовые тулы/шелл-экранирование).
- **Проверено:**
  - Побайтовое сравнение старой (git HEAD) и новой версии файла: после
    обратной подстановки `\x00`/`\x7f` (текст) → сырые байты содержимое
    полностью идентично — изменилось только представление, не сам текст.
  - Прямое исполнение regex в Node.js — извлечён `cleanChunk` regex из
    старой (HEAD) и новой версии файла, прогнан на 8 репрезентативных
    строках (кириллица, градусы/№/%, знаки зодиака ♈-♓, "случайная
    латиница" типа café/naïve, control-символы, CJK-символы, markdown-
    мусор, пустая строка, чистый ASCII) — результат идентичен байт в
    байт для каждой строки в обеих версиях.
  - `tsc --noEmit` — 0 ошибок.
  - Юнит-тестов на фронтенде в проекте нет вообще (test runner не
    настроен) — ручная проверка через Node сыграла роль регрессионного
    теста для этой конкретной функции.
  - `git diff` для этого коммита всё ещё показывает "Binary files
    differ" — ожидаемо и неизбежно для самого переходного коммита,
    т.к. старая сторона (HEAD) физически содержит настоящий NUL-байт;
    начиная со следующего коммита, затрагивающего этот файл, diff будет
    обычным текстовым.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Перепроверить `shareToTelegram` на реальном телефоне после деплоя
  - Настроить webhook URL ЮKassa в личном кабинете

## 2026-07-06 — ТЗ-037c: SEO-страницы на 5 языках (615 страниц)

- **Контекст/находки:**
  - Языки: en, es, pt, tr, uk (код украинского — `uk`, не `ua` — так во
    всём проекте). 123 страницы × 5 языков = 615 новых + 3 хаба на язык.
  - Таблица `SeoContent` УЖЕ имела колонку `lang` и индекс
    `(page_type, slug, lang)` — мультиязычность была заложена, но
    `seo_generator.py` хардкодил `lang=="ru"` в SELECT и INSERT.
  - Готовых переводов контента нет (i18n — только UI-строки), поэтому
    контент генерируется AI, как и русский — через тот же пайплайн.
  - Попутные баги, закрытые этим тикетом: (1) `_CLEAN_RE` вырезал
    турецкие буквы ğ/ş/ı/İ (Latin Extended-A вне разрешённых диапазонов);
    (2) существование строки в `warm_seo_cache` проверялось без фильтра
    по lang; (3) JSON-LD BreadcrumbList нумерологии ссылался на
    несуществующий хаб `/numerology` (404) — сокращён до 2 крошек.
- **Сделано (бэкенд):**
  - `app/data/seo_i18n.py` (новый) — статические переводы: UI-хром
    (~42 ключа × 6 языков), знаки зодиака (имена/даты/стихии/камни/цвета,
    12 × 5), Старшие Арканы (22 × 5), ранги/масти + пер-языковый формат
    имён Младших Арканов (турецкий — масть первой с притяжательным
    аффиксом: «Asa İkilisi»), руны (латиница для en/es/pt/tr, кириллица
    для uk), архетипы нумерологии; хелперы `localize_*`, `abs_url`,
    `hreflang_alternates` (7 пар: 6 языков + x-default → русская версия).
  - `seo_generator.py` — `get_seo_content(..., lang)`; для ru — прежние
    промпты байт-в-байт, для 5 новых — английские мастер-промпты с
    явной директивой целевого языка (данные передаются уже
    локализованными); **stale-while-revalidate**: протухшая строка
    отдаётся сразу, обновление — фоновой задачей (краулеры больше не
    ждут 10–20с на регенерации); пер-языковые fallback'и с маркером
    `_fallback` → шаблон ставит `noindex, follow` (пустышки не
    индексируются, автоматически откроются после генерации контента);
    `warm_seo_cache` — только языки из `settings.seo_warm_langs`
    (default "ru" — деплой не запускает часы фоновой генерации).
  - `seo_pages.py` — каждый хендлер получил второй декоратор
    `/{lang}/...` (язык читается из `request.path_params`, НЕ из
    сигнатуры — иначе FastAPI биндит его из query-string на корневых
    роутах, что и было первой версией бага в тестах); `?lang=xx` из
    старой разметки → 301 на `/{xx}/...`; canonical — self-referencing
    на каждой версии; sitemap.xml — 757 `<loc>` (126 путей × 6 языков +
    главная) с `xhtml:link` hreflang-аннотациями по спецификации.
  - Шаблоны (base + 7) — `<html lang>`, hreflang-цикл (заменил мёртвые
    `?lang=`-ссылки и добавил отсутствовавший en), весь хром из
    словаря переводов, переключатель языков обычными `<a href>` под
    крошками, JSON-LD с `inLanguage` и переведёнными крошками,
    внутренние ссылки с префиксом языка.
  - `scripts/generate_seo_translations.py` (новый) — батч-генерация:
    `--langs/--types/--slugs/--force/--delay/--dry-run`, resume
    (пропускает существующие строки), экспоненциальный backoff, сводка
    неудач, pre-flight проверка `OPENROUTER_API_KEY`, отклоняет `ua`
    с подсказкой про `uk`.
  - `nginx/nginx.prod.conf` — regex SEO-локации расширен префиксом
    `((en|es|pt|tr|uk)/)?`; порядок локаций сохранён (статика по
    расширениям — раньше, `/tarot/5.jpg` по-прежнему уходит на
    frontend). Синтаксис проверен `nginx -t` в docker.
- **Проверено:**
  - `pytest` — **125 passed, 2 skipped** (29 новых SEO-тестов: языковые
    страницы/хабы/SVG, валидация языка (404 для `/de/...`), 301-редиректы
    `?lang=`, RU-регрессия (canonical/title/крошки байт-в-байт, включая
    отсутствие `?lang=` и `/ru/`-ссылок), sitemap ровно 757 loc +
    well-formed XML, noindex на fallback).
  - SSR-чек через ASGI (эквивалент curl): `/es/zodiac/aries`,
    `/tr/tarot/the-fool`, `/uk/runes/fehu`, `/en/numerology/life-path-7`,
    `/pt/zodiac` — правильный `<html lang>`, локализованные title/h1,
    self-canonical, 7 hreflang, переключатель со всеми 6 языками.
  - `tsc --noEmit` — 0 ошибок (фронтенд не затронут).
- **Ручные шаги для Саши после деплоя:**
  1. **Запустить батч-генерацию контента на проде** (~1.5–2 часа на все
     615 страниц, стоимость порядка нескольких $ OpenRouter):
     `docker compose exec backend python scripts/generate_seo_translations.py`
     (можно частями: `--langs es`, `--types zodiac` и т.д.; прерванный
     запуск продолжается с места остановки). До генерации страницы
     отдают короткую заглушку с `noindex` — не индексируются.
  2. Выборочно проверить контент: `curl https://mystral.space/es/zodiac/aries`
     и 3–5 других страниц на языках — текст должен быть на целевом языке.
  3. Отправить обновлённый sitemap.xml в Яндекс.Вебмастер и Google
     Search Console.
- **Следующий шаг:**
  - Alembic миграции (вместо create_all)
  - Тестирование уведомлений на VPS
  - Перепроверить `shareToTelegram` на реальном телефоне после деплоя
  - Настроить webhook URL ЮKassa в личном кабинете
  - Честный per-page lastmod в sitemap (по `generated_at`) — бэклог
  - Уникальный индекс `(page_type, slug, lang)` от гоночных дублей — бэклог

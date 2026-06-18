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
  - TZ-010: Лунный календарь (страница Moon)
  - Alembic миграции (вместо create_all)

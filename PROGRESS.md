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
  - TZ-004: `docker-compose up --build` — запуск всего стека
  - TZ-005: Alembic autogenerate первой миграции
  - TZ-006: Auth через Telegram (initData валидация, JWT выдача)
  - TZ-007: react-router, навигация между страницами

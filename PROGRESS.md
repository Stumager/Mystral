# Mystral — прогресс разработки

## 2026-07-06 — ТЗ-060 доп. фикс #2: тот же обрыв, но уже без «раздумий вслух»

### Completed
- Прод после фикса #1: снова `Expecting ',' delimiter`, но контент чистый (intro+10 секций+5 FAQ, без саморассуждений — анти-rambling сработала). Обрыв на последнем поле `cta_text`.
- Причина неизвестности: `finish_reason` от API не логировался — не было прямого сигнала "обрыв по лимиту токенов vs другая ошибка".
- `GENERATION_MAX_TOKENS`: 4096 → **6144**.
- Логирование `finish_reason`: если `"length"` — WARNING до попытки парсинга.

### Problems found
- tiktoken-оценка (cl100k_base, прокси для токенизатора DeepSeek) легла в диапазон, где 4096 могло не хватить впритык — цифра ненадёжна, см. фикс #3.

### Verified
- Новый тест в `test_seo_generator.py` (13→14): мок `finish_reason="length"` + обрезанный JSON — проверяет лог и контролируемый fallback. Полный `pytest` — 139 passed, 2 skipped.
- Прод-прогон `--langs en,tr --types zodiac --slugs aries,taurus,gemini`: **3 generated, 3 skipped, 0 failed**. ТЗ-060 закрыто (на тот момент) — можно запускать оставшиеся ~600 страниц.

### Next step
- `git pull && ./deploy.sh`. Если `Expecting ',' delimiter` вернётся: `finish_reason=length` в логе → токен-бюджет (поднять лимит ещё); без него → другой класс ошибки.

---

## 2026-07-06 — ТЗ-060 доп. фикс #3: 6144 тоже не хватило

### Completed
- Полный прогон 615 страниц: после 6 успешных en-страниц — `zodiac/capricorn/en` обрезан, `finish_reason=length` в логе подтвердил причину (сигнал из фикса #2 сработал).
- `GENERATION_MAX_TOKENS`: 6144 → **12000** (сразу щедрый запас, не по чуть-чуть). `max_tokens` — потолок, не стоимость: платится по факту сгенерированного.

### Problems found
- tiktoken-оценка по смещению обрыва дала ~3–4.5k токенов — противоречит факту обрыва при лимите 6144. Вывод: cl100k_base недостаточно точно аппроксимирует токенизатор DeepSeek для таких расчётов — дальше полагаться на эмпирику (реальные обрывы), не на вычисления.

### Verified
- Регрессионный тест на порог `GENERATION_MAX_TOKENS >= 12000`. Полный `pytest` — 139 passed, 2 skipped.

### Next step
- `git pull && ./deploy.sh`, продолжить полный прогон (resume пропустит уже успешные страницы): `docker compose exec backend python scripts/generate_seo_translations.py`. Обрыв с `finish_reason=length` → лимита всё ещё не хватает, прислать лог; без него → другой класс проблемы.

---

## 2026-07-07 — ТЗ-037c/ТЗ-060: полная батч-генерация завершена

### Completed
- Прод: **577 generated, 38 skipped, 0 failed** — все 615 страниц (123 × 5 языков), ноль сбоев парсинга JSON. 38 skipped — уже сгенерированные в пробных прогонах, resume отработал корректно.
- Все три уровня фиксов ТЗ-060 (`response_format=json_object`, прогрессия `GENERATION_MAX_TOKENS` 3000→4096→6144→12000, анти-rambling промпт, логирование `finish_reason`) в сумме дали 0% отказов на полном объёме.
- ТЗ-037c закрыто по контенту.

### Next step
- Ручное (вне доступа Claude Code): проверить несколько страниц curl'ом (`/es/zodiac/aries`, `/tr/tarot/the-fool`, `/uk/runes/fehu`) на язык контента; отправить обновлённый `sitemap.xml` в Яндекс.Вебмастер и Google Search Console.
- Alembic миграции (вместо create_all); тестирование уведомлений на VPS; перепроверить `shareToTelegram` на телефоне; webhook URL ЮKassa в личном кабинете; честный per-page lastmod в sitemap — бэклог; уникальный индекс `(page_type, slug, lang)` от гоночных дублей — бэклог.

---

## 2026-07-07 — ТЗ-061: возврат средств не отзывал Pro-статус (критический баг)

### Completed
- Найдено: ТЗ-038b обрабатывал `payment.succeeded`/`payment.canceled`, но не `refund.succeeded`. Подтверждено на тесте: оплата → Pro → возврат → Pro остался активным бессрочно. Финансовая дыра.
- API ЮKassa: объект `refund` содержит `id` (ID возврата, НЕ платежа), `status`, `payment_id`, `amount`; вебхук — та же обёртка `{"type":"notification","event":"refund.succeeded","object":{...}}`. Частичные возвраты существуют (от 1₽).
- Решение (согласовано с Сашей): отзывать Pro при любом возврате (полном или частичном), без сравнения суммы — проще и безопаснее для бизнеса.
- `backend/app/api/v1/payments.py`:
  - `_revoke_pro(user)` — зеркалит `POST /admin/users/{id}/revoke-pro` (`tier="free"`, `expires_at=None`).
  - `_verify_and_revoke_refund(refund_id, session)` — обратный `GET /v3/refunds/{id}` к API ЮKassa (не доверяем телу вебхука), находит `Payment` по `payment_id`, отзывает Pro. Идемпотентно (уже `status="refunded"` → пропуск).
  - `yukassa_webhook` — принимает `refund.succeeded`; `object.id` для `refund.*` — ID возврата, не платежа (payment_id внутри объекта возврата).
  - `Payment.status` — добавлено значение `refunded` в комментарий (миграция не нужна — поле `str`, схема через `create_all`).

### Verified
- `TestYukassaRefund` (6 тестов): полный цикл оплата→Pro→возврат→отозван; частичный возврат тоже отзывает; идемпотентность повтора; возврат по неизвестному платежу → 400 без краша; тело вебхука врёт о статусе → переверификация не отзывает Pro; отсутствие `object.id` → `no_refund_id` без краша.
- Полный `pytest` — **145 passed, 2 skipped** (было 139, +6, без регрессий). `tsc --noEmit` — 0 ошибок.

### Next step
- Ручное (вне доступа — личный кабинет ЮKassa и прод-БД):
  1. Включить подписку на `refund.succeeded` в личном кабинете ЮKassa (Интеграция → HTTP-уведомления).
  2. Вручную снять Pro со своего тестового аккаунта (`POST /admin/users/{user_id}/revoke-pro` с admin-токеном) — старый вебхук повторно не придёт.
- Alembic миграции; тестирование уведомлений на VPS; перепроверить `shareToTelegram`; webhook URL ЮKassa; per-page lastmod в sitemap — бэклог; уникальный индекс `(page_type, slug, lang)` — бэклог.

---

## 2026-07-08 — Полный аудит проекта + фикс: ежедневный гороскоп в Telegram обрывался на полуслове

### Completed
- Полный функциональный аудит (8 параллельных read-only агентов, каждая находка перепроверена по коду, не по ТЗ/PROGRESS.md). Полный отчёт: `docs/archive/AUDIT_2026-07-07.md` (не читать целиком без необходимости — точечно смотреть нужный раздел). Топ-находки: реферальная программа не работает с момента внедрения (`RegisterRequest` не принимает `ref_code`); возврат Telegram Stars не отзывает Pro (тот же класс бага, что ТЗ-061 для ЮKassa); `/natal/calculate` и `/natal/svg` без авторизации и rate limit; push-уведомления никто не вызывает (только ручной self-test); структурные данные AI-фич (карты/руны/планеты/знаки) только ru/en; Privacy.tsx и Terms.tsx противоречат друг другу по сроку хранения данных (12 мес vs 30 дней — код подтверждает 30).
- Найдено по скриншоту (push "Гороскоп на сегодня"): текст обрывался на середине предложения. Причина — `app/services/horoscope.py:35` (`generate_horoscope`, только для планировщика Telegram-рассылки; интерактивный экран в приложении использует отдельный путь `max_tokens=700`, `horoscope.py:107`, не затронут) — `max_tokens=200` мало для 60-70 слов на кириллице. Тот же класс бага, что 3 раза чинили в ТЗ-060.
- `GENERATION_MAX_TOKENS` вынесен в константу, 200 → **500**. Логирование `finish_reason == "length"`.

### Verified
- `tests/test_horoscope_service.py` (3 теста): регрессия на порог `>= 500`, мок обрезанного/полного ответа. Полный `pytest` — **148 passed, 2 skipped** (было 145, без регрессий).

### Next step
- Alembic миграции (вместо create_all); перепроверить `shareToTelegram` на телефоне; webhook URL ЮKassa; per-page lastmod в sitemap — бэклог; уникальный индекс `(page_type, slug, lang)` — бэклог.
- Приоритизировать находки `AUDIT_2026-07-07.md` в отдельные тикеты: реферальная программа, возврат Stars, `/natal` без auth+rate limit, push, языковой пробел, противоречие Privacy/Terms.
- Подписка на `refund.succeeded` + ручное снятие Pro со своего аккаунта (см. ТЗ-061 выше).

---

## 2026-07-11 — ТЗ-062: фикс UUID в composite_interpret (500 на каждый вызов)

### Completed
- Диагностика (найдено в `docs/archive/AUDIT_2026-07-07.md`, подтверждено эмпирически по запросу Саши) — `compatibility.py:603`: `session.get(UserPartner, req.partner_id)` передавал str вместо UUID. Падало со `StatementError`/`AttributeError: 'str' object has no attribute 'hex'` на каждый вызов, для любого пользователя и раздела — весь AI-интерпретатор Composite Chart (overview/planets/aspects/advice) был нерабочим. Сам расчёт Composite Chart (не интерпретация, `compat_composite`) не затронут — там уже стоял `UUID(req.partner_id)`.
- Добавлен общий `_parse_partner_id(partner_id: str) -> UUID` в `compatibility.py`: оборачивает `UUID()`, превращает `ValueError` в `HTTPException(422, "Invalid partner_id")`. Ни одно из 4 мест разбора `partner_id` в файле раньше не обрабатывало невалидный формат (свалились бы в общий 500) — применено единообразно во всех четырёх местах (строки 208, 228, 526, 603), не только в багованном.

### Verified
- Новый `tests/test_compatibility.py`: невалидный формат partner_id → 422, не 500; partner_id чужого партнёра → 404, не 500. Оба гоняются без Docker.
- По одному тесту на все 4 раздела (overview/planets/aspects/advice) с валидным partner_id — требуют реального kerykeion/pyswisseph (нет Windows-колеса), помечены `skipif` по образцу `test_natal_timezone.py`: локально скипаются, реально прогоняются в Docker/CI.
- Полный `pytest` — **150 passed, 6 skipped** (было 148/2 — +2 passed, +4 skipped, без регрессий).
- `tsc --noEmit` — 0 ошибок. Фронтенд не менялся: `streamRequest`/`parseApiError` уже показывают `body.detail` для любого не-2xx статуса вне 401/402/429/5xx — новый 422 подхватывается существующей веткой без правок. `partner_id` на фронте всегда берётся из списка партнёров (реальный UUID), так что 422 — защитный случай на бэкенде, не реальный пользовательский сценарий.

### Next step
- Прогнать 4 skipped-теста реально в Docker (`docker compose exec backend pytest tests/test_compatibility.py -v`) на сервере — Саша делает деплой/pull сам.
- Alembic миграции; перепроверить `shareToTelegram`; webhook URL ЮKassa; per-page lastmod в sitemap; уникальный индекс `(page_type, slug, lang)` — бэклог.
- Остальные находки `AUDIT_2026-07-07.md`: реферальная программа, возврат Stars, `/natal` без auth+rate limit, push, языковой пробел, Privacy/Terms — в отдельные тикеты.

---

## 2026-07-11 — ТЗ-063: реферальная программа не начисляла бонусы никогда

### Completed
- Диагностика (отдельным заходом, до фикса): бэкенд-логика начисления (`POST /referrals/apply`, `_extend_pro`, `ReferralLog`) уже была полностью реализована и покрыта 5 тестами — разрыв был только в интеграции. `RegisterRequest` не принимал `ref_code`; фронтенд ни разу не вызывал `/referrals/apply`; Telegram-пути (auto-login/widget/merge) вообще не касались реферального кода; `startapp`/`start_param` deep-link не читался совсем (`initDataUnsafe` даже не был в типах).
- Решение: не трогать `RegisterRequest`/`register()` — вместо этого фронтенд сам вызывает уже готовый и протестированный `/referrals/apply` в момент, когда у нового пользователя впервые появляется JWT (email — сразу после `/auth/verify-email`; Telegram — сразу после `/auth/telegram` при `is_new === true`, во всех трёх местах, где дергается этот эндпоинт: auto-login, widget-login, и теперь единообразно).
- `backend/app/api/v1/referrals.py`: rate-limit на `/referrals/apply` (переиспользован `_check_ip_rate`/`_get_ip` из `auth.py`, тот же лимит 5/час, что у `register`); гейт `email_verified` для email-аккаунтов — с явным исключением для Telegram-нативных (`email is None`), иначе Telegram-бонусы никогда бы не начислялись (у них `email_verified` по умолчанию `False` и никогда не станет `True`); коллизия `ref_code` теперь исключена ретраем в `_ensure_ref_code` (колонка не была `unique`).
- Frontend: `utils/telegram.ts` — тип `initDataUnsafe.start_param`; `main.tsx` — мост `start_param` → тот же `localStorage["mystral_ref_code"]`, что и у веб-пути `/ref/CODE`, один механизм применения на оба источника; новый `applyStoredReferralCode()` в `utils/api.ts`; подключён в `VerifyEmail.tsx`, `AuthContext.tsx` (auto-login), `LoginScreen.tsx` (widget-login); убрано мёртвое поле `ref_code` из тела `/auth/register` (бэкенд его больше не читает и не будет). `Profile.tsx` — явная строка `total_bonus_days`.

### Verified
- Новый `TestReferralFullCycle` в `test_profile.py` (4 теста): полный HTTP-цикл email (register→verify→apply, оба получают Pro); неверифицированный email → 400, бонус не начислен; Telegram-нативный пользователь (`email=None`, `email_verified=False`) **не** блокируется гейтом — ключевой тест, доказывающий, что фикс не сломал Telegram; rate-limit на 6-й попытке → 429.
- Полный `pytest` — **154 passed, 6 skipped** (было 150/6, +4 passed, без регрессий).
- `tsc --noEmit` — 0 ошибок.
- Живая ручная проверка в браузере — **выполнена** после того, как Docker поднялся (первая попытка упёрлась в краш Docker Desktop, вторая — в устаревший образ backend без `json-repair`, пересобран `docker compose build backend`). Полный цикл на 2 реальных аккаунтах через настоящий UI: Alice регистрируется → верифицирует email → копирует ссылку `/ref/3ZERN953` → Bob переходит по ней (код лёг в `localStorage`) → регистрируется → верифицирует email → в network-логе браузера виден автоматический `POST /referrals/apply → 200 OK` сразу после `verify-email`. Проверено в БД напрямую: Alice `subscription_tier=pro`, `expires_at=+7д`, `ref_bonus_days_given=7`; Bob `subscription_tier=pro`, `expires_at=+3д`, `referred_by=<Alice.id>`; `referral_log` — 1 строка. В профиле Alice вживую: «Mystral Pro активен · Pro до 18 июля», «Получено дней Pro: +7», счётчик рефералов «1», в списке приглашённых — «Bo\*\*\* +7д».
- Telegram `start_param`-путь — покрыт только `tsc`/код-ревью, не проверен вживую (нужен настоящий Telegram-клиент/бот, недоступно даже с поднятым Docker).

### Next step
- `scheduler.py` `ReferralLog.user_id` краш — уже отдельный тикет-предложение (не в рамках ТЗ-063).
- Тестовые аккаунты `alice@test.com`/`bob@test.com` остались в локальной dev-БД (Docker) — не мешают, можно почистить или оставить для дальнейшего ручного тыканья.
- Остальные находки `AUDIT_2026-07-07.md`: возврат Stars, `/natal` без auth+rate limit, push, языковой пробел, Privacy/Terms — в отдельные тикеты.

# Webinar KPI — Instrukcja wdrożenia na Vercel

## Co masz w folderze
```
webinar-kpi/
├── index.html          ← cała apka
├── api/
│   ├── meta.js         ← backend Meta Ads API
│   ├── webinarjam.js   ← backend WebinarJam API
│   └── notion.js       ← push sesji do bazy Notion (wodospad)
├── vercel.json         ← konfiguracja
└── INSTRUKCJA.md       ← ten plik
```

---

## Krok 1 — Załóż konto na Vercel (darmowe)
1. Wejdź na https://vercel.com
2. Kliknij "Sign Up" → zaloguj się przez GitHub lub email
3. Potwierdź email jeśli rejestrujesz przez email

---

## Krok 2 — Wdróż projekt

### Opcja A — przez przeglądarkę (najprościej)
1. Wejdź na https://vercel.com/new
2. Kliknij "Browse" lub przeciągnij folder `webinar-kpi` na stronę
3. Kliknij "Deploy"
4. Poczekaj ~30 sekund → dostaniesz link np. `https://webinar-kpi-abc123.vercel.app`

### Opcja B — przez terminal
```bash
npm i -g vercel
cd webinar-kpi
vercel
```

---

## Krok 3 — Dodaj tokeny API (WAŻNE)

Po deployu wejdź w ustawienia projektu na Vercelu:
**Project → Settings → Environment Variables**

Dodaj dwie zmienne:

| Name | Value |
|------|-------|
| `META_TOKEN` | twój Meta Access Token |
| `WJ_API_KEY` | twój WebinarJam API Key |
| `NOTION_TOKEN` | twój Notion Integration Token (opcjonalnie — patrz niżej) |

Po dodaniu zmiennych kliknij **Redeploy** (Deployments → trzy kropki → Redeploy).

---

## Skąd wziąć Meta Access Token?

1. Wejdź na https://developers.facebook.com/tools/explorer
2. Zaloguj się swoim kontem Facebook
3. Wybierz swoją aplikację (lub utwórz nową)
4. Kliknij "Generate Access Token"
5. Zaznacz uprawnienia: `ads_read`, `read_insights`
6. Skopiuj token

⚠ Token wygasa po ~60 dniach. Możesz wygenerować długoterminowy token przez:
https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived

---

## Skąd wziąć WebinarJam API Key?

1. Wejdź na panel WebinarJam
2. Kliknij ikonę profilu → Advanced Integration
3. Znajdź pole "API Key"
4. Jeśli nie masz jeszcze dostępu: złóż wniosek na
   https://support.webinarjam.com/support/solutions/articles/153000168623
   (zatwierdzają do 2 dni roboczych)

---

## Integracja z Notion (wodospad) — opcjonalna

Pozwala wysyłać zapisane sesje wprost do bazy Notion (np. wodospad Aleksandra).
Każde kliknięcie „Zapisz sesję" automatycznie tworzy nowy wpis w bazie,
a przycisk „↑ Wyślij do Notion" w sekcji Historia wysyła wszystkie zapisane sesje hurtem.

### 1. Utwórz Notion Integration
1. Wejdź na https://www.notion.so/profile/integrations
2. Kliknij **+ New integration** → nadaj nazwę (np. „Webinar KPI")
3. Wybierz workspace, **Internal integration**
4. Skopiuj **Internal Integration Secret** (zaczyna się od `secret_...` lub `ntn_...`)
5. Wklej do Vercela jako zmienną `NOTION_TOKEN` → **Redeploy**

### 2. Udostępnij bazę (wodospad) integracji
1. Otwórz bazę „wodospad" w Notion
2. Prawy górny róg → `...` → **Connections** → **Add connections** → wybierz utworzoną integrację

### 3. Skopiuj Database ID
Z URL bazy, np. `https://notion.so/workspace/<DATABASE_ID>?v=...` —
Database ID to 32-znakowy ciąg (bez myślników też zadziała).
Wpisz go w apce: **⚙ Ustawienia → Notion Database ID → Zapisz ustawienia**.

### 4. Kolumny w bazie Notion
Apka rozpoznaje kolumny po nazwach (PL/EN, wielkość liter nie ma znaczenia).
Pasują m.in.:

| Pole sesji | Akceptowane nazwy kolumn | Typ Notion |
|------------|---------------------------|------------|
| Tytuł      | (dowolna kolumna typu *Title*) | Title |
| Zakres dat | `Data`, `Okres`, `Date` | Date (range) |
| Spend      | `Spend`, `Wydatki`, `Budżet`, `Koszt reklamy` | Number |
| Kliknięcia | `Clicks`, `Kliknięcia` | Number |
| Zapisy     | `Leads`, `Zapisy`, `Leady`, `Rejestracje` | Number |
| Przyszło   | `Show up`, `Przyszło`, `Uczestnicy`, `Obecni` | Number |
| Sprzedaż   | `Sales`, `Sprzedaż`, `Kupili` | Number |
| Cena       | `Price`, `Cena`, `Cena kursu` | Number |
| Przychód   | `Revenue`, `Przychód` | Number |
| Zysk       | `Profit`, `Zysk` | Number |
| CPL        | `CPL`, `Koszt zapisu` | Number |
| LP CR%     | `LP CR`, `LPCR`, `CR%` | Number |
| Show up %  | `Show up rate`, `Show up %`, `Frekwencja` | Number |
| CPATT      | `CPATT`, `Koszt uczestnika` | Number |
| Close %    | `Close rate`, `Sprzedaż %`, `Konwersja sprzedaży` | Number |
| ROAS       | `ROAS` | Number |

Apka wyśle tylko te kolumny, które naprawdę istnieją w bazie — reszta jest pomijana,
więc nie musisz mieć wszystkich. Wymagana jest co najmniej jedna kolumna typu *Title*.

---

## Krok 4 — Skonfiguruj apkę

1. Otwórz swoją apkę pod adresem z Vercela
2. Wpisz hasło: `Alufelga10`
3. Kliknij ⚙ Ustawienia
4. Wpisz:
   - **Meta Ad Account ID** — znajdziesz w Meta Business Suite → ustawienia konta
     (sama liczba, bez "act_")
   - **WebinarJam Webinar ID** — znajdziesz w URL webinaru lub przez API
5. Kliknij "Zapisz ustawienia"

---

## Jak używać

1. Wybierz przedział dat (od → do)
2. Kliknij "↓ Pobierz z Meta" → automatycznie wypełni spend i kliknięcia
3. Kliknij "↓ Pobierz z WebinarJam" → automatycznie wypełni zapisy i obecnych
4. Wpisz ręcznie: ile osób kupiło + cena kursu
5. KPI liczą się na żywo
6. Kliknij "Zapisz sesję" → trafia do historii

---

## Problemy?

**"META_TOKEN not set"** → dodaj zmienną środowiskową w Vercelu i zrób Redeploy

**"WebinarJam error"** → sprawdź czy Webinar ID jest poprawne (sama liczba)

**Meta zwraca 0** → sprawdź czy Ad Account ID jest poprawne i czy token ma uprawnienia `ads_read`

**"NOTION_TOKEN not set"** → dodaj zmienną w Vercelu i Redeploy

**Notion: `object_not_found`** → integracja nie ma dostępu do bazy. Otwórz bazę w Notion → `...` → Connections → Add connections → wybierz swoją integrację

**Notion: `has no matching columns`** → nazwy kolumn w bazie nie pasują do żadnego aliasu z tabeli wyżej. Dodaj/zmień nazwę kolumny (np. „Spend", „Zapisy") lub dorzuć kolumnę typu *Title*

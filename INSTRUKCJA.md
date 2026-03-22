# Webinar KPI — Instrukcja wdrożenia na Vercel

## Co masz w folderze
```
webinar-kpi/
├── index.html          ← cała apka
├── api/
│   ├── meta.js         ← backend Meta Ads API
│   └── webinarjam.js   ← backend WebinarJam API
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

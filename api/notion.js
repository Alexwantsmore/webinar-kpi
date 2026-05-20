// Push a webinar KPI session to a Notion database ("waterfall").
// Schema-aware: fetches the database schema, then writes only the properties
// that exist there, matched by aliases (PL/EN). Mismatched/missing columns
// are silently skipped so a single endpoint works against different layouts.

const NOTION_VERSION = '2022-06-28';

const ALIASES = {
  title:     ['name', 'nazwa', 'tytuł', 'tytul', 'sesja', 'webinar', 'okres'],
  dateFrom:  ['data od', 'date from', 'od', 'start', 'początek', 'poczatek'],
  dateTo:    ['data do', 'date to', 'do', 'end', 'koniec'],
  dateRange: ['data', 'date', 'okres', 'date range', 'zakres dat', 'przedział dat'],
  spend:     ['spend', 'wydatki', 'wydatki na reklamę', 'wydatki na reklame', 'budżet', 'budzet', 'koszt reklamy', 'koszty'],
  clicks:    ['clicks', 'kliknięcia', 'klikniecia', 'kliki'],
  leads:     ['leads', 'zapisy', 'leady', 'zapisani', 'ilość zapisów', 'ilosc zapisow', 'rejestracje'],
  showup:    ['showup', 'show up', 'show-up', 'przyszło', 'przyszlo', 'uczestnicy', 'obecni', 'ile osób przyszło', 'ile osob przyszlo'],
  sales:     ['sales', 'sprzedaż', 'sprzedaz', 'kupili', 'kupujący', 'kupujacy', 'ile osób kupiło', 'ile osob kupilo'],
  price:     ['price', 'cena', 'cena kursu'],
  revenue:   ['revenue', 'przychód', 'przychod', 'obrót', 'obrot'],
  profit:    ['profit', 'zysk'],
  cpl:       ['cpl', 'koszt zapisu', 'koszt za zapis'],
  lpcr:      ['lp cr', 'lpcr', 'lp cr%', 'cr lp', 'cr%', 'lp conversion'],
  showrate:  ['show up rate', 'show up %', 'showup rate', 'showrate', 'widzowie', 'widzowie %', 'show%', 'frekwencja'],
  cpatt:     ['cpatt', 'cpa', 'koszt uczestnika', 'koszt za uczestnika'],
  closerate: ['close rate', 'close%', 'sprzedaż %', 'sprzedaz %', 'closerate', 'konwersja sprzedaży', 'konwersja sprzedazy'],
  roas:      ['roas'],
};

const normalize = (s) => String(s || '').toLowerCase().trim().replace(/\s+/g, ' ');

function findProp(schema, aliases) {
  const wanted = new Set(aliases.map(normalize));
  for (const [name, def] of Object.entries(schema)) {
    if (wanted.has(normalize(name))) return { name, type: def.type };
  }
  return null;
}

function num(v) {
  const n = typeof v === 'number' ? v : parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

function textValue(type, content) {
  const text = [{ type: 'text', text: { content: String(content) } }];
  if (type === 'title') return { title: text };
  if (type === 'rich_text') return { rich_text: text };
  return null;
}

function numberValue(type, value) {
  const n = num(value);
  if (n === null) return null;
  if (type === 'number') return { number: n };
  if (type === 'rich_text') return { rich_text: [{ type: 'text', text: { content: String(n) } }] };
  if (type === 'title') return { title: [{ type: 'text', text: { content: String(n) } }] };
  return null;
}

function dateValue(type, start, end) {
  if (!start) return null;
  if (type === 'date') {
    const payload = { start };
    if (end && end !== start) payload.end = end;
    return { date: payload };
  }
  if (type === 'rich_text') {
    const content = end && end !== start ? `${start} → ${end}` : start;
    return { rich_text: [{ type: 'text', text: { content } }] };
  }
  return null;
}

function buildProperties(schema, session) {
  const props = {};
  const set = (key, builder) => {
    const found = findProp(schema, ALIASES[key]);
    if (!found) return;
    const value = builder(found.type);
    if (value) props[found.name] = value;
  };

  // Title — find the actual title property in the schema, regardless of name.
  const titleEntry = Object.entries(schema).find(([, def]) => def.type === 'title');
  if (titleEntry) {
    const [titleName] = titleEntry;
    const label = session.dateFrom && session.dateTo
      ? (session.dateFrom === session.dateTo ? `Webinar ${session.dateFrom}` : `Webinar ${session.dateFrom} → ${session.dateTo}`)
      : `Webinar ${new Date().toISOString().slice(0, 10)}`;
    props[titleName] = { title: [{ type: 'text', text: { content: label } }] };
  }

  set('dateRange', (t) => dateValue(t, session.dateFrom, session.dateTo));
  set('dateFrom',  (t) => dateValue(t, session.dateFrom, null));
  set('dateTo',    (t) => dateValue(t, session.dateTo, null));

  const numericFields = ['spend', 'clicks', 'leads', 'showup', 'sales', 'price',
                          'revenue', 'profit', 'cpl', 'lpcr', 'showrate', 'cpatt',
                          'closerate', 'roas'];
  for (const f of numericFields) {
    set(f, (t) => numberValue(t, session[f]));
  }

  return props;
}

async function notionRequest(path, token, init = {}) {
  const res = await fetch(`https://api.notion.com/v1${path}`, {
    ...init,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Notion-Version': NOTION_VERSION,
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.message || data.error || `Notion API ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const token = process.env.NOTION_TOKEN;
  if (!token) return res.status(500).json({ error: 'NOTION_TOKEN not set in environment variables' });

  const body = req.body && typeof req.body === 'object' ? req.body : (() => {
    try { return JSON.parse(req.body || '{}'); } catch { return {}; }
  })();

  const databaseId = (body.database_id || '').replace(/-/g, '').trim();
  const session = body.session || {};
  if (!databaseId) return res.status(400).json({ error: 'database_id is required' });
  if (!session || typeof session !== 'object') return res.status(400).json({ error: 'session payload is required' });

  try {
    const db = await notionRequest(`/databases/${databaseId}`, token);
    const properties = buildProperties(db.properties || {}, session);

    if (Object.keys(properties).length === 0) {
      return res.status(400).json({
        error: 'Notion database has no matching columns. Expected at least a title or a numeric column (spend, leads, sales, ...).',
        available_properties: Object.keys(db.properties || {}),
      });
    }

    const page = await notionRequest('/pages', token, {
      method: 'POST',
      body: JSON.stringify({
        parent: { database_id: databaseId },
        properties,
      }),
    });

    return res.status(200).json({
      ok: true,
      url: page.url,
      id: page.id,
      matched_properties: Object.keys(properties),
    });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to push to Notion: ' + err.message });
  }
}

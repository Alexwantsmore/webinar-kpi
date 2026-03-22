export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const apiKey    = process.env.WJ_API_KEY;
  const webinarId = req.query.webinar_id;

  if (!apiKey)    return res.status(500).json({ error: 'WJ_API_KEY not set in environment variables' });
  if (!webinarId) return res.status(400).json({ error: 'webinar_id is required' });

  try {
    // Step 1: get webinar details
    const webinarRes = await fetch('https://api.webinarjam.com/webinarjam/webinar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ api_key: apiKey, webinar_id: webinarId }),
    });
    const webinarData = await webinarRes.json();

    if (webinarData.status !== 'success') {
      return res.status(400).json({ error: webinarData.message || 'WebinarJam error' });
    }

    // Step 2: get registrants + attendees
    const regRes = await fetch('https://api.webinarjam.com/webinarjam/registrants', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ api_key: apiKey, webinar_id: webinarId }),
    });
    const regData = await regRes.json();

    const registrants = regData.registrants || [];
    const total       = registrants.length;
    const attended    = registrants.filter(r => r.attended === 1 || r.attended === '1' || r.attended === true).length;

    return res.status(200).json({
      webinar_name: webinarData.webinar?.name || '',
      registrants:  total,
      attended:     attended,
    });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to fetch WebinarJam data: ' + err.message });
  }
}

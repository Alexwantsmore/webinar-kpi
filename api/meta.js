export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const token     = process.env.META_TOKEN;
  const accountId = req.query.account_id;
  const dateFrom  = req.query.date_from;
  const dateTo    = req.query.date_to;

  if (!token)     return res.status(500).json({ error: 'META_TOKEN not set in environment variables' });
  if (!accountId) return res.status(400).json({ error: 'account_id is required' });
  if (!dateFrom)  return res.status(400).json({ error: 'date_from is required' });
  if (!dateTo)    return res.status(400).json({ error: 'date_to is required' });

  const fields = 'spend,clicks,impressions,reach,cpm,cpc,ctr';
  const url = `https://graph.facebook.com/v19.0/act_${accountId}/insights`
    + `?fields=${fields}`
    + `&time_range={"since":"${dateFrom}","until":"${dateTo}"}`
    + `&level=account`
    + `&access_token=${token}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.error) {
      return res.status(400).json({ error: data.error.message });
    }

    const insight = data.data?.[0];
    if (!insight) {
      return res.status(200).json({ spend: 0, clicks: 0, impressions: 0, reach: 0 });
    }

    return res.status(200).json({
      spend:       parseFloat(insight.spend       || 0),
      clicks:      parseInt(insight.clicks        || 0),
      impressions: parseInt(insight.impressions   || 0),
      reach:       parseInt(insight.reach         || 0),
      cpm:         parseFloat(insight.cpm         || 0),
      cpc:         parseFloat(insight.cpc         || 0),
      ctr:         parseFloat(insight.ctr         || 0),
    });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to fetch Meta data: ' + err.message });
  }
}

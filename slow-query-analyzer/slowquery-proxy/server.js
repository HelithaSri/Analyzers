const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Try models in order until one works
const GEMINI_MODELS = [
  'gemini-flash-latest'
];

app.post('/api/analyze', async (req, res) => {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return res.status(401).json({ error: { message: 'GEMINI_API_KEY not set. Run: export GEMINI_API_KEY=your-key' } });
  }

  const userMessage = req.body.messages?.[0]?.content || '';
  let lastError = null;

  for (const model of GEMINI_MODELS) {
    try {
      console.log(`\n→ Trying: ${model}`);

      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: userMessage }] }],
            generationConfig: { maxOutputTokens: 1000, temperature: 0.3 }
          })
        }
      );

      const raw = await response.text();
      console.log(`  HTTP: ${response.status} | Response: ${raw.substring(0, 200)}`);

      let data;
      try { data = JSON.parse(raw); }
      catch (e) {
        lastError = 'Invalid JSON: ' + raw.substring(0, 100);
        continue;
      }

      if (data.error) {
        const msg = data.error.message || JSON.stringify(data.error);
        console.log(`  Error: ${msg}`);
        lastError = msg;
        // quota/rate limit — try next model
        if (msg.includes('quota') || msg.includes('Quota') || msg.includes('rate') || msg.includes('limit: 0')) {
          continue;
        }
        // auth error — stop immediately
        if (response.status === 400 && msg.includes('API key')) {
          return res.status(401).json({ error: { message: 'Invalid API key: ' + msg } });
        }
        continue;
      }

      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) {
        lastError = 'Empty response';
        continue;
      }

      console.log(`  ✓ Success with ${model} (${text.length} chars)`);
      res.json({ content: [{ text }] });
      return;

    } catch (err) {
      console.log(`  Network error: ${err.message}`);
      lastError = err.message;
    }
  }

  console.log('\n✗ All Gemini models failed. Last error:', lastError);
  res.status(500).json({
    error: { message: `All Gemini models exhausted. Last error: ${lastError}` }
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', provider: 'Google Gemini', models: GEMINI_MODELS, key_set: !!process.env.GEMINI_API_KEY });
});

const PORT = process.env.PORT || 3333;
app.listen(PORT, () => {
  console.log(`\n✅ SlowQuery Proxy (Gemini) on http://localhost:${PORT}`);
  console.log(`   Key   : ${process.env.GEMINI_API_KEY ? '✓ Set' : '✗ NOT SET'}`);
  console.log(`   Models: ${GEMINI_MODELS.join(' → ')}`);
  console.log(`\n   Waiting for requests...\n`);
});

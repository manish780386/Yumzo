from django.http import HttpResponse

def welcome(request):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>DjangoForge</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh;
      background: #0d0d0d;
      color: #f0f0f0;
      font-family: 'Space Grotesk', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
    }
    .container { width: 100%; max-width: 720px; }

    /* Header */
    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
      padding-bottom: 24px;
      border-bottom: 1px solid #1f1f1f;
    }
    .logo {
      width: 52px; height: 52px;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px;
    }
    .header-text h1 { font-size: 1.6rem; font-weight: 700; color: #f0f0f0; letter-spacing: -0.5px; }
    .header-text p { font-size: 0.85rem; color: #666; margin-top: 3px; }

    /* Badge */
    .badge {
      display: inline-flex; align-items: center; gap: 7px;
      background: #0d2e1a;
      border: 1px solid #1a5c33;
      border-radius: 20px;
      padding: 5px 14px;
      font-size: 0.78rem; font-weight: 500;
      color: #4ade80;
      margin-bottom: 24px;
    }
    .dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; animation: blink 1.4s ease-in-out infinite; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

    /* Feature grid */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 24px;
    }
    .card {
      background: #141414;
      border: 1px solid #1f1f1f;
      border-radius: 12px;
      padding: 16px 14px;
      transition: border-color 0.2s, background 0.2s;
    }
    .card:hover { background: #1a1a1a; border-color: #2f2f2f; }
    .card .icon { font-size: 1.3rem; margin-bottom: 8px; display: block; }
    .card .name { font-size: 0.82rem; font-weight: 600; color: #e0e0e0; }
    .card .desc { font-size: 0.72rem; color: #555; margin-top: 3px; }

    /* Steps */
    .steps {
      background: #111;
      border: 1px solid #1f1f1f;
      border-radius: 14px;
      padding: 22px 24px;
      margin-bottom: 24px;
    }
    .steps-title {
      font-size: 0.7rem; font-weight: 600;
      color: #444;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-bottom: 16px;
    }
    .step { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px; }
    .step:last-child { margin-bottom: 0; }
    .step-num {
      width: 22px; height: 22px;
      border-radius: 50%;
      background: #1a2e4a;
      border: 1px solid #1e4080;
      color: #60a5fa;
      font-size: 0.72rem; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; margin-top: 1px;
    }
    .step-text { font-size: 0.83rem; color: #888; line-height: 1.6; }
    code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 5px;
      padding: 1px 7px;
      color: #a3e635;
    }

    /* Footer */
    .footer {
      text-align: center;
      font-size: 0.72rem;
      color: #333;
      padding-top: 20px;
      border-top: 1px solid #1a1a1a;
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">⚡</div>
      <div class="header-text">
        <h1>DjangoForge</h1>
        <p>Forge your backend instantly</p>
      </div>
    </div>

    <div class="badge">
      <div class="dot"></div>
      Server running
    </div>

    <div class="grid">
      <div class="card"><span class="icon">🐍</span><div class="name">Django</div><div class="desc">Web framework</div></div>
      <div class="card"><span class="icon">🔌</span><div class="name">DRF</div><div class="desc">REST APIs</div></div>
      <div class="card"><span class="icon">🌐</span><div class="name">CORS</div><div class="desc">Cross origin</div></div>
      <div class="card"><span class="icon">🔐</span><div class="name">.env</div><div class="desc">Secrets safe</div></div>
      <div class="card"><span class="icon">📦</span><div class="name">Venv</div><div class="desc">Isolated env</div></div>
      <div class="card"><span class="icon">🚫</span><div class="name">.gitignore</div><div class="desc">Git ready</div></div>
    </div>

    <div class="steps">
      <div class="steps-title">Next steps</div>
      <div class="step"><div class="step-num">1</div><div class="step-text">Run migrations — <code>python manage.py migrate</code></div></div>
      <div class="step"><div class="step-num">2</div><div class="step-text">Create admin user — <code>python manage.py createsuperuser</code></div></div>
      <div class="step"><div class="step-num">3</div><div class="step-text">Update <code>.env</code> with a strong <code>SECRET_KEY</code> before production</div></div>
      <div class="step"><div class="step-num">4</div><div class="step-text">Open Django admin panel at <code>/admin</code></div></div>
    </div>

    <div class="footer">Built with ⚡ DjangoForge &nbsp;·&nbsp; Happy coding!</div>
  </div>
</body>
</html>
"""
    return HttpResponse(html)

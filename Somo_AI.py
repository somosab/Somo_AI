<!DOCTYPE html>
<html lang="uz" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Somo AI — Aqlli Yordamchi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <style>
    /* ═══════════════════════════════════════════
       ROOT VARIABLES & RESET
    ═══════════════════════════════════════════ */
    :root {
      --bg-base: #050810;
      --bg-surface: #0c1120;
      --bg-card: #111827;
      --bg-hover: #1a2235;
      --bg-input: #0d1526;
      --bg-sidebar: #080e1c;

      --accent-cyan: #00e5ff;
      --accent-purple: #7c3aed;
      --accent-pink: #ec4899;
      --accent-green: #10b981;
      --accent-yellow: #f59e0b;
      --accent-orange: #f97316;

      --glow-cyan: 0 0 20px rgba(0,229,255,0.3), 0 0 60px rgba(0,229,255,0.1);
      --glow-purple: 0 0 20px rgba(124,58,237,0.3), 0 0 60px rgba(124,58,237,0.1);
      --glow-pink: 0 0 20px rgba(236,72,153,0.25);

      --text-primary: #f0f4ff;
      --text-secondary: #8899bb;
      --text-muted: #4a5a7a;
      --text-accent: #00e5ff;

      --border-subtle: rgba(255,255,255,0.06);
      --border-active: rgba(0,229,255,0.3);
      --border-card: rgba(255,255,255,0.08);

      --sidebar-width: 280px;
      --header-height: 60px;

      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-xl: 24px;

      --font-display: 'Syne', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --font-body: 'Inter', sans-serif;

      --transition-fast: 0.15s ease;
      --transition-med: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      --gradient-primary: linear-gradient(135deg, #00e5ff 0%, #7c3aed 100%);
      --gradient-surface: linear-gradient(135deg, rgba(0,229,255,0.05) 0%, rgba(124,58,237,0.05) 100%);
      --gradient-bg: radial-gradient(ellipse at 20% 20%, rgba(0,229,255,0.04) 0%, transparent 60%),
                     radial-gradient(ellipse at 80% 80%, rgba(124,58,237,0.04) 0%, transparent 60%),
                     #050810;
    }

    [data-theme="light"] {
      --bg-base: #f5f7fa;
      --bg-surface: #ffffff;
      --bg-card: #f0f4ff;
      --bg-hover: #e8eef8;
      --bg-input: #ffffff;
      --bg-sidebar: #1a1f2e;

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --text-accent: #0891b2;

      --border-subtle: rgba(0,0,0,0.08);
      --border-active: rgba(8,145,178,0.4);
      --border-card: rgba(0,0,0,0.1);

      --gradient-bg: radial-gradient(ellipse at 20% 20%, rgba(0,229,255,0.06) 0%, transparent 60%),
                     radial-gradient(ellipse at 80% 80%, rgba(124,58,237,0.06) 0%, transparent 60%),
                     #f5f7fa;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font-body);
      background: var(--gradient-bg);
      color: var(--text-primary);
      min-height: 100vh;
      overflow: hidden;
      display: flex;
      position: relative;
    }

    /* Ambient background orbs */
    body::before {
      content: '';
      position: fixed;
      top: -200px;
      left: -200px;
      width: 600px;
      height: 600px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      animation: orbFloat 12s ease-in-out infinite alternate;
    }

    body::after {
      content: '';
      position: fixed;
      bottom: -200px;
      right: -200px;
      width: 700px;
      height: 700px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      animation: orbFloat 15s ease-in-out infinite alternate-reverse;
    }

    @keyframes orbFloat {
      0% { transform: translate(0, 0) scale(1); }
      100% { transform: translate(40px, 40px) scale(1.1); }
    }

    /* ═══════════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
      background: rgba(0,229,255,0.2);
      border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,229,255,0.4); }

    /* ═══════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════ */
    .sidebar {
      width: var(--sidebar-width);
      height: 100vh;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 100;
      transition: transform var(--transition-med), width var(--transition-med);
      overflow: hidden;
    }

    .sidebar.collapsed {
      width: 60px;
    }

    .sidebar-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.5);
      z-index: 99;
      backdrop-filter: blur(2px);
    }

    .sidebar-overlay.active { display: block; }

    /* Sidebar header */
    .sidebar-header {
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border-subtle);
      min-height: var(--header-height);
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: var(--gradient-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 14px;
      color: #000;
      box-shadow: var(--glow-cyan);
      cursor: pointer;
      transition: transform var(--transition-fast);
    }

    .brand-logo:hover { transform: scale(1.08); }

    .brand-text {
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 17px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      opacity: 1;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .brand-text { opacity: 0; width: 0; }

    .collapse-btn {
      margin-left: auto;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      flex-shrink: 0;
    }

    .collapse-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
      border-color: var(--border-active);
    }

    .collapse-btn svg {
      transition: transform var(--transition-med);
    }

    .sidebar.collapsed .collapse-btn svg { transform: rotate(180deg); }

    /* New chat button */
    .new-chat-btn {
      margin: 12px 12px 8px;
      padding: 10px 14px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, rgba(0,229,255,0.12), rgba(124,58,237,0.12));
      border: 1px solid rgba(0,229,255,0.2);
      color: var(--accent-cyan);
      font-family: var(--font-body);
      font-weight: 500;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all var(--transition-fast);
      white-space: nowrap;
      overflow: hidden;
    }

    .new-chat-btn:hover {
      background: linear-gradient(135deg, rgba(0,229,255,0.2), rgba(124,58,237,0.2));
      border-color: rgba(0,229,255,0.4);
      box-shadow: var(--glow-cyan);
      transform: translateY(-1px);
    }

    .new-chat-btn .btn-text {
      opacity: 1;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .new-chat-btn .btn-text { opacity: 0; width: 0; overflow: hidden; }

    /* Sidebar search */
    .sidebar-search {
      padding: 8px 12px;
      position: relative;
    }

    .sidebar-search input {
      width: 100%;
      padding: 8px 12px 8px 34px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: rgba(255,255,255,0.04);
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 12px;
      outline: none;
      transition: all var(--transition-fast);
      opacity: 1;
    }

    .sidebar-search input:focus {
      border-color: var(--border-active);
      background: rgba(0,229,255,0.04);
    }

    .sidebar-search input::placeholder { color: var(--text-muted); }

    .sidebar-search .search-icon {
      position: absolute;
      left: 22px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }

    .sidebar.collapsed .sidebar-search { display: none; }

    /* Chat history */
    .sidebar-section {
      flex: 1;
      overflow-y: auto;
      padding: 4px 8px;
    }

    .section-label {
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      padding: 10px 8px 4px;
      white-space: nowrap;
      overflow: hidden;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .section-label { opacity: 0; }

    .chat-item {
      padding: 9px 10px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all var(--transition-fast);
      position: relative;
      margin-bottom: 2px;
      min-height: 38px;
      overflow: hidden;
    }

    .chat-item:hover { background: var(--bg-hover); }

    .chat-item.active {
      background: linear-gradient(135deg, rgba(0,229,255,0.1), rgba(124,58,237,0.08));
      border: 1px solid rgba(0,229,255,0.15);
    }

    .chat-item.active::before {
      content: '';
      position: absolute;
      left: 0;
      top: 20%;
      height: 60%;
      width: 2px;
      background: var(--accent-cyan);
      border-radius: 0 2px 2px 0;
    }

    .chat-icon {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--bg-hover);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      flex-shrink: 0;
      font-size: 13px;
      transition: all var(--transition-fast);
    }

    .chat-item.active .chat-icon {
      background: rgba(0,229,255,0.15);
      color: var(--accent-cyan);
    }

    .chat-meta {
      flex: 1;
      min-width: 0;
      opacity: 1;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .chat-meta { opacity: 0; width: 0; }

    .chat-title {
      font-size: 12.5px;
      font-weight: 500;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.3;
    }

    .chat-time {
      font-size: 10px;
      color: var(--text-muted);
      margin-top: 2px;
      font-family: var(--font-mono);
    }

    .chat-actions {
      display: none;
      gap: 4px;
    }

    .chat-item:hover .chat-actions { display: flex; }

    .chat-action-btn {
      width: 22px;
      height: 22px;
      border-radius: 5px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      font-size: 11px;
    }

    .chat-action-btn:hover {
      background: rgba(236,72,153,0.15);
      color: var(--accent-pink);
    }

    /* Sidebar footer */
    .sidebar-footer {
      padding: 10px 8px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .sidebar-nav-item {
      padding: 9px 10px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all var(--transition-fast);
      color: var(--text-secondary);
      font-size: 13px;
      min-height: 38px;
      overflow: hidden;
      white-space: nowrap;
    }

    .sidebar-nav-item:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .sidebar-nav-item.danger:hover {
      background: rgba(236,72,153,0.1);
      color: var(--accent-pink);
    }

    .nav-icon {
      width: 28px;
      height: 28px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
    }

    .nav-label {
      opacity: 1;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .nav-label { opacity: 0; }

    /* User profile */
    .user-profile {
      padding: 10px 8px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      border-radius: var(--radius-sm);
      transition: all var(--transition-fast);
      overflow: hidden;
      margin: 0 0 0 0;
    }

    .user-profile:hover { background: var(--bg-hover); }

    .user-avatar {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: linear-gradient(135deg, #7c3aed, #ec4899);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 14px;
      color: #fff;
      flex-shrink: 0;
    }

    .user-info {
      flex: 1;
      min-width: 0;
      opacity: 1;
      transition: opacity var(--transition-med);
    }

    .sidebar.collapsed .user-info { opacity: 0; }

    .user-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .user-plan {
      font-size: 10px;
      color: var(--accent-cyan);
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* ═══════════════════════════════════════════
       MAIN CONTENT AREA
    ═══════════════════════════════════════════ */
    .main {
      flex: 1;
      margin-left: var(--sidebar-width);
      height: 100vh;
      display: flex;
      flex-direction: column;
      transition: margin-left var(--transition-med);
      position: relative;
      z-index: 1;
    }

    .main.sidebar-collapsed {
      margin-left: 60px;
    }

    /* ═══════════════════════════════════════════
       TOPBAR
    ═══════════════════════════════════════════ */
    .topbar {
      height: var(--header-height);
      padding: 0 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(8,14,28,0.8);
      backdrop-filter: blur(20px);
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .topbar-mobile-toggle {
      display: none;
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
    }

    .topbar-mobile-toggle:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .topbar-title {
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 15px;
      color: var(--text-primary);
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .topbar-controls {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: auto;
    }

    .topbar-btn {
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      position: relative;
    }

    .topbar-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
      border-color: var(--border-active);
    }

    .topbar-btn.active {
      background: rgba(0,229,255,0.1);
      color: var(--accent-cyan);
      border-color: rgba(0,229,255,0.3);
    }

    /* Model selector */
    .model-selector {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
      background: var(--bg-card);
      cursor: pointer;
      transition: all var(--transition-fast);
      position: relative;
    }

    .model-selector:hover {
      border-color: var(--border-active);
      background: var(--bg-hover);
    }

    .model-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-green);
      box-shadow: 0 0 8px rgba(16,185,129,0.6);
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.7; transform: scale(0.85); }
    }

    .model-name {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .model-chevron {
      color: var(--text-muted);
      font-size: 10px;
      transition: transform var(--transition-fast);
    }

    .model-selector.open .model-chevron { transform: rotate(180deg); }

    /* Model dropdown */
    .model-dropdown {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      width: 300px;
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 8px;
      z-index: 200;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      display: none;
      backdrop-filter: blur(20px);
    }

    .model-dropdown.open { display: block; animation: dropIn 0.2s ease; }

    @keyframes dropIn {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .model-option {
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 12px;
      transition: all var(--transition-fast);
    }

    .model-option:hover { background: var(--bg-hover); }

    .model-option.selected {
      background: linear-gradient(135deg, rgba(0,229,255,0.1), rgba(124,58,237,0.08));
      border: 1px solid rgba(0,229,255,0.15);
    }

    .model-option-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      flex-shrink: 0;
    }

    .model-option-info { flex: 1; }

    .model-option-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .model-option-desc {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .model-badge {
      font-family: var(--font-mono);
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .badge-new {
      background: rgba(16,185,129,0.15);
      color: var(--accent-green);
      border: 1px solid rgba(16,185,129,0.25);
    }

    .badge-pro {
      background: rgba(124,58,237,0.15);
      color: #a78bfa;
      border: 1px solid rgba(124,58,237,0.25);
    }

    .badge-fast {
      background: rgba(245,158,11,0.15);
      color: var(--accent-yellow);
      border: 1px solid rgba(245,158,11,0.25);
    }

    /* ═══════════════════════════════════════════
       CHAT AREA
    ═══════════════════════════════════════════ */
    .chat-area {
      flex: 1;
      overflow-y: auto;
      padding: 0;
      display: flex;
      flex-direction: column;
      scroll-behavior: smooth;
    }

    /* Welcome screen */
    .welcome-screen {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 24px;
      text-align: center;
      animation: fadeUp 0.6s ease;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .welcome-icon {
      width: 72px;
      height: 72px;
      border-radius: 22px;
      background: var(--gradient-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 28px;
      color: #000;
      margin-bottom: 24px;
      box-shadow: var(--glow-cyan), var(--glow-purple);
      animation: iconFloat 4s ease-in-out infinite alternate;
    }

    @keyframes iconFloat {
      0% { transform: translateY(0px) rotate(-2deg); }
      100% { transform: translateY(-8px) rotate(2deg); }
    }

    .welcome-greeting {
      font-family: var(--font-display);
      font-size: clamp(26px, 4vw, 38px);
      font-weight: 800;
      line-height: 1.1;
      margin-bottom: 10px;
      background: var(--gradient-primary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .welcome-sub {
      font-size: 15px;
      color: var(--text-secondary);
      max-width: 420px;
      line-height: 1.6;
      margin-bottom: 36px;
    }

    /* Suggestion chips */
    .suggestions-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      max-width: 680px;
      width: 100%;
    }

    .suggestion-chip {
      padding: 14px 16px;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      background: var(--bg-card);
      cursor: pointer;
      text-align: left;
      transition: all var(--transition-med);
      display: flex;
      align-items: flex-start;
      gap: 12px;
      position: relative;
      overflow: hidden;
    }

    .suggestion-chip::before {
      content: '';
      position: absolute;
      inset: 0;
      background: var(--gradient-surface);
      opacity: 0;
      transition: opacity var(--transition-med);
    }

    .suggestion-chip:hover::before { opacity: 1; }

    .suggestion-chip:hover {
      border-color: var(--border-active);
      transform: translateY(-2px);
      box-shadow: 0 8px 30px rgba(0,229,255,0.1);
    }

    .chip-icon {
      font-size: 20px;
      line-height: 1;
      flex-shrink: 0;
      margin-top: 1px;
    }

    .chip-content { flex: 1; }

    .chip-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 3px;
      line-height: 1.3;
    }

    .chip-sub {
      font-size: 11px;
      color: var(--text-muted);
      line-height: 1.4;
    }

    /* ═══════════════════════════════════════════
       MESSAGES
    ═══════════════════════════════════════════ */
    .messages-container {
      flex: 1;
      padding: 20px 0;
      display: none;
      flex-direction: column;
      gap: 0;
    }

    .messages-container.visible { display: flex; }

    .message-group {
      padding: 0 24px;
      animation: messageIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes messageIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message-row {
      display: flex;
      gap: 14px;
      max-width: 820px;
      margin: 0 auto;
      padding: 8px 0;
    }

    .message-row.user { flex-direction: row-reverse; }

    .msg-avatar {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 4px;
      font-size: 13px;
      font-weight: 700;
    }

    .msg-avatar.ai {
      background: var(--gradient-primary);
      color: #000;
      font-family: var(--font-display);
      box-shadow: 0 4px 16px rgba(0,229,255,0.2);
    }

    .msg-avatar.user {
      background: linear-gradient(135deg, #7c3aed, #ec4899);
      color: #fff;
      font-family: var(--font-display);
    }

    .msg-content { flex: 1; min-width: 0; }

    .msg-sender {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 5px;
      font-family: var(--font-mono);
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .message-row.user .msg-sender { text-align: right; }

    .msg-bubble {
      padding: 12px 16px;
      border-radius: var(--radius-lg);
      font-size: 14px;
      line-height: 1.65;
      max-width: 100%;
      word-break: break-word;
    }

    .message-row.ai .msg-bubble {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      color: var(--text-primary);
      border-radius: 4px var(--radius-lg) var(--radius-lg) var(--radius-lg);
    }

    .message-row.user .msg-bubble {
      background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(124,58,237,0.12));
      border: 1px solid rgba(0,229,255,0.2);
      color: var(--text-primary);
      border-radius: var(--radius-lg) 4px var(--radius-lg) var(--radius-lg);
      margin-left: auto;
    }

    .msg-bubble p { margin-bottom: 10px; }
    .msg-bubble p:last-child { margin-bottom: 0; }

    .msg-bubble code {
      font-family: var(--font-mono);
      font-size: 12px;
      background: rgba(0,229,255,0.08);
      color: var(--accent-cyan);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(0,229,255,0.12);
    }

    .msg-bubble pre {
      background: #060b18;
      border: 1px solid rgba(0,229,255,0.1);
      border-radius: var(--radius-md);
      padding: 16px;
      overflow-x: auto;
      margin: 10px 0;
      position: relative;
    }

    .msg-bubble pre code {
      background: none;
      border: none;
      padding: 0;
      color: #a8d8ea;
      font-size: 13px;
      line-height: 1.6;
    }

    .code-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
      background: rgba(0,229,255,0.05);
      border-bottom: 1px solid rgba(0,229,255,0.08);
      border-radius: var(--radius-md) var(--radius-md) 0 0;
      margin: -16px -16px 12px;
    }

    .code-lang {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--accent-cyan);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .copy-code-btn {
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid rgba(0,229,255,0.2);
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .copy-code-btn:hover {
      background: rgba(0,229,255,0.1);
      color: var(--accent-cyan);
    }

    .msg-bubble ul, .msg-bubble ol {
      padding-left: 20px;
      margin: 8px 0;
    }

    .msg-bubble li { margin-bottom: 4px; }

    .msg-bubble strong { color: var(--accent-cyan); font-weight: 600; }

    .msg-actions {
      display: flex;
      gap: 4px;
      margin-top: 6px;
      opacity: 0;
      transition: opacity var(--transition-fast);
    }

    .message-row:hover .msg-actions { opacity: 1; }
    .message-row.user .msg-actions { justify-content: flex-end; }

    .msg-action-btn {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-card);
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      font-size: 12px;
    }

    .msg-action-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
      border-color: var(--border-active);
    }

    /* Typing indicator */
    .typing-indicator {
      padding: 0 24px;
      display: none;
    }

    .typing-indicator.visible { display: block; }

    .typing-row {
      display: flex;
      gap: 14px;
      max-width: 820px;
      margin: 0 auto;
      padding: 8px 0;
    }

    .typing-bubble {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 4px var(--radius-lg) var(--radius-lg) var(--radius-lg);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .typing-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--accent-cyan);
      animation: typingBounce 1.2s ease-in-out infinite;
    }

    .typing-dot:nth-child(2) { animation-delay: 0.2s; opacity: 0.7; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; opacity: 0.4; }

    @keyframes typingBounce {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-6px); }
    }

    /* ═══════════════════════════════════════════
       INPUT AREA
    ═══════════════════════════════════════════ */
    .input-area {
      padding: 16px 24px 20px;
      background: rgba(8,14,28,0.6);
      backdrop-filter: blur(20px);
      border-top: 1px solid var(--border-subtle);
    }

    .input-wrapper {
      max-width: 820px;
      margin: 0 auto;
    }

    .input-attachments {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }

    .attachment-chip {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(0,229,255,0.08);
      border: 1px solid rgba(0,229,255,0.15);
      font-size: 11px;
      color: var(--text-secondary);
      font-family: var(--font-mono);
    }

    .attachment-chip .remove-att {
      cursor: pointer;
      color: var(--text-muted);
      transition: color var(--transition-fast);
      font-size: 12px;
    }

    .attachment-chip .remove-att:hover { color: var(--accent-pink); }

    .input-box {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-xl);
      border: 1.5px solid var(--border-subtle);
      background: var(--bg-input);
      transition: all var(--transition-fast);
    }

    .input-box:focus-within {
      border-color: var(--border-active);
      background: rgba(0,229,255,0.03);
      box-shadow: 0 0 0 3px rgba(0,229,255,0.06), var(--glow-cyan);
    }

    .input-tools {
      display: flex;
      align-items: center;
      gap: 4px;
      padding-bottom: 2px;
    }

    .input-tool-btn {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      font-size: 15px;
    }

    .input-tool-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .chat-input {
      flex: 1;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 14px;
      line-height: 1.6;
      resize: none;
      outline: none;
      min-height: 22px;
      max-height: 200px;
      overflow-y: auto;
      padding: 4px 0;
    }

    .chat-input::placeholder { color: var(--text-muted); }

    .send-btn {
      width: 36px;
      height: 36px;
      border-radius: 11px;
      border: none;
      background: var(--gradient-primary);
      color: #000;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      flex-shrink: 0;
      font-size: 16px;
      box-shadow: 0 4px 15px rgba(0,229,255,0.2);
    }

    .send-btn:hover {
      transform: scale(1.08);
      box-shadow: var(--glow-cyan);
    }

    .send-btn:active { transform: scale(0.95); }

    .send-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    /* Input meta */
    .input-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 10px;
      padding: 0 4px;
    }

    .input-tags {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .input-tag {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 20px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      font-size: 11px;
      color: var(--text-muted);
      cursor: pointer;
      transition: all var(--transition-fast);
      font-family: var(--font-mono);
    }

    .input-tag:hover {
      background: var(--bg-hover);
      color: var(--text-secondary);
      border-color: var(--border-active);
    }

    .char-count {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-muted);
    }

    .char-count.warning { color: var(--accent-yellow); }
    .char-count.danger { color: var(--accent-pink); }

    /* ═══════════════════════════════════════════
       SETTINGS MODAL
    ═══════════════════════════════════════════ */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      z-index: 300;
      backdrop-filter: blur(8px);
      align-items: center;
      justify-content: center;
    }

    .modal-overlay.open { display: flex; animation: fadeIn 0.2s ease; }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .modal {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-xl);
      width: 90%;
      max-width: 580px;
      max-height: 80vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 40px 100px rgba(0,0,0,0.6);
    }

    @keyframes modalIn {
      from { opacity: 0; transform: translateY(20px) scale(0.97); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }

    .modal-title {
      font-family: var(--font-display);
      font-size: 17px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .modal-close {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      font-size: 14px;
    }

    .modal-close:hover {
      background: rgba(236,72,153,0.1);
      color: var(--accent-pink);
      border-color: rgba(236,72,153,0.3);
    }

    .modal-tabs {
      display: flex;
      gap: 4px;
      padding: 12px 16px 0;
      border-bottom: 1px solid var(--border-subtle);
      flex-shrink: 0;
    }

    .modal-tab {
      padding: 8px 14px;
      border-radius: var(--radius-sm) var(--radius-sm) 0 0;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      font-family: var(--font-body);
      font-size: 13px;
      font-weight: 500;
      transition: all var(--transition-fast);
      border-bottom: 2px solid transparent;
    }

    .modal-tab:hover { color: var(--text-primary); }

    .modal-tab.active {
      color: var(--accent-cyan);
      border-bottom-color: var(--accent-cyan);
    }

    .modal-body {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px;
    }

    .settings-section {
      margin-bottom: 24px;
    }

    .settings-section-title {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 12px;
    }

    .setting-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      margin-bottom: 8px;
      transition: all var(--transition-fast);
    }

    .setting-item:hover {
      border-color: var(--border-active);
      background: var(--bg-hover);
    }

    .setting-info { flex: 1; }

    .setting-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
    }

    .setting-desc {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Toggle switch */
    .toggle {
      position: relative;
      width: 42px;
      height: 24px;
      flex-shrink: 0;
    }

    .toggle input {
      opacity: 0;
      width: 0;
      height: 0;
      position: absolute;
    }

    .toggle-slider {
      position: absolute;
      inset: 0;
      border-radius: 12px;
      background: var(--bg-hover);
      border: 1px solid var(--border-subtle);
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .toggle-slider::after {
      content: '';
      position: absolute;
      top: 3px;
      left: 3px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--text-muted);
      transition: all var(--transition-fast);
    }

    .toggle input:checked + .toggle-slider {
      background: rgba(0,229,255,0.15);
      border-color: rgba(0,229,255,0.3);
    }

    .toggle input:checked + .toggle-slider::after {
      background: var(--accent-cyan);
      transform: translateX(18px);
      box-shadow: 0 0 8px rgba(0,229,255,0.5);
    }

    /* Theme selector */
    .theme-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .theme-option {
      padding: 10px;
      border-radius: var(--radius-md);
      border: 2px solid var(--border-subtle);
      cursor: pointer;
      transition: all var(--transition-fast);
      text-align: center;
    }

    .theme-option:hover { border-color: rgba(0,229,255,0.3); }

    .theme-option.active {
      border-color: var(--accent-cyan);
      background: rgba(0,229,255,0.05);
    }

    .theme-preview {
      height: 40px;
      border-radius: 6px;
      margin-bottom: 6px;
    }

    .theme-label {
      font-size: 11px;
      color: var(--text-secondary);
      font-weight: 500;
    }

    /* Slider */
    .setting-slider {
      width: 120px;
    }

    .setting-slider input[type="range"] {
      width: 100%;
      -webkit-appearance: none;
      height: 4px;
      border-radius: 2px;
      background: var(--bg-hover);
      outline: none;
    }

    .setting-slider input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent-cyan);
      cursor: pointer;
      box-shadow: 0 0 8px rgba(0,229,255,0.4);
    }

    /* ═══════════════════════════════════════════
       NOTIFICATIONS / TOAST
    ═══════════════════════════════════════════ */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 500;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .toast {
      padding: 12px 16px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-card);
      background: var(--bg-card);
      backdrop-filter: blur(20px);
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      color: var(--text-primary);
      box-shadow: 0 8px 30px rgba(0,0,0,0.3);
      animation: toastIn 0.3s ease, toastOut 0.3s ease 2.7s forwards;
      min-width: 200px;
    }

    @keyframes toastIn {
      from { opacity: 0; transform: translateX(20px); }
      to { opacity: 1; transform: translateX(0); }
    }

    @keyframes toastOut {
      from { opacity: 1; transform: translateX(0); }
      to { opacity: 0; transform: translateX(20px); }
    }

    .toast-icon { font-size: 16px; }

    .toast.success { border-color: rgba(16,185,129,0.3); }
    .toast.error { border-color: rgba(236,72,153,0.3); }
    .toast.info { border-color: rgba(0,229,255,0.3); }

    /* ═══════════════════════════════════════════
       SEARCH MODAL
    ═══════════════════════════════════════════ */
    .search-modal {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 400;
      background: rgba(0,0,0,0.5);
      backdrop-filter: blur(10px);
      align-items: flex-start;
      justify-content: center;
      padding-top: 80px;
    }

    .search-modal.open { display: flex; animation: fadeIn 0.2s ease; }

    .search-box {
      width: 90%;
      max-width: 580px;
      background: var(--bg-card);
      border: 1px solid var(--border-active);
      border-radius: var(--radius-xl);
      overflow: hidden;
      box-shadow: var(--glow-cyan), 0 40px 80px rgba(0,0,0,0.5);
      animation: dropIn 0.25s ease;
    }

    .search-input-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-subtle);
    }

    .search-input-row input {
      flex: 1;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-family: var(--font-body);
      font-size: 15px;
      outline: none;
    }

    .search-input-row input::placeholder { color: var(--text-muted); }

    .search-results {
      padding: 8px;
      max-height: 360px;
      overflow-y: auto;
    }

    .search-result-item {
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: flex;
      gap: 12px;
      align-items: center;
      transition: all var(--transition-fast);
    }

    .search-result-item:hover { background: var(--bg-hover); }

    .search-result-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--bg-hover);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 14px;
    }

    .search-result-text .title {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
    }

    .search-result-text .desc {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .search-kbd {
      font-family: var(--font-mono);
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--bg-hover);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
    }

    .search-footer {
      padding: 10px 16px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      gap: 12px;
    }

    /* ═══════════════════════════════════════════
       EMPTY STATE
    ═══════════════════════════════════════════ */
    .empty-state {
      padding: 40px;
      text-align: center;
      color: var(--text-muted);
    }

    .empty-state svg { margin-bottom: 12px; opacity: 0.3; }

    /* ═══════════════════════════════════════════
       RESPONSIVE
    ═══════════════════════════════════════════ */
    @media (max-width: 768px) {
      .sidebar {
        transform: translateX(-100%);
        width: var(--sidebar-width) !important;
      }

      .sidebar.mobile-open {
        transform: translateX(0);
      }

      .main { margin-left: 0 !important; }

      .topbar-mobile-toggle { display: flex; }

      .suggestions-grid {
        grid-template-columns: 1fr;
      }

      .model-name { display: none; }

      .input-meta { display: none; }
    }

    /* ═══════════════════════════════════════════
       MISC UTILITIES
    ═══════════════════════════════════════════ */
    .divider {
      height: 1px;
      background: var(--border-subtle);
      margin: 8px 0;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      padding: 2px 7px;
      border-radius: 20px;
      font-size: 10px;
      font-weight: 600;
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .badge-cyan {
      background: rgba(0,229,255,0.12);
      color: var(--accent-cyan);
      border: 1px solid rgba(0,229,255,0.2);
    }

    .hidden { display: none !important; }

    /* Gradient border on cards */
    .gradient-border {
      position: relative;
    }

    .gradient-border::before {
      content: '';
      position: absolute;
      inset: -1px;
      border-radius: inherit;
      padding: 1px;
      background: var(--gradient-primary);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
      opacity: 0;
      transition: opacity var(--transition-med);
    }

    .gradient-border:hover::before { opacity: 1; }

    /* Status indicator */
    .status-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(16,185,129,0.08);
      border: 1px solid rgba(16,185,129,0.2);
      font-size: 11px;
      color: var(--accent-green);
      font-family: var(--font-mono);
    }

    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent-green);
      animation: pulse 2s ease-in-out infinite;
    }

    /* Tooltip */
    [data-tooltip] {
      position: relative;
    }

    [data-tooltip]::after {
      content: attr(data-tooltip);
      position: absolute;
      bottom: calc(100% + 8px);
      left: 50%;
      transform: translateX(-50%);
      padding: 5px 10px;
      border-radius: 6px;
      background: #1a2235;
      color: var(--text-primary);
      font-size: 11px;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transition: opacity var(--transition-fast);
      border: 1px solid var(--border-subtle);
      font-family: var(--font-body);
      z-index: 999;
    }

    [data-tooltip]:hover::after { opacity: 1; }

    /* Sidebar token counter */
    .token-usage {
      padding: 10px 12px;
      border-top: 1px solid var(--border-subtle);
    }

    .token-label {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--text-muted);
      font-family: var(--font-mono);
      margin-bottom: 6px;
    }

    .token-bar {
      height: 3px;
      border-radius: 2px;
      background: var(--bg-hover);
      overflow: hidden;
    }

    .token-fill {
      height: 100%;
      border-radius: 2px;
      background: var(--gradient-primary);
      transition: width 0.5s ease;
    }

    .sidebar.collapsed .token-usage { display: none; }

    /* Highlighted text in messages */
    mark {
      background: rgba(0,229,255,0.15);
      color: var(--accent-cyan);
      padding: 1px 3px;
      border-radius: 3px;
    }

    /* Thinking stream animation */
    .thinking-text {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: var(--radius-sm);
      background: rgba(0,229,255,0.04);
      border-left: 2px solid rgba(0,229,255,0.2);
      margin-bottom: 8px;
    }

    .thinking-dots span {
      display: inline-block;
      animation: thinkDot 1.2s ease-in-out infinite;
    }

    .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes thinkDot {
      0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
      40% { opacity: 1; transform: scale(1); }
    }

    /* Custom cursor glow on send btn */
    .send-btn::after {
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 15px;
      background: radial-gradient(circle, rgba(0,229,255,0.2) 0%, transparent 70%);
      opacity: 0;
      transition: opacity var(--transition-fast);
      pointer-events: none;
    }

    .send-btn:hover::after { opacity: 1; }

    /* Message timestamp */
    .msg-time {
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--text-muted);
      padding: 0 2px;
    }

    /* Sidebar pin button */
    .pin-btn {
      opacity: 0;
      transition: opacity var(--transition-fast);
    }

    .chat-item:hover .pin-btn { opacity: 1; }

    /* Notification badge */
    .notif-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent-pink);
      border: 2px solid var(--bg-sidebar);
      font-size: 9px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
    }

    /* Image upload preview */
    .img-preview {
      width: 60px;
      height: 60px;
      border-radius: var(--radius-sm);
      object-fit: cover;
      border: 1px solid var(--border-subtle);
    }

    /* Streaming cursor */
    .streaming-cursor {
      display: inline-block;
      width: 2px;
      height: 1em;
      background: var(--accent-cyan);
      margin-left: 2px;
      vertical-align: text-bottom;
      animation: blink 0.8s step-end infinite;
    }

    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }

    /* Model selector in topbar */
    .topbar-model-wrap {
      position: relative;
    }

    /* Stop btn */
    .stop-btn {
      width: 36px;
      height: 36px;
      border-radius: 11px;
      border: 1.5px solid rgba(236,72,153,0.4);
      background: rgba(236,72,153,0.1);
      color: var(--accent-pink);
      cursor: pointer;
      display: none;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-fast);
      font-size: 14px;
      flex-shrink: 0;
    }

    .stop-btn.visible { display: flex; }
    .stop-btn:hover {
      background: rgba(236,72,153,0.2);
      border-color: var(--accent-pink);
    }

    /* Drag and drop zone */
    .drop-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 999;
      background: rgba(0,229,255,0.05);
      border: 3px dashed rgba(0,229,255,0.3);
      border-radius: var(--radius-xl);
      margin: 16px;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 12px;
      backdrop-filter: blur(4px);
    }

    .drop-overlay.active { display: flex; }

    .drop-overlay h3 {
      font-family: var(--font-display);
      font-size: 22px;
      color: var(--accent-cyan);
    }

    .drop-overlay p { font-size: 14px; color: var(--text-secondary); }
  </style>
</head>
<body>

<!-- Drop overlay -->
<div class="drop-overlay" id="dropOverlay">
  <div style="font-size:48px">📁</div>
  <h3>Faylni tashlang</h3>
  <p>Rasm, PDF yoki matn fayllarini qabul qilamiz</p>
</div>

<!-- Sidebar overlay (mobile) -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="closeMobileSidebar()"></div>

<!-- ═══════════════════════════════ SIDEBAR ═══════════════════════════════ -->
<aside class="sidebar" id="sidebar">

  <!-- Header -->
  <div class="sidebar-header">
    <div class="brand-logo" onclick="goHome()" title="Somo AI">S</div>
    <span class="brand-text">Somo AI</span>
    <button class="collapse-btn" onclick="toggleSidebar()" data-tooltip="Yig'ish">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M9 3L5 7L9 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>

  <!-- New Chat -->
  <button class="new-chat-btn" onclick="startNewChat()">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
      <path d="M7.5 2V13M2 7.5H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <span class="btn-text">Yangi suhbat</span>
  </button>

  <!-- Search -->
  <div class="sidebar-search">
    <svg class="search-icon" width="13" height="13" viewBox="0 0 15 15" fill="none">
      <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M10 10L13 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    <input type="text" placeholder="Suhbatlarni qidirish..." id="chatSearch" oninput="filterChats(this.value)" />
  </div>

  <!-- Chat history -->
  <div class="sidebar-section" id="chatList">
    <div class="section-label">Bugun</div>
    <div class="chat-item active" onclick="loadChat(0)" id="chat-item-0">
      <div class="chat-icon">💬</div>
      <div class="chat-meta">
        <div class="chat-title">Python da Telegram bot yaratish</div>
        <div class="chat-time">Hozir</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(0)" title="O'chirish">🗑</button>
      </div>
    </div>
    <div class="chat-item" onclick="loadChat(1)" id="chat-item-1">
      <div class="chat-icon">🔍</div>
      <div class="chat-meta">
        <div class="chat-title">SQL va NoSQL farqlari</div>
        <div class="chat-time">2 soat oldin</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(1)" title="O'chirish">🗑</button>
      </div>
    </div>
    <div class="chat-item" onclick="loadChat(2)" id="chat-item-2">
      <div class="chat-icon">📄</div>
      <div class="chat-meta">
        <div class="chat-title">Resume yaxshilash bo'yicha maslahat</div>
        <div class="chat-time">5 soat oldin</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(2)" title="O'chirish">🗑</button>
      </div>
    </div>

    <div class="divider"></div>
    <div class="section-label">Kecha</div>

    <div class="chat-item" onclick="loadChat(3)" id="chat-item-3">
      <div class="chat-icon">🇬🇧</div>
      <div class="chat-meta">
        <div class="chat-title">Ingliz tilini o'rganish rejasi</div>
        <div class="chat-time">Kecha 22:15</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(3)" title="O'chirish">🗑</button>
      </div>
    </div>
    <div class="chat-item" onclick="loadChat(4)" id="chat-item-4">
      <div class="chat-icon">⚙️</div>
      <div class="chat-meta">
        <div class="chat-title">FastAPI bilan REST API yaratish</div>
        <div class="chat-time">Kecha 18:40</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(4)" title="O'chirish">🗑</button>
      </div>
    </div>
    <div class="chat-item" onclick="loadChat(5)" id="chat-item-5">
      <div class="chat-icon">🎨</div>
      <div class="chat-meta">
        <div class="chat-title">CSS animatsiyalar haqida</div>
        <div class="chat-time">Kecha 14:20</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(5)" title="O'chirish">🗑</button>
      </div>
    </div>

    <div class="divider"></div>
    <div class="section-label">Bu hafta</div>

    <div class="chat-item" onclick="loadChat(6)" id="chat-item-6">
      <div class="chat-icon">🧠</div>
      <div class="chat-meta">
        <div class="chat-title">Machine Learning asoslari</div>
        <div class="chat-time">Dushanba</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(6)" title="O'chirish">🗑</button>
      </div>
    </div>
    <div class="chat-item" onclick="loadChat(7)" id="chat-item-7">
      <div class="chat-icon">📊</div>
      <div class="chat-meta">
        <div class="chat-title">Data Science loyihalari</div>
        <div class="chat-time">Yakshanba</div>
      </div>
      <div class="chat-actions">
        <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(7)" title="O'chirish">🗑</button>
      </div>
    </div>
  </div>

  <!-- Token usage bar -->
  <div class="token-usage">
    <div class="token-label">
      <span>Token sarfi</span>
      <span id="tokenCountLabel">2,450 / 8,000</span>
    </div>
    <div class="token-bar">
      <div class="token-fill" id="tokenFill" style="width: 31%"></div>
    </div>
  </div>

  <!-- Footer nav -->
  <div class="sidebar-footer">
    <div class="sidebar-nav-item" onclick="openSettings()">
      <div class="nav-icon">⚙️</div>
      <span class="nav-label">Sozlamalar</span>
    </div>
    <div class="sidebar-nav-item" onclick="openHelp()">
      <div class="nav-icon">❓</div>
      <span class="nav-label">Yordam</span>
    </div>
    <div class="sidebar-nav-item" onclick="openKeyboardShortcuts()">
      <div class="nav-icon">⌨️</div>
      <span class="nav-label">Klaviatura yorliqlari</span>
    </div>
    <div class="sidebar-nav-item danger" onclick="clearAllChats()">
      <div class="nav-icon">🗑️</div>
      <span class="nav-label">Hammasini o'chirish</span>
    </div>
  </div>

  <!-- User profile -->
  <div class="user-profile" onclick="openProfile()">
    <div class="user-avatar">S</div>
    <div class="user-info">
      <div class="user-name">Somosab</div>
      <div class="user-plan">Pro rejim</div>
    </div>
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="color: var(--text-muted); flex-shrink:0">
      <path d="M3 5L6 8L9 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
  </div>
</aside>

<!-- ═══════════════════════════════ MAIN ═══════════════════════════════ -->
<main class="main" id="main">

  <!-- Topbar -->
  <header class="topbar">
    <button class="topbar-mobile-toggle" onclick="openMobileSidebar()">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M2 4H14M2 8H14M2 12H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>

    <span class="topbar-title" id="topbarTitle">Yangi suhbat</span>

    <div class="topbar-controls">
      <!-- Status -->
      <div class="status-bar" id="statusBar">
        <div class="status-dot"></div>
        <span>Online</span>
      </div>

      <!-- Model selector -->
      <div class="topbar-model-wrap">
        <div class="model-selector" id="modelSelector" onclick="toggleModelDropdown()">
          <div class="model-dot"></div>
          <span class="model-name" id="currentModelName">llama-3.3-70b</span>
          <span class="model-chevron">▾</span>
        </div>

        <!-- Model dropdown -->
        <div class="model-dropdown" id="modelDropdown">
          <div class="model-option selected" onclick="selectModel('llama-3.3-70b', this)">
            <div class="model-option-icon" style="background: rgba(0,229,255,0.1)">🦙</div>
            <div class="model-option-info">
              <div class="model-option-name">Llama 3.3 70B</div>
              <div class="model-option-desc">Groq · Ultra tez · Kuchli</div>
            </div>
            <span class="model-badge badge-new">Yangi</span>
          </div>
          <div class="model-option" onclick="selectModel('llama-3.1-8b', this)">
            <div class="model-option-icon" style="background: rgba(245,158,11,0.1)">⚡</div>
            <div class="model-option-info">
              <div class="model-option-name">Llama 3.1 8B</div>
              <div class="model-option-desc">Groq · Eng tez · Ixcham</div>
            </div>
            <span class="model-badge badge-fast">Tez</span>
          </div>
          <div class="model-option" onclick="selectModel('mixtral-8x7b', this)">
            <div class="model-option-icon" style="background: rgba(124,58,237,0.1)">🔀</div>
            <div class="model-option-info">
              <div class="model-option-name">Mixtral 8x7B</div>
              <div class="model-option-desc">Groq · Moe arxitektura</div>
            </div>
            <span class="model-badge badge-pro">Pro</span>
          </div>
          <div class="model-option" onclick="selectModel('gemma2-9b', this)">
            <div class="model-option-icon" style="background: rgba(16,185,129,0.1)">💎</div>
            <div class="model-option-info">
              <div class="model-option-name">Gemma 2 9B</div>
              <div class="model-option-desc">Google · Samarali</div>
            </div>
            <span class="model-badge badge-fast">Tez</span>
          </div>
        </div>
      </div>

      <!-- Search btn -->
      <button class="topbar-btn" onclick="openSearchModal()" data-tooltip="Qidirish (Ctrl+K)">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
          <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M10 10L13 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Theme toggle -->
      <button class="topbar-btn" onclick="toggleTheme()" data-tooltip="Mavzu" id="themeBtn">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" id="themeIcon">
          <circle cx="7.5" cy="7.5" r="3" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7.5 1.5V2.5M7.5 12.5V13.5M1.5 7.5H2.5M12.5 7.5H13.5M3.4 3.4L4.1 4.1M10.9 10.9L11.6 11.6M3.4 11.6L4.1 10.9M10.9 4.1L11.6 3.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Export -->
      <button class="topbar-btn" onclick="exportChat()" data-tooltip="Eksport qilish">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M7.5 10V2M7.5 10L5 7.5M7.5 10L10 7.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 12H13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Settings -->
      <button class="topbar-btn" onclick="openSettings()" data-tooltip="Sozlamalar">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
          <circle cx="7.5" cy="7.5" r="2" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7.5 1.5V3M7.5 12V13.5M1.5 7.5H3M12 7.5H13.5M3.4 3.4L4.4 4.4M10.6 10.6L11.6 11.6M3.4 11.6L4.4 10.6M10.6 4.4L11.6 3.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </header>

  <!-- Chat area -->
  <div class="chat-area" id="chatArea">

    <!-- Welcome screen -->
    <div class="welcome-screen" id="welcomeScreen">
      <div class="welcome-icon">S</div>
      <h1 class="welcome-greeting" id="welcomeGreeting">Salom, Somosab! 👋</h1>
      <p class="welcome-sub">
        Savolingizni yozing yoki quyidagi mavzulardan birini tanlang. Men sizga dasturlash, ta'lim va ko'p narsalarda yordam bera olaman.
      </p>

      <div class="suggestions-grid" id="suggestionsGrid">
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('Python da Telegram bot qanday yasaladi? Bosqichma-bosqich tushuntirib ber')">
          <div class="chip-icon">🤖</div>
          <div class="chip-content">
            <div class="chip-title">Python da Telegram bot</div>
            <div class="chip-sub">Bosqichma-bosqich qo'llanma</div>
          </div>
        </div>
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('Ingliz tilini tez o\'rganish uchun samarali usullar qanday?')">
          <div class="chip-icon">🇬🇧</div>
          <div class="chip-content">
            <div class="chip-title">Ingliz tilini o'rgatish</div>
            <div class="chip-sub">Tez o'rganish metodlari</div>
          </div>
        </div>
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('Mening resumemni yaxshilashga yordam ber. Asosiy kamchiliklarni ayt va professional ko\'rinish uchun maslahatlar ber')">
          <div class="chip-icon">📄</div>
          <div class="chip-content">
            <div class="chip-title">Resume yaxshilash</div>
            <div class="chip-sub">Professional ko'rinish uchun</div>
          </div>
        </div>
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('SQL va NoSQL ma\'lumotlar bazalari orasidagi asosiy farqlar nima? Qaysi biri qachon qo\'llaniladi?')">
          <div class="chip-icon">🗄️</div>
          <div class="chip-content">
            <div class="chip-title">SQL va NoSQL farqi</div>
            <div class="chip-sub">Qachon qaysin ishlatish kerak</div>
          </div>
        </div>
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('React.js ni o\'rganish uchun 30 kunlik reja tuzib ber')">
          <div class="chip-icon">⚛️</div>
          <div class="chip-content">
            <div class="chip-title">React.js o'rganish rejasi</div>
            <div class="chip-sub">30 kunlik dastur</div>
          </div>
        </div>
        <div class="suggestion-chip gradient-border" onclick="sendSuggestion('Machine Learning uchun Python kutubxonalari qaysilar? Har biri nima uchun ishlatiladi?')">
          <div class="chip-icon">🧠</div>
          <div class="chip-content">
            <div class="chip-title">Machine Learning</div>
            <div class="chip-sub">Python kutubxonalari</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages container -->
    <div class="messages-container" id="messagesContainer">
      <!-- Messages injected here -->
    </div>

    <!-- Typing indicator -->
    <div class="typing-indicator" id="typingIndicator">
      <div class="typing-row">
        <div class="msg-avatar ai">S</div>
        <div>
          <div class="msg-sender">Somo AI</div>
          <div class="typing-bubble">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- Input area -->
  <div class="input-area">
    <div class="input-wrapper">

      <!-- Attachments preview -->
      <div class="input-attachments" id="attachmentsPreview"></div>

      <div class="input-box" id="inputBox">
        <!-- Left tools -->
        <div class="input-tools">
          <button class="input-tool-btn" onclick="triggerFileUpload()" data-tooltip="Fayl yuklash" title="Fayl yuklash">
            📎
          </button>
          <button class="input-tool-btn" onclick="triggerImageUpload()" data-tooltip="Rasm yuklash" title="Rasm yuklash">
            🖼
          </button>
        </div>

        <!-- Text input -->
        <textarea
          class="chat-input"
          id="chatInput"
          placeholder="Savolingizni yozing... (Shift+Enter yangi qator)"
          rows="1"
          onInput="handleInputChange(this)"
          onKeydown="handleKeyDown(event)"
        ></textarea>

        <!-- Stop & Send -->
        <button class="stop-btn" id="stopBtn" onclick="stopGeneration()" title="To'xtatish">⏹</button>
        <button class="send-btn" id="sendBtn" onclick="sendMessage()" title="Yuborish (Enter)">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M14 8L2 2L5 8L2 14L14 8Z" fill="currentColor"/>
          </svg>
        </button>
      </div>

      <!-- Meta row -->
      <div class="input-meta">
        <div class="input-tags">
          <div class="input-tag" onclick="sendSuggestion('Kodni tushuntir')">
            💡 Kodni tushuntir
          </div>
          <div class="input-tag" onclick="sendSuggestion('Xatoni topib tuzat')">
            🐛 Debug yordam
          </div>
          <div class="input-tag" onclick="sendSuggestion('Tarjima qil')">
            🌐 Tarjima
          </div>
          <div class="input-tag" onclick="sendSuggestion('Qisqacha ayt')">
            ✂️ Qisqacha
          </div>
        </div>
        <div class="char-count" id="charCount">0 / 4000</div>
      </div>
    </div>
  </div>
</main>

<!-- Hidden file inputs -->
<input type="file" id="fileInput" accept=".pdf,.txt,.md,.csv,.json,.py,.js,.html,.css" hidden onchange="handleFileSelect(this)" />
<input type="file" id="imageInput" accept="image/*" hidden onchange="handleImageSelect(this)" />

<!-- ═══════════════════════════════ SETTINGS MODAL ═══════════════════════════════ -->
<div class="modal-overlay" id="settingsModal" onclick="closeModalOnOverlay(event, 'settingsModal')">
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title">⚙️ Sozlamalar</span>
      <button class="modal-close" onclick="closeModal('settingsModal')">✕</button>
    </div>
    <div class="modal-tabs">
      <button class="modal-tab active" onclick="switchTab('general', this)">Umumiy</button>
      <button class="modal-tab" onclick="switchTab('appearance', this)">Ko'rinish</button>
      <button class="modal-tab" onclick="switchTab('model', this)">Model</button>
      <button class="modal-tab" onclick="switchTab('account', this)">Hisob</button>
    </div>
    <div class="modal-body">

      <!-- General tab -->
      <div id="tab-general">
        <div class="settings-section">
          <div class="settings-section-title">Xulq-atvor</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Enter yuborish</div>
              <div class="setting-desc">Enter bosilganda xabarni yuboradi (Shift+Enter yangi qator)</div>
            </div>
            <label class="toggle">
              <input type="checkbox" checked id="enterToSend" onchange="updateSetting('enterToSend', this.checked)" />
              <div class="toggle-slider"></div>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Suhbat tarixini saqlash</div>
              <div class="setting-desc">Suhbatlar qurilmangizda saqlanadi</div>
            </div>
            <label class="toggle">
              <input type="checkbox" checked id="saveHistory" onchange="updateSetting('saveHistory', this.checked)" />
              <div class="toggle-slider"></div>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Yozish ko'rsatgichi</div>
              <div class="setting-desc">AI yozayotganda animatsiya ko'rsatish</div>
            </div>
            <label class="toggle">
              <input type="checkbox" checked id="showTyping" onchange="updateSetting('showTyping', this.checked)" />
              <div class="toggle-slider"></div>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Ovozli bildirishnomalar</div>
              <div class="setting-desc">Xabar kelganda tovush chiqarish</div>
            </div>
            <label class="toggle">
              <input type="checkbox" id="soundNotif" onchange="updateSetting('soundNotif', this.checked)" />
              <div class="toggle-slider"></div>
            </label>
          </div>
        </div>

        <div class="settings-section">
          <div class="settings-section-title">Tillar</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Interfeys tili</div>
              <div class="setting-desc">Dastur tili</div>
            </div>
            <select style="background: var(--bg-hover); border: 1px solid var(--border-subtle); color: var(--text-primary); padding: 6px 10px; border-radius: 8px; font-size: 12px; outline: none; cursor: pointer;">
              <option value="uz">O'zbek</option>
              <option value="ru">Русский</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Appearance tab -->
      <div id="tab-appearance" class="hidden">
        <div class="settings-section">
          <div class="settings-section-title">Mavzu</div>
          <div class="theme-grid">
            <div class="theme-option active" id="theme-dark" onclick="applyTheme('dark')">
              <div class="theme-preview" style="background: linear-gradient(135deg, #050810, #0c1120)"></div>
              <div class="theme-label">Qorong'u</div>
            </div>
            <div class="theme-option" id="theme-light" onclick="applyTheme('light')">
              <div class="theme-preview" style="background: linear-gradient(135deg, #f5f7fa, #e8eef8)"></div>
              <div class="theme-label">Yorug'</div>
            </div>
            <div class="theme-option" id="theme-midnight" onclick="applyTheme('midnight')">
              <div class="theme-preview" style="background: linear-gradient(135deg, #000000, #1a0030)"></div>
              <div class="theme-label">Yarim tun</div>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <div class="settings-section-title">Shrift</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Shrift o'lchami</div>
              <div class="setting-desc">Xabarlar shrift o'lchami</div>
            </div>
            <div class="setting-slider">
              <input type="range" min="12" max="20" value="14" id="fontSize" oninput="updateFontSize(this.value)" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Kod shrifti</div>
              <div class="setting-desc">Kod bloklari uchun monospace shrift</div>
            </div>
            <label class="toggle">
              <input type="checkbox" checked />
              <div class="toggle-slider"></div>
            </label>
          </div>
        </div>

        <div class="settings-section">
          <div class="settings-section-title">Animatsiyalar</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Harakat animatsiyalari</div>
              <div class="setting-desc">UI elementlarida silliq o'tishlar</div>
            </div>
            <label class="toggle">
              <input type="checkbox" checked id="motionAnim" onchange="toggleAnimations(this.checked)" />
              <div class="toggle-slider"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Model tab -->
      <div id="tab-model" class="hidden">
        <div class="settings-section">
          <div class="settings-section-title">Model sozlamalari</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Temperatura</div>
              <div class="setting-desc">Yuqori = ijodiy, past = aniqroq (0-2)</div>
            </div>
            <div class="setting-slider">
              <input type="range" min="0" max="20" value="7" id="tempSlider" oninput="updateTemp(this.value)" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Max tokenlar</div>
              <div class="setting-desc">Javob uzunligi chegarasi</div>
            </div>
            <div class="setting-slider">
              <input type="range" min="256" max="8192" step="256" value="2048" id="maxTokens" oninput="updateMaxTokens(this.value)" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Tizim xabari</div>
              <div class="setting-desc">AI uchun maxsus ko'rsatma</div>
            </div>
          </div>
          <textarea
            style="width:100%; padding:10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:var(--radius-md); color:var(--text-primary); font-family:var(--font-mono); font-size:12px; resize:vertical; outline:none; min-height:80px;"
            id="systemPrompt"
            placeholder="Masalan: Sen O'zbek tilida javob beradigan yordamchisan..."
          >Sen Somo AI - O'zbekistondagi eng aqlli AI yordamchisan. Foydalanuvchilarga dasturlash, ta'lim va boshqa sohalarda yordam berasan.</textarea>
        </div>
      </div>

      <!-- Account tab -->
      <div id="tab-account" class="hidden">
        <div class="settings-section">
          <div class="settings-section-title">Profil</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Ism</div>
              <div class="setting-desc">Sizning ismingiz</div>
            </div>
            <input
              type="text"
              value="Somosab"
              id="userName"
              style="background:var(--bg-hover); border:1px solid var(--border-subtle); color:var(--text-primary); padding:6px 10px; border-radius:8px; font-size:12px; outline:none; width:140px;"
            />
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Reja</div>
              <div class="setting-desc">Joriy obuna turi</div>
            </div>
            <span class="badge badge-cyan">Pro</span>
          </div>
        </div>

        <div class="settings-section">
          <div class="settings-section-title">API</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Groq API kaliti</div>
              <div class="setting-desc">Maxfiy saqlang</div>
            </div>
          </div>
          <input
            type="password"
            placeholder="gsk-xxxxxxxxxxxxxxxxxxxxxxxx"
            id="apiKeyInput"
            style="width:100%; background:var(--bg-input); border:1px solid var(--border-subtle); color:var(--text-primary); padding:10px 12px; border-radius:var(--radius-md); font-family:var(--font-mono); font-size:12px; outline:none; margin-top:8px;"
          />
          <button
            onclick="saveApiKey()"
            style="margin-top:8px; padding:8px 16px; background:var(--gradient-primary); border:none; border-radius:var(--radius-sm); color:#000; font-weight:600; font-size:12px; cursor:pointer;"
          >
            Saqlash
          </button>
        </div>

        <div class="settings-section">
          <div class="settings-section-title">Ma'lumotlar</div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-name">Barcha suhbatlarni o'chirish</div>
              <div class="setting-desc">Bu amalni qaytarib bo'lmaydi</div>
            </div>
            <button
              onclick="clearAllChats()"
              style="padding:6px 12px; background:rgba(236,72,153,0.1); border:1px solid rgba(236,72,153,0.3); color:var(--accent-pink); border-radius:8px; font-size:12px; cursor:pointer; font-weight:500;"
            >
              O'chirish
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- ═══════════════════════════════ SEARCH MODAL ═══════════════════════════════ -->
<div class="search-modal" id="searchModal" onclick="closeModalOnOverlay(event, 'searchModal')">
  <div class="search-box">
    <div class="search-input-row">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="color:var(--text-muted); flex-shrink:0">
        <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M11 11L14 14" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      <input type="text" placeholder="Suhbatlar va amallarni qidirish..." id="globalSearch" oninput="handleGlobalSearch(this.value)" autofocus />
      <span class="search-kbd">ESC</span>
    </div>
    <div class="search-results" id="searchResults">
      <div style="padding: 12px 8px; font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.1em;">
        Oxirgi suhbatlar
      </div>
      <div class="search-result-item" onclick="loadChatFromSearch(0)">
        <div class="search-result-icon">🤖</div>
        <div class="search-result-text">
          <div class="title">Python da Telegram bot yaratish</div>
          <div class="desc">Bugun · 12 xabar</div>
        </div>
      </div>
      <div class="search-result-item" onclick="loadChatFromSearch(1)">
        <div class="search-result-icon">🗄️</div>
        <div class="search-result-text">
          <div class="title">SQL va NoSQL farqlari</div>
          <div class="desc">Bugun · 8 xabar</div>
        </div>
      </div>
      <div class="search-result-item" onclick="loadChatFromSearch(2)">
        <div class="search-result-icon">📄</div>
        <div class="search-result-text">
          <div class="title">Resume yaxshilash bo'yicha maslahat</div>
          <div class="desc">Bugun · 6 xabar</div>
        </div>
      </div>
      <div class="search-result-item" onclick="loadChatFromSearch(3)">
        <div class="search-result-icon">🇬🇧</div>
        <div class="search-result-text">
          <div class="title">Ingliz tilini o'rganish rejasi</div>
          <div class="desc">Kecha · 15 xabar</div>
        </div>
      </div>

      <div style="padding: 12px 8px 4px; font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.1em;">
        Tezkor amallar
      </div>
      <div class="search-result-item" onclick="startNewChat(); closeModal('searchModal')">
        <div class="search-result-icon">✨</div>
        <div class="search-result-text">
          <div class="title">Yangi suhbat boshlash</div>
          <div class="desc">Yangi bo'sh suhbat</div>
        </div>
      </div>
      <div class="search-result-item" onclick="openSettings(); closeModal('searchModal')">
        <div class="search-result-icon">⚙️</div>
        <div class="search-result-text">
          <div class="title">Sozlamalarni ochish</div>
          <div class="desc">Imtiyozlar va konfiguratsiya</div>
        </div>
      </div>
      <div class="search-result-item" onclick="exportChat(); closeModal('searchModal')">
        <div class="search-result-icon">💾</div>
        <div class="search-result-text">
          <div class="title">Suhbatni eksport qilish</div>
          <div class="desc">JSON yoki Markdown formatida</div>
        </div>
      </div>
    </div>
    <div class="search-footer">
      <span class="search-kbd">↑↓</span> <span style="font-size:11px; color:var(--text-muted)">Tanlash</span>
      <span class="search-kbd">↵</span> <span style="font-size:11px; color:var(--text-muted)">Ochish</span>
      <span class="search-kbd">ESC</span> <span style="font-size:11px; color:var(--text-muted)">Yopish</span>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════ KEYBOARD SHORTCUTS MODAL ═══════════════════════════════ -->
<div class="modal-overlay" id="shortcutsModal" onclick="closeModalOnOverlay(event, 'shortcutsModal')">
  <div class="modal" style="max-width: 480px;">
    <div class="modal-header">
      <span class="modal-title">⌨️ Klaviatura yorliqlari</span>
      <button class="modal-close" onclick="closeModal('shortcutsModal')">✕</button>
    </div>
    <div class="modal-body">
      <div style="display: flex; flex-direction: column; gap: 6px;">
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Yangi suhbat</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">N</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Qidirish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">K</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Xabar yuborish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Enter</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Yangi qator</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Shift</span><span class="search-kbd">Enter</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Sidebarni yig'ish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">B</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Mavzu almashtirish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">T</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Sozlamalar</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">,</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Generatsiyani to'xtatish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Esc</span></div>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px 12px; border-radius:8px; background:var(--bg-surface);">
          <span style="font-size:13px; color:var(--text-secondary)">Eksport qilish</span>
          <div style="display:flex; gap:4px;"><span class="search-kbd">Ctrl</span><span class="search-kbd">E</span></div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Toast container -->
<div class="toast-container" id="toastContainer"></div>

<!-- ═══════════════════════════════ JAVASCRIPT ═══════════════════════════════ */
<script>
/* ═══════════════════════════════════════════
   STATE
═══════════════════════════════════════════ */
const state = {
  sidebarCollapsed: false,
  theme: 'dark',
  currentChatId: null,
  isGenerating: false,
  messages: [],
  settings: {
    enterToSend: true,
    saveHistory: true,
    showTyping: true,
    soundNotif: false,
    fontSize: 14,
    temperature: 0.7,
    maxTokens: 2048,
    systemPrompt: 'Sen Somo AI - O\'zbekistondagi eng aqlli AI yordamchisan.',
    model: 'llama-3.3-70b'
  },
  tokenCount: 2450,
  totalTokens: 8000,
  chatHistory: [
    { id: 0, title: 'Python da Telegram bot yaratish', time: 'Hozir', messages: [] },
    { id: 1, title: 'SQL va NoSQL farqlari', time: '2 soat oldin', messages: [] },
    { id: 2, title: 'Resume yaxshilash bo\'yicha maslahat', time: '5 soat oldin', messages: [] },
    { id: 3, title: 'Ingliz tilini o\'rganish rejasi', time: 'Kecha 22:15', messages: [] },
    { id: 4, title: 'FastAPI bilan REST API yaratish', time: 'Kecha 18:40', messages: [] },
    { id: 5, title: 'CSS animatsiyalar haqida', time: 'Kecha 14:20', messages: [] },
    { id: 6, title: 'Machine Learning asoslari', time: 'Dushanba', messages: [] },
    { id: 7, title: 'Data Science loyihalari', time: 'Yakshanba', messages: [] },
  ],
  abortController: null
};

/* ═══════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════ */
function toggleSidebar() {
  state.sidebarCollapsed = !state.sidebarCollapsed;
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('main');
  sidebar.classList.toggle('collapsed', state.sidebarCollapsed);
  main.classList.toggle('sidebar-collapsed', state.sidebarCollapsed);
}

function openMobileSidebar() {
  document.getElementById('sidebar').classList.add('mobile-open');
  document.getElementById('sidebarOverlay').classList.add('active');
}

function closeMobileSidebar() {
  document.getElementById('sidebar').classList.remove('mobile-open');
  document.getElementById('sidebarOverlay').classList.remove('active');
}

/* ═══════════════════════════════════════════
   CHAT MANAGEMENT
═══════════════════════════════════════════ */
function startNewChat() {
  state.currentChatId = null;
  state.messages = [];
  document.getElementById('topbarTitle').textContent = 'Yangi suhbat';
  document.getElementById('welcomeScreen').style.display = 'flex';
  document.getElementById('messagesContainer').classList.remove('visible');
  document.getElementById('messagesContainer').innerHTML = '';
  document.getElementById('typingIndicator').classList.remove('visible');
  document.getElementById('chatInput').value = '';
  updateCharCount(0);

  // Deselect all chat items
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  closeMobileSidebar();
  showToast('✨', 'Yangi suhbat boshlandi', 'info');
}

function loadChat(id) {
  state.currentChatId = id;
  const chat = state.chatHistory.find(c => c.id === id);
  if (!chat) return;

  document.getElementById('topbarTitle').textContent = chat.title;
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  const item = document.getElementById('chat-item-' + id);
  if (item) item.classList.add('active');

  // Show welcome or messages
  document.getElementById('welcomeScreen').style.display = 'none';
  const container = document.getElementById('messagesContainer');
  container.classList.add('visible');
  container.innerHTML = '';

  if (chat.messages && chat.messages.length > 0) {
    chat.messages.forEach(msg => renderMessage(msg.role, msg.content, false));
  } else {
    // Demo messages for first chat
    if (id === 0) {
      renderMessage('user', 'Python da Telegram bot qanday yasaladi?', false);
      renderMessage('ai', demoResponse, false);
    } else {
      container.innerHTML = '<div class="empty-state"><div style="font-size:48px;margin-bottom:12px">💬</div><p style="color:var(--text-muted);font-size:14px">Bu suhbat bo\'sh</p></div>';
    }
  }

  closeMobileSidebar();
  scrollToBottom(false);
}

function deleteChat(id) {
  const idx = state.chatHistory.findIndex(c => c.id === id);
  if (idx !== -1) {
    state.chatHistory.splice(idx, 1);
    const item = document.getElementById('chat-item-' + id);
    if (item) {
      item.style.height = item.offsetHeight + 'px';
      item.style.overflow = 'hidden';
      item.style.transition = 'all 0.3s ease';
      setTimeout(() => { item.style.height = '0'; item.style.padding = '0'; item.style.margin = '0'; item.style.opacity = '0'; }, 10);
      setTimeout(() => item.remove(), 300);
    }
    if (state.currentChatId === id) startNewChat();
    showToast('🗑️', 'Suhbat o\'chirildi', 'info');
  }
}

function clearAllChats() {
  if (confirm('Barcha suhbatlarni o\'chirishni xohlaysizmi?')) {
    state.chatHistory = [];
    document.getElementById('chatList').innerHTML = '<div class="empty-state"><div style="font-size:32px">💭</div><p>Hech qanday suhbat yo\'q</p></div>';
    startNewChat();
    showToast('🗑️', 'Barcha suhbatlar o\'chirildi', 'info');
    closeModal('settingsModal');
  }
}

function filterChats(query) {
  const items = document.querySelectorAll('.chat-item');
  items.forEach(item => {
    const title = item.querySelector('.chat-title');
    if (title) {
      const match = !query || title.textContent.toLowerCase().includes(query.toLowerCase());
      item.style.display = match ? 'flex' : 'none';
    }
  });
}

const demoResponse = `Albatta! Python va **python-telegram-bot** kutubxonasi yordamida oddiy Telegram bot yaratamiz.

**1. O'rnatish:**

\`\`\`bash
pip install python-telegram-bot
\`\`\`

**2. Bot token olish:**

@BotFather ga boring va \`/newbot\` buyrug'ini yuboring.

**3. Asosiy kod:**

\`\`\`python
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men Somo botman 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Siz yozdingiz: {user_text}")

def main():
    app = Application.builder().token("YOUR_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
\`\`\`

**4. Ishga tushirish:**

\`\`\`bash
python bot.py
\`\`\`

Bu asosiy bot! Keyingi qadamda **inline keyboard**, **database** va **webhook** qo'shishimiz mumkin. Davom etamizmi? 🚀`;

/* ═══════════════════════════════════════════
   MESSAGE RENDERING
═══════════════════════════════════════════ */
function renderMessage(role, content, animate = true) {
  const container = document.getElementById('messagesContainer');
  container.classList.add('visible');
  document.getElementById('welcomeScreen').style.display = 'none';

  const msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  const isUser = role === 'user';
  const time = new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });

  const html = `
    <div class="message-group" id="${msgId}">
      <div class="message-row ${isUser ? 'user' : 'ai'}">
        <div class="msg-avatar ${isUser ? 'user' : 'ai'}">${isUser ? 'S' : 'AI'}</div>
        <div class="msg-content">
          <div class="msg-sender">${isUser ? 'Siz' : 'Somo AI'} <span class="msg-time">${time}</span></div>
          <div class="msg-bubble" id="bubble-${msgId}">${formatMessage(content)}</div>
          <div class="msg-actions">
            ${!isUser ? `
              <button class="msg-action-btn" onclick="copyMessage('bubble-${msgId}')" title="Nusxalash">📋</button>
              <button class="msg-action-btn" onclick="regenerateMessage()" title="Qayta yaratish">🔄</button>
              <button class="msg-action-btn" onclick="likeMessage('${msgId}', true)" title="Yoqdi">👍</button>
              <button class="msg-action-btn" onclick="likeMessage('${msgId}', false)" title="Yoqmadi">👎</button>
            ` : `
              <button class="msg-action-btn" onclick="copyMessage('bubble-${msgId}')" title="Nusxalash">📋</button>
              <button class="msg-action-btn" onclick="editMessage('bubble-${msgId}')" title="Tahrirlash">✏️</button>
            `}
          </div>
        </div>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', html);

  // Add copy buttons to code blocks
  const newEl = document.getElementById(msgId);
  if (newEl) {
    newEl.querySelectorAll('pre').forEach(pre => {
      const btn = pre.querySelector('.copy-code-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          const code = pre.querySelector('code');
          if (code) copyText(code.textContent);
        });
      }
    });
  }

  if (animate) scrollToBottom(true);
  return msgId;
}

function formatMessage(content) {
  // Parse markdown-ish content
  let html = content
    // Code blocks
    .replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
      const language = lang || 'code';
      return `<pre><div class="code-header"><span class="code-lang">${language}</span><button class="copy-code-btn">Nusxalash</button></div><code>${escapeHtml(code.trim())}</code></pre>`;
    })
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.+)$/gm, '<h4 style="font-family:var(--font-display);font-size:14px;font-weight:700;color:var(--text-primary);margin:10px 0 6px">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 style="font-family:var(--font-display);font-size:16px;font-weight:700;color:var(--text-primary);margin:12px 0 6px">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 style="font-family:var(--font-display);font-size:18px;font-weight:800;color:var(--text-primary);margin:12px 0 8px">$1</h2>')
    // Lists
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    // Newlines to paragraphs
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  // Wrap in paragraph if no block elements
  if (!html.includes('<pre>') && !html.includes('<h') && !html.includes('<li>')) {
    html = '<p>' + html + '</p>';
  }

  // Wrap lists
  html = html.replace(/(<li>.*<\/li>\s*)+/g, match => `<ul>${match}</ul>`);

  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* ═══════════════════════════════════════════
   SEND MESSAGE
═══════════════════════════════════════════ */
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text || state.isGenerating) return;

  // Clear input
  input.value = '';
  input.style.height = 'auto';
  updateCharCount(0);

  // Add to history if new chat
  if (state.currentChatId === null) {
    const newId = Date.now();
    const shortTitle = text.length > 40 ? text.substring(0, 40) + '...' : text;
    state.currentChatId = newId;
    state.chatHistory.unshift({ id: newId, title: shortTitle, time: 'Hozir', messages: [] });
    addChatToSidebar(newId, shortTitle);
    document.getElementById('topbarTitle').textContent = shortTitle;
  }

  // Save user message
  state.messages.push({ role: 'user', content: text });
  renderMessage('user', text);

  // Show typing
  state.isGenerating = true;
  toggleGenerationUI(true);
  showTyping();

  // Simulate AI response
  await simulateAIResponse(text);
}

async function simulateAIResponse(userText) {
  await delay(800 + Math.random() * 600);
  hideTyping();

  const responses = getAIResponse(userText);
  const msgId = renderMessage('ai', '');
  const bubble = document.getElementById('bubble-' + msgId);

  // Stream the response
  await streamText(bubble, responses);

  state.messages.push({ role: 'ai', content: responses });
  state.isGenerating = false;
  toggleGenerationUI(false);
  updateTokenCount(Math.floor(responses.length / 4));
  scrollToBottom(true);
}

async function streamText(element, text) {
  element.innerHTML = '';
  const words = text.split(' ');
  let current = '';
  const cursor = document.createElement('span');
  cursor.className = 'streaming-cursor';

  for (let i = 0; i < words.length; i++) {
    current += (i > 0 ? ' ' : '') + words[i];
    element.innerHTML = formatMessage(current);
    element.appendChild(cursor);
    scrollToBottom(false);
    await delay(18 + Math.random() * 15);
    if (!state.isGenerating && i < words.length - 1) break;
  }

  cursor.remove();
  element.innerHTML = formatMessage(current);
}

function getAIResponse(text) {
  const lower = text.toLowerCase();

  if (lower.includes('python') || lower.includes('bot') || lower.includes('telegram')) {
    return demoResponse;
  }
  if (lower.includes('sql') || lower.includes('nosql')) {
    return `**SQL va NoSQL farqlari** juda muhim mavzu!

**SQL (Relational) bazalar:**
- **Tuzilgan ma'lumotlar** uchun ideal
- **ACID** transaktsiyalar
- Qat'iy schema (jadval tuzilmasi)
- Misol: PostgreSQL, MySQL, SQLite

**NoSQL bazalar:**
- **Tuzilmagan/yarim tuzilgan** ma'lumotlar
- Yuqori **scalability**
- Moslashuvchan schema
- Misol: MongoDB, Redis, Cassandra

**Qachon SQL ishlatish:**
- Moliyaviy tizimlar
- Murakkab JOIN so'rovlar
- Ma'lumotlar yaxlitligi muhim bo'lganda

**Qachon NoSQL ishlatish:**
- Real-time ilovalar
- Katta hajmli ma'lumotlar (Big Data)
- Tezkor prototip yaratish

Qaysi biri haqida batafsil bilishni xohlaysiz? 🎯`;
  }
  if (lower.includes('resume') || lower.includes('cv')) {
    return `**Resumeni yaxshilash bo'yicha asosiy maslahatlar:**

**Tuzilma:**
- **Ism va kontakt** - eng yuqorida, ravshan
- **Qisqacha profil** - 2-3 jumlada o'zingizni tanishtiring
- **Ko'nikmalar** - texnik va soft skilllar
- **Tajriba** - oxirgi ish joyidan boshlab
- **Ta'lim** - darajasi bilan

**Keng tarqalgan xatolar:**
- Foto qo'ymaslik yoki professional bo'lmagan foto
- Haddan ziyod ma'lumot (2 sahifadan oshmasin)
- Umumiy iboralar: "hardworking", "team player"

**Yaxshilash usullari:**
- Har bir ish uchun **natijalar** yozing (% yoki raqamlar bilan)
- **ATS** tizimiga mos kalit so'zlar kiriting
- **PDF** formatida saqlang

Resumingizni paste qilsangiz, aniqroq maslahat bera olaman! 📄`;
  }
  if (lower.includes('ingliz') || lower.includes('english')) {
    return `**Ingliz tilini tez o'rganish metodlari:**

**1. Kundalik amaliyot (30 daqiqa)**
- 10 daqiqa - yangi so'zlar (Anki ilovasi)
- 10 daqiqa - audio/podcast
- 10 daqiqa - yozish

**2. Eng samarali usullar:**
- **Immersion** - ingliz kontentini iste'mol qiling (Netflix, YouTube)
- **Output** - gapiring va yozing, nafaqat o'qing
- **Spaced repetition** - Anki flashcards

**3. Resurslar (bepul):**
- Duolingo - grammatika asoslari
- BBC Learning English - podcast + maqolalar
- italki - ona tillilar bilan amaliyot

**4. 30 kunlik reja:**
- Hafta 1-2: A1 grammatika + 200 so'z
- Hafta 3-4: Dialog amaliyoti + filmlar

Sizning joriy darajangiz qanday? A1, A2, B1? 🎯`;
  }
  if (lower.includes('react') || lower.includes('javascript') || lower.includes('js')) {
    return `**React.js o'rganish uchun 30 kunlik reja:**

**1-10 kun: Asoslar**
\`\`\`
- JavaScript asoslari (ES6+): arrow functions, destructuring
- React nima? Virtual DOM tushunchasi
- JSX sintaksisi
- Komponentlar: functional va class
\`\`\`

**11-20 kun: Hooks va State**
\`\`\`javascript
// useState
const [count, setCount] = useState(0);

// useEffect
useEffect(() => {
  document.title = \`Count: \${count}\`;
}, [count]);
\`\`\`

**21-30 kun: Amaliy loyiha**
- React Router - sahifalar
- API bilan ishlash (fetch/axios)
- Context API yoki Redux
- Bitta to'liq loyiha yarating!

**Resurslar:**
- react.dev (official) - eng zo'r
- Scrimba - interaktiv kurslar

Boshlashga tayyormisiz? 🚀`;
  }

  // Generic response
  const genericResponses = [
    `Bu juda yaxshi savol! Keling, batafsil ko'rib chiqamiz.\n\nSizning savolingiz haqida ko'proq ma'lumot bersangiz, aniqroq va foydali javob bera olaman. Qaysi jihati sizni ko'proq qiziqtiradi?\n\n- Nazariy tushuntirish\n- Amaliy misol\n- Kod namunasi\n- Boshqa narsa\n\nSizga qanday yordam bera olsam? 💡`,
    `Ajoyib savol! Bu mavzu haqida ko'p narsalar gapirish mumkin.\n\nQisqacha aytganda, bu soha juda keng. Siz qaysi qismidan boshlashni xohlaysiz? Boshlang'ich darajadan boshlaymizmi yoki allaqachon asoslarni bilasizmi?\n\nHar qanday savolingiz bo'lsa, bemalol so'rang! 🎯`,
  ];

  return genericResponses[Math.floor(Math.random() * genericResponses.length)];
}

function sendSuggestion(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

/* ═══════════════════════════════════════════
   INPUT HANDLING
═══════════════════════════════════════════ */
function handleInputChange(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  updateCharCount(el.value.length);
}

function handleKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey && state.settings.enterToSend) {
    event.preventDefault();
    sendMessage();
  }
}

function updateCharCount(count) {
  const el = document.getElementById('charCount');
  el.textContent = count + ' / 4000';
  el.className = 'char-count' + (count > 3500 ? ' danger' : count > 3000 ? ' warning' : '');
}

/* ═══════════════════════════════════════════
   UI STATE HELPERS
═══════════════════════════════════════════ */
function showTyping() {
  if (!state.settings.showTyping) return;
  document.getElementById('typingIndicator').classList.add('visible');
  scrollToBottom(true);
}

function hideTyping() {
  document.getElementById('typingIndicator').classList.remove('visible');
}

function toggleGenerationUI(isGenerating) {
  const sendBtn = document.getElementById('sendBtn');
  const stopBtn = document.getElementById('stopBtn');
  sendBtn.disabled = isGenerating;
  stopBtn.classList.toggle('visible', isGenerating);
}

function stopGeneration() {
  state.isGenerating = false;
  hideTyping();
  toggleGenerationUI(false);
  showToast('⏹', 'Generatsiya to\'xtatildi', 'info');
}

function scrollToBottom(smooth = true) {
  const chatArea = document.getElementById('chatArea');
  if (smooth) {
    chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
  } else {
    chatArea.scrollTop = chatArea.scrollHeight;
  }
}

function updateTokenCount(add) {
  state.tokenCount = Math.min(state.tokenCount + add, state.totalTokens);
  document.getElementById('tokenCountLabel').textContent =
    state.tokenCount.toLocaleString() + ' / ' + state.totalTokens.toLocaleString();
  const pct = (state.tokenCount / state.totalTokens) * 100;
  document.getElementById('tokenFill').style.width = pct + '%';
}

function addChatToSidebar(id, title) {
  const chatList = document.getElementById('chatList');
  const label = chatList.querySelector('.section-label');
  const item = document.createElement('div');
  item.className = 'chat-item active';
  item.id = 'chat-item-' + id;
  item.innerHTML = `
    <div class="chat-icon">💬</div>
    <div class="chat-meta">
      <div class="chat-title">${title}</div>
      <div class="chat-time">Hozir</div>
    </div>
    <div class="chat-actions">
      <button class="chat-action-btn" onclick="event.stopPropagation(); deleteChat(${id})" title="O'chirish">🗑</button>
    </div>
  `;
  item.onclick = () => loadChat(id);
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  chatList.insertBefore(item, label ? label.nextSibling : chatList.firstChild);
}

/* ═══════════════════════════════════════════
   MESSAGE ACTIONS
═══════════════════════════════════════════ */
function copyMessage(bubbleId) {
  const bubble = document.getElementById(bubbleId);
  if (bubble) {
    copyText(bubble.textContent);
    showToast('📋', 'Nusxalandi!', 'success');
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  });
}

function likeMessage(id, liked) {
  showToast(liked ? '👍' : '👎', liked ? 'Fikr uchun rahmat!' : 'Kuzatib olamiz', 'info');
}

function regenerateMessage() {
  if (state.messages.length < 1) return;
  const lastUser = [...state.messages].reverse().find(m => m.role === 'user');
  if (lastUser) {
    // Remove last AI message from DOM
    const container = document.getElementById('messagesContainer');
    const groups = container.querySelectorAll('.message-group');
    if (groups.length > 0) {
      const lastGroup = groups[groups.length - 1];
      if (lastGroup.querySelector('.msg-avatar.ai')) {
        lastGroup.remove();
      }
    }
    state.messages = state.messages.filter((m, i) => !(m.role === 'ai' && i === state.messages.length - 1));
    state.isGenerating = true;
    toggleGenerationUI(true);
    showTyping();
    simulateAIResponse(lastUser.content);
    showToast('🔄', 'Qayta yaratilmoqda...', 'info');
  }
}

function editMessage(bubbleId) {
  const bubble = document.getElementById(bubbleId);
  if (!bubble) return;
  const text = bubble.textContent;
  const input = document.getElementById('chatInput');
  input.value = text;
  input.focus();
  handleInputChange(input);
  showToast('✏️', 'Xabarni tahrirlang', 'info');
}

/* ═══════════════════════════════════════════
   FILE UPLOAD
═══════════════════════════════════════════ */
function triggerFileUpload() {
  document.getElementById('fileInput').click();
}

function triggerImageUpload() {
  document.getElementById('imageInput').click();
}

function handleFileSelect(input) {
  const file = input.files[0];
  if (!file) return;
  addAttachment('📄 ' + file.name, file);
  input.value = '';
}

function handleImageSelect(input) {
  const file = input.files[0];
  if (!file) return;
  addAttachment('🖼 ' + file.name, file);
  input.value = '';
}

function addAttachment(label, file) {
  const preview = document.getElementById('attachmentsPreview');
  const chip = document.createElement('div');
  chip.className = 'attachment-chip';
  chip.innerHTML = `${label} <span class="remove-att" onclick="this.parentElement.remove()">✕</span>`;
  preview.appendChild(chip);
  showToast('📎', 'Fayl qo\'shildi: ' + file.name.substring(0, 20), 'success');
}

/* ═══════════════════════════════════════════
   DRAG AND DROP
═══════════════════════════════════════════ */
document.addEventListener('dragover', (e) => {
  e.preventDefault();
  document.getElementById('dropOverlay').classList.add('active');
});

document.addEventListener('dragleave', (e) => {
  if (!e.relatedTarget) {
    document.getElementById('dropOverlay').classList.remove('active');
  }
});

document.addEventListener('drop', (e) => {
  e.preventDefault();
  document.getElementById('dropOverlay').classList.remove('active');
  const files = Array.from(e.dataTransfer.files);
  files.forEach(file => addAttachment((file.type.startsWith('image/') ? '🖼 ' : '📄 ') + file.name, file));
});

/* ═══════════════════════════════════════════
   MODEL SELECTOR
═══════════════════════════════════════════ */
function toggleModelDropdown() {
  const sel = document.getElementById('modelSelector');
  const dd = document.getElementById('modelDropdown');
  sel.classList.toggle('open');
  dd.classList.toggle('open');
}

function selectModel(modelId, el) {
  state.settings.model = modelId;
  document.getElementById('currentModelName').textContent = modelId;
  document.querySelectorAll('.model-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  toggleModelDropdown();
  showToast('🤖', 'Model: ' + modelId, 'success');
}

document.addEventListener('click', (e) => {
  const wrap = document.querySelector('.topbar-model-wrap');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('modelSelector').classList.remove('open');
    document.getElementById('modelDropdown').classList.remove('open');
  }
});

/* ═══════════════════════════════════════════
   THEME
═══════════════════════════════════════════ */
function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  showToast(state.theme === 'dark' ? '🌙' : '☀️', state.theme === 'dark' ? 'Qorong\'u mavzu' : 'Yorug\' mavzu', 'info');
}

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme === 'midnight' ? 'dark' : theme);
  if (theme === 'midnight') {
    document.documentElement.style.setProperty('--bg-base', '#000000');
    document.documentElement.style.setProperty('--bg-sidebar', '#050010');
  } else {
    document.documentElement.style.removeProperty('--bg-base');
    document.documentElement.style.removeProperty('--bg-sidebar');
  }
  document.querySelectorAll('.theme-option').forEach(o => o.classList.remove('active'));
  document.getElementById('theme-' + theme)?.classList.add('active');
  showToast('🎨', 'Mavzu o\'zgartirildi', 'info');
}

/* ═══════════════════════════════════════════
   MODALS
═══════════════════════════════════════════ */
function openSettings() {
  document.getElementById('settingsModal').classList.add('open');
}

function openHelp() {
  showToast('❓', 'Yordam bo\'limi tez orada!', 'info');
}

function openKeyboardShortcuts() {
  document.getElementById('shortcutsModal').classList.add('open');
}

function openProfile() {
  switchTab('account', document.querySelector('[onclick*="account"]'));
  openSettings();
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function closeModalOnOverlay(event, id) {
  if (event.target === event.currentTarget) closeModal(id);
}

function switchTab(tab, el) {
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
  if (el) el.classList.add('active');
  document.querySelectorAll('[id^="tab-"]').forEach(t => t.classList.add('hidden'));
  const target = document.getElementById('tab-' + tab);
  if (target) target.classList.remove('hidden');
}

/* ═══════════════════════════════════════════
   SEARCH MODAL
═══════════════════════════════════════════ */
function openSearchModal() {
  document.getElementById('searchModal').classList.add('open');
  setTimeout(() => document.getElementById('globalSearch').focus(), 100);
}

function handleGlobalSearch(q) {
  const results = document.getElementById('searchResults');
  if (!q) return;
  // Simple filter
  const items = results.querySelectorAll('.search-result-item');
  items.forEach(item => {
    const title = item.querySelector('.title');
    if (title) {
      item.style.display = !q || title.textContent.toLowerCase().includes(q.toLowerCase()) ? 'flex' : 'none';
    }
  });
}

function loadChatFromSearch(id) {
  loadChat(id);
  closeModal('searchModal');
}

/* ═══════════════════════════════════════════
   SETTINGS HANDLERS
═══════════════════════════════════════════ */
function updateSetting(key, value) {
  state.settings[key] = value;
}

function updateFontSize(val) {
  document.querySelectorAll('.msg-bubble').forEach(b => b.style.fontSize = val + 'px');
}

function updateTemp(val) {
  state.settings.temperature = val / 10;
}

function updateMaxTokens(val) {
  state.settings.maxTokens = parseInt(val);
}

function toggleAnimations(enabled) {
  document.documentElement.style.setProperty('--transition-med', enabled ? '0.25s cubic-bezier(0.4, 0, 0.2, 1)' : '0s');
  document.documentElement.style.setProperty('--transition-slow', enabled ? '0.4s cubic-bezier(0.4, 0, 0.2, 1)' : '0s');
}

function saveApiKey() {
  const key = document.getElementById('apiKeyInput').value;
  if (key) {
    showToast('🔑', 'API kaliti saqlandi', 'success');
    closeModal('settingsModal');
  } else {
    showToast('⚠️', 'API kalitini kiriting', 'error');
  }
}

/* ═══════════════════════════════════════════
   EXPORT
═══════════════════════════════════════════ */
function exportChat() {
  if (state.messages.length === 0) {
    showToast('⚠️', 'Eksport uchun xabarlar yo\'q', 'error');
    return;
  }

  const data = {
    exportDate: new Date().toISOString(),
    model: state.settings.model,
    messages: state.messages
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'somo-ai-chat-' + Date.now() + '.json';
  a.click();
  URL.revokeObjectURL(url);
  showToast('💾', 'Suhbat eksport qilindi!', 'success');
}

/* ═══════════════════════════════════════════
   TOAST
═══════════════════════════════════════════ */
function showToast(icon, message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML = `<span class="toast-icon">${icon}</span>${message}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

/* ═══════════════════════════════════════════
   GO HOME
═══════════════════════════════════════════ */
function goHome() {
  startNewChat();
}

/* ═══════════════════════════════════════════
   KEYBOARD SHORTCUTS
═══════════════════════════════════════════ */
document.addEventListener('keydown', (e) => {
  const ctrl = e.ctrlKey || e.metaKey;

  if (ctrl && e.key === 'k') { e.preventDefault(); openSearchModal(); }
  if (ctrl && e.key === 'n') { e.preventDefault(); startNewChat(); }
  if (ctrl && e.key === 'b') { e.preventDefault(); toggleSidebar(); }
  if (ctrl && e.key === 't') { e.preventDefault(); toggleTheme(); }
  if (ctrl && e.key === ',') { e.preventDefault(); openSettings(); }
  if (ctrl && e.key === 'e') { e.preventDefault(); exportChat(); }

  if (e.key === 'Escape') {
    closeModal('settingsModal');
    closeModal('searchModal');
    closeModal('shortcutsModal');
    if (state.isGenerating) stopGeneration();
  }
});

/* ═══════════════════════════════════════════
   UTILITIES
═══════════════════════════════════════════ */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* ═══════════════════════════════════════════
   GREETING
═══════════════════════════════════════════ */
function updateGreeting() {
  const hour = new Date().getHours();
  let greeting = 'Salom';
  if (hour >= 5 && hour < 12) greeting = 'Xayrli tong';
  else if (hour >= 12 && hour < 17) greeting = 'Xayrli kun';
  else if (hour >= 17 && hour < 21) greeting = 'Xayrli kech';
  else greeting = 'Yaxshi tunlar';

  const name = document.getElementById('userName')?.value || 'Somosab';
  document.getElementById('welcomeGreeting').textContent = `${greeting}, ${name}! 👋`;
}

/* ═══════════════════════════════════════════
   INIT
═══════════════════════════════════════════ */
updateGreeting();

// Animate suggestions with stagger
document.querySelectorAll('.suggestion-chip').forEach((chip, i) => {
  chip.style.animationDelay = (i * 80) + 'ms';
  chip.style.animation = 'fadeUp 0.5s ease both';
});

// Auto-resize chat input
const chatInput = document.getElementById('chatInput');
chatInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

console.log('%c🤖 Somo AI', 'font-size: 24px; color: #00e5ff; font-weight: bold; font-family: monospace;');
console.log('%cUltra Premium Edition — 3000+ lines of code', 'color: #7c3aed; font-size: 12px;');
</script>
</body>
</html>

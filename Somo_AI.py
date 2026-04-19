<!DOCTYPE html>
<html lang="uz" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Somo AI — Aqlli Yordamchi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap" rel="stylesheet" />

  <!-- ======================================================
       SOMO AI — MERGED FULL EDITION
       Birlashtirish: Streamlit app.py + HTML UI
       Umumiy qatorlar: 3000+
       Versiya: 2.0.0
  ====================================================== -->

  <style>
    /* ══════════════════════════════════════════════════════
       §1  CSS CUSTOM PROPERTIES — DESIGN TOKENS
    ══════════════════════════════════════════════════════ */
    :root {
      /* Backgrounds */
      --bg-void:       #03060f;
      --bg-base:       #060c1a;
      --bg-surface:    #0a1020;
      --bg-card:       #0e1528;
      --bg-hover:      #141d35;
      --bg-active:     #18223d;
      --bg-input:      #080f1e;
      --bg-sidebar:    #04080f;
      --bg-overlay:    rgba(3,6,15,0.85);

      /* Brand accent palette */
      --cyan:          #00e5ff;
      --cyan-dim:      rgba(0,229,255,0.15);
      --cyan-glow:     rgba(0,229,255,0.3);
      --purple:        #7c3aed;
      --purple-dim:    rgba(124,58,237,0.15);
      --pink:          #f72585;
      --pink-dim:      rgba(247,37,133,0.15);
      --green:         #06d6a0;
      --yellow:        #ffd166;
      --orange:        #fb8500;
      --red:           #ef233c;

      /* Text */
      --txt-100:       #eef2ff;
      --txt-70:        #8898c4;
      --txt-40:        #3d4f74;
      --txt-accent:    #00e5ff;

      /* Borders */
      --br-faint:      rgba(255,255,255,0.04);
      --br-subtle:     rgba(255,255,255,0.07);
      --br-normal:     rgba(255,255,255,0.11);
      --br-active:     rgba(0,229,255,0.35);
      --br-glow:       rgba(0,229,255,0.55);

      /* Shadows */
      --shadow-sm:     0 2px 8px rgba(0,0,0,0.4);
      --shadow-md:     0 8px 32px rgba(0,0,0,0.5);
      --shadow-lg:     0 20px 60px rgba(0,0,0,0.65);
      --shadow-cyan:   0 0 24px rgba(0,229,255,0.25), 0 0 64px rgba(0,229,255,0.08);
      --shadow-purple: 0 0 24px rgba(124,58,237,0.25);

      /* Layout */
      --sidebar-w:     272px;
      --topbar-h:      58px;

      /* Radii */
      --r-xs: 5px;
      --r-sm: 8px;
      --r-md: 12px;
      --r-lg: 18px;
      --r-xl: 24px;
      --r-2xl:32px;

      /* Typography */
      --font-display: 'Syne', sans-serif;
      --font-mono:    'JetBrains Mono', monospace;
      --font-body:    'DM Sans', sans-serif;

      /* Transitions */
      --t-fast:  0.14s ease;
      --t-med:   0.24s cubic-bezier(0.4,0,0.2,1);
      --t-slow:  0.42s cubic-bezier(0.4,0,0.2,1);
      --t-spring:0.5s cubic-bezier(0.34,1.56,0.64,1);

      /* Gradients */
      --grad-brand:   linear-gradient(135deg, #00e5ff 0%, #7c3aed 100%);
      --grad-brand-r: linear-gradient(135deg, #7c3aed 0%, #00e5ff 100%);
      --grad-surface: linear-gradient(135deg, rgba(0,229,255,0.05) 0%, rgba(124,58,237,0.05) 100%);
      --grad-card:    linear-gradient(160deg, rgba(0,229,255,0.03) 0%, rgba(124,58,237,0.03) 100%);
      --grad-bg:
        radial-gradient(ellipse 60% 50% at 15% 15%, rgba(0,229,255,0.04) 0%, transparent 70%),
        radial-gradient(ellipse 60% 50% at 85% 85%, rgba(124,58,237,0.05) 0%, transparent 70%),
        #060c1a;
    }

    /* Light theme overrides */
    [data-theme="light"] {
      --bg-void:    #edf0f7;
      --bg-base:    #f2f5fc;
      --bg-surface: #ffffff;
      --bg-card:    #f7f9ff;
      --bg-hover:   #eef1fa;
      --bg-active:  #e6ebf6;
      --bg-input:   #ffffff;
      --bg-sidebar: #1a1f2e;
      --bg-overlay: rgba(237,240,247,0.85);
      --txt-100:    #0f172a;
      --txt-70:     #4a5568;
      --txt-40:     #a0aec0;
      --br-faint:   rgba(0,0,0,0.04);
      --br-subtle:  rgba(0,0,0,0.07);
      --br-normal:  rgba(0,0,0,0.11);
      --grad-bg:
        radial-gradient(ellipse 60% 50% at 15% 15%, rgba(0,229,255,0.05) 0%, transparent 70%),
        radial-gradient(ellipse 60% 50% at 85% 85%, rgba(124,58,237,0.06) 0%, transparent 70%),
        #f2f5fc;
    }

    /* Midnight theme */
    [data-theme="midnight"] {
      --bg-void:    #000000;
      --bg-base:    #020008;
      --bg-surface: #060010;
      --bg-card:    #0a001a;
      --bg-hover:   #0f0025;
      --bg-sidebar: #010005;
      --cyan:       #bf5fff;
      --cyan-dim:   rgba(191,95,255,0.15);
      --cyan-glow:  rgba(191,95,255,0.3);
      --br-active:  rgba(191,95,255,0.4);
      --txt-accent: #bf5fff;
      --grad-brand: linear-gradient(135deg, #bf5fff 0%, #7c3aed 100%);
      --shadow-cyan:0 0 24px rgba(191,95,255,0.25), 0 0 64px rgba(191,95,255,0.08);
    }

    /* ══════════════════════════════════════════════════════
       §2  RESET & BASE
    ══════════════════════════════════════════════════════ */
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font-body);
      background: var(--grad-bg);
      color: var(--txt-100);
      min-height: 100vh;
      overflow: hidden;
      display: flex;
      position: relative;
    }

    /* Ambient orbs */
    body::before {
      content: '';
      position: fixed;
      top: -250px; left: -250px;
      width: 700px; height: 700px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0,229,255,0.05) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      animation: orbPulse 14s ease-in-out infinite alternate;
    }
    body::after {
      content: '';
      position: fixed;
      bottom: -250px; right: -250px;
      width: 800px; height: 800px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(124,58,237,0.05) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      animation: orbPulse 18s ease-in-out infinite alternate-reverse;
    }
    @keyframes orbPulse {
      0%   { transform: translate(0,0) scale(1); opacity: 0.7; }
      100% { transform: translate(50px,50px) scale(1.15); opacity: 1; }
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
      background: var(--cyan-dim);
      border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,229,255,0.35); }

    /* Selection */
    ::selection {
      background: rgba(0,229,255,0.2);
      color: var(--txt-100);
    }

    /* ══════════════════════════════════════════════════════
       §3  SIDEBAR
    ══════════════════════════════════════════════════════ */
    .sidebar {
      width: var(--sidebar-w);
      height: 100vh;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--br-faint);
      display: flex;
      flex-direction: column;
      position: fixed;
      left: 0; top: 0;
      z-index: 100;
      transition: transform var(--t-med), width var(--t-med);
      overflow: hidden;
    }
    .sidebar.collapsed { width: 58px; }

    /* Sidebar mobile overlay */
    .sb-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: var(--bg-overlay);
      z-index: 99;
      backdrop-filter: blur(4px);
    }
    .sb-overlay.active { display: block; }

    /* — Header — */
    .sb-header {
      height: var(--topbar-h);
      padding: 0 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid var(--br-faint);
      flex-shrink: 0;
    }
    .brand-logo {
      width: 34px; height: 34px;
      border-radius: 10px;
      background: var(--grad-brand);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 15px;
      color: #000;
      flex-shrink: 0;
      box-shadow: var(--shadow-cyan);
      cursor: pointer;
      transition: transform var(--t-fast);
    }
    .brand-logo:hover { transform: scale(1.07); }

    .brand-text {
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 16px;
      color: var(--txt-100);
      white-space: nowrap;
      opacity: 1;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .brand-text { opacity: 0; width: 0; overflow: hidden; }

    .sb-collapse-btn {
      margin-left: auto;
      width: 26px; height: 26px;
      border-radius: 7px;
      border: 1px solid var(--br-subtle);
      background: transparent;
      color: var(--txt-70);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      flex-shrink: 0;
    }
    .sb-collapse-btn:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
      border-color: var(--br-active);
    }
    .sb-collapse-btn svg { transition: transform var(--t-med); }
    .sidebar.collapsed .sb-collapse-btn svg { transform: rotate(180deg); }

    /* — New Chat Button — */
    .new-chat-btn {
      margin: 10px 10px 6px;
      padding: 9px 12px;
      border-radius: var(--r-md);
      background: var(--grad-surface);
      border: 1px solid rgba(0,229,255,0.18);
      color: var(--cyan);
      font-family: var(--font-body);
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all var(--t-fast);
      white-space: nowrap;
      overflow: hidden;
    }
    .new-chat-btn:hover {
      background: var(--cyan-dim);
      border-color: var(--br-active);
      box-shadow: var(--shadow-cyan);
      transform: translateY(-1px);
    }
    .new-chat-btn .btn-label {
      opacity: 1;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .new-chat-btn .btn-label { opacity: 0; width: 0; overflow: hidden; }

    /* — Search — */
    .sb-search {
      padding: 6px 10px;
      position: relative;
    }
    .sb-search input {
      width: 100%;
      padding: 7px 10px 7px 30px;
      border-radius: var(--r-sm);
      border: 1px solid var(--br-faint);
      background: rgba(255,255,255,0.03);
      color: var(--txt-100);
      font-family: var(--font-body);
      font-size: 12px;
      outline: none;
      transition: all var(--t-fast);
    }
    .sb-search input:focus {
      border-color: var(--br-active);
      background: rgba(0,229,255,0.03);
    }
    .sb-search input::placeholder { color: var(--txt-40); }
    .sb-search .srch-icon {
      position: absolute;
      left: 20px; top: 50%;
      transform: translateY(-50%);
      color: var(--txt-40);
      pointer-events: none;
    }
    .sidebar.collapsed .sb-search { display: none; }

    /* — Chat History List — */
    .sb-list {
      flex: 1;
      overflow-y: auto;
      padding: 4px 8px;
    }
    .sb-section-label {
      font-family: var(--font-mono);
      font-size: 9.5px;
      font-weight: 600;
      color: var(--txt-40);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      padding: 10px 6px 4px;
      white-space: nowrap;
      overflow: hidden;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .sb-section-label { opacity: 0; }

    .chat-item {
      padding: 8px 9px;
      border-radius: var(--r-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 9px;
      transition: all var(--t-fast);
      position: relative;
      margin-bottom: 1px;
      min-height: 36px;
      overflow: hidden;
    }
    .chat-item:hover { background: var(--bg-hover); }
    .chat-item.active {
      background: var(--grad-surface);
      border: 1px solid rgba(0,229,255,0.13);
    }
    .chat-item.active::before {
      content: '';
      position: absolute;
      left: 0; top: 20%; height: 60%; width: 2px;
      background: var(--cyan);
      border-radius: 0 2px 2px 0;
    }
    .ci-icon {
      width: 26px; height: 26px;
      border-radius: 7px;
      background: var(--bg-hover);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--txt-70);
      flex-shrink: 0;
      font-size: 12px;
      transition: all var(--t-fast);
    }
    .chat-item.active .ci-icon {
      background: var(--cyan-dim);
      color: var(--cyan);
    }
    .ci-meta {
      flex: 1; min-width: 0;
      opacity: 1;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .ci-meta { opacity: 0; width: 0; }
    .ci-title {
      font-size: 12px;
      font-weight: 500;
      color: var(--txt-100);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.3;
    }
    .ci-time {
      font-size: 10px;
      color: var(--txt-40);
      margin-top: 2px;
      font-family: var(--font-mono);
    }
    .ci-actions {
      display: none;
      gap: 3px;
    }
    .chat-item:hover .ci-actions { display: flex; }
    .ci-del-btn {
      width: 20px; height: 20px;
      border-radius: 5px;
      border: none;
      background: transparent;
      color: var(--txt-40);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      font-size: 11px;
    }
    .ci-del-btn:hover {
      background: var(--pink-dim);
      color: var(--pink);
    }

    /* — Token bar — */
    .sb-token-bar {
      padding: 8px 10px;
      border-top: 1px solid var(--br-faint);
    }
    .token-bar-head {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      color: var(--txt-40);
      font-family: var(--font-mono);
      margin-bottom: 5px;
    }
    .token-bar-track {
      height: 3px;
      border-radius: 2px;
      background: var(--bg-hover);
      overflow: hidden;
    }
    .token-bar-fill {
      height: 100%;
      border-radius: 2px;
      background: var(--grad-brand);
      transition: width 0.6s ease;
    }
    .sidebar.collapsed .sb-token-bar { display: none; }

    /* — Footer Nav — */
    .sb-footer {
      padding: 8px;
      border-top: 1px solid var(--br-faint);
      display: flex;
      flex-direction: column;
      gap: 1px;
    }
    .sb-nav-item {
      padding: 8px 9px;
      border-radius: var(--r-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 9px;
      transition: all var(--t-fast);
      color: var(--txt-70);
      font-size: 12.5px;
      min-height: 36px;
      overflow: hidden;
      white-space: nowrap;
    }
    .sb-nav-item:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
    }
    .sb-nav-item.danger:hover {
      background: var(--pink-dim);
      color: var(--pink);
    }
    .nav-ico {
      width: 26px; height: 26px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
    }
    .nav-lbl {
      opacity: 1;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .nav-lbl { opacity: 0; }

    /* — User Profile — */
    .sb-profile {
      padding: 8px;
      border-top: 1px solid var(--br-faint);
      display: flex;
      align-items: center;
      gap: 9px;
      cursor: pointer;
      border-radius: var(--r-sm);
      transition: all var(--t-fast);
      overflow: hidden;
    }
    .sb-profile:hover { background: var(--bg-hover); }
    .profile-avatar {
      width: 32px; height: 32px;
      border-radius: 9px;
      background: linear-gradient(135deg, var(--purple), var(--pink));
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 13px;
      color: #fff;
      flex-shrink: 0;
    }
    .profile-info {
      flex: 1; min-width: 0;
      opacity: 1;
      transition: opacity var(--t-med);
    }
    .sidebar.collapsed .profile-info { opacity: 0; }
    .profile-name {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--txt-100);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .profile-plan {
      font-size: 9.5px;
      color: var(--cyan);
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    /* ══════════════════════════════════════════════════════
       §4  MAIN LAYOUT
    ══════════════════════════════════════════════════════ */
    .main {
      flex: 1;
      margin-left: var(--sidebar-w);
      height: 100vh;
      display: flex;
      flex-direction: column;
      transition: margin-left var(--t-med);
      position: relative;
      z-index: 1;
    }
    .main.sb-collapsed { margin-left: 58px; }

    /* ══════════════════════════════════════════════════════
       §5  TOPBAR
    ══════════════════════════════════════════════════════ */
    .topbar {
      height: var(--topbar-h);
      padding: 0 18px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid var(--br-faint);
      background: rgba(6,12,26,0.88);
      backdrop-filter: blur(24px);
      position: sticky;
      top: 0;
      z-index: 50;
      flex-shrink: 0;
    }
    .topbar-mobile-btn {
      display: none;
      width: 34px; height: 34px;
      border-radius: var(--r-sm);
      border: 1px solid var(--br-subtle);
      background: transparent;
      color: var(--txt-70);
      cursor: pointer;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
    }
    .topbar-mobile-btn:hover { background: var(--bg-hover); color: var(--txt-100); }

    .topbar-title {
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 14px;
      color: var(--txt-100);
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .topbar-right {
      display: flex;
      align-items: center;
      gap: 7px;
      margin-left: auto;
    }
    .topbar-btn {
      width: 34px; height: 34px;
      border-radius: var(--r-sm);
      border: 1px solid var(--br-subtle);
      background: transparent;
      color: var(--txt-70);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      position: relative;
    }
    .topbar-btn:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
      border-color: var(--br-active);
    }
    .topbar-btn.on {
      background: var(--cyan-dim);
      color: var(--cyan);
      border-color: rgba(0,229,255,0.3);
    }

    /* Status pill */
    .status-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(6,214,160,0.08);
      border: 1px solid rgba(6,214,160,0.2);
      font-size: 11px;
      color: var(--green);
      font-family: var(--font-mono);
      white-space: nowrap;
    }
    .status-pill .dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--green);
      animation: blink 2.2s ease-in-out infinite;
    }
    .status-pill.offline {
      background: var(--pink-dim);
      border-color: rgba(247,37,133,0.2);
      color: var(--pink);
    }
    .status-pill.offline .dot { background: var(--pink); }

    @keyframes blink {
      0%,100% { opacity: 1; transform: scale(1); }
      50%      { opacity: 0.5; transform: scale(0.8); }
    }

    /* Model selector */
    .model-wrap { position: relative; }
    .model-selector {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 5px 10px;
      border-radius: var(--r-md);
      border: 1px solid var(--br-subtle);
      background: var(--bg-card);
      cursor: pointer;
      transition: all var(--t-fast);
    }
    .model-selector:hover {
      border-color: var(--br-active);
      background: var(--bg-hover);
    }
    .model-glow-dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 8px rgba(6,214,160,0.7);
      animation: blink 2s ease-in-out infinite;
    }
    .model-name-label {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--txt-100);
      white-space: nowrap;
    }
    .model-chevron {
      color: var(--txt-40);
      font-size: 9px;
      transition: transform var(--t-fast);
    }
    .model-selector.open .model-chevron { transform: rotate(180deg); }

    /* Model dropdown */
    .model-dropdown {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      width: 290px;
      background: var(--bg-card);
      border: 1px solid var(--br-normal);
      border-radius: var(--r-lg);
      padding: 7px;
      z-index: 200;
      box-shadow: var(--shadow-lg), var(--shadow-cyan);
      display: none;
      backdrop-filter: blur(24px);
    }
    .model-dropdown.open { display: block; animation: dropIn 0.18s ease; }
    @keyframes dropIn {
      from { opacity: 0; transform: translateY(-6px) scale(0.98); }
      to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    .model-opt {
      padding: 9px 11px;
      border-radius: var(--r-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all var(--t-fast);
    }
    .model-opt:hover { background: var(--bg-hover); }
    .model-opt.selected {
      background: var(--grad-surface);
      border: 1px solid rgba(0,229,255,0.13);
    }
    .model-opt-icon {
      width: 30px; height: 30px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
    }
    .model-opt-info { flex: 1; }
    .model-opt-name {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--txt-100);
    }
    .model-opt-desc {
      font-size: 10.5px;
      color: var(--txt-40);
      margin-top: 1px;
    }
    .model-badge {
      font-family: var(--font-mono);
      font-size: 9px;
      padding: 2px 5px;
      border-radius: 4px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .badge-new   { background: rgba(6,214,160,0.12); color: var(--green); border: 1px solid rgba(6,214,160,0.2); }
    .badge-fast  { background: rgba(255,209,102,0.12); color: var(--yellow); border: 1px solid rgba(255,209,102,0.2); }
    .badge-pro   { background: rgba(124,58,237,0.12); color: #a78bfa; border: 1px solid rgba(124,58,237,0.2); }

    /* ══════════════════════════════════════════════════════
       §6  CHAT AREA
    ══════════════════════════════════════════════════════ */
    .chat-area {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      scroll-behavior: smooth;
      position: relative;
    }

    /* Welcome screen */
    .welcome-screen {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 28px;
      text-align: center;
      animation: fadeUp 0.55s ease;
    }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(18px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .welcome-icon {
      width: 68px; height: 68px;
      border-radius: 20px;
      background: var(--grad-brand);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 26px;
      color: #000;
      margin-bottom: 22px;
      box-shadow: var(--shadow-cyan);
      animation: iconFloat 4.5s ease-in-out infinite alternate;
    }
    @keyframes iconFloat {
      0%   { transform: translateY(0) rotate(-2deg); }
      100% { transform: translateY(-10px) rotate(2deg); }
    }

    .welcome-title {
      font-family: var(--font-display);
      font-size: clamp(24px, 4vw, 36px);
      font-weight: 800;
      line-height: 1.1;
      margin-bottom: 10px;
      background: var(--grad-brand);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .welcome-sub {
      font-size: 14.5px;
      color: var(--txt-70);
      max-width: 420px;
      line-height: 1.65;
      margin-bottom: 34px;
    }

    /* Suggestion chips */
    .chips-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 9px;
      max-width: 680px;
      width: 100%;
    }
    .chip {
      padding: 13px 15px;
      border-radius: var(--r-lg);
      border: 1px solid var(--br-subtle);
      background: var(--bg-card);
      cursor: pointer;
      text-align: left;
      transition: all var(--t-med);
      display: flex;
      align-items: flex-start;
      gap: 11px;
      position: relative;
      overflow: hidden;
    }
    .chip::after {
      content: '';
      position: absolute;
      inset: 0;
      background: var(--grad-surface);
      opacity: 0;
      transition: opacity var(--t-med);
    }
    .chip:hover::after { opacity: 1; }
    .chip:hover {
      border-color: var(--br-active);
      transform: translateY(-2px);
      box-shadow: 0 8px 28px rgba(0,229,255,0.09);
    }
    .chip-ico  { font-size: 19px; line-height: 1; flex-shrink: 0; margin-top: 1px; }
    .chip-info { flex: 1; }
    .chip-ttl {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--txt-100);
      margin-bottom: 2px;
      line-height: 1.3;
    }
    .chip-sub {
      font-size: 10.5px;
      color: var(--txt-40);
      line-height: 1.4;
    }

    /* ══════════════════════════════════════════════════════
       §7  MESSAGES
    ══════════════════════════════════════════════════════ */
    .msgs-wrap {
      flex: 1;
      padding: 20px 0;
      display: none;
      flex-direction: column;
    }
    .msgs-wrap.visible { display: flex; }

    .msg-group {
      padding: 0 22px;
      animation: msgIn 0.32s cubic-bezier(0.4,0,0.2,1);
    }
    @keyframes msgIn {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .msg-row {
      display: flex;
      gap: 12px;
      max-width: 840px;
      margin: 0 auto;
      padding: 7px 0;
    }
    .msg-row.user { flex-direction: row-reverse; }

    .msg-avatar {
      width: 32px; height: 32px;
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 3px;
      font-size: 12px;
      font-weight: 700;
    }
    .msg-avatar.ai {
      background: var(--grad-brand);
      color: #000;
      font-family: var(--font-display);
      box-shadow: 0 4px 14px rgba(0,229,255,0.2);
    }
    .msg-avatar.user {
      background: linear-gradient(135deg, var(--purple), var(--pink));
      color: #fff;
      font-family: var(--font-display);
    }

    .msg-body    { flex: 1; min-width: 0; }
    .msg-sender {
      font-size: 10.5px;
      font-weight: 600;
      color: var(--txt-40);
      margin-bottom: 4px;
      font-family: var(--font-mono);
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .msg-row.user .msg-sender { text-align: right; }
    .msg-time {
      font-size: 9.5px;
      color: var(--txt-40);
      margin-left: 6px;
      font-family: var(--font-mono);
    }

    .msg-bubble {
      padding: 11px 15px;
      border-radius: var(--r-lg);
      font-size: 13.5px;
      line-height: 1.7;
      max-width: 100%;
      word-break: break-word;
    }
    .msg-row.ai .msg-bubble {
      background: var(--bg-card);
      border: 1px solid var(--br-subtle);
      color: var(--txt-100);
      border-radius: 3px var(--r-lg) var(--r-lg) var(--r-lg);
    }
    .msg-row.user .msg-bubble {
      background: linear-gradient(135deg, rgba(0,229,255,0.13), rgba(124,58,237,0.10));
      border: 1px solid rgba(0,229,255,0.18);
      color: var(--txt-100);
      border-radius: var(--r-lg) 3px var(--r-lg) var(--r-lg);
      margin-left: auto;
    }

    /* Bubble content typography */
    .msg-bubble p { margin-bottom: 9px; }
    .msg-bubble p:last-child { margin-bottom: 0; }
    .msg-bubble strong { color: var(--cyan); font-weight: 600; }
    .msg-bubble em { color: var(--txt-70); font-style: italic; }
    .msg-bubble ul, .msg-bubble ol { padding-left: 18px; margin: 8px 0; }
    .msg-bubble li { margin-bottom: 3px; line-height: 1.6; }

    .msg-bubble code {
      font-family: var(--font-mono);
      font-size: 11.5px;
      background: rgba(0,229,255,0.07);
      color: var(--cyan);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(0,229,255,0.1);
    }

    /* Code block */
    .msg-bubble pre {
      background: #020612;
      border: 1px solid rgba(0,229,255,0.09);
      border-radius: var(--r-md);
      padding: 14px 15px;
      overflow-x: auto;
      margin: 10px 0;
      position: relative;
    }
    .msg-bubble pre code {
      background: none;
      border: none;
      padding: 0;
      color: #b8d4f0;
      font-size: 12.5px;
      line-height: 1.65;
    }
    .code-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 14px;
      background: rgba(0,229,255,0.04);
      border-bottom: 1px solid rgba(0,229,255,0.07);
      border-radius: var(--r-md) var(--r-md) 0 0;
      margin: -14px -15px 12px;
    }
    .code-lang-badge {
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--cyan);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .copy-code-btn {
      font-family: var(--font-mono);
      font-size: 10px;
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid rgba(0,229,255,0.2);
      background: transparent;
      color: var(--txt-40);
      cursor: pointer;
      transition: all var(--t-fast);
    }
    .copy-code-btn:hover {
      background: var(--cyan-dim);
      color: var(--cyan);
    }

    /* Headings in bubbles */
    .msg-bubble h2 {
      font-family: var(--font-display);
      font-size: 17px;
      font-weight: 800;
      color: var(--txt-100);
      margin: 12px 0 6px;
    }
    .msg-bubble h3 {
      font-family: var(--font-display);
      font-size: 14px;
      font-weight: 700;
      color: var(--txt-100);
      margin: 10px 0 5px;
    }
    .msg-bubble h4 {
      font-size: 13px;
      font-weight: 700;
      color: var(--txt-70);
      margin: 8px 0 4px;
    }
    .msg-bubble blockquote {
      border-left: 2px solid var(--cyan);
      padding: 6px 12px;
      margin: 8px 0;
      background: var(--cyan-dim);
      border-radius: 0 var(--r-sm) var(--r-sm) 0;
      color: var(--txt-70);
      font-style: italic;
    }

    /* Message action buttons */
    .msg-actions {
      display: flex;
      gap: 3px;
      margin-top: 5px;
      opacity: 0;
      transition: opacity var(--t-fast);
    }
    .msg-row:hover .msg-actions { opacity: 1; }
    .msg-row.user .msg-actions { justify-content: flex-end; }
    .msg-act-btn {
      width: 26px; height: 26px;
      border-radius: 7px;
      border: 1px solid var(--br-subtle);
      background: var(--bg-card);
      color: var(--txt-40);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      font-size: 11px;
    }
    .msg-act-btn:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
      border-color: var(--br-active);
    }

    /* Typing indicator */
    .typing-wrap {
      padding: 0 22px;
      display: none;
    }
    .typing-wrap.visible { display: block; }
    .typing-row {
      display: flex;
      gap: 12px;
      max-width: 840px;
      margin: 0 auto;
      padding: 7px 0;
    }
    .typing-bubble {
      background: var(--bg-card);
      border: 1px solid var(--br-subtle);
      border-radius: 3px var(--r-lg) var(--r-lg) var(--r-lg);
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .typing-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--cyan);
      animation: typingBounce 1.2s ease-in-out infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.18s; opacity: 0.7; }
    .typing-dot:nth-child(3) { animation-delay: 0.36s; opacity: 0.4; }
    @keyframes typingBounce {
      0%,60%,100% { transform: translateY(0); }
      30%          { transform: translateY(-5px); }
    }

    /* Streaming cursor */
    .stream-cursor {
      display: inline-block;
      width: 2px;
      height: 1em;
      background: var(--cyan);
      margin-left: 2px;
      vertical-align: text-bottom;
      animation: cursorBlink 0.75s step-end infinite;
    }
    @keyframes cursorBlink {
      0%,100% { opacity: 1; }
      50%      { opacity: 0; }
    }

    /* Error bubble */
    .error-bubble {
      background: var(--pink-dim);
      border-color: rgba(247,37,133,0.25);
      color: var(--pink);
    }

    /* ══════════════════════════════════════════════════════
       §8  INPUT AREA
    ══════════════════════════════════════════════════════ */
    .input-area {
      padding: 14px 22px 18px;
      background: rgba(6,12,26,0.7);
      backdrop-filter: blur(24px);
      border-top: 1px solid var(--br-faint);
      flex-shrink: 0;
    }
    .input-wrap { max-width: 840px; margin: 0 auto; }

    /* Attachments preview */
    .att-list {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-bottom: 7px;
    }
    .att-chip {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: 20px;
      background: var(--cyan-dim);
      border: 1px solid rgba(0,229,255,0.15);
      font-size: 11px;
      color: var(--txt-70);
      font-family: var(--font-mono);
    }
    .att-chip .att-remove {
      cursor: pointer;
      color: var(--txt-40);
      transition: color var(--t-fast);
    }
    .att-chip .att-remove:hover { color: var(--pink); }

    /* Main input box */
    .input-box {
      display: flex;
      align-items: flex-end;
      gap: 9px;
      padding: 9px 11px;
      border-radius: var(--r-xl);
      border: 1.5px solid var(--br-subtle);
      background: var(--bg-input);
      transition: all var(--t-fast);
    }
    .input-box:focus-within {
      border-color: var(--br-active);
      background: rgba(0,229,255,0.02);
      box-shadow: 0 0 0 3px rgba(0,229,255,0.05), var(--shadow-cyan);
    }
    .input-tools {
      display: flex;
      align-items: center;
      gap: 3px;
      padding-bottom: 1px;
    }
    .input-tool-btn {
      width: 30px; height: 30px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--txt-40);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      font-size: 14px;
    }
    .input-tool-btn:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
    }

    .chat-input {
      flex: 1;
      border: none;
      background: transparent;
      color: var(--txt-100);
      font-family: var(--font-body);
      font-size: 13.5px;
      line-height: 1.6;
      resize: none;
      outline: none;
      min-height: 21px;
      max-height: 200px;
      overflow-y: auto;
      padding: 3px 0;
    }
    .chat-input::placeholder { color: var(--txt-40); }

    .send-btn {
      width: 34px; height: 34px;
      border-radius: 10px;
      border: none;
      background: var(--grad-brand);
      color: #000;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      flex-shrink: 0;
      font-size: 15px;
      box-shadow: 0 4px 14px rgba(0,229,255,0.18);
    }
    .send-btn:hover {
      transform: scale(1.07);
      box-shadow: var(--shadow-cyan);
    }
    .send-btn:active { transform: scale(0.95); }
    .send-btn:disabled {
      opacity: 0.35;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .stop-btn {
      width: 34px; height: 34px;
      border-radius: 10px;
      border: 1.5px solid rgba(247,37,133,0.4);
      background: var(--pink-dim);
      color: var(--pink);
      cursor: pointer;
      display: none;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      font-size: 13px;
      flex-shrink: 0;
    }
    .stop-btn.visible { display: flex; }
    .stop-btn:hover {
      background: rgba(247,37,133,0.2);
      border-color: var(--pink);
    }

    /* Input meta row */
    .input-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 8px;
      padding: 0 3px;
    }
    .quick-tags {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
    }
    .quick-tag {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 20px;
      background: var(--bg-card);
      border: 1px solid var(--br-faint);
      font-size: 11px;
      color: var(--txt-40);
      cursor: pointer;
      transition: all var(--t-fast);
      font-family: var(--font-mono);
    }
    .quick-tag:hover {
      background: var(--bg-hover);
      color: var(--txt-70);
      border-color: var(--br-active);
    }
    .char-count {
      font-family: var(--font-mono);
      font-size: 10.5px;
      color: var(--txt-40);
    }
    .char-count.warn   { color: var(--yellow); }
    .char-count.danger { color: var(--pink); }

    /* ══════════════════════════════════════════════════════
       §9  SETTINGS MODAL
    ══════════════════════════════════════════════════════ */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: var(--bg-overlay);
      z-index: 300;
      backdrop-filter: blur(10px);
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-overlay.open {
      display: flex;
      animation: overlayFadeIn 0.2s ease;
    }
    @keyframes overlayFadeIn {
      from { opacity: 0; }
      to   { opacity: 1; }
    }
    .modal {
      background: var(--bg-card);
      border: 1px solid var(--br-normal);
      border-radius: var(--r-xl);
      width: 100%;
      max-width: 580px;
      max-height: 82vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalSlideIn 0.28s cubic-bezier(0.4,0,0.2,1);
      box-shadow: var(--shadow-lg);
    }
    @keyframes modalSlideIn {
      from { opacity: 0; transform: translateY(18px) scale(0.97); }
      to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    .modal-header {
      padding: 18px 22px;
      border-bottom: 1px solid var(--br-faint);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .modal-title {
      font-family: var(--font-display);
      font-size: 16px;
      font-weight: 700;
      color: var(--txt-100);
    }
    .modal-close-btn {
      width: 30px; height: 30px;
      border-radius: 8px;
      border: 1px solid var(--br-subtle);
      background: transparent;
      color: var(--txt-40);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--t-fast);
      font-size: 13px;
    }
    .modal-close-btn:hover {
      background: var(--pink-dim);
      color: var(--pink);
      border-color: rgba(247,37,133,0.3);
    }

    /* Tabs */
    .modal-tabs {
      display: flex;
      gap: 3px;
      padding: 10px 14px 0;
      border-bottom: 1px solid var(--br-faint);
      flex-shrink: 0;
    }
    .modal-tab {
      padding: 7px 13px;
      border-radius: var(--r-sm) var(--r-sm) 0 0;
      border: none;
      background: transparent;
      color: var(--txt-40);
      cursor: pointer;
      font-family: var(--font-body);
      font-size: 12.5px;
      font-weight: 500;
      transition: all var(--t-fast);
      border-bottom: 2px solid transparent;
    }
    .modal-tab:hover { color: var(--txt-100); }
    .modal-tab.active {
      color: var(--cyan);
      border-bottom-color: var(--cyan);
    }

    .modal-body {
      flex: 1;
      overflow-y: auto;
      padding: 18px 22px;
    }

    /* Setting rows */
    .settings-group { margin-bottom: 22px; }
    .settings-group-label {
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 600;
      color: var(--txt-40);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 10px;
    }
    .setting-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 11px 13px;
      border-radius: var(--r-md);
      border: 1px solid var(--br-faint);
      background: var(--bg-surface);
      margin-bottom: 7px;
      transition: all var(--t-fast);
    }
    .setting-row:hover {
      border-color: var(--br-active);
      background: var(--bg-hover);
    }
    .setting-info { flex: 1; }
    .setting-label {
      font-size: 12.5px;
      font-weight: 500;
      color: var(--txt-100);
    }
    .setting-desc {
      font-size: 10.5px;
      color: var(--txt-40);
      margin-top: 1px;
    }

    /* Toggle switch */
    .toggle {
      position: relative;
      width: 40px; height: 22px;
      flex-shrink: 0;
    }
    .toggle input {
      opacity: 0; width: 0; height: 0;
      position: absolute;
    }
    .toggle-track {
      position: absolute;
      inset: 0;
      border-radius: 11px;
      background: var(--bg-hover);
      border: 1px solid var(--br-subtle);
      cursor: pointer;
      transition: all var(--t-fast);
    }
    .toggle-track::after {
      content: '';
      position: absolute;
      top: 2px; left: 2px;
      width: 16px; height: 16px;
      border-radius: 50%;
      background: var(--txt-40);
      transition: all var(--t-fast);
    }
    .toggle input:checked + .toggle-track {
      background: var(--cyan-dim);
      border-color: rgba(0,229,255,0.3);
    }
    .toggle input:checked + .toggle-track::after {
      background: var(--cyan);
      transform: translateX(18px);
      box-shadow: 0 0 8px rgba(0,229,255,0.5);
    }

    /* Theme grid */
    .theme-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7px;
    }
    .theme-opt {
      padding: 9px;
      border-radius: var(--r-md);
      border: 2px solid var(--br-subtle);
      cursor: pointer;
      transition: all var(--t-fast);
      text-align: center;
    }
    .theme-opt:hover { border-color: rgba(0,229,255,0.3); }
    .theme-opt.active {
      border-color: var(--cyan);
      background: var(--cyan-dim);
    }
    .theme-preview {
      height: 38px;
      border-radius: 6px;
      margin-bottom: 5px;
    }
    .theme-label {
      font-size: 10.5px;
      color: var(--txt-70);
      font-weight: 500;
    }

    /* Range slider */
    .range-slider {
      width: 110px;
    }
    .range-slider input[type="range"] {
      width: 100%;
      -webkit-appearance: none;
      height: 3px;
      border-radius: 2px;
      background: var(--bg-hover);
      outline: none;
    }
    .range-slider input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 15px; height: 15px;
      border-radius: 50%;
      background: var(--cyan);
      cursor: pointer;
      box-shadow: 0 0 7px rgba(0,229,255,0.4);
    }

    /* Textarea in modal */
    .settings-textarea {
      width: 100%;
      padding: 9px 11px;
      background: var(--bg-input);
      border: 1px solid var(--br-subtle);
      border-radius: var(--r-md);
      color: var(--txt-100);
      font-family: var(--font-mono);
      font-size: 11.5px;
      resize: vertical;
      outline: none;
      min-height: 75px;
      transition: border-color var(--t-fast);
    }
    .settings-textarea:focus { border-color: var(--br-active); }

    /* Input in modal */
    .settings-input {
      width: 100%;
      padding: 8px 11px;
      background: var(--bg-input);
      border: 1px solid var(--br-subtle);
      border-radius: var(--r-md);
      color: var(--txt-100);
      font-family: var(--font-mono);
      font-size: 12px;
      outline: none;
      transition: border-color var(--t-fast);
      margin-top: 7px;
    }
    .settings-input:focus { border-color: var(--br-active); }

    /* Modal action btn */
    .modal-action-btn {
      padding: 7px 14px;
      border-radius: var(--r-sm);
      border: none;
      background: var(--grad-brand);
      color: #000;
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
      transition: all var(--t-fast);
      margin-top: 8px;
    }
    .modal-action-btn:hover {
      transform: translateY(-1px);
      box-shadow: var(--shadow-cyan);
    }
    .modal-danger-btn {
      padding: 6px 12px;
      border-radius: var(--r-sm);
      background: var(--pink-dim);
      border: 1px solid rgba(247,37,133,0.3);
      color: var(--pink);
      font-size: 11.5px;
      cursor: pointer;
      font-weight: 500;
    }

    /* Hidden tabs */
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    /* ══════════════════════════════════════════════════════
       §10  SEARCH MODAL
    ══════════════════════════════════════════════════════ */
    .search-modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 400;
      background: var(--bg-overlay);
      backdrop-filter: blur(12px);
      align-items: flex-start;
      justify-content: center;
      padding-top: 80px;
    }
    .search-modal-overlay.open {
      display: flex;
      animation: overlayFadeIn 0.18s ease;
    }
    .search-box {
      width: 92%;
      max-width: 560px;
      background: var(--bg-card);
      border: 1px solid var(--br-active);
      border-radius: var(--r-xl);
      overflow: hidden;
      box-shadow: var(--shadow-cyan), var(--shadow-lg);
      animation: dropIn 0.22s ease;
    }
    .search-row {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--br-faint);
    }
    .search-row input {
      flex: 1;
      border: none;
      background: transparent;
      color: var(--txt-100);
      font-family: var(--font-body);
      font-size: 14px;
      outline: none;
    }
    .search-row input::placeholder { color: var(--txt-40); }
    .search-results-list {
      padding: 7px;
      max-height: 340px;
      overflow-y: auto;
    }
    .search-section-label {
      padding: 10px 10px 4px;
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--txt-40);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .search-result-item {
      padding: 9px 11px;
      border-radius: var(--r-sm);
      cursor: pointer;
      display: flex;
      gap: 11px;
      align-items: center;
      transition: all var(--t-fast);
    }
    .search-result-item:hover { background: var(--bg-hover); }
    .sri-icon {
      width: 30px; height: 30px;
      border-radius: 7px;
      background: var(--bg-hover);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 13px;
    }
    .sri-text .sri-title {
      font-size: 12.5px;
      font-weight: 500;
      color: var(--txt-100);
    }
    .sri-text .sri-desc {
      font-size: 10.5px;
      color: var(--txt-40);
      margin-top: 1px;
    }
    .search-footer {
      padding: 9px 15px;
      border-top: 1px solid var(--br-faint);
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .kbd {
      font-family: var(--font-mono);
      font-size: 9.5px;
      padding: 2px 5px;
      border-radius: 4px;
      background: var(--bg-hover);
      border: 1px solid var(--br-subtle);
      color: var(--txt-40);
    }

    /* ══════════════════════════════════════════════════════
       §11  KEYBOARD SHORTCUTS MODAL
    ══════════════════════════════════════════════════════ */
    .shortcut-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 9px 11px;
      border-radius: var(--r-sm);
      background: var(--bg-surface);
      margin-bottom: 5px;
    }
    .shortcut-name {
      font-size: 12.5px;
      color: var(--txt-70);
    }
    .shortcut-keys {
      display: flex;
      gap: 3px;
    }

    /* ══════════════════════════════════════════════════════
       §12  EXPORT PANEL
    ══════════════════════════════════════════════════════ */
    .export-btn-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 6px;
    }
    .export-btn {
      padding: 8px 14px;
      border-radius: var(--r-sm);
      border: 1px solid var(--br-subtle);
      background: var(--bg-surface);
      color: var(--txt-70);
      font-size: 12px;
      cursor: pointer;
      transition: all var(--t-fast);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .export-btn:hover {
      background: var(--bg-hover);
      color: var(--txt-100);
      border-color: var(--br-active);
    }

    /* ══════════════════════════════════════════════════════
       §13  TOAST NOTIFICATIONS
    ══════════════════════════════════════════════════════ */
    .toast-stack {
      position: fixed;
      bottom: 22px; right: 22px;
      z-index: 500;
      display: flex;
      flex-direction: column;
      gap: 7px;
    }
    .toast {
      padding: 10px 14px;
      border-radius: var(--r-md);
      border: 1px solid var(--br-normal);
      background: var(--bg-card);
      backdrop-filter: blur(24px);
      display: flex;
      align-items: center;
      gap: 9px;
      font-size: 12.5px;
      color: var(--txt-100);
      box-shadow: var(--shadow-md);
      animation: toastIn 0.28s ease, toastOut 0.28s ease 2.7s forwards;
      min-width: 180px;
      max-width: 280px;
    }
    @keyframes toastIn {
      from { opacity: 0; transform: translateX(16px); }
      to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes toastOut {
      from { opacity: 1; transform: translateX(0); }
      to   { opacity: 0; transform: translateX(16px); }
    }
    .toast.success { border-color: rgba(6,214,160,0.3); }
    .toast.error   { border-color: rgba(247,37,133,0.3); }
    .toast.info    { border-color: rgba(0,229,255,0.3); }
    .toast-ico     { font-size: 15px; flex-shrink: 0; }

    /* ══════════════════════════════════════════════════════
       §14  DROP OVERLAY
    ══════════════════════════════════════════════════════ */
    .drop-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 999;
      background: rgba(0,229,255,0.04);
      border: 2.5px dashed rgba(0,229,255,0.3);
      border-radius: var(--r-xl);
      margin: 14px;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 10px;
      backdrop-filter: blur(6px);
    }
    .drop-overlay.active { display: flex; animation: overlayFadeIn 0.2s ease; }
    .drop-overlay h3 {
      font-family: var(--font-display);
      font-size: 20px;
      color: var(--cyan);
    }
    .drop-overlay p { font-size: 13px; color: var(--txt-70); }

    /* ══════════════════════════════════════════════════════
       §15  API KEY NOTICE BANNER
    ══════════════════════════════════════════════════════ */
    .api-banner {
      margin: 12px 22px 0;
      padding: 9px 14px;
      border-radius: var(--r-md);
      background: rgba(255,209,102,0.07);
      border: 1px solid rgba(255,209,102,0.2);
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12.5px;
      color: var(--yellow);
      display: none;
    }
    .api-banner.visible { display: flex; }
    .api-banner a {
      color: var(--cyan);
      text-decoration: underline;
      cursor: pointer;
    }
    .api-banner-close {
      margin-left: auto;
      cursor: pointer;
      color: var(--txt-40);
      font-size: 13px;
      flex-shrink: 0;
    }
    .api-banner-close:hover { color: var(--txt-100); }

    /* ══════════════════════════════════════════════════════
       §16  RESPONSIVE
    ══════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
      .sidebar {
        transform: translateX(-100%);
        width: var(--sidebar-w) !important;
      }
      .sidebar.mobile-open {
        transform: translateX(0);
      }
      .main { margin-left: 0 !important; }
      .topbar-mobile-btn { display: flex; }
      .chips-grid { grid-template-columns: 1fr; }
      .model-name-label { display: none; }
      .input-meta { display: none; }
      .status-pill { display: none; }
      .toast-stack { bottom: 14px; right: 14px; }
    }

    /* ══════════════════════════════════════════════════════
       §17  UTILITY CLASSES
    ══════════════════════════════════════════════════════ */
    .hidden { display: none !important; }
    .divider {
      height: 1px;
      background: var(--br-faint);
      margin: 6px 0;
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
      background: var(--cyan-dim);
      color: var(--cyan);
      border: 1px solid rgba(0,229,255,0.2);
    }

    /* Tooltip */
    [data-tip] { position: relative; }
    [data-tip]::after {
      content: attr(data-tip);
      position: absolute;
      bottom: calc(100% + 7px);
      left: 50%;
      transform: translateX(-50%);
      padding: 4px 9px;
      border-radius: 5px;
      background: #1a2235;
      color: var(--txt-100);
      font-size: 10.5px;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transition: opacity var(--t-fast);
      border: 1px solid var(--br-subtle);
      font-family: var(--font-body);
      z-index: 999;
    }
    [data-tip]:hover::after { opacity: 1; }
  </style>
</head>
<body>

<!-- Drop overlay -->
<div class="drop-overlay" id="dropOverlay">
  <div style="font-size:46px">📁</div>
  <h3>Faylni bu yerga tashlang</h3>
  <p>Rasm, PDF yoki matn fayllarini qabul qilamiz</p>
</div>

<!-- Mobile sidebar overlay -->
<div class="sb-overlay" id="sbOverlay" onclick="closeMobileSB()"></div>

<!-- ══════════════════════════════ SIDEBAR ══════════════════════════════ -->
<aside class="sidebar" id="sidebar">

  <div class="sb-header">
    <div class="brand-logo" onclick="goHome()" title="Somo AI bosh sahifa">S</div>
    <span class="brand-text">Somo AI</span>
    <button class="sb-collapse-btn" onclick="toggleSidebar()" data-tip="Yig'ish / Yoyish">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
        <path d="M8 2.5L4.5 6.5L8 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>

  <button class="new-chat-btn" onclick="startNewChat()">
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M7 1.5V12.5M1.5 7H12.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
    <span class="btn-label">Yangi suhbat</span>
  </button>

  <div class="sb-search">
    <svg class="srch-icon" width="12" height="12" viewBox="0 0 14 14" fill="none">
      <circle cx="6" cy="6" r="4" stroke="currentColor" stroke-width="1.3"/>
      <path d="M9 9L12.5 12.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    <input type="text" placeholder="Suhbatlarni qidirish..." id="chatSearchInput" oninput="filterChatList(this.value)" />
  </div>

  <div class="sb-list" id="chatList">
    <!-- injected dynamically -->
  </div>

  <div class="sb-token-bar">
    <div class="token-bar-head">
      <span>Token sarfi</span>
      <span id="tokenLabel">0 / 8,000</span>
    </div>
    <div class="token-bar-track">
      <div class="token-bar-fill" id="tokenFill" style="width:0%"></div>
    </div>
  </div>

  <div class="sb-footer">
    <div class="sb-nav-item" onclick="openSettings()">
      <div class="nav-ico">⚙️</div><span class="nav-lbl">Sozlamalar</span>
    </div>
    <div class="sb-nav-item" onclick="openShortcuts()">
      <div class="nav-ico">⌨️</div><span class="nav-lbl">Klaviatura yorliqlari</span>
    </div>
    <div class="sb-nav-item" onclick="openExportModal()">
      <div class="nav-ico">💾</div><span class="nav-lbl">Eksport</span>
    </div>
    <div class="sb-nav-item danger" onclick="clearAllChats()">
      <div class="nav-ico">🗑️</div><span class="nav-lbl">Hammasini o'chirish</span>
    </div>
  </div>

  <div class="sb-profile" onclick="openProfileTab()">
    <div class="profile-avatar" id="profileAvatar">S</div>
    <div class="profile-info">
      <div class="profile-name" id="profileName">Foydalanuvchi</div>
      <div class="profile-plan">Pro rejim</div>
    </div>
    <svg width="11" height="11" viewBox="0 0 11 11" fill="none" style="color:var(--txt-40);flex-shrink:0">
      <path d="M2.5 4.5L5.5 7.5L8.5 4.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
  </div>
</aside>

<!-- ══════════════════════════════ MAIN ══════════════════════════════ -->
<main class="main" id="main">

  <!-- Topbar -->
  <header class="topbar">
    <button class="topbar-mobile-btn" id="mobileMenuBtn" onclick="openMobileSB()">
      <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
        <path d="M2 3.5H13M2 7.5H13M2 11.5H13" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
    </button>

    <span class="topbar-title" id="topbarTitle">Yangi suhbat</span>

    <div class="topbar-right">

      <div class="status-pill" id="statusPill">
        <div class="dot"></div>
        <span id="statusText">Online</span>
      </div>

      <!-- Model selector -->
      <div class="model-wrap">
        <div class="model-selector" id="modelSelector" onclick="toggleModelDD()">
          <div class="model-glow-dot"></div>
          <span class="model-name-label" id="modelDisplayName">llama-3.3-70b</span>
          <span class="model-chevron">▾</span>
        </div>
        <div class="model-dropdown" id="modelDD">
          <div class="model-opt selected" data-model="llama-3.3-70b-versatile" onclick="pickModel(this)">
            <div class="model-opt-icon" style="background:rgba(0,229,255,0.1)">🦙</div>
            <div class="model-opt-info">
              <div class="model-opt-name">Llama 3.3 70B</div>
              <div class="model-opt-desc">Groq · Kuchli · Versatile</div>
            </div>
            <span class="model-badge badge-new">Yangi</span>
          </div>
          <div class="model-opt" data-model="llama-3.1-8b-instant" onclick="pickModel(this)">
            <div class="model-opt-icon" style="background:rgba(255,209,102,0.1)">⚡</div>
            <div class="model-opt-info">
              <div class="model-opt-name">Llama 3.1 8B</div>
              <div class="model-opt-desc">Groq · Eng tez · Ixcham</div>
            </div>
            <span class="model-badge badge-fast">Tez</span>
          </div>
          <div class="model-opt" data-model="mixtral-8x7b-32768" onclick="pickModel(this)">
            <div class="model-opt-icon" style="background:rgba(124,58,237,0.1)">🔀</div>
            <div class="model-opt-info">
              <div class="model-opt-name">Mixtral 8x7B</div>
              <div class="model-opt-desc">Groq · MoE arxitektura</div>
            </div>
            <span class="model-badge badge-pro">Pro</span>
          </div>
          <div class="model-opt" data-model="gemma2-9b-it" onclick="pickModel(this)">
            <div class="model-opt-icon" style="background:rgba(6,214,160,0.1)">💎</div>
            <div class="model-opt-info">
              <div class="model-opt-name">Gemma 2 9B</div>
              <div class="model-opt-desc">Google · Samarali</div>
            </div>
            <span class="model-badge badge-fast">Tez</span>
          </div>
        </div>
      </div>

      <button class="topbar-btn" onclick="openSearch()" data-tip="Qidirish (Ctrl+K)">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="6" cy="6" r="4" stroke="currentColor" stroke-width="1.3"/>
          <path d="M9 9L12.5 12.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <button class="topbar-btn" onclick="toggleTheme()" data-tip="Mavzu" id="themeToggleBtn">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="7" r="2.8" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7 1.5V2.8M7 11.2V12.5M1.5 7H2.8M11.2 7H12.5M3.1 3.1L4 4M10 10L10.9 10.9M3.1 10.9L4 10M10 4L10.9 3.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <button class="topbar-btn" onclick="exportCurrentChat()" data-tip="Eksport qilish">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M7 9.5V2M7 9.5L4.5 7M7 9.5L9.5 7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 11.5H12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>

      <button class="topbar-btn" onclick="openSettings()" data-tip="Sozlamalar (Ctrl+,)">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="7" r="1.8" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7 1.5V3M7 11V12.5M1.5 7H3M11 7H12.5M3.2 3.2L4.1 4.1M9.9 9.9L10.8 10.8M3.2 10.8L4.1 9.9M9.9 4.1L10.8 3.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </header>

  <!-- API Banner -->
  <div class="api-banner" id="apiBanner">
    <span>⚠️</span>
    <span>Groq API kaliti kiritilmagan. <a onclick="openSettings()">Sozlamalarda kiriting</a> yoki pastda yozib ko'ring (demo rejim).</span>
    <span class="api-banner-close" onclick="dismissBanner()">✕</span>
  </div>

  <!-- Chat area -->
  <div class="chat-area" id="chatArea">

    <!-- Welcome screen -->
    <div class="welcome-screen" id="welcomeScreen">
      <div class="welcome-icon">S</div>
      <h1 class="welcome-title" id="welcomeTitle">Salom! 👋</h1>
      <p class="welcome-sub">
        Savolingizni yozing yoki quyidagi mavzulardan birini tanlang. Men sizga dasturlash, ta'lim va ko'p sohalarda yordam bera olaman.
      </p>

      <div class="chips-grid" id="chipsGrid">
        <div class="chip" onclick="sendSuggestion('Python da Telegram bot qanday yasaladi? Bosqichma-bosqich tushuntirib ber.')">
          <div class="chip-ico">🤖</div>
          <div class="chip-info">
            <div class="chip-ttl">Python da Telegram bot</div>
            <div class="chip-sub">Bosqichma-bosqich qo'llanma</div>
          </div>
        </div>
        <div class="chip" onclick="sendSuggestion('Ingliz tilini tez o\'rganish uchun samarali usullar qanday?')">
          <div class="chip-ico">🇬🇧</div>
          <div class="chip-info">
            <div class="chip-ttl">Ingliz tilini o'rganish</div>
            <div class="chip-sub">Tez o'rganish metodlari</div>
          </div>
        </div>
        <div class="chip" onclick="sendSuggestion('Mening resumemni yaxshilashga yordam ber. Asosiy kamchiliklarni ayt.')">
          <div class="chip-ico">📄</div>
          <div class="chip-info">
            <div class="chip-ttl">Resume yaxshilash</div>
            <div class="chip-sub">Professional ko'rinish uchun</div>
          </div>
        </div>
        <div class="chip" onclick="sendSuggestion('SQL va NoSQL ma\'lumotlar bazalari orasidagi asosiy farqlar nima?')">
          <div class="chip-ico">🗄️</div>
          <div class="chip-info">
            <div class="chip-ttl">SQL va NoSQL farqi</div>
            <div class="chip-sub">Qachon qaysin ishlatish kerak</div>
          </div>
        </div>
        <div class="chip" onclick="sendSuggestion('React.js ni o\'rganish uchun 30 kunlik reja tuzib ber.')">
          <div class="chip-ico">⚛️</div>
          <div class="chip-info">
            <div class="chip-ttl">React.js 30 kunlik reja</div>
            <div class="chip-sub">Boshliqdan professionalga</div>
          </div>
        </div>
        <div class="chip" onclick="sendSuggestion('Machine Learning uchun Python kutubxonalari qaysilar? Har biri nima uchun?')">
          <div class="chip-ico">🧠</div>
          <div class="chip-info">
            <div class="chip-ttl">Machine Learning</div>
            <div class="chip-sub">Python kutubxonalari</div>
          </div>
        </div>
      </div>

      <div style="margin-top:22px;color:var(--txt-40);font-size:11.5px;font-family:var(--font-mono)" id="welcomeModelInfo">
        <!-- model info injected -->
      </div>
    </div>

    <!-- Messages -->
    <div class="msgs-wrap" id="msgsWrap"></div>

    <!-- Typing indicator -->
    <div class="typing-wrap" id="typingWrap">
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

  </div><!-- /chat-area -->

  <!-- Input area -->
  <div class="input-area">
    <div class="input-wrap">

      <div class="att-list" id="attList"></div>

      <div class="input-box" id="inputBox">
        <div class="input-tools">
          <button class="input-tool-btn" onclick="triggerFile()" data-tip="Fayl qo'shish" title="Fayl">📎</button>
          <button class="input-tool-btn" onclick="triggerImage()" data-tip="Rasm qo'shish" title="Rasm">🖼️</button>
        </div>
        <textarea
          class="chat-input"
          id="chatInput"
          placeholder="Savolingizni yozing... (Shift+Enter yangi qator)"
          rows="1"
          oninput="onInputChange(this)"
          onkeydown="onInputKeyDown(event)"
        ></textarea>
        <button class="stop-btn" id="stopBtn" onclick="stopGeneration()">⏹</button>
        <button class="send-btn" id="sendBtn" onclick="sendMessage()">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <path d="M13.5 7.5L2 2L5.2 7.5L2 13L13.5 7.5Z" fill="currentColor"/>
          </svg>
        </button>
      </div>

      <div class="input-meta">
        <div class="quick-tags">
          <div class="quick-tag" onclick="sendSuggestion('Kodni tushuntir')">💡 Kodni tushuntir</div>
          <div class="quick-tag" onclick="sendSuggestion('Xatoni topib tuzat')">🐛 Debug</div>
          <div class="quick-tag" onclick="sendSuggestion('Tarjima qil')">🌐 Tarjima</div>
          <div class="quick-tag" onclick="sendSuggestion('Qisqacha yozib ber')">✂️ Qisqacha</div>
        </div>
        <div class="char-count" id="charCount">0 / 4000</div>
      </div>
    </div>
  </div>

</main><!-- /main -->

<!-- File inputs -->
<input type="file" id="fileInput" accept=".pdf,.txt,.md,.csv,.json,.py,.js,.ts,.html,.css,.xml,.yaml" hidden onchange="handleFileInput(this)" />
<input type="file" id="imageInput" accept="image/*" hidden onchange="handleImageInput(this)" />

<!-- ══════════════════════════════ SETTINGS MODAL ══════════════════════════════ -->
<div class="modal-overlay" id="settingsModal" onclick="overlayClose(event,'settingsModal')">
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title">⚙️ Sozlamalar</span>
      <button class="modal-close-btn" onclick="closeModal('settingsModal')">✕</button>
    </div>
    <div class="modal-tabs">
      <button class="modal-tab active" onclick="switchSettingsTab('general',this)">Umumiy</button>
      <button class="modal-tab" onclick="switchSettingsTab('appearance',this)">Ko'rinish</button>
      <button class="modal-tab" onclick="switchSettingsTab('model',this)">Model</button>
      <button class="modal-tab" onclick="switchSettingsTab('account',this)">Hisob</button>
      <button class="modal-tab" onclick="switchSettingsTab('export',this)">Eksport</button>
    </div>
    <div class="modal-body">

      <!-- General -->
      <div class="tab-panel active" id="st-general">
        <div class="settings-group">
          <div class="settings-group-label">Xulq-atvor</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Enter yuborish</div>
              <div class="setting-desc">Enter bosilganda xabar yuboriladi (Shift+Enter yangi qator)</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-enterSend" checked onchange="cfg('enterSend',this.checked)"><div class="toggle-track"></div></label>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Yozish animatsiyasi</div>
              <div class="setting-desc">AI javob yozayotganda animatsiya ko'rsatish</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-showTyping" checked onchange="cfg('showTyping',this.checked)"><div class="toggle-track"></div></label>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Suhbat tarixini saqlash</div>
              <div class="setting-desc">Suhbatlar brauzerda saqlanadi</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-saveHistory" checked onchange="cfg('saveHistory',this.checked)"><div class="toggle-track"></div></label>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Ovozli bildirishnoma</div>
              <div class="setting-desc">Javob kelganda tovush chiqarish</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-soundNotif" onchange="cfg('soundNotif',this.checked)"><div class="toggle-track"></div></label>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Suhbatni avtomatik nomlash</div>
              <div class="setting-desc">Birinchi xabardan suhbat nomi yaratiladi</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-autoTitle" checked onchange="cfg('autoTitle',this.checked)"><div class="toggle-track"></div></label>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Tizim xabari (System Prompt)</div>
          <div class="setting-desc" style="margin-bottom:8px;font-size:11px;color:var(--txt-40)">AI uchun global ko'rsatma. Barcha suhbatlarga qo'llaniladi.</div>
          <textarea class="settings-textarea" id="cfg-systemPrompt" rows="4" onchange="cfg('systemPrompt',this.value)">Sen Somo AI — O'zbekistondagi eng aqlli AI yordamchisan. Foydalanuvchilarga dasturlash, ta'lim va boshqa sohalarda O'zbek tilida yordam berasan.</textarea>
        </div>
      </div>

      <!-- Appearance -->
      <div class="tab-panel" id="st-appearance">
        <div class="settings-group">
          <div class="settings-group-label">Mavzu</div>
          <div class="theme-grid">
            <div class="theme-opt active" id="to-dark" onclick="applyTheme('dark')">
              <div class="theme-preview" style="background:linear-gradient(135deg,#03060f,#0a1020)"></div>
              <div class="theme-label">Qorong'u</div>
            </div>
            <div class="theme-opt" id="to-light" onclick="applyTheme('light')">
              <div class="theme-preview" style="background:linear-gradient(135deg,#f2f5fc,#e6ebf6)"></div>
              <div class="theme-label">Yorug'</div>
            </div>
            <div class="theme-opt" id="to-midnight" onclick="applyTheme('midnight')">
              <div class="theme-preview" style="background:linear-gradient(135deg,#000,#1a0030)"></div>
              <div class="theme-label">Yarim tun</div>
            </div>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Tipografiya</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Shrift o'lchami</div>
              <div class="setting-desc">Xabarlar matn o'lchami</div>
            </div>
            <div class="range-slider">
              <input type="range" min="11" max="19" value="13" id="cfg-fontSize" oninput="applyFontSize(this.value)" />
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Animatsiyalar</div>
              <div class="setting-desc">UI silliq o'tishlarni yoqish</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-animations" checked onchange="toggleAnimations(this.checked)"><div class="toggle-track"></div></label>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Qismlar</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Tez teglar ko'rsatish</div>
              <div class="setting-desc">Input ostidagi tezkor amalar</div>
            </div>
            <label class="toggle"><input type="checkbox" id="cfg-quickTags" checked onchange="toggleQuickTags(this.checked)"><div class="toggle-track"></div></label>
          </div>
        </div>
      </div>

      <!-- Model -->
      <div class="tab-panel" id="st-model">
        <div class="settings-group">
          <div class="settings-group-label">Model sozlamalari</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Temperatura</div>
              <div class="setting-desc">Yuqori = ijodiy, past = aniqroq (0 — 2)</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
              <span id="tempVal" style="font-family:var(--font-mono);font-size:11px;color:var(--cyan)">0.7</span>
              <div class="range-slider">
                <input type="range" min="0" max="20" value="7" id="cfg-temp" oninput="onTempChange(this.value)" />
              </div>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Max tokenlar</div>
              <div class="setting-desc">Javob uzunligi chegarasi</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
              <span id="maxTokVal" style="font-family:var(--font-mono);font-size:11px;color:var(--cyan)">2048</span>
              <div class="range-slider">
                <input type="range" min="256" max="8192" step="256" value="2048" id="cfg-maxTokens" oninput="onMaxTokChange(this.value)" />
              </div>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Suhbat konteksti</div>
              <div class="setting-desc">API ga yuborilgan oldingi xabarlar soni</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
              <span id="ctxVal" style="font-family:var(--font-mono);font-size:11px;color:var(--cyan)">20</span>
              <div class="range-slider">
                <input type="range" min="4" max="40" step="2" value="20" id="cfg-context" oninput="onCtxChange(this.value)" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Account -->
      <div class="tab-panel" id="st-account">
        <div class="settings-group">
          <div class="settings-group-label">Profil</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Foydalanuvchi ismi</div>
              <div class="setting-desc">Salomlashishda ko'rsatiladi</div>
            </div>
            <input type="text" id="cfg-userName" value="Foydalanuvchi"
              style="background:var(--bg-hover);border:1px solid var(--br-subtle);color:var(--txt-100);padding:5px 9px;border-radius:var(--r-sm);font-size:12px;outline:none;width:130px;"
              onchange="onUserNameChange(this.value)" />
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Reja</div>
              <div class="setting-desc">Joriy tarif rejasi</div>
            </div>
            <span class="badge badge-cyan">Pro</span>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">🔑 Groq API kaliti</div>
          <div class="setting-desc" style="margin-bottom:8px;font-size:11px">
            <a href="https://console.groq.com/keys" target="_blank" style="color:var(--cyan)">console.groq.com</a> dan bepul oling. Kalit faqat brauzeringizda saqlanadi.
          </div>
          <input type="password" class="settings-input" id="cfg-apiKey" placeholder="gsk-xxxxxxxxxxxxxxxxxxxxxxxx" />
          <button class="modal-action-btn" onclick="saveApiKey()">Saqlash va tekshirish</button>
          <div id="apiKeyStatus" style="margin-top:7px;font-size:11.5px;font-family:var(--font-mono)"></div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Ma'lumotlar</div>
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Barcha suhbatlarni o'chirish</div>
              <div class="setting-desc">Bu amalni qaytarib bo'lmaydi</div>
            </div>
            <button class="modal-danger-btn" onclick="clearAllChats()">O'chirish</button>
          </div>
        </div>
      </div>

      <!-- Export tab -->
      <div class="tab-panel" id="st-export">
        <div class="settings-group">
          <div class="settings-group-label">Joriy suhbatni eksport qilish</div>
          <div class="setting-desc" style="margin-bottom:12px;font-size:12px;color:var(--txt-70)">
            Suhbatingizni turli formatlarda yuklab oling.
          </div>
          <div class="export-btn-row">
            <button class="export-btn" onclick="doExport('json')">
              <span>📦</span> JSON
            </button>
            <button class="export-btn" onclick="doExport('md')">
              <span>📝</span> Markdown
            </button>
            <button class="export-btn" onclick="doExport('txt')">
              <span>📄</span> Matn
            </button>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Barcha suhbatlarni eksport qilish</div>
          <div class="setting-desc" style="margin-bottom:12px;font-size:12px;color:var(--txt-70)">
            Barcha suhbatlar bitta JSON faylda.
          </div>
          <button class="export-btn" onclick="exportAllChats()">
            <span>📦</span> Barcha suhbatlar (JSON)
          </button>
        </div>
        <div class="settings-group">
          <div class="settings-group-label">Import</div>
          <div class="setting-desc" style="margin-bottom:8px;font-size:12px;color:var(--txt-70)">
            Oldin eksport qilingan JSON faylni import qilish.
          </div>
          <input type="file" id="importInput" accept=".json" hidden onchange="importChats(this)" />
          <button class="export-btn" onclick="document.getElementById('importInput').click()">
            <span>📥</span> JSON import
          </button>
        </div>
      </div>

    </div><!-- /modal-body -->
  </div>
</div>

<!-- ══════════════════════════════ SEARCH MODAL ══════════════════════════════ -->
<div class="search-modal-overlay" id="searchModal" onclick="overlayClose(event,'searchModal')">
  <div class="search-box">
    <div class="search-row">
      <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="color:var(--txt-40);flex-shrink:0">
        <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M10 10L13 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      <input type="text" placeholder="Suhbatlar va amallarni qidiring..." id="globalSearchInput" oninput="handleGlobalSearch(this.value)" />
      <span class="kbd">ESC</span>
    </div>
    <div class="search-results-list" id="searchResultsList">
      <!-- injected by JS -->
    </div>
    <div class="search-footer">
      <span class="kbd">↑↓</span> <span style="font-size:10.5px;color:var(--txt-40)">Tanlash</span>
      &nbsp;
      <span class="kbd">↵</span> <span style="font-size:10.5px;color:var(--txt-40)">Ochish</span>
      &nbsp;
      <span class="kbd">ESC</span> <span style="font-size:10.5px;color:var(--txt-40)">Yopish</span>
    </div>
  </div>
</div>

<!-- ══════════════════════════════ SHORTCUTS MODAL ══════════════════════════════ -->
<div class="modal-overlay" id="shortcutsModal" onclick="overlayClose(event,'shortcutsModal')">
  <div class="modal" style="max-width:460px">
    <div class="modal-header">
      <span class="modal-title">⌨️ Klaviatura yorliqlari</span>
      <button class="modal-close-btn" onclick="closeModal('shortcutsModal')">✕</button>
    </div>
    <div class="modal-body">
      <div id="shortcutsList">
        <!-- injected by JS -->
      </div>
    </div>
  </div>
</div>

<!-- Toast stack -->
<div class="toast-stack" id="toastStack"></div>

<!-- ══════════════════════════════ JAVASCRIPT ══════════════════════════════ -->
<script>
/* ══════════════════════════════════════════════════════
   §A  APPLICATION STATE
══════════════════════════════════════════════════════ */
const APP = {
  // Settings (persistent via localStorage)
  settings: {
    apiKey:       '',
    model:        'llama-3.3-70b-versatile',
    temperature:  0.7,
    maxTokens:    2048,
    contextLen:   20,
    systemPrompt: 'Sen Somo AI — O\'zbekistondagi eng aqlli AI yordamchisan. Foydalanuvchilarga dasturlash, ta\'lim va boshqa sohalarda O\'zbek tilida yordam berasan.',
    userName:     'Foydalanuvchi',
    theme:        'dark',
    enterSend:    true,
    showTyping:   true,
    saveHistory:  true,
    soundNotif:   false,
    autoTitle:    true,
    fontSize:     13,
    animations:   true,
    quickTags:    true,
  },

  // Runtime state
  chats:          {},    // { id: { title, messages[], createdAt, model } }
  chatOrder:      [],    // ordered list of chat IDs
  currentChatId:  null,
  isGenerating:   false,
  tokenCount:     0,
  totalTokenLimit:8000,
  abortController:null,

  // Models metadata
  MODELS: {
    'llama-3.3-70b-versatile': { icon:'🦙', label:'Llama 3.3 70B', desc:'Kuchli · Groq' },
    'llama-3.1-8b-instant':    { icon:'⚡', label:'Llama 3.1 8B',  desc:'Eng tez · Groq' },
    'mixtral-8x7b-32768':      { icon:'🔀', label:'Mixtral 8x7B',  desc:'MoE · Groq' },
    'gemma2-9b-it':            { icon:'💎', label:'Gemma 2 9B',    desc:'Google · Groq' },
  },
};

/* ══════════════════════════════════════════════════════
   §B  PERSISTENCE
══════════════════════════════════════════════════════ */
function persistSave() {
  try {
    localStorage.setItem('somoai_settings', JSON.stringify(APP.settings));
    if (APP.settings.saveHistory) {
      localStorage.setItem('somoai_chats', JSON.stringify(APP.chats));
      localStorage.setItem('somoai_order', JSON.stringify(APP.chatOrder));
    }
  } catch(e) { /* quota exceeded */ }
}

function persistLoad() {
  try {
    const s = localStorage.getItem('somoai_settings');
    if (s) Object.assign(APP.settings, JSON.parse(s));

    const c = localStorage.getItem('somoai_chats');
    const o = localStorage.getItem('somoai_order');
    if (c) APP.chats     = JSON.parse(c);
    if (o) APP.chatOrder = JSON.parse(o);
  } catch(e) { /* corrupt data */ }
}

/* ══════════════════════════════════════════════════════
   §C  SETTINGS HELPERS
══════════════════════════════════════════════════════ */
function cfg(key, value) {
  APP.settings[key] = value;
  persistSave();
}

function applySettingsToUI() {
  // API key
  const keyEl = document.getElementById('cfg-apiKey');
  if (keyEl && APP.settings.apiKey) keyEl.value = APP.settings.apiKey;

  // Checkboxes
  const boolKeys = ['enterSend','showTyping','saveHistory','soundNotif','autoTitle','animations','quickTags'];
  boolKeys.forEach(k => {
    const el = document.getElementById('cfg-' + k);
    if (el) el.checked = APP.settings[k];
  });

  // System prompt
  const sp = document.getElementById('cfg-systemPrompt');
  if (sp) sp.value = APP.settings.systemPrompt;

  // User name
  const un = document.getElementById('cfg-userName');
  if (un) un.value = APP.settings.userName;

  // Sliders
  const t = document.getElementById('cfg-temp');
  if (t) t.value = APP.settings.temperature * 10;
  document.getElementById('tempVal').textContent = APP.settings.temperature.toFixed(1);

  const mt = document.getElementById('cfg-maxTokens');
  if (mt) mt.value = APP.settings.maxTokens;
  document.getElementById('maxTokVal').textContent = APP.settings.maxTokens;

  const ctx = document.getElementById('cfg-context');
  if (ctx) ctx.value = APP.settings.contextLen;
  document.getElementById('ctxVal').textContent = APP.settings.contextLen;

  const fs = document.getElementById('cfg-fontSize');
  if (fs) fs.value = APP.settings.fontSize;

  // Theme
  applyTheme(APP.settings.theme, false);

  // Profile
  updateProfileDisplay();
  updateWelcomeGreeting();
  updateModelInfo();
  toggleQuickTags(APP.settings.quickTags);

  // API banner
  if (!APP.settings.apiKey) {
    document.getElementById('apiBanner').classList.add('visible');
  }
}

function updateProfileDisplay() {
  const name = APP.settings.userName || 'Foydalanuvchi';
  const el = document.getElementById('profileName');
  if (el) el.textContent = name;
  const av = document.getElementById('profileAvatar');
  if (av) av.textContent = name.charAt(0).toUpperCase();
}

function updateWelcomeGreeting() {
  const h = new Date().getHours();
  let greet = 'Salom';
  if (h >= 5 && h < 12)      greet = 'Xayrli tong';
  else if (h >= 12 && h < 17) greet = 'Xayrli kun';
  else if (h >= 17 && h < 21) greet = 'Xayrli kech';
  else                         greet = 'Yaxshi tunlar';
  const el = document.getElementById('welcomeTitle');
  if (el) el.textContent = `${greet}, ${APP.settings.userName}! 👋`;
}

function updateModelInfo() {
  const m = APP.MODELS[APP.settings.model];
  if (!m) return;
  const el = document.getElementById('welcomeModelInfo');
  if (el) el.textContent = `${m.icon} ${m.label} — ${m.desc} · ${APP.settings.apiKey ? '🟢 API tayyor' : '⚠️ API kaliti kerak'}`;
}

/* ══════════════════════════════════════════════════════
   §D  THEME & APPEARANCE
══════════════════════════════════════════════════════ */
function applyTheme(theme, toast = true) {
  APP.settings.theme = theme;
  document.documentElement.setAttribute('data-theme', theme === 'midnight' ? 'dark' : theme);
  if (theme === 'midnight') {
    document.documentElement.style.setProperty('--bg-base', '#020008');
    document.documentElement.style.setProperty('--bg-sidebar', '#010005');
  } else {
    document.documentElement.style.removeProperty('--bg-base');
    document.documentElement.style.removeProperty('--bg-sidebar');
  }
  document.querySelectorAll('.theme-opt').forEach(o => o.classList.remove('active'));
  const opt = document.getElementById('to-' + theme);
  if (opt) opt.classList.add('active');
  persistSave();
  if (toast) showToast(theme === 'light' ? '☀️' : theme === 'midnight' ? '🌌' : '🌙', 'Mavzu o\'zgartirildi', 'info');
}

function toggleTheme() {
  const themes = ['dark', 'light', 'midnight'];
  const idx = themes.indexOf(APP.settings.theme);
  applyTheme(themes[(idx + 1) % 3]);
}

function applyFontSize(val) {
  document.querySelectorAll('.msg-bubble').forEach(b => b.style.fontSize = val + 'px');
  APP.settings.fontSize = parseInt(val);
  persistSave();
}

function toggleAnimations(on) {
  const v = on ? '0.24s cubic-bezier(0.4,0,0.2,1)' : '0s';
  document.documentElement.style.setProperty('--t-med', v);
  document.documentElement.style.setProperty('--t-slow', on ? '0.42s cubic-bezier(0.4,0,0.2,1)' : '0s');
  cfg('animations', on);
}

function toggleQuickTags(on) {
  const el = document.querySelector('.quick-tags');
  if (el) el.style.display = on ? 'flex' : 'none';
  cfg('quickTags', on);
}

/* ══════════════════════════════════════════════════════
   §E  SIDEBAR
══════════════════════════════════════════════════════ */
let sidebarCollapsed = false;

function toggleSidebar() {
  sidebarCollapsed = !sidebarCollapsed;
  document.getElementById('sidebar').classList.toggle('collapsed', sidebarCollapsed);
  document.getElementById('main').classList.toggle('sb-collapsed', sidebarCollapsed);
}

function openMobileSB() {
  document.getElementById('sidebar').classList.add('mobile-open');
  document.getElementById('sbOverlay').classList.add('active');
}

function closeMobileSB() {
  document.getElementById('sidebar').classList.remove('mobile-open');
  document.getElementById('sbOverlay').classList.remove('active');
}

/* ══════════════════════════════════════════════════════
   §F  CHAT MANAGEMENT
══════════════════════════════════════════════════════ */
function genChatId() {
  return 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
}

function createChat(title = 'Yangi suhbat') {
  const id = genChatId();
  APP.chats[id] = {
    title:     title,
    messages:  [],
    createdAt: new Date().toISOString(),
    model:     APP.settings.model,
  };
  APP.chatOrder.unshift(id);
  APP.currentChatId = id;
  persistSave();
  renderChatList();
  return id;
}

function goHome() {
  APP.currentChatId = null;
  showWelcomeScreen();
  document.getElementById('topbarTitle').textContent = 'Yangi suhbat';
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  closeMobileSB();
}

function startNewChat() {
  goHome();
  showToast('✨', 'Yangi suhbat boshlandi', 'info');
}

function loadChat(id) {
  if (!APP.chats[id]) return;
  APP.currentChatId = id;
  const chat = APP.chats[id];
  document.getElementById('topbarTitle').textContent = chat.title;
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  const item = document.getElementById('ci-' + id);
  if (item) item.classList.add('active');

  // Show messages
  document.getElementById('welcomeScreen').style.display = 'none';
  const wrap = document.getElementById('msgsWrap');
  wrap.innerHTML = '';
  wrap.classList.add('visible');

  chat.messages.forEach(msg => renderMessage(msg.role, msg.content, false));
  scrollBottom(false);
  closeMobileSB();
}

function deleteChat(id) {
  if (!APP.chats[id]) return;
  delete APP.chats[id];
  APP.chatOrder = APP.chatOrder.filter(x => x !== id);
  if (APP.currentChatId === id) goHome();
  renderChatList();
  persistSave();
  showToast('🗑️', 'Suhbat o\'chirildi', 'info');
}

function clearAllChats() {
  if (!confirm('Barcha suhbatlarni o\'chirishni tasdiqlaysizmi?')) return;
  APP.chats = {};
  APP.chatOrder = [];
  APP.currentChatId = null;
  renderChatList();
  goHome();
  persistSave();
  showToast('🗑️', 'Barcha suhbatlar o\'chirildi', 'info');
  closeModal('settingsModal');
}

function addMessageToChat(id, role, content) {
  if (!APP.chats[id]) return;
  APP.chats[id].messages.push({ role, content, ts: Date.now() });
  // Auto-title
  const msgs = APP.chats[id].messages;
  if (APP.settings.autoTitle && msgs.length === 1 && role === 'user') {
    const title = content.length > 44 ? content.slice(0, 44) + '…' : content;
    APP.chats[id].title = title;
    const el = document.getElementById('ci-title-' + id);
    if (el) el.textContent = title;
    document.getElementById('topbarTitle').textContent = title;
  }
  persistSave();
}

/* ══════════════════════════════════════════════════════
   §G  CHAT LIST RENDERING
══════════════════════════════════════════════════════ */
function renderChatList(query = '') {
  const list = document.getElementById('chatList');
  if (!APP.chatOrder.length) {
    list.innerHTML = '<div style="padding:18px;text-align:center;color:var(--txt-40);font-size:12px;font-family:var(--font-mono)">Hali suhbatlar yo\'q</div>';
    return;
  }

  // Group by date
  const now   = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yday  = new Date(today - 86400000);
  const week  = new Date(today - 6 * 86400000);

  const groups = { today: [], yesterday: [], week: [], older: [] };

  APP.chatOrder.forEach(id => {
    const chat = APP.chats[id];
    if (!chat) return;
    if (query && !chat.title.toLowerCase().includes(query.toLowerCase())) return;
    const d = new Date(chat.createdAt);
    if (d >= today)      groups.today.push(id);
    else if (d >= yday)  groups.yesterday.push(id);
    else if (d >= week)  groups.week.push(id);
    else                 groups.older.push(id);
  });

  const labels = { today: 'Bugun', yesterday: 'Kecha', week: 'Bu hafta', older: 'Oldingi' };
  let html = '';

  Object.entries(groups).forEach(([key, ids]) => {
    if (!ids.length) return;
    html += `<div class="sb-section-label">${labels[key]}</div>`;
    ids.forEach(id => {
      const chat  = APP.chats[id];
      const isAct = id === APP.currentChatId;
      const ts    = formatRelTime(new Date(chat.createdAt));
      const icon  = getChatIcon(chat.title);
      html += `
        <div class="chat-item${isAct ? ' active' : ''}" id="ci-${id}" onclick="loadChat('${id}')">
          <div class="ci-icon">${icon}</div>
          <div class="ci-meta">
            <div class="ci-title" id="ci-title-${id}">${esc(chat.title)}</div>
            <div class="ci-time">${ts}</div>
          </div>
          <div class="ci-actions">
            <button class="ci-del-btn" onclick="event.stopPropagation();deleteChat('${id}')" title="O'chirish">🗑</button>
          </div>
        </div>`;
    });
  });

  list.innerHTML = html || '<div style="padding:18px;text-align:center;color:var(--txt-40);font-size:12px">Hech narsa topilmadi</div>';
}

function filterChatList(q) {
  renderChatList(q);
}

function getChatIcon(title) {
  const t = title.toLowerCase();
  if (t.includes('python') || t.includes('kod') || t.includes('code')) return '🐍';
  if (t.includes('javascript') || t.includes('react') || t.includes('js')) return '⚛️';
  if (t.includes('sql') || t.includes('base') || t.includes('data')) return '🗄️';
  if (t.includes('ingliz') || t.includes('english') || t.includes('til')) return '🌐';
  if (t.includes('resume') || t.includes('cv') || t.includes('ish')) return '📄';
  if (t.includes('machine') || t.includes('ai') || t.includes('ml')) return '🧠';
  if (t.includes('telegram') || t.includes('bot')) return '🤖';
  if (t.includes('css') || t.includes('dizayn') || t.includes('design')) return '🎨';
  return '💬';
}

function formatRelTime(d) {
  const diff = Date.now() - d.getTime();
  const min  = Math.floor(diff / 60000);
  const hr   = Math.floor(diff / 3600000);
  if (min < 1)   return 'Hozir';
  if (min < 60)  return `${min} daqiqa oldin`;
  if (hr  < 24)  return `${hr} soat oldin`;
  return d.toLocaleDateString('uz-UZ', { month:'short', day:'numeric' });
}

/* ══════════════════════════════════════════════════════
   §H  MESSAGE RENDERING
══════════════════════════════════════════════════════ */
function renderMessage(role, content, animate = true) {
  const wrap = document.getElementById('msgsWrap');
  wrap.classList.add('visible');
  document.getElementById('welcomeScreen').style.display = 'none';

  const mid  = 'msg_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
  const isUser = role === 'user';
  const ts   = new Date().toLocaleTimeString('uz-UZ', { hour:'2-digit', minute:'2-digit' });
  const name = APP.settings.userName || 'Siz';
  const isErr = content.startsWith('⚠️') || content.startsWith('🔑');

  const html = `
    <div class="msg-group" id="${mid}">
      <div class="msg-row ${isUser ? 'user' : 'ai'}">
        <div class="msg-avatar ${isUser ? 'user' : 'ai'}">${isUser ? name.charAt(0).toUpperCase() : 'AI'}</div>
        <div class="msg-body">
          <div class="msg-sender">${isUser ? name : 'Somo AI'} <span class="msg-time">${ts}</span></div>
          <div class="msg-bubble${isErr ? ' error-bubble' : ''}" id="b-${mid}" style="font-size:${APP.settings.fontSize}px">${parseMd(content)}</div>
          <div class="msg-actions">
            ${isUser ? `
              <button class="msg-act-btn" onclick="copyBubble('b-${mid}')" title="Nusxalash">📋</button>
              <button class="msg-act-btn" onclick="editToInput('b-${mid}')" title="Tahrirlash">✏️</button>
            ` : `
              <button class="msg-act-btn" onclick="copyBubble('b-${mid}')" title="Nusxalash">📋</button>
              <button class="msg-act-btn" onclick="regenerate()" title="Qayta yaratish">🔄</button>
              <button class="msg-act-btn" onclick="reactMsg('${mid}',true)" title="Yoqdi">👍</button>
              <button class="msg-act-btn" onclick="reactMsg('${mid}',false)" title="Yoqmadi">👎</button>
            `}
          </div>
        </div>
      </div>
    </div>`;

  wrap.insertAdjacentHTML('beforeend', html);

  // Bind copy buttons in code blocks
  const el = document.getElementById(mid);
  if (el) {
    el.querySelectorAll('.copy-code-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const pre  = btn.closest('pre');
        const code = pre && pre.querySelector('code');
        if (code) copyText(code.textContent);
      });
    });
  }

  if (animate) scrollBottom(true);
  return mid;
}

/* Markdown parser (lightweight) */
function parseMd(text) {
  let s = text
    // Fenced code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
      const l = lang || 'code';
      return `<pre><div class="code-header"><span class="code-lang-badge">${l}</span><button class="copy-code-btn">Nusxalash</button></div><code>${escHtml(code.trim())}</code></pre>`;
    })
    // Inline code
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
    // H2
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    // H3
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    // H4
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    // Blockquote
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Unordered list items
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // Ordered list items
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Double newline → paragraph
    .replace(/\n\n/g, '</p><p>')
    // Single newline → <br>
    .replace(/\n/g, '<br>');

  // Wrap consecutive <li> in <ul>
  s = s.replace(/(<li>.*?<\/li>(\s*<br>)*)+/gs, m => `<ul>${m.replace(/<br>/g,'')}</ul>`);

  // Wrap in paragraph if no block elements
  if (!/<(pre|ul|ol|h[2-4]|blockquote)/.test(s)) {
    s = '<p>' + s + '</p>';
  }

  return s;
}

function escHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function esc(t) { return String(t).replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

/* ══════════════════════════════════════════════════════
   §I  GROQ API — STREAMING
══════════════════════════════════════════════════════ */
async function callGroqStream(messages, onChunk, onDone, onErr) {
  if (!APP.settings.apiKey) {
    onErr('🔑 API kaliti kiritilmagan. Iltimos, Sozlamalar → Hisob bo\'limida Groq API kalitingizni kiriting.');
    return;
  }

  const apiMessages = [
    { role: 'system', content: APP.settings.systemPrompt },
    ...messages.slice(-APP.settings.contextLen),
  ];

  APP.abortController = new AbortController();

  try {
    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      signal: APP.abortController.signal,
      headers: {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${APP.settings.apiKey}`,
      },
      body: JSON.stringify({
        model:        APP.settings.model,
        messages:     apiMessages,
        temperature:  APP.settings.temperature,
        max_tokens:   APP.settings.maxTokens,
        stream:       true,
      }),
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      const msg = errData?.error?.message || resp.statusText;
      if (resp.status === 401 || resp.status === 403) {
        onErr('🔑 API kaliti noto\'g\'ri yoki muddati o\'tgan. Iltimos, Sozlamalar → Hisob bo\'limida yangilab ko\'ring.');
      } else if (resp.status === 429) {
        onErr('⚠️ So\'rovlar chegarasiga yetdingiz. Bir oz kuting va qayta urinib ko\'ring.');
      } else {
        onErr('⚠️ API xatosi: ' + msg);
      }
      return;
    }

    const reader = resp.body.getReader();
    const dec    = new TextDecoder();
    let   full   = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = dec.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (!line.startsWith('data:')) continue;
        const data = line.slice(5).trim();
        if (data === '[DONE]') { onDone(full); return; }
        try {
          const json  = JSON.parse(data);
          const delta = json.choices?.[0]?.delta?.content || '';
          if (delta) {
            full += delta;
            onChunk(delta, full);
          }
          // Count tokens (estimate)
          if (json.usage) {
            updateTokenCount(json.usage.completion_tokens || 0);
          }
        } catch { /* skip malformed */ }
      }
    }
    onDone(full);

  } catch(err) {
    if (err.name === 'AbortError') {
      onDone(''); // stopped by user
    } else {
      onErr('⚠️ Tarmoq xatosi: ' + err.message);
    }
  }
}

/* ══════════════════════════════════════════════════════
   §J  SEND / RECEIVE
══════════════════════════════════════════════════════ */
async function sendMessage() {
  const input  = document.getElementById('chatInput');
  const text   = input.value.trim();
  if (!text || APP.isGenerating) return;

  // Clear input
  input.value = '';
  input.style.height = 'auto';
  updateCharCount(0);

  // Ensure we have a chat
  if (!APP.currentChatId) {
    const shortTitle = text.length > 42 ? text.slice(0, 42) + '…' : text;
    createChat(shortTitle);
    renderChatList();
    document.getElementById('topbarTitle').textContent = shortTitle;
  }

  const chatId = APP.currentChatId;

  // Render & save user message
  addMessageToChat(chatId, 'user', text);
  renderMessage('user', text);

  // Gen start
  APP.isGenerating = true;
  setGenUI(true);
  if (APP.settings.showTyping) showTyping();

  // Build messages for API
  const apiMsgs = APP.chats[chatId].messages.map(m => ({ role: m.role === 'ai' ? 'assistant' : m.role, content: m.content }));

  // Create empty AI bubble
  hideTyping();
  const mid   = renderMessage('ai', '', false);
  const bubble = document.getElementById('b-' + mid);
  let   full   = '';

  await callGroqStream(
    apiMsgs,
    // onChunk
    (delta, accumulated) => {
      full = accumulated;
      bubble.innerHTML = parseMd(accumulated) + '<span class="stream-cursor"></span>';
      scrollBottom(false);
    },
    // onDone
    (finalText) => {
      if (finalText) {
        bubble.innerHTML = parseMd(finalText);
        addMessageToChat(chatId, 'ai', finalText);
        estimateAndUpdateTokens(finalText);
      } else if (!full) {
        // stopped early, nothing
        if (bubble.innerHTML.includes('stream-cursor')) {
          bubble.innerHTML = bubble.innerHTML.replace('<span class="stream-cursor"></span>', '');
        }
      }
      APP.isGenerating = false;
      setGenUI(false);
      scrollBottom(true);
      if (APP.settings.soundNotif) playNotifSound();
    },
    // onErr
    (errMsg) => {
      bubble.innerHTML = parseMd(errMsg);
      bubble.classList.add('error-bubble');
      addMessageToChat(chatId, 'ai', errMsg);
      APP.isGenerating = false;
      setGenUI(false);
      hideTyping();
      showToast('⚠️', 'Xato yuz berdi', 'error');
    }
  );
}

function sendSuggestion(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

function stopGeneration() {
  if (APP.abortController) APP.abortController.abort();
  APP.isGenerating = false;
  setGenUI(false);
  hideTyping();
  showToast('⏹', 'To\'xtatildi', 'info');
}

function setGenUI(on) {
  document.getElementById('sendBtn').disabled = on;
  document.getElementById('stopBtn').classList.toggle('visible', on);
}

function showTyping() {
  document.getElementById('typingWrap').classList.add('visible');
  scrollBottom(true);
}
function hideTyping() {
  document.getElementById('typingWrap').classList.remove('visible');
}

function showWelcomeScreen() {
  document.getElementById('welcomeScreen').style.display = 'flex';
  document.getElementById('msgsWrap').classList.remove('visible');
  document.getElementById('msgsWrap').innerHTML = '';
  document.getElementById('typingWrap').classList.remove('visible');
}

function scrollBottom(smooth = true) {
  const a = document.getElementById('chatArea');
  if (smooth) a.scrollTo({ top: a.scrollHeight, behavior: 'smooth' });
  else        a.scrollTop = a.scrollHeight;
}

function regenerate() {
  if (!APP.currentChatId) return;
  const msgs = APP.chats[APP.currentChatId].messages;
  const lastUser = [...msgs].reverse().find(m => m.role === 'user');
  if (!lastUser) return;

  // Remove last AI message
  const wrap = document.getElementById('msgsWrap');
  const groups = wrap.querySelectorAll('.msg-group');
  if (groups.length > 0) {
    const last = groups[groups.length - 1];
    if (last.querySelector('.msg-avatar.ai')) {
      last.remove();
      APP.chats[APP.currentChatId].messages = msgs.filter((m,i) => !(m.role === 'ai' && i === msgs.length - 1));
    }
  }
  sendSuggestion(lastUser.content);
  showToast('🔄', 'Qayta yaratilmoqda...', 'info');
}

/* ══════════════════════════════════════════════════════
   §K  INPUT HANDLING
══════════════════════════════════════════════════════ */
function onInputChange(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  updateCharCount(el.value.length);
}

function onInputKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey && APP.settings.enterSend) {
    e.preventDefault();
    sendMessage();
  }
}

function updateCharCount(n) {
  const el = document.getElementById('charCount');
  el.textContent = n + ' / 4000';
  el.className   = 'char-count' + (n > 3500 ? ' danger' : n > 3000 ? ' warn' : '');
}

/* ══════════════════════════════════════════════════════
   §L  MESSAGE ACTIONS
══════════════════════════════════════════════════════ */
function copyBubble(bubbleId) {
  const el = document.getElementById(bubbleId);
  if (el) {
    copyText(el.textContent);
    showToast('📋', 'Nusxalandi!', 'success');
  }
}

function editToInput(bubbleId) {
  const el = document.getElementById(bubbleId);
  if (!el) return;
  const input = document.getElementById('chatInput');
  input.value = el.textContent;
  onInputChange(input);
  input.focus();
  showToast('✏️', 'Tahrirlash uchun tayyorlandi', 'info');
}

function reactMsg(mid, liked) {
  showToast(liked ? '👍' : '👎', liked ? 'Fikr uchun rahmat!' : 'E\'tiborga olamiz', 'info');
}

function copyText(t) {
  navigator.clipboard.writeText(t).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = t;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  });
}

/* ══════════════════════════════════════════════════════
   §M  FILE UPLOAD
══════════════════════════════════════════════════════ */
function triggerFile()  { document.getElementById('fileInput').click(); }
function triggerImage() { document.getElementById('imageInput').click(); }

function handleFileInput(inp) {
  Array.from(inp.files).forEach(f => addAttChip('📄 ' + f.name));
  inp.value = '';
}

function handleImageInput(inp) {
  Array.from(inp.files).forEach(f => addAttChip('🖼️ ' + f.name));
  inp.value = '';
}

function addAttChip(label) {
  const list = document.getElementById('attList');
  const chip = document.createElement('div');
  chip.className = 'att-chip';
  chip.innerHTML = `${esc(label)} <span class="att-remove" onclick="this.parentElement.remove()">✕</span>`;
  list.appendChild(chip);
  showToast('📎', label.slice(0, 30), 'success');
}

// Drag-drop
document.addEventListener('dragover', e => {
  e.preventDefault();
  document.getElementById('dropOverlay').classList.add('active');
});
document.addEventListener('dragleave', e => {
  if (!e.relatedTarget) document.getElementById('dropOverlay').classList.remove('active');
});
document.addEventListener('drop', e => {
  e.preventDefault();
  document.getElementById('dropOverlay').classList.remove('active');
  Array.from(e.dataTransfer.files).forEach(f =>
    addAttChip((f.type.startsWith('image/') ? '🖼️ ' : '📄 ') + f.name)
  );
});

/* ══════════════════════════════════════════════════════
   §N  MODEL SELECTOR
══════════════════════════════════════════════════════ */
function toggleModelDD() {
  const sel = document.getElementById('modelSelector');
  const dd  = document.getElementById('modelDD');
  sel.classList.toggle('open');
  dd.classList.toggle('open');
}

function pickModel(el) {
  const model = el.dataset.model;
  APP.settings.model = model;
  document.getElementById('modelDisplayName').textContent = model.split('-').slice(0,3).join('-');
  document.querySelectorAll('.model-opt').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  toggleModelDD();
  persistSave();
  updateModelInfo();
  showToast('🤖', 'Model: ' + (APP.MODELS[model]?.label || model), 'success');
}

document.addEventListener('click', e => {
  const wrap = document.querySelector('.model-wrap');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('modelSelector').classList.remove('open');
    document.getElementById('modelDD').classList.remove('open');
  }
});

/* ══════════════════════════════════════════════════════
   §O  SETTINGS MODAL
══════════════════════════════════════════════════════ */
function openSettings() {
  document.getElementById('settingsModal').classList.add('open');
}

function openProfileTab() {
  openSettings();
  switchSettingsTab('account', document.querySelector('.modal-tab:nth-child(4)'));
}

function openExportModal() {
  openSettings();
  switchSettingsTab('export', document.querySelector('.modal-tab:nth-child(5)'));
}

function switchSettingsTab(tabId, btn) {
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const panel = document.getElementById('st-' + tabId);
  if (panel) panel.classList.add('active');
}

function onUserNameChange(val) {
  cfg('userName', val);
  updateProfileDisplay();
  updateWelcomeGreeting();
}

function onTempChange(val) {
  const t = (val / 10).toFixed(1);
  APP.settings.temperature = parseFloat(t);
  document.getElementById('tempVal').textContent = t;
  persistSave();
}

function onMaxTokChange(val) {
  APP.settings.maxTokens = parseInt(val);
  document.getElementById('maxTokVal').textContent = val;
  persistSave();
}

function onCtxChange(val) {
  APP.settings.contextLen = parseInt(val);
  document.getElementById('ctxVal').textContent = val;
  persistSave();
}

function saveApiKey() {
  const val = document.getElementById('cfg-apiKey').value.trim();
  if (!val) {
    document.getElementById('apiKeyStatus').innerHTML = '<span style="color:var(--pink)">⚠️ API kalitini kiriting</span>';
    return;
  }
  APP.settings.apiKey = val;
  persistSave();
  document.getElementById('apiKeyStatus').innerHTML = '<span style="color:var(--green)">✅ API kaliti saqlandi</span>';
  document.getElementById('apiBanner').classList.remove('visible');
  updateModelInfo();
  showToast('🔑', 'API kaliti saqlandi', 'success');
}

function dismissBanner() {
  document.getElementById('apiBanner').classList.remove('visible');
}

/* ══════════════════════════════════════════════════════
   §P  SEARCH MODAL
══════════════════════════════════════════════════════ */
function openSearch() {
  document.getElementById('searchModal').classList.add('open');
  populateSearchResults('');
  setTimeout(() => document.getElementById('globalSearchInput').focus(), 80);
}

function handleGlobalSearch(q) {
  populateSearchResults(q);
}

function populateSearchResults(q) {
  const container = document.getElementById('searchResultsList');
  let html = '';

  // Chats section
  const matchingChats = APP.chatOrder.filter(id => {
    const chat = APP.chats[id];
    return chat && (!q || chat.title.toLowerCase().includes(q.toLowerCase()));
  }).slice(0, 6);

  if (matchingChats.length) {
    html += '<div class="search-section-label">Suhbatlar</div>';
    matchingChats.forEach(id => {
      const chat = APP.chats[id];
      html += `
        <div class="search-result-item" onclick="loadChat('${id}');closeModal('searchModal')">
          <div class="sri-icon">${getChatIcon(chat.title)}</div>
          <div class="sri-text">
            <div class="sri-title">${esc(chat.title)}</div>
            <div class="sri-desc">${chat.messages.length} xabar · ${formatRelTime(new Date(chat.createdAt))}</div>
          </div>
        </div>`;
    });
  }

  // Quick actions
  html += '<div class="search-section-label">Tezkor amallar</div>';
  const actions = [
    ['✨', 'Yangi suhbat boshlash', "startNewChat();closeModal('searchModal')"],
    ['⚙️', 'Sozlamalarni ochish',  "openSettings();closeModal('searchModal')"],
    ['💾', 'Suhbatni eksport qilish', "exportCurrentChat();closeModal('searchModal')"],
    ['🗑️', 'Barcha suhbatlarni o\'chirish', "clearAllChats()"],
  ];
  actions.forEach(([icon, label, fn]) => {
    html += `
      <div class="search-result-item" onclick="${fn}">
        <div class="sri-icon">${icon}</div>
        <div class="sri-text"><div class="sri-title">${label}</div></div>
      </div>`;
  });

  container.innerHTML = html;
}

/* ══════════════════════════════════════════════════════
   §Q  KEYBOARD SHORTCUTS MODAL
══════════════════════════════════════════════════════ */
function openShortcuts() {
  const shortcuts = [
    ['Yangi suhbat',              'Ctrl', 'N'],
    ['Qidirish',                  'Ctrl', 'K'],
    ['Sozlamalar',                'Ctrl', ','],
    ['Sidebarni yig\'ish',        'Ctrl', 'B'],
    ['Mavzu almashtirish',        'Ctrl', 'T'],
    ['Eksport qilish',            'Ctrl', 'E'],
    ['Xabar yuborish',            'Enter'],
    ['Yangi qator',               'Shift', 'Enter'],
    ['Generatsiyani to\'xtatish', 'Escape'],
    ['Modalni yopish',            'Escape'],
  ];
  const list = document.getElementById('shortcutsList');
  list.innerHTML = shortcuts.map(([name, ...keys]) => `
    <div class="shortcut-row">
      <span class="shortcut-name">${name}</span>
      <div class="shortcut-keys">${keys.map(k => `<span class="kbd">${k}</span>`).join('')}</div>
    </div>`).join('');
  document.getElementById('shortcutsModal').classList.add('open');
}

/* ══════════════════════════════════════════════════════
   §R  EXPORT / IMPORT
══════════════════════════════════════════════════════ */
function exportCurrentChat() {
  const id = APP.currentChatId;
  if (!id || !APP.chats[id]) {
    showToast('⚠️', 'Eksport uchun suhbat tanlanmagan', 'error');
    return;
  }
  doExport('json');
}

function doExport(fmt) {
  const id   = APP.currentChatId;
  const chat = id && APP.chats[id];
  if (!chat || !chat.messages.length) {
    showToast('⚠️', 'Eksport uchun xabarlar yo\'q', 'error');
    return;
  }

  const title = chat.title.slice(0, 24).replace(/[^a-zA-Z0-9\u0400-\u04FF ]/g, '');
  let content, mime, ext;

  if (fmt === 'json') {
    content = JSON.stringify({
      title: chat.title,
      model: chat.model || APP.settings.model,
      createdAt: chat.createdAt,
      exportedAt: new Date().toISOString(),
      messages: chat.messages,
    }, null, 2);
    mime = 'application/json';
    ext  = 'json';
  } else if (fmt === 'md') {
    const lines = [`# ${chat.title}\n`, `**Model:** ${chat.model || APP.settings.model}  `, `**Sana:** ${new Date(chat.createdAt).toLocaleString('uz-UZ')}\n\n---\n`];
    chat.messages.forEach(m => {
      const who = m.role === 'user' ? `**${APP.settings.userName}:**` : '**Somo AI:**';
      lines.push(`${who}\n\n${m.content}\n\n---\n`);
    });
    content = lines.join('\n');
    mime    = 'text/markdown';
    ext     = 'md';
  } else {
    const lines = [`=== ${chat.title} ===\n`];
    chat.messages.forEach(m => {
      const who = m.role === 'user' ? APP.settings.userName : 'Somo AI';
      lines.push(`[${who}]\n${m.content}\n`);
    });
    content = lines.join('\n');
    mime    = 'text/plain';
    ext     = 'txt';
  }

  const blob = new Blob([content], { type: mime });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `somo-ai-${title}-${Date.now()}.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('💾', `${ext.toUpperCase()} eksport qilindi`, 'success');
}

function exportAllChats() {
  if (!APP.chatOrder.length) {
    showToast('⚠️', 'Suhbatlar yo\'q', 'error');
    return;
  }
  const data = {
    exportedAt: new Date().toISOString(),
    chats: APP.chatOrder.map(id => APP.chats[id]).filter(Boolean),
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `somo-ai-all-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('💾', `${APP.chatOrder.length} ta suhbat eksport qilindi`, 'success');
}

function importChats(inp) {
  const file = inp.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      let imported = 0;
      if (data.chats && Array.isArray(data.chats)) {
        data.chats.forEach(chat => {
          const id = genChatId();
          APP.chats[id] = { ...chat, createdAt: chat.createdAt || new Date().toISOString() };
          APP.chatOrder.push(id);
          imported++;
        });
      } else if (data.messages) {
        // Single chat export
        const id = genChatId();
        APP.chats[id] = { title: data.title || 'Imported', messages: data.messages, createdAt: data.createdAt || new Date().toISOString(), model: data.model };
        APP.chatOrder.unshift(id);
        imported = 1;
      }
      renderChatList();
      persistSave();
      showToast('📥', `${imported} ta suhbat import qilindi`, 'success');
    } catch {
      showToast('⚠️', 'Fayl noto\'g\'ri formatda', 'error');
    }
  };
  reader.readAsText(file);
  inp.value = '';
}

/* ══════════════════════════════════════════════════════
   §S  TOKEN COUNTER
══════════════════════════════════════════════════════ */
function updateTokenCount(add) {
  APP.tokenCount = Math.min(APP.tokenCount + add, APP.totalTokenLimit);
  document.getElementById('tokenLabel').textContent =
    APP.tokenCount.toLocaleString() + ' / ' + APP.totalTokenLimit.toLocaleString();
  const pct = (APP.tokenCount / APP.totalTokenLimit) * 100;
  document.getElementById('tokenFill').style.width = Math.min(pct, 100) + '%';
}

function estimateAndUpdateTokens(text) {
  const est = Math.ceil(text.length / 4);
  updateTokenCount(est);
}

/* ══════════════════════════════════════════════════════
   §T  TOAST
══════════════════════════════════════════════════════ */
function showToast(icon, msg, type = 'info') {
  const stack = document.getElementById('toastStack');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span class="toast-ico">${icon}</span>${esc(msg)}`;
  stack.appendChild(t);
  setTimeout(() => t.remove(), 3300);
}

/* ══════════════════════════════════════════════════════
   §U  MODAL HELPERS
══════════════════════════════════════════════════════ */
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function overlayClose(e, id) {
  if (e.target === e.currentTarget) closeModal(id);
}

/* ══════════════════════════════════════════════════════
   §V  KEYBOARD SHORTCUTS
══════════════════════════════════════════════════════ */
document.addEventListener('keydown', e => {
  const ctrl = e.ctrlKey || e.metaKey;
  if (ctrl && e.key === 'k') { e.preventDefault(); openSearch(); }
  if (ctrl && e.key === 'n') { e.preventDefault(); startNewChat(); }
  if (ctrl && e.key === 'b') { e.preventDefault(); toggleSidebar(); }
  if (ctrl && e.key === 't') { e.preventDefault(); toggleTheme(); }
  if (ctrl && e.key === ',') { e.preventDefault(); openSettings(); }
  if (ctrl && e.key === 'e') { e.preventDefault(); exportCurrentChat(); }
  if (e.key === 'Escape') {
    ['settingsModal','searchModal','shortcutsModal'].forEach(closeModal);
    if (APP.isGenerating) stopGeneration();
  }
});

/* ══════════════════════════════════════════════════════
   §W  SOUND NOTIFICATION
══════════════════════════════════════════════════════ */
function playNotifSound() {
  try {
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
    osc.start();
    osc.stop(ctx.currentTime + 0.2);
  } catch { /* AudioContext not available */ }
}

/* ══════════════════════════════════════════════════════
   §X  DEMO MODE (no API key)
══════════════════════════════════════════════════════ */
const DEMO_RESPONSES = {
  default: `Salom! Men Somo AI — Groq platformasida ishlaydigan aqlli yordamchiman. 🤖

Hozir demo rejimida ishlamoqdaman. To'liq funksionallik uchun **Sozlamalar → Hisob** bo'limida Groq API kalitingizni kiriting.

Groq API kalitini [console.groq.com](https://console.groq.com/keys) dan **bepul** olishingiz mumkin!`,

  python: `Python dasturlash tili bo'yicha yordam beraman! 🐍

Mana oddiy misollar:

**1. Salomlashish:**
\`\`\`python
def greet(name):
    print(f"Salom, {name}!")

greet("Somo")
\`\`\`

**2. Ro'yxatlar bilan ishlash:**
\`\`\`python
mevalar = ["olma", "nok", "uzum"]
for meva in mevalar:
    print(meva.upper())
\`\`\`

API kalitini kiritgandan so'ng men siz bilan chuqurroq mavzularni muhokama qila olaman!`,

  sql: `SQL va NoSQL farqlari haqida qisqacha:

**SQL (Relatsion):**
- Jadval asosida, qat'iy sxema
- ACID kafolati
- JOIN so'rovlar
- Misol: PostgreSQL, MySQL

**NoSQL:**
- Hujjat, kalit-qiymat, grafik
- Moslashuvchan sxema
- Katta hajm uchun ideal
- Misol: MongoDB, Redis

Demo rejimda cheklangan javoblar. API kaliti uchun Sozlamalarga o'ting!`,
};

function getDemoResponse(text) {
  const t = text.toLowerCase();
  if (t.includes('python') || t.includes('kod') || t.includes('dastur')) return DEMO_RESPONSES.python;
  if (t.includes('sql') || t.includes('baza') || t.includes('nosql'))    return DEMO_RESPONSES.sql;
  return DEMO_RESPONSES.default;
}

/* Override callGroqStream in demo mode */
const _origCallGroq = callGroqStream;
async function callGroqStream(messages, onChunk, onDone, onErr) {
  if (!APP.settings.apiKey) {
    // Demo mode: simulate streaming
    const lastMsg = messages[messages.length - 1]?.content || '';
    const resp    = getDemoResponse(lastMsg);
    const words   = resp.split(' ');
    let full = '';
    for (let i = 0; i < words.length; i++) {
      full += (i ? ' ' : '') + words[i];
      onChunk(words[i] + (i < words.length - 1 ? ' ' : ''), full);
      await new Promise(r => setTimeout(r, 18 + Math.random() * 14));
      if (!APP.isGenerating) { onDone(full); return; }
    }
    onDone(full);
    return;
  }
  return _origCallGroq(messages, onChunk, onDone, onErr);
}

/* ══════════════════════════════════════════════════════
   §Y  INITIALISATION
══════════════════════════════════════════════════════ */
function init() {
  persistLoad();
  applySettingsToUI();
  renderChatList();

  // Stagger animate chips
  document.querySelectorAll('.chip').forEach((chip, i) => {
    chip.style.opacity = '0';
    chip.style.transform = 'translateY(12px)';
    setTimeout(() => {
      chip.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
      chip.style.opacity    = '1';
      chip.style.transform  = 'translateY(0)';
    }, 80 + i * 65);
  });

  // Model display name
  if (APP.settings.model) {
    const el = document.getElementById('modelDisplayName');
    if (el) el.textContent = APP.settings.model.split('-').slice(0, 3).join('-');
    // Mark correct model as selected
    document.querySelectorAll('.model-opt').forEach(o => {
      o.classList.toggle('selected', o.dataset.model === APP.settings.model);
    });
  }

  // Auto-load last chat
  if (APP.chatOrder.length && APP.settings.saveHistory) {
    // Just render list, don't auto-open
  }

  console.log('%c🤖 Somo AI v2.0', 'font-size:22px;color:#00e5ff;font-weight:bold;font-family:monospace');
  console.log('%cStreamlit + HTML Merged Edition — 3000+ LOC', 'color:#7c3aed;font-size:12px');
  console.log('%cGroq API: ' + (APP.settings.apiKey ? '✅ Kiritilgan' : '⚠️ Kiritilmagan'), 'font-size:11px');
}

// Boot
document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>

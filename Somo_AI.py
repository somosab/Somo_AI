# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║           SOMO AI  —  Ijodiy AI Yordamchi  v4.1                 ║
# ║                                                                  ║
# ║  Muallif  : Usmonov Sodiq  (@Somo_AI)                           ║
# ║  Model    : Groq Llama-3.3-70B  +  Google Gemini 2.0 Flash      ║
# ║  Stack    : Python · Streamlit · Dual-API Streaming             ║
# ║  Versiya  : 4.1  |  2026  (Mobile-Perfect Edition)              ║
# ║                                                                  ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  YANGILIKLAR v4.1:                                               ║
# ║  ✦ Telefon uchun mukammal dizayn (320px–430px)                   ║
# ║  ✦ Safe-area insets (notch / home bar phones)                    ║
# ║  ✦ 44px minimum touch targets barcha tugmalar                    ║
# ║  ✦ Mobil header: ultra-compact, scroll-proof                     ║
# ║  ✦ Sticky input: viewport-lock, iOS Safari fix                   ║
# ║  ✦ Welcome cards: 2-col mobile, 3-col desktop                    ║
# ║  ✦ Larger base font on mobile (16px) — no zoom on focus          ║
# ║  ✦ Chips horizontal scroll, no wrap on small screens             ║
# ║  ✦ Copy button: full-width on mobile                             ║
# ║  ✦ Reduced motion support (prefers-reduced-motion)               ║
# ║  ✦ Smooth overscroll + momentum scrolling (iOS)                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import google.generativeai as genai
from groq import Groq
import time, re, random

# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
GROQ_MODEL     = "llama-3.3-70b-versatile"
GEMINI_MODEL   = "gemini-2.0-flash"
GROQ_MAX_TOK   = 4096
GEMINI_MAX_TOK = 4096
GROQ_TEMP      = 0.85
GEMINI_TEMP    = 0.95
COOLDOWN_LONG  = 90

# ═══════════════════════════════════════════════════════════════════
#  MARKDOWN → HTML  (LaTeX-safe, full-featured)
# ═══════════════════════════════════════════════════════════════════
def md_to_html(text: str) -> str:
    saved = {}

    def save(m):
        k = f"__BLK{len(saved)}__"
        saved[k] = m.group(0)
        return k

    text = re.sub(r'\$\$.+?\$\$', save, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$', save, text)

    def fmt_code(m):
        lang = m.group(1) or ""
        body = m.group(2).strip()
        return f'<pre><code class="lang-{lang}">{body}</code></pre>'
    text = re.sub(r'```(\w*)\n?(.*?)```', fmt_code, text, flags=re.DOTALL)

    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)

    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$',  r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',   r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',    r'<h1>\1</h1>', text, flags=re.MULTILINE)

    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*',       r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)

    text = re.sub(r'^---+$', r'<hr class="md-hr">', text, flags=re.MULTILINE)
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    def ul_block(m):
        items = re.findall(r'^[\-\*•] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    text = re.sub(r'(^[\-\*•] .+\n?)+', ul_block, text, flags=re.MULTILINE)

    def ol_block(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', ol_block, text, flags=re.MULTILINE)

    def tbl(m):
        rows = [r.strip() for r in m.group(0).strip().split('\n') if '|' in r]
        if not rows: return m.group(0)
        out = '<table>'
        for i, row in enumerate(rows):
            if re.match(r'^\|[\-\| :]+\|$', row): continue
            tag = 'th' if i == 0 else 'td'
            cells = [c.strip() for c in row.strip('|').split('|')]
            out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        return out + '</table>'
    text = re.sub(r'(\|.+\|\n?)+', tbl, text)

    paras = text.split('\n\n')
    result = []
    for p in paras:
        p = p.strip()
        if not p: continue
        if re.match(r'^<(h[1-4]|ul|ol|pre|blockquote|table|hr)', p):
            result.append(p)
        else:
            p = p.replace('\n', '<br>')
            result.append(f'<p>{p}</p>')
    text = '\n'.join(result)

    for k, v in saved.items():
        text = text.replace(k, v)
    return text


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def get_time() -> str:
    return time.strftime("%H:%M")

def get_date() -> str:
    return time.strftime("%d.%m.%Y")

def wc(text: str) -> int:
    return len(text.split())

def is_rate_err(e: str) -> bool:
    keys = ["429", "rate_limit", "quota", "rate limit",
            "Resource exhausted", "RESOURCE_EXHAUSTED",
            "too many requests", "Too Many Requests"]
    return any(k.lower() in e.lower() for k in keys)

def get_greeting() -> tuple:
    h = int(time.strftime("%H"))
    if 5  <= h < 12: return "🌅", "Xayrli tong"
    if 12 <= h < 17: return "☀️",  "Xayrli kun"
    if 17 <= h < 21: return "🌆", "Xayrli kech"
    return "🌙", "Tungi ilhom"


# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
RAND_PROMPTS = [
    "Yolg'izlik haqida she'r yoz",
    "Vaqt haqida qisqa hikoya yoz",
    "Orzular haqida nutq yoz",
    "Kitob o'qishning foydasi haqida esse yoz",
    "Toshkent haqida she'r yoz",
    "Musiqa va hayot haqida esse",
    "Ona haqida she'r yoz",
    "Yoshlikda qilish kerak 10 ta g'oya ber",
    "Do'stlik haqida qisqa hikoya",
    "Ilm haqida she'r yoz",
    "Baxt nima — esse yoz",
    "Kelajak haqida nutq yoz",
    "Sevgi va vaqt haqida hikoya",
    "O'zbekiston tarixi haqida esse",
    "Tabiat va inson haqida she'r",
    "Bolalikning ta'mi haqida she'r",
    "Muvaffaqiyat sirlari — esse",
    "Quyosh botishi haqida she'r",
    "Hayot go'zalligi haqida esse",
    "Kitob va hayot haqida hikoya",
]

MODE_META = {
    "esse"     : {"icon": "✍️",  "label": "Esse",           "color": "#f59e0b"},
    "story"    : {"icon": "📖",  "label": "Hikoya / She'r", "color": "#ec4899"},
    "speech"   : {"icon": "🎤",  "label": "Nutq",            "color": "#8b5cf6"},
    "ideas"    : {"icon": "💡",  "label": "G'oyalar",        "color": "#0ea5e9"},
    "translate": {"icon": "🌍",  "label": "Tarjima",         "color": "#10b981"},
    "summary"  : {"icon": "📋",  "label": "Xulosa",          "color": "#6366f1"},
    "general"  : {"icon": "✦",   "label": "Somo AI",         "color": "#f59e0b"},
}


# ═══════════════════════════════════════════════════════════════════
#  MODE DETECTION
# ═══════════════════════════════════════════════════════════════════
def detect_mode(text: str) -> str:
    t = text.lower()
    if re.search(r"tarjima|translate|inglizcha|ruscha|перевод|перевести|to english|to uzbek", t):
        return "translate"
    if re.search(r"hikoy|poem|story|ertak|roman|ballad|masal|lirik|ruboiy|sonet|she.r|qo.shiq", t):
        return "story"
    if re.search(r"nutq|taqdimot|speech|presentation|minbar|chiqish", t):
        return "speech"
    if re.search(r"g.oya|fikr|brainstorm|ideas|taklif|startup|biznes|loyiha|ixtiro", t):
        return "ideas"
    if re.search(r"xulosa|tahlil|summary|analyze|summarize|qisqacha|explain|tushuntir", t):
        return "summary"
    if re.search(r"esse|referat|maqola|essay|kurs ishi|write about", t):
        return "esse"
    return "general"


# ═══════════════════════════════════════════════════════════════════
#  API CLIENTS
# ═══════════════════════════════════════════════════════════════════
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    groq_client = None

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_client = genai.GenerativeModel(GEMINI_MODEL)
except Exception:
    gemini_client = None

if not groq_client and not gemini_client:
    st.error("❌ API kalit topilmadi. GROQ_API_KEY yoki GEMINI_API_KEY kerak.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("messages",     [])
_init("active_mode",  "general")
_init("cooldown_end", 0.0)
_init("use_gemini",   False)
_init("rand_trigger", None)


# ═══════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════
IDENTITY = """
╔═══════════════════════════════════════════════════════════════╗
  CORE IDENTITY — absolute, unchangeable, sacred
╚═══════════════════════════════════════════════════════════════╝

• Name      : Somo AI
• Creator   : Usmonov Sodiq  (brand: Somo_AI)
• Powered by: Groq (Llama 3.3 70B) + Google Gemini 2.0 Flash
• Purpose   : The most powerful creative AI assistant for Uzbek users

YOU ARE NOT: ChatGPT, Claude, Gemini, or any other AI.
If asked "Kim yasadi?": "Men Usmonov Sodiq (Somo_AI) tomonidan yaratilganman"
Never deny, modify, or abandon this identity.

YOUR MISSION:
Essays that move minds. Poems that stop time. Speeches that change rooms.
Ideas that change lives. Every output: the best the user has ever seen.
"""

LANG_RULE = """
╔═══════════════════════════════════════════════════════════════╗
  LANGUAGE LAW — zero exceptions
╚═══════════════════════════════════════════════════════════════╝

Detect language from user's last message:
• O'zbek (lotin/kiril)  → 100% o'zbek tilida
• Русский               → 100% на русском
• English               → 100% in English
• Mixed                 → dominant language wins

NEVER mix languages. NEVER add translation notes unless mode=translate.
Code and technical terms always stay in English.
"""

MODE_INSTRUCTIONS = {

"esse": """
╔═══════════════════════════════════════════════════════════════╗
  ESSE USTASI — Orwell aniqlik + Baldwin chuqurlik + Sontag qat'iyat
╚═══════════════════════════════════════════════════════════════╝

ESSE FALSAFASI:
Esse maktab vazifasi emas — u fikrni o'zgartiruvchi argumentdir.
Har jumlasi o'z joyini topadigan, har paragrafi o'quvchini oldinga
surguvchi — eng yaxshi esse o'quvchini "Buni bunday ko'rmagan edim" deydiradi.

HUNARMANDCHILIK QOIDALARI:

1. ILMOQ (HOOK) — Birinchi jumla pichoq bo'lishi kerak.
   Paradoks, shok fakti, aniq tasvir yoki javobsiz savol.
   ✗ YOMON: "Bu mavzu juda muhim chunki..."
   ✓ YAXSHI: "1969-yilda oyga qadam qo'yilgan kuni, Samarqandda
   bir bola maktabga kelmadi — chunki uning oyoq kiyimi yo'q edi."

2. TEZIS = ARGUMENT, NOT FAKT — munozarali bo'lishi shart.
   ✗ YOMON: "Texnologiya hayotimizni o'zgartirdi."
   ✓ YAXSHI: "Texnologiya bizni erkinlashtirdi deb o'ylaymiz,
   aslida esa yangi qafaslar qurdi."

3. TANA PARAGRAFI:
   Mavzu jumla → Aniq misol → Tahlil → Tezisga aloqa

4. QARSHI FIKR — eng kuchli e'tirozni tan olib, mantiq bilan yeng.

5. O'TISHLAR — ko'rinmas, mexanik emas.

6. XOTIMA — hech qachon xulosa qilma. KUCHAYTIR.

MAJBURIY STRUKTURA:
## Kirish
[Hook] [Kontekst] [Tezis]

## [Birinchi Argument]
## [Ikkinchi Argument]
## [Uchinchi va Eng Kuchli Argument]
## Xulosa

UZUNLIK: 550–900 so'z.
""",

"story": """
╔═══════════════════════════════════════════════════════════════╗
  IJOD USTASI — Navoiy + Oripov + Cho'lpon + Neruda ruhi
╚═══════════════════════════════════════════════════════════════╝

ADABIY E'TIQOD:
San'at tushuntirmaydi — U OCHIB BERADI.

HUNARMANDCHILIK TEXNIKALARI (har asarda kamida 3):
1. Volta          — 2/3 nuqtada butun ma'noni o'zgartiradigan burilish
2. Sinestetika    — "U uning sukunatini tatidi"
3. Ob'ektiv korrelyat — "g'amgin" dema; bo'sh stulni ko'rsat
4. In medias res  — harakat o'rtasidan boshlash
5. Anafora        — imdga aylangan takror
6. Aniq tasvir    — "qush" emas → "iyul-yorilgan o'rik shoxidagi popishak"

HIKOYALAR: O'rta harakatdan och. Dialog xarakterni ochadi.
SHE'RLAR: Sarlavha ma'no qo'shadi. 1-qator: aniq tasvir.

MUTLAQ TAQIQLAR:
✗ "Bu bir hikoya..." bilan boshlamaslik
✗ His-tuyg'uni ayt emas — tasvirla
✗ Kuchsiz tugama
""",

"speech": """
╔═══════════════════════════════════════════════════════════════╗
  NUTQ USTASI — MLK + Churchill + Obama + O'zbek notiqlik san'ati
╚═══════════════════════════════════════════════════════════════╝

MAJBURIY STRUKTURA:
🎯 ILMOQ — Birinchi 15 so'z vaqtni to'xtatishi kerak
🤝 BOG'LANISH — Gapirish huquqini qozon
💡 BIRINCHI ASOSIY FIKR
🔥 IKKINCHI ASOSIY FIKR
⚡ UCHINCHI ASOSIY FIKR — CHO'QQI
🚀 CHAQIRIQ — Aniq, mumkin, darhol
🔔 YOPISH — aks-sado va oshib ket

RITORIK ASBOBLAR: Anafora, Trikolon, Ritorik savollar, Antiteza, Ellipsis
STANDART: To'liq matn. Ijroga tayyor.
""",

"ideas": """
╔═══════════════════════════════════════════════════════════════╗
  G'OYA USTASI — IDEO dizayn + YC instinkt + shoir tasavvur
╚═══════════════════════════════════════════════════════════════╝

MAJBURIY FORMAT:

### 💡 [Tematik Kategoriya]

**[N]. [Jasur, Esda qolarli Nom]**
*Mohiyat:* [Bir aniq jumla]
*Nima uchun ishlaydi:* [2 jumla]
*Noyoblik:* [Aniq alternativlardan nimasi farqli]
*Birinchi qadam:* [Eng aniq, bajariladigan birinchi harakat]

### 🏆 ENG YAXSHI TANLOV

QOIDALAR: Minimum 6, maksimal 12 g'oya. Kamida 2 ta kutilmagan bo'lsin.
""",

"translate": """
╔═══════════════════════════════════════════════════════════════╗
  TARJIMA USTASI — Matn emas, RUH tarjimasi
╚═══════════════════════════════════════════════════════════════╝

MAJBURIY FORMAT:

**📄 Asl matn:**
> [asl matn]

**✅ Tarjima:**
> [tarjima]

**📝 Izohlar** *(faqat kerak bo'lsa)*:
- [atama]: [qisqa izoh]
""",

"summary": """
╔═══════════════════════════════════════════════════════════════╗
  TAHLIL USTASI — Feynman soddalik + Sud aniqligi
╚═══════════════════════════════════════════════════════════════╝

MAJBURIY FORMAT:

## 🎯 Asosiy G'oya
## 🔑 Muhim Fikrlar
## 🧩 Chuqur Tahlil
## 💡 Noodatiy Insight
## ❓ Ochiq Savol
""",

"general": """
╔═══════════════════════════════════════════════════════════════╗
  SOMO AI — Eng foydali, halol va ajoyib yordamchi
╚═══════════════════════════════════════════════════════════════╝

JAVOB KALIBRLASH:
• Oddiy faktik savol → To'g'ridan-to'g'ri javob, 1-3 jumla
• Murakkab savol → Strukturali tushuntirish + misollar
• Ijodiy so'rov → To'liq ijodiy chiqish
• Hissiy → Iliq, hozir, chin
""",

}

FORMATTING_RULES = """
╔═══════════════════════════════════════════════════════════════╗
  UNIVERSAL CHIQISH QOIDALARI
╚═══════════════════════════════════════════════════════════════╝

TIPOGRAFIYA:
• **Qalin** — asosiy atamalar
• *Kursiv* — sarlavhalar, xorijiy so'zlar
• `kod` — texnik atamalar
• > blokiqtibos — to'g'ridan-to'g'ri iqtiboslar

MATEMATIK — har doim LaTeX:
• Qatorida: $ax^2 + bx + c = 0$
• Alohida: $$\\int_0^\\infty e^{-x^2}dx = \\frac{\\sqrt{\\pi}}{2}$$

SIFAT NAZORATI:
✓ Har paragraf oldinga siltayaptimi?
✓ Oxirgi jumla eng kuchlimi?
"""


def build_system_prompt(mode: str) -> str:
    instr = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["general"])
    return "\n\n".join([IDENTITY, instr, LANG_RULE, FORMATTING_RULES])


# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════
#  FONTS + KaTeX
# ═══════════════════════════════════════════════════════════════════
st.markdown(
    '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">'
    '<meta name="theme-color" content="#fdf7ee">'
    '<meta name="apple-mobile-web-app-capable" content="yes">'
    '<meta name="apple-mobile-web-app-status-bar-style" content="default">'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"'
    ' onload="renderMathInElement(document.body,{delimiters:['
    '{left:String.fromCharCode(36,36),right:String.fromCharCode(36,36),display:true},'
    '{left:String.fromCharCode(36),right:String.fromCharCode(36),display:false}]});"></script>',
    unsafe_allow_html=True
)

# ═══════════════════════════════════════════════════════════════════
#  CSS — MOBILE-PERFECT PREMIUM DESIGN v4.1
# ═══════════════════════════════════════════════════════════════════
_CSS = """

/* ═══════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════ */
:root {
  --cream      : #fdf7ee;
  --warm       : #f5ead2;
  --card       : #fffef9;
  --border     : #e8ddc8;
  --border-soft: #ede5d2;

  --amber  : #f59e0b;
  --amber-l: #fcd34d;
  --orange : #ea580c;
  --orange-l:#fb923c;

  --text   : #1a1208;
  --muted  : #6b5c42;
  --light  : #a8936e;
  --faint  : #c5b59a;

  --blue   : #3b82f6;
  --green  : #15803d;
  --red    : #dc2626;

  --fh     : 'Fraunces', Georgia, serif;
  --fb     : 'DM Sans', system-ui, -apple-system, sans-serif;

  --shadow-xs  : 0 1px 3px rgba(26,18,8,.06);
  --shadow-sm  : 0 2px 8px rgba(26,18,8,.08);
  --shadow-md  : 0 4px 18px rgba(26,18,8,.1);
  --shadow-lg  : 0 8px 32px rgba(26,18,8,.12);
  --shadow-amb : 0 4px 18px rgba(245,158,11,.28);

  --ease-spring: cubic-bezier(.34,1.56,.64,1);
  --ease-out   : cubic-bezier(.22,.68,0,1.2);
  --dur-fast   : .15s;
  --dur-mid    : .25s;
  --dur-slow   : .4s;

  /* Safe area — for notch phones */
  --sat : env(safe-area-inset-top,    0px);
  --sar : env(safe-area-inset-right,  0px);
  --sab : env(safe-area-inset-bottom, 0px);
  --sal : env(safe-area-inset-left,   0px);
}

/* ═══════════════════════════════════════════════════════════════
   GLOBAL RESET
   ═══════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html {
  /* Prevent text size inflation on orientation change */
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

html, body {
  background     : var(--cream) !important;
  margin         : 0;
  padding        : 0;
  -webkit-font-smoothing : antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
  /* iOS momentum scroll */
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: none;
}

/* Hide all streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stChatInputSuggestions"],
[data-testid="stChatInputSuggestionsContainer"] { display: none !important; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main,
.stApp { background: var(--cream) !important; }

.block-container,
[data-testid="stMainBlockContainer"] {
  padding   : 0 !important;
  max-width : 100% !important;
}

/* Scrollbar */
::-webkit-scrollbar       { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background    : var(--border);
  border-radius : 4px;
}

/* ═══════════════════════════════════════════════════════════════
   HEADER — glass morphism, sticky, safe-area aware
   ═══════════════════════════════════════════════════════════════ */
.somo-header {
  position        : sticky;
  top             : 0;
  z-index         : 900;
  background      : rgba(253,247,238,.95);
  backdrop-filter : blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
  border-bottom   : 1px solid var(--border-soft);
  box-shadow      : 0 1px 0 var(--border-soft),
                    0 2px 20px rgba(26,18,8,.05);
  /* safe area top for notch */
  padding-top     : var(--sat);
}
.somo-header-inner {
  display         : flex;
  align-items     : center;
  justify-content : space-between;
  max-width       : 860px;
  margin          : 0 auto;
  padding         : .7rem 1.25rem;
  gap             : .5rem;
}

/* Brand */
.somo-brand { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.somo-logo  {
  width           : 36px;
  height          : 36px;
  min-width       : 36px;
  border-radius   : 10px;
  background      : linear-gradient(145deg, var(--amber), var(--orange));
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-family     : var(--fh) !important;
  font-size       : 16px;
  font-weight     : 900;
  color           : #fff;
  box-shadow      : var(--shadow-amb),
                    inset 0 1px 0 rgba(255,255,255,.22);
  letter-spacing  : -.5px;
}
.somo-name {
  font-family : var(--fh) !important;
  font-size   : 1rem;
  font-weight : 900;
  color       : var(--text);
  line-height : 1;
  letter-spacing: -.3px;
}
.somo-name em {
  font-style  : italic;
  color       : var(--orange);
}
.somo-by {
  font-family    : var(--fb) !important;
  font-size      : .5rem;
  color          : var(--light);
  letter-spacing : 1px;
  text-transform : uppercase;
  margin-top     : 3px;
}

/* Right side */
.somo-hdr-right {
  display     : flex;
  align-items : center;
  gap         : 6px;
  flex-shrink : 0;
}

.somo-mode-chip {
  display         : inline-flex;
  align-items     : center;
  gap             : 4px;
  font-family     : var(--fb) !important;
  font-size       : .6rem;
  font-weight     : 600;
  padding         : .24rem .65rem;
  border-radius   : 20px;
  white-space     : nowrap;
  transition      : all var(--dur-mid) ease;
}
.somo-mode-chip.off {
  background : var(--warm);
  border     : 1.5px solid var(--border);
  color      : var(--muted);
}
.somo-mode-chip.on {
  background  : linear-gradient(135deg, var(--amber), var(--orange));
  border      : 1.5px solid transparent;
  color       : #fff;
  box-shadow  : var(--shadow-amb);
}

.somo-online {
  display     : flex;
  align-items : center;
  gap         : 5px;
  font-family : var(--fb) !important;
  font-size   : .58rem;
  color       : var(--green);
  white-space : nowrap;
}
.somo-dot {
  width           : 7px;
  height          : 7px;
  min-width       : 7px;
  border-radius   : 50%;
  background      : var(--green);
  box-shadow      : 0 0 0 0 rgba(21,128,61,.4);
  animation       : ripple 2.2s ease-in-out infinite;
}
@keyframes ripple {
  0%   { box-shadow: 0 0 0 0   rgba(21,128,61,.4); }
  70%  { box-shadow: 0 0 0 6px rgba(21,128,61,0);  }
  100% { box-shadow: 0 0 0 0   rgba(21,128,61,0);  }
}

.somo-model-pill {
  font-family    : var(--fb) !important;
  font-size      : .55rem;
  font-weight    : 600;
  color          : var(--muted);
  background     : var(--warm);
  border         : 1.5px solid var(--border);
  border-radius  : 20px;
  padding        : .2rem .65rem;
  white-space    : nowrap;
}

/* ═══════════════════════════════════════════════════════════════
   LAYOUT WRAPPER
   ═══════════════════════════════════════════════════════════════ */
.somo-wrap {
  max-width  : 860px;
  margin     : 0 auto;
  padding    : 1.75rem 1.25rem;
  /* Reserve space for fixed input + safe area */
  padding-bottom : calc(7rem + var(--sab));
  min-height     : calc(100vh - 60px);
}

/* ═══════════════════════════════════════════════════════════════
   WELCOME SCREEN
   ═══════════════════════════════════════════════════════════════ */
.somo-welcome {
  text-align  : center;
  padding     : 1.8rem 0 1.5rem;
}

.somo-eyebrow {
  display         : inline-flex;
  align-items     : center;
  gap             : 7px;
  background      : linear-gradient(135deg, var(--amber), var(--orange));
  color           : #fff;
  font-family     : var(--fb) !important;
  font-size       : .6rem;
  font-weight     : 700;
  letter-spacing  : 1.4px;
  text-transform  : uppercase;
  padding         : .3rem 1rem;
  border-radius   : 30px;
  margin-bottom   : 1.2rem;
  box-shadow      : var(--shadow-amb);
  animation       : popIn .55s var(--ease-spring) both;
}
@keyframes popIn {
  from { opacity: 0; transform: scale(.72) translateY(6px); }
  to   { opacity: 1; transform: scale(1)   translateY(0);   }
}

.somo-headline {
  font-family    : var(--fh) !important;
  font-size      : clamp(2rem, 8vw, 3.2rem);
  font-weight    : 900;
  color          : var(--text);
  line-height    : 1.08;
  letter-spacing : -.5px;
  margin-bottom  : .5rem;
  animation      : riseUp .5s ease-out .08s both;
}
.somo-headline em {
  font-style              : italic;
  background              : linear-gradient(135deg, var(--amber), var(--orange));
  -webkit-background-clip : text;
  -webkit-text-fill-color : transparent;
  background-clip         : text;
}
@keyframes riseUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0);    }
}

.somo-subtext {
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  color         : var(--muted);
  line-height   : 1.75;
  max-width     : 420px;
  margin        : 0 auto 1.8rem;
  animation     : riseUp .5s ease-out .15s both;
}

/* Feature cards grid */
.somo-cards {
  display               : grid;
  grid-template-columns : repeat(3, 1fr);
  gap                   : .6rem;
  max-width             : 560px;
  margin                : 0 auto 1.5rem;
  animation             : riseUp .5s ease-out .22s both;
}
.somo-card {
  background    : var(--card);
  border        : 1.5px solid var(--border-soft);
  border-radius : 16px;
  padding       : 1rem .75rem .85rem;
  text-align    : center;
  cursor        : default;
  transition    : border-color var(--dur-mid) ease,
                  transform    var(--dur-mid) var(--ease-spring),
                  box-shadow   var(--dur-mid) ease;
  position      : relative;
  overflow      : hidden;
  /* Touch-friendly */
  -webkit-tap-highlight-color: transparent;
}
.somo-card::before {
  content    : '';
  position   : absolute;
  inset      : 0;
  background : linear-gradient(135deg, rgba(245,158,11,.05), rgba(234,88,12,.04));
  opacity    : 0;
  transition : opacity var(--dur-mid) ease;
}
@media (hover: hover) {
  .somo-card:hover {
    transform    : translateY(-4px);
    border-color : var(--amber);
    box-shadow   : 0 8px 28px rgba(0,0,0,.1);
  }
  .somo-card:hover::before { opacity: 1; }
}
/* Touch active state for mobile */
.somo-card:active {
  transform    : scale(.97);
  border-color : var(--amber);
}
.somo-card-icon {
  font-size     : 1.5rem;
  display       : block;
  margin-bottom : .4rem;
  filter        : drop-shadow(0 2px 5px rgba(0,0,0,.1));
}
.somo-card-name {
  font-family   : var(--fb) !important;
  font-size     : .72rem;
  font-weight   : 700;
  color         : var(--text);
  margin-bottom : .18rem;
}
.somo-card-hint {
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--light);
  font-style  : italic;
  line-height : 1.4;
}

/* Prompt chips — horizontal scroll on mobile */
.somo-chips-wrap {
  width     : 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom : 2px;
  margin-bottom  : 1.4rem;
  animation      : riseUp .5s ease-out .3s both;
}
.somo-chips-wrap::-webkit-scrollbar { display: none; }
.somo-chips {
  display     : flex;
  flex-wrap   : nowrap;
  gap         : .42rem;
  padding     : .1rem .25rem;
  width       : max-content;
  margin      : 0 auto;
}
.somo-chip {
  background    : var(--warm);
  border        : 1.5px solid var(--border-soft);
  border-radius : 20px;
  padding       : .32rem .85rem;
  font-family   : var(--fb) !important;
  font-size     : .68rem;
  color         : var(--muted);
  white-space   : nowrap;
  /* 44px min touch target height */
  display       : inline-flex;
  align-items   : center;
  min-height    : 36px;
  cursor        : default;
  -webkit-tap-highlight-color: transparent;
  transition    : all var(--dur-fast) ease;
}
@media (hover: hover) {
  .somo-chip:hover {
    border-color : var(--amber);
    color        : var(--orange);
    background   : rgba(245,158,11,.07);
  }
}
.somo-chip:active {
  border-color : var(--amber);
  color        : var(--orange);
}

/* ═══════════════════════════════════════════════════════════════
   CHAT AREA — stats bar
   ═══════════════════════════════════════════════════════════════ */
.somo-stats {
  display       : flex;
  align-items   : center;
  gap           : .75rem;
  padding       : .5rem 0;
  font-family   : var(--fb) !important;
  font-size     : .64rem;
  color         : var(--faint);
  border-bottom : 1px solid var(--border-soft);
  margin-bottom : .75rem;
  overflow-x    : auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  white-space   : nowrap;
}
.somo-stats::-webkit-scrollbar { display: none; }
.somo-stat { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
.somo-stat b { color: var(--muted); font-weight: 600; }

.somo-divider {
  text-align  : center;
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--faint);
  margin      : .75rem 0;
  position    : relative;
  letter-spacing: .5px;
}
.somo-divider::before, .somo-divider::after {
  content    : '';
  position   : absolute;
  top        : 50%;
  width      : calc(50% - 55px);
  height     : 1px;
  background : var(--border-soft);
}
.somo-divider::before { left: 0; }
.somo-divider::after  { right: 0; }

/* ═══════════════════════════════════════════════════════════════
   MESSAGES
   ═══════════════════════════════════════════════════════════════ */
.somo-msg-user {
  display         : flex;
  justify-content : flex-end;
  margin-bottom   : .9rem;
  animation       : msgIn .2s ease-out;
}
.somo-msg-ai {
  display       : flex;
  align-items   : flex-start;
  gap           : 10px;
  margin-bottom : 1.6rem;
  animation     : msgIn .2s ease-out;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(7px); }
  to   { opacity: 1; transform: translateY(0);   }
}

/* Avatar */
.somo-av {
  width           : 30px;
  height          : 30px;
  min-width       : 30px;
  border-radius   : 9px;
  background      : linear-gradient(145deg, var(--amber), var(--orange));
  color           : #fff;
  font-family     : var(--fh) !important;
  font-size       : 13px;
  font-weight     : 900;
  display         : flex;
  align-items     : center;
  justify-content : center;
  flex-shrink     : 0;
  margin-top      : 2px;
  box-shadow      : 0 2px 10px rgba(245,158,11,.3),
                    inset 0 1px 0 rgba(255,255,255,.2);
}

/* Message body */
.somo-msg-user .somo-body { max-width: 78%; }
.somo-msg-ai  .somo-body  { flex: 1; max-width: 100%; min-width: 0; }

.somo-sender {
  font-family    : var(--fb) !important;
  font-size      : .53rem;
  color          : var(--faint);
  margin-bottom  : .2rem;
  letter-spacing : .6px;
  text-transform : uppercase;
}

/* Bubble: user */
.somo-bubble-user {
  background    : linear-gradient(135deg, #eff6ff, #e0effe);
  border        : 1.5px solid #bfdbfe;
  border-radius : 18px 5px 18px 18px;
  padding       : .65rem 1rem;
  font-family   : var(--fb) !important;
  /* 16px prevents iOS auto-zoom on focus */
  font-size     : 16px;
  line-height   : 1.65;
  color         : var(--text);
  word-break    : break-word;
  display       : inline-block;
  box-shadow    : 0 1px 4px rgba(59,130,246,.08);
}

/* Bubble: ai */
.somo-bubble-ai {
  background  : transparent;
  padding     : .1rem 0;
  font-family : var(--fb) !important;
  font-size   : 15px;
  line-height : 1.82;
  color       : var(--text);
  word-break  : break-word;
  overflow-wrap: break-word;
}

/* Mode label */
.somo-mode-label {
  display        : inline-flex;
  align-items    : center;
  gap            : 5px;
  font-family    : var(--fb) !important;
  font-size      : .57rem;
  font-weight    : 700;
  letter-spacing : .9px;
  text-transform : uppercase;
  color          : var(--amber);
  margin-bottom  : .4rem;
  padding        : .14rem .5rem;
  background     : rgba(245,158,11,.08);
  border         : 1px solid rgba(245,158,11,.2);
  border-radius  : 6px;
}

/* Meta row: timestamp + word count + copy */
.somo-meta-row {
  display     : flex;
  align-items : center;
  gap         : 6px;
  margin-top  : .4rem;
  flex-wrap   : wrap;
}
.somo-ts {
  font-family : var(--fb) !important;
  font-size   : .55rem;
  color       : var(--faint);
}
.somo-wc {
  display       : inline-flex;
  align-items   : center;
  gap           : 3px;
  font-family   : var(--fb) !important;
  font-size     : .55rem;
  color         : var(--faint);
  background    : var(--warm);
  border        : 1px solid var(--border-soft);
  padding       : .08rem .38rem;
  border-radius : 6px;
}
.somo-copy {
  display       : inline-flex;
  align-items   : center;
  justify-content: center;
  gap           : 4px;
  font-family   : var(--fb) !important;
  font-size     : .6rem;
  font-weight   : 500;
  color         : var(--muted);
  background    : var(--warm);
  border        : 1px solid var(--border-soft);
  border-radius : 8px;
  padding       : .22rem .65rem;
  cursor        : pointer;
  /* Min touch target */
  min-height    : 32px;
  min-width     : 72px;
  transition    : all var(--dur-fast) ease;
  user-select   : none;
  -webkit-tap-highlight-color: transparent;
}
@media (hover: hover) {
  .somo-copy:hover {
    background   : var(--border);
    color        : var(--text);
    border-color : var(--border);
  }
}
.somo-copy:active { transform: scale(.93); }
.somo-msg-user .somo-ts { display: block; text-align: right; margin-top: .26rem; }

/* ═══════════════════════════════════════════════════════════════
   RICH CONTENT INSIDE AI BUBBLE
   ═══════════════════════════════════════════════════════════════ */
.somo-bubble-ai strong { color: var(--orange); font-weight: 700; }
.somo-bubble-ai em     { color: var(--muted); }
.somo-bubble-ai del    { color: var(--faint); text-decoration: line-through; }

.somo-bubble-ai h1,
.somo-bubble-ai h2,
.somo-bubble-ai h3,
.somo-bubble-ai h4 {
  font-family  : var(--fh) !important;
  font-weight  : 700;
  color        : var(--text);
  margin       : .85rem 0 .28rem;
  line-height  : 1.25;
}
.somo-bubble-ai h1 { font-size: 1.15rem; }
.somo-bubble-ai h2 { font-size: 1.02rem; }
.somo-bubble-ai h3 { font-size: .94rem;  }
.somo-bubble-ai h4 { font-size: .88rem;  }

.somo-bubble-ai code {
  background    : rgba(245,158,11,.1);
  border        : 1px solid rgba(245,158,11,.2);
  padding       : .1rem .34rem;
  border-radius : 5px;
  font-size     : .78rem;
  color         : var(--orange);
  font-family   : 'Courier New', monospace !important;
  word-break    : break-all;
}

.somo-bubble-ai pre {
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 12px;
  padding       : .9rem 1rem;
  overflow-x    : auto;
  -webkit-overflow-scrolling: touch;
  margin        : .65rem 0;
}
.somo-bubble-ai pre code {
  background : none;
  border     : none;
  padding    : 0;
  color      : var(--green);
  font-size  : .75rem;
  word-break : normal;
}

.somo-bubble-ai ul,
.somo-bubble-ai ol  { padding-left: 1.25rem; margin: .3rem 0; }
.somo-bubble-ai li  { margin-bottom: .25rem; }

.somo-bubble-ai blockquote {
  border-left   : 3px solid var(--amber);
  background    : linear-gradient(135deg,
                    rgba(245,158,11,.05),
                    rgba(234,88,12,.03));
  padding       : .5rem .9rem;
  border-radius : 0 10px 10px 0;
  color         : var(--muted);
  margin        : .5rem 0;
  font-style    : italic;
}

.somo-bubble-ai table {
  border-collapse : collapse;
  width           : 100%;
  margin          : .6rem 0;
  font-size       : .78rem;
  display         : block;
  overflow-x      : auto;
  -webkit-overflow-scrolling: touch;
}
.somo-bubble-ai th {
  background  : var(--warm);
  border      : 1.5px solid var(--border);
  padding     : .4rem .7rem;
  font-weight : 700;
  color       : var(--orange);
  text-align  : left;
  white-space : nowrap;
}
.somo-bubble-ai td {
  border   : 1px solid var(--border-soft);
  padding  : .35rem .7rem;
  white-space: nowrap;
}
.somo-bubble-ai tr:nth-child(even) td {
  background : rgba(245,158,11,.025);
}

.somo-bubble-ai hr.md-hr {
  border     : none;
  border-top : 1.5px solid var(--border-soft);
  margin     : .75rem 0;
}
.somo-bubble-ai p { margin: .3rem 0; }

/* ═══════════════════════════════════════════════════════════════
   TYPING CURSOR
   ═══════════════════════════════════════════════════════════════ */
.somo-cur {
  display        : inline-block;
  width          : 2.5px;
  height         : .9em;
  background     : linear-gradient(to bottom, var(--amber), var(--orange));
  border-radius  : 2px;
  margin-left    : 2px;
  vertical-align : middle;
  animation      : blink .75s step-end infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* ═══════════════════════════════════════════════════════════════
   COOLDOWN BANNER
   ═══════════════════════════════════════════════════════════════ */
.somo-cd-wrap {
  max-width  : 860px;
  margin     : 0 auto;
  padding    : .5rem 1.25rem 0;
}
.somo-cd-box {
  display       : flex;
  align-items   : center;
  gap           : 12px;
  background    : linear-gradient(135deg, #fffbeb, #fff7d6);
  border        : 2px solid var(--amber);
  border-radius : 16px;
  padding       : .9rem 1.2rem;
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  color         : #92400e;
  box-shadow    : 0 4px 20px rgba(245,158,11,.14);
}
.somo-cd-icon { font-size: 1.4rem; }
.somo-cd-sec  { color: var(--orange); font-size: 1rem; font-weight: 700; }

/* ═══════════════════════════════════════════════════════════════
   INPUT BAR — iOS Safari + Android Chrome fix
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stBottom"] {
  max-width   : 860px !important;
  margin      : 0 auto !important;
  left        : 50% !important;
  transform   : translateX(-50%) !important;
  width       : 100% !important;
  /* Respect safe area on iPhone */
  padding     : 0 1.25rem calc(.75rem + var(--sab)) !important;
  background  : linear-gradient(to top,
                  var(--cream) 70%,
                  transparent) !important;
}
[data-testid="stChatInput"] {
  background    : var(--card) !important;
  border        : 2px solid var(--border) !important;
  border-radius : 18px !important;
  box-shadow    : var(--shadow-sm) !important;
  transition    : border-color var(--dur-fast) ease,
                  box-shadow   var(--dur-fast) ease !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color : var(--amber) !important;
  box-shadow   : 0 0 0 3px rgba(245,158,11,.12),
                 var(--shadow-sm) !important;
}
[data-testid="stChatInput"] textarea {
  background  : transparent !important;
  color       : var(--text) !important;
  /* 16px = no zoom on iOS */
  font-size   : 16px !important;
  font-family : var(--fb) !important;
  border      : none !important;
  outline     : none !important;
  box-shadow  : none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color : var(--light) !important;
}
[data-testid="stChatInput"] button {
  background    : linear-gradient(135deg, var(--amber), var(--orange)) !important;
  border        : none !important;
  border-radius : 12px !important;
  box-shadow    : 0 3px 12px rgba(245,158,11,.3) !important;
  /* 44px touch target */
  min-width     : 44px !important;
  min-height    : 44px !important;
  transition    : all var(--dur-fast) ease !important;
}
@media (hover: hover) {
  [data-testid="stChatInput"] button:hover {
    transform  : scale(1.04) !important;
    box-shadow : 0 4px 18px rgba(245,158,11,.4) !important;
  }
}
[data-testid="stChatInput"] button:active {
  transform: scale(.95) !important;
}
[data-testid="stChatInput"] button svg { fill: #fff !important; }

.somo-input-footer {
  text-align     : center;
  font-family    : var(--fb) !important;
  font-size      : .5rem;
  color          : var(--faint);
  padding        : .25rem 0 .4rem;
  letter-spacing : .4px;
}

/* ═══════════════════════════════════════════════════════════════
   STREAMLIT BUTTONS (random + clear) — 44px touch targets
   ═══════════════════════════════════════════════════════════════ */
.stButton > button {
  background    : var(--card) !important;
  border        : 1.5px solid var(--border) !important;
  border-radius : 14px !important;
  color         : var(--muted) !important;
  font-family   : var(--fb) !important;
  font-size     : .8rem !important;
  font-weight   : 500 !important;
  padding       : .6rem 1rem !important;
  /* 44px min height */
  min-height    : 44px !important;
  transition    : all var(--dur-fast) ease !important;
  box-shadow    : var(--shadow-xs) !important;
  -webkit-tap-highlight-color: transparent !important;
}
@media (hover: hover) {
  .stButton > button:hover {
    border-color : var(--amber) !important;
    color        : var(--orange) !important;
    background   : rgba(245,158,11,.05) !important;
    transform    : translateY(-1px) !important;
    box-shadow   : 0 3px 12px rgba(0,0,0,.08) !important;
  }
}
.stButton > button:active {
  transform: scale(.96) !important;
  border-color : var(--amber) !important;
}

/* ═══════════════════════════════════════════════════════════════
   KaTeX
   ═══════════════════════════════════════════════════════════════ */
.katex { font-size: 1em !important; color: var(--text) !important; }
.katex-display {
  overflow-x : auto;
  -webkit-overflow-scrolling: touch;
  padding    : .35rem 0;
  margin     : .4rem 0;
}

/* ═══════════════════════════════════════════════════════════════
   REDUCED MOTION
   ═══════════════════════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration   : .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration  : .01ms !important;
  }
}

/* ═══════════════════════════════════════════════════════════════
   TABLET (641px – 860px)
   ═══════════════════════════════════════════════════════════════ */
@media (min-width: 641px) and (max-width: 860px) {
  .somo-wrap { padding: 1.5rem 1.5rem calc(7rem + var(--sab)); }
  .somo-cards { max-width: 100%; }
}

/* ═══════════════════════════════════════════════════════════════
   MOBILE (≤ 640px) — main mobile breakpoint
   ═══════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  /* Header */
  .somo-header-inner { padding: .6rem .9rem; gap: .4rem; }
  .somo-by           { display: none; }
  .somo-name         { font-size: .92rem; }
  .somo-logo         { width: 33px; height: 33px; font-size: 14px; border-radius: 9px; }
  .somo-model-pill   { display: none; } /* hide on mobile to save space */
  .somo-mode-chip    { font-size: .56rem; padding: .2rem .55rem; }
  .somo-online span:not(.somo-dot) { display: none; } /* keep dot, hide text */

  /* Layout */
  .somo-wrap {
    padding       : 1.2rem .9rem;
    padding-bottom: calc(6.5rem + var(--sab));
  }

  /* Welcome */
  .somo-welcome { padding: 1.2rem 0 1.2rem; }
  .somo-eyebrow { font-size: .57rem; padding: .28rem .9rem; }
  .somo-headline {
    font-size   : clamp(1.75rem, 10vw, 2.4rem);
    margin-bottom: .4rem;
  }
  .somo-subtext {
    font-size    : .8rem;
    margin-bottom: 1.4rem;
    padding      : 0 .5rem;
  }

  /* Cards: 2-column grid */
  .somo-cards {
    grid-template-columns: repeat(2, 1fr);
    max-width             : 100%;
    gap                   : .5rem;
  }
  .somo-card         { padding: .85rem .6rem .75rem; border-radius: 14px; }
  .somo-card-icon    { font-size: 1.3rem; }
  .somo-card-name    { font-size: .68rem; }
  .somo-card-hint    { font-size: .56rem; }

  /* Chips — horizontal scroll */
  .somo-chips-wrap   { margin-bottom: 1.2rem; }
  .somo-chips        { padding: .1rem .5rem; }
  .somo-chip         { font-size: .65rem; padding: .28rem .8rem; min-height: 34px; }

  /* Messages */
  .somo-msg-user .somo-body { max-width: 90%; }
  .somo-bubble-user  { font-size: 15px; padding: .58rem .88rem; }
  .somo-bubble-ai    { font-size: 14.5px; line-height: 1.78; }
  .somo-av           { width: 28px; height: 28px; min-width: 28px; font-size: 12px; }

  /* Copy button full-width feel */
  .somo-meta-row     { gap: 5px; }
  .somo-copy         { min-height: 30px; min-width: 68px; font-size: .58rem; }

  /* Input */
  [data-testid="stBottom"] {
    padding: 0 .9rem calc(.6rem + var(--sab)) !important;
  }
  [data-testid="stChatInput"] { border-radius: 16px !important; }

  /* Stats */
  .somo-stats { font-size: .6rem; gap: .6rem; }
}

/* ═══════════════════════════════════════════════════════════════
   SMALL MOBILE (≤ 390px) — iPhone SE, older Androids
   ═══════════════════════════════════════════════════════════════ */
@media (max-width: 390px) {
  .somo-header-inner  { padding: .55rem .75rem; }
  .somo-name          { font-size: .86rem; }
  .somo-logo          { width: 30px; height: 30px; font-size: 13px; }
  .somo-wrap          { padding: 1rem .75rem calc(6rem + var(--sab)); }
  .somo-headline      { font-size: clamp(1.6rem, 11vw, 2rem); }
  .somo-subtext       { font-size: .75rem; }
  .somo-cards         { gap: .4rem; }
  .somo-card          { padding: .75rem .5rem .65rem; border-radius: 12px; }
  .somo-card-icon     { font-size: 1.2rem; }
  .somo-card-name     { font-size: .64rem; }
  .somo-card-hint     { display: none; } /* too cramped */
  .somo-bubble-user   { font-size: 14.5px; }
  .somo-bubble-ai     { font-size: 14px; }

  [data-testid="stBottom"] {
    padding: 0 .75rem calc(.5rem + var(--sab)) !important;
  }
}

/* ═══════════════════════════════════════════════════════════════
   LANDSCAPE MOBILE — extra compact
   ═══════════════════════════════════════════════════════════════ */
@media (max-width: 812px) and (orientation: landscape) and (max-height: 500px) {
  .somo-header-inner  { padding: .45rem 1rem; }
  .somo-logo          { width: 30px; height: 30px; }
  .somo-eyebrow, .somo-subtext { display: none; }
  .somo-headline      { margin-bottom: .3rem; }
  .somo-wrap          { padding: .9rem 1rem calc(5.5rem + var(--sab)); }
  .somo-cards         { margin-bottom: 1rem; }
}
"""

st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  KaTeX re-render trigger
# ═══════════════════════════════════════════════════════════════════
KJ = ('<script>setTimeout(()=>{'
      'if(typeof renderMathInElement!=="undefined")'
      'renderMathInElement(document.body,{'
      'delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}]'
      '});},130);</script>')


# ═══════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════
_am = st.session_state.active_mode
_mm = MODE_META.get(_am, MODE_META["general"])
_badge = "Gemini 2.0 ✦" if st.session_state.use_gemini else "Groq · Llama 3.3 ✦"
_chip_cls = "on" if _am != "general" else "off"

st.markdown(
    '<div class="somo-header">'
    '<div class="somo-header-inner">'
    '<div class="somo-brand">'
    '<div class="somo-logo">S</div>'
    '<div>'
    '<div class="somo-name">Somo <em>AI</em></div>'
    '<div class="somo-by">BY USMONOV SODIQ</div>'
    '</div></div>'
    '<div class="somo-hdr-right">'
    '<div class="somo-mode-chip ' + _chip_cls + '">' + _mm["icon"] + ' ' + _mm["label"] + '</div>'
    '<div class="somo-online"><div class="somo-dot"></div><span>Online</span></div>'
    '<div class="somo-model-pill">' + _badge + '</div>'
    '</div></div></div>',
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════════
#  MAIN CONTENT AREA
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="somo-wrap">', unsafe_allow_html=True)

msgs = st.session_state.messages

if not msgs:
    # ── WELCOME SCREEN ──────────────────────────────────────────────
    gi, gt = get_greeting()
    st.markdown(
        '<div class="somo-welcome">'
        '<div class="somo-eyebrow">✦ ' + gi + ' ' + gt + '</div>'
        '<div class="somo-headline">Ijodingizni<br><em>kuchlaytiring</em></div>'
        '<div class="somo-subtext">'
        "Shunchaki xabar yozing — esse, she'r, nutq, tarjima yoki istalgan savol.<br>"
        "Somo AI mavzudan rejimni o'zi aniqlaydi. 🚀"
        '</div>'
        '<div class="somo-cards">'
        '<div class="somo-card"><span class="somo-card-icon">✍️</span>'
        '<div class="somo-card-name">Esse / Referat</div>'
        '<div class="somo-card-hint">"Vatan haqida esse"</div></div>'
        '<div class="somo-card"><span class="somo-card-icon">📖</span>'
        "<div class=\"somo-card-name\">Hikoya / She'r</div>"
        '<div class="somo-card-hint">"Bahor she\'ri"</div></div>'
        '<div class="somo-card"><span class="somo-card-icon">🎤</span>'
        '<div class="somo-card-name">Nutq</div>'
        '<div class="somo-card-hint">"Yoshlar nutqi"</div></div>'
        '<div class="somo-card"><span class="somo-card-icon">💡</span>'
        "<div class=\"somo-card-name\">G'oyalar</div>"
        '<div class="somo-card-hint">"Startup g\'oyasi"</div></div>'
        '<div class="somo-card"><span class="somo-card-icon">🌍</span>'
        '<div class="somo-card-name">Tarjima</div>'
        '<div class="somo-card-hint">"To English"</div></div>'
        '<div class="somo-card"><span class="somo-card-icon">📋</span>'
        '<div class="somo-card-name">Xulosa / Tahlil</div>'
        '<div class="somo-card-hint">"Matnni tahlil qil"</div></div>'
        '</div>'
        '<div class="somo-chips-wrap"><div class="somo-chips">'
        '<div class="somo-chip">📝 Ekologiya esse</div>'
        "<div class=\"somo-chip\">🌸 Bahor she'ri</div>"
        '<div class="somo-chip">🎤 Maktab nutqi</div>'
        "<div class=\"somo-chip\">💡 10 biznes g'oya</div>"
        '<div class="somo-chip">🌍 Hello — o\'zbekcha</div>'
        "<div class=\"somo-chip\">📖 Ona haqida she'r</div>"
        '</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1.2, 2.2, 1.2])
    with c2:
        if st.button("🎲  Tasodifiy ilhom", use_container_width=True, key="rand"):
            st.session_state.rand_trigger = random.choice(RAND_PROMPTS)
            st.rerun()

else:
    # ── CHAT VIEW ──────────────────────────────────────────────────
    _ai_msgs  = [m for m in msgs if m["role"] == "assistant"]
    _usr_msgs = [m for m in msgs if m["role"] == "user"]
    _total_w  = sum(wc(m["content"]) for m in _ai_msgs)
    gi2, gt2  = get_greeting()

    st.markdown(
        '<div class="somo-stats">'
        '<span class="somo-stat">' + gi2 + '&nbsp;' + gt2 + '</span>'
        '<span class="somo-stat">💬 <b>' + str(len(_usr_msgs)) + '</b> savol</span>'
        '<span class="somo-stat">✍️ <b>' + str(_total_w) + "</b> so'z</span>"
        '</div>',
        unsafe_allow_html=True
    )

    cc1, cc2, cc3 = st.columns([3, 1.5, 3])
    with cc2:
        if st.button("🗑️  Tozalash", use_container_width=True, key="clr"):
            st.session_state.messages    = []
            st.session_state.active_mode = "general"
            st.session_state.use_gemini  = False
            st.rerun()

    st.markdown('<div class="somo-divider">Suhbat</div>', unsafe_allow_html=True)

    for i, msg in enumerate(msgs):
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
        m_mode  = msg.get("mode", "general")
        mm      = MODE_META.get(m_mode, MODE_META["general"])

        if role == "user":
            st.markdown(
                '<div class="somo-msg-user">'
                '<div class="somo-body">'
                '<div class="somo-bubble-user">' + content + '</div>'
                '<div class="somo-ts">' + ts + '</div>'
                '</div></div>',
                unsafe_allow_html=True
            )
        else:
            _wc_val = wc(content)
            label   = ""
            if m_mode != "general":
                label = (
                    '<div class="somo-mode-label">'
                    + mm["icon"] + " " + mm["label"] +
                    '</div><br>'
                )
            _cid = "scp" + str(i)
            _fid = "scf" + str(i)
            _cjs = (
                '<script>function ' + _fid + '(){'
                'navigator.clipboard.writeText(' + repr(content) + ');'
                'var b=document.getElementById("' + _cid + '");'
                'b.innerText="✅ Nusxalandi";'
                'setTimeout(()=>{b.innerText="📋 Nusxa"},2400);}'
                '</script>'
            )
            st.markdown(
                '<div class="somo-msg-ai">'
                '<div class="somo-av">S</div>'
                '<div class="somo-body">'
                '<div class="somo-sender">Somo AI</div>'
                '<div class="somo-bubble-ai">' + label + md_to_html(content) + '</div>'
                '<div class="somo-meta-row">'
                '<span class="somo-ts">' + ts + '</span>'
                '<span class="somo-wc">📝 ' + str(_wc_val) + " so'z</span>"
                '<button class="somo-copy" id="' + _cid + '" onclick="' + _fid + '()">📋&nbsp;Nusxa</button>'
                '</div></div></div>' + _cjs + KJ,
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)  # close somo-wrap


# ═══════════════════════════════════════════════════════════════════
#  COOLDOWN TIMER
# ═══════════════════════════════════════════════════════════════════
_rem = int(st.session_state.cooldown_end - time.time())
if _rem > 0:
    st.markdown(
        '<div class="somo-cd-wrap">'
        '<div class="somo-cd-box">'
        '<span class="somo-cd-icon">⏳</span>'
        '<div><strong>API limiti tugadi.</strong> Kuting — '
        '<span class="somo-cd-sec">' + str(_rem) + ' soniya</span></div>'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.chat_input("Iltimos kuting…", disabled=True)
    time.sleep(1)
    st.rerun()
else:
    prompt = st.chat_input("Xabar yozing… esse, she'r, nutq, tarjima…")
    if not prompt and st.session_state.rand_trigger:
        prompt = st.session_state.rand_trigger
        st.session_state.rand_trigger = None

st.markdown(
    '<div class="somo-input-footer">Somo AI · Usmonov Sodiq (@Somo_AI) · Groq + Gemini</div>',
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════════
#  PROCESS MESSAGE
# ═══════════════════════════════════════════════════════════════════
if prompt and prompt.strip():
    utxt   = prompt.strip()
    now    = get_time()
    mode   = detect_mode(utxt)
    mm     = MODE_META.get(mode, MODE_META["general"])
    syspmt = build_system_prompt(mode)

    st.session_state.active_mode = mode
    st.session_state.messages.append(
        {"role": "user", "content": utxt, "time": now, "mode": mode}
    )

    st.markdown(
        '<div class="somo-msg-user">'
        '<div class="somo-body">'
        '<div class="somo-bubble-user">' + utxt + '</div>'
        '<div class="somo-ts">' + now + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    ph = st.empty()
    ph.markdown(
        '<div class="somo-msg-ai">'
        '<div class="somo-av">S</div>'
        '<div class="somo-body">'
        '<div class="somo-sender">Somo AI</div>'
        '<div class="somo-bubble-ai"><span class="somo-cur"></span></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    _lbl = ""
    if mode != "general":
        _lbl = (
            '<div class="somo-mode-label">'
            + mm["icon"] + " " + mm["label"] +
            '</div><br>'
        )

    def render(text: str, cursor: bool = False, ts: str = "") -> None:
        _cur = '<span class="somo-cur"></span>' if cursor else ""
        _td  = '<div class="somo-ts">' + ts + '</div>' if ts else ""
        ph.markdown(
            '<div class="somo-msg-ai">'
            '<div class="somo-av">S</div>'
            '<div class="somo-body">'
            '<div class="somo-sender">Somo AI</div>'
            '<div class="somo-bubble-ai">' + _lbl + md_to_html(text) + _cur + '</div>'
            + _td +
            '</div></div>' + KJ,
            unsafe_allow_html=True
        )

    def stream_groq() -> str:
        if not groq_client: raise Exception("no groq client")
        api_msgs = [{"role": "system", "content": syspmt}]
        for m in st.session_state.messages:
            api_msgs.append({"role": m["role"], "content": m["content"]})
        stream = groq_client.chat.completions.create(
            model=GROQ_MODEL, messages=api_msgs, stream=True,
            max_tokens=GROQ_MAX_TOK, temperature=GROQ_TEMP,
        )
        out = ""
        for chunk in stream:
            out += chunk.choices[0].delta.content or ""
            render(out, cursor=True)
        return out

    def stream_gemini() -> str:
        if not gemini_client: raise Exception("no gemini client")
        hist = []
        for m in st.session_state.messages[:-1]:
            hist.append({
                "role"  : "user" if m["role"] == "user" else "model",
                "parts" : [m["content"]]
            })
        chat = gemini_client.start_chat(history=hist)
        resp = chat.send_message(
            syspmt + "\n\n---\n\n" + utxt,
            generation_config={"temperature": GEMINI_TEMP, "max_output_tokens": GEMINI_MAX_TOK},
            stream=True,
        )
        out = ""
        for chunk in resp:
            try:    out += chunk.text or ""
            except: pass
            if out: render(out, cursor=True)
        return out

    full    = ""
    is_rate = lambda e: is_rate_err(str(e))

    try:
        if st.session_state.use_gemini:
            full = stream_gemini()
        else:
            full = stream_groq()
            st.session_state.use_gemini = False

    except Exception as e1:
        if is_rate(e1) and not st.session_state.use_gemini:
            st.session_state.use_gemini = True
            render("⚡ Groq limiti tugadi, Gemini ga o'tmoqda…", cursor=True)
            try:
                full = stream_gemini()
            except Exception as e2:
                if is_rate(e2):
                    st.session_state.cooldown_end = time.time() + COOLDOWN_LONG
                    full = "⏳ Ikkala API limiti tugadi. " + str(COOLDOWN_LONG) + " soniya kuting."
                else:
                    full = "❌ Gemini xatolik: " + str(e2)
        elif is_rate(e1) and st.session_state.use_gemini:
            st.session_state.use_gemini = False
            render("⚡ Gemini limiti tugadi, Groq ga qaytmoqda…", cursor=True)
            try:
                full = stream_groq()
            except Exception as e3:
                if is_rate(e3):
                    st.session_state.cooldown_end = time.time() + COOLDOWN_LONG
                    full = "⏳ Ikkala API limiti tugadi. " + str(COOLDOWN_LONG) + " soniya kuting."
                else:
                    full = "❌ Xatolik: " + str(e3)
        elif "api_key" in str(e1).lower() or "auth" in str(e1).lower():
            full = "❌ API kalit xato. Secrets faylini tekshiring."
        else:
            full = "❌ Xatolik: " + str(e1)

    if full:
        render(full, cursor=False, ts=get_time())

    st.session_state.messages.append({
        "role"    : "assistant",
        "content" : full,
        "time"    : get_time(),
        "mode"    : mode,
    })


# ═══════════════════════════════════════════════════════════════════
#  DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════
#
#  SECRETS  (.streamlit/secrets.toml):
#    GROQ_API_KEY   = "gsk_..."
#    GEMINI_API_KEY = "AIza..."
#
#  REQUIREMENTS (requirements.txt):
#    streamlit>=1.32.0
#    groq>=0.8.0
#    google-generativeai>=0.8.0
#
# ─────────────────────────────────────────────────────────────────
#  VERSIYA TARIXI
# ─────────────────────────────────────────────────────────────────
#  v1.0  Boshlang'ich (Groq + qorong'i tema)
#  v2.0  Cream dizayn, auto rejim aniqlash
#  v2.1  Sidebar o'chirildi, layout=wide
#  v2.2  Dual-API: Groq + Gemini fallback
#  v2.3  Cooldown timer + input qulflash
#  v2.4  System prompt kuchaytirildi
#  v2.5  AI bubble ramkasiz uslub
#  v3.0  Copy, so'z soni, statistika, random, tozalash, salomlash
#  v4.0  Premium dizayn: glass morphism, gradient, Fraunces + DM Sans
#  v4.1  MOBILE-PERFECT EDITION:
#        • viewport-fit=cover (notch support)
#        • env(safe-area-inset-*) hamma joylarda
#        • 44px min touch targets barcha interaktiv elementlar
#        • font-size: 16px input (iOS zoom oldini olish)
#        • @media (hover: hover) — mobil hover effektini o'chirish
#        • Chips horizontal scroll (nowrap, iOS momentum)
#        • Cards: 2-col mobile, 3-col desktop
#        • Model pill hidden on mobile (header compact)
#        • Online text hidden on mobile (dot qoladi)
#        • Landscape mobile breakpoint
#        • prefers-reduced-motion support
#        • Table/pre/katex: overflow-x auto + iOS touch scroll
#        • Copy button: 44px touch area
#        • somo-subtext hint mobil uchun padding
#        • 390px breakpoint (iPhone SE / small Android)
#
# ═══════════════════════════════════════════════════════════════════
#  © 2026  Usmonov Sodiq  |  @Somo_AI  |  Barcha huquqlar himoyalangan
# ═══════════════════════════════════════════════════════════════════

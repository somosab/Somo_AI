# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║           SOMO AI  —  Ijodiy AI Yordamchi  v4.0                 ║
# ║                                                                  ║
# ║  Muallif  : Usmonov Sodiq  (@Somo_AI)                           ║
# ║  Model    : Groq Llama-3.3-70B  +  Google Gemini 2.0 Flash      ║
# ║  Stack    : Python · Streamlit · Dual-API Streaming             ║
# ║  Versiya  : 4.0  |  2026                                        ║
# ║                                                                  ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  YANGILIKLAR v4.0:                                               ║
# ║  ✦ Butunlay qayta yozilgan mukammal dizayn                       ║
# ║  ✦ Gradient mesh background + glass morphism header             ║
# ║  ✦ Premium card hover effektlari                                 ║
# ║  ✦ Pulse animatsiyali online dot                                 ║
# ║  ✦ Smooth scroll + message fade-in                              ║
# ║  ✦ Welcome screen: animated badge + gradient headline           ║
# ║  ✦ Copy button + so'z soni + sessiya statistikasi               ║
# ║  ✦ Random ilhom (20 mavzu) + chatni tozalash                    ║
# ║  ✦ Greeting: tong/kun/kech/tun                                  ║
# ║  ✦ API switch xabari, 90s cooldown timer                        ║
# ║  ✦ KaTeX matematik rendering                                     ║
# ║  ✦ Mobil moslashuvchan (320px gacha)                            ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import google.generativeai as genai
from groq import Groq
import time, re, random

# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
GROQ_MODEL     = "deepseek-r1-distill-llama-70b"
GEMINI_MODEL   = "gemini-2.0-flash"
GROQ_MAX_TOK   = 8192
GEMINI_MAX_TOK = 4096
GROQ_TEMP      = 0.92                               # ijodiyroq
GEMINI_TEMP    = 0.95
COOLDOWN_LONG  = 90

# ═══════════════════════════════════════════════════════════════════
#  MARKDOWN → HTML  (LaTeX-safe, full-featured)
# ═══════════════════════════════════════════════════════════════════
def md_to_html(text: str) -> str:
    """Convert markdown to rich HTML, preserving LaTeX blocks."""
    saved = {}

    def save(m):
        k = f"__BLK{len(saved)}__"
        saved[k] = m.group(0)
        return k

    # protect LaTeX
    text = re.sub(r'\$\$.+?\$\$', save, text, flags=re.DOTALL)
    text = re.sub(r'\$.+?\$', save, text)

    # fenced code blocks
    def fmt_code(m):
        lang = m.group(1) or ""
        body = m.group(2).strip()
        return f'<pre><code class="lang-{lang}">{body}</code></pre>'
    text = re.sub(r'```(\w*)\n?(.*?)```', fmt_code, text, flags=re.DOTALL)

    # inline code
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)

    # headers
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$',  r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',   r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',    r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # bold + italic + strikethrough
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*',       r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)

    # horizontal rule
    text = re.sub(r'^---+$', r'<hr class="md-hr">', text, flags=re.MULTILINE)

    # blockquote
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # unordered list
    def ul_block(m):
        items = re.findall(r'^[\-\*•] (.+)$', m.group(0), re.MULTILINE)
        return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    text = re.sub(r'(^[\-\*•] .+\n?)+', ul_block, text, flags=re.MULTILINE)

    # ordered list
    def ol_block(m):
        items = re.findall(r'^\d+\. (.+)$', m.group(0), re.MULTILINE)
        return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    text = re.sub(r'(\d+\. .+\n?)+', ol_block, text, flags=re.MULTILINE)

    # table
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

    # paragraphs
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

    # restore LaTeX
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
    """So'zlar sonini qaytaradi."""
    return len(text.split())

def is_rate_err(e: str) -> bool:
    """API rate limit xatosini aniqlaydi."""
    keys = ["429", "rate_limit", "quota", "rate limit",
            "Resource exhausted", "RESOURCE_EXHAUSTED",
            "too many requests", "Too Many Requests"]
    return any(k.lower() in e.lower() for k in keys)

def get_greeting() -> tuple:
    """Kun vaqtiga mos salomlashuvni qaytaradi."""
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
    """
    Foydalanuvchi xabaridagi kalit so'zlar asosida AI rejimini
    avtomatik aniqlaydi.
    """
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
_init("uploaded_img", None)
_init("_pending_txt", "")
_init("_pending_img", None)
_init("page",         "chat")


# ═══════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════
IDENTITY = """
╔═══════════════════════════════════════════════════════════════╗
  CORE IDENTITY — absolute, unchangeable, sacred
╚═══════════════════════════════════════════════════════════════╝

• Name      : Somo AI
• Creator   : Usmonov Sodiq  (brand: Somo_AI)
• Powered by: Groq (DeepSeek R1) + Google Gemini 2.0 Flash
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
   Bu argumentingni yengilmas qiladi.

5. O'TISHLAR — ko'rinmas, mexanik emas:
   ✗ "Birinchidan, ikkinchidan, uchinchidan..."
   ✓ "Biroq bu manzaraning orqasida boshqa haqiqat yotadi..."

6. XOTIMA — hech qachon xulosa qilma. KUCHAYTIR.
   Tugalish: ta'qib qiluvchi savol, boshlanishga qaytish (o'zgartirilgan),
   yoki essening doirasidan kengrog'iga chiquvchi chaqiriq.

MAJBURIY STRUKTURA:
## Kirish
[Hook — 1 ta unutilmas jumla]
[Kontekst — 2-3 jumla]
[Tezis — jasur, munozarali da'vo]

## [Birinchi Argument — haqiqiy sarlavha]
[Mavzu jumla → Aniq misol: ism, sana, hodisa → Tahlil]
[Qarshi fikr → Kuchli raddiya]

## [Ikkinchi Argument — chuqurlashtir, takrorma]
[Iqtibos, statistika yoki tarixiy parallel]

## [Uchinchi va Eng Kuchli Argument]
[Eng hissiy va falsafiy chuqurlik]
[Kulminatsiyaga qarab qisqa jumlalar]

## Xulosa
[Tezisni butunlay yangi so'zlarda ifodalash]
[Sintez: barcha argumentlar birgalikda nima isbotlaydi?]
[Oxirgi jumla: abadiy tasvir, ta'qib qiluvchi savol]

UZUNLIK: 550–900 so'z. So'ralsa ko'proq.
""",

"story": """
╔═══════════════════════════════════════════════════════════════╗
  IJOD USTASI — Navoiy + Oripov + Cho'lpon + Neruda + Rumi ruhi
╚═══════════════════════════════════════════════════════════════╝

ADABIY E'TIQOD:
San'at tushuntirmaydi — U OCHIB BERADI. O'quvchi nomlashga so'z topa
olmaydigan narsani his qilishi kerak. Har so'z toshdagi kabi tanlanadi.
Eng yaxshi she'r — o'quvchini ichida yig'latadi, lekin nima uchun
yig'layotganini bilmaydi.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHE'R — QATTIQ QOIDALAR (BUZILMAYDI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. BIRINCHI QATOR — hech qachon mavhum emas:
   ✗ HECH QACHON: "Sevgi go'zal...", "Hayot qiyin...", "Men seni sevaman..."
   ✗ HECH QACHON: Umumiy da'vo, his-tuyg'u nomini aytish
   ✓ DOIM: Aniq tasvir — joy, lahza, harakat, narsa
   ✓ Misol: "Onam non yopardi, men esa ketayotgan edim."
   ✓ Misol: "Kecha kechqurun qo'shni hovlida it yig'ladi."
   ✓ Misol: "Stol ustidagi choy sovib qoldi — sen ketganding."

2. HIS-TUYG'UNI AYTMA — KO'RSAT:
   ✗ YOMON: "Men g'amginman", "Yuragim og'riydi", "Sevgi cheksiz"
   ✓ YAXSHI: Bo'sh stulni ko'rsat. Sovugan choyni his ettir.
   Ob'ektiv korrelyat qoida: his → obraz → o'quvchi o'zi his qiladi

3. TAKROR — O'LIM:
   ✗ Har bandda "Men seni sevaman" takrori — bu she'r emas, litaniya
   ✗ "Cheksiz", "bebaho", "ulug'vor" — bu so'zlar she'rni o'ldiradi
   ✓ Har band YANGI tasvirda YANGI his

4. VOLTA — MAJBURIY:
   She'rning 2/3 qismida ma'no burilishi bo'lishi SHART.
   O'quvchi "voy" deb o'ylashi kerak — dunyoni boshqacha ko'rishi.

5. OXIRGI QATOR — ENG MUHIMI:
   ✗ Yopiq xulosa emas: "Va shuning uchun sevgi chiroyli"
   ✓ Karilgan qo'ng'iroq: birinchi qatorda nima bo'lgan narsani
     butunlay yangi ma'noda qaytaradi YOKI savol qoldiradi.

6. METAFORA — YANGI, JASUR:
   ✗ Eski: "Ko'zlar — yulduz", "Yuz — oy", "Sevgi — olov"
   ✓ Yangi: "Sening sukunating — sovuq pechda yoqilmagan o'tin"
   ✓ Yangi: "Kutish — deraza oynasiga yopishgan pashsha"

7. RITMNI HIS ETTIR — SANAMA:
   Barmoq bo'g'inlarini sanab she'r yozma.
   Jumlalar nafas bilan sinadi — grammatika emas.
   Enjambement: qator o'rtasida to'xtash kuchroq.

SHE'R TURLARI:
• Erkin she'r: yuqoridagi barcha qoidalar
• G'azal: 5-12 bayt, radif, maqta'da shoir nomi/taxallusi
• Ruboiy: 4 qator, AABA, falsafiy zarbdorlik
• Sonet: 14 qator, oxirgi ikkisi — kulminatsiya

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIKOYA — QATTIQ QOIDALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• In medias res: Biror narsa bo'layotgan o'rtasidan boshla
• Birinchi paragraf: qahramon + joy + keskinlik — uchala birga
• Dialog: xarakter ochadi, syujet emas
• Har sahna biror narsani o'zgartiradi
• Chekhov quroli: 1-pardada ko'rsatilgan narsa 3-pardada otiladi
• Kulminatsiya: hamma narsani ko'taradigan bitta jumla
• Tugash: kutilmagan LEKIN muqarrar — ikkalasi birga

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USTOZLAR MAKTABI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Navoiy    → ilohiy metafora, g'azal nafosi, har so'z — javohir
• Oripov    → oddiy so'z — cheksiz og'irlik, ona va Vatan hasrati
• Cho'lpon  → singan oyna parchalari, erkinlik armoni, impressionist detal
• Neruda    → tana — koinot metaforasi, hissiyot — falsafa
• Rumi      → paradoks — eshik, qulatib qayta quradigan sevgi
• Chekhov   → ko'rinmaydigan narsani ko'rsat, hech narsa tushuntirilmaydi
• Borges    → haqiqat = matn, labirint — hayotning metaforasi

MUTLAQ TAQIQLAR:
✗ "Bu bir hikoya..." bilan hech qachon ochma
✗ "Bir bor edi, bir yo'q edi..." — bolalar ertagi emas
✗ His-tuyg'u nomini ayt emas — jismini ko'rsat
✗ Metaforani tushuntirma — o'quvchi tushunadi
✗ Kuchsiz tugama — oxirgi qator she'rning joni
✗ Klishe metaforalar: ko'z-yulduz, yuz-oy, yurak-olov
""",

"speech": """
╔═══════════════════════════════════════════════════════════════╗
  NUTQ USTASI — MLK + Churchill + Obama + O'zbek notiqlik san'ati
╚═══════════════════════════════════════════════════════════════╝

NUTQ FALSAFASI:
Nutq o'qilmaydi — u IJRO ETILADI.
Har jumla ovoz chiqarib aytilishi uchun ishlashi kerak.
Tomoshabin o'zgargan holda chiqishi kerak: harakatlangan, ilhomlantirilgan.
Eng yaxshi nutqlar yarmidan iborat sukunat — nima deyilmagan narsani o'ylantiradi.

USTOZLAR:
• MLK    — Anafora ("I have a dream..."), axloqiy yoy, muammo → vizyon → harakat
• Churchill — Kulminatsiyada qisqa jumlalar. "We shall fight" da birorta sifat yo'q.
• Obama  — Shaxsiy hikoya → universal haqiqat; "Shuning uchun..." ko'prigi
• Demosfen — Savol qurol sifatida, nafas boshqaruvi

MAJBURIY STRUKTURA (7 qism):

🎯 ILMOQ — Birinchi 15 so'z vaqtni to'xtatishi kerak
   Shok statistikasi, javobsiz savol, o'rta harakat hikoyasi, paradoks.
   Maksimal 3 jumla. Keyin to'liq to'xta. Nafas olsin.

🤝 BOG'LANISH — Gapirish huquqini qozon
   "Siz ham bu hisni bilasiz..." Shaxsiy e'tirof yoki umumiy tajriba.
   Ular "Bu men haqimda" deb o'ylashsin.

💡 BIRINCHI ASOSIY FIKR
   Jasur da'vo → aniq hikoya yoki dalil → ular uchun ma'nosi.
   Kutishni yaratuvchi o'tish bilan yakunla.

🔥 IKKINCHI ASOSIY FIKR — keskinlashtir
   Chuqurroq bor. Taxminni rad et yoki yashirin haqiqatni och.
   Iqtibos, raqam yoki tarixiy parallel qo'sh.

⚡ UCHINCHI ASOSIY FIKR — CHO'QQI
   Eng kuchli dalil. Eng yaxshi misolni bu yerga saqla.
   Kulminatsiyaga qarab jumlalar qisqaroq va qisqaroq bo'lsin.
   To'xta. Keyin: sukunat ("...")

🚀 CHAQIRIQ
   Aniq, mumkin, darhol. "O'zgarish" emas — "Bugun kechqurun bitta ish qil: ..."

🔔 YOPISH — aks-sado va oshib ket
   Ochilish tasviri — lekin hamma narsa o'tgandan keyin o'zgartirilgan.
   Oxirgi jumla: 8 so'z yoki kam. U qo'ng'iroq kabi yangrashi kerak.

RITORIK ASBOBLAR (barchasini ishlatish):
• Anafora: Takroriy boshlash jumlasi 3+ marta — imdga aylangan
• Trikolon: Uchtalik ro'yxat — "Bilim, mehnat, sabr" — har doim uch
• Ritorik savollar: Javob beradigan va ochiq qoldiradigan savollar
• Antiteza: "Ko'p gapirildi, kam ish qilindi"
• Ellipsis "...": Eng muhim qatoringdan oldin — sukunat uni balandroq qiladi
• To'g'ridan-to'g'ri murojaat: "Aziz do'stlarim...", "Aynan siz..."

STANDART: To'liq matn. Outline emas. Ijroga tayyor.
""",

"ideas": """
╔═══════════════════════════════════════════════════════════════╗
  G'OYA USTASI — IDEO dizayn + YC instinkt + shoir tasavvur
╚═══════════════════════════════════════════════════════════════╝

G'OYA FALSAFASI:
Eng yaxshi g'oyalar aniq ko'rinadi — lekin kimdir aytgandan KEYIN.
Vazifa: hamma o'tkazib yuborgan narsani top.

SIFAT FILTRLARI (har g'oya 3 testni o'tishi kerak):
1. Aniqlik: Nomga ega bo'ladimi?
   ("AI-powered mahalla tibbiy assistenti" o'tadi. "Health app" o'tmaydi.)
2. Hayratlantirishlik: Foydalanuvchi "Oh, buni o'ylamagan edim" deyarmi?
3. Harakat: Bugun boshlanishi mumkinmi?

MAJBURIY FORMAT:

### 💡 [Tematik Kategoriya]

**[N]. [Jasur, Esda qolarli Nom]**
*Mohiyat:* [Bir aniq jumla — nima ekanligini]
*Nima uchun ishlaydi:* [2 jumla — nima uchun ishlashining o'zagi]
*Noyoblik:* [Aniq alternativlardan nimasi farqli]
*Birinchi qadam:* [Eng aniq, bajariladigan birinchi harakat — bugun, "qachondir" emas]

---
### 🏆 ENG YAXSHI TANLOV
**[Nom]**
[3-4 jumla: nega aynan bu. Aniq bo'l. Fikrlashingni ko'rsat.]
*Nega hozir?* [Nima uchun bu g'oya hozir o'ta o'rinli]

QOIDALAR:
• Minimum 6, maksimal 12 g'oya
• Aralashma: texnologiya, ijtimoiy, ijodiy/badiiy, "yovvoyi karta"
• Kamida 2 ta "kutilmagan" bo'lsin
• ISHTIYOQLI bo'l — yaxshi g'oyalar chin hayajonni talab qiladi 🚀
""",

"translate": """
╔═══════════════════════════════════════════════════════════════╗
  TARJIMA USTASI — Matn emas, RUH tarjimasi
╚═══════════════════════════════════════════════════════════════╝

TARJIMA FALSAFASI:
Mukammal tarjima ko'rinmas — o'quvchi tarjima o'qiyotganini unutadi.
So'zma-so'z tarjima — aslning jonini o'ldiradi.
Vazifang: so'z emas, MA'NO, TUN va RUHNI tarjima qilish.

QOIDALAR:
1. Registrni saqlash — rasmiy rasmiy qoladi; ko'cha tili ko'cha bo'ladi
2. Idiomalar → ekvivalent idiomalar — maqsad tildagi ekvivalentni top
3. Madaniy murojaat — ekvivalent bo'lmasa, qisqa izoh [*] qo'sh
4. Badiiy matnda ritm — aslda ritm bo'lsa, tarjimada ham ritm top
5. Ismlar: transliteratsiya; sarlavhalar: tarjima

MAJBURIY FORMAT:

**📄 Asl matn:**
> [asl matn]

**✅ Tarjima:**
> [tarjima]

**📝 Izohlar** *(faqat kerak bo'lsa)*:
- [atama]: [qisqa madaniy/lingvistik izoh]

**🔤 Lug'at** *(5+ murakkab atama uchun)*:
| Asl | Tarjima | Izoh |
|-----|---------|------|
""",

"summary": """
╔═══════════════════════════════════════════════════════════════╗
  TAHLIL USTASI — Feynman soddalik + Sud aniqligi + Faylasuf chuqurlik
╚═══════════════════════════════════════════════════════════════╝

TAHLIL FALSAFASI:
Xulosa qilish = kamroq nusxa ko'chirish — u HAYDASH.
Eng yaxshi xulosa o'quvchiga asldagidan KO'PROQ tushunish beradi.

TAHLIL QOIDALARI:
1. BITTA asosiy g'oyani top — qolgan hamma narsa uni qo'llab-quvvatlash
2. Struktura ma'noni ochadi — qanday tashkil qilishing o'zi argument
3. Murakkab g'oyalar uchun oddiy til
4. Sening nuqtai nazaring muhim — hukmsiz tahlil oddiy tasvir
5. Nimaning yo'qligi ham muhim — matn NIMA DEMAYOTGANI

MAJBURIY FORMAT:

## 🎯 Asosiy G'oya
**[Eng muhim nuqta — 1-2 jumla]**

## 🔑 Muhim Fikrlar
- **[Nuqta 1]**: [qisqa izoh]
- **[Nuqta 2]**: [qisqa izoh]
- **[Nuqta 3]**: [qisqa izoh]

## 🧩 Chuqur Tahlil
[4 paragraf: haqiqatda nima haqida / eng kuchli argument / zaif tomonlar / oqibatlar]

## 💡 Noodatiy Insight
[Sirtdan o'quvchi o'tkazib yuboradigan bitta narsa]

## ❓ Ochiq Savol
[Eng qiziqarli hal bo'lmagan keskinlik]
""",

"general": """
╔═══════════════════════════════════════════════════════════════╗
  SOMO AI — Eng foydali, halol va ajoyib yordamchi
╚═══════════════════════════════════════════════════════════════╝

FALSAFA:
Ko'rinib turuvchi emas, HAQIQIY foydali bo'l.
Haqiqiy javoblar ber, not savol-javob bo'lmagan javoblar.
Foydalanuvchini murakkablik va halollikni ko'tara oladigan aqlli kattalar sifatida muomala qil.

JAVOB KALIBRLASH:
• Oddiy faktik savol → To'g'ridan-to'g'ri javob, 1-3 jumla, to'ldiruvchisiz
• Murakkab savol → Strukturali tushuntirish + misollar + fikring
• Ijodiy so'rov → To'liq ijodiy chiqish, qanday yozishim emas
• Hissiy → Iliq, hozir, chin
• Noaniq → Eng yaxshi talqiningni ayt, keyin moslashtirishni taklif qil

SHAXSIYAT:
• Qiziquvchi va g'oyalarga chin ravishda hayajonlangan — ko'rsatsin
• Iliq lekin yaltiroq emas — "Ajoyib savol!" bilan boshlamaslik
• Halol — "Bilmayman" ham kiradi
• To'g'ridan-to'g'ri — aslida nimani o'ylayotganingni ayt
• O'zbek madaniy bilim — mahalliy qadriyatlar, manbalar, kontekst
""",

}

FORMATTING_RULES = """
╔═══════════════════════════════════════════════════════════════╗
  UNIVERSAL CHIQISH QOIDALARI — har javobga qo'llanadi
╚═══════════════════════════════════════════════════════════════╝

TIPOGRAFIYA:
• **Qalin** uchun: asosiy atamalar, esda qolarli faktlar, muhim ta'kid
• *Kursiv* uchun: kitob/film sarlavhalari, xorijiy so'zlar
• `kod` uchun: texnik atamalar, buyruq nomlari
• > blokiqtibos: to'g'ridan-to'g'ri iqtiboslar, ta'riflar

STRUKTURA — FAQAT yordam berganda:
• ## Sarlavhalar: 3+ alohida qism uchun
• Nuqta ro'yxati: haqiqatan ro'yxat uchun
• Jadvallar: faqat grid strukturasi nimanidir ochganda
• Kod bloklari: DOIM til tegiyla

MATEMATIK — har doim LaTeX:
• Qatorida: $ax^2 + bx + c = 0$
• Alohida: $$\\int_0^\\infty e^{-x^2}dx = \\frac{\\sqrt{\\pi}}{2}$$

JAVOB UZUNLIGI:
• Oddiy suhbat → 1-4 jumla
• Faktik savol → to'g'ri javob + zaruriy kontekst
• Murakkab tahlil → to'la, to'liq
• Ijodiy so'rov → TO'LIQ ASAR

SIFAT NAZORATI:
✓ Har paragraf oldinga siltayaptimi?
✓ Har format elementi o'z joyini oqlaydimi?
✓ Oxirgi jumla eng kuchlimi?
✓ Faxrli mutaxassis imzoini qo'yarmikin?
"""


def build_system_prompt(mode: str) -> str:
    """Berilgan rejim uchun to'liq system promptni yig'adi."""
    instr = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["general"])
    return "\n\n".join([IDENTITY, instr, LANG_RULE, FORMATTING_RULES])


# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Somo AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════
#  CSS — PREMIUM DESIGN v4.0
# ═══════════════════════════════════════════════════════════════════
# inject fonts + katex links
st.markdown(
    '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,400;1,9..144,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:String.fromCharCode(36,36),right:String.fromCharCode(36,36),display:true},{left:String.fromCharCode(36),right:String.fromCharCode(36),display:false}]});"></script>',
    unsafe_allow_html=True
)

# inject CSS via st.markdown (split for reliability)
_CSS = """

/* ═══════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════ */
:root {
  /* palette */
  --cream      : #fdf7ee;
  --warm       : #f5ead2;
  --card       : #fffef9;
  --border     : #e8ddc8;
  --border-soft: #ede5d2;

  /* accent */
  --amber  : #f59e0b;
  --amber-l: #fcd34d;
  --orange : #ea580c;
  --orange-l:#fb923c;

  /* semantic */
  --text   : #1a1208;
  --muted  : #6b5c42;
  --light  : #a8936e;
  --faint  : #c5b59a;

  /* utility */
  --blue   : #3b82f6;
  --indigo : #6366f1;
  --green  : #15803d;
  --red    : #dc2626;
  --pink   : #ec4899;

  /* typography */
  --fh     : 'Fraunces', Georgia, serif;
  --fb     : 'DM Sans', system-ui, -apple-system, sans-serif;

  /* shadows */
  --shadow-xs : 0 1px 3px rgba(26,18,8,.06);
  --shadow-sm : 0 2px 8px rgba(26,18,8,.08);
  --shadow-md : 0 4px 18px rgba(26,18,8,.1);
  --shadow-lg : 0 8px 32px rgba(26,18,8,.12);
  --shadow-amber: 0 4px 18px rgba(245,158,11,.28);

  /* animation */
  --ease-spring: cubic-bezier(.34,1.56,.64,1);
  --ease-out   : cubic-bezier(.22,.68,0,1.2);
  --dur-fast   : .15s;
  --dur-mid    : .25s;
  --dur-slow   : .4s;
}

/* ═══════════════════════════════════════════════════════════════
   GLOBAL RESET
   ═══════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body {
  background : var(--cream) !important;
  margin     : 0;
  padding    : 0;
  -webkit-font-smoothing : antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
}

/* hide all streamlit chrome */
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

/* Remove Streamlit's default top padding */
.main .block-container { padding-top: 0 !important; }
section.main > div { padding-top: 0 !important; }
[data-testid="stMain"] > div:first-child { padding-top: 0 !important; }

.block-container,
[data-testid="stMainBlockContainer"] {
  padding    : 0 !important;
  max-width  : 100% !important;
}
/* remove streamlit default top padding */
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
.stVerticalBlock {
  padding-top    : 0 !important;
  margin-top     : 0 !important;
}
/* iframe wrapper - invisible but JS still runs */
[data-testid="stCustomComponentV1"] {
  height     : 1px !important;
  min-height : 0 !important;
  overflow   : hidden !important;
  margin     : 0 !important;
  padding    : 0 !important;
}
[data-testid="stCustomComponentV1"] > div {
  height     : 1px !important;
  overflow   : hidden !important;
  margin     : 0 !important;
  padding    : 0 !important;
}
[data-testid="stCustomComponentV1"] iframe {
  height     : 1px !important;
  min-height : 0 !important;
  opacity    : 0 !important;
  pointer-events: none;
  position   : absolute !important;
}

/* scrollbar */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background    : var(--border);
  border-radius : 4px;
}
::-webkit-scrollbar-thumb:hover { background: var(--faint); }

/* ═══════════════════════════════════════════════════════════════
   HEADER — glass morphism, sticky
   ═══════════════════════════════════════════════════════════════ */
.somo-header {
  position        : sticky;
  top             : 0;
  z-index         : 900;
  background      : rgba(253,247,238,.94);
  backdrop-filter : blur(20px) saturate(1.6);
  -webkit-backdrop-filter: blur(20px) saturate(1.6);
  border-bottom   : 1px solid var(--border-soft);
  box-shadow      : 0 1px 0 var(--border-soft),
                    0 2px 16px rgba(26,18,8,.04);
}
.somo-header-inner {
  display         : flex;
  align-items     : center;
  justify-content : space-between;
  max-width       : 820px;
  margin          : 0 auto;
  padding         : .72rem 1.5rem;
}

/* brand */
.somo-brand { display: flex; align-items: center; gap: 11px; }
.somo-logo  {
  width           : 38px;
  height          : 38px;
  border-radius   : 11px;
  background      : linear-gradient(145deg, var(--amber), var(--orange));
  display         : flex;
  align-items     : center;
  justify-content : center;
  font-family     : var(--fh) !important;
  font-size       : 17px;
  font-weight     : 900;
  color           : #fff;
  box-shadow      : var(--shadow-amber),
                    inset 0 1px 0 rgba(255,255,255,.22);
  flex-shrink     : 0;
  letter-spacing  : -.5px;
}
.somo-name {
  font-family : var(--fh) !important;
  font-size   : 1.05rem;
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
  font-size      : .55rem;
  color          : var(--light);
  letter-spacing : 1px;
  text-transform : uppercase;
  margin-top     : 3px;
}

/* right side */
.somo-hdr-right { display: flex; align-items: center; gap: 7px; }

.somo-mode-chip {
  display         : inline-flex;
  align-items     : center;
  gap             : 5px;
  font-family     : var(--fb) !important;
  font-size       : .62rem;
  font-weight     : 600;
  padding         : .26rem .72rem;
  border-radius   : 20px;
  transition      : all var(--dur-mid) ease;
  white-space     : nowrap;
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
  box-shadow  : var(--shadow-amber);
}

.somo-online {
  display     : flex;
  align-items : center;
  gap         : 5px;
  font-family : var(--fb) !important;
  font-size   : .6rem;
  color       : var(--green);
  white-space : nowrap;
}
.somo-dot {
  width           : 7px;
  height          : 7px;
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
  font-size      : .58rem;
  font-weight    : 600;
  color          : var(--muted);
  background     : var(--warm);
  border         : 1.5px solid var(--border);
  border-radius  : 20px;
  padding        : .22rem .7rem;
  white-space    : nowrap;
  letter-spacing : .2px;
}

/* ═══════════════════════════════════════════════════════════════
   LAYOUT WRAPPER
   ═══════════════════════════════════════════════════════════════ */
.somo-wrap {
  max-width  : 820px;
  margin     : 0 auto;
  padding    : 2rem 1.5rem 7rem;
  min-height : calc(100vh - 60px);
}

/* ═══════════════════════════════════════════════════════════════
   WELCOME SCREEN
   ═══════════════════════════════════════════════════════════════ */
.somo-welcome {
  text-align  : center;
  padding     : 2.2rem 0 1.8rem;
}

.somo-eyebrow {
  display         : inline-flex;
  align-items     : center;
  gap             : 7px;
  background      : linear-gradient(135deg, var(--amber), var(--orange));
  color           : #fff;
  font-family     : var(--fb) !important;
  font-size       : .62rem;
  font-weight     : 700;
  letter-spacing  : 1.4px;
  text-transform  : uppercase;
  padding         : .3rem 1rem;
  border-radius   : 30px;
  margin-bottom   : 1.3rem;
  box-shadow      : var(--shadow-amber);
  animation       : popIn .55s var(--ease-spring) both;
}
@keyframes popIn {
  from { opacity: 0; transform: scale(.72) translateY(6px); }
  to   { opacity: 1; transform: scale(1)   translateY(0);   }
}

.somo-headline {
  font-family    : var(--fh) !important;
  font-size      : clamp(2.2rem, 6vw, 3.4rem);
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
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0);    }
}

.somo-subtext {
  font-family   : var(--fb) !important;
  font-size     : .9rem;
  color         : var(--muted);
  line-height   : 1.75;
  max-width     : 440px;
  margin        : 0 auto 2rem;
  animation     : riseUp .5s ease-out .15s both;
}

/* feature cards grid */
.somo-cards {
  display               : grid;
  grid-template-columns : repeat(3, 1fr);
  gap                   : .65rem;
  max-width             : 580px;
  margin                : 0 auto 1.6rem;
  animation             : riseUp .5s ease-out .22s both;
}
.somo-card {
  background    : var(--card);
  border        : 1.5px solid var(--border-soft);
  border-radius : 16px;
  padding       : 1.1rem .8rem .9rem;
  text-align    : center;
  cursor        : default;
  transition    : border-color var(--dur-mid) ease,
                  transform    var(--dur-mid) var(--ease-spring),
                  box-shadow   var(--dur-mid) ease;
  position      : relative;
  overflow      : hidden;
}
.somo-card::before {
  content    : '';
  position   : absolute;
  inset      : 0;
  background : linear-gradient(135deg, rgba(245,158,11,.04), rgba(234,88,12,.04));
  opacity    : 0;
  transition : opacity var(--dur-mid) ease;
}
.somo-card:hover { 
  transform    : translateY(-4px);
  border-color : var(--amber);
  box-shadow   : 0 8px 28px rgba(0,0,0,.1);
}
.somo-card:hover::before { opacity: 1; }
.somo-card-icon {
  font-size     : 1.65rem;
  display       : block;
  margin-bottom : .45rem;
  filter        : drop-shadow(0 2px 6px rgba(0,0,0,.12));
}
.somo-card-name {
  font-family   : var(--fb) !important;
  font-size     : .75rem;
  font-weight   : 700;
  color         : var(--text);
  margin-bottom : .22rem;
}
.somo-card-hint {
  font-family : var(--fb) !important;
  font-size   : .62rem;
  color       : var(--light);
  font-style  : italic;
  line-height : 1.4;
}

/* prompt chips */
.somo-chips {
  display         : flex;
  flex-wrap       : wrap;
  gap             : .45rem;
  justify-content : center;
  margin-bottom   : 1.4rem;
  animation       : riseUp .5s ease-out .3s both;
}
.somo-chip {
  background    : var(--warm);
  border        : 1.5px solid var(--border-soft);
  border-radius : 20px;
  padding       : .3rem .82rem;
  font-family   : var(--fb) !important;
  font-size     : .7rem;
  color         : var(--muted);
  transition    : all var(--dur-fast) ease;
  cursor        : default;
  white-space   : nowrap;
}
.somo-chip:hover {
  border-color : var(--amber);
  color        : var(--orange);
  background   : rgba(245,158,11,.07);
}

/* ═══════════════════════════════════════════════════════════════
   CHAT AREA
   ═══════════════════════════════════════════════════════════════ */
.somo-stats {
  display     : flex;
  align-items : center;
  gap         : 1.2rem;
  padding     : .55rem 0 .5rem;
  font-family : var(--fb) !important;
  font-size   : .66rem;
  color       : var(--faint);
  border-bottom : 1px solid var(--border-soft);
  margin-bottom : .8rem;
  flex-wrap   : wrap;
}
.somo-stat { display: flex; align-items: center; gap: 4px; }
.somo-stat b { color: var(--muted); font-weight: 600; }

.somo-divider {
  text-align  : center;
  font-family : var(--fb) !important;
  font-size   : .62rem;
  color       : var(--faint);
  margin      : .9rem 0;
  position    : relative;
  letter-spacing: .5px;
}
.somo-divider::before, .somo-divider::after {
  content    : '';
  position   : absolute;
  top        : 50%;
  width      : calc(50% - 60px);
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
  margin-bottom   : .95rem;
  animation       : msgIn .2s ease-out;
}
.somo-msg-ai {
  display       : flex;
  align-items   : flex-start;
  gap           : 11px;
  margin-bottom : 1.75rem;
  animation     : msgIn .2s ease-out;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0);   }
}

/* avatar */
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
  letter-spacing  : -.3px;
}

/* message body */
.somo-msg-user .somo-body { max-width: 64%; }
.somo-msg-ai  .somo-body  { flex: 1; max-width: 100%; min-width: 0; }

.somo-sender {
  font-family    : var(--fb) !important;
  font-size      : .55rem;
  color          : var(--faint);
  margin-bottom  : .2rem;
  letter-spacing : .6px;
  text-transform : uppercase;
}
.somo-msg-user .somo-sender { display: none; }

/* bubble: user */
.somo-bubble-user {
  background    : linear-gradient(135deg, #eff6ff, #e0effe);
  border        : 1.5px solid #bfdbfe;
  border-radius : 18px 5px 18px 18px;
  padding       : .65rem 1.05rem;
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  line-height   : 1.68;
  color         : var(--text);
  word-break    : break-word;
  display       : inline-block;
  box-shadow    : 0 1px 4px rgba(59,130,246,.08);
}

/* bubble: ai (open, no border) */
.somo-bubble-ai {
  background  : transparent;
  padding     : .15rem 0;
  font-family : var(--fb) !important;
  font-size   : .9rem;
  line-height : 1.82;
  color       : var(--text);
  word-break  : break-word;
}

/* mode label */
.somo-mode-label {
  display        : inline-flex;
  align-items    : center;
  gap            : 5px;
  font-family    : var(--fb) !important;
  font-size      : .58rem;
  font-weight    : 700;
  letter-spacing : .9px;
  text-transform : uppercase;
  color          : var(--amber);
  margin-bottom  : .45rem;
  padding        : .14rem .52rem;
  background     : rgba(245,158,11,.08);
  border         : 1px solid rgba(245,158,11,.2);
  border-radius  : 6px;
}

/* timestamp + word count + copy row */
.somo-meta-row {
  display     : flex;
  align-items : center;
  gap         : 7px;
  margin-top  : .42rem;
  flex-wrap   : wrap;
}
.somo-ts {
  font-family : var(--fb) !important;
  font-size   : .56rem;
  color       : var(--faint);
}
.somo-wc {
  display       : inline-flex;
  align-items   : center;
  gap           : 3px;
  font-family   : var(--fb) !important;
  font-size     : .56rem;
  color         : var(--faint);
  background    : var(--warm);
  border        : 1px solid var(--border-soft);
  padding       : .08rem .38rem;
  border-radius : 6px;
}
.somo-copy {
  display       : inline-flex;
  align-items   : center;
  gap           : 4px;
  font-family   : var(--fb) !important;
  font-size     : .6rem;
  font-weight   : 500;
  color         : var(--muted);
  background    : var(--warm);
  border        : 1px solid var(--border-soft);
  border-radius : 7px;
  padding       : .16rem .52rem;
  cursor        : pointer;
  transition    : all var(--dur-fast) ease;
  user-select   : none;
}
.somo-copy:hover {
  background   : var(--border);
  color        : var(--text);
  border-color : var(--border);
}
.somo-copy:active { transform: scale(.94); }
.somo-msg-user .somo-ts { display: block; text-align: right; margin-top: .28rem; }

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
  margin       : .9rem 0 .3rem;
  line-height  : 1.25;
}
.somo-bubble-ai h1 { font-size: 1.18rem; }
.somo-bubble-ai h2 { font-size: 1.05rem; }
.somo-bubble-ai h3 { font-size: .96rem;  }
.somo-bubble-ai h4 { font-size: .9rem;   }

.somo-bubble-ai code {
  background    : rgba(245,158,11,.1);
  border        : 1px solid rgba(245,158,11,.2);
  padding       : .1rem .36rem;
  border-radius : 5px;
  font-size     : .78rem;
  color         : var(--orange);
  font-family   : 'Courier New', 'SF Mono', monospace !important;
}

.somo-bubble-ai pre {
  background    : var(--warm);
  border        : 1.5px solid var(--border);
  border-radius : 12px;
  padding       : 1rem 1.1rem;
  overflow-x    : auto;
  margin        : .7rem 0;
}
.somo-bubble-ai pre code {
  background : none;
  border     : none;
  padding    : 0;
  color      : var(--green);
  font-size  : .77rem;
}

.somo-bubble-ai ul,
.somo-bubble-ai ol  { padding-left: 1.3rem; margin: .35rem 0; }
.somo-bubble-ai li  { margin-bottom: .28rem; }

.somo-bubble-ai blockquote {
  border-left   : 3px solid var(--amber);
  background    : linear-gradient(135deg,
                    rgba(245,158,11,.05),
                    rgba(234,88,12,.03));
  padding       : .55rem 1rem;
  border-radius : 0 10px 10px 0;
  color         : var(--muted);
  margin        : .55rem 0;
  font-style    : italic;
}

.somo-bubble-ai table {
  border-collapse : collapse;
  width           : 100%;
  margin          : .65rem 0;
  font-size       : .8rem;
  border-radius   : 8px;
  overflow        : hidden;
}
.somo-bubble-ai th {
  background  : var(--warm);
  border      : 1.5px solid var(--border);
  padding     : .42rem .75rem;
  font-weight : 700;
  color       : var(--orange);
  text-align  : left;
}
.somo-bubble-ai td {
  border  : 1px solid var(--border-soft);
  padding : .38rem .75rem;
}
.somo-bubble-ai tr:nth-child(even) td {
  background : rgba(245,158,11,.025);
}

.somo-bubble-ai hr.md-hr {
  border     : none;
  border-top : 1.5px solid var(--border-soft);
  margin     : .8rem 0;
}
.somo-bubble-ai p { margin: .35rem 0; }

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
  max-width  : 820px;
  margin     : 0 auto;
  padding    : .5rem 1.5rem 0;
}
.somo-cd-box {
  display       : flex;
  align-items   : center;
  gap           : 13px;
  background    : linear-gradient(135deg, #fffbeb, #fff7d6);
  border        : 2px solid var(--amber);
  border-radius : 16px;
  padding       : .95rem 1.4rem;
  font-family   : var(--fb) !important;
  font-size     : .875rem;
  color         : #92400e;
  box-shadow    : 0 4px 20px rgba(245,158,11,.14);
}
.somo-cd-icon { font-size: 1.5rem; }
.somo-cd-sec  {
  color       : var(--orange);
  font-size   : 1.05rem;
  font-weight : 700;
}

/* ═══════════════════════════════════════════════════════════════
   INPUT BAR
   ═══════════════════════════════════════════════════════════════ */
/* hide streamlit's native chat input completely */
[data-testid="stChatInputSuggestions"],
[data-testid="stChatInputSuggestionsContainer"] { display: none !important; }

/* Style native chat input beautifully */
[data-testid="stBottom"] {
  background: linear-gradient(to top, #fdf7ee 72%, transparent) !important;
  padding: .4rem 0 max(.55rem, env(safe-area-inset-bottom)) !important;
  border-top: none !important;
}
[data-testid="stChatInputContainer"] {
  max-width: 780px !important;
  margin: 0 auto !important;
  padding: 0 1rem !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stChatInputContainer"] > div {
  background: #fffef9 !important;
  border: 2px solid #e8dfd3 !important;
  border-radius: 18px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.06) !important;
  padding: .4rem .5rem .4rem .9rem !important;
}
[data-testid="stChatInputContainer"]:focus-within > div {
  border-color: #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245,158,11,.12), 0 1px 4px rgba(0,0,0,.06) !important;
}
[data-testid="stChatInputTextArea"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: .88rem !important;
  color: #3d2c1e !important;
  background: transparent !important;
}
[data-testid="stChatInputTextArea"]::placeholder {
  color: #c4b49e !important;
}
/* Send button */
[data-testid="stChatInputSubmitButton"] button {
  background: linear-gradient(135deg, #f59e0b, #f97316) !important;
  border: none !important;
  border-radius: 11px !important;
  width: 36px !important;
  height: 36px !important;
  box-shadow: 0 3px 10px rgba(245,158,11,.35) !important;
  color: white !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
  transform: scale(1.08) !important;
  box-shadow: 0 4px 16px rgba(245,158,11,.45) !important;
}
/* Footer text below input */
[data-testid="stBottom"]::after {
  content: 'Somo AI · Usmonov Sodiq (@Somo_AI) · DeepSeek R1 + Gemini';
  display: block;
  text-align: center;
  font-size: .52rem;
  color: #d4c4b0;
  padding: .15rem 0 .3rem;
  letter-spacing: .3px;
  font-family: sans-serif;
}

/* ── CUSTOM FIXED INPUT BAR ── */
#somo-bar {
  position      : fixed;
  bottom        : 0; left : 0; right : 0;
  z-index       : 9999;
  background    : linear-gradient(to top, var(--cream) 70%, transparent);
  padding       : .5rem 0 .6rem;
  padding-bottom: max(.6rem, env(safe-area-inset-bottom));
}
#somo-bar-inner {
  max-width     : 820px;
  margin        : 0 auto;
  padding       : 0 1.2rem;
  display       : flex;
  flex-direction: column;
  gap           : .35rem;
}
/* image preview strip */
#somo-img-preview {
  display       : none;
  align-items   : center;
  gap           : .5rem;
  background    : var(--card);
  border        : 1.5px solid var(--border);
  border-radius : 12px;
  padding       : .4rem .7rem;
  font-size     : .75rem;
  color         : var(--muted);
}
#somo-img-preview img {
  height        : 40px;
  border-radius : 6px;
  object-fit    : cover;
}
#somo-img-preview.visible { display: flex; }
#somo-img-rm {
  margin-left   : auto;
  cursor        : pointer;
  font-size     : 1rem;
  color         : var(--light);
  line-height   : 1;
}
#somo-img-rm:hover { color: var(--orange); }
/* input row */
#somo-row {
  display       : flex;
  align-items   : flex-end;
  gap           : .5rem;
}
/* + button */
#somo-plus {
  flex-shrink   : 0;
  width         : 40px; height : 40px;
  border-radius : 50%;
  background    : var(--card);
  border        : 1.5px solid var(--border);
  display       : flex;
  align-items   : center;
  justify-content:center;
  cursor        : pointer;
  font-size     : 1.25rem;
  color         : var(--muted);
  box-shadow    : var(--shadow-sm);
  transition    : all .15s ease;
  user-select   : none;
  position      : relative;
}
#somo-plus:hover { border-color:var(--amber); color:var(--amber); transform:scale(1.08); }
#somo-file-inp   { display:none; }
/* textarea wrap */
#somo-ta-wrap {
  flex          : 1;
  background    : var(--card);
  border        : 2px solid var(--border);
  border-radius : 18px;
  box-shadow    : var(--shadow-sm);
  display       : flex;
  align-items   : flex-end;
  padding       : .45rem .55rem .45rem .85rem;
  transition    : border-color .15s ease, box-shadow .15s ease;
}
#somo-ta-wrap:focus-within {
  border-color  : var(--amber);
  box-shadow    : 0 0 0 3px rgba(245,158,11,.12), var(--shadow-sm);
}
#somo-ta {
  flex          : 1;
  background    : transparent;
  border        : none;
  outline       : none;
  resize        : none;
  font-family   : var(--fb);
  font-size     : .875rem;
  color         : var(--text);
  line-height   : 1.45;
  max-height    : 120px;
  overflow-y    : auto;
  padding       : 0;
  scrollbar-width: none;
}
#somo-ta::placeholder { color: var(--light); }
/* send button */
#somo-send {
  flex-shrink   : 0;
  width         : 36px; height: 36px;
  border-radius : 11px;
  background    : linear-gradient(135deg, var(--amber), var(--orange));
  border        : none;
  display       : flex;
  align-items   : center;
  justify-content:center;
  cursor        : pointer;
  box-shadow    : 0 3px 10px rgba(245,158,11,.35);
  transition    : all .15s ease;
  color         : #fff;
  font-size     : 1rem;
}
#somo-send:hover { transform:scale(1.07); box-shadow:0 4px 16px rgba(245,158,11,.45); }
#somo-send:disabled { opacity:.45; cursor:default; transform:none; }

.somo-input-footer {
  text-align     : center;
  font-family    : var(--fb) !important;
  font-size      : .55rem;
  color          : var(--faint);
  padding        : .3rem 0 .6rem;
  letter-spacing : .4px;
}

/* ═══════════════════════════════════════════════════════════════
   STREAMLIT BUTTONS (random + clear)
   ═══════════════════════════════════════════════════════════════ */
.stButton > button {
  background    : var(--card) !important;
  border        : 1.5px solid var(--border) !important;
  border-radius : 12px !important;
  color         : var(--muted) !important;
  font-family   : var(--fb) !important;
  font-size     : .78rem !important;
  font-weight   : 500 !important;
  padding       : .38rem 1rem !important;
  transition    : all var(--dur-fast) ease !important;
  box-shadow    : var(--shadow-xs) !important;
}
.stButton > button:hover {
  border-color : var(--amber) !important;
  color        : var(--orange) !important;
  background   : rgba(245,158,11,.05) !important;
  transform    : translateY(-1px) !important;
  box-shadow   : 0 3px 12px rgba(0,0,0,.08) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ═══════════════════════════════════════════════════════════════
   KaTeX
   ═══════════════════════════════════════════════════════════════ */
.katex { font-size: 1em !important; color: var(--text) !important; }
.katex-display {
  overflow-x : auto;
  padding    : .35rem 0;
  margin     : .4rem 0;
}

/* ═══════════════════════════════════════════════════════════════
   MOBILE
   ═══════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  .somo-header-inner { padding: .65rem 1rem; }
  .somo-by           { display: none; }
  .somo-name         { font-size: .95rem; }
  .somo-logo         { width: 34px; height: 34px; font-size: 15px; }
  .somo-wrap         { padding: 1.5rem 1rem 9rem; }
  .somo-headline     { font-size: clamp(1.8rem, 9vw, 2.6rem); }
  .somo-subtext      { font-size: .83rem; }
  .somo-cards        { grid-template-columns: repeat(2, 1fr); max-width: 100%; }
  .somo-msg-user .somo-body { max-width: 88%; }
  .somo-msgs-wrap { padding-bottom: 9rem !important; }
  .somo-bubble-user,
  .somo-bubble-ai    { font-size: .845rem; }
  .somo-cd-wrap      { padding: .5rem 1rem 0; }
  #somo-bar-inner { padding: 0 .75rem; }
}
@media (max-width: 380px) {
  .somo-cards { grid-template-columns: 1fr 1fr; }
  .somo-chips { gap: .35rem; }
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
#  SIDEBAR — Streamlit native
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center;padding:8px 0 20px;">
        <div style="width:52px;height:52px;border-radius:16px;background:linear-gradient(135deg,#f59e0b,#f97316);
                    display:inline-flex;align-items:center;justify-content:center;font-size:22px;font-weight:900;
                    color:white;box-shadow:0 4px 20px rgba(245,158,11,0.4);font-family:'Fraunces',serif;margin-bottom:10px;">S</div>
        <div style="font-size:18px;font-weight:900;color:#3d2c1e;font-family:'Fraunces',serif;">Somo <em style='color:#f97316;'>AI</em></div>
        <div style="font-size:10px;color:#c4b49e;letter-spacing:2px;font-weight:700;margin-top:2px;">BY USMONOV SODIQ</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    st.markdown('<p style="font-size:10px;font-weight:700;color:#c4b49e;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Navigatsiya</p>', unsafe_allow_html=True)

    _nav_pages = [
        ("chat",      "💬", "Chat AI"),
        ("excel",     "📊", "Excel Generator"),
        ("word",      "📝", "Word Generator"),
        ("code",      "💻", "Kod Generator"),
        ("html",      "🌐", "HTML Generator"),
        ("csv",       "📋", "CSV Generator"),
        ("analyze",   "🔍", "Hujjat Tahlili"),
    ]
    for _pid, _picon, _plabel in _nav_pages:
        _is_active = st.session_state.page == _pid
        if st.button(
            f"{_picon}  {_plabel}",
            key=f"nav_{_pid}",
            use_container_width=True,
            type="primary" if _is_active else "secondary"
        ):
            st.session_state.page = _pid
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Chat settings (only on chat page)
    if st.session_state.page == "chat":
        st.markdown('<p style="font-size:10px;font-weight:700;color:#c4b49e;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Chat Sozlamalari</p>', unsafe_allow_html=True)
        _prov_label = "Gemini 2.0 Flash" if st.session_state.use_gemini else "DeepSeek R1"
        st.markdown(f'<div style="font-size:12px;color:#8a7968;margin-bottom:8px;">🤖 AI: <b style=\'color:#f59e0b;\'>{_prov_label}</b></div>', unsafe_allow_html=True)

        if st.button("🔄  AI ni almashtirish", use_container_width=True, key="switch_ai"):
            st.session_state.use_gemini = not st.session_state.use_gemini
            st.rerun()

        if st.button("🗑️  Chatni tozalash", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.session_state.active_mode = "general"
            st.rerun()

        _msg_cnt = len(st.session_state.messages)
        _ai_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
        _total_words = sum(wc(m["content"]) for m in _ai_msgs)

        st.markdown(f"""
        <div style="background:#fdf7ee;border:1px solid #e8dfd3;border-radius:12px;padding:12px;margin-top:8px;">
            <div style="font-size:11px;color:#8a7968;margin-bottom:6px;font-weight:600;">📊 Sessiya</div>
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#5a4a3a;margin:3px 0;">
                <span>💬 Xabarlar</span><b>{_msg_cnt}</b>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#5a4a3a;margin:3px 0;">
                <span>✍️ So'zlar</span><b>{_total_words}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Random prompt button
    if st.button("🎲  Tasodifiy ilhom", use_container_width=True, key="rand_sb"):
        st.session_state.rand_trigger = random.choice(RAND_PROMPTS)
        st.session_state.page = "chat"
        st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:16px 0 4px;">
        <div style="font-size:10px;color:#d4c4b0;line-height:1.8;">
            Somo AI · DeepSeek R1 + Gemini<br>
            Usmonov Sodiq (@Somo_AI)<br>
            <span style="color:#e8dfd3;">v4.1 · 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════
_am = st.session_state.active_mode
_mm = MODE_META.get(_am, MODE_META["general"])
_badge = "Gemini 2.0 ✦" if st.session_state.use_gemini else "DeepSeek R1 ✦"

_chip_cls = "on" if _am != "general" else "off"
_chip_html = (
    '<div class="somo-mode-chip ' + _chip_cls + '">' +
    _mm["icon"] + " " + _mm["label"] +
    '</div>'
)

st.markdown(
    '<div class="somo-header">' +
    '<div class="somo-header-inner">' +
    '<div class="somo-brand">' +
    '<div class="somo-logo">S</div>' +
    '<div>' +
    '<div class="somo-name">Somo <em>AI</em></div>' +
    '<div class="somo-by">BY USMONOV SODIQ</div>' +
    '</div></div>' +
    '<div class="somo-hdr-right">' +
    _chip_html +
    '<div class="somo-online"><div class="somo-dot"></div>Online</div>' +
    '<div class="somo-model-pill">' + _badge + '</div>' +
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
        '<div class="somo-welcome">' +
        '<div class="somo-eyebrow">✦ ' + gi + ' ' + gt + '</div>' +
        '<div class="somo-headline">Ijodingizni<br><em>kuchlaytiring</em></div>' +
        '<div class="somo-subtext">'
        'Shunchaki xabar yozing — esse, she\'r, nutq, tarjima yoki istalgan savol.<br>'
        'Somo AI mavzudan rejimni o\'zi aniqlaydi. 🚀' +
        '</div>' +
        '<div class="somo-cards">' +
        '<div class="somo-card"><span class="somo-card-icon">✍️</span>' +
        '<div class="somo-card-name">Esse / Referat</div>' +
        '<div class="somo-card-hint">"Vatan haqida esse yoz"</div></div>' +
        '<div class="somo-card"><span class="somo-card-icon">📖</span>' +
        '<div class="somo-card-name">Hikoya / She\'r</div>' +
        '<div class="somo-card-hint">"Bahor haqida she\'r"</div></div>' +
        '<div class="somo-card"><span class="somo-card-icon">🎤</span>' +
        '<div class="somo-card-name">Nutq</div>' +
        '<div class="somo-card-hint">"Yoshlar haqida nutq"</div></div>' +
        '<div class="somo-card"><span class="somo-card-icon">💡</span>' +
        '<div class="somo-card-name">G\'oyalar</div>' +
        '<div class="somo-card-hint">"Startup g\'oyalari ber"</div></div>' +
        '<div class="somo-card"><span class="somo-card-icon">🌍</span>' +
        '<div class="somo-card-name">Tarjima</div>' +
        '<div class="somo-card-hint">"Translate to English"</div></div>' +
        '<div class="somo-card"><span class="somo-card-icon">📋</span>' +
        '<div class="somo-card-name">Xulosa / Tahlil</div>' +
        '<div class="somo-card-hint">"Ushbu matnni tahlil qil"</div></div>' +
        '</div>' +
        '<div class="somo-chips">' +
        '<div class="somo-chip">📝 "Ekologiya esse"</div>' +
        '<div class="somo-chip">🌸 "Bahor haqida she\'r"</div>' +
        '<div class="somo-chip">🎤 "Maktab nutqi"</div>' +
        '<div class="somo-chip">💡 "10 ta biznes g\'oya"</div>' +
        '<div class="somo-chip">🌍 "Hello — o\'zbekcha"</div>' +
        '</div></div>',
        unsafe_allow_html=True
    )

    # random button
    c1, c2, c3 = st.columns([1.4, 2, 1.4])
    with c2:
        if st.button("🎲  Tasodifiy ilhom", use_container_width=True, key="rand"):
            st.session_state.rand_trigger = random.choice(RAND_PROMPTS)
            st.rerun()

else:
    # ── CHAT VIEW ──────────────────────────────────────────────────
    # stats bar
    _ai_msgs  = [m for m in msgs if m["role"] == "assistant"]
    _usr_msgs = [m for m in msgs if m["role"] == "user"]
    _total_w  = sum(wc(m["content"]) for m in _ai_msgs)
    gi2, gt2  = get_greeting()
    st.markdown(
        '<div class="somo-stats">' +
        '<span class="somo-stat">' + gi2 + ' &nbsp;' + gt2 + '</span>' +
        '<span class="somo-stat">💬 <b>' + str(len(_usr_msgs)) + '</b> savol</span>' +
        '<span class="somo-stat">✍️ <b>' + str(_total_w) + '</b> so\'z</span>' +
        '</div>',
        unsafe_allow_html=True
    )

    # clear button
    cc1, cc2, cc3 = st.columns([3, 1.4, 3])
    with cc2:
        if st.button("🗑️  Tozalash", use_container_width=True, key="clr"):
            st.session_state.messages    = []
            st.session_state.active_mode = "general"
            st.session_state.use_gemini  = False
            st.rerun()

    st.markdown('<div class="somo-divider">Suhbat</div>', unsafe_allow_html=True)

    # render messages
    for i, msg in enumerate(msgs):
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
        m_mode  = msg.get("mode", "general")
        mm      = MODE_META.get(m_mode, MODE_META["general"])

        if role == "user":
            st.markdown(
                '<div class="somo-msg-user">' +
                '<div class="somo-body">' +
                '<div class="somo-bubble-user">' + content + '</div>' +
                '<div class="somo-ts">' + ts + '</div>' +
                '</div></div>',
                unsafe_allow_html=True
            )
        else:
            _wc_val = wc(content)
            label   = ""
            if m_mode != "general":
                label = (
                    '<div class="somo-mode-label">' +
                    mm["icon"] + " " + mm["label"] +
                    '</div><br>'
                )
            _cid = "scp" + str(i)
            _fid = "scf" + str(i)
            _cjs = (
                '<script>function ' + _fid + '(){' +
                'navigator.clipboard.writeText(' + repr(content) + ');' +
                'var b=document.getElementById("' + _cid + '"  );' +
                'b.innerText="✅  Nusxalandi";' +
                'setTimeout(()=>{b.innerText="📋  Nusxa"},2400);}' +
                '</script>'
            )
            st.markdown(
                '<div class="somo-msg-ai">' +
                '<div class="somo-av">S</div>' +
                '<div class="somo-body">' +
                '<div class="somo-sender">Somo AI</div>' +
                '<div class="somo-bubble-ai">' + label + md_to_html(content) + '</div>' +
                '<div class="somo-meta-row">' +
                '<span class="somo-ts">' + ts + '</span>' +
                '<span class="somo-wc">📝 ' + str(_wc_val) + ' so\'z</span>' +
                '<button class="somo-copy" id="' + _cid + '" onclick="' + _fid + '()">📋&nbsp;Nusxa</button>' +
                '</div></div></div>' + _cjs + KJ,
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)   # close somo-wrap

# ═══════════════════════════════════════════════════════════════════
#  COOLDOWN CHECK
# ═══════════════════════════════════════════════════════════════════
#  COOLDOWN CHECK
# ═══════════════════════════════════════════════════════════════════
_rem = int(st.session_state.cooldown_end - time.time())
_cooldown_active = _rem > 0
if _cooldown_active:
    time.sleep(1)
    st.rerun()

# ═══════════════════════════════════════════════════════════════════
#  CUSTOM FIXED INPUT BAR
# ═══════════════════════════════════════════════════════════════════
_cd_msg = f"""
<div id="somo-cd-notice" style="display:{'block' if _cooldown_active else 'none'};
  text-align:center;padding:.35rem;font-size:.78rem;color:#b45309;font-family:var(--fb)">
  ⏳ <strong>API limiti.</strong> Kuting — <span id="somo-cd-s">{_rem}</span> soniya
</div>
"""


# ── Native chat input ──────────────────────────────────────────
prompt = st.chat_input("Xabar yozing… (esse, she'r, nutq…)", disabled=_cooldown_active)

if not prompt and st.session_state.rand_trigger:
    prompt = st.session_state.rand_trigger
    st.session_state.rand_trigger = None

# ═══════════════════════════════════════════════════════════════════
#  PROCESS MESSAGE
# ═══════════════════════════════════════════════════════════════════
#
#  Jarayon:
#  1. detect_mode()  — rejimni aniqlash
#  2. build_system_prompt()  — rejimga mos system prompt
#  3. User bubbleni ko'rsatish
#  4. Typing placeholder (miltillovchi kursor)
#  5. Groq stream — birinchi urinish
#     429/rate_limit → Gemini ga o'tish
#     Ikkalasi ham 429 → 90s cooldown timer
#  6. Streaming render (real-time)
#  7. Javobni session tarixiga saqlash
#
# ═══════════════════════════════════════════════════════════════════
if prompt and prompt.strip():
    utxt   = prompt.strip()
    now    = get_time()
    mode   = detect_mode(utxt)
    mm     = MODE_META.get(mode, MODE_META["general"])
    syspmt = build_system_prompt(mode)

    # ── check if image attached (set by JS paste or file pick) ──
    _img_data = st.session_state.get("uploaded_img", None)

    st.session_state.active_mode = mode
    st.session_state.messages.append(
        {"role": "user", "content": utxt, "time": now, "mode": mode}
    )

    # user bubble (show image thumbnail if attached)
    _img_preview = ""
    if _img_data:
        _img_preview = (
            '<img src="data:' + _img_data["mime"] + ';base64,' + _img_data["b64"] +
            '" style="max-width:160px;border-radius:10px;margin-bottom:6px;display:block">' +
            '<span style="font-size:.7rem;color:#888">📎 ' + _img_data["name"] + '</span>'
        )
    st.markdown(
        '<div class="somo-msg-user">' +
        '<div class="somo-body">' +
        '<div class="somo-bubble-user">' + _img_preview + utxt + '</div>' +
        '<div class="somo-ts">' + now + '</div>' +
        '</div></div>',
        unsafe_allow_html=True
    )

    # typing indicator placeholder
    ph = st.empty()
    ph.markdown(
        '<div class="somo-msg-ai">' +
        '<div class="somo-av">S</div>' +
        '<div class="somo-body">' +
        '<div class="somo-sender">Somo AI</div>' +
        '<div class="somo-bubble-ai"><span class="somo-cur"></span></div>' +
        '</div></div>',
        unsafe_allow_html=True
    )

    # mode label for streaming
    _lbl = ""
    if mode != "general":
        _lbl = (
            '<div class="somo-mode-label">' +
            mm["icon"] + " " + mm["label"] +
            '</div><br>'
        )

    def render(text: str, cursor: bool = False, ts: str = "") -> None:
        _cur = '<span class="somo-cur"></span>' if cursor else ""
        _td  = '<div class="somo-ts">' + ts + '</div>' if ts else ""
        ph.markdown(
            '<div class="somo-msg-ai">' +
            '<div class="somo-av">S</div>' +
            '<div class="somo-body">' +
            '<div class="somo-sender">Somo AI</div>' +
            '<div class="somo-bubble-ai">' + _lbl + md_to_html(text) + _cur + '</div>' +
            _td +
            '</div></div>' + KJ,
            unsafe_allow_html=True
        )

    # ── Groq streaming ────────────────────────────────────────────
    def strip_think(text: str) -> str:
        """DeepSeek R1 <think>...</think> ichki fikrlarini yashiradi."""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def stream_groq() -> str:
        if not groq_client: raise Exception("no groq client")
        api_msgs = [{"role": "system", "content": syspmt}]
        for m in st.session_state.messages:
            api_msgs.append({"role": m["role"], "content": m["content"]})
        stream = groq_client.chat.completions.create(
            model       = GROQ_MODEL,
            messages    = api_msgs,
            stream      = True,
            max_tokens  = GROQ_MAX_TOK,
            temperature = GROQ_TEMP,
        )
        out = ""
        for chunk in stream:
            out += chunk.choices[0].delta.content or ""
            visible = strip_think(out)
            if visible:
                render(visible, cursor=True)
            else:
                render("💭 O'ylamoqda…", cursor=True)
        return strip_think(out)

    # ── Gemini streaming ──────────────────────────────────────────
    def stream_gemini(img_data=None) -> str:
        if not gemini_client: raise Exception("no gemini client")
        import google.generativeai as _genai
        import base64 as _b64

        # ── image mode: use vision model directly ─────────────────
        if img_data:
            vision_model = _genai.GenerativeModel("gemini-2.0-flash")
            img_part = {
                "mime_type": img_data["mime"],
                "data"     : _b64.b64decode(img_data["b64"])
            }
            full_prompt = (
                syspmt + "\n\n---\n\n"
                "Foydalanuvchi quyidagi rasm/faylni yubordi va shunday dedi:\n"
                + utxt + "\n\nRasmni diqqat bilan tahlil qilib, ijodiy va chuqur javob ber."
            )
            resp = vision_model.generate_content(
                [full_prompt, img_part],
                generation_config={
                    "temperature": GEMINI_TEMP,
                    "max_output_tokens": GEMINI_MAX_TOK,
                },
                stream=True,
            )
            out = ""
            for chunk in resp:
                try:    out += chunk.text or ""
                except: pass
                if out: render(out, cursor=True)
            return out

        # ── text mode ─────────────────────────────────────────────
        hist = []
        for m in st.session_state.messages[:-1]:
            hist.append({
                "role"  : "user" if m["role"] == "user" else "model",
                "parts" : [m["content"]]
            })
        chat = gemini_client.start_chat(history=hist)
        resp = chat.send_message(
            syspmt + "\n\n---\n\n" + utxt,
            generation_config = {
                "temperature"     : GEMINI_TEMP,
                "max_output_tokens": GEMINI_MAX_TOK,
            },
            stream=True,
        )
        out = ""
        for chunk in resp:
            try:    out += chunk.text or ""
            except: pass
            if out: render(out, cursor=True)
        return out

    # ── Dual-API fallback logic ───────────────────────────────────
    full    = ""
    is_rate = lambda e: is_rate_err(str(e))

    # image attached → always use Gemini Vision
    if _img_data:
        render("🔍 Rasm tahlil qilinmoqda…", cursor=True)
        try:
            full = stream_gemini(img_data=_img_data)
        except Exception as _ve:
            full = "❌ Rasm tahlil xatolik: " + str(_ve)
        # clear image after use
        st.session_state.uploaded_img = None
        st.session_state.show_upload  = False
    else:
        try:
            if st.session_state.use_gemini:
                full = stream_gemini()
            else:
                full = stream_groq()
                st.session_state.use_gemini = False

        except Exception as e1:
            if is_rate(e1) and not st.session_state.use_gemini:
                # Groq rate-limited → try Gemini
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
                # Gemini rate-limited → try Groq
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

    # final render (no cursor, with timestamp)
    if full:
        render(full, cursor=False, ts=get_time())

    # save to history
    st.session_state.messages.append({
        "role"    : "assistant",
        "content" : full,
        "time"    : get_time(),
        "mode"    : mode,
    })


# ═══════════════════════════════════════════════════════════════════
#  DEPLOYMENT & VERSION HISTORY
# ═══════════════════════════════════════════════════════════════════
#
#  SECRETS  (.streamlit/secrets.toml):
#    GROQ_API_KEY   = "gsk_..."     groq.com
#    GEMINI_API_KEY = "AIza..."     aistudio.google.com
#
#  REQUIREMENTS (requirements.txt):
#    streamlit>=1.32.0
#    groq>=0.8.0
#    google-generativeai>=0.8.0
#
#  ISHGA TUSHIRISH:
#    streamlit run app.py
#
# ─────────────────────────────────────────────────────────────────
#  VERSIYA TARIXI
# ─────────────────────────────────────────────────────────────────
#  v1.0  Boshlang'ich (Groq + qorong'i tema)
#  v2.0  Cream dizayn, auto rejim aniqlash
#  v2.1  Sidebar o'chirildi, layout=wide
#  v2.2  Dual-API: Groq + Gemini fallback
#  v2.3  Cooldown timer + input qulflash
#  v2.4  System prompt kuchaytirildi (Navoiy, Neruda, MLK...)
#  v2.5  AI bubble ramkasiz (Claude/ChatGPT uslubi)
#  v3.0  Copy, so'z soni, statistika, random, tozalash, salomlash
#  v4.0  Premium dizayn qayta yozildi:
#        • Glass morphism header
#        • Gradient mesh tokens
#        • Ripple pulse online dot
#        • Spring animation kartalar
#        • Gradient text headline
#        • Refined typography (Fraunces + DM Sans)
#        • 2-layered shadows
#        • Smooth input focus ring
#        • Rich bubble content CSS
#        • Strikethrough, h4, del support
#        • Improved mobile breakpoints
#        • All class names namespaced (somo-*)
#
# ═══════════════════════════════════════════════════════════════════
#  ADABIY MA'LUMOTNOMA
# ═══════════════════════════════════════════════════════════════════
#
#  O'ZBEK ADABIYOTI:
#  📜 Alisher Navoiy (1441–1501) — ilohiy metafora, g'azal nafosi
#  📜 Abdulla Oripov (1941–2016) — oddiy so'z, cheksiz og'irlik
#  📜 Erkin Vohidov (1936–2016)  — falsafiy hazil, aforizm
#  📜 Cho'lpon (1897–1938)       — impressionist detal, erkinlik
#  📜 Abdulla Qahhor (1907–1968) — keskin realizm, portret detal
#  📜 Hamid Olimjon (1909–1944)  — romantik idealizm
#
#  JAHON ADABIYOTI:
#  🌍 Pablo Neruda (1904–1973)   — hissiy metafora, kosmik romantika
#  🌍 Jaloliddin Rumi (1207–1273)— mistik paradoks, sevgi koinot
#  🌍 Anton Chekhov (1860–1904)  — ko'rsatish, tushuntirmaslik
#  🌍 O. Henry (1862–1910)       — kutilmagan burilish = haqiqat
#  🌍 García Márquez (1927–2014) — sehrli realizm, vaqt mif
#  🌍 Jorge Luis Borges (1899–1986)— borliq = matn
#
#  NOTIQLIK:
#  🎤 MLK (1929–1968)    — anafora, axloqiy yoy, vizyon
#  🎤 Churchill (1874–1965)— kulminatsiyada qisqa jumlalar
#  🎤 Obama (1961–)      — shaxsiy hikoya → universal haqiqat
#
# ═══════════════════════════════════════════════════════════════════
#  © 2026  Usmonov Sodiq  |  @Somo_AI  |  Barcha huquqlar himoyalangan
# ═══════════════════════════════════════════════════════════════════

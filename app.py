
import json
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ================================================
# THEME & PAGE
# ================================================
st.set_page_config(page_title="Bilgi Ekosistemi Oyunu 🎮", layout="wide")

# Global CSS (youthful look)
st.markdown(
    """
    <style>
    :root{
        --bg:#0f172a;
        --card:#111827;
        --muted:#94a3b8;
        --text:#e5e7eb;
        --accent:#8b5cf6;
        --accent2:#22c55e;
        --warn:#f59e0b;
        --danger:#ef4444;
        --chip:#1f2937;
    }
    html, body, [data-testid="stAppViewContainer"]{
        background: radial-gradient(1200px 600px at 10% 10%, #1f2937 0%, #0f172a 60%) fixed;
        color: var(--text);
    }
    .hero{
        background: linear-gradient(135deg, rgba(139,92,246,.9), rgba(34,197,94,.9));
        color:white; padding: 18px 22px; border-radius: 16px; 
        box-shadow: 0 10px 30px rgba(0,0,0,.3); margin-bottom: 14px;
    }
    .card{ background: var(--card); border:1px solid #1f2937; border-radius:16px; padding:16px; box-shadow: 0 6px 18px rgba(0,0,0,.2); }
    .pill{ display:inline-block; padding:4px 10px; border-radius:999px; font-size:.85rem; margin-right:6px; }
    .rel-high{ background:#052e16; color:#bbf7d0; border:1px solid #16a34a; }
    .rel-med{ background:#341b05; color:#fed7aa; border:1px solid #f59e0b; }
    .rel-low{ background:#3b0a0a; color:#fecaca; border:1px solid #ef4444; }
    .small{ color: var(--muted); font-size:.9rem; }
    .option-btn button{ width:100%; padding:14px 12px !important; border-radius:14px !important; border:1px solid #374151 !important; }
    .primary-btn button{ width:100%; padding:16px 14px !important; border-radius:14px !important; background: var(--accent) !important; color:white !important; border:0 !important; font-weight:700 !important; }
    .ghost-btn button{ width:100%; padding:16px 14px !important; border-radius:14px !important; background: #0b1220 !important; color:#e5e7eb !important; border:1px solid #334155 !important; }
    .warn-btn button{ width:100%; padding:16px 14px !important; border-radius:14px !important; background: var(--warn) !important; color:black !important; font-weight:700 !important; }
    .emoji{ font-size:1.2rem; margin-right:.4rem; }
    .dot{ width:10px; height:10px; display:inline-block; border-radius:999px; background:#374151; margin-right:6px;}
    .dot.on{ background:#22c55e; }
    .title{ font-weight:800; font-size:1.6rem; letter-spacing:.3px; }
    .score-card .metric{ font-size:1.3rem; font-weight:800; }
    .score-card .label{ color:#cbd5e1; font-size:.8rem; text-transform:uppercase; letter-spacing:1px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================================================
# DATA
# ================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_ACTORS = BASE_DIR / "data" / "actors.json"
DATA_CLASSES = BASE_DIR / "data" / "classes.json"

def _write_minimal_actors_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    minimal = [
        {
            "id": "BOT_00",
            "class_id": "BOT",
            "class_name": "Bot Ağı",
            "name": "Bot Ağı (Minimal)",
            "clues": [
                {"text": "Aynı metin + link 30 hesapta <2 dk içinde paylaşıldı.", "reliability": "High", "type": "behavioral", "rationale": "Eşzamanlılık otomasyonu işaret eder."},
                {"text": "Hesapların çoğu aynı hafta açılmış.", "reliability": "Medium", "type": "operational", "rationale": "Toplu kurulum paterni."},
                {"text": "Gece-gündüz paylaşım temposu sabit.", "reliability": "High", "type": "behavioral", "rationale": "İnsan ritminden bağımsızdır."},
                {"text": "Yanıtlar kalıp ifadelerden oluşuyor.", "reliability": "Low", "type": "content", "rationale": "Düşük bağlamsal tepki."},
                {"text": "Biyografiler boş/tek kelime.", "reliability": "Low", "type": "operational", "rationale": "Hızlı kurulum izi."}
            ]
        },
        {
            "id": "TROLL_00",
            "class_id": "TROLL",
            "class_name": "Trol Çiftliği",
            "name": "Trol Çiftliği (Minimal)",
            "clues": [
                {"text": "Hedefe özgü lakap/mem üretiliyor.", "reliability": "Medium", "type": "content", "rationale": "İnsan yaratıcılığı ve bağlam."},
                {"text": "Uzun yanıt dizileriyle tartışma dağıtılıyor.", "reliability": "High", "type": "behavioral", "rationale": "Etkileşim derinliği yüksek."},
                {"text": "Vardiya paternleri (akşam/hafta içi) görülüyor.", "reliability": "Medium", "type": "behavioral", "rationale": "Çalışma ritmi izi."},
                {"text": "Karşı argüman taklidi ve yeniden çerçeveleme.", "reliability": "Medium", "type": "content", "rationale": "Anlık bağlam takibi."},
                {"text": "Hesap yaşı dağılımı karışık.", "reliability": "Low", "type": "operational", "rationale": "Gerçekçi profil demeti."}
            ]
        }
    ]
    with path.open("w", encoding="utf-8") as f:
        json.dump(minimal, f, ensure_ascii=False, indent=2)

if not DATA_ACTORS.exists():
    _write_minimal_actors_json(DATA_ACTORS)

with DATA_ACTORS.open("r", encoding="utf-8") as f:
    ACTORS = json.load(f)

if DATA_CLASSES.exists():
    with DATA_CLASSES.open("r", encoding="utf-8") as f:
        CLASS_CARDS = json.load(f)
else:
    CLASS_CARDS = []

CLASS_ORDER = [
    ("BOT", "Bot Ağı"),
    ("TROLL", "Trol Çiftliği"),
    ("STATE_MEDIA", "Devlet Destekli Medya"),
    ("AGENCY", "Kampanya Ajansı"),
    ("GRASS", "Gönüllü Partizan Topluluk"),
    ("INFL", "Kanaat Önderi/Influencer"),
    ("NEWS", "Bağımsız Gazeteci/Haber"),
    ("FACT", "Doğrulama Kuruluşu"),
    ("TNS", "Platform Güven/Güvenlik"),
]
CLASS_NAME = {cid: cname for cid, cname in CLASS_ORDER}

CONFUSABLES = {
    "BOT": ["TROLL", "AGENCY", "GRASS", "INFL"],
    "TROLL": ["BOT", "GRASS", "INFL", "AGENCY"],
    "STATE_MEDIA": ["NEWS", "AGENCY", "FACT", "TNS"],
    "AGENCY": ["GRASS", "INFL", "NEWS", "BOT"],
    "GRASS": ["TROLL", "AGENCY", "INFL", "NEWS"],
    "INFL": ["GRASS", "NEWS", "AGENCY", "TROLL"],
    "NEWS": ["STATE_MEDIA", "FACT", "INFL", "GRASS"],
    "FACT": ["NEWS", "STATE_MEDIA", "TNS", "AGENCY"],
    "TNS": ["FACT", "STATE_MEDIA", "NEWS", "AGENCY"],
}

EMOJI = {
    "BOT":"🤖",
    "TROLL":"😈",
    "STATE_MEDIA":"🏛️",
    "AGENCY":"🎯",
    "GRASS":"🌱",
    "INFL":"🎤",
    "NEWS":"📰",
    "FACT":"✅",
    "TNS":"🛡️",
}

# ================================================
# HELPERS
# ================================================
def rel_chip(level:str)->str:
    level = (level or "").lower()
    if level.startswith("high"):
        return '<span class="pill rel-high">🟢 High</span>'
    if level.startswith("med"):
        return '<span class="pill rel-med">🟠 Medium</span>'
    return '<span class="pill rel-low">⚪ Low</span>'

def choose_clues_simple(clues):
    highs = [c for c in clues if c.get("reliability") == "High"]
    meds = [c for c in clues if c.get("reliability") == "Medium"]
    lows = [c for c in clues if c.get("reliability") == "Low"]
    rest = [c for c in clues if c not in highs + meds + lows]
    selected = []
    if highs: selected.append(highs[0])
    selected.extend(meds[:2])
    selected.extend(lows[:2])
    pool = highs[1:] + meds[2:] + lows[2:] + rest
    for c in pool:
        if len(selected) >= 5: break
        selected.append(c)
    return selected[:5]

def init_game():
    st.session_state["score"] = 0
    st.session_state["game_over"] = False
    st.session_state["used_elimination"] = False
    st.session_state["confidence"] = 70
    st.session_state["explanation"] = None

    target = random.choice(ACTORS)
    t_class = target["class_id"]
    conf_class_list = CONFUSABLES.get(t_class, [])
    options = [CLASS_NAME.get(t_class, t_class)] + [CLASS_NAME[c] for c in conf_class_list[:4] if c in CLASS_NAME]
    opts = []
    for o in options:
        if o not in opts: opts.append(o)
    random.shuffle(opts)

    st.session_state["target"] = target
    st.session_state["options"] = opts
    st.session_state["selected_guess"] = None
    st.session_state["clues_all"] = choose_clues_simple(target.get("clues", [])[:5])
    st.session_state["clues_revealed"] = 1
    st.session_state["start_ts"] = time.time()

def calc_points(correct, clues_revealed):
    base = 100
    penalty = 15 * (clues_revealed - 1)
    early_bonus = 10 * max(0, 5 - clues_revealed) if correct else 0
    if correct: return max(0, base - penalty + early_bonus)
    return max(0, base - penalty - 20)

def log_outcome(row):
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "pilot_log.csv"
    df = pd.DataFrame([row])
    if log_path.exists():
        df.to_csv(log_path, index=False, mode="a", header=False, encoding="utf-8")
    else:
        df.to_csv(log_path, index=False, encoding="utf-8")

# ================================================
# INTRO / CAROUSEL
# ================================================
def init_intro():
    st.session_state.setdefault("phase", "intro")
    st.session_state.setdefault("carousel_idx", 0)

def render_intro():
    init_intro()
    n = len(CLASS_CARDS)
    st.markdown('<div class="hero"><div class="title">Sınıfları Tanı 📚</div><div class="small">Oklarla gez — hazır olunca Oyuna Başla!</div></div>', unsafe_allow_html=True)

    if n == 0:
        st.info("Tanıtım kartları bulunamadı.")
    else:
        idx = st.session_state["carousel_idx"]
        card = CLASS_CARDS[idx]
        cid = card.get("id","")
        emoji = EMOJI.get(cid,"🔎")

        nav_cols = st.columns([1, 6, 1])
        with nav_cols[0]:
            if st.button("⟵ Önceki"):
                st.session_state["carousel_idx"] = (idx - 1) % n
                st.rerun()
        with nav_cols[2]:
            if st.button("Sonraki ⟶"):
                st.session_state["carousel_idx"] = (idx + 1) % n
                st.rerun()

        st.markdown(f"### {emoji} {card.get('name')}  <span class='small'>({idx+1}/{n})</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>{card.get('summary','')}</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Ayırt Edici Sinyaller**")
            for s in card.get("key_signals", []):
                st.markdown(f"- {s}")
        with c2:
            st.markdown("**Örnek İpuçları**")
            for s in card.get("example_clues", []):
                st.markdown(f"- {s}")

        st.markdown("---")
        dotcols = st.columns(min(n,10))
        for i in range(min(n,10)):
            with dotcols[i]:
                on = "on" if i == idx else ""
                st.markdown(f"<span class='dot {on}'></span>", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("🎮 Oyuna Başla"):
            st.session_state["phase"] = "play"
            init_game(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("⏭️ Tanıtımı Atla"):
            st.session_state["phase"] = "play"
            init_game(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("📜 Kuralları Gör"):
            st.session_state["phase"] = "rules"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ================================================
# RULES
# ================================================
def render_rules():
    st.markdown('<div class="hero"><div class="title">Kurallar 📜</div><div class="small">Kısa ve net.</div></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("#### Nasıl Oynanır?")
        st.markdown("- Başta **tek bir hedef aktör** seçilir.")
        st.markdown("- En fazla **5 ipucu** açabilirsin (sıra: **1 High → 2 Medium → 2 Low**).")
        st.markdown("- Sınıf butonuna bas, **Tahmin et** de.")
        st.markdown("- **Joker:** Bir kez “Yanlış sınıfı ele (−15)”.")
        st.markdown("#### Skor")
        st.code("Tur Puanı = 100 − 15×(ek ipucu)\nErken Doğru Bonus = 10 × (kalan ipucu)\nYanlış: Tur Puanı − 20", language="text")
        st.markdown("Örnek: 2. ipucunda doğru → **115** puan.")
        st.markdown("#### Not")
        st.markdown("- Gerçek isim yok; sadece **tipler** var.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Tanıtıma Dön"):
            st.session_state["phase"] = "intro"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("🎮 Oyuna Başla"):
            st.session_state["phase"] = "play"; init_game(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ================================================
# PHASE
# ================================================
st.session_state.setdefault("phase", "intro")
if st.session_state["phase"] == "intro":
    render_intro(); st.stop()
if st.session_state["phase"] == "rules":
    render_rules(); st.stop()

# ================================================
# PLAY
# ================================================
# init if needed
if "target" not in st.session_state:
    init_game()

target = st.session_state["target"]
true_class_name = CLASS_NAME.get(target["class_id"], target["class_id"])
clues = st.session_state["clues_all"]
revealed = st.session_state["clues_revealed"]
options = st.session_state["options"]

# Header
st.markdown('<div class="hero"><div class="title">Tahmin Zamanı 🕵️‍♀️</div><div class="small">İpucuna bak, akıllıca seç!</div></div>', unsafe_allow_html=True)

# Score & progress
s1, s2, s3 = st.columns([1,1,2])
with s1:
    st.markdown('<div class="card score-card"><div class="label">Skor</div><div class="metric">{} pts</div></div>'.format(st.session_state.get("score",0)), unsafe_allow_html=True)
with s2:
    pct = int((revealed/5)*100)
    st.progress(pct, text=f"İpucu ilerleme: {revealed}/5")
with s3:
    st.caption("Güven (%): 50 / 70 / 90 — sadece kayıt için")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("50"):
            st.session_state["confidence"] = 50
    with b2:
        if st.button("70"):
            st.session_state["confidence"] = 70
    with b3:
        if st.button("90"):
            st.session_state["confidence"] = 90
    st.caption(f"Seçili: {st.session_state['confidence']}%")

left, right = st.columns([2,1])

# LEFT: clues + actions
with left:
    st.markdown("#### İpuçları")
    for i, clue in enumerate(clues[:revealed], start=1):
        chip = rel_chip(clue.get("reliability",""))
        st.markdown(f"<div class='card'><b>İpucu {i}:</b> {clue.get('text','')}<div class='small' style='margin-top:6px;'>{chip}</div></div>", unsafe_allow_html=True)

    if not st.session_state["game_over"]:
        a1, a2 = st.columns(2)
        with a1:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("➕ Bir ipucu daha aç"):
                if st.session_state["clues_revealed"] < min(5, len(clues)):
                    st.session_state["clues_revealed"] += 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with a2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("✅ Tahmin et"):
                if st.session_state.get("selected_guess") is None:
                    st.warning("Önce bir sınıf seç.")
                else:
                    guess_name = st.session_state["selected_guess"]
                    correct = (guess_name == true_class_name)
                    pts = calc_points(correct, st.session_state["clues_revealed"])
                    st.session_state["score"] += pts
                    st.session_state["game_over"] = True
                    duration = time.time() - st.session_state["start_ts"]
                    row = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "target_actor_id": target.get("id"),
                        "target_class": true_class_name,
                        "guess_class": guess_name,
                        "correct": int(correct),
                        "clues_revealed": st.session_state["clues_revealed"],
                        "confidence": st.session_state["confidence"],
                        "explanation": st.session_state.get("explanation"),
                        "used_elimination": int(st.session_state.get("used_elimination", False)),
                        "points": pts,
                        "duration_sec": round(duration, 2),
                    }
                    log_outcome(row)
                    if correct:
                        st.balloons()
                        st.success(f"Doğru! 🎉 +{pts} puan")
                    else:
                        st.error(f"Yanlış. Doğru sınıf: **{true_class_name}** · +{pts}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success(f"Oyun bitti. Toplam skor: **{st.session_state['score']}**")
        if st.session_state["clues_revealed"] < len(clues):
            with st.expander("Açılmayan ipuçlarını gör"):
                for i, clue in enumerate(clues[revealed:], start=revealed+1):
                    chip = rel_chip(clue.get("reliability",""))
                    st.markdown(f"<div class='card'><b>İpucu {i}:</b> {clue.get('text','')}<div class='small' style='margin-top:6px;'>{chip}</div></div>", unsafe_allow_html=True)

# RIGHT: options + tools
with right:
    st.markdown("#### Sınıf Seçimi")
    st.caption("Kararını en çok hangi sinyal etkiledi? (log)")
    st.session_state["explanation"] = st.radio("Sinyal", ["Davranış","Ağ","Operasyonel","İçerik"], index=None, horizontal=True)

    # tiled class buttons with emoji
    rows = []
    row = []
    for i, opt in enumerate(options, start=1):
        row.append(opt)
        if len(row) == 3 or i == len(options):
            rows.append(row); row = []
    for row in rows:
        cols = st.columns(len(row))
        for c, opt in zip(cols, row):
            with c:
                code = None
                for k,v in CLASS_NAME.items():
                    if v == opt: code = k; break
                emo = EMOJI.get(code,"🔎")
                st.markdown('<div class="option-btn">', unsafe_allow_html=True)
                if st.button(f"{emo} {opt}"):
                    st.session_state["selected_guess"] = opt
                st.markdown('</div>', unsafe_allow_html=True)
    sel = st.session_state.get("selected_guess")
    st.caption(f"Seçili sınıf: {sel if sel else '—'}")

    st.markdown("---")
    if not st.session_state["game_over"] and not st.session_state.get("used_elimination") and len(options) > 2:
        st.markdown('<div class="warn-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Yanlış bir sınıfı ele (−15)"):
            wrongs = [o for o in options if o != true_class_name]
            if wrongs:
                remove = random.choice(wrongs)
                st.session_state["options"] = [o for o in options if o != remove]
                st.session_state["used_elimination"] = True
                st.session_state["score"] = max(0, st.session_state["score"] - 15)
                st.info(f"Elendi: {remove}")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Genç dostu arayüz · tipoloji odaklı içerik · gizlilik duyarlı")

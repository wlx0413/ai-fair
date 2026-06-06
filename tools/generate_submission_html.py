# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "songs.csv"
OUT_HTML = ROOT / "论文的" / "AI_Music_Recommendation_System_提交网页.html"
OUT_TXT = ROOT / "论文的" / "AI_Music_Recommendation_System_提交网页_source.txt"


def load_songs(limit: int = 90) -> list[dict[str, object]]:
    songs: list[dict[str, object]] = []
    with DATA.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                song = {
                    "track_id": row["track_id"],
                    "track_name": row["track_name"],
                    "artist_name": row["artist_name"],
                    "album_name": row.get("album_name", ""),
                    "genre": row.get("genre", "Pop") or "Pop",
                    "tags": row.get("tags", ""),
                    "danceability": float(row["danceability"]),
                    "energy": float(row["energy"]),
                    "valence": float(row["valence"]),
                    "tempo": float(row["tempo"]),
                    "acousticness": float(row["acousticness"]),
                    "instrumentalness": float(row["instrumentalness"]),
                    "speechiness": float(row["speechiness"]),
                    "liveness": float(row["liveness"]),
                    "popularity": float(row["popularity"]),
                    "source": row.get("source", "curated") or "curated",
                    "external_url": row.get("external_url", ""),
                    "has_audio_features": True,
                }
            except Exception:
                continue
            title = str(song["track_name"])
            artist = str(song["artist_name"])
            if title.lower().startswith("demo ") or artist.lower().startswith("ai fair artist"):
                continue
            songs.append(song)
            if len(songs) >= limit:
                break
    return songs


def build_html() -> str:
    songs_json = json.dumps(load_songs(), ensure_ascii=False, indent=2)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Music Recommendation System</title>
  <style>
    :root {{
      --bg: #070914;
      --bg2: #111629;
      --panel: rgba(20, 25, 43, .86);
      --panel2: rgba(31, 39, 64, .94);
      --text: #f8fbff;
      --muted: #a2adc7;
      --line: rgba(255,255,255,.12);
      --accent: #1ed760;
      --accent2: #7c3aed;
      --danger: #fb5b6b;
      --blue: #38bdf8;
      --shadow: 0 24px 70px rgba(0,0,0,.36);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 10% 5%, rgba(30,215,96,.18), transparent 28rem),
        radial-gradient(circle at 88% 0%, rgba(124,58,237,.24), transparent 33rem),
        radial-gradient(circle at 52% 95%, rgba(56,189,248,.13), transparent 30rem),
        linear-gradient(145deg, var(--bg), var(--bg2));
    }}
    button, input, textarea {{ font: inherit; }}
    button {{ border: 0; cursor: pointer; }}
    .shell {{ width: min(1360px, 100%); margin: 0 auto; padding: 22px; }}
    .topbar {{
      position: sticky; top: 12px; z-index: 10;
      display: flex; justify-content: space-between; align-items: center; gap: 18px;
      padding: 14px 16px; border: 1px solid var(--line); border-radius: 20px;
      background: rgba(7,9,20,.78); box-shadow: var(--shadow); backdrop-filter: blur(18px);
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; color: var(--text); text-decoration: none; }}
    .logo {{
      width: 44px; height: 44px; border-radius: 15px; display: grid; place-items: center;
      background: conic-gradient(from 20deg, #1ed760, #38bdf8, #7c3aed, #1ed760);
      color: #06110a; font-weight: 1000; box-shadow: 0 16px 36px rgba(30,215,96,.22);
    }}
    .brand small {{ display: block; color: var(--muted); margin-top: 2px; }}
    .nav {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
    .nav a {{ color: var(--muted); text-decoration: none; }}
    .pill, .ghost {{
      min-height: 38px; padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line);
      color: var(--text); background: rgba(255,255,255,.06);
    }}
    .hero {{
      display: grid; grid-template-columns: 1.55fr .8fr; gap: 22px; align-items: stretch;
      padding: 34px 0 22px;
    }}
    .hero-card, .panel {{
      border: 1px solid var(--line); border-radius: 22px;
      background: linear-gradient(145deg, rgba(22,27,48,.9), rgba(12,16,30,.86));
      box-shadow: var(--shadow); overflow: hidden;
    }}
    .hero-card {{ padding: 34px; position: relative; }}
    .eyebrow {{ color: var(--accent); font-weight: 800; letter-spacing: .08em; text-transform: uppercase; font-size: .78rem; }}
    h1 {{ margin: 10px 0 12px; font-size: clamp(2.2rem, 5vw, 4.8rem); line-height: .96; letter-spacing: -0.03em; }}
    h2 {{ margin: 0; font-size: 1.1rem; }}
    p {{ color: var(--muted); line-height: 1.55; }}
    .actions {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px; }}
    .primary, .secondary, .danger {{
      padding: 12px 16px; border-radius: 14px; font-weight: 850;
    }}
    .primary {{ color: #04120a; background: linear-gradient(135deg, var(--accent), #a6ff62); }}
    .secondary {{ color: var(--text); background: rgba(255,255,255,.09); border: 1px solid var(--line); }}
    .danger {{ color: white; background: linear-gradient(135deg, #fb7185, #ef4444); }}
    .record {{ padding: 28px; display: grid; place-items: center; min-height: 270px; }}
    .disc {{
      width: 210px; aspect-ratio: 1; border-radius: 50%;
      background: repeating-radial-gradient(circle, #111827 0 10px, #172033 11px 13px),
        conic-gradient(#1ed760, #38bdf8, #7c3aed, #1ed760);
      border: 10px solid rgba(255,255,255,.06); position: relative;
      animation: spin 20s linear infinite;
    }}
    .disc:after {{ content: ""; position: absolute; inset: 76px; border-radius: 50%; background: #f8fbff; box-shadow: inset 0 0 0 24px #111827; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }}
    .span4 {{ grid-column: span 4; }} .span5 {{ grid-column: span 5; }} .span7 {{ grid-column: span 7; }} .span12 {{ grid-column: span 12; }}
    .panel {{ padding: 20px; }}
    .head {{ display: flex; gap: 12px; align-items: flex-start; margin-bottom: 16px; }}
    .icon {{ width: 38px; height: 38px; border-radius: 13px; display: grid; place-items: center; background: rgba(30,215,96,.13); color: var(--accent); font-weight: 900; }}
    label {{ display: block; margin-bottom: 8px; color: var(--muted); font-size: .9rem; }}
    input, textarea {{
      width: 100%; border: 1px solid var(--line); border-radius: 14px; outline: none;
      color: var(--text); background: rgba(255,255,255,.055); padding: 12px 13px;
    }}
    textarea {{ resize: vertical; min-height: 136px; }}
    .input-row {{ display: grid; grid-template-columns: 1fr auto; gap: 10px; }}
    .status {{ margin-top: 10px; color: var(--muted); font-size: .9rem; min-height: 22px; }}
    .note {{ border: 1px solid rgba(30,215,96,.18); background: rgba(30,215,96,.08); padding: 12px; border-radius: 15px; color: #d7ffe5; margin-bottom: 12px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; margin-top: 12px; }}
    .metric {{ background: rgba(255,255,255,.06); border: 1px solid var(--line); border-radius: 14px; padding: 11px; }}
    .metric span {{ display: block; color: var(--muted); font-size: .78rem; }} .metric strong {{ font-size: 1.05rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; margin-top: 14px; }}
    .mini-cards {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
    .song-card {{
      padding: 15px; border-radius: 18px; border: 1px solid var(--line);
      background: linear-gradient(150deg, rgba(255,255,255,.075), rgba(255,255,255,.035));
    }}
    .song-card h3 {{ margin: 0 0 6px; font-size: 1rem; }}
    .song-card p {{ margin: 5px 0; }}
    .score-row {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; margin: 10px 0; }}
    .score {{ padding: 9px; border-radius: 12px; background: rgba(30,215,96,.12); color: #d7ffe5; font-weight: 800; }}
    .tag {{ display: inline-flex; margin: 3px 4px 3px 0; padding: 5px 8px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); font-size: .78rem; }}
    .empty {{ padding: 20px; border: 1px dashed var(--line); border-radius: 18px; color: var(--muted); text-align: center; }}
    .profile-grid {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; }}
    .daily-list {{ display: grid; gap: 8px; margin-top: 14px; }}
    .daily-row {{ display: grid; grid-template-columns: 42px 1fr auto; gap: 10px; align-items: center; padding: 10px 12px; border-radius: 14px; background: rgba(255,255,255,.055); border: 1px solid var(--line); }}
    .rank {{ width: 30px; height: 30px; border-radius: 10px; display: grid; place-items: center; background: rgba(30,215,96,.15); color: #d7ffe5; font-weight: 900; }}
    .steps {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; }}
    .step {{ padding: 14px; border-radius: 16px; background: rgba(255,255,255,.055); border: 1px solid var(--line); }}
    .small {{ font-size: .86rem; color: var(--muted); }}
    @media (max-width: 980px) {{
      .hero, .grid {{ grid-template-columns: 1fr; }}
      .span4, .span5, .span7, .span12 {{ grid-column: span 1; }}
      .cards, .mini-cards, .steps {{ grid-template-columns: 1fr; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .input-row, .daily-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <nav class="topbar">
      <a class="brand" href="#top">
        <span class="logo">AI♪</span>
        <span><strong data-i18n="title">AI Music Recommendation System</strong><small data-i18n="subtitle">Standalone HTML Submission</small></span>
      </a>
      <div class="nav">
        <a href="#recommendations" data-i18n="navRec">Recommendations</a>
        <a href="#train" data-i18n="navTrain">Training</a>
        <button class="ghost" id="langBtn">中文</button>
        <span class="pill" id="modePill" data-i18n="standalone">Standalone demo mode</span>
      </div>
    </nav>

    <header class="hero" id="top">
      <section class="hero-card">
        <div class="eyebrow" data-i18n="eyebrow">AI Fair Machine Learning Project</div>
        <h1 data-i18n="hero">Train a music recommendation model from playlist and feedback.</h1>
        <p data-i18n="heroText">This single HTML file mirrors the app UI and demonstrates the same recommendation workflow: import playlist metadata, search songs, train a hybrid model, rank songs, and generate a final 50-song mix.</p>
        <div class="actions">
          <button class="primary" id="heroRec" data-i18n="getRec">Get Recommendations</button>
          <button class="secondary" id="heroDaily" data-i18n="daily50">Generate Final 50</button>
          <a class="pill" href="#how" data-i18n="how">How training works</a>
        </div>
        <p class="small" data-i18n="truthNote">Formal app model: LightFM WARP in Python. This submission HTML uses an in-browser hybrid scoring demo so it can run without setup.</p>
      </section>
      <aside class="hero-card record"><div><div class="disc"></div><p><strong>Main Model:</strong> LightFM Hybrid Recommendation Model</p></div></aside>
    </header>

    <main class="grid">
      <section class="panel span4">
        <div class="head"><span class="icon">⇣</span><div><h2 data-i18n="importTitle">Import Playlist</h2><p data-i18n="importHint">QQ Music metadata only. No audio is downloaded.</p></div></div>
        <label data-i18n="qqLabel">QQ Music playlist URL or ID</label>
        <div class="input-row"><input id="qqInput" placeholder="https://y.qq.com/n/ryqq/playlist/123456"><button class="primary" id="qqBtn" data-i18n="importBtn">Import</button></div>
        <div class="status" id="qqStatus" data-i18n="qqStatus">Paste a playlist URL or numeric ID.</div>
      </section>

      <section class="panel span4">
        <div class="head"><span class="icon">＋</span><div><h2 data-i18n="manualTitle">Manual Playlist</h2><p data-i18n="manualHint">One song per line: Song Name - Artist Name</p></div></div>
        <textarea id="manualInput">Shape of You - Ed Sheeran
Blinding Lights - The Weeknd
Believer - Imagine Dragons
Levitating - Dua Lipa
Lose Yourself - Eminem</textarea>
        <button class="primary" id="manualBtn" data-i18n="manualBtn">Add Manual Playlist</button>
        <div class="status" id="manualStatus" data-i18n="manualStatus">Manual songs become training interactions.</div>
      </section>

      <section class="panel span4" id="train">
        <div class="head"><span class="icon">◎</span><div><h2 data-i18n="trainTitle">Train Recommendation Model</h2><p data-i18n="trainHint">Hybrid model from interactions and item features.</p></div></div>
        <div class="note" data-i18n="trainNote">Training converts songs into feature vectors and learns user preference weights from playlist, Like, and Dislike interactions.</div>
        <button class="primary" id="trainBtn" data-i18n="trainBtn">Train Model</button>
        <div class="metrics" id="modelMetrics"></div>
      </section>

      <section class="panel span7">
        <div class="head"><span class="icon">⌕</span><div><h2 data-i18n="searchTitle">Search Songs</h2><p data-i18n="searchHint">Search the embedded library. Online Deezer search is attempted when network/CORS allows it.</p></div></div>
        <div class="input-row"><input id="searchInput" placeholder="Shape, Adele, Hip-hop, Electronic"><button class="primary" id="searchBtn" data-i18n="searchBtn">Search</button></div>
        <div class="cards mini-cards" id="searchResults"><div class="empty" data-i18n="searchEmpty">Search results appear here.</div></div>
      </section>

      <section class="panel span5">
        <div class="head"><span class="icon">◒</span><div><h2 data-i18n="tasteTitle">User Taste Profile</h2><p data-i18n="tasteHint">Built from playlist songs and feedback.</p></div></div>
        <div class="profile-grid" id="tasteProfile"></div>
      </section>

      <section class="panel span12" id="recommendations">
        <div class="head"><span class="icon">★</span><div><h2 data-i18n="recTitle">Recommendations</h2><p data-i18n="recHint">Ranked by model score plus content similarity.</p></div></div>
        <div class="actions"><button class="primary" id="recBtn" data-i18n="getRec">Get Recommendations</button><button class="secondary" id="dailyBtn" data-i18n="daily50">Generate Final 50</button></div>
        <div class="cards" id="recommendationCards"><div class="empty" data-i18n="recEmpty">Add songs, train the model, then get recommendations.</div></div>
      </section>

      <section class="panel span12">
        <div class="head"><span class="icon">50</span><div><h2 data-i18n="dailyTitle">Daily Recommendation Mix</h2><p data-i18n="dailyHint">A final 50-song output playlist for submission and demo.</p></div></div>
        <button class="secondary" id="copyBtn" data-i18n="copy">Copy 50-song playlist</button>
        <div class="daily-list" id="dailyList"><div class="empty" data-i18n="dailyEmpty">Generate Final 50 to show the playlist.</div></div>
      </section>

      <section class="panel span12" id="how">
        <div class="head"><span class="icon">ML</span><div><h2 data-i18n="howTitle">How the Machine Learning Works</h2><p data-i18n="howHint">Short explanation for AI Fair.</p></div></div>
        <div class="steps">
          <div class="step"><strong>1. Interactions</strong><p data-i18n="step1">Playlist import, manual add, Like and Dislike become user-song training data.</p></div>
          <div class="step"><strong>2. Item Features</strong><p data-i18n="step2">Each song becomes genre, artist, energy, tempo, mood and popularity features.</p></div>
          <div class="step"><strong>3. Train Model</strong><p data-i18n="step3">The app learns preference weights. The full app trains LightFM WARP.</p></div>
          <div class="step"><strong>4. Rank Songs</strong><p data-i18n="step4">Final score combines model preference and content similarity.</p></div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const SONGS = {songs_json};
    const FEATURES = ["danceability","energy","valence","tempo","acousticness","instrumentalness","speechiness","liveness","popularity"];
    const state = {{
      lang: localStorage.getItem("submissionLang") || "en",
      interactions: JSON.parse(localStorage.getItem("submissionInteractions") || "[]"),
      feedback: JSON.parse(localStorage.getItem("submissionFeedback") || "{{}}"),
      trained: false,
      trainedAt: "",
      userVector: null,
      genreWeights: {{}},
      artistWeights: {{}},
      daily: []
    }};
    const I18N = {{
      en: {{
        title:"AI Music Recommendation System", subtitle:"Standalone HTML Submission", navRec:"Recommendations", navTrain:"Training", standalone:"Standalone demo mode",
        eyebrow:"AI Fair Machine Learning Project", hero:"Train a music recommendation model from playlist and feedback.", heroText:"This single HTML file mirrors the app UI and demonstrates the same recommendation workflow: import playlist metadata, search songs, train a hybrid model, rank songs, and generate a final 50-song mix.",
        getRec:"Get Recommendations", daily50:"Generate Final 50", how:"How training works", truthNote:"Formal app model: LightFM WARP in Python. This submission HTML uses an in-browser hybrid scoring demo so it can run without setup.",
        importTitle:"Import Playlist", importHint:"QQ Music metadata only. No audio is downloaded.", qqLabel:"QQ Music playlist URL or ID", importBtn:"Import", qqStatus:"Paste a playlist URL or numeric ID.",
        manualTitle:"Manual Playlist", manualHint:"One song per line: Song Name - Artist Name", manualBtn:"Add Manual Playlist", manualStatus:"Manual songs become training interactions.",
        trainTitle:"Train Recommendation Model", trainHint:"Hybrid model from interactions and item features.", trainNote:"Training converts songs into feature vectors and learns user preference weights from playlist, Like, and Dislike interactions.", trainBtn:"Train Model",
        searchTitle:"Search Songs", searchHint:"Search the embedded library. Online Deezer search is attempted when network/CORS allows it.", searchBtn:"Search", searchEmpty:"Search results appear here.",
        tasteTitle:"User Taste Profile", tasteHint:"Built from playlist songs and feedback.", recTitle:"Recommendations", recHint:"Ranked by model score plus content similarity.", recEmpty:"Add songs, train the model, then get recommendations.",
        dailyTitle:"Daily Recommendation Mix", dailyHint:"A final 50-song output playlist for submission and demo.", copy:"Copy 50-song playlist", dailyEmpty:"Generate Final 50 to show the playlist.",
        howTitle:"How the Machine Learning Works", howHint:"Short explanation for AI Fair.", step1:"Playlist import, manual add, Like and Dislike become user-song training data.", step2:"Each song becomes genre, artist, energy, tempo, mood and popularity features.", step3:"The app learns preference weights. The full app trains LightFM WARP.", step4:"Final score combines model preference and content similarity.",
        liked:"Liked", disliked:"Disliked", add:"Add to Training Data", like:"Like", dislike:"Dislike", algorithm:"Algorithm Used", model:"Model", content:"Content", final:"Final", copied:"Copied playlist.", noDaily:"Generate Daily 50 first."
      }},
      zh: {{
        title:"AI 音乐推荐系统", subtitle:"单文件 HTML 提交版", navRec:"推荐结果", navTrain:"模型训练", standalone:"单文件演示模式",
        eyebrow:"AI Fair 机器学习项目", hero:"从歌单和反馈训练音乐推荐模型。", heroText:"这个单文件 HTML 复刻 App 界面和推荐流程：导入歌单元数据、搜索歌曲、训练混合模型、排序歌曲，并生成最终 50 首推荐。",
        getRec:"获取推荐", daily50:"生成最终 50 首", how:"查看训练流程", truthNote:"正式 App 模型：Python LightFM WARP。本提交版用浏览器内混合评分演示，所以无需配置即可运行。",
        importTitle:"导入歌单", importHint:"只导入 QQ 音乐元数据，不下载音频。", qqLabel:"QQ 音乐歌单链接或 ID", importBtn:"导入", qqStatus:"粘贴歌单链接或数字 ID。",
        manualTitle:"手动歌单", manualHint:"每行一首歌：歌曲名 - 歌手名", manualBtn:"添加手动歌单", manualStatus:"手动歌曲会变成训练交互。",
        trainTitle:"训练推荐模型", trainHint:"基于交互和歌曲特征的混合模型。", trainNote:"训练会把歌曲转换成特征向量，并从歌单、喜欢、不喜欢中学习用户偏好权重。", trainBtn:"训练模型",
        searchTitle:"搜索歌曲", searchHint:"搜索内置曲库。网络和 CORS 允许时会尝试 Deezer 在线搜索。", searchBtn:"搜索", searchEmpty:"搜索结果会显示在这里。",
        tasteTitle:"用户口味画像", tasteHint:"根据歌单和反馈生成。", recTitle:"推荐结果", recHint:"根据模型分数和内容相似度排序。", recEmpty:"添加歌曲、训练模型后获取推荐。",
        dailyTitle:"每日推荐歌单", dailyHint:"用于提交和展示的最终 50 首推荐。", copy:"复制 50 首歌单", dailyEmpty:"点击生成最终 50 首后显示歌单。",
        howTitle:"机器学习如何工作", howHint:"适合 AI Fair 的简短解释。", step1:"歌单导入、手动添加、喜欢和不喜欢都会变成用户-歌曲训练数据。", step2:"每首歌会变成风格、歌手、能量、速度、情绪和流行度特征。", step3:"系统学习偏好权重；正式 App 使用 LightFM WARP。", step4:"最终分数结合模型偏好和内容相似度。",
        liked:"已喜欢", disliked:"已不喜欢", add:"加入训练数据", like:"喜欢", dislike:"不喜欢", algorithm:"使用算法", model:"模型", content:"内容", final:"最终", copied:"已复制歌单。", noDaily:"请先生成最终 50 首。"
      }}
    }};
    const $ = id => document.getElementById(id);
    const text = key => I18N[state.lang][key] || I18N.en[key] || key;
    function save() {{
      localStorage.setItem("submissionInteractions", JSON.stringify(state.interactions));
      localStorage.setItem("submissionFeedback", JSON.stringify(state.feedback));
      localStorage.setItem("submissionLang", state.lang);
    }}
    function applyLanguage() {{
      document.documentElement.lang = state.lang;
      document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = text(el.dataset.i18n));
      $("langBtn").textContent = state.lang === "en" ? "中文" : "EN";
      renderStatus(); renderTaste();
    }}
    function idFor(song) {{ return song.track_id || (song.track_name + "|" + song.artist_name).toLowerCase().replace(/[^a-z0-9]+/g,"-"); }}
    function vector(song) {{
      return [
        +song.danceability || 0, +song.energy || 0, +song.valence || 0, (+song.tempo || 100)/180,
        +song.acousticness || 0, +song.instrumentalness || 0, +song.speechiness || 0, +song.liveness || 0, (+song.popularity || 60)/100
      ];
    }}
    function dot(a,b) {{ return a.reduce((s,x,i)=>s+x*b[i],0); }}
    function norm(a) {{ return Math.sqrt(dot(a,a)) || 1; }}
    function cosine(a,b) {{ return Math.max(0, Math.min(1, (dot(a,b)/(norm(a)*norm(b)) + 1)/2)); }}
    function findSong(name, artist="") {{
      const n = name.trim().toLowerCase(), a = artist.trim().toLowerCase();
      return SONGS.find(s => s.track_name.toLowerCase() === n && (!a || s.artist_name.toLowerCase().includes(a)))
        || SONGS.find(s => s.track_name.toLowerCase() === n)
        || null;
    }}
    function estimateSong(name, artist) {{
      const genre = /eminem|drake|kendrick|rap|hip/i.test(artist+name) ? "Hip-hop" : /zedd|avicii|edm|remix|dance/i.test(artist+name) ? "Electronic" : /adele|piano|sad/i.test(artist+name) ? "Ballad" : /coldplay|rock|dragon|nirvana/i.test(artist+name) ? "Rock" : "Pop";
      const base = {{Pop:[.72,.7,.72,112,.12,.01,.07,.12,72], Rock:[.5,.84,.48,130,.05,.02,.06,.17,74], Electronic:[.7,.86,.46,126,.03,.3,.06,.15,76], "Hip-hop":[.8,.68,.48,98,.05,0,.22,.14,75], Ballad:[.43,.32,.28,84,.78,.01,.04,.1,73]}}[genre];
      return {{track_id:"manual_"+Math.random().toString(36).slice(2), track_name:name, artist_name:artist||"Unknown Artist", album_name:"Manual Input", genre, tags:"manual,estimated", danceability:base[0], energy:base[1], valence:base[2], tempo:base[3], acousticness:base[4], instrumentalness:base[5], speechiness:base[6], liveness:base[7], popularity:base[8], source:"manual", has_audio_features:true}};
    }}
    function addInteraction(song, type, weight) {{
      const id = idFor(song); if (!SONGS.find(s=>idFor(s)===id)) SONGS.push(song);
      state.interactions.push({{track_id:id, type, weight, at:new Date().toISOString()}});
      save();
    }}
    function selectedIds() {{ return new Set(state.interactions.map(x=>x.track_id)); }}
    function positiveInteractions() {{ return state.interactions.filter(x=>x.weight>0); }}
    function profileVector() {{
      const pos = positiveInteractions(); if (!pos.length) return null;
      const sum = Array(9).fill(0); let total = 0;
      pos.forEach(x => {{
        const song = SONGS.find(s=>idFor(s)===x.track_id); if (!song) return;
        const v = vector(song); v.forEach((n,i)=>sum[i]+=n*x.weight); total += x.weight;
      }});
      return sum.map(x=>x/(total||1));
    }}
    function trainModel() {{
      state.userVector = profileVector();
      state.genreWeights = {{}}; state.artistWeights = {{}};
      state.interactions.forEach(x => {{
        const s = SONGS.find(song=>idFor(song)===x.track_id); if (!s) return;
        state.genreWeights[s.genre] = (state.genreWeights[s.genre]||0) + x.weight;
        state.artistWeights[s.artist_name] = (state.artistWeights[s.artist_name]||0) + x.weight;
      }});
      state.trained = !!state.userVector && state.interactions.length >= 3;
      state.trainedAt = new Date().toLocaleString();
      renderStatus(); renderTaste();
    }}
    function scoreSong(song) {{
      const defaultProfile = [.67,.68,.58,.62,.18,.04,.08,.12,.72];
      const p = state.userVector || defaultProfile;
      const content = cosine(vector(song), p);
      const genreBoost = (state.genreWeights[song.genre] || 0) * .045;
      const artistBoost = (state.artistWeights[song.artist_name] || 0) * .025;
      const pop = (+song.popularity || 60)/100;
      let model = Math.max(0, Math.min(1, content*.72 + pop*.18 + genreBoost + artistBoost));
      if (state.feedback[idFor(song)] === 0) model -= .35;
      if (state.feedback[idFor(song)] === 1) model += .2;
      model = Math.max(0, Math.min(1, model));
      const finalScore = state.trained ? .7*model + .3*content : .6*content + .4*pop;
      return {{model, content, finalScore}};
    }}
    function matched(song) {{
      const p = getTaste();
      const out = [];
      if (p.genres.includes(song.genre)) out.push(song.genre + " genre");
      if (song.energy >= .7 && p.energy.includes("High")) out.push("high energy");
      if (song.tempo >= 125 && p.tempo.includes("Fast")) out.push("fast tempo");
      if (song.danceability >= .7 && p.dance.includes("Danceable")) out.push("danceable rhythm");
      if (song.valence >= .65 && p.mood.includes("Positive")) out.push("positive mood");
      if (song.valence <= .4 && p.mood.includes("Sad")) out.push("sad mood");
      return out.length ? out : ["overall feature profile"];
    }}
    function recommendations(n=10, exclude=true) {{
      const excluded = selectedIds();
      let rows = SONGS.filter(s => !exclude || !excluded.has(idFor(s))).map(s => ({{...s, ...scoreSong(s)}}));
      rows.sort((a,b)=>b.finalScore-a.finalScore);
      return diversify(rows, n);
    }}
    function diversify(rows, n) {{
      const selected=[], artists={{}}, genres={{}}, seen=new Set();
      for (let pass=0; pass<3; pass++) {{
        for (const r of rows) {{
          const key=(r.track_name+"|"+r.artist_name).toLowerCase(); if (seen.has(key)) continue;
          if (pass===0 && ((artists[r.artist_name]||0)>=2 || (genres[r.genre]||0)>=14)) continue;
          if (pass===1 && ((artists[r.artist_name]||0)>=3 || (genres[r.genre]||0)>=20)) continue;
          selected.push(r); seen.add(key); artists[r.artist_name]=(artists[r.artist_name]||0)+1; genres[r.genre]=(genres[r.genre]||0)+1;
          if (selected.length>=n) return selected;
        }}
      }}
      return selected;
    }}
    function getTaste() {{
      const pos = positiveInteractions().map(x=>SONGS.find(s=>idFor(s)===x.track_id)).filter(Boolean);
      if (!pos.length) return {{energy:"Unknown", dance:"Unknown", mood:"Unknown", tempo:"Unknown", genres:[], artists:[], summary:"Add songs to build a taste profile."}};
      const avg = k => pos.reduce((s,x)=>s+(+x[k]||0),0)/pos.length;
      const counts = arr => Object.entries(arr.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{{}})).sort((a,b)=>b[1]-a[1]).map(x=>x[0]);
      const genres = counts(pos.map(x=>x.genre)).slice(0,4), artists = counts(pos.map(x=>x.artist_name)).slice(0,4);
      const energy = avg("energy")>=.65 ? "High Energy" : avg("energy")<=.4 ? "Low Energy" : "Medium Energy";
      const dance = avg("danceability")>=.65 ? "Danceable" : "Less Danceable";
      const mood = avg("valence")>=.65 ? "Positive Mood" : avg("valence")<=.4 ? "Sad Mood" : "Neutral Mood";
      const tempo = avg("tempo")>=125 ? "Fast Tempo" : avg("tempo")<=90 ? "Slow Tempo" : "Medium Tempo";
      return {{energy,dance,mood,tempo,genres,artists,summary:`Your profile leans toward ${{energy}}, ${{tempo}}, and ${{genres.slice(0,2).join(", ")}}.`}};
    }}
    function renderStatus() {{
      $("modelMetrics").innerHTML = [
        ["Model Type", state.trained ? "Browser Hybrid Demo / LightFM in full app" : "LightFM Hybrid Model"],
        ["Training Status", state.trained ? "Trained" : "Not trained"],
        ["Users", "1 demo_user"],
        ["Songs", SONGS.length],
        ["Interactions", state.interactions.length],
        ["Item Features", countItemFeatures()],
        ["Last Trained", state.trainedAt || "Never"],
        ["Message", state.trained ? "Model learned preference weights from your playlist." : "Add songs and train the model."]
      ].map(([a,b])=>`<div class="metric"><span>${{a}}</span><strong>${{b}}</strong></div>`).join("");
    }}
    function countItemFeatures() {{
      const set = new Set();
      SONGS.forEach(s => {{ set.add("genre:"+s.genre); set.add("artist:"+s.artist_name); set.add("source:"+s.source); set.add("energy:"+(s.energy>=.7?"high":s.energy<=.4?"low":"medium")); set.add("tempo:"+(s.tempo>=125?"fast":s.tempo<=90?"slow":"medium")); }});
      return set.size;
    }}
    function renderTaste() {{
      const p = getTaste();
      $("tasteProfile").innerHTML = [
        ["Energy", p.energy], ["Dance", p.dance], ["Mood", p.mood], ["Tempo", p.tempo],
        ["Favorite Genres", p.genres.join(", ") || "None yet"], ["Main Artists", p.artists.join(", ") || "None yet"], ["Summary", p.summary]
      ].map(([a,b])=>`<div class="metric"><span>${{a}}</span><strong>${{b}}</strong></div>`).join("");
    }}
    function songCard(song, withFeedback=false) {{
      const m = matched(song);
      const reason = m.includes("overall feature profile")
        ? "This song is recommended because its audio feature profile is close to your imported playlist."
        : `This song is recommended because it shares ${{m.slice(0,3).join(", ")}} with your playlist.`;
      return `<article class="song-card">
        <h3>${{htmlEscape(song.track_name)}}</h3>
        <p>${{htmlEscape(song.artist_name)}} · ${{htmlEscape(song.genre)}}</p>
        <p><strong>${{text("algorithm")}}:</strong> ${{state.trained ? "Hybrid Learned Preference Model" : "Content-Based Baseline"}}</p>
        <div class="score-row"><div class="score">${{text("model")}} ${{song.model.toFixed(3)}}</div><div class="score">${{text("content")}} ${{song.content.toFixed(3)}}</div><div class="score">${{text("final")}} ${{song.finalScore.toFixed(3)}}</div></div>
        <p>${{reason}}</p>
        <p>${{m.map(x=>`<span class="tag">${{htmlEscape(x)}}</span>`).join("")}}</p>
        ${{withFeedback ? `<div class="actions"><button class="primary" onclick="feedback('${{idFor(song)}}',1)">${{text("like")}}</button><button class="danger" onclick="feedback('${{idFor(song)}}',0)">${{text("dislike")}}</button></div>` : `<button class="secondary" onclick="addFromSearch('${{idFor(song)}}')">${{text("add")}}</button>`}}
      </article>`;
    }}
    function htmlEscape(s) {{ return String(s ?? "").replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c])); }}
    function renderRecommendations() {{
      const rows = recommendations(10, true);
      $("recommendationCards").innerHTML = rows.length ? rows.map(s=>songCard(s,true)).join("") : `<div class="empty">${{text("recEmpty")}}</div>`;
    }}
    function renderDaily() {{
      const rows = recommendations(50, false); state.daily = rows; save();
      $("dailyList").innerHTML = rows.map((s,i)=>`<div class="daily-row"><span class="rank">${{i+1}}</span><div><strong>${{htmlEscape(s.track_name)}}</strong><br><span class="small">${{htmlEscape(s.artist_name)}} · ${{htmlEscape(s.genre)}}</span></div><strong>${{s.finalScore.toFixed(3)}}</strong></div>`).join("");
    }}
    function feedback(trackId, label) {{
      state.feedback[trackId] = label;
      addInteraction(SONGS.find(s=>idFor(s)===trackId), label ? "like" : "dislike", label ? 2 : -1);
      trainModel(); renderRecommendations();
    }}
    function addFromSearch(trackId) {{
      const s = SONGS.find(song=>idFor(song)===trackId); if (!s) return;
      addInteraction(s, "manual_add", 1); trainModel();
      $("searchResults").insertAdjacentHTML("afterbegin", `<div class="empty">${{htmlEscape(s.track_name)}} added to training data.</div>`);
    }}
    function searchLocal(query) {{
      const q = query.trim().toLowerCase();
      return SONGS.filter(s => [s.track_name,s.artist_name,s.genre,s.tags].join(" ").toLowerCase().includes(q)).slice(0,10).map(s=>({{...s,...scoreSong(s)}}));
    }}
    async function searchDeezer(query) {{
      try {{
        const res = await fetch(`https://api.deezer.com/search?q=${{encodeURIComponent(query)}}&limit=5`);
        const data = await res.json();
        return (data.data || []).map(item => {{
          const s = estimateSong(item.title, item.artist?.name || "Unknown Artist");
          s.album_name = item.album?.title || ""; s.source = "deezer"; s.external_url = item.link || ""; return {{...s,...scoreSong(s)}};
        }});
      }} catch (e) {{ return []; }}
    }}
    function extractQQId(text) {{
      text = (text||"").trim();
      const patterns = [/playlist\\/(\\d+)/, /[?&](?:id|disstid|tid)=(\\d+)/, /(?:id|disstid|tid)=(\\d+)/, /^(\\d{{4,}})$/];
      for (const p of patterns) {{ const m = text.match(p); if (m) return m[1]; }}
      return "";
    }}
    async function handleSearch() {{
      const q = $("searchInput").value;
      let rows = searchLocal(q);
      if (rows.length < 8) rows = rows.concat(await searchDeezer(q));
      const seen = new Set();
      rows = rows.filter(s => {{ const k=(s.track_name+"|"+s.artist_name).toLowerCase(); if(seen.has(k)) return false; seen.add(k); return true; }}).slice(0,12);
      $("searchResults").innerHTML = rows.length ? rows.map(s=>songCard(s,false)).join("") : `<div class="empty">No results found.</div>`;
    }}
    function handleManual() {{
      const lines = $("manualInput").value.split(/\\n+/).map(x=>x.trim()).filter(Boolean);
      let count=0;
      lines.forEach(line => {{
        const [name, ...rest] = line.split("-");
        const artist = rest.join("-").trim();
        if (!name.trim()) return;
        const song = findSong(name, artist) || estimateSong(name.trim(), artist);
        addInteraction(song, "manual_add", 1); count++;
      }});
      trainModel();
      $("manualStatus").textContent = `Saved ${{count}} songs and created ${{count}} training interactions.`;
    }}
    function handleQQ() {{
      const id = extractQQId($("qqInput").value);
      if (!id) {{ $("qqStatus").textContent = "Could not recognize QQ playlist ID. Try manual playlist input."; return; }}
      const sample = SONGS.slice(0, 8);
      sample.forEach(s => addInteraction(s, "playlist_import", 1));
      trainModel();
      $("qqStatus").textContent = `Recognized QQ playlist ID ${{id}}. Standalone HTML imported ${{sample.length}} metadata demo songs. Full Flask app calls QQ metadata endpoints.`;
    }}
    function copyDaily() {{
      if (!state.daily.length) {{ alert(text("noDaily")); return; }}
      const body = state.daily.map((s,i)=>`${{i+1}}. ${{s.track_name}} - ${{s.artist_name}}`).join("\\n");
      navigator.clipboard?.writeText(body); alert(text("copied"));
    }}
    $("langBtn").onclick = () => {{ state.lang = state.lang === "en" ? "zh" : "en"; save(); applyLanguage(); }};
    $("manualBtn").onclick = handleManual; $("trainBtn").onclick = trainModel; $("searchBtn").onclick = handleSearch; $("qqBtn").onclick = handleQQ;
    $("recBtn").onclick = renderRecommendations; $("heroRec").onclick = renderRecommendations; $("dailyBtn").onclick = renderDaily; $("heroDaily").onclick = renderDaily; $("copyBtn").onclick = copyDaily;
    $("searchInput").addEventListener("keydown", e => {{ if(e.key==="Enter") handleSearch(); }});
    window.feedback = feedback; window.addFromSearch = addFromSearch;
    applyLanguage(); renderStatus(); renderTaste();
  </script>
</body>
</html>
"""


def main() -> None:
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    html_text = build_html()
    OUT_HTML.write_text(html_text, encoding="utf-8")
    OUT_TXT.write_text(html_text, encoding="utf-8")
    print(OUT_HTML)
    print(OUT_TXT)
    print(f"characters={len(html_text)}")


if __name__ == "__main__":
    main()

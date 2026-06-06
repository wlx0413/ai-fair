const translations = {
  en: {
    navTitle: "AI Music Recommendation System",
    navSubtitle: "LightFM Hybrid Recommender",
    navRecommendations: "Recommendations",
    navTraining: "Training",
    checkingSystem: "Checking system...",
    systemRunning: "System running locally",
    systemError: "System error",
    eyebrow: "AI Fair Machine Learning Project",
    heroTitle: "Train a music recommendation model from your playlist.",
    heroSubtitle: "Analyze your playlist and recommend similar songs using machine learning, item features, and user feedback.",
    getRecommendations: "Get Recommendations",
    generateFinal50: "Generate Final 50",
    seeHowItWorks: "See how it trains",
    mainModel: "Main Model",
    modelOneLiner: "Hybrid ranking model trained on playlist interactions and song item features.",
    importTitle: "Import Playlist",
    importHint: "Only metadata is imported. No music audio is downloaded.",
    qqUrlLabel: "QQ Music playlist URL or ID",
    importButton: "Import",
    qqEmpty: "Paste a public QQ Music playlist URL or ID.",
    qqLoading: "Importing playlist metadata...",
    manualTitle: "Manual Playlist",
    manualHint: "Add one song per line: Song Name - Artist Name",
    manualButton: "Add Manual Playlist",
    manualEmpty: "Manual songs become user-item interactions for training.",
    manualSaved: "Saved {songs} songs and created {interactions} training interactions.",
    trainTitle: "Train Model",
    trainHint: "LightFM hybrid model with WARP ranking loss.",
    howTrainLabel: "How we train:",
    howTrainText: "playlist songs and feedback become a user-song matrix, while each song becomes features like genre, artist, energy, tempo, mood, and tags.",
    trainButton: "Train Model",
    training: "Training...",
    searchTitle: "Search Songs",
    searchHint: "Search local demo songs first, then free metadata APIs when available.",
    searchButton: "Search",
    searching: "Searching...",
    searchEmpty: "Search results will appear here.",
    noResults: "No results found.",
    addTraining: "Add to Training Data",
    trainingReady: "training-ready",
    metadataOnly: "metadata only",
    estimatedNote: "Audio features are estimated from public metadata for model training.",
    metadataNote: "This online result was found, but it does not have enough audio features for model training.",
    tasteTitle: "User Taste Profile",
    tasteHint: "Built from imported songs and feedback.",
    tasteEmpty: "Add songs to build a taste profile.",
    energy: "Energy",
    dance: "Dance",
    mood: "Mood",
    tempo: "Tempo",
    favoriteGenres: "Favorite Genres",
    mainArtists: "Main Artists",
    summary: "Summary",
    noneYet: "None yet",
    recommendationsTitle: "Recommendations",
    recommendationsHint: "Ranked by learned model score plus content similarity.",
    recommendationsEmpty: "No recommendations yet. Add songs, train the model, then get recommendations.",
    loadingRecommendations: "Generating recommendations...",
    dailyTitle: "Daily Recommendation Mix",
    dailyHint: "A final 50-song output playlist for your AI Fair demo.",
    dailyEmpty: "Generate the final 50-song playlist to show your daily recommendations.",
    loadingDaily: "Generating final 50-song playlist...",
    copyFinal50: "Copy 50-song playlist",
    copiedFinal50: "Copied final playlist.",
    noDailyToCopy: "Generate the final playlist first.",
    dailyScore: "Score",
    algorithmUsed: "Algorithm Used",
    model: "Model",
    content: "Content",
    final: "Final",
    matched: "Matched",
    overallProfile: "overall feature profile",
    reasonWithFeatures: "This song is recommended because it shares {features} with your playlist.",
    reasonFallback: "This song is recommended because its audio feature profile is close to your imported playlist.",
    like: "Like",
    dislike: "Dislike",
    sendingFeedback: "Saving feedback...",
    mlTitle: "How the Machine Learning Works",
    mlHint: "A simple AI Fair explanation for the training pipeline.",
    step1Title: "Collect interactions",
    step1Text: "Imported playlist songs, manual songs, Likes, and Dislikes become training signals.",
    step2Title: "Build item features",
    step2Text: "Songs are represented by genre, artist, tags, energy, tempo, mood, and popularity buckets.",
    step3Title: "Train LightFM",
    step3Text: "LightFM learns user preference weights using a hybrid recommendation model.",
    step4Title: "Rank songs",
    step4Text: "The app combines model score and content similarity, then shows the Top-N results.",
    modelStatusLabels: {
      model_type: "Model Type",
      is_trained: "Training Status",
      num_users: "Users",
      num_items: "Songs",
      num_interactions: "Interactions",
      num_item_features: "Item Features",
      last_trained_at: "Last Trained",
      message: "Message",
    },
    trained: "Trained",
    notTrained: "Not trained",
    never: "Never",
  },
  zh: {
    navTitle: "AI 音乐推荐系统",
    navSubtitle: "LightFM 混合推荐模型",
    navRecommendations: "推荐结果",
    navTraining: "模型训练",
    checkingSystem: "正在检查系统...",
    systemRunning: "本地系统正在运行",
    systemError: "系统错误",
    eyebrow: "AI Fair 机器学习项目",
    heroTitle: "从你的歌单训练音乐推荐模型。",
    heroSubtitle: "系统会分析歌单、歌曲特征和用户反馈，用机器学习推荐更符合口味的歌曲。",
    getRecommendations: "获取推荐",
    generateFinal50: "生成最终 50 首",
    seeHowItWorks: "查看训练流程",
    mainModel: "主模型",
    modelOneLiner: "基于歌单交互和歌曲特征训练的混合排序推荐模型。",
    importTitle: "导入歌单",
    importHint: "只导入歌单元数据，不下载任何音乐音频。",
    qqUrlLabel: "QQ 音乐歌单链接或 ID",
    importButton: "导入",
    qqEmpty: "粘贴公开 QQ 音乐歌单链接或 ID。",
    qqLoading: "正在导入歌单元数据...",
    manualTitle: "手动歌单",
    manualHint: "每行一首歌：歌曲名 - 歌手名",
    manualButton: "添加手动歌单",
    manualEmpty: "手动歌曲会变成模型训练用的用户-歌曲交互。",
    manualSaved: "已保存 {songs} 首歌，并创建 {interactions} 条训练交互。",
    trainTitle: "训练模型",
    trainHint: "使用 WARP ranking loss 的 LightFM 混合模型。",
    howTrainLabel: "训练方式：",
    howTrainText: "歌单和反馈会变成用户-歌曲矩阵；每首歌会变成风格、歌手、能量、速度、情绪和标签等特征。",
    trainButton: "训练模型",
    training: "训练中...",
    searchTitle: "搜索歌曲",
    searchHint: "优先搜索本地 demo 数据，必要时再使用免费音乐元数据 API。",
    searchButton: "搜索",
    searching: "搜索中...",
    searchEmpty: "搜索结果会显示在这里。",
    noResults: "没有找到结果。",
    addTraining: "加入训练数据",
    trainingReady: "可用于训练",
    metadataOnly: "仅元数据",
    estimatedNote: "音频特征已根据公开元数据估算，可用于模型训练。",
    metadataNote: "这个在线结果已找到，但没有足够音频特征用于模型训练。",
    tasteTitle: "用户口味画像",
    tasteHint: "根据导入歌曲和反馈自动生成。",
    tasteEmpty: "添加歌曲后会生成口味画像。",
    energy: "能量",
    dance: "律动",
    mood: "情绪",
    tempo: "速度",
    favoriteGenres: "喜欢的风格",
    mainArtists: "主要歌手",
    summary: "总结",
    noneYet: "暂无",
    recommendationsTitle: "推荐结果",
    recommendationsHint: "根据模型学习分数和内容相似度排序。",
    recommendationsEmpty: "还没有推荐结果。请先添加歌曲、训练模型，再获取推荐。",
    loadingRecommendations: "正在生成推荐...",
    dailyTitle: "每日推荐歌单",
    dailyHint: "AI Fair 展示用的最终 50 首推荐输出。",
    dailyEmpty: "点击生成最终 50 首，展示你的每日推荐歌单。",
    loadingDaily: "正在生成最终 50 首歌单...",
    copyFinal50: "复制 50 首歌单",
    copiedFinal50: "已复制最终歌单。",
    noDailyToCopy: "请先生成最终歌单。",
    dailyScore: "分数",
    algorithmUsed: "使用算法",
    model: "模型",
    content: "内容",
    final: "最终",
    matched: "匹配特征",
    overallProfile: "整体特征画像",
    reasonWithFeatures: "推荐原因：它和你的歌单有相似的 {features}。",
    reasonFallback: "推荐原因：它的音频特征画像接近你的歌单。",
    like: "喜欢",
    dislike: "不喜欢",
    sendingFeedback: "正在保存反馈...",
    mlTitle: "机器学习如何工作",
    mlHint: "适合 AI Fair 展示的简短训练流程说明。",
    step1Title: "收集交互",
    step1Text: "导入歌单、手动添加、喜欢和不喜欢都会成为训练信号。",
    step2Title: "构建歌曲特征",
    step2Text: "歌曲会表示成风格、歌手、标签、能量、速度、情绪和流行度等特征。",
    step3Title: "训练 LightFM",
    step3Text: "LightFM 使用混合推荐模型学习用户偏好的权重。",
    step4Title: "排序歌曲",
    step4Text: "系统结合模型分数和内容相似度，展示 Top-N 推荐结果。",
    modelStatusLabels: {
      model_type: "模型类型",
      is_trained: "训练状态",
      num_users: "用户数",
      num_items: "歌曲数",
      num_interactions: "交互数",
      num_item_features: "歌曲特征数",
      last_trained_at: "最近训练时间",
      message: "状态说明",
    },
    trained: "已训练",
    notTrained: "未训练",
    never: "从未训练",
  },
};

let currentLanguage = localStorage.getItem("aiMusicLanguage") || "en";
let lastDailyRecommendations = [];

const t = (key) => translations[currentLanguage][key] ?? translations.en[key] ?? key;

const api = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
};

const esc = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

const format = (template, values) =>
  Object.entries(values).reduce((text, [key, value]) => text.replace(`{${key}}`, value), template);

function applyTranslations() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (translations[currentLanguage][key]) {
      element.textContent = translations[currentLanguage][key];
    }
  });
  document.getElementById("languageToggle").textContent = currentLanguage === "en" ? "中文" : "EN";
}

function setLoading(button, isLoading, loadingText, normalText) {
  button.disabled = isLoading;
  button.classList.toggle("is-loading", isLoading);
  button.textContent = isLoading ? loadingText : normalText;
}

async function refreshHealth() {
  try {
    const data = await api("/api/health");
    document.getElementById("healthStatus").textContent = data.status === "ok" ? t("systemRunning") : t("systemError");
  } catch {
    document.getElementById("healthStatus").textContent = t("systemError");
  }
}

async function refreshModelStatus() {
  const status = await api("/api/model-status");
  const labels = translations[currentLanguage].modelStatusLabels;
  const fields = {
    model_type: status.model_type,
    is_trained: status.is_trained ? t("trained") : t("notTrained"),
    num_users: status.num_users,
    num_items: status.num_items,
    num_interactions: status.num_interactions,
    num_item_features: status.num_item_features,
    last_trained_at: status.last_trained_at || t("never"),
    message: status.message,
  };
  document.getElementById("modelStatus").innerHTML = Object.entries(fields)
    .map(([key, value]) => `<dt>${esc(labels[key])}</dt><dd>${esc(value)}</dd>`)
    .join("");
}

async function refreshTasteProfile(profileFromRecommendations = null) {
  const profile = profileFromRecommendations || (await api("/api/taste-profile"));
  document.getElementById("tasteProfile").innerHTML = `
    <div><strong>${esc(t("energy"))}:</strong> ${esc(profile.energy_level)}</div>
    <div><strong>${esc(t("dance"))}:</strong> ${esc(profile.danceability)}</div>
    <div><strong>${esc(t("mood"))}:</strong> ${esc(profile.mood)}</div>
    <div><strong>${esc(t("tempo"))}:</strong> ${esc(profile.tempo)}</div>
    <div><strong>${esc(t("favoriteGenres"))}:</strong> ${esc((profile.favorite_genres || []).join(", ") || t("noneYet"))}</div>
    <div><strong>${esc(t("mainArtists"))}:</strong> ${esc((profile.main_artists || []).join(", ") || t("noneYet"))}</div>
    <div><strong>${esc(t("summary"))}:</strong> ${esc(profile.summary)}</div>
  `;
}

async function importQQPlaylist() {
  const button = document.getElementById("qqImportBtn");
  setLoading(button, true, t("qqLoading"), t("importButton"));
  document.getElementById("qqStatus").textContent = t("qqLoading");
  try {
    const data = await api("/api/import/qq", {
      method: "POST",
      body: JSON.stringify({ playlist_url: document.getElementById("qqInput").value }),
    });
    document.getElementById("qqStatus").textContent = data.success
      ? `${data.message} (${data.songs.length})`
      : data.message;
    await refreshModelStatus();
    await refreshTasteProfile();
  } catch (error) {
    document.getElementById("qqStatus").textContent = error.message;
  } finally {
    setLoading(button, false, t("qqLoading"), t("importButton"));
  }
}

async function addManualPlaylist() {
  const button = document.getElementById("manualAddBtn");
  setLoading(button, true, t("training"), t("manualButton"));
  try {
    const lines = document
      .getElementById("manualSongs")
      .value.split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    const songs = lines.map((line) => {
      const [trackName, artistName = ""] = line.split(" - ");
      return { track_name: trackName.trim(), artist_name: artistName.trim() };
    });
    const data = await api("/api/playlist/manual", {
      method: "POST",
      body: JSON.stringify({ songs }),
    });
    document.getElementById("manualStatus").textContent = format(t("manualSaved"), {
      songs: data.saved_songs.length,
      interactions: data.interactions_created,
    });
    await refreshModelStatus();
    await refreshTasteProfile();
  } catch (error) {
    document.getElementById("manualStatus").textContent = error.message;
  } finally {
    setLoading(button, false, t("training"), t("manualButton"));
  }
}

async function searchSongs() {
  const button = document.getElementById("searchBtn");
  const container = document.getElementById("searchResults");
  setLoading(button, true, t("searching"), t("searchButton"));
  container.innerHTML = `<div class="empty-state">${esc(t("searching"))}</div>`;
  try {
    const q = document.getElementById("searchInput").value;
    const data = await api(`/api/search?q=${encodeURIComponent(q)}`);
    container.innerHTML = data.results.map(renderSearchCard).join("") || `<div class="empty-state">${esc(t("noResults"))}</div>`;
  } catch (error) {
    container.innerHTML = `<div class="empty-state">${esc(error.message)}</div>`;
  } finally {
    setLoading(button, false, t("searching"), t("searchButton"));
  }
}

function renderSearchCard(song) {
  const encoded = encodeURIComponent(JSON.stringify(song));
  const note = translateTrainingNote(song.training_note);
  return `
    <article class="card">
      <h3>${esc(song.track_name)}</h3>
      <p class="meta">${esc(song.artist_name)} · ${esc(formatSource(song.source))} · ${song.has_audio_features ? esc(t("trainingReady")) : esc(t("metadataOnly"))}</p>
      ${note ? `<p class="note">${esc(note)}</p>` : ""}
      <button class="secondary" onclick="addSearchResult('${encoded}')">${esc(t("addTraining"))}</button>
    </article>
  `;
}

function translateTrainingNote(note) {
  if (!note) return "";
  if (note.includes("estimated")) return t("estimatedNote");
  if (note.includes("does not have enough")) return t("metadataNote");
  return note;
}

function formatSource(source) {
  if (currentLanguage === "zh") {
    return {
      curated: "精选曲库",
      local: "本地曲库",
      deezer: "Deezer 在线",
      musicbrainz: "MusicBrainz 在线",
      lastfm: "Last.fm 在线",
      manual: "手动添加",
      qq: "QQ 音乐",
    }[source] || source;
  }
  return {
    curated: "curated library",
    local: "local library",
  }[source] || source;
}

async function addSearchResult(encoded) {
  const song = JSON.parse(decodeURIComponent(encoded));
  const data = await api("/api/training/add", {
    method: "POST",
    body: JSON.stringify({ song }),
  });
  document.getElementById("searchResults").insertAdjacentHTML("beforebegin", "");
  alert(data.message);
  await refreshModelStatus();
  await refreshTasteProfile();
}

async function trainModel() {
  const button = document.getElementById("trainBtn");
  setLoading(button, true, t("training"), t("trainButton"));
  try {
    const status = await api("/api/train", { method: "POST", body: "{}" });
    await refreshModelStatus();
    alert(status.message);
  } finally {
    setLoading(button, false, t("training"), t("trainButton"));
  }
}

async function getRecommendations() {
  const button = document.getElementById("recommendBtn");
  const container = document.getElementById("recommendations");
  setLoading(button, true, t("loadingRecommendations"), t("getRecommendations"));
  container.innerHTML = `<div class="empty-state large">${esc(t("loadingRecommendations"))}</div>`;
  try {
    const data = await api("/api/recommendations?user_id=demo_user");
    renderRecommendations(data.recommendations);
    await refreshTasteProfile(data.taste_profile);
  } catch (error) {
    container.innerHTML = `<div class="empty-state large">${esc(error.message)}</div>`;
  } finally {
    setLoading(button, false, t("loadingRecommendations"), t("getRecommendations"));
  }
}

async function getDailyRecommendations() {
  const buttons = [document.getElementById("dailyBtn"), document.getElementById("heroDailyBtn")].filter(Boolean);
  const container = document.getElementById("dailyRecommendations");
  buttons.forEach((button) => setLoading(button, true, t("loadingDaily"), t("generateFinal50")));
  container.innerHTML = `<div class="empty-state large">${esc(t("loadingDaily"))}</div>`;
  try {
    const data = await api("/api/daily-recommendations?user_id=demo_user");
    lastDailyRecommendations = data.recommendations || [];
    renderDailyRecommendations(lastDailyRecommendations);
    await refreshTasteProfile(data.taste_profile);
    document.getElementById("dailyMixPanel").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    container.innerHTML = `<div class="empty-state large">${esc(error.message)}</div>`;
  } finally {
    buttons.forEach((button) => setLoading(button, false, t("loadingDaily"), t("generateFinal50")));
  }
}

function renderDailyRecommendations(items) {
  document.getElementById("dailyRecommendations").innerHTML =
    items
      .map(
        (item, index) => `
    <article class="daily-row">
      <div class="daily-rank">${String(index + 1).padStart(2, "0")}</div>
      <div class="daily-song">
        <strong>${esc(item.track_name)}</strong>
        <span>${esc(item.artist_name)}</span>
      </div>
      <div class="daily-genre">${esc(item.genre)}</div>
      <div class="daily-score">${esc(t("dailyScore"))} ${Number(item.score).toFixed(3)}</div>
    </article>
  `
      )
      .join("") || `<div class="empty-state large">${esc(t("dailyEmpty"))}</div>`;
}

async function copyDailyRecommendations() {
  if (!lastDailyRecommendations.length) {
    alert(t("noDailyToCopy"));
    return;
  }
  const text = lastDailyRecommendations
    .map((item, index) => `${index + 1}. ${item.track_name} - ${item.artist_name} (${item.genre})`)
    .join("\n");
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
  alert(t("copiedFinal50"));
}

function renderRecommendations(items) {
  document.getElementById("recommendations").innerHTML =
    items
      .map(
        (item) => `
    <article class="card">
      <h3>${esc(item.track_name)}</h3>
      <p class="meta">${esc(item.artist_name)} · ${esc(item.genre)}</p>
      <p class="meta"><strong>${esc(t("algorithmUsed"))}:</strong> ${esc(item.algorithm_used)}</p>
      <div class="score-grid">
        <span>${esc(t("model"))} ${Number(item.model_score).toFixed(3)}</span>
        <span>${esc(t("content"))} ${Number(item.content_score).toFixed(3)}</span>
        <span>${esc(t("final"))} ${Number(item.score).toFixed(3)}</span>
      </div>
      <p>${esc(formatReason(item))}</p>
      <p class="meta">${esc(t("matched"))}: ${esc(formatMatchedFeatures(item.features_matched || []))}</p>
      <div class="feedback-row">
        <button class="like" onclick="sendFeedback('${esc(item.track_id)}', 1)">${esc(t("like"))}</button>
        <button class="dislike" onclick="sendFeedback('${esc(item.track_id)}', 0)">${esc(t("dislike"))}</button>
      </div>
    </article>
  `
      )
      .join("") || `<div class="empty-state large">${esc(t("recommendationsEmpty"))}</div>`;
}

function formatReason(item) {
  const matched = item.features_matched || [];
  if (matched.length) {
    return format(t("reasonWithFeatures"), { features: formatMatchedFeatures(matched) });
  }
  return t("reasonFallback");
}

function formatMatchedFeatures(features) {
  if (!features.length) return t("overallProfile");
  return features.map(translateFeature).join(", ");
}

function translateFeature(feature) {
  if (currentLanguage !== "zh") return feature;
  return String(feature)
    .replace("Pop genre", "流行风格")
    .replace("Rock genre", "摇滚风格")
    .replace("Electronic genre", "电子风格")
    .replace("Hip-hop genre", "嘻哈风格")
    .replace("Ballad genre", "抒情风格")
    .replace("Indie genre", "独立风格")
    .replace("R&B genre", "R&B 风格")
    .replace("Acoustic genre", "原声风格")
    .replace("high energy", "高能量")
    .replace("fast tempo", "快节奏")
    .replace("danceable rhythm", "强律动")
    .replace("sad mood", "伤感情绪")
    .replace("positive mood", "积极情绪");
}

async function sendFeedback(trackId, label) {
  const container = document.getElementById("recommendations");
  container.insertAdjacentHTML("beforebegin", "");
  await api("/api/feedback", {
    method: "POST",
    body: JSON.stringify({ track_id: trackId, label }),
  });
  await refreshModelStatus();
  const data = await api("/api/recommendations?user_id=demo_user");
  renderRecommendations(data.recommendations);
  await refreshTasteProfile(data.taste_profile);
}

function wireEvents() {
  document.getElementById("languageToggle").addEventListener("click", async () => {
    currentLanguage = currentLanguage === "en" ? "zh" : "en";
    localStorage.setItem("aiMusicLanguage", currentLanguage);
    applyTranslations();
    await refreshModelStatus();
    await refreshTasteProfile();
    renderDailyRecommendations(lastDailyRecommendations);
  });
  document.getElementById("qqImportBtn").addEventListener("click", importQQPlaylist);
  document.getElementById("manualAddBtn").addEventListener("click", addManualPlaylist);
  document.getElementById("searchBtn").addEventListener("click", searchSongs);
  document.getElementById("searchInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") searchSongs();
  });
  document.getElementById("trainBtn").addEventListener("click", trainModel);
  document.getElementById("recommendBtn").addEventListener("click", getRecommendations);
  document.getElementById("heroRecommendBtn").addEventListener("click", getRecommendations);
  document.getElementById("dailyBtn").addEventListener("click", getDailyRecommendations);
  document.getElementById("heroDailyBtn").addEventListener("click", getDailyRecommendations);
  document.getElementById("copyDailyBtn").addEventListener("click", copyDailyRecommendations);
}

applyTranslations();
wireEvents();
refreshHealth();
refreshModelStatus();
refreshTasteProfile();

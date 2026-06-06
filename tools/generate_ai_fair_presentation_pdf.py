# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PPT_DIR = ROOT / "ppt"
ASSET_DIR = ROOT / "outputs" / "manual-ppt-work" / "assets"
PAGE_DIR = ROOT / "outputs" / "manual-ppt-work" / "pdf_pages"
PDF_PATH = PPT_DIR / "AI_Music_Recommendation_System_AI_Fair_Presentation_FIXED.pdf"

W, H = 1600, 900
PDF_W, PDF_H = 960, 540

BG = (7, 9, 20)
PANEL = (24, 29, 50)
PANEL_2 = (34, 42, 69)
TEXT = (248, 251, 255)
MUTED = (165, 176, 205)
ACCENT = (30, 215, 96)
BLUE = (56, 189, 248)
PURPLE = (124, 58, 237)
RED = (251, 91, 107)
INK = (11, 18, 32)


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            test = f"{line} {word}"
            if text_size(draw, test, font)[0] <= width:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    line_gap: int = 8,
    max_lines: int | None = None,
    center: bool = False,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, font, width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "..."
    line_h = text_size(draw, "Ag", font)[1] + line_gap
    for line in lines:
        line_x = x
        if center:
            line_x = x + (width - text_size(draw, line, font)[0]) // 2
        draw.text((line_x, y), line, font=font, fill=fill)
        y += line_h
    return y


def background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(7 + 18 * y / H)
        g = int(9 + 12 * y / H)
        b = int(20 + 28 * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    draw.ellipse((-260, -220, 610, 430), fill=(16, 88, 52))
    draw.ellipse((1030, -230, 1830, 390), fill=(56, 28, 118))
    draw.ellipse((1180, 640, 1780, 1150), fill=(9, 62, 78))
    return img


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill=PANEL, outline=(63, 72, 102), radius=28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def title(draw: ImageDraw.ImageDraw, kicker: str, heading: str, subtitle: str | None = None) -> None:
    draw.text((70, 45), kicker.upper(), font=get_font(18, True), fill=ACCENT)
    draw_wrapped(draw, (70, 86), heading, get_font(48, True), TEXT, 1280, line_gap=10, max_lines=2)
    if subtitle:
        draw_wrapped(draw, (72, 180), subtitle, get_font(25), MUTED, 1250, line_gap=6, max_lines=2)


def footer(draw: ImageDraw.ImageDraw, num: int) -> None:
    draw.text((70, 850), "AI Music Recommendation System", font=get_font(16), fill=(95, 107, 135))
    text = f"{num:02d}/21"
    tw, _ = text_size(draw, text, get_font(16, True))
    draw.text((W - 70 - tw, 850), text, font=get_font(16, True), fill=(95, 107, 135))


def metric(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str, color=ACCENT) -> None:
    card(draw, (x, y, x + 250, y + 105), PANEL_2, radius=24)
    draw.text((x + 20, y + 18), label, font=get_font(17, True), fill=MUTED)
    draw.text((x + 20, y + 50), value, font=get_font(34, True), fill=color)


def mini_card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, heading: str, body: str, color=ACCENT) -> None:
    card(draw, (x, y, x + w, y + h))
    draw.text((x + 24, y + 22), heading, font=get_font(24, True), fill=color)
    draw_wrapped(draw, (x + 24, y + 68), body, get_font(20), TEXT, w - 48, line_gap=8, max_lines=4)


def bullet_list(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, items: Iterable[str], size: int = 24) -> None:
    font = get_font(size)
    yy = y
    for item in items:
        draw.rounded_rectangle((x, yy + 8, x + 16, yy + 24), radius=8, fill=ACCENT)
        yy = draw_wrapped(draw, (x + 34, yy), item, font, TEXT, width - 34, line_gap=8, max_lines=2) + 8


def paste_asset(img: Image.Image, name: str, box: tuple[int, int, int, int]) -> None:
    path = ASSET_DIR / name
    if not path.exists():
        return
    asset = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    asset.thumbnail((x2 - x1, y2 - y1), Image.LANCZOS)
    ax = x1 + (x2 - x1 - asset.width) // 2
    ay = y1 + (y2 - y1 - asset.height) // 2
    draw = ImageDraw.Draw(img)
    card(draw, (x1 - 8, y1 - 8, x2 + 8, y2 + 8), (15, 20, 38), radius=30)
    img.paste(asset, (ax, ay))


def flow(draw: ImageDraw.ImageDraw, items: list[tuple[str, str]], y: int) -> None:
    for i, (head, body) in enumerate(items):
        x = 70 + i * 298
        card(draw, (x, y, x + 245, y + 150), PANEL_2, radius=24)
        draw_wrapped(draw, (x + 18, y + 28), head, get_font(23, True), TEXT, 209, max_lines=1, center=True)
        draw_wrapped(draw, (x + 20, y + 72), body, get_font(17), MUTED, 205, max_lines=2, center=True)
        if i < len(items) - 1:
            draw.text((x + 258, y + 55), ">", font=get_font(38, True), fill=ACCENT)


def make_slide(num: int, build_fn) -> Path:
    img = background()
    draw = ImageDraw.Draw(img)
    build_fn(img, draw)
    footer(draw, num)
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = PAGE_DIR / f"slide_{num:02d}.jpg"
    img.save(path, quality=92, optimize=True)
    return path


def build_pages() -> list[Path]:
    PPT_DIR.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []

    def s01(img, draw):
        draw.text((70, 70), "AI FAIR 2026 - MACHINE LEARNING TRACK", font=get_font(20, True), fill=ACCENT)
        draw_wrapped(draw, (70, 150), "AI Music Recommendation System", get_font(72, True), TEXT, 720, line_gap=14)
        draw_wrapped(draw, (75, 360), "Training a hybrid recommendation model from playlists, song features, and user feedback.", get_font(30), MUTED, 670, line_gap=10)
        metric(draw, 75, 570, "Main Model", "LightFM")
        metric(draw, 350, 570, "Output", "Daily 50", BLUE)
        metric(draw, 625, 570, "Storage", "CSV")
        paste_asset(img, "ppt-ui-home.png", (910, 130, 1510, 610))
        draw_wrapped(draw, (930, 690), "Presenter: AI Fair Project Team", get_font(24, True), MUTED, 520, center=True)

    def s02(img, draw):
        title(draw, "project overview", "The project solves a real music recommendation problem.", "It learns from playlist behavior and feedback instead of returning random songs.")
        mini_card(draw, 80, 330, 430, 220, "Problem", "Music libraries are too large to browse manually. A recommender should learn the listener's taste.")
        mini_card(draw, 560, 330, 430, 220, "Users", "Students, music listeners, and AI Fair visitors who want to see a model learn from data.", BLUE)
        mini_card(draw, 1040, 330, 430, 220, "Goal", "Show the complete machine learning loop: data, features, training, prediction, and feedback.", PURPLE)
        draw_wrapped(draw, (140, 660), "Thesis: this is not just a search page. It creates training data, trains a hybrid model, and updates recommendations after feedback.", get_font(32, True), ACCENT, 1320, center=True)

    def s03(img, draw):
        title(draw, "system architecture", "A local Flask app turns music metadata and user actions into training data.")
        flow(draw, [("Playlist Import", "QQ metadata"), ("Song Search", "Local + APIs"), ("CSV Store", "songs + feedback"), ("Training", "LightFM WARP"), ("Ranking", "Final 50")], 340)
        draw_wrapped(draw, (160, 650), "All data is stored locally. Online services are used only for public song metadata. The system does not download music audio.", get_font(30), MUTED, 1280, center=True)

    def s04(img, draw):
        title(draw, "dataset and features", "The dataset is inspectable, structured, and ready for machine learning.")
        rows = [
            ("songs.csv", "Song metadata + audio features", "track, artist, genre, energy, tempo, popularity"),
            ("interactions.csv", "Training signals", "playlist_import, manual_add, like, dislike"),
            ("feedback.csv", "Explicit feedback", "Like = 1, Dislike = 0"),
            ("playlists.csv", "Import history", "source, song_count, created_at"),
        ]
        for i, (a, b, c) in enumerate(rows):
            y = 285 + i * 125
            card(draw, (120, y, 1480, y + 82), PANEL_2, radius=22)
            draw.text((150, y + 25), a, font=get_font(27, True), fill=ACCENT)
            draw.text((460, y + 25), b, font=get_font(25, True), fill=TEXT)
            draw.text((850, y + 27), c, font=get_font(20), fill=MUTED)

    def s05(img, draw):
        title(draw, "playlist import", "QQ Music links are parsed safely, then metadata is imported.")
        bullet_list(draw, 90, 300, 690, [
            "Supports playlist/{id}, taoge.html?id=, disstid=, tid=, and pure numeric IDs.",
            "Tries multiple metadata endpoints: qzone, v8 playlist, and musicu.fcg.",
            "Imports metadata only. It does not download music or bypass copyright.",
            "If QQ fails, the user can use manual input or song search."
        ])
        card(draw, (880, 300, 1470, 650), PANEL_2)
        draw.text((920, 340), "URL extraction example", font=get_font(30, True), fill=ACCENT)
        code = "QQ playlist URL\n> extract playlist_id\n> fetch metadata\n> normalize songs\n> save songs.csv\n> create interactions"
        draw_wrapped(draw, (920, 420), code, get_font(27, True), TEXT, 500, line_gap=12)

    def s06(img, draw):
        title(draw, "music search APIs", "The app searches local data first, then public music metadata APIs.")
        providers = [
            ("1", "Local CSV", "Fast, stable, includes model-ready features."),
            ("2", "Deezer", "Public metadata for mainstream songs."),
            ("3", "MusicBrainz", "Open music database, rate limited safely."),
            ("4", "Last.fm", "Optional API key. Skipped if missing."),
        ]
        for i, (n, name, body) in enumerate(providers):
            x = 120 + (i % 2) * 720
            y = 295 + (i // 2) * 180
            card(draw, (x, y, x + 610, y + 125), PANEL_2)
            draw.rounded_rectangle((x + 24, y + 28, x + 78, y + 82), radius=16, fill=ACCENT)
            draw.text((x + 42, y + 40), n, font=get_font(25, True), fill=INK)
            draw.text((x + 105, y + 25), name, font=get_font(30, True), fill=TEXT)
            draw_wrapped(draw, (x + 105, y + 68), body, get_font(21), MUTED, 460)
        draw_wrapped(draw, (160, 690), "Every request uses timeout=8 and try/except, so API failure does not crash the Flask app.", get_font(30, True), BLUE, 1280, center=True)

    def s07(img, draw):
        title(draw, "feature engineering", "Songs become item feature tokens that LightFM can learn from.")
        tokens = ["genre:pop", "artist:the_weeknd", "tag:dance", "source:qq", "energy:high", "tempo:fast", "valence:positive", "danceability:high", "popularity:high"]
        for i, tok in enumerate(tokens):
            x = 120 + (i % 3) * 500
            y = 290 + (i // 3) * 120
            card(draw, (x, y, x + 390, y + 74), PANEL_2, radius=22)
            draw_wrapped(draw, (x + 20, y + 20), tok, get_font(26, True), ACCENT if i % 2 == 0 else BLUE, 350, center=True)
        draw_wrapped(draw, (190, 690), "The model learns from interpretable features such as high energy, fast tempo, genre, artist, source, and mood.", get_font(30), MUTED, 1220, center=True)

    def s08(img, draw):
        title(draw, "training data", "Playlist actions and feedback become a user-song interaction matrix.")
        metric(draw, 150, 300, "playlist_import", "+1.0")
        metric(draw, 435, 300, "manual_add", "+1.0", BLUE)
        metric(draw, 720, 300, "like", "+2.0")
        metric(draw, 1005, 300, "dislike", "-1.0", RED)
        card(draw, (180, 535, 1420, 660), PANEL_2)
        draw_wrapped(draw, (225, 570), "LightFM WARP trains from positive ranking examples. Dislikes are stored and used during re-ranking to lower scores.", get_font(34, True), TEXT, 1150, center=True)

    def s09(img, draw):
        title(draw, "model and method", "LightFM is the main machine learning model because it supports hybrid recommendation.")
        bullet_list(draw, 100, 300, 650, [
            "Open-source recommender library.",
            "Learns from implicit and explicit feedback.",
            "Uses WARP ranking loss for Top-N recommendation.",
            "Combines interactions with item features.",
            "Works well for a school AI Fair dataset."
        ])
        card(draw, (860, 300, 1460, 620), PANEL_2)
        draw.text((900, 345), "Training object", font=get_font(32, True), fill=ACCENT)
        code = 'model = LightFM(loss="warp")\nmodel.fit(interactions,\n          item_features,\n          sample_weight,\n          epochs=30)'
        draw_wrapped(draw, (900, 425), code, get_font(28, True), TEXT, 520, line_gap=14)

    def s10(img, draw):
        title(draw, "training workflow", "The UI exposes the machine learning pipeline.")
        paste_asset(img, "ppt-ui-training.png", (80, 260, 800, 690))
        bullet_list(draw, 900, 295, 560, ["Import or manually add songs.", "Write interactions.csv rows.", "Build item feature tokens.", "Train LightFM WARP.", "Save lightfm_model.pkl.", "Show model status in the UI."], 26)

    def s11(img, draw):
        title(draw, "recommendation ranking", "Final recommendations blend learned preference and content similarity.")
        draw_wrapped(draw, (150, 280), "final_score = 0.7 x model_score + 0.3 x content_similarity_score", get_font(42, True), ACCENT, 1300, center=True)
        mini_card(draw, 120, 430, 420, 205, "model_score", "The trained LightFM model predicts how much the user may like each candidate song.")
        mini_card(draw, 580, 430, 420, 205, "content_similarity", "Cosine similarity compares audio features such as energy, tempo, danceability, and mood.", BLUE)
        mini_card(draw, 1040, 430, 420, 205, "rule explanation", "Reasons are generated deterministically, not by a language model.", PURPLE)

    def s12(img, draw):
        title(draw, "software experience", "The app looks and feels like a modern music recommendation dashboard.")
        paste_asset(img, "ppt-ui-home.png", (80, 260, 760, 650))
        paste_asset(img, "ppt-ui-recommendations.png", (840, 260, 1520, 650))
        draw_wrapped(draw, (170, 710), "Bilingual UI, playlist import, manual songs, model status, recommendation cards, Like/Dislike, and Daily 50 output.", get_font(28), MUTED, 1260, center=True)

    def s13(img, draw):
        title(draw, "results and evaluation", "The system produces ranked songs, explanations, and a final 50-song daily mix.")
        paste_asset(img, "ppt-ui-recommendations.png", (80, 250, 780, 690))
        metric(draw, 880, 290, "Top Cards", "10")
        metric(draw, 1160, 290, "Final Mix", "50", BLUE)
        metric(draw, 880, 430, "Explanation", "Rules")
        metric(draw, 1160, 430, "Feedback", "Retrain")
        draw_wrapped(draw, (880, 590), "After Like/Dislike feedback, interactions.csv changes, the model retrains, and future rankings shift.", get_font(27), MUTED, 560)

    def s14(img, draw):
        title(draw, "final output", "Daily Recommendation Mix turns model scores into a show-ready playlist.")
        paste_asset(img, "ppt-ui-daily.png", (80, 245, 920, 710))
        bullet_list(draw, 1010, 310, 470, ["Generates up to 50 songs.", "Filters songs already used for training.", "Reduces repeated artists and genres.", "Can be copied as playlist text output."], 26)

    def s15(img, draw):
        title(draw, "real-world use", "The same pipeline can support personal and school music discovery.")
        mini_card(draw, 100, 315, 410, 210, "For students", "Learn ML from a product everyone understands: playlists and song recommendations.")
        mini_card(draw, 560, 315, 410, 210, "For music apps", "Convert playlist behavior and feedback into a recommendation loop.", BLUE)
        mini_card(draw, 1020, 315, 410, 210, "Future work", "Add richer audio analysis, multi-user data, metrics, and stronger diversity controls.", PURPLE)
        draw_wrapped(draw, (170, 670), "Most useful improvement: collect more feedback over time and evaluate precision@k and recall@k.", get_font(32, True), ACCENT, 1260, center=True)

    def s16(img, draw):
        title(draw, "ethical AI disclosure", "The project uses AI help responsibly and avoids copyright risks.")
        bullet_list(draw, 100, 300, 720, ["AI assistance was used for coding, debugging, UI writing, and documentation support.", "The model and code were checked and understood by the student.", "No local LLM, LM Studio, Ollama, or OpenAI API is used for explanations.", "QQ import uses metadata only, with no audio download or unauthorized playback."], 24)
        mini_card(draw, 940, 310, 430, 260, "Risk controls", "Timeouts for API requests, friendly error fallback, local CSV storage, rule-based explanations, and no private audio scraping.", ACCENT)

    def s17(img, draw):
        title(draw, "limitations", "The model is real, but dataset size and public metadata sources limit accuracy.")
        mini_card(draw, 100, 315, 410, 210, "Small dataset", "A single demo user is useful for demonstration, not production-scale personalization.")
        mini_card(draw, 560, 315, 410, 210, "Estimated features", "Some online results do not provide true audio features, so the app estimates from metadata.", BLUE)
        mini_card(draw, 1020, 315, 410, 210, "Unstable APIs", "QQ Music public endpoints may change, so the app includes fallback and manual input.", PURPLE)
        draw_wrapped(draw, (170, 670), "Future improvements: real audio-feature sources, multi-user data, train/test evaluation, precision@k, recall@k, and stronger diversity re-ranking.", get_font(28), MUTED, 1260, center=True)

    def s18(img, draw):
        title(draw, "how to use", "Quick start: open the app, import music taste data, then train the model.")
        paste_asset(img, "ppt-ui-home.png", (80, 250, 760, 650))
        steps = [
            ("1", "Start the app", "Run python app.py and open the local URL."),
            ("2", "Import or add songs", "Paste a QQ playlist link or type Song - Artist lines."),
            ("3", "Check the dataset", "The app saves local CSV training data."),
            ("4", "Train the model", "Click Train Model to build LightFM.")
        ]
        for i, (n, head, body) in enumerate(steps):
            y = 250 + i * 108
            card(draw, (870, y, 1480, y + 82), PANEL_2, radius=22)
            draw.rounded_rectangle((895, y + 21, 940, y + 66), radius=14, fill=ACCENT)
            draw.text((910, y + 30), n, font=get_font(21, True), fill=INK)
            draw.text((965, y + 14), head, font=get_font(25, True), fill=TEXT)
            draw_wrapped(draw, (965, y + 46), body, get_font(18), MUTED, 420, max_lines=1)

    def s19(img, draw):
        title(draw, "demo tutorial", "A live demo can show the full ML loop in under three minutes.")
        items = [
            ("Step 1", "Search or import", "Use familiar songs or a QQ playlist."),
            ("Step 2", "Create interactions", "Add songs to the training playlist."),
            ("Step 3", "Train LightFM", "Show users, songs, interactions, and item features."),
            ("Step 4", "Recommend", "Show Top 10 scores and rule-based reasons."),
            ("Step 5", "Feedback", "Click Like or Dislike to update training data."),
            ("Step 6", "Final 50", "Generate a Daily Recommendation Mix.")
        ]
        for i, (label, head, body) in enumerate(items):
            x = 100 + (i % 2) * 760
            y = 250 + (i // 2) * 145
            card(draw, (x, y, x + 650, y + 105), PANEL_2, radius=24)
            draw.text((x + 24, y + 20), label, font=get_font(18, True), fill=ACCENT)
            draw.text((x + 135, y + 18), head, font=get_font(27, True), fill=TEXT)
            draw_wrapped(draw, (x + 135, y + 55), body, get_font(20), MUTED, 470, max_lines=1)
        draw_wrapped(draw, (160, 715), "Key line: every click creates data that can change the trained model.", get_font(30, True), BLUE, 1280, center=True)

    def s20(img, draw):
        title(draw, "usage notes", "If an online service fails, the system still works through local data and manual input.")
        mini_card(draw, 100, 310, 410, 210, "If QQ import fails", "Use manual playlist input or Search Songs. Public QQ endpoints can change or block some playlists.")
        mini_card(draw, 560, 310, 410, 210, "If API search is slow", "The app uses timeouts and skips failed providers so Flask stays running.", BLUE)
        mini_card(draw, 1020, 310, 410, 210, "If LightFM is unavailable", "The app falls back to content similarity and a logistic regression feedback model.", PURPLE)
        draw_wrapped(draw, (170, 670), "The project is designed for live demos: API errors become friendly messages while local data and the recommender still work.", get_font(30, True), ACCENT, 1260, center=True)

    def s21(img, draw):
        draw.text((80, 80), "CLOSING", font=get_font(20, True), fill=ACCENT)
        draw_wrapped(draw, (80, 160), "This project shows the full ML loop: data, features, training, ranking, and feedback.", get_font(60, True), TEXT, 850, line_gap=15)
        paste_asset(img, "ppt-ui-home.png", (990, 130, 1510, 520))
        draw_wrapped(draw, (90, 590), "Playlist import creates implicit feedback. Like/Dislike creates explicit feedback. LightFM learns preferences and ranks songs the user is likely to enjoy.", get_font(31), MUTED, 770)
        draw_wrapped(draw, (200, 780), "Thank you. Questions?", get_font(44, True), ACCENT, 1200, center=True)

    builders = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21]
    for idx, fn in enumerate(builders, start=1):
        pages.append(make_slide(idx, fn))
    return pages


def build_pdf(pages: list[Path]) -> None:
    c = canvas.Canvas(str(PDF_PATH), pagesize=(PDF_W, PDF_H))
    for page in pages:
        c.drawImage(ImageReader(str(page)), 0, 0, width=PDF_W, height=PDF_H)
        c.showPage()
    c.save()


if __name__ == "__main__":
    pages = build_pages()
    build_pdf(pages)
    print(PDF_PATH)

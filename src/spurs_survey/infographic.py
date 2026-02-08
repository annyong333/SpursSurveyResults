"""Infographic generator — renders a 1920×1080 results image.

Produces a three-column layout:
  - Left sidebar (22%): match info, score, overall rating, manager card, photo, quote
  - Main content (56%): formation-based player layout over stadium background
  - Right sidebar (22%): substitute player cards
"""

from __future__ import annotations

import logging
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from spurs_survey.formations import FORMATION_LAYOUTS
from spurs_survey.models import (
    CoachRatings,
    CompiledResults,
    PlayerRating,
    RatingStats,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1920, 1080

LEFT_PCT = 0.22
MAIN_PCT = 0.56
RIGHT_PCT = 0.22

LEFT_W = int(WIDTH * LEFT_PCT)
MAIN_W = int(WIDTH * MAIN_PCT)
RIGHT_W = WIDTH - LEFT_W - MAIN_W

MAIN_X = LEFT_W
RIGHT_X = LEFT_W + MAIN_W

# Colours
NAVY = (15, 20, 50)
DARK_NAVY = (10, 14, 36)
BLUE_OVERLAY = (20, 40, 100, 160)
YELLOW = (255, 210, 50)
WHITE = (255, 255, 255)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
BLACK = (0, 0, 0)
PILL_BG = (20, 20, 20, 220)
CARD_BG = (30, 35, 60, 200)
SIDEBAR_BG = (18, 22, 48)

PLACEHOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets",
    "placeholder.png",
)

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a system font; fall back to default bitmap font."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSDisplay-Bold.otf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSDisplay.otf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def _load_player_image(image_path: str | None, size: int = 80) -> Image.Image:
    """Load and resize a player image, falling back to placeholder."""
    target = None
    if image_path and os.path.isfile(image_path):
        target = image_path
    elif os.path.isfile(PLACEHOLDER_PATH):
        target = PLACEHOLDER_PATH
    else:
        # Generate a simple gray circle as last-resort placeholder
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, size - 1, size - 1], fill=(160, 160, 160, 255))
        return img

    try:
        img = Image.open(target).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        return img
    except Exception:
        logger.warning("Failed to load image %s, using fallback", target)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, size - 1, size - 1], fill=(160, 160, 160, 255))
        return img


def _draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    cx: int,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple,
) -> int:
    """Draw text centered at (cx, y). Returns the bottom y coordinate."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, y), text, font=font, fill=fill)
    return y + th


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    text: str,
    cx: int,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    bg: tuple = PILL_BG,
    fg: tuple = WHITE,
    pad_x: int = 10,
    pad_y: int = 3,
) -> int:
    """Draw text on a rounded-rect pill. Returns bottom y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx = cx - tw // 2 - pad_x
    ry = y
    rw = tw + 2 * pad_x
    rh = th + 2 * pad_y
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=rh // 2, fill=bg)
    draw.text((cx - tw // 2, y + pad_y), text, font=font, fill=fg)
    return y + rh


def _draw_rating_circle(
    draw: ImageDraw.ImageDraw,
    rating: float,
    cx: int,
    cy: int,
    radius: int = 16,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None,
) -> None:
    """Draw a yellow circle with the rating value inside."""
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=YELLOW,
    )
    text = f"{rating:.1f}"
    f = font or _get_font(max(radius, 12), bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=f, fill=BLACK)


# ---------------------------------------------------------------------------
# Player card renderer
# ---------------------------------------------------------------------------

def _draw_player_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    player: PlayerRating,
    cx: int,
    cy: int,
    img_size: int = 70,
) -> None:
    """Draw a single player card centred at (cx, cy).

    Layout (top to bottom):
      - Player image
      - Uppercase name pill
      - Yellow rating circle + gray stddev
      - Event badges (goals, assists, own goals, MOTM)
    """
    font_name = _get_font(11, bold=True)
    font_rating = _get_font(13, bold=True)
    font_std = _get_font(10)
    font_badge = _get_font(10, bold=True)

    # Player image
    img = _load_player_image(player.image_path, img_size)
    paste_x = cx - img_size // 2
    paste_y = cy - img_size // 2 - 20
    canvas.paste(img, (paste_x, paste_y), img)

    # Name pill
    name_y = paste_y + img_size + 2
    _draw_pill(draw, player.name.upper(), cx, name_y, font_name, pad_x=8, pad_y=2)

    # Rating circle + stddev
    rating_y = name_y + 22
    _draw_rating_circle(draw, player.rating.mean, cx, rating_y + 14, radius=14, font=font_rating)
    std_text = f"±{player.rating.std_dev:.1f}"
    draw.text((cx + 18, rating_y + 8), std_text, font=font_std, fill=LIGHT_GRAY)

    # Event badges
    badge_y = rating_y + 32
    badges: list[str] = []
    if player.goals > 0:
        badges.append("⚽" * player.goals)
    if player.assists > 0:
        badges.append("👟" * player.assists)
    if player.own_goals > 0:
        badges.append("🔴" * player.own_goals)
    if player.is_motm:
        badges.append("MOTM")

    if badges:
        badge_str = " ".join(badges)
        _draw_text_centered(draw, badge_str, cx, badge_y, font_badge, YELLOW)


# ---------------------------------------------------------------------------
# Left sidebar renderer
# ---------------------------------------------------------------------------

def _draw_left_sidebar(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    results: CompiledResults,
    quote: str,
    photo_path: str,
) -> None:
    """Render the left sidebar: match info, score, overall, manager, photo, quote."""
    meta = results.match_metadata

    # Background
    draw.rectangle([0, 0, LEFT_W, HEIGHT], fill=NAVY)

    font_title = _get_font(16, bold=True)
    font_large = _get_font(28, bold=True)
    font_med = _get_font(14, bold=True)
    font_sm = _get_font(12)
    font_score = _get_font(36, bold=True)
    font_diamond = _get_font(22, bold=True)

    cx = LEFT_W // 2
    y = 20

    # Match header: competition + matchday
    y = _draw_text_centered(draw, meta.competition.upper(), cx, y, font_title, YELLOW) + 4
    y = _draw_text_centered(draw, meta.matchday, cx, y, font_sm, LIGHT_GRAY) + 2
    y = _draw_text_centered(draw, f"{meta.venue}  •  {meta.date}", cx, y, font_sm, LIGHT_GRAY) + 16

    # Score block
    if meta.is_tottenham_home:
        left_team, right_team = "TOTTENHAM", meta.opponent.upper()
        left_score, right_score = meta.home_score, meta.away_score
        left_rating = results.team_rating
        right_rating = results.opponent_rating
    else:
        left_team, right_team = meta.opponent.upper(), "TOTTENHAM"
        left_score, right_score = meta.home_score, meta.away_score
        left_rating = results.opponent_rating
        right_rating = results.team_rating

    y = _draw_text_centered(draw, left_team, cx, y, font_med, WHITE) + 2
    score_str = f"{left_score}  -  {right_score}"
    y = _draw_text_centered(draw, score_str, cx, y, font_score, WHITE) + 2
    y = _draw_text_centered(draw, right_team, cx, y, font_med, WHITE) + 6

    # Team ratings below score
    rating_str = f"{left_rating.mean:.1f}  vs  {right_rating.mean:.1f}"
    y = _draw_text_centered(draw, rating_str, cx, y, font_sm, LIGHT_GRAY) + 20

    # Diamond overall rating
    diamond_cy = y + 30
    diamond_r = 28
    diamond_points = [
        (cx, diamond_cy - diamond_r),
        (cx + diamond_r, diamond_cy),
        (cx, diamond_cy + diamond_r),
        (cx - diamond_r, diamond_cy),
    ]
    draw.polygon(diamond_points, fill=YELLOW)
    overall_text = f"{results.overall_rating:.1f}"
    bbox = draw.textbbox((0, 0), overall_text, font=font_diamond)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, diamond_cy - th // 2), overall_text, font=font_diamond, fill=BLACK)
    y = diamond_cy + diamond_r + 6
    y = _draw_text_centered(draw, "OVERALL", cx, y, font_sm, LIGHT_GRAY) + 16

    # Manager card
    _draw_manager_card(draw, results.coach_ratings, cx, y, font_med, font_sm)
    y += 100

    # Photo of the match
    if photo_path and os.path.isfile(photo_path):
        try:
            photo = Image.open(photo_path).convert("RGBA")
            photo_w = LEFT_W - 30
            ratio = photo_w / photo.width
            photo_h = int(photo.height * ratio)
            photo_h = min(photo_h, 160)
            photo = photo.resize((photo_w, photo_h), Image.LANCZOS)
            canvas.paste(photo, (15, y), photo)
            y += photo_h + 8
        except Exception:
            logger.warning("Could not load photo: %s", photo_path)
            y += 8
    else:
        y += 8

    # Quote of the match
    if quote:
        _draw_quote(draw, quote, cx, y, LEFT_W - 30, font_sm)


def _draw_manager_card(
    draw: ImageDraw.ImageDraw,
    coach: CoachRatings,
    cx: int,
    y: int,
    font_name: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    font_sm: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw the manager card with three tactical ratings."""
    card_w = LEFT_W - 30
    card_x = cx - card_w // 2
    draw.rounded_rectangle(
        [card_x, y, card_x + card_w, y + 90],
        radius=8,
        fill=CARD_BG,
    )
    _draw_text_centered(draw, coach.name.upper(), cx, y + 6, font_name, WHITE)

    row_y = y + 28
    items = [
        ("XI Selection", coach.starting_eleven),
        ("Tactics", coach.on_field_tactics),
        ("Subs", coach.substitutions),
    ]
    for label, stats in items:
        text = f"{label}: {stats.mean:.1f}"
        _draw_text_centered(draw, text, cx, row_y, font_sm, LIGHT_GRAY)
        row_y += 18


def _draw_quote(
    draw: ImageDraw.ImageDraw,
    quote: str,
    cx: int,
    y: int,
    max_width: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw a wrapped quote string."""
    words = quote.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    _draw_text_centered(draw, '"QUOTE OF THE MATCH"', cx, y, font, YELLOW)
    y += 18
    for line in lines[:4]:  # cap at 4 lines
        y = _draw_text_centered(draw, line, cx, y, font, WHITE) + 2


# ---------------------------------------------------------------------------
# Main content renderer (formation layout)
# ---------------------------------------------------------------------------

def _draw_main_content(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    results: CompiledResults,
) -> None:
    """Render the main content area with formation-based player layout."""
    # Background: blurred dark blue
    bg = Image.new("RGBA", (MAIN_W, HEIGHT), NAVY)
    bg_draw = ImageDraw.Draw(bg)
    # Gradient-ish overlay
    for yy in range(HEIGHT):
        alpha = int(100 + 60 * (yy / HEIGHT))
        bg_draw.line([(0, yy), (MAIN_W, yy)], fill=(20, 40, 100, alpha))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=3))
    canvas.paste(bg, (MAIN_X, 0))

    font_header = _get_font(14, bold=True)
    font_sm = _get_font(11)
    font_ref = _get_font(12, bold=True)

    # Header: response count
    header_text = f"PLAYER RATINGS  •  {results.total_responses} RESPONSES"
    _draw_text_centered(
        draw, header_text,
        MAIN_X + MAIN_W // 2, 12,
        font_header, WHITE,
    )

    # Formation layout
    formation = results.formation
    layout = FORMATION_LAYOUTS.get(formation)
    if layout is None:
        # Fallback: flat list
        logger.warning("Unknown formation %s, using flat layout", formation)
        layout = [("PL", len(results.starting_player_ratings))]

    # Distribute players into rows
    players = list(results.starting_player_ratings)
    rows: list[list[PlayerRating]] = []
    idx = 0
    for _label, count in layout:
        row = players[idx : idx + count]
        rows.append(row)
        idx += count

    # Y positions for rows (top = attackers, bottom = GK)
    num_rows = len(rows)
    y_start = 60
    y_end = HEIGHT - 100
    row_spacing = (y_end - y_start) // max(num_rows, 1)

    for row_idx, row_players in enumerate(rows):
        row_cy = y_start + row_idx * row_spacing + row_spacing // 2
        n = len(row_players)
        if n == 0:
            continue
        col_spacing = MAIN_W // (n + 1)
        for col_idx, player in enumerate(row_players):
            px = MAIN_X + col_spacing * (col_idx + 1)
            _draw_player_card(canvas, draw, player, px, row_cy)

    # Referee rating at bottom
    ref_y = HEIGHT - 70
    ref_cx = MAIN_X + MAIN_W // 2
    ref_text = f"REFEREE: {results.referee_rating.mean:.1f}"
    _draw_text_centered(draw, ref_text, ref_cx, ref_y, font_ref, WHITE)

    # Legend at very bottom
    legend_y = HEIGHT - 40
    legend_items = [
        ("● = Avg Rating", YELLOW),
        ("⚽ = Goal", WHITE),
        ("👟 = Assist", WHITE),
        ("±n = Std Dev", LIGHT_GRAY),
    ]
    legend_font = _get_font(10)
    lx = MAIN_X + 30
    for text, color in legend_items:
        draw.text((lx, legend_y), text, font=legend_font, fill=color)
        bbox = draw.textbbox((0, 0), text, font=legend_font)
        lx += (bbox[2] - bbox[0]) + 20


# ---------------------------------------------------------------------------
# Right sidebar renderer (substitutes)
# ---------------------------------------------------------------------------

def _draw_right_sidebar(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    results: CompiledResults,
) -> None:
    """Render the right sidebar with substitute player cards."""
    draw.rectangle([RIGHT_X, 0, WIDTH, HEIGHT], fill=SIDEBAR_BG)

    font_header = _get_font(14, bold=True)
    cx = RIGHT_X + RIGHT_W // 2

    _draw_text_centered(draw, "SUBSTITUTES", cx, 16, font_header, YELLOW)

    subs = results.substitute_player_ratings
    if not subs:
        font_sm = _get_font(11)
        _draw_text_centered(draw, "No substitutions", cx, 50, font_sm, LIGHT_GRAY)
        return

    # Space subs evenly in the sidebar
    available_h = HEIGHT - 60
    spacing = min(available_h // len(subs), 180)
    start_y = 60 + spacing // 2

    for i, player in enumerate(subs):
        py = start_y + i * spacing
        _draw_player_card(canvas, draw, player, cx, py, img_size=60)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_infographic(
    results: CompiledResults,
    quote: str,
    photo_path: str,
    output_path: str,
) -> str:
    """Generate a 1920×1080 results infographic PNG.

    Parameters
    ----------
    results : CompiledResults
        Compiled survey results for the match.
    quote : str
        "Quote of the match" text to display in the left sidebar.
    photo_path : str
        Path to a "photo of the match" image file.
    output_path : str
        Destination path for the output PNG.

    Returns
    -------
    str
        The *output_path* where the PNG was saved.
    """
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(canvas)

    _draw_left_sidebar(canvas, draw, results, quote, photo_path)
    _draw_main_content(canvas, draw, results)
    _draw_right_sidebar(canvas, draw, results)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Save as RGB PNG (drop alpha)
    canvas.convert("RGB").save(output_path, "PNG")
    logger.info("Infographic saved to %s", output_path)
    return output_path

"""Generate a simple silhouette placeholder PNG for missing player images."""

from PIL import Image, ImageDraw

def create_placeholder(output_path: str = "assets/placeholder.png", size: int = 200) -> None:
    """Create a gray silhouette placeholder image."""
    img = Image.new("RGBA", (size, size), (200, 200, 200, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # Head (circle)
    head_r = size // 6
    head_cy = cy - size // 6
    draw.ellipse(
        [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
        fill=(160, 160, 160, 255),
    )

    # Body (rounded trapezoid approximation)
    body_top = head_cy + head_r + 4
    body_bottom = size - 10
    shoulder_w = size // 3
    hip_w = size // 4
    draw.polygon(
        [
            (cx - shoulder_w, body_top),
            (cx + shoulder_w, body_top),
            (cx + hip_w, body_bottom),
            (cx - hip_w, body_bottom),
        ],
        fill=(160, 160, 160, 255),
    )

    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Placeholder saved to {output_path}")


if __name__ == "__main__":
    create_placeholder()

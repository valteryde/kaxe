"""
Test assertion tools for Kaxe regression testing.

Provides pixel_match, fingerprint_match, judge, sanity_check, diff_image,
and crop_region for use with the custom test runner.
"""

from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path
from typing import Optional

from PIL import Image

try:
    import imagehash
except ImportError:
    imagehash = None  # type: ignore

try:
    import openai
except ImportError:
    openai = None  # type: ignore

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass


def pixel_match(
    image: Image.Image,
    reference_image: Image.Image,
    tolerance: int = 0,
) -> bool:
    """
    Compare two images byte-for-byte. Optionally allow up to `tolerance`
    differing pixels (for minor antialiasing differences).

    Returns True if images match within tolerance.
    """
    if tolerance <= 0:
        return image.tobytes() == reference_image.tobytes()
    actual = image.tobytes()
    ref = reference_image.tobytes()
    if len(actual) != len(ref):
        return False
    diff_count = sum(1 for a, r in zip(actual, ref) if a != r)
    return diff_count <= tolerance


def pixel_diff_count(image: Image.Image, reference_image: Image.Image) -> int:
    """Return the number of differing bytes between two images."""
    actual = image.tobytes()
    ref = reference_image.tobytes()
    if len(actual) != len(ref):
        return max(len(actual), len(ref))
    return sum(1 for a, r in zip(actual, ref) if a != r)


def fingerprint_match(
    image: Image.Image,
    reference_image: Image.Image,
    hash_size: int = 8,
    max_diff_bits: int = 5,
) -> bool:
    """
    Compare images using perceptual hash. Tolerant of minor antialiasing
    and font rendering differences.

    Returns True if hashes are within max_diff_bits.
    """
    if imagehash is None:
        raise ImportError("imagehash is required for fingerprint_match. Install with: pip install imagehash")
    hash_fn = imagehash.average_hash
    h1 = hash_fn(image, hash_size=hash_size)
    h2 = hash_fn(reference_image, hash_size=hash_size)
    return h1 - h2 <= max_diff_bits


def crop_region(image: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    """Extract a region (left, top, right, bottom) from the image."""
    return image.crop(bbox)


def sanity_check(
    image: Image.Image,
    min_size: tuple[int, int] = (10, 10),
    max_blank_ratio: float = 0.99,
) -> bool:
    """
    Assert image is not blank and has reasonable size/color distribution.

    - min_size: minimum (width, height)
    - max_blank_ratio: fail if more than this fraction of pixels are the
      dominant (background) color
    """
    w, h = image.size
    if w < min_size[0] or h < min_size[1]:
        return False
    # Convert to RGB if necessary for color analysis
    if image.mode != "RGB":
        img_rgb = image.convert("RGB")
    else:
        img_rgb = image
    pixels = list(img_rgb.getdata())
    total = len(pixels)
    if total == 0:
        return False
    # Count most common color
    from collections import Counter
    counts = Counter(pixels)
    most_common_count = counts.most_common(1)[0][1]
    blank_ratio = most_common_count / total
    return blank_ratio <= max_blank_ratio


def diff_image(
    actual: Image.Image,
    reference: Image.Image,
    out_path: str | Path,
) -> bool:
    """
    Compare images; on failure save a side-by-side diff to out_path.
    Returns True if images match (pixel_match).
    """
    if pixel_match(actual, reference):
        return True
    # Create side-by-side diff
    w1, h1 = actual.size
    w2, h2 = reference.size
    max_w = max(w1, w2)
    total_h = max(h1, h2)
    diff_img = Image.new("RGB", (max_w * 2 + 20, total_h), (255, 255, 255))
    diff_img.paste(actual.convert("RGB") if actual.mode != "RGB" else actual, (0, 0))
    diff_img.paste(reference.convert("RGB") if reference.mode != "RGB" else reference, (max_w + 20, 0))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    diff_img.save(out_path)
    return False


def judge(
    image: Image.Image,
    elements: list[str],
    focus: str,
    min_score: int = 7,
    model: str = "gpt-4o",
    strict_elements: bool = True,
) -> dict:
    """
    AI-powered visual QA. Sends image to OpenAI vision model for analysis.

    Returns dict with: legible, overlapping_text, missing_elements, score.
    Raises AssertionError if score < min_score, legible is False, or
    (when strict_elements) any requested element is in missing_elements.

    Be precise in elements: e.g. "sine curve" not "periodic curve" — the judge
    will treat cosine as missing "sine curve". Use model="gpt-4o" (default).
    """
    if openai is None:
        raise ImportError("openai is required for judge. Install with: pip install openai")

    # Encode image as base64
    buffer = io.BytesIO()
    if image.mode in ("RGBA", "P"):
        image.save(buffer, format="PNG")
    else:
        image.convert("RGB").save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    prompt = f"""
You are a Senior QA Engineer specialized in data visualization.
Analyze this plot and return a JSON object with the following keys:
{{
  "legible": boolean,
  "overlapping_text": boolean,
  "missing_elements": ["list", "of", "elements"],
  "incorrect_elements": ["elements present but wrong - e.g. cosine when sine was expected"],
  "score": 1-10
}}

The score is a score from 1 to 10, where 1 is the worst and 10 is the best.
The legible is a boolean that is true if the plot is legible.
The overlapping_text is a boolean that is true if the text is overlapping.
The missing_elements is a list of elements that are missing from the plot.
The incorrect_elements is a list of elements that are present but WRONG (e.g. we expect "sine curve" but the plot shows cosine — add "cosine curve" to incorrect_elements).

Be strict and precise. Names matter: sine ≠ cosine (sine crosses zero at the left, cosine has a peak). If an element is specified exactly, a similar-but-different thing counts as missing or incorrect.
Your focus is on the {focus}.
The elements that should be present are:
{"\n- ".join(elements)}

Return ONLY valid JSON, no other text.
"""

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from API")
        # Extract JSON (handle markdown code blocks)
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.startswith("```"))
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from judge API: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Judge API error: {e}") from e

    if result.get("score", 0) < min_score:
        raise AssertionError(
            f"Judge score {result.get('score')} below min_score {min_score}. "
            f"Result: {result}"
        )
    if not result.get("legible", True):
        raise AssertionError(f"Plot not legible. Result: {result}")

    if strict_elements:
        missing = result.get("missing_elements") or []
        incorrect = result.get("incorrect_elements") or []
        if missing:
            raise AssertionError(
                f"Judge reported missing elements: {missing}. "
                f"Expected all of: {elements}. Result: {result}"
            )
        if incorrect:
            raise AssertionError(
                f"Judge reported incorrect elements: {incorrect}. "
                f"Expected: {elements}. Result: {result}"
            )

    return result


def load_reference(references_dir: Path, reference_name: str) -> Image.Image:
    """Load a reference image from the references directory."""
    path = references_dir / reference_name
    if not path.exists():
        raise FileNotFoundError(f"Reference image not found: {path}")
    return Image.open(path).convert("RGBA")

"""
Custom test runner for Kaxe regression tests.

Uses Flask-style stacked decorators. Each decorator registers one assertion.
Run with: python -m runner [--test name] [--collect] [--update-refs]

Run from the kaxe/ directory.
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from PIL import Image

# Suppress noisy output before any kaxe/httpx imports
logging.basicConfig(level=logging.CRITICAL)
for _ in ("httpx", "httpcore", "openai"):
    logging.getLogger(_).setLevel(logging.CRITICAL)

# Ensure kaxe and tests are importable
_TESTS_DIR = Path(__file__).resolve().parent
_KAXE_ROOT = _TESTS_DIR.parent
if str(_KAXE_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_KAXE_ROOT / "src"))
if str(_KAXE_ROOT) not in sys.path:
    sys.path.insert(0, str(_KAXE_ROOT))
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

IMAGES_DIR = _TESTS_DIR / "images"
REFERENCES_DIR = IMAGES_DIR / "references"
REFERENCES_DIR.mkdir(parents=True, exist_ok=True)

# Attribute name for registered assertions
_ASSERTIONS_ATTR = "_kaxe_assertions"
_TEST_NAME_ATTR = "_kaxe_test_name"
_UNIT_ATTR = "_kaxe_unit_test"


def _ensure_assertions(fn: Callable) -> list:
    if not hasattr(fn, _ASSERTIONS_ATTR):
        setattr(fn, _ASSERTIONS_ATTR, [])
    return getattr(fn, _ASSERTIONS_ATTR)


def _decorator(mode: str, **kwargs: Any) -> Callable:
    """Factory for assertion decorators."""

    def decorator(fn: Callable) -> Callable:
        assertions = _ensure_assertions(fn)
        assertions.append((mode, kwargs))
        return fn

    return decorator


def smoke() -> Callable:
    """Run plot generation; pass if no exception."""
    return _decorator("smoke")


def sanity(min_size: tuple[int, int] = (10, 10), max_blank_ratio: float = 0.99) -> Callable:
    """Assert image is not blank and has reasonable size."""
    return _decorator("sanity", min_size=min_size, max_blank_ratio=max_blank_ratio)


def pixel(reference: str, tolerance: int = 0) -> Callable:
    """Exact byte match vs reference."""
    return _decorator("pixel", reference=reference, tolerance=tolerance)


def fingerprint(reference: str, hash_size: int = 8, max_diff_bits: int = 5) -> Callable:
    """Perceptual hash vs reference."""
    return _decorator(
        "fingerprint",
        reference=reference,
        hash_size=hash_size,
        max_diff_bits=max_diff_bits,
    )


def diff(reference: str, out_path: str | None = None) -> Callable:
    """Compare vs reference; save diff image on failure."""
    return _decorator("diff", reference=reference, out_path=out_path)


def region(reference: str, bbox: tuple[int, int, int, int]) -> Callable:
    """Compare cropped region vs reference."""
    return _decorator("region", reference=reference, bbox=bbox)


def judge(
    elements: list[str],
    focus: str,
    min_score: int = 7,
    model: str = "gpt-4o",
    strict_elements: bool = True,
) -> Callable:
    """AI vision check. Be precise in elements (e.g. 'sine curve' not 'periodic curve')."""
    return _decorator(
        "judge",
        elements=elements,
        focus=focus,
        min_score=min_score,
        model=model,
        strict_elements=strict_elements,
    )


def idempotent() -> Callable:
    """Run plot twice; assert outputs identical."""
    return _decorator("idempotent")


def stability(runs: int = 3) -> Callable:
    """Run N times; assert all outputs identical."""
    return _decorator("stability", runs=runs)


def unit() -> Callable:
    """Mark as unit test: no plot required, just run and assert. Use assert or return False/str to fail."""
    def decorator(fn: Callable) -> Callable:
        setattr(fn, _UNIT_ATTR, True)
        _ensure_assertions(fn)
        return fn
    return decorator


def _run_unit_test(fn: Callable, test_name: str) -> tuple[bool, list[str]]:
    """Run a unit test. Returns (passed, list of error messages)."""
    try:
        with _suppress_prints():
            result = fn()
        if result is False:
            return False, ["Unit test returned False"]
        if isinstance(result, str):
            return False, [result]
        return True, []
    except AssertionError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"{type(e).__name__}: {e}"]


def _run_assertion(
    mode: str,
    kwargs: dict,
    image: Image.Image,
    image_path: Path,
    test_name: str,
    collect_errors: bool,
) -> list[str]:
    """Run a single assertion. Returns list of error messages (empty if pass)."""
    import tools

    errors: list[str] = []

    try:
        if mode == "smoke":
            pass  # Already passed by getting here

        elif mode == "sanity":
            if not tools.sanity_check(
                image,
                min_size=kwargs.get("min_size", (10, 10)),
                max_blank_ratio=kwargs.get("max_blank_ratio", 0.99),
            ):
                errors.append("sanity_check failed: image blank or too small")

        elif mode in ("pixel", "fingerprint", "diff", "region"):
            ref_path = REFERENCES_DIR / kwargs["reference"]
            if not ref_path.exists():
                errors.append(f"Reference not found: {ref_path}")
            else:
                ref_img = Image.open(ref_path).convert("RGBA")
                if image.mode != "RGBA":
                    image = image.convert("RGBA")

                if mode == "pixel":
                    if not tools.pixel_match(
                        image, ref_img, tolerance=kwargs.get("tolerance", 0)
                    ):
                        errors.append("pixel_match failed")
                elif mode == "fingerprint":
                    if not tools.fingerprint_match(
                        image,
                        ref_img,
                        hash_size=kwargs.get("hash_size", 8),
                        max_diff_bits=kwargs.get("max_diff_bits", 5),
                    ):
                        errors.append("fingerprint_match failed")
                elif mode == "region":
                    bbox = kwargs["bbox"]
                    cropped = tools.crop_region(image, bbox)
                    ref_cropped = tools.crop_region(ref_img, bbox)
                    if not tools.fingerprint_match(cropped, ref_cropped):
                        errors.append("region fingerprint_match failed")
                elif mode == "diff":
                    out = kwargs.get("out_path") or str(
                        IMAGES_DIR / f"diff_{test_name}.png"
                    )
                    if not tools.diff_image(image, ref_img, out):
                        errors.append(f"diff failed; saved to {out}")

        elif mode == "judge":
            if not os.environ.get("OPENAI_API_KEY"):
                errors.append("OPENAI_API_KEY not set; skipping judge")
            else:
                tools.judge(
                    image,
                    elements=kwargs["elements"],
                    focus=kwargs["focus"],
                    min_score=kwargs.get("min_score", 7),
                    model=kwargs.get("model", "gpt-4o"),
                    strict_elements=kwargs.get("strict_elements", True),
                )

    except AssertionError as e:
        errors.append(str(e))
    except Exception as e:
        errors.append(f"{type(e).__name__}: {e}")

    return errors


def _run_test(
    fn: Callable,
    test_name: str,
    collect_errors: bool,
    update_refs: bool,
) -> tuple[bool, list[str]]:
    """Run a single test. Returns (passed, list of error messages)."""
    # Unit tests: no plot, just run and check
    if getattr(fn, _UNIT_ATTR, False):
        return _run_unit_test(fn, test_name)

    assertions = getattr(fn, _ASSERTIONS_ATTR, None)
    if not assertions:
        return False, ["No assertions registered"]

    all_errors: list[str] = []

    # Handle idempotent and stability: run function multiple times
    run_count = 1
    for mode, _ in assertions:
        if mode == "idempotent":
            run_count = 2
            break
        if mode == "stability":
            run_count = _.get("runs", 3)
            break

    plots: list[Any] = []
    for i in range(run_count):
        try:
            with _suppress_prints():
                plot = fn()
            if plot is None:
                return False, ["Test returned None"]
            plots.append(plot)
        except Exception as e:
            return False, [f"Plot generation failed: {type(e).__name__}: {e}"]

    # For idempotent/stability: compare all outputs
    if run_count > 1:
        import tools
        img_paths = []
        for i, plot in enumerate(plots):
            path = IMAGES_DIR / "actual" / f"{test_name}_run{i}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            plot.save(str(path))
            img_paths.append(path)
        imgs = [Image.open(p).convert("RGBA") for p in img_paths]
        for i in range(1, len(imgs)):
            if not tools.pixel_match(imgs[0], imgs[i]):
                all_errors.append(
                    f"Run 0 and run {i} differ (idempotent/stability failed)"
                )
                if not collect_errors:
                    return False, all_errors
        if all_errors:
            return False, all_errors
        # Use first image for remaining assertions
        image = imgs[0]
        image_path = img_paths[0]
    else:
        # Single run: save and load
        plot = plots[0]
        image_path = IMAGES_DIR / "actual" / f"{test_name}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        plot.save(str(image_path))
        if update_refs:
            # Use first reference from assertions, or test_name.png
            ref_name = None
            for mode, kwargs in assertions:
                if mode in ("pixel", "fingerprint", "diff", "region") and "reference" in kwargs:
                    ref_name = kwargs["reference"]
                    break
            ref_name = ref_name or f"{test_name}.png"
            ref_path = REFERENCES_DIR / ref_name
            plot.save(str(ref_path))
            return True, []
        image = Image.open(image_path).convert("RGBA")

    # Run each assertion (skip idempotent/stability, already done)
    for mode, kwargs in assertions:
        if mode in ("idempotent", "stability"):
            continue
        errs = _run_assertion(
            mode, kwargs, image, image_path, test_name, collect_errors
        )
        all_errors.extend(errs)
        if errs and not collect_errors:
            return False, all_errors

    return len(all_errors) == 0, all_errors


class _SuppressOutput:
    """Suppress stdout and stderr during test execution."""

    def __enter__(self):
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        self._devnull = open(os.devnull, "w")
        sys.stdout = self._devnull
        sys.stderr = self._devnull
        return self

    def __exit__(self, *args):
        self._devnull.close()
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr


def _suppress_prints():
    return _SuppressOutput()


def discover_tests(cases_dir: Path | None = None) -> dict[str, Callable]:
    """Discover test functions from cases directory."""
    cases_dir = cases_dir or _TESTS_DIR / "cases"
    tests: dict[str, Callable] = {}

    if not cases_dir.exists():
        return tests

    cases_dir = cases_dir.resolve()
    if str(cases_dir) not in sys.path:
        sys.path.insert(0, str(cases_dir.parent))

    for path in sorted(cases_dir.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in dir(mod):
            obj = getattr(mod, name)
            if callable(obj) and (hasattr(obj, _ASSERTIONS_ATTR) or getattr(obj, _UNIT_ATTR, False)):
                test_name = name
                tests[test_name] = obj

    return tests


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kaxe regression test runner",
        epilog="Examples: python tests/runner.py  |  python tests/runner.py --test test_zoom_inset  |  python tests/runner.py test_zoom_connector_right_right",
    )
    parser.add_argument("test_name", nargs="?", type=str, help="Run only this test (e.g. test_zoom_inset)")
    parser.add_argument("--test", "-t", type=str, dest="test_flag", help="Run only this test (alternative to positional)")
    parser.add_argument("--collect", action="store_true", help="Report all failures, don't fail fast")
    parser.add_argument("--update-refs", action="store_true", help="Copy actuals to reference dir")
    parser.add_argument("--cases-dir", type=Path, default=None, help="Path to test cases directory")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests (no plot generation)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show kaxe/log output")
    args = parser.parse_args()

    # Support both positional and --test
    args.test = args.test_name or args.test_flag

    # Suppress kaxe progress bars, debug output, and logging (unless verbose)
    import kaxe
    if not args.verbose:
        kaxe.setSetting(removeInfo=True)
        logging.getLogger().setLevel(logging.CRITICAL)

    tests = discover_tests(args.cases_dir)
    if not tests:
        print("No tests found. Add test cases to tests/cases/")
        sys.exit(0)

    if args.unit:
        tests = {n: fn for n, fn in tests.items() if getattr(fn, _UNIT_ATTR, False)}
        if not tests:
            print("No unit tests found.")
            sys.exit(0)
    if args.test:
        if args.test not in tests:
            print(f"Test not found: {args.test}")
            print(f"Available: {', '.join(sorted(tests.keys()))}")
            sys.exit(1)
        tests = {args.test: tests[args.test]}

    passed = 0
    failed = 0
    for name, fn in tests.items():
        ok, errs = _run_test(fn, name, args.collect, args.update_refs)
        if ok:
            passed += 1
            print(f"\033[92mPASS\033[0m {name}")
        else:
            failed += 1
            print(f"\033[91mFAIL\033[0m {name}")
            for e in errs:
                print(f"  {e}")

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

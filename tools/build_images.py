from __future__ import annotations

import io
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow não está instalado. Rode: python -m pip install pillow"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
OUT_IMAGES = ROOT / "assets" / "images"
OUT_ICONS = ROOT / "assets" / "icons"


@dataclass(frozen=True)
class ImageJob:
    url: str
    out_dir: Path
    base_name: str  # sem extensão
    widths: tuple[int, ...]
    format: str = "webp"  # webp|png
    quality: int = 78


def download_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; image-downloader/1.0)"
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def save_original(job: ImageJob, blob: bytes) -> Path:
    job.out_dir.mkdir(parents=True, exist_ok=True)

    # Mantém uma cópia do original (útil p/ auditoria e reprocesso)
    original_ext = job.url.split("?")[0].split("#")[0].split(".")[-1].lower()
    original_path = job.out_dir / f"{job.base_name}.orig.{original_ext}"
    original_path.write_bytes(blob)
    return original_path


def encode_webp(img: Image.Image, out_path: Path, quality: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # WebP com compressão boa + sem metadados.
    img.save(
        out_path,
        format="WEBP",
        quality=quality,
        method=6,
        optimize=True,
    )


def resize_to_width(img: Image.Image, width: int) -> Image.Image:
    if img.width == width:
        return img

    height = max(1, round(img.height * (width / img.width)))
    return img.resize((width, height), resample=Image.Resampling.LANCZOS)


def process_job(job: ImageJob) -> None:
    print(f"Baixando: {job.url}")
    blob = download_bytes(job.url)
    save_original(job, blob)

    if job.format == "png":
        out_path = job.out_dir / f"{job.base_name}.png"
        out_path.write_bytes(blob)
        print(f"  -> {out_path.relative_to(ROOT)}")
        return

    # WebP pipeline
    with Image.open(io.BytesIO(blob)) as im:
        im.load()

        # Normaliza modo pra evitar erros (ex: P)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")

        for w in job.widths:
            resized = resize_to_width(im, w)
            out_path = job.out_dir / f"{job.base_name}-{w}.webp"
            encode_webp(resized, out_path, quality=job.quality)
            print(f"  -> {out_path.relative_to(ROOT)}")


def main() -> int:
    jobs: list[ImageJob] = [
        # HERO / BACKGROUNDS
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/10/Imagem.webp",
            out_dir=OUT_IMAGES,
            base_name="hero",
            widths=(640, 960, 1280, 1600, 1920),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2024/05/studio_voll_campinas_pilates_5.webp",
            out_dir=OUT_IMAGES,
            base_name="target-left",
            widths=(480, 640, 800),
            quality=78,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2024/05/studio_voll_campinas_pilates_6.webp",
            out_dir=OUT_IMAGES,
            base_name="security-bg",
            widths=(640, 960, 1200),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/mapa.webp",
            out_dir=OUT_IMAGES,
            base_name="mapa",
            widths=(640, 960, 1200),
            quality=76,
        ),

        # LOGOS
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/10/VOLL-PILATES-Logotipo-Institucional-Branco-01.webp",
            out_dir=OUT_IMAGES,
            base_name="logo-voll-branco",
            widths=(150, 300),
            quality=82,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/Associacao-Brasileira-de-Franchising-e1758288849748.webp",
            out_dir=OUT_IMAGES,
            base_name="logo-abf",
            widths=(200, 400),
            quality=82,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/02/voll-pilates.png",
            out_dir=OUT_IMAGES,
            base_name="logo-voll-grupo",
            widths=(200, 400),
            quality=82,
        ),

        # TESTIMONIALS
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/maxresdefault.webp",
            out_dir=OUT_IMAGES,
            base_name="testi-1",
            widths=(480, 768, 1024, 1200),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/depoimento2.webp",
            out_dir=OUT_IMAGES,
            base_name="testi-2",
            widths=(480, 768, 1024, 1200),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/depoimento3.webp",
            out_dir=OUT_IMAGES,
            base_name="testi-3",
            widths=(480, 768, 1024, 1200),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/depoimento4.webp",
            out_dir=OUT_IMAGES,
            base_name="testi-4",
            widths=(480, 768, 1024, 1200),
            quality=76,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2025/09/depoimento5.webp",
            out_dir=OUT_IMAGES,
            base_name="testi-5",
            widths=(480, 768, 1024, 1200),
            quality=76,
        ),

        # ICONS (pequenos)
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-f%C3%A1cil-100.png",
            out_dir=OUT_ICONS,
            base_name="investimento-facilitado",
            widths=(64, 128),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-presente-100.png",
            out_dir=OUT_ICONS,
            base_name="equipamentos",
            widths=(64, 128),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-gr%C3%A1fico-100.png",
            out_dir=OUT_ICONS,
            base_name="escalabilidade",
            widths=(64, 128),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-professor-100.png",
            out_dir=OUT_ICONS,
            base_name="formacao-tecnica",
            widths=(64, 128),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-undefined-100.png",
            out_dir=OUT_ICONS,
            base_name="direitos-marca",
            widths=(64, 128),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-sacar-dinheiro-100.png",
            out_dir=OUT_ICONS,
            base_name="fature-muito",
            widths=(64, 128),
            quality=80,
        ),

        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-restitui%C3%A7%C3%A3o-2-100.png",
            out_dir=OUT_ICONS,
            base_name="payback",
            widths=(48, 96),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-undefined-1001.png",
            out_dir=OUT_ICONS,
            base_name="breakeven",
            widths=(48, 96),
            quality=80,
        ),
        ImageJob(
            url="https://franquiadepilates.com.br/wp-content/uploads/2019/11/icons8-comprar-moedas-100.png",
            out_dir=OUT_ICONS,
            base_name="royalties",
            widths=(48, 96),
            quality=80,
        ),
    ]

    failures = 0
    for job in jobs:
        try:
            process_job(job)
        except Exception as exc:
            failures += 1
            print(f"ERRO em {job.url}: {exc}", file=sys.stderr)

    if failures:
        print(f"Concluído com {failures} falha(s).", file=sys.stderr)
        return 2

    print("Concluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

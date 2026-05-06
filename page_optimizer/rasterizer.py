from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


def rasterize_pdf(pdf_path: str | Path, output_dir: str | Path, scale: float = 2.0) -> list[str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(pdf_path))
    paths: list[str] = []
    stem = Path(pdf_path).stem
    for index in range(len(doc)):
        page = doc[index]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        path = output / f"{stem}_page_{index + 1:03d}.png"
        image.save(path)
        paths.append(str(path))
        page.close()
    doc.close()
    return paths

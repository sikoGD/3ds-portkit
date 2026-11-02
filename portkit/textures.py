"""Offline PNG preparation with reversible manifests; never packages source assets."""
import hashlib
import json
from pathlib import Path


def _pow2(n):
    return 1 << (n - 1).bit_length()


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare_texture(input_path: Path, output_path: Path, max_edge=1024, pad_power2=True,
                    max_rgba_bytes=4 * 1024 * 1024, manifest_path=None):
    if not isinstance(max_edge, int) or max_edge < 1 or max_edge > 1024:
        raise ValueError('max_edge must be from 1 to 1024')
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('Pillow required: python -m pip install Pillow') from exc
    src, dest = Path(input_path).resolve(), Path(output_path).resolve()
    if not src.is_file() or src.suffix.lower() != '.png' or dest.suffix.lower() != '.png':
        raise ValueError('Source and output must be PNG files')
    if dest == src or dest.exists():
        raise ValueError('Refusing to overwrite input or an existing output')
    with Image.open(src) as img:
        rgba = img.convert('RGBA')
        before = rgba.size
        if max(rgba.size) > max_edge:
            scale = max_edge / max(rgba.size)
            dims = (max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale)))
            rgba = rgba.resize(dims, resample=Image.Resampling.NEAREST)
        image_size = rgba.size
        if pad_power2:
            canvas = Image.new('RGBA', (_pow2(rgba.width), _pow2(rgba.height)))
            canvas.paste(rgba, (0, 0))
            rgba = canvas
        estimated_bytes = rgba.width * rgba.height * 4
        if estimated_bytes > max_rgba_bytes:
            raise ValueError(f'RGBA estimate {estimated_bytes} exceeds budget {max_rgba_bytes}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(dest, 'PNG')
    report = {'source_dimensions': before, 'content_dimensions': image_size,
            'output_dimensions': rgba.size, 'output': str(dest),
            'estimated_rgba8_bytes': estimated_bytes, 'max_rgba8_bytes': max_rgba_bytes,
            'note': 'Host PNG only. tex3ds conversion is a separate, user-run build step.'}
    if manifest_path:
        manifest = Path(manifest_path)
        if manifest.exists():
            raise ValueError('Refusing to overwrite an existing manifest')
        payload = {"format": "3ds-portkit-texture-manifest-v1", "source": str(src),
                   "source_sha256": _sha256(src), "prepared": str(dest),
                   "prepared_sha256": _sha256(dest), "preparation": report,
                   "tex3ds_example": f'tex3ds -o "{dest.with_suffix(".t3x")}" "{dest}"',
                   "reversal": "Delete the prepared PNG and manifest; the source PNG is unchanged."}
        manifest.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        report['manifest'] = str(manifest)
    return report

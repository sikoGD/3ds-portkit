"""Offline inventory of RPG Maker MV/MZ projects and image assets.

Does not extract, modify, upload or redistribute user game data.
"""
import json
import re
import struct
from collections import Counter
from pathlib import Path

_MAX_JSON_BYTES = 32 * 1024 * 1024
_MAP_NAME = re.compile(r'^Map\d{3,4}\.json$', re.IGNORECASE)


def _read_json(path: Path):
    if path.stat().st_size > _MAX_JSON_BYTES:
        raise ValueError(f'{path.name} exceeds the 32 MiB safe input limit')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def analyze_rpgmaker(root: Path) -> dict:
    """Collect structural numbers; no game strings or asset content in output."""
    root = Path(root).resolve()
    data = root / 'data'
    if not data.is_dir():
        raise ValueError('Expected a project directory containing data/Map*.json')
    result = {'format': 'rpg-maker-mv-mz', 'map_count': 0,
              'event_count': 0, 'event_page_count': 0,
              'command_count': 0, 'command_codes': {},
              'script_command_count': 0, 'maps_with_parse_errors': [],
              'plugin_file_count': 0, 'resource_inventory': {}}
    codes = Counter()
    for path in sorted(data.iterdir()):
        if not path.is_file() or not _MAP_NAME.fullmatch(path.name):
            continue
        try:
            data_obj = _read_json(path)
            if not isinstance(data_obj, dict):
                raise ValueError('Map root must be an object')
            events = data_obj.get('events', [])
            if not isinstance(events, list):
                raise ValueError('Map events must be a list')
            result['map_count'] += 1
            for ev in events:
                if not isinstance(ev, dict):
                    continue
                result['event_count'] += 1
                for page in ev.get('pages', []):
                    if not isinstance(page, dict):
                        continue
                    result['event_page_count'] += 1
                    for command in page.get('list', []):
                        if isinstance(command, dict) and isinstance(command.get('code'), int):
                            codes[command['code']] += 1
                            result['command_count'] += 1
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            result['maps_with_parse_errors'].append({'file': path.name, 'error_type': type(exc).__name__})
    result['command_codes'] = {str(k): v for k, v in sorted(codes.items())}
    # 355/655 are the RPG Maker MV script command and its continuation.
    result['script_command_count'] = codes[355] + codes[655]
    plugins = root / 'js' / 'plugins'
    if plugins.is_dir():
        result['plugin_file_count'] = sum(1 for x in plugins.glob('*.js') if x.is_file())
    for folder in ('img', 'audio', 'movies'):
        directory = root / folder
        by_extension = Counter()
        if directory.is_dir():
            for path in directory.rglob('*'):
                if path.is_file() and not path.is_symlink():
                    by_extension[path.suffix.lower() or '(none)'] += 1
        result['resource_inventory'][folder] = dict(sorted(by_extension.items()))
    return result


def inspect_png(path: Path) -> dict:
    """Read PNG IHDR only, without decoding or exposing proprietary pixels."""
    with Path(path).open('rb') as fp:
        header = fp.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('Not a valid PNG header')
    width, height = struct.unpack('>II', header[16:24])
    if not (0 < width <= 65535 and 0 < height <= 65535):
        raise ValueError('Unsupported PNG dimensions')
    return {'width': width, 'height': height, 'rgba8_uncompressed_bytes': width * height * 4,
            'bgr8_uncompressed_bytes': width * height * 3, 'exceeds_1024_dimension': max(width, height) > 1024}


def inspect_assets(root: Path) -> dict:
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Asset directory not found')
    count, total, oversized, problems = 0, 0, 0, []
    by_extension = Counter()
    for path in root.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        count += 1
        by_extension[path.suffix.lower() or '(none)'] += 1
        total += path.stat().st_size
        if path.suffix.lower() == '.png':
            try:
                if inspect_png(path)['exceeds_1024_dimension']:
                    oversized += 1
            except (ValueError, OSError):
                problems.append(str(path.relative_to(root)))
    return {'file_count': count, 'source_bytes': total,
            'png_above_1024_dimension': oversized, 'invalid_png_paths': problems,
            'extensions': dict(sorted(by_extension.items()))}

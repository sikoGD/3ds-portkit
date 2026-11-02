"""Command-line entrypoint."""
import argparse
import json
import re
import shutil
from pathlib import Path
from .analyze import analyze_rpgmaker, inspect_assets
from .profile import analyze_frames
from .textures import prepare_texture

TEMPLATE = Path(__file__).resolve().parent.parent / 'templates' / 'native-demo'


def _write_report(report, dest):
    contents = json.dumps(report, indent=2, ensure_ascii=False)
    if dest:
        Path(dest).write_text(contents + '\n', encoding='utf-8')
        print('Report saved:', dest)
    else:
        print(contents)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='3ds-portkit', description='Offline 3DS port development tools')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inspect-rpgmv', help='Analyze a locally owned RPG Maker MV/MZ data directory')
    p.add_argument('project'); p.add_argument('--output')
    p = sub.add_parser('inspect-assets', help='Inventory images and estimate basic resource budgets')
    p.add_argument('folder'); p.add_argument('--output')
    p = sub.add_parser('profile', help='Analyze scene frame-time CSV')
    p.add_argument('csv'); p.add_argument('--fps', type=float, default=30); p.add_argument('--output')
    p = sub.add_parser('prepare-texture', help='Offline PNG resize/pad (optional Pillow)')
    p.add_argument('source'); p.add_argument('destination'); p.add_argument('--max-edge', type=int, default=1024)
    p.add_argument('--no-pad', action='store_true'); p.add_argument('--max-rgba-bytes', type=int, default=4 * 1024 * 1024)
    p.add_argument('--manifest', help='new JSON manifest; never overwrites')
    p = sub.add_parser('init', help='Create an original libctru development template')
    p.add_argument('destination'); p.add_argument('--name', default='PortKit Demo')
    args = parser.parse_args(argv)
    if args.command == 'inspect-rpgmv':
        _write_report(analyze_rpgmaker(Path(args.project)), args.output)
    elif args.command == 'inspect-assets':
        _write_report(inspect_assets(Path(args.folder)), args.output)
    elif args.command == 'profile':
        if args.fps <= 0:
            parser.error('--fps must be positive')
        _write_report(analyze_frames(Path(args.csv), 1000 / args.fps), args.output)
    elif args.command == 'prepare-texture':
        _write_report(prepare_texture(Path(args.source), Path(args.destination),
                                      max_edge=args.max_edge, pad_power2=not args.no_pad,
                                      max_rgba_bytes=args.max_rgba_bytes, manifest_path=args.manifest), None)
    elif args.command == 'init':
        destination = Path(args.destination)
        if destination.exists():
            parser.error('destination already exists (refusing to overwrite)')
        if not re.fullmatch(r'[A-Za-z0-9 _.-]{1,64}', args.name):
            parser.error('name must be 1-64 letters/numbers/spaces/._-')
        shutil.copytree(TEMPLATE, destination)
        path = destination / 'Makefile'
        path.write_text(path.read_text(encoding='utf-8').replace('PORTKIT_DEMO', args.name), encoding='utf-8')
        print('Created', destination, '- install devkitPro 3ds-dev, then run make')


if __name__ == '__main__':
    main()

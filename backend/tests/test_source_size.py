from pathlib import Path


def test_handwritten_sources_are_under_eighty_lines():
    root = Path(__file__).resolve().parents[2]
    ignored = {'.venv', 'node_modules', '.runtime', 'dist', '__pycache__', '.git'}
    extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html', '.sql'}
    oversized = []
    for path in root.rglob('*'):
        if path.suffix not in extensions or ignored.intersection(path.parts) or not path.is_file():
            continue
        lines = len(path.read_text().splitlines())
        if lines >= 80:
            oversized.append(f'{path.relative_to(root)}: {lines}')
    assert not oversized, '\n'.join(oversized)

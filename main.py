from __future__ import annotations

import html
from pathlib import Path
from typing import Dict, List, Tuple

# =========================
# Configuration
# =========================
# Put your 12 folders here. Each folder should look like:
#   chinese__LXC_arctic_a0049/
#       source.wav
#       to_hindi.wav
#       to_spanish.wav
#       to_vietnamese.wav
# If your folders are directly under the project root, change this to Path('.')
TASK1_BASE_DIR = Path("task1_samples")
OUTPUT_HTML = Path("index.html")

ACCENT_ORDER = [
    "chinese",
    "hindi",
    "spanish",
    "vietnamese",
    "indian",
    "south_african",
    "southafrican",
]

ACCENT_PRETTY: Dict[str, str] = {
    "chinese": "Chinese",
    "hindi": "Hindi",
    "indian": "Indian",
    "spanish": "Spanish",
    "vietnamese": "Vietnamese",
    "south_african": "South African",
    "southafrican": "South African",
    "sa": "South African",
}


def normalize_accent(name: str) -> str:
    s = name.strip().lower().replace("-", "_").replace(" ", "_")
    if s in {"southafrican", "south_african", "south-african", "sa"}:
        return "south_african"
    return s


# folder examples:
#   chinese__LXC_arctic_a0049
#   hindi__ASI_arctic_a0277
#   spanish__ERMS_arctic_b0272
# fallback: take the first token before '__' or '_'
def get_source_accent_from_folder(folder_name: str) -> str:
    if "__" in folder_name:
        raw = folder_name.split("__", 1)[0]
    else:
        raw = folder_name.split("_", 1)[0]
    return normalize_accent(raw)


# file examples:
#   to_hindi.wav
#   to_spanish.wav
#   to_vietnamese.wav
#   to_south_african.wav
def get_target_accent_from_filename(file_name: str) -> str | None:
    stem = Path(file_name).stem.lower()
    if not stem.startswith("to_"):
        return None
    raw = stem[3:]
    return normalize_accent(raw)


# Use a stable order if possible; unknown accents go to the end alphabetically.
def accent_sort_key(accent: str) -> Tuple[int, str]:
    if accent in ACCENT_ORDER:
        return (ACCENT_ORDER.index(accent), accent)
    return (999, accent)


# Build rows from disk.
def collect_task1_samples(base_dir: Path) -> List[dict]:
    if not base_dir.exists():
        raise FileNotFoundError(
            f"Task 1 base directory not found: {base_dir.resolve()}\n"
            f"Please set TASK1_BASE_DIR in main.py correctly."
        )

    sample_dirs = [
        p for p in sorted(base_dir.iterdir())
        if p.is_dir() and (p / "source.wav").exists()
    ]

    rows: List[dict] = []
    for folder in sample_dirs:
        source_accent = get_source_accent_from_folder(folder.name)
        target_items = []
        for wav in sorted(folder.glob("to_*.wav")):
            target_accent = get_target_accent_from_filename(wav.name)
            if target_accent is None:
                continue
            if target_accent == source_accent:
                continue
            target_items.append(
                {
                    "accent": target_accent,
                    "pretty": ACCENT_PRETTY.get(target_accent, target_accent.replace("_", " ").title()),
                    "rel_path": wav.as_posix(),
                }
            )

        target_items.sort(key=lambda x: accent_sort_key(x["accent"]))

        rows.append(
            {
                "folder_name": folder.name,
                "source_accent": source_accent,
                "source_pretty": ACCENT_PRETTY.get(source_accent, source_accent.replace("_", " ").title()),
                "source_rel_path": (folder / "source.wav").as_posix(),
                "targets": target_items,
            }
        )

    return rows


def render_task1_block(rows: List[dict]) -> str:
    blocks: List[str] = []

    for idx, row in enumerate(rows, start=1):
        source_pretty = html.escape(row["source_pretty"])
        folder_name = html.escape(row["folder_name"])

        # exactly the remaining accents for this sample
        # if there are fewer than 3, fill with placeholders so layout stays stable
        targets = row["targets"][:3]
        while len(targets) < 3:
            targets.append(
                {
                    "accent": "",
                    "pretty": "N/A",
                    "rel_path": "",
                }
            )

        header_html = "\n".join(
            f'<th width="25%">{html.escape(t["pretty"])}</th>' for t in targets
        )

        cell_html_parts: List[str] = []
        for t in targets:
            if t["rel_path"]:
                pretty = html.escape(t["pretty"])
                rel_path = html.escape(t["rel_path"])
                cell_html_parts.append(
                    f'''<td>
                            <span class="tag tag-res">Ours</span><br>
                            <audio controls src="{rel_path}"></audio>
                            <div class="desc">Converted to {pretty}</div>
                        </td>'''
                )
            else:
                cell_html_parts.append(
                    '''<td>
                            <span class="tag tag-empty">Missing</span><br>
                            <div class="desc">Audio not found</div>
                        </td>'''
                )
        cell_html = "\n".join(cell_html_parts)

        blocks.append(
            f'''
            <div class="sample-subblock">
                <div class="sample-subtitle">Sample {idx}: {folder_name}</div>
                <table>
                    <thead>
                        <tr>
                            <th width="25%">Source ({source_pretty})</th>
                            {header_html}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <span class="tag tag-src">Source</span><br>
                                <audio controls src="{html.escape(row["source_rel_path"])}"></audio>
                                <div class="desc">{source_pretty}</div>
                            </td>
                            {cell_html}
                        </tr>
                    </tbody>
                </table>
            </div>
            '''
        )

    return "\n".join(blocks)


def build_html(task1_html: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Conversion Demo Page</title>
    <link href="https://fonts.googleapis.com/css?family=Google+Sans|Noto+Sans|Castoro" rel="stylesheet">
    <style>
        body {{
            font-family: 'Noto Sans', sans-serif;
            max-width: 1180px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background-color: #fff;
        }}

        header {{ text-align: center; margin-bottom: 50px; }}
        h1 {{ font-family: 'Google Sans', sans-serif; font-size: 2.5rem; margin-bottom: 10px; }}
        h2 {{ font-size: 1.5rem; color: #555; font-weight: normal; margin-top: 0; }}
        .authors {{ color: #007bff; margin-top: 20px; font-size: 1.1rem; }}
        .affiliations {{ color: #666; font-size: 0.9rem; margin-top: 5px; }}

        section {{ margin-bottom: 60px; }}
        h3 {{
            font-family: 'Google Sans', sans-serif;
            font-size: 1.8rem;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .model-figure {{
            text-align: center;
            margin: 30px 0;
        }}
        .model-figure img {{
            max-width: 90%;
            height: auto;
            border: 1px solid #eee;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        .caption {{
            margin-top: 10px;
            color: #666;
            font-style: italic;
            font-size: 0.95rem;
        }}

        .task-title {{
            font-size: 1.3rem;
            color: #444;
            margin-top: 40px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 10px;
        }}
        .sample-subblock {{
            margin-bottom: 18px;
        }}
        .sample-subtitle {{
            font-size: 1rem;
            font-weight: 600;
            color: #4a4a4a;
            margin: 6px 0 8px 2px;
        }}
        p.note {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.95rem;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            table-layout: fixed;
        }}
        th, td {{
            padding: 15px 10px;
            text-align: center;
            border-bottom: 1px solid #eee;
            vertical-align: middle;
        }}
        th {{ background-color: #f8f9fa; font-weight: 600; color: #444; }}
        tr:hover {{ background-color: #fafafa; }}

        audio {{ width: 200px; max-width: 100%; height: 35px; }}
        .desc {{ font-size: 0.82rem; color: #777; margin-top: 4px; }}
        .tag {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 6px;
        }}
        .tag-src {{ background-color: #e3f2fd; color: #0d47a1; }}
        .tag-ref {{ background-color: #f3e5f5; color: #4a148c; }}
        .tag-res {{ background-color: #e8f5e9; color: #1b5e20; }}
        .tag-empty {{ background-color: #eeeeee; color: #616161; }}

        @media (max-width: 900px) {{
            body {{ padding: 24px 12px; }}
            th, td {{ padding: 10px 6px; }}
            audio {{ width: 150px; }}
        }}
    </style>
</head>
<body>

    <header>
        <h1>SPACE: Subspace Projected Attribute Control & Editing</h1>
        <h2>Zero-Shot Voice Attribute Editing Demo</h2>

        <div class="authors">
            <span class="author">Anonymous Authors</span>
        </div>
        <div class="affiliations">Under Review</div>
    </header>

    <section id="abstract">
        <h3>Abstract</h3>
        <p>
            To do.
        </p>
    </section>

    <section id="model">
        <h3>Model Architecture</h3>
        <p>
            The overview of our proposed framework.
        </p>

        <div class="model-figure">
            <img src="model.png" alt="Model Architecture Diagram">
            <div class="caption">Figure 1: The proposed architecture for attribute editing.</div>
        </div>
    </section>

    <section id="demos">
        <h3>Audio Samples</h3>
        <p class="note">
            Below are the conversion results.
            <strong>Task 1</strong> demonstrates accent conversion, and
            <strong>Task 2</strong> demonstrates gender attribute editing.
        </p>

        <div class="task-block">
            <div class="task-title">Task 1: Accent Conversion</div>
            {task1_html}
        </div>

        <div class="task-block">
            <div class="task-title">Task 2: Gender Conversion</div>

            <table>
                <thead>
                    <tr>
                        <th width="33%">Source (Input)</th>
                        <th width="33%">Target Gender (Reference)</th>
                        <th width="33%">Converted Result (Ours)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <span class="tag tag-src">Male</span><br>
                            <audio controls src="MToF/p226_014.wav"></audio>
                        </td>
                        <td>
                            <span class="tag tag-ref">Female Ref</span><br>
                            <audio controls src="FToM/p226_014.wav"></audio>
                        </td>
                        <td>
                            <span class="tag tag-res">Result</span><br>
                            <audio controls src="MToF/p226_p226_014_female.wav"></audio>
                            <div class="desc">Converted to Female</div>
                        </td>
                    </tr>

                    <tr>
                        <td>
                            <span class="tag tag-src">Female</span><br>
                            <audio controls src="FToM/p226_014.wav"></audio>
                        </td>
                        <td>
                            <span class="tag tag-ref">Male Ref</span><br>
                            <audio controls src="MToF/p226_014.wav"></audio>
                        </td>
                        <td>
                            <span class="tag tag-res">Result</span><br>
                            <audio controls src="FToM/p264_p264_014_F.wav"></audio>
                            <div class="desc">Converted to Male</div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

    </section>

</body>
</html>
'''


def main() -> None:
    rows = collect_task1_samples(TASK1_BASE_DIR)
    task1_html = render_task1_block(rows)
    html_text = build_html(task1_html)
    OUTPUT_HTML.write_text(html_text, encoding="utf-8")
    print(f"[OK] Wrote {OUTPUT_HTML.resolve()}")
    print(f"[OK] Task 1 rows: {len(rows)}")


if __name__ == "__main__":
    main()

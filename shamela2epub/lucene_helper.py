from __future__ import annotations
import json
import os
import subprocess
import tempfile
from pathlib import Path

MVN = "mvn.cmd" if os.name == "nt" else "mvn"


def _helper_dir(project_root: Path) -> Path:
    return Path(project_root) / "java-helper"


def ensure_helper(project_root: Path) -> None:
    helper = _helper_dir(project_root)
    if not helper.exists():
        raise FileNotFoundError(f"Java helper folder not found: {helper}")
    subprocess.run([MVN, "-q", "compile"], cwd=helper, check=True)


def dump_index(project_root: Path, index: Path, kind: str, book_id: str | None = None) -> dict:
    """Dump a Shamela Lucene index through the Java helper.

    The helper writes JSON to a UTF-8 file instead of stdout. This avoids Windows
    console encoding problems that turn Arabic into question marks.
    """
    ensure_helper(project_root)
    helper = _helper_dir(project_root)
    index = Path(index)
    if not index.exists():
        raise FileNotFoundError(f"Lucene index not found: {index}")

    with tempfile.TemporaryDirectory(prefix="shamela2epub_") as tmp:
        out_json = Path(tmp) / f"{kind}.json"
        dump_args = f'"{index}" {kind} "{out_json}"'
        if book_id:
            dump_args += f" {book_id}"

        args = [
            MVN,
            "-q",
            "exec:java",
            "-Dexec.mainClass=org.shamela2epub.helper.DumpIndex",
            f"-Dexec.args={dump_args}",
            "-Dexec.jvmArgs=-Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8",
        ]
        p = subprocess.run(
            args,
            cwd=helper,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if p.returncode != 0:
            raise RuntimeError(p.stderr or p.stdout)
        if not out_json.exists():
            raise RuntimeError(f"Lucene helper did not create output file: {out_json}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
        return json.loads(out_json.read_text(encoding="utf-8"))

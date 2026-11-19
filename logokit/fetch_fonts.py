"""Fetch the open-source fonts of Digonto Logo from the Google Fonts collection (https://github.com/google/fonts).

The list of families, and the exact version of the collection, are in data/fonts.json. Only the font files that
list names are downloaded (a few hundred MB, not the whole collection). They go to data/gf/, with one licence file
that holds every family's copyright line and the licence texts.

    python logokit/fetch_fonts.py            (run by the build before packaging Digonto Logo)

Digonto Logo works without them too: it then offers the 40 fonts that are part of its own repository.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DEST = os.path.join(DATA, "gf")
REPO = "https://github.com/google/fonts"


def git(*args, cwd=None):
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    subprocess.run(["git", *args], cwd=cwd, check=True, env=env)


def main():
    with open(os.path.join(DATA, "fonts.json"), encoding="utf-8") as f:
        doc = json.load(f)
    if not isinstance(doc, dict) or "revision" not in doc:
        print("fonts.json has no Google Fonts list - nothing to fetch")
        return 0
    rev, fonts = doc["revision"], doc["fonts"]
    files = []
    for e in fonts:
        g = e.get("gf") or {}
        for k in ("var", "regular", "bold"):
            if g.get(k):
                files.append(f"{g['dir']}/{g[k]}")
    dirs = sorted({e["gf"]["dir"] for e in fonts if e.get("gf")})
    work = tempfile.mkdtemp(prefix="digonto-fonts-")
    try:
        git("init", "-q", work)
        git("remote", "add", "origin", REPO, cwd=work)
        git("config", "core.sparseCheckout", "true", cwd=work)
        esc = lambda p: "/" + p.replace("[", "\\[").replace("]", "\\]")   # noqa: E731 - [wght] is not a pattern
        with open(os.path.join(work, ".git", "info", "sparse-checkout"), "w", encoding="utf-8") as f:
            f.write("\n".join([esc(p) for p in files] + [f"/{d}/OFL.txt" for d in dirs] +
                              [f"/{d}/LICENSE.txt" for d in dirs] + [f"/{d}/UFL.txt" for d in dirs]) + "\n")
        print(f"fetching {len(files)} font files of {len(fonts)} families (google/fonts {rev[:10]}) ...", flush=True)
        for attempt in range(3):
            try:
                git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", rev, cwd=work)
                git("checkout", "-q", "FETCH_HEAD", cwd=work)
                break
            except subprocess.CalledProcessError:
                if attempt == 2:
                    raise
        shutil.rmtree(DEST, ignore_errors=True)
        os.makedirs(DEST)
        n, size, notices = 0, 0, []
        for e in fonts:
            g = e.get("gf")
            if not g:
                continue
            src_dir = os.path.join(work, g["dir"])
            dst_dir = os.path.join(DEST, os.path.basename(g["dir"]))
            os.makedirs(dst_dir, exist_ok=True)
            for k in ("var", "regular", "bold"):
                if g.get(k) and os.path.isfile(os.path.join(src_dir, g[k])):
                    shutil.copy2(os.path.join(src_dir, g[k]), dst_dir)
                    n += 1
                    size += os.path.getsize(os.path.join(src_dir, g[k]))
            for lic in ("OFL.txt", "LICENSE.txt", "UFL.txt"):
                p = os.path.join(src_dir, lic)
                if os.path.isfile(p):
                    with open(p, encoding="utf-8", errors="replace") as f:
                        first = next((ln.strip() for ln in f if ln.strip()), "")
                    if lic == "OFL.txt" and not re.search(r"copyright", first, re.I):
                        first = ""
                    notices.append(f"{e['name']} ({e['license']}): {first}")
                    break
        ofl = next((os.path.join(work, d, "OFL.txt") for d in dirs if os.path.isfile(os.path.join(work, d, "OFL.txt"))), None)
        apache = next((os.path.join(work, d, "LICENSE.txt") for d in dirs if os.path.isfile(os.path.join(work, d, "LICENSE.txt"))), None)
        with open(os.path.join(DEST, "LICENSES.txt"), "w", encoding="utf-8") as out:
            out.write(f"Fonts from the Google Fonts collection ({REPO}, revision {rev}).\n"
                      "Each family is licensed by its authors under the SIL Open Font License 1.1 (OFL) or the Apache\n"
                      "License 2.0, as noted. The fonts are unchanged. Logos made with them may be used for any purpose.\n\n"
                      "== Copyright notices ==\n" + "\n".join(notices) + "\n\n")
            for title, p in (("SIL Open Font License 1.1", ofl), ("Apache License 2.0", apache)):
                if p:
                    with open(p, encoding="utf-8", errors="replace") as f:
                        body = f.read()
                    if title.startswith("SIL"):                     # the licence text, without one family's copyright line
                        i = body.find("This Font Software is licensed")
                        body = body[i:] if i >= 0 else body
                    out.write(f"== {title} ==\n{body}\n\n")
        print(f"{n} files, {size / 1048576:.0f} MB -> {DEST}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

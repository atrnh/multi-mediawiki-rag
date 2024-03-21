from pathlib import Path
from . import embed_mediawiki_dump

for f in Path.cwd().glob("./sources/*.xml"):
    print(f"Processing {f}")
    embed_mediawiki_dump(f)

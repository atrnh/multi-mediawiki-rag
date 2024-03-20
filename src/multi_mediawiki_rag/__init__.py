from langchain_community.document_loaders import MWDumpLoader
from pathlib import Path

# package_dir = Path(path.abspath(path.dirname(__file__)))
# print(package_dir)
# sources_dir = Path.cwd()

# load each file in package_dir / sources
# just do 1 for now as a test
documents = None
for file in Path.cwd().glob("./sources/*"):
    print(file)
    loader = MWDumpLoader(
        file_path=file,
        encoding="utf8",
        namespaces=[
            0
        ],  # Optional list to load only specific namespaces. Loads all namespaces by default.
        skip_redirects=True,  # will skip over pages that just redirect to other pages (or not if False)
        stop_on_error=False,  # will skip over pages that cause parsing errors (or not if False)
    )
    documents = loader.load()
    break

print(f"You have {len(documents)} document(s) in your data ")

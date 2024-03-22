import os
from pathlib import Path

import chromadb
from langchain_community.embeddings import (
    OllamaEmbeddings,
)
from langchain_community.vectorstores import Chroma

from loguru import logger

from .loader import LoggingMWDumpLoader
from .splitter import LoggingSemanticChunker

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", 8000)

chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

# splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
embeddings = OllamaEmbeddings(model="mistral:latest")
splitter = LoggingSemanticChunker(embeddings, breakpoint_threshold_type="percentile")

t_start = os.times()


def get_wiki(file_path: Path):
    logger.debug(f"Loading dump from {file_path}")
    wiki_loader = LoggingMWDumpLoader(
        file_path=file_path,
        encoding="utf8",
        namespaces=[0],
        skip_redirects=True,
        stop_on_error=False,
    )
    docs = wiki_loader.load()
    return docs


def load_and_split_wiki(file_path: Path):
    logger.debug("loading and splitting wiki")
    docs = get_wiki(file_path)
    logger.debug(f"Loaded {docs} documents from {file_path}.")
    s = splitter.split_documents(docs)
    logger.debug(f"Loaded {len(s)} documents from {file_path}.")
    return s


def embed_mediawiki_dump(file_path: Path):
    collection_name = file_path.stem
    # fix this gross shit
    try:
        db = chroma.get_collection(collection_name)
        print(f"{collection_name} already exists and contains {db.count()} documents.")
        if db.count() > 0:
            return db
        print(f"Collection {collection_name} is empty, re-embedding.")
    except Exception as e:
        print(e)
        print(f"Creating {collection_name}, probably b/c it didn't exist.")

    splits = load_and_split_wiki(file_path)

    return Chroma.from_documents(
        splits,
        embeddings,
        client=chroma,
        collection_name=collection_name,
    )

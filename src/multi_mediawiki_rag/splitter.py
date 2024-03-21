from typing import TYPE_CHECKING
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from loguru import logger

if TYPE_CHECKING:
    from typing import Iterable, List


class LoggingSemanticChunker(SemanticChunker):
    def split_documents(self, documents: "Iterable[Document]") -> "List[Document]":
        texts, metadatas = [], []
        for doc in documents:
            logger.debug(f"Start chunking: {doc.metadata.get('source')}")
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
            logger.debug(f"Finished: {doc.metadata.get('source')}")
        return self.create_documents(texts, metadatas=metadatas)

    def create_documents(
        self, texts: "List[str]", metadatas: "List[dict]" = None
    ) -> "List[Document]":
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            logger.debug(f"Splitting text n={len(text)}")
            index = -1
            chunks = self.split_text(text)
            logger.debug("Completed splitting text")
            for chunk in chunks:
                metadata = _metadatas[i].copy()
                if self._add_start_index:
                    index = text.find(chunk, index + 1)
                    metadata["start_index"] = index
                new_doc = Document(page_content=chunk, metadata=metadata)
                logger.debug(f"Created chunk: {new_doc.metadata.get('source')}")
                documents.append(new_doc)
        return documents

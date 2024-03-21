from typing import TYPE_CHECKING

from langchain_community.document_loaders import MWDumpLoader
from loguru import logger

if TYPE_CHECKING:
    from typing import Iterator
    from langchain_core.documents import Document


class LoggingMWDumpLoader(MWDumpLoader):
    def lazy_load(self) -> "Iterator[Document]":
        dump = self._load_dump_file()
        for page in dump.pages:
            if self.skip_redirects and page.redirect:
                continue
            if self.namespaces and page.namespace not in self.namespaces:
                continue
            try:
                yield self._load_single_page_from_dump(page)
                logger.debug(f"Finished loading: {page.title}")
            except Exception as e:
                logger.error("Parsing error: {}".format(e))
                if self.stop_on_error:
                    raise e
                else:
                    continue

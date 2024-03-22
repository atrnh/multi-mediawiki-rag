from typing import TYPE_CHECKING

from langchain_community.document_loaders import MWDumpLoader
from loguru import logger

if TYPE_CHECKING:
    from typing import Iterator
    from langchain_core.documents import Document


class LoggingMWDumpLoader(MWDumpLoader):
    def _load_single_page_from_dump(self, page) -> Document:  # type: ignore[no-untyped-def, return]
        """Parse a single page."""
        try:
            import mwparserfromhell
        except ImportError as e:
            raise ImportError(
                "Unable to import 'mwparserfromhell'. Please install with"
                " `pip install mwparserfromhell`."
            ) from e
        for revision in page:
            code = mwparserfromhell.parse(revision.text)
            # FIXME: before strip code, do a little more processing to clean up
            # _process_code(code)

            text = code.strip_code(
                normalize=True, collapse=True, keep_template_params=False
            )
            metadata = {"source": page.title}
            return Document(page_content=text, metadata=metadata)

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


def _transform_mw(mw):
    sections = mw.get_sections()
    for s in sections:
        pass
        # extract title: check the first node of every section, getattr title
        # then remove the SECTION from mw

    for link in mw.ifilter_wikilinks():
        if link.title.startswith("File:"):
            mw.remove(link)

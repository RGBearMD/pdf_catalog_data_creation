# =====================================================
# PDF PARSER ESEMPIO DI USO
# =====================================================
'''
from pdf_parser import PDFParser

parser = PDFParser(
    "catalogo.pdf"
)

products = parser.analyze()

print(
    f"Prodotti: {len(products)}"
)

print(
    f"Marchi: {len(parser.get_unique_brands())}"
)

print(
    f"Prodotti Kg: {len(parser.get_kg_products())}"
)
'''


from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Callable, Optional

try:
    import fitz
except ImportError as exc:
    raise ImportError(
        "PyMuPDF is required to use PDFParser. Install it with 'pip install PyMuPDF'."
    ) from exc

from utils import (
    Product,
    CODE_REGEX,
    extract_weight,
)


class PDFParser:
    """
    Analizzatore cataloghi PDF.
    """

    def _extract_section_brand(
        self,
        lines: list[str],
        line_index: int
    ) -> str:

        for i in range(line_index - 1, -1, -1):

            text = lines[i].strip()

            if not text:
                continue

            if text.startswith("Cod."):
                continue

            if len(text) < 3:
                continue
            
            if extract_weight(text):
                continue
            
            if text.startswith("G."):
                continue

            if len(text.split()) <= 6:

                upper_ratio = (
                    sum(
                        1
                        for c in text
                        if c.isupper()
                    )
                    /
                    max(
                        1,
                        sum(
                            1
                            for c in text
                            if c.isalpha()
                        )
                    )
                )

            if upper_ratio > 0.6:
                return text

        return ""

    def __init__(self, pdf_path: str | Path) -> None:

        self.pdf_path = Path(pdf_path)

        self.products: list[Product] = []

        self.total_pages: int = 0

    # =====================================================
    # PUBLIC
    # =====================================================

    def analyze(
        self,
        progress_callback: Optional[
            Callable[[int, int], None]
        ] = None
    ) -> list[Product]:
        """
        Analizza il PDF e restituisce i prodotti.
        """

        self.products.clear()

        document = fitz.open(self.pdf_path)

        try:

            self.total_pages = len(document)

            for page_index in range(self.total_pages):

                page = document[page_index]

                text = page.get_text("text")

                self._parse_page(
                    page_number=page_index + 1,
                    text=text
                )

                if progress_callback:
                    progress_callback(
                        page_index + 1,
                        self.total_pages
                    )

        finally:
            document.close()

        return self.products

    # =====================================================
    # PAGE PARSER
    # =====================================================

    def _parse_page(
        self,
        page_number: int,
        text: str
    ) -> None:
        """
        Estrae i prodotti da una singola pagina.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for index, line in enumerate(lines):

            match = CODE_REGEX.search(line)

            if not match:
                continue

            code = match.group(1)
            
            if code == "MON1001368":

                print("\n----- DEBUG -----")

                for j in range(
                    max(0, index - 8),
                    min(len(lines), index + 3)
                ):
                    print(j, repr(lines[j]))

                print("-----------------\n")

            product = self._build_product(
                page_number=page_number,
                code=code,
                line_index=index,
                lines=lines
            )

            '''print(
                "DEBUG PRODUCT:",
                product.section_brand,
                product.brand,
                product.code
            )'''
            print(product)

            self.products.append(product)

    # =====================================================
    # PRODUCT EXTRACTION
    # =====================================================

    def _build_product(
        self,
        page_number: int,
        code: str,
        line_index: int,
        lines: list[str]
    ) -> Product:
        """
        Costruisce un Product usando le righe
        vicine al codice.
        """

        description = self._extract_description(
            line_index,
            lines
        )

        weight = self._extract_weight_nearby(
            line_index,
            lines
        )

        section_brand = self._extract_section_brand(
            lines,
            line_index
        )

        brand = section_brand

        print("DEBUG BRAND:", section_brand)

        return Product(
            page=page_number,
            section_brand=section_brand,
            description=description,
            weight=weight,
            brand=section_brand,
            code=code
        )

    # =====================================================
    # DESCRIPTION
    # =====================================================

    def _extract_description(
        self,
        line_index: int,
        lines: list[str]
    ) -> str:
        """
        Cerca il nome prodotto nelle righe precedenti.
        """

        candidates: list[str] = []

        start = max(0, line_index - 4)

        for idx in range(start, line_index):

            value = lines[idx].strip()

            if not value:
                continue

            if CODE_REGEX.search(value):
                continue

            candidates.append(value)

        if not candidates:
            return "Descrizione non trovata"

        description_lines = []

        for value in candidates:

            if CODE_REGEX.search(value):
                continue

            if value == self._extract_section_brand(
                lines,
                line_index
            ):
                continue

            weight = extract_weight(value)

            if weight:

                if value == weight:
                    continue
            
            description_lines.append(value)

        return " ".join(description_lines)

    # =====================================================
    # WEIGHT
    # =====================================================

    def _extract_weight_nearby(
        self,
        line_index: int,
        lines: list[str]
    ) -> str:
        """
        Cerca un peso nelle righe vicine.
        """

        start = max(0, line_index - 5)

        end = min(
            len(lines),
            line_index + 3
        )

        for idx in range(start, end):

            weight = extract_weight(
                lines[idx]
            )

            if weight:
                return weight

        return ""

    # =====================================================
    # STATS
    # =====================================================

    def get_brand_counter(self) -> Counter:
        """
        Conteggio prodotti per marchio.
        """

        counter = Counter()

        for product in self.products:
            counter[product.brand] += 1

        return counter

    def get_unique_brands(self) -> list[str]:
        """
        Elenco marchi univoci.
        """

        return sorted(
            {
                product.brand
                for product in self.products
            }
        )

    def get_kg_products(self) -> list[Product]:
        """
        Restituisce solo prodotti Kg.
        """

        return [
            product
            for product in self.products
            if product.is_kg_product
        ]

    # =====================================================
    # SUMMARY
    # =====================================================

    def get_summary(self) -> dict:
        """
        Statistiche generali.
        """

        brand_counter = self.get_brand_counter()

        return {
            "pages": self.total_pages,
            "products": len(self.products),
            "brands": len(brand_counter),
            "kg_products": len(
                self.get_kg_products()
            )
        }
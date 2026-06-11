from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# =====================================================
# REGEX
# =====================================================

CODE_REGEX = re.compile(
    r"Cod\.\s*([A-Z]{3}\d{7})\b",
    re.IGNORECASE
)

CODE_WITH_PREFIX_REGEX = re.compile(
    r"Cod\.\s*([A-Z]{3}\d{7})",
    re.IGNORECASE
)

KG_REGEX = re.compile(
    r"\d+,\d+\s*Kg",
    re.IGNORECASE
)


# =====================================================
# DATACLASS
# =====================================================

@dataclass(slots=True)
class Product:

    page: int

    section_brand: str

    description: str

    weight: str

    brand: str

    code: str

    image_index: int | None = None

    @property
    def is_kg_product(self) -> bool:
        """
        Verifica se il prodotto è espresso in Kg.
        """
        return bool(KG_REGEX.search(self.weight))


# =====================================================
# OUTPUT DIRECTORY
# =====================================================

OUTPUT_DIR = Path("output")


def ensure_output_dir() -> None:
    """
    Crea la cartella output se non esiste.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# =====================================================
# FILE VALIDATION
# =====================================================

def validate_pdf(path: str | Path) -> bool:
    """
    Verifica che il file sia PDF.
    """

    path = Path(path)

    return (
        path.exists()
        and path.suffix.lower() == ".pdf"
    )


def validate_image(path: str | Path) -> bool:
    """
    Verifica che il file sia immagine.
    """

    path = Path(path)

    valid_ext = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    return (
        path.exists()
        and path.suffix.lower() in valid_ext
    )


# =====================================================
# BRAND HELPERS
# =====================================================

def extract_brand_from_code(
    code: str
) -> str:
    """
    Le prime tre lettere identificano il marchio.

    Esempio:
    RAN1005961 -> RAN
    """

    if len(code) < 3:
        return ""

    return code[:3].upper()


# =====================================================
# WEIGHT HELPERS
# =====================================================

def is_kg_weight(text: str) -> bool:
    """
    Determina se il testo contiene un peso in Kg.
    """

    return bool(
        KG_REGEX.search(text)
    )


def extract_weight(text: str) -> Optional[str]:
    """
    Cerca una stringa peso.

    Esempi:
    300 gr
    1,00 Kg
    2,50 Kg
    """

    patterns = [
        r"\d+,\d+\s*Kg",
        r"\d+\s*gr",
        r"\d+\s*g"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return match.group()

    return None


# =====================================================
# LOGGING
# =====================================================

class AppLogger:
    """
    Logger semplice utilizzabile
    dalla GUI.
    """

    def __init__(self) -> None:
        self._messages: list[str] = []

    def add(self, message: str) -> None:
        """
        Aggiunge messaggio.
        """

        self._messages.append(message)

    def clear(self) -> None:
        """
        Svuota log.
        """

        self._messages.clear()

    def get_all(self) -> list[str]:
        """
        Restituisce tutti i messaggi.
        """

        return self._messages.copy()
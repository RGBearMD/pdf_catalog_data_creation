from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Product:

    description: str

    weight: str

    brand: str

    code: str

    page: int

    @property
    def image_name(self) -> str:

        return f"{self.code[-6:]}.jpg"

    @property
    def logo_name(self) -> str:

        return (
            self.brand
            .replace(" ", "")
            .replace("'", "")
            .replace("-", "")
            .lower()
            + ".jpg"
        )
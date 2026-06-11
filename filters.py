from models import Product


def exclude_codes(
    products: list[Product],
    codes: set[str]
) -> list[Product]:

    return [
        p
        for p in products
        if p.code not in codes
    ]


def only_kg(
    products: list[Product]
) -> list[Product]:

    return [
        p
        for p in products
        if "kg" in p.weight.lower()
    ]
from __future__ import annotations
from itertools import product

import pandas as pd

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import shutil

#Posizioni relative all'interno della cella
# PRODUCT CARD

IMAGE_BOTTOM_Y = 55

GOLD_LINE_Y = 55

BLUE_SEPARATOR_Y = 24

WEIGHT_OFFSET = 8
BRAND_OFFSET = 9
CODE_OFFSET = 8

# BRAND CARD

BRAND_LOGO_BOTTOM_Y = 55
BRAND_SEPARATOR_Y = 40

TEXT_LEFT = 6
LINE_LEFT = TEXT_LEFT
LINE_RIGHT = TEXT_LEFT

description_style = ParagraphStyle(
    "Description",
    fontName="JostSemiBold",
    fontSize=8,
    leading=9,
    textColor=(50/255, 77/255, 153/255)
)


pdfmetrics.registerFont(
    TTFont(
        "JostSemiBold",
        "assets/font/Jost-SemiBold.ttf"
    )
)

pdfmetrics.registerFont(
    TTFont(
        "JostRegular",
        "assets/font/Jost-Regular.ttf"
    )
)

from tempfile import gettempdir
from PIL import Image


def optimize_image_for_pdf(
    image_path
):

    temp_dir = Path(
        "output/pdf_cache"
    )

    temp_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = (
        temp_dir
        / f"{Path(image_path).stem}_pdf.jpg"
    )

    with Image.open(image_path) as img:

        if img.mode in ("RGBA", "LA"):

            background = Image.new(
                "RGB",
                img.size,
                (255, 255, 255)
            )

            background.paste(
                img,
                mask=img.split()[-1]
            )

            img = background

        else:

            img = img.convert("RGB")

        max_width = 300

        if img.width > max_width:

            ratio = (
                max_width / img.width
            )

            img = img.resize(
                (
                    max_width,
                    int(img.height * ratio)
                ),
                Image.LANCZOS
            )

        img.save(
            temp_file,
            format="JPEG",
            quality=25,
            optimize=True,
            progressive=True
        )

    return str(temp_file)

def draw_image_fit(
    pdf,
    image_path,
    x,
    y,
    box_w,
    box_h
):

    image_path = optimize_image_for_pdf(
        image_path
    )

    img = ImageReader(image_path)

    iw, ih = img.getSize()

    scale = min(
        box_w / iw,
        box_h / ih
    )

    w = iw * scale
    h = ih * scale

    draw_x = x + (box_w - w) / 2
    draw_y = y + (box_h - h) / 2

    pdf.drawImage(
        image_path,
        draw_x,
        draw_y,
        width=w,
        height=h,
        preserveAspectRatio=True,
        mask="auto"
    )

class CatalogPDFGenerator:

    PAGE_W = 595.3
    PAGE_H = 841.9

    def generate(
        self,
        excel_file,
        output_pdf,
        top_banner,
        bottom_banner,
        cover_image,
        progress_callback=None
    ):
        
        cache_dir = Path(
            "output/pdf_cache"
        )

        if cache_dir.exists():
            shutil.rmtree(cache_dir)

        cache_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        
        df = pd.read_excel(excel_file)

        items = []
        #conteggio prodotti per pagina per mostrare progresso e per indice
        brand_pages = {}

        current_brand = None

        for _, row in df.iterrows():

            brand = str(
                row["Nome marchio"]
            ).strip()

            if brand != current_brand:

                items.append(
                    {
                        "type": "brand",
                        "brand": brand,
                        "logo": str(
                            row["Logo"]
                        )
                    }
                )

                current_brand = brand

            items.append(
                {
                    "type": "product",
                    "row": row
                }
            )

        sim_row = 0
        sim_col = 0

        sim_page = 1
        
        for item in items:

            if item["type"] == "brand":

                if item["brand"] not in brand_pages:

                    brand_pages[
                        item["brand"]
                    ] = sim_page

                if sim_col != 0:

                    sim_row += 1
                    sim_col = 0

            if sim_row >= 3:

                sim_page += 1

                sim_row = 0
                sim_col = 0

            sim_col += 1

            if sim_col >= 3:

                sim_col = 0
                sim_row += 1

        pdf = canvas.Canvas(
            output_pdf,
            pagesize=(
                self.PAGE_W,
                self.PAGE_H
            )
        )
        
        pdf.setTitle(
            Path(output_pdf).stem
        )
        
        pdf.setSubject(
            "Catalogo prodotti"
        )

        pdf.setAuthor(
            "Massimo D'Ambrogio di DiA Srl"
        )

        pdf.setCreator(
            "DiA Catalog Suite by Massimo D'Ambrogio"
        )

        pdf.setProducer(
            "DiA Srl"
        )

        pdf.setSubject(
            "Catalogo prodotti"
        )

        pdf.setKeywords(
            "DiA Srl, Catalog Suite, PDF Automation"
        )
        top = ImageReader(top_banner)

        if cover_image:

            '''cover_image = optimize_image_for_pdf(
                cover_image
            )'''

            pdf.drawImage(
                cover_image,
                0,
                0,
                width=self.PAGE_W,
                height=self.PAGE_H,
                preserveAspectRatio=False
            )
        
        pdf.showPage()
        
        pdf.setFont(
            "JostSemiBold",
            18
        )

        pdf.drawString(
            50,
            self.PAGE_H - 80,
            "INDICE"
        )

        LEFT_X = 60
        RIGHT_X = 320

        TOP_Y = self.PAGE_H - 130

        ROW_H = 18
        MAX_ROWS = 30

        #ORDINE PER PAGINA
        '''for idx, (brand, page) in enumerate(
            brand_pages.items()
        ):'''
        
        #ORDINE ALFABETICO INDICE
        for idx, (brand, page) in enumerate(
            sorted(brand_pages.items())
        ):

            if idx < MAX_ROWS:

                x_left = LEFT_X
                x_right = 260

                y = TOP_Y - (idx * ROW_H)

            else:

                row = idx - MAX_ROWS

                x_left = RIGHT_X
                x_right = self.PAGE_W - 60

                y = TOP_Y - (row * ROW_H)

            pdf.setFont(
                "JostRegular",
                10
            )

            pdf.drawString(
                x_left,
                y,
                brand
            )

            pdf.drawRightString(
                x_right,
                y,
                str(page)
            )

        pdf.showPage()
        
        page_number = 1

        pdf.drawImage(
            top,
            0,
            self.PAGE_H - 80,
            width=self.PAGE_W,
            height=80,
            preserveAspectRatio=False
        )
        
        page_number = 1
        '''bottom_banner = optimize_image_for_pdf(
            bottom_banner
        )'''

        bottom = ImageReader(bottom_banner)

        pdf.drawImage(
            bottom,
            0,
            0,
            width=self.PAGE_W,
            height=80,
            preserveAspectRatio=False
        )

        TOP_BANNER_H = 80
        BOTTOM_BANNER_H = 80

#MISURE CARD PRODOTTO

        CELL_W = 150
        CELL_H = 200

        COL_GAP = 20

        available_h = (
            self.PAGE_H
            - TOP_BANNER_H
            - BOTTOM_BANNER_H
        )

        ROW_GAP = (
            available_h
            - (CELL_H * 3)
        ) / 4

        START_Y = (
            self.PAGE_H
            - TOP_BANNER_H
            - ROW_GAP
        )

        current_row = 0
        current_col = 0

        for idx, item in enumerate(items):
            total_items = len(items)

            if item["type"] == "brand":

                if current_col != 0:

                    current_row += 1
                    current_col = 0

            if current_row >= 3:

                pdf.setFont(
                    "JostRegular",
                    8
                )

                pdf.setFillColorRGB(
                    0,
                    0,
                    0
                )

                pdf.drawRightString(
                    self.PAGE_W - 15,
                    15,
                    str(page_number)
                )


                pdf.showPage()

                page_number += 1


                pdf.drawImage(
                    top,
                    0,
                    self.PAGE_H - 80,
                    width=self.PAGE_W,
                    height=80,
                    preserveAspectRatio=False
                )

                pdf.drawImage(
                    bottom,
                    0,
                    0,
                    width=self.PAGE_W,
                    height=80,
                    preserveAspectRatio=False
                )

                current_row = 0
                current_col = 0

            grid_width = (
                CELL_W * 3
                + COL_GAP * 2
            )

            grid_x = (
                self.PAGE_W - grid_width
            ) / 2

            x = grid_x + current_col * (
                CELL_W + COL_GAP
            )

            y = START_Y - (
                current_row * (
                    CELL_H + ROW_GAP
                )
            ) - CELL_H

###BORDO CARD

            '''pdf.setStrokeColorRGB(
                0.85,
                0.85,
                0.85
            )

            pdf.setLineWidth(0.3)

            pdf.rect(
                x,
                y,
                CELL_W,
                CELL_H
            )'''
            
###GRIGLIA CARD
            '''for yy in range(
                0,
                int(CELL_H),
                10
            ):

                pdf.setFont(
                    "JostRegular",
                    5
                )

                pdf.drawString(
                    x + CELL_W - 15,
                    y + yy,
                    str(yy)
                )'''


            if item["type"] == "brand":

                logo_base = Path(
                    str(item["logo"])
                ).stem

                png_logo = (
                    Path("assets/loghi")
                    / f"{logo_base}.png"
                )

                jpg_logo = (
                    Path("assets/loghi")
                    / f"{logo_base}.jpg"
                )

                jpeg_logo = (
                    Path("assets/loghi")
                    / f"{logo_base}.jpeg"
                )

                logo_file = None

                for candidate in (
                    png_logo,
                    jpg_logo,
                    jpeg_logo
                ):

                    if candidate.exists():

                        logo_file = candidate
                        break

                if logo_file:

                    try:

                        draw_image_fit(
                        pdf,
                        logo_file,
                        x + 10,
                        y + 55,
                        130,
                        110
                    )

                    except Exception:

                        pdf.setFont(
                            "JostSemiBold",
                            8
                        )

                        pdf.setStrokeColorRGB(
                            216 / 255,
                            181 / 255,
                            0 / 255
                        )

                        pdf.setLineWidth(0.8)

                        pdf.line(
                            x + 20,
                            y + BRAND_LOGO_BOTTOM_Y,
                            x + CELL_W - 20,
                            y + BRAND_LOGO_BOTTOM_Y
                        )

                        pdf.drawString(
                            x + 6,
                            y + 120,
                            logo_file.name
                        )

                else:

                    pdf.setFont(
                        "JostSemiBold",
                        8
                    )

                    pdf.drawString(
                        x + 6,
                        y + 120,
                        (
                            f"{logo_base}.png / "
                            f"{logo_base}.jpg"
                        )
                    )

                pdf.setFont(
                    "JostSemiBold",
                    8
                )

                pdf.setStrokeColorRGB(
                    216 / 255,
                    181 / 255,
                    0 / 255
                )

                pdf.setLineWidth(0.3)

                pdf.line(
                     x + 10,
                    y + BRAND_SEPARATOR_Y,
                    x + CELL_W - 10,
                    y + BRAND_SEPARATOR_Y
                )

                pdf.drawCentredString(
                    x + CELL_W / 2,
                    y + 18,
                    item["brand"]
                )

            else:

                product = item["row"]

                image_path = str(
                    product["Immagine"]
                )
                
                local_folder = Path(
                    "assets/immagini_prodotti"
                )
                
                code = str(
                    product["Codice"]
                ).strip()

                image_number = code[-6:]

                for ext in (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                ):

                    local_image = (
                        local_folder
                        / f"{image_number}{ext}"
                    )

                    if local_image.exists():

                        image_path = str(local_image)

                        break


                try:
                    
                    draw_image_fit(
                        pdf,
                        image_path,
                        x + 10,
                        y + IMAGE_BOTTOM_Y,
                        130,
                        120
                    )

                except Exception:

                    pdf.setFont(
                        "JostSemiBold",
                        7
                    )

                    pdf.drawString(
                        x + 6,
                        y + 125,
                        Path(image_path).name
                    )

                pdf.setStrokeColorRGB(
                    216 / 255,
                    181 / 255,
                    0 / 255
                )

                pdf.setLineWidth(0.3)

                pdf.line(
                    x + LINE_LEFT,
                    y + GOLD_LINE_Y,
                    x + CELL_W - LINE_RIGHT,
                    y + GOLD_LINE_Y
                )

                pdf.setFont(
                    "JostSemiBold",
                    8
                )

                pdf.setFillColorRGB(
                    50 / 255,
                    77 / 255,
                    153 / 255
                )

                paragraph = Paragraph(
                    str(product["Nome referenza"]),
                    description_style
                )

                w, h = paragraph.wrap(
                    125,
                    25
                )

#IMPOSTAZIONE PRAGRAFO PER DESCRIZIONE PRODOTTO
                paragraph.drawOn(
                    pdf,
                    x + TEXT_LEFT,
                    y + GOLD_LINE_Y - 2 - h
                )

                current = ""


                pdf.setStrokeColorRGB(
                    50 / 255,
                    77 / 255,
                    153 / 255
                )

                pdf.setLineWidth(0.3)

                pdf.line(
                    x + LINE_LEFT,
                    y + BLUE_SEPARATOR_Y,
                    x + CELL_W - LINE_RIGHT,
                    y + BLUE_SEPARATOR_Y
                )

                pdf.setFont(
                    "JostRegular",
                    8
                )

                pdf.setFillColorRGB(
                    0,
                    0,
                    0
                )
    
                weight_y = (
                    BLUE_SEPARATOR_Y - WEIGHT_OFFSET
                )    
                
                pdf.drawString(
                    x + TEXT_LEFT,
                    y + weight_y,
                    str(product["Peso"])
                )
                
                pdf.setFont(
                    "JostRegular",
                    7
                )

                pdf.setFillColorRGB(
                    130 / 255,
                    130 / 255,
                    130 / 255
                )

                brand_y = (
                    weight_y - BRAND_OFFSET
                )

                pdf.drawString(
                    x + TEXT_LEFT,
                    y + brand_y,
                    str(product["Nome marchio"])
                )

                pdf.setFont(
                    "JostRegular",
                    7
                )

                pdf.setFillColorRGB(
                    130 / 255,
                    130 / 255,
                    130 / 255
                )

                code_y = (
                    brand_y - CODE_OFFSET
                )

                pdf.drawString(
                    x + TEXT_LEFT,
                    y + code_y,
                    str(product["Codice"])
                )

            if progress_callback:

                progress_callback(
                        int(
                            ((idx + 1) / total_items)
                            * 100
                        )
                    )

                current_col += 1

            if current_col >= 3:

                current_col = 0
                current_row += 1

        pdf.setFont(
            "JostRegular",
            8
        )

        pdf.setFillColorRGB(
            0,
            0,
            0
        )

        pdf.drawRightString(
            self.PAGE_W - 15,
            15,
            str(page_number)
        )

        pdf.showPage()

        pdf.drawImage(
            "assets/DiaSrl 2026 coverR.jpg",
            0,
            0,
            width=self.PAGE_W,
            height=self.PAGE_H,
            preserveAspectRatio=False
        )

        pdf.showPage()

        pdf.save()
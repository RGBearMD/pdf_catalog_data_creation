from __future__ import annotations

import threading
from pathlib import Path

import tkinter as tk

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from pdf_parser import PDFParser
from excel_export import ExcelExporter
from pdf_generator import CatalogPDFGenerator

from utils import (
    AppLogger,
    ensure_output_dir,
)


class PDFCatalogApp:
    
    def update_pdf_progress(
        self,
        value: int
    ) -> None:

        self.root.after(
            0,
            lambda v=value: self.pdf_progress.configure(
                value=v
            )
        )

    def safe_ui_call(self, func, *args):

        self.root.after(
            0,
            lambda: func(*args)
        )

    def __init__(self) -> None:

        ensure_output_dir()

        self.root = tk.Tk()

        self.root.title(
            "PDF Catalog Analyzer"
        )

        self.root.geometry(
            "900x750"
        )

        self.root.minsize(
            900,
            700
        )

        self.logger = AppLogger()

        self.products = []

        self.filtered_products = []

        self.parser = None

        self.pdf_path: str = ""
        
        self.selected_excel: str = ""

        self.top_banner: str = (
            "assets/banner1_2480.2x377.6.jpg"
        )

        self.bottom_banner: str = (
            "assets/banner2_2480.2x327.3.jpg"
        )
        
        self.cover_image: str = ""

        self._build_ui()

        self.top_banner_label.config(
            text=Path(
                self.top_banner
            ).name
        )

        self.bottom_banner_label.config(
            text=Path(
                self.bottom_banner
            ).name
        )

    # ==================================================
    # UI
    # ==================================================

    def _build_ui(self) -> None:

        container = ttk.Frame(
            self.root,
            padding=15
        )

        container.pack(
            fill="both",
            expand=True
        )

        notebook = ttk.Notebook(
            container
        )

        notebook.pack(
            fill="both",
            expand=True
        )

        excel_tab = ttk.Frame(
            notebook
        )

        pdf_tab = ttk.Frame(
            notebook
        )

        notebook.add(
            excel_tab,
            text="Excel"
        )

        notebook.add(
            pdf_tab,
            text="PDF Finale"
        )
        
        # ------------------------------------------
        # PDF
        # ------------------------------------------

        pdf_frame = ttk.LabelFrame(
            excel_tab,
            text="PDF"
        )

        pdf_frame.pack(
            fill="x",
            pady=5
        )

        self.pdf_label = ttk.Label(
            pdf_frame,
            text="Nessun PDF selezionato"
        )

        self.pdf_label.pack(
            anchor="w",
            padx=10,
            pady=5
        )

        ttk.Button(
            pdf_frame,
            text="Seleziona PDF",
            command=self.select_pdf
        ).pack(
            padx=10,
            pady=10
        )

        # ------------------------------------------
        # ANALISI
        # ------------------------------------------

        analysis_frame = ttk.LabelFrame(
            excel_tab,
            text="Analisi"
        )

        analysis_frame.pack(
            fill="x",
            pady=5
        )

        ttk.Button(
            analysis_frame,
            text="Analizza PDF",
            command=self.analyze_pdf
        ).pack(
            pady=10
        )

        self.pages_var = tk.StringVar(
            value="Pagine: 0"
        )

        self.codes_var = tk.StringVar(
            value="Codici trovati: 0"
        )

        self.brands_var = tk.StringVar(
            value="Marchi trovati: 0"
        )

        self.kg_var = tk.StringVar(
            value="Prodotti Kg: 0"
        )

        ttk.Label(
            analysis_frame,
            textvariable=self.pages_var
        ).pack(anchor="w", padx=10)

        ttk.Label(
            analysis_frame,
            textvariable=self.codes_var
        ).pack(anchor="w", padx=10)

        ttk.Label(
            analysis_frame,
            textvariable=self.brands_var
        ).pack(anchor="w", padx=10)

        ttk.Label(
            analysis_frame,
            textvariable=self.kg_var
        ).pack(anchor="w", padx=10)

        # ------------------------------------------
        # PROGRESS
        # ------------------------------------------

        self.progress = ttk.Progressbar(
            excel_tab,
            orient="horizontal",
            mode="determinate"
        )

        self.progress.pack(
            fill="x",
            pady=10
        )

        # ------------------------------------------
        # EXPORT
        # ------------------------------------------

        export_frame = ttk.LabelFrame(
            excel_tab,
            text="Export"
        )

        export_frame.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            export_frame,
            text="Codici da escludere (separati da virgola)"
        ).pack(
            anchor="w",
            padx=10,
            pady=(10, 0)
        )

        self.exclude_codes_text = tk.Text(
            export_frame,
            height=4
        )

        self.exclude_codes_text.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Button(
            export_frame,
            text="Esporta Excel",
            command=self.export_excel
        ).pack(
            pady=10
        )

        # ------------------------------------------
        # BANNER
        # ------------------------------------------

        banner_frame = ttk.LabelFrame(
            pdf_tab,
            text="Modifica Banner"
        )

        banner_frame.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            banner_frame,
            text="Copertina iniziale"
        ).pack(
            anchor="w",
            padx=10
        )
        
        # ------------------------------------------
        # EXCEL SORGENTE
        # ------------------------------------------

        excel_frame = ttk.LabelFrame(
            pdf_tab,
            text="Excel sorgente"
        )

        excel_frame.pack(
            fill="x",
            pady=5
        )

        self.excel_label = ttk.Label(
            excel_frame,
            text="Nessun Excel selezionato"
        )

        self.excel_label.pack(
            anchor="w",
            padx=10,
            pady=5
        )
        
        self.excel_combo = ttk.Combobox(
            excel_frame,
            state="readonly",
            width=60
        )

        self.excel_combo.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.excel_combo.bind(
            "<<ComboboxSelected>>",
            self.on_excel_selected
        )
        
        self.cover_combo = ttk.Combobox(
            banner_frame,
            state="readonly",
            width=60
        )

        self.cover_combo.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.cover_combo.bind(
            "<<ComboboxSelected>>",
            self.on_cover_selected
        )

        self.root.after(
            100,
            self.refresh_excel_list
        )

        self.root.after(
            100,
            self.refresh_cover_list
        )

        ttk.Button(
            excel_frame,
            text="Seleziona Excel",
            command=self.select_excel
        ).pack(
            padx=10,
            pady=10
        )

        final_frame = ttk.LabelFrame(
            pdf_tab,
            text="PDF Finale"
        )

        final_frame.pack(
            fill="x",
            pady=5
        )
        
        self.pdf_progress = ttk.Progressbar(
            final_frame,
            orient="horizontal",
            mode="determinate",
            length=300
        )

        self.pdf_progress.pack(
            fill="x",
            padx=10,
            pady=5
        )
        
        self.generate_pdf_btn = ttk.Button(
            final_frame,
            text="Genera PDF",
            command=self.generate_pdf
        )

        self.generate_pdf_btn.pack(
            pady=10
        )

        self.cover_label = ttk.Label(
            banner_frame,
            text="-"
        )

        self.cover_label.pack(
            anchor="w",
            padx=20
        )

        ttk.Button(
            banner_frame,
            text="Seleziona copertina",
            command=self.select_cover
        ).pack(
            padx=10,
            pady=5
        )

        ttk.Label(
            banner_frame,
            text="Banner superiore"
        ).pack(
            anchor="w",
            padx=10
        )

        self.top_banner_label = ttk.Label(
            banner_frame,
            text="-"
        )

        self.top_banner_label.pack(
            anchor="w",
            padx=20
        )

        ttk.Button(
            banner_frame,
            text="Seleziona immagine",
            command=self.select_top_banner
        ).pack(
            padx=10,
            pady=5
        )

        ttk.Label(
            banner_frame,
            text="Banner inferiore"
        ).pack(
            anchor="w",
            padx=10
        )

        self.bottom_banner_label = ttk.Label(
            banner_frame,
            text="-"
        )

        self.bottom_banner_label.pack(
            anchor="w",
            padx=20
        )

        ttk.Button(
            banner_frame,
            text="Seleziona immagine",
            command=self.select_bottom_banner
        ).pack(
            padx=10,
            pady=5
        )


        # ------------------------------------------
        # LOG
        # ------------------------------------------

        log_frame = ttk.LabelFrame(
            excel_tab,
            text="Log Operazioni"
        )

        log_frame.pack(
            fill="both",
            expand=True,
            pady=5
        )

        self.log_text = tk.Text(
            log_frame,
            height=15
        )

        self.log_text.pack(
            fill="both",
            expand=True
        )


    def refresh_excel_list(self) -> None:

        excel_folder = Path(
            "output/excel"
        )

        excel_files = sorted(
            excel_folder.glob("*.xlsx"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        self.available_excels = {
            f.name: str(f)
            for f in excel_files
        }

        self.excel_combo["values"] = list(
            self.available_excels.keys()
        )

        if excel_files:

            self.excel_combo.set(
                excel_files[0].name
            )

            self.selected_excel = str(
                excel_files[0]
            )

            self.excel_label.config(
                text=excel_files[0].name
            )

    def refresh_cover_list(self) -> None:

        base_dir = Path(__file__).resolve().parent

        cover_folder = (
            base_dir
            / "assets"
        )

        self.log(
            f"Base dir: {base_dir}"
        )

        self.log(
            f"Cartella copertine: {cover_folder}"
        )

        self.log(
            f"Esiste: {cover_folder.exists()}"
        )
        
        self.log(
            f"Cartella copertine: {cover_folder.resolve()}"
        )

        assets_folder = (
            base_dir
            / "assets"
        )

        if assets_folder.exists():

            self.log(
                "Contenuto assets:"
            )

            for f in assets_folder.iterdir():

                self.log(
                    f" - {f.name}"
                )

        else:

            self.log(
                "CARTELLA ASSETS NON TROVATA"
            )

        cover_files = []
        
        if not cover_folder.exists():

            self.log(
                f"Cartella inesistente: {cover_folder}"
            )

            return

        for ext in (
            "*.jpg",
            "*.jpeg"
        ):
            cover_files.extend(
                cover_folder.glob(ext)
            )

        cover_files = sorted(
            cover_files
        )
        
        self.log(
            f"Copertine trovate: {len(cover_files)}"
        )

        for f in cover_files:

            self.log(
                f"Copertina trovata: {f.name}"
            )

        for f in cover_files:
            print(f)

        self.available_covers = {
            f.name: str(f)
            for f in cover_files
        }

        self.cover_combo["values"] = list(
            self.available_covers.keys()
        )
        
        self.log(
            f"Valori combobox: {self.cover_combo['values']}"
        )

        if cover_files:

            self.cover_combo.configure(
                values=[
                    f.name
                    for f in cover_files
                ]
            )

            self.cover_combo.current(0)

            self.cover_image = str(
                cover_files[0]
            )

            self.cover_label.config(
                text=cover_files[0].name
            )


    def on_cover_selected(
        self,
        event=None
    ) -> None:

        filename = self.cover_combo.get()

        if filename not in self.available_covers:
            return

        self.cover_image = (
            self.available_covers[
                filename
            ]
        )

        self.cover_label.config(
            text=filename
        )

    def on_excel_selected(
        self,
        event=None
    ) -> None:

        filename = self.excel_combo.get()

        if filename not in self.available_excels:
            return

        self.selected_excel = (
            self.available_excels[
                filename
            ]
        )

        self.excel_label.config(
            text=filename
        )

    # ==================================================
    # LOG
    # ==================================================

    def log(self, message: str) -> None:

        self.logger.add(message)

        self.log_text.insert(
            tk.END,
            message + "\n"
        )

        self.log_text.see(tk.END)

    # ==================================================
    # FILE PICKERS
    # ==================================================

    def select_pdf(self) -> None:

        path = filedialog.askopenfilename(
            filetypes=[
                ("PDF", "*.pdf")
            ]
        )

        if not path:
            return

        self.pdf_path = path

        self.pdf_label.config(
            text=Path(path).name
        )

        self.log(
            f"PDF selezionato: {path}"
        )


# SELEZIONA EXCEL PER PDF FINALE

    def select_excel(self) -> None:

        path = filedialog.askopenfilename(
            filetypes=[
                ("Excel", "*.xlsx")
            ]
        )

        if not path:
            return

        self.selected_excel = path

        self.excel_label.config(
            text=Path(path).name
        )
        
        self.excel_combo.set(
            Path(path).name
        )

        self.log(
            f"Excel selezionato: {path}"
        )

    def select_cover(self) -> None:

        path = filedialog.askopenfilename(
            filetypes=[
                ("Immagini", "*.jpg *.jpeg *.png")
            ]
        )

        if not path:
            return

        self.cover_image = path

        self.cover_label.config(
            text=Path(path).name
        )
        
        if hasattr(
            self,
            "cover_combo"
        ):
            self.cover_combo.set(
                Path(path).name
            )

    def select_top_banner(self) -> None:

        path = filedialog.askopenfilename(
            filetypes=[
                ("Immagini", "*.png *.jpg *.jpeg")
            ]
        )

        if path:

            self.top_banner = path

            self.top_banner_label.config(
                text=Path(path).name
            )

    def select_bottom_banner(self) -> None:

        path = filedialog.askopenfilename(
            filetypes=[
                ("Immagini", "*.png *.jpg *.jpeg")
            ]
        )

        if path:

            self.bottom_banner = path

            self.bottom_banner_label.config(
                text=Path(path).name
            )

    # ==================================================
    # ANALISI
    # ==================================================

    def analyze_pdf(self) -> None:

        if not self.pdf_path:

            messagebox.showerror(
                "Errore",
                "Selezionare un PDF."
            )

            return

        thread = threading.Thread(
            target=self._analysis_worker,
            daemon=True
        )

        thread.start()

    def _analysis_worker(self) -> None:

        try:

            self.log(
                "Analisi avviata..."
            )

            self.parser = PDFParser(
                self.pdf_path
            )

            self.products = self.parser.analyze(
                progress_callback=self.update_progress
            )

            summary = (
                self.parser.get_summary()
            )

            self.safe_ui_call(
                self.pages_var.set,
                f"Pagine: {summary['pages']}"
            )

            self.codes_var.set(
                f"Codici trovati: {summary['products']}"
            )

            self.brands_var.set(
                f"Marchi trovati: {summary['brands']}"
            )

            self.kg_var.set(
                f"Prodotti Kg: {summary['kg_products']}"
            )

            self.log(
                "Analisi completata."
            )

        except Exception as exc:

            messagebox.showerror(
                "Errore",
                str(exc)
            )

    # ==================================================
    # PROGRESS
    # ==================================================

    def update_progress(
        self,
        current: int,
        total: int
    ) -> None:

        value = (
            current / total
        ) * 100

        percentage = (
            current / total
        ) * 100

        self.progress["value"] = 0
        self.progress["maximum"] = 100

        self.root.update_idletasks()

    # ==================================================
    # EXPORT
    # ==================================================

    def export_excel(self) -> None:

        if not self.products:

            messagebox.showwarning(
                "Attenzione",
                "Analizzare prima un PDF."
            )

            return

        try:

            pdf_name = Path(
                self.pdf_path
            ).stem

            output_file = (
                f"output/excel/{pdf_name}.xlsx"
            )

            exporter = ExcelExporter()

            excluded_codes = {

                code.strip().upper()

                for code in self.exclude_codes_text.get(
                    "1.0",
                    tk.END
                ).replace(
                    "\n",
                    ","
                ).split(",")

                if code.strip()
            }

            products_to_export = [

                product

                for product in self.products

                if product.code.upper()
                not in excluded_codes
            ]

            exporter.export_products(
                products_to_export,
                output_file
            )
            
            self.selected_excel = output_file
            
            self.root.after(
                100,
                self.refresh_excel_list
            )
            
            self.root.after(
                100,
                self.refresh_cover_list
            )

            self.excel_combo.set(
                Path(output_file).name
            )

            if hasattr(
                self,
                "excel_label"
            ):
                self.excel_label.config(
                    text=Path(output_file).name
                )
            
            self.selected_excel = output_file

            self.log(
                f"Excel creato: {output_file}"
            )

            messagebox.showinfo(
                "Successo",
                f"Creato:\n{output_file}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Errore",
                str(exc)
            )

    # ==================================================
    # PDF GENERATION
    # ==================================================

    def generate_pdf(self) -> None:

        threading.Thread(
            target=self._generate_pdf_worker,
            daemon=True
        ).start()
        
    def _generate_pdf_worker(self) -> None:
        
        self.root.after(
            0,
            lambda: self.generate_pdf_btn.config(
                state="disabled"
            )
        )

        try:

            self.root.after(
                0,
                lambda: self.pdf_progress.configure(
                    value=0
                )
            )

            generator = CatalogPDFGenerator()

            if not hasattr(
                self,
                "selected_excel"
            ):

                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Errore",
                        "Seleziona prima un file Excel."
                    )
                )

                return

            excel_path = Path(
                self.selected_excel
            )

            pdf_path = excel_path.with_suffix(
                ".pdf"
            )

            generator.generate(
                excel_file=str(excel_path),
                output_pdf=str(pdf_path),
                top_banner=self.top_banner,
                bottom_banner=self.bottom_banner,
                cover_image=self.cover_image,
                progress_callback=self.update_pdf_progress
            )

            self.root.after(
                0,
                lambda: self.pdf_progress.configure(
                    value=100
                )
            )

            self.root.after(
                0,
                lambda: self.log(
                    "PDF generato."
                )
            )

            self.root.after(
                0,
                lambda: self.generate_pdf_btn.config(
                    state="normal"
                )
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Successo",
                    f"Creato:\n{pdf_path}"
                )
            )

        except Exception as exc:

            error_text = str(exc)

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Errore",
                    error_text
                )
            )

    # ==================================================
    # RUN
    # ==================================================

    def run(self) -> None:

        self.root.mainloop()
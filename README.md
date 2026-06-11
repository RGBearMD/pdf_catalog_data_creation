\# PDF Catalog Data Creation



Applicazione Python con interfaccia Tkinter per:



\* Analizzare cataloghi PDF

\* Estrarre prodotti e codici articolo

\* Esportare dati in Excel

\* Generare cataloghi PDF finali personalizzati

\* Gestire copertine, banner e loghi



\## Funzionalità



\### Analisi PDF



\* Lettura cataloghi PDF

\* Estrazione prodotti

\* Conteggio pagine

\* Conteggio marchi

\* Identificazione prodotti a peso



\### Export Excel



\* Creazione automatica file Excel

\* Esclusione codici personalizzata

\* Salvataggio in `output/excel`



\### Generazione PDF Finale



\* Utilizzo di un Excel sorgente

\* Copertina personalizzabile

\* Banner superiore personalizzabile

\* Banner inferiore personalizzabile

\* Inserimento immagini prodotto

\* Inserimento loghi



\## Requisiti



Python 3.11 o superiore.



\## Installazione



Clonare il repository:



```bash

git clone https://github.com/TUO-UTENTE/pdf\_catalog\_data\_creation.git

cd pdf\_catalog\_data\_creation

```



Creare un ambiente virtuale:



```bash

python -m venv venv

```



Attivazione Windows:



```bash

venv\\Scripts\\activate

```



Installare le dipendenze:



```bash

pip install -r requirements.txt

```



\## Avvio



```bash

python gui.py

```



\## Struttura del progetto



```text

assets/

├─ immagini\_prodotti/

├─ loghi/

├─ font/



output/

├─ excel/



gui.py

pdf\_generator.py

pdf\_parser.py

excel\_export.py

utils.py

```



\## Note



Le cartelle:



```text

assets/loghi/

assets/immagini\_prodotti/

```



non sono incluse nel repository Git e devono essere fornite separatamente.



\## Licenza



Uso interno aziendale.




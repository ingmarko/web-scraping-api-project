# Web Scraping + API Integration (Python)

## Përshkrimi
Ky projekt:
1. Bën web scraping në Hacker News për të nxjerrë titujt dhe URL-të e artikujve.
2. Përdor Microlink API për të marrë metadata shtesë për çdo URL (title/description/image/domain).
3. Bashkon të dhënat dhe i ruan në `output.csv` dhe `output.json`.

## Teknologjitë / Libraritë
- Python 3
- requests
- beautifulsoup4
- lxml
- pandas

## Si ekzekutohet
### 1) Instalimi
```bash

## Krijimi i virtual environment python
python3 -m venv .venv

## Aktivizimi i virtual environment
source .venv/bin/activate

## Install librarite e nevojshme
pip install requests beautifulsoup4 pandas lxml

## Ruaj dependencies
pip freeze > requirements.txt

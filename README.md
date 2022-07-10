# Notion Diary to Book

The scrips in this repository were implemented as a novel way of converting the markdown files produced by exporting a Notion database of pages to a Book. LaTeX is used to compile the book.

It is implemented for the notion template given here, which is a diary that can be kept with a partner. The compiled book is intended to be for a year of entries for two people, but may easily be adjusted as required.

Essentially, the code included is a markdown to tex converter.

## Requirements

```bash
pip install -r requirements.txt
```

## Getting started

- Export your notion database as a 'Markdown & CSV' zip file, making sure to 'Include subpages'
- Unzip into a folder called 'notion-export'
- If desired, compile a dedication PDF page (template script given in build directory)
- Upload images to be used as month cover photos into a month_photos folder, naming by lowercase first three letters of the month + index

## Folder structure

Run the following command to automatically generate the required build folder structure

```bash
python3 src/structure.py
```

## Converting files to tex

Run the following command to generate all the required tex files and convert images to PDFs

```bash
python3 src/convertor.py
```

## Compiling book

Run the following command to compile the book, ensuring a suitable distribution of XeLaTeX is installed on the system

```bash
xelatex build\book.tex 
```

## Contact

Please do drop me an email at is473@cam.ac.uk with any questions for about this project
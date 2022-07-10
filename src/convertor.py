import os
import emojis
import numpy as np
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
import csv


class NotionBook:

    def __init__(self):
        self.months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        self.full_months = {'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April', 'May': 'May', 'Jun': 'Jun', 'Jul': 'July', 'Aug': 'August', 'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'}
        self.notion_dir = 'notion-export/'
        self.DIARIES_DIR = self.notion_dir + 'diaries-export/'

    def preprocessing(self):
        '''Returns dict {months:
                            {dates:
                                {partner:
                                    {Title: str,
                                     Picture dir: str,
                                     Text dir: str}
                                }
                            }
                        }
        '''

        self.entries = {month: {} for month in self.months.values()}

        titles = []

        with open(self.notion_dir + 'contents.csv', 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                titles.append(row[0].replace('/', ' ')[0:10])

        for file in os.listdir(self.DIARIES_DIR):
            if file.endswith(".md") and file[0:10] in titles:
                TEXT_DIR = self.DIARIES_DIR + file
                PICTURE_DIR = self.DIARIES_DIR + file[:-3] + "/"
                picture_file = "No Picture"

                if os.path.isdir(PICTURE_DIR) and len(os.listdir(PICTURE_DIR)) != 0:
                    picture_file = PICTURE_DIR + os.listdir(PICTURE_DIR)[0]

                if file[0:2] not in self.entries[self.months[file[3:5]]]:
                    self.entries[self.months[file[3:5]]][file[0:2]] = {}

                if file[6] == "-":
                    partner = "partner 2"
                    if partner in self.entries[self.months[file[3:5]]][file[0:2]]:
                        partner = "partner 1"
                    title = file[8:].rsplit(' ', 1)[0]
                else:
                    partner = "partner 1"
                    if partner in self.entries[self.months[file[3:5]]][file[0:2]]:
                        partner = "partner 2"
                    title = file[6:].rsplit(' ', 1)[0]

                title = self.textitle(title)

                self.entries[self.months[file[3:5]]][file[0:2]][partner] = {"Title": title, "Text dir": TEXT_DIR,
                                                                            "Picture dir": picture_file}

                print(f"Entry {title} collected")

    @staticmethod
    def textitle(title):
        if len(title) == 0:
            return 'empty' + str(np.random.randint(100, 999))
        else:
            title = title.encode("ascii", "ignore")
            title = title.decode()
            title = title.replace(',', '')
            title = title.replace('(', '')
            title = title.replace(')', '')
            return title

    def create_latex_diary(self, date, month, partner):
        with open(self.entries[month][date][partner]['Text dir'], 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            line = self.texclean(lines[i])

            lines[i] = self.texemoji(line)

            if line.startswith('# Goals and objectives'):
                if lines[i + 4].startswith('#'):
                    lines[i] = ''
                    lines[i + 2] = ''
                else:
                    lines[
                        i] = '\n \subsubsection{Goals and objectives} \n \n' + r'\begin{todolist}' + '\n \itemsep0em \n'

            elif line.startswith(('- [ ]', '- [x]')):
                lines[i] = '\item ' + line[7:]

                if not lines[i + 1].startswith(('- [ ]', '- [x]', '    -')):
                    lines[i + 1] = '\end{todolist} \n'

            elif line.startswith('# How was '):
                lines = self.converter(lines, i, 'How was your')

            elif line.startswith('# What have '):
                lines = self.converter(lines, i, 'What have you learnt?')

            elif line.startswith('# What do '):
                lines = self.converter(lines, i, 'What do you love most?')

            elif line.startswith('# What did '):
                lines = self.converter(lines, i, 'What did you lose?')

            elif line.startswith('# How could '):
                lines = self.converter(lines, i, 'How could you be better?')

            elif line.startswith('# How can '):
                lines = self.converter(lines, i, 'How can you make sure you dont forget?')

            elif line.startswith('# Any other thoughts'):
                lines = self.converter(lines, i, 'Any other thoughts?')

        lines = list(filter(None, lines[9:]))
        title = self.entries[month][date][partner]['Title']
        picture_dir = self.entries[month][date][partner]['Picture dir']

        with open(f'build/entries/{month}/pages/{title}.tex', 'w', encoding='utf-8') as t:
            t.write('\n\section*{' + title + '}\n\n')
            t.writelines(lines)

            if picture_dir != 'No Picture':
                self.img_to_pdf(picture_dir, f'build/entries/{month}/pages/{title}.pdf')
                t.write(
                    '\n \n\includepdf[pages={1}, height=\paperheight]' + '{' f"entries/{month}/pages/{title}.pdf" + '}')

    @staticmethod
    def converter(lines, i, section: str):
        if len(lines) <= i + 1 or lines[i + 2].startswith('#'):
            lines[i] = ''
        else:
            lines[i] = '\n' + '\subsubsection{' + section + '}' + '\n'
        return lines

    @staticmethod
    def texclean(line):
        line = line.replace('&', '\&')
        line = line.replace('%', '\%')
        line = line.replace('_', '\_')
        line = line.replace("’", "'")
        line = line.replace("~", "")
        return line

    @staticmethod
    def texemoji(line):
        all_emojis = emojis.get(line)
        ignore_emoji = ['1F92D', '1F970', '1F642', '1F97A', '1F929', '1F9D0', '1F913', '1F976', '1F928', '1F923',
                        '1F4F8']
        for emoji in all_emojis:
            emoji.replace(" ", "")
            emoji_unicode = '{:X}'.format(ord(emoji[0]))

            if emoji_unicode not in ignore_emoji:
                latex_emoji = r'\raisebox{-0.2em}{\includegraphics[height=1em]{emojis/' + emoji_unicode + '.pdf}}'
                line = line.replace(emoji, latex_emoji)
        return line

    @staticmethod
    def img_to_pdf(in_dir, out_dir):
        print(f"Converting image to pdf")
        temp_dir = out_dir[:-4] + '-temp.pdf'
        image = Image.open(in_dir)
        pdf_bytes = image.convert('RGB')
        pdf_bytes.save(temp_dir)
        pdfIn = open(temp_dir, 'rb')
        pdfReader = PdfFileReader(pdfIn)
        page = pdfReader.getPage(0)
        size = list(page.mediaBox)[2:]
        if size[0] > size[1]:
            pdfWriter = PdfFileWriter()
            page.rotateClockwise(90)
            pdfWriter.addPage(page)
            pdfOut = open(out_dir, 'wb')
            pdfWriter.write(pdfOut)
            pdfOut.close()
        else:
            pdf_bytes.save(out_dir)

        pdfIn.close()
        os.remove(temp_dir)

    def write_to_tex(self):
        for month in self.months.values():

            with open(f'build/entries/{month}/{month}.tex', 'w', encoding='utf-8') as f:
                f.write('\chapter{' + self.full_months[month] + '}\n\n')
                pic_dirs = []
                for picture in os.listdir('month_photos/'):
                    if picture[0:3].capitalize() == month:
                        pic_dirs.append('month_photos/' + picture)
                for picture_dir in pic_dirs:
                    out_dir = f"build/entries/{month}/pages/{month}{pic_dirs.index(picture_dir) + 1}.pdf"
                    self.img_to_pdf(picture_dir, out_dir)
                    f.write('\includepdf[pages={1}, height=\paperheight]' + '{' + out_dir + '}' + '\n')
                for date in self.entries[month].keys():
                    for partner in self.entries[month][date].keys():
                        title = self.entries[month][date][partner]['Title']
                        if partner == "partner 2":
                            emoji = r'\raisebox{-0.2em}{\includegraphics[height=1em]{emojis/2600.pdf}}'
                        else:
                            emoji = r'\raisebox{-0.2em}{\includegraphics[height=1em]{emojis/1F427.pdf}}'
                        f.write(r'{\thispageheader[L]{' + partner + ' ' + emoji + '}\n')
                        f.write(r'\thispageheader[R]{' + date + ' ' + month + '}\n')
                        f.write('\input{entries/' + month + '/pages/' + title + '.tex}\n')
                        f.write(r'\newpage}' + '\n')
        with open('build/book.tex', 'w', encoding='utf-8') as f:
            f.write(r'\documentclass[9pt]{memoir}' + '\n\n')

            f.write(r'\input{style.tex}' + '\n\n')
            f.write(r'\begin{document}' + '\n \n')
            # Optional
            # f.write(r'\input{dedication.tex}' + '\n\n')
            f.write(r'\tableofcontents*' + '\n\n')

            for month in self.months.values():
                f.write('\input{entries/' + month + '/' + month + '.tex' + '}\n')
            f.write(r'\end{document}')


if __name__ == "__main__":
    N = NotionBook()
    N.preprocessing()

    for month in N.months.values():
        for date in N.entries[month].keys():
            for partner in N.entries[month][date].keys():
                N.create_latex_diary(date, month, partner)

    N.write_to_tex()

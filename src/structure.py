import os
import shutil
import calendar


def month_folders(ENTRIES_DIR):
    if os.path.exists(ENTRIES_DIR):
        shutil.rmtree(ENTRIES_DIR)
    for month in calendar.month_abbr:
        os.mkdir(f"build/entries/{month}")
        os.mkdir(f"build/entries/{month}/pages")


if __name__ == "__main__":
    month_folders("build/entries")

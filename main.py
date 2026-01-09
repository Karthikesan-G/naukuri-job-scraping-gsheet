import json
from scraper import scrape
from processor import process_output
from gsheet import clean_sheet, write_sheet

with open("config.json") as f:
    config = json.load(f)

headers = config["headers"]
infos = config["infos"]

def main():
    g_client = clean_sheet()
    for info in infos:
        scrape(info, headers)
        df = process_output(info)
        write_sheet(g_client, info["job_title_keyword"], df)

if __name__ == "__main__":
    main()

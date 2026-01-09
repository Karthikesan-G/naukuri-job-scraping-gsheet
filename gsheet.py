import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

def clean_sheet():
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("gsheet-creds.json", scope)
    client = gspread.authorize(creds)

    # clear sheets
    spreadsheet = client.open("Job Scrape Results")
    for sheet in spreadsheet.worksheets():
        sheet.clear()
    
    return client

def write_sheet(client, job_title_keyword, df):

    spreadsheet = client.open("Job Scrape Results")

    sheet_names = [ws.title for ws in spreadsheet.worksheets()]
    if job_title_keyword in sheet_names:
        worksheet = spreadsheet.worksheet(job_title_keyword)
    else:
        worksheet = spreadsheet.add_worksheet(title=job_title_keyword, rows=1000, cols=20)

    worksheet.clear()
    set_with_dataframe(worksheet, df)
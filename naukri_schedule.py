
##### Importing required modules #####

import os
import re
import time
import warnings
import requests
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import string
from concurrent.futures import ThreadPoolExecutor
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
warnings.filterwarnings("ignore")

today = datetime.now().strftime("%Y-%m-%d")

# Cache_path = "Cache/"
# if not os.path.exists(Cache_path):
#     os.makedirs(Cache_path)

def clean(data):
    data = str(data)
    data = re.sub(r'\s\s+', ' ', data)
    data = re.sub(r'\n|\\n|\r|\\r', ' ', data)
    data = re.sub(r'\t|\\t', ' ', data)
    data = re.sub(r'<[^>]*?>', ' ', data)
    data = re.sub(r'\s\s+', ' ', data)
    data = re.sub(r'\s*\,\s*$', '', data)
    data = re.sub(r'\s*\.\s*$', '', data)
    data = re.sub(r'\s*$', '', data)
    data = re.sub(r'^\s*', '', data)
    data = re.sub(r'^\s*\|\s*', '', data)
    data = re.sub(r'\s*\|\s*$', '', data)
    data = re.sub(r'\&amp\;', '&', data)
    data = re.sub(r'None', '', data)
    data = re.sub(r'^\s*\:\s*', '', data)
    data = re.sub(r'\s*\:\s*$', '', data)
    data = re.sub(r'\s*\&nbsp;\s*', '', data)
    if isinstance(data, str):
        data =  re.sub(f"[^{re.escape(string.printable)}]", "", data)
    return data

# gsheet auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gsheet-creds.json", scope)
client = gspread.authorize(creds)

# clear sheets
spreadsheet = client.open("Job Scrape Results")
for sheet in spreadsheet.worksheets():
    sheet.clear()

# global declarations 
FinalOutputList = []
Output_List = []

infos = [
    {
        'job_title_keyword': 'Web Scraping',
        'job_location': 'india',
        'exp': True,
        'match_keywords': ["python", "perl", "web scraping", "data extraction", "data manipulation", "data analysis", "automation", "selenium", "beautifulsoup", "scrapy", "regex", "pandas", "numpy", "etl", "mysql", "data cleaning", "data transformation", "code optimization", "json", "csv", "apis", "xml", "xpath", "sql", "docker", "git", "github", "headless browsers", "captcha solving", "proxy management", "ip rotation", "html", "css", "javascript", "css selectors", "web crawling", "browser automation", "api integration", "multi-threading", "asynchronous scraping", "dynamic content"]
    },
    {
        'job_title_keyword': 'Data Engineer',
        'job_location': 'india',
        'exp': False,
        'match_keywords': ["data engineer", "python", "pyspark", "spark", "sql", "aws", "azure", "gcp", "airlfow", "cloud", "snowflake", "dbt", "data build tool", "data warehousing", "date ingestion", "data ingestion", "data pipeline", "etl", "extract", "transform", "load", "databricks"]

    }
]


req = requests.Session()

con_header = {"accept":"application/json" ,"appid":"109" ,"nkparam":"cfLKV5XiEzsCnBxwGGyf35+jH3uBA0AcwWKn9eHnVB6KWXce44Fb6at/NI06sGi5bwFLY1u3sJQ4ATWTLWFvUA==" ,"priority":"u=1, i" ,"systemid":"Naukri" ,"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"}

def main():
    """Main function"""

    try:
        pid = str(os.getpid())
        print('pid:' + pid)

        for info in infos:

            Home_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(info['job_location'])}&keyword={str(info['job_title_keyword'])}&jobAge=2"

            Home_con_obj = req.get(Home_url, headers=con_header)
            print(Home_con_obj.status_code)

            Home_con = Home_con_obj.content

            # with open("Cache/Home_page.html", 'wb') as fh:
            #     fh.write(Home_con)

            # if os.path.exists("Cache/Home_page.html"):
            #     with open("Cache/Home_page.html", 'r', encoding='utf-8') as fh:
            #         Home_con = fh.read()
                
            home_json_con = json.loads(Home_con)

            if 'noOfJobs' in home_json_con:
                total_jobs = home_json_con['noOfJobs']
                total_pages = round(total_jobs / 20)
                print(total_pages)
                time.sleep(2)

                page_nums = [i for i in range(1, total_pages + 1)]
                key_info = [(i, info) for i in page_nums]

                concurrent_requests = 30

                with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                    executor.map(fetch_page, key_info)

                process_output(info)
    except Exception as e:
        print(f"Error in main function : {str(e)}")


def fetch_page(key_info):
    """Navigate through all pages and capture details"""

    try:
        # print(key_info)
        page = key_info[0]
        info = key_info[1]

        List_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(info['job_location'])}&keyword={str(info['job_title_keyword'])}&pageNo={str(page)}&jobAge=2"
        # print(List_url)

        List_con_obj = req.get(List_url, headers=con_header)
        print(f"{page}\t{List_con_obj.status_code}")

        List_con = List_con_obj.content

        # with open(f"Cache/List_page_{str(page)}.html", 'wb') as fh:
        #     fh.write(List_con)

        # if os.path.exists(f"Cache/List_page_{str(page)}.html"):
        #     with open(f"Cache/List_page_{str(page)}.html", 'r', encoding='utf') as fh:
        #         List_con = fh.read()

        json_con = json.loads(List_con)

        if 'jobDetails' in json_con:
            for job_blk in json_con['jobDetails']:
                # print(job_blk)
                name=posted_time=companyName=skills=jobDescription=experience=currency=salary=location=detail_link=''

                name = job_blk['title'] if 'title' in job_blk else ''
                posted_time = job_blk['footerPlaceholderLabel'] if 'footerPlaceholderLabel' in job_blk else ''
                companyName = job_blk['companyName'] if 'companyName' in job_blk else ''
                skills = job_blk['tagsAndSkills'] if 'tagsAndSkills' in job_blk else ''
                jobDescription = job_blk['jobDescription'] if 'jobDescription' in job_blk else ''
                experience = job_blk['experienceText'] if 'experienceText' in job_blk else ''
                currency = job_blk['currency'] if 'currency' in job_blk else ''
                detail_link = "https://www.naukri.com"+job_blk['jdURL'] if 'jdURL' in job_blk else ''
                if 'placeholders' in job_blk:
                    for placeholders_blk in job_blk['placeholders']:
                        if experience == '':
                            if placeholders_blk['type'] == 'experience':
                                experience = placeholders_blk['label']
                        if placeholders_blk['type'] == 'salary':
                            salary = placeholders_blk['label']
                        if placeholders_blk['type'] == 'location':
                            location = placeholders_blk['label']
                
                name = clean(name)
                companyName = clean(companyName)
                location = clean(location)
                skills = clean(skills)
                salary = clean(salary)
                experience = clean(experience)
                posted_time = clean(posted_time)
                currency = clean(currency)
                jobDescription = clean(jobDescription)

                output_dict = {
                    "SL NO.": None,
                    "DATE": today,
                    "NAME": name,
                    "DETAIL LINK": detail_link,
                    "COMPANY NAME": companyName,
                    "LOCATION": location,
                    "SKILLS": skills,
                    "SALARY": salary,
                    "EXPERIENCE": experience,
                    "POSTED TIME": posted_time,
                    "CURRENCY": currency,
                    "DESCRIPTION": jobDescription,
                }

                Output_List.append(output_dict)

                # with open("Raw_Output.txt", "a", encoding='utf-8') as fh:
                #     fh.write(f"{str(page)}\t{str(name)}\t{str(detail_link)}\t{str(companyName)}\t{str(location)}\t{str(skills)}\t{str(salary)}\t{str(experience)}\t{str(posted_time)}\t{str(currency)}\t{str(jobDescription)}\n")
    except Exception as e:
        print(f"Error in fetch page function : {e}")

def process_output(info):
    """Processing output"""
    
    try:
        df = pd.DataFrame(Output_List)

        df["SL NO."] = range(1, len(df) + 1)

        # remove dups
        df = df.drop_duplicates(subset=['NAME','COMPANY NAME','DESCRIPTION'])

        job_title_keyword = info['job_title_keyword']
        keywords = info['match_keywords']
        keywords_text = " ".join(keywords)

        documents = df['DESCRIPTION'].tolist() + [keywords_text]
        vectorizer = TfidfVectorizer(stop_words='english')

        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:]) 

        percentage_matches = cosine_similarities.flatten() * 100


        #sorting percentage
        df['Match_Percentage'] = percentage_matches
        df['Match_Percentage'] = df['Match_Percentage'].astype(int)
        df = df.sort_values(by='Match_Percentage', ascending=False)
        df['Match_Percentage'] = df['Match_Percentage'].apply(lambda x: f"{x:.2f}%")

        #filterout unwanted
        df = df[df['Match_Percentage'] != '0.00%']
        # df = df[df['POSTED TIME'].str.contains(r'Today|Just Now|Few Hours Ago|^1 Day Ago|^2 Days Ago|^3 Days Ago|^4 Days Ago|^5 Days Ago', case=False, na=False)]

        # resetiing index values
        df.drop('SL NO.', axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1
        df.index.name = 'SL NO.'

        #filter based on location
        df = df[df['LOCATION'].str.contains(r'chennai|remote|bangalore|bangaluru|coimbatore', case=False, na=False)]

        # writing output
        # df.to_excel("Naukri_Output.xlsx")

        # save to gsheet
        spreadsheet = client.open("Job Scrape Results")

        sheet_names = [ws.title for ws in spreadsheet.worksheets()]
        if job_title_keyword in sheet_names:
            worksheet = spreadsheet.worksheet(job_title_keyword)
        else:
            worksheet = spreadsheet.add_worksheet(title=job_title_keyword, rows=1000, cols=20)

        worksheet.clear()
        set_with_dataframe(worksheet, df)
        

        # top_n = int(len(df) * 0.10)
        # df = df.iloc[:top_n]
        # FinalOutputList.append(df.to_dict(orient='records'))
        # print(FinalOutputList)

    except Exception as e:
        print(f"Error in process output function : {e}")

if __name__ == '__main__':
    main()

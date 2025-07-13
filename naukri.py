
##### Importing required modules #####

import os
import re
import time
import warnings
import requests
import traceback
import random
import pyautogui
import json
import pandas as pd
from selenium import webdriver
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import string
warnings.filterwarnings("ignore")

today = datetime.now().strftime("%Y-%m-%d")

Cache_path = "Cache/"
if not os.path.exists(Cache_path):
    os.makedirs(Cache_path)

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

page_num=1
detail_count=1

output_list = []

info_keywords = ["Python", "Perl", "Web Scraping", "Data Extraction", "Data Manipulation", "Data Analysis", "Automation", "Selenium", "BeautifulSoup", "Scrapy", "RegEx", "Regular Expression", "Pandas", "Numpy", "Extract, Transform, Load (ETL)", "ETL", "Django", "MySQL", "Data Processing Pipelines", "Data Cleaning", "Data Transformation", "Runtime Improvement", "Automated Data Processing", "Code Optimization", "Web Technologies", "Filezilla", "JSON", "CSV", "APIs", "XML", "XPath", "Data ", "SQL", "Docker", "Git", "GitHub", "Headless Browsers", "CAPTCHA Solving", "Proxy Management", "Rate Limiting", "IP Rotation", "HTML", "CSS", "JavaScript", "XPath", "CSS Selectors", "Web Crawling", "Browser Automation", "Headless Browsers", "Scrapy Framework", "Selenium WebDriver", "BeautifulSoup Parser", "Data Extraction Techniques", "API Integration", "Scraping APIs", "Data Storage Solutions", "Database Integration", "Cloud Scraping", "Multi-threading", "Asynchronous Scraping", "Proxy Rotation", "Captcha Bypass", "Anti-Scraping Measures", "Rate Limiting Handling", "Scraping Dynamic Content", "Scraping JavaScript-rendered Content", "Web Scraping Ethics", "Web Scraping Legal Compliance"]

# header = "SL NO.\tNAME\tDETAIL LINK\tCOMPANY NAME\tSALARY\tLOCATION\tPOSTED TIME\tEASYAPPLY\tWORK MODE\tWORK TYPE\tAPPLIED COUNT\tDESCRIPTION\n"

# with open(f"Raw_Output.txt", 'w', encoding='utf-8') as fh:
#     fh.write(header)

job_title_keyword = "tata consultancy services"
job_location = "chennai"

if __name__ == '__main__':
    
    pid = str(os.getpid())
    print('pid:' + pid)

    req = requests.Session()

    con_header = {"accept":"application/json" ,"appid":"109" ,"nkparam":"cfLKV5XiEzsCnBxwGGyf35+jH3uBA0AcwWKn9eHnVB6KWXce44Fb6at/NI06sGi5bwFLY1u3sJQ4ATWTLWFvUA==" ,"priority":"u=1, i" ,"systemid":"Naukri" ,"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"}

    Home_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(job_location)}&keyword={str(job_title_keyword)}"

    Home_con_obj = req.get(Home_url, headers=con_header)
    print(Home_con_obj.status_code)

    Home_con = Home_con_obj.content

    with open("Cache/Home_page.html", 'wb') as fh:
        fh.write(Home_con)

    if os.path.exists("Cache/Home_page.html"):
        with open("Cache/Home_page.html", 'r', encoding='utf-8') as fh:
            Home_con = fh.read()
        
        home_json_con = json.loads(Home_con)

        if 'noOfJobs' in home_json_con:
            total_jobs = home_json_con['noOfJobs']
            total_pages = round(total_jobs / 20)
            print(total_pages)

            for page in range(1, total_pages + 1):

                List_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(job_location)}&keyword={str(job_title_keyword)}&pageNo={str(page)}"

                List_con_obj = req.get(List_url, headers=con_header)
                print(List_con_obj.status_code)

                List_con = List_con_obj.content

                with open(f"Cache/List_page_{str(page)}.html", 'wb') as fh:
                    fh.write(List_con)

                if os.path.exists(f"Cache/List_page_{str(page)}.html"):
                    with open(f"Cache/List_page_{str(page)}.html", 'r', encoding='utf') as fh:
                        List_con = fh.read()

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
                                "SL NO.": str(detail_count),
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

                            output_list.append(output_dict)

                            detail_count += 1

    df = pd.DataFrame(output_list)

    # remove dups
    df = df.drop_duplicates(subset=['NAME','COMPANY NAME','DESCRIPTION'])

    keywords = info_keywords

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

    #filterout 0% percentage match
    # df = df[df['Match_Percentage'] != '0.00%']

    # resetiing index values
    df.drop('SL NO.', axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    df.index.name = 'SL NO.'

    # writing output
    df.to_excel("Naukri_Output.xlsx")


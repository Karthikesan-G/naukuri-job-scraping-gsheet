from datetime import datetime
import requests, os, re, json, string, time
from concurrent.futures import ThreadPoolExecutor


today = datetime.now().strftime("%Y-%m-%d")

FinalOutputList = []
Output_List = []

req = requests.Session()

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


def fetch_page(key_info, con_header):
    """Navigate through all pages and capture details"""

    try:
        page = key_info[0]
        info = key_info[1]

        List_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(info['job_location'])}&keyword={str(info['job_title_keyword'])}&pageNo={str(page)}&jobAge=2"

        List_con_obj = req.get(List_url, headers=con_header)

        List_con = List_con_obj.content

        json_con = json.loads(List_con)

        if 'jobDetails' in json_con:
            for job_blk in json_con['jobDetails']:
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

    except Exception as e:
        print(f"Error in fetch page function : {e}")

def scrape(info, con_header):
    try:
        Home_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_key_loc&searchType=adv&location={str(info['job_location'])}&keyword={str(info['job_title_keyword'])}&jobAge=2"

        Home_con_obj = req.get(Home_url, headers=con_header)
        print(Home_con_obj.status_code)

        Home_con = Home_con_obj.content

        home_json_con = json.loads(Home_con)

        if 'noOfJobs' in home_json_con:
            total_jobs = home_json_con['noOfJobs']
            total_pages = round(total_jobs / 20)
            print(total_pages)
            time.sleep(2)

            page_nums = [i for i in range(1, total_pages + 1)]
            key_info = [(i, info) for i in page_nums]

            concurrent_requests = 5

            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                executor.map(lambda x: fetch_page(x, con_header), key_info)

    except Exception as e:
        print(f"Error in main function : {str(e)}")

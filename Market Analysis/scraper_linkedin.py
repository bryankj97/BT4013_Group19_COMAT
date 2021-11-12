#!/usr/bin/env python
# coding: utf-8

# In[8]:


# importing packages
import pandas as pd
import re

from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from IPython.core.display import clear_output
from random import randint
from requests import get
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from time import time
start_time = time()

from warnings import warn
from selenium import webdriver


# In[9]:


technologies = ["scratch", "Unity", "SAP", "Wordpress", "Swift", "Django", "Spring", "Docker", "Arduino", "Angular", "Bootstrap",
               "Laravel", "Git", "Firebase", "Flutter", "node.js", "mongodb", "Ruby", "Kotlin", "tensorflow", "Vue", "redux",
               "Selenium", "jenkins", "ajax", "typescript", "postgres", "pandas", "Scala",
               "graphql", "golang", "xcode", "flask"]
#technologies = ["sql", "django"]
url = "https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=Singapore&sortBy=DD"
no_of_jobs = 100


# In[10]:



#run this code if 1st time setup
#from webdrivermanager.chrome import ChromeDriverManager
#cdm = ChromeDriverManager()
#cdm.download_and_install()


# In[14]:


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome('C:/Users/Axel/AppData/Local/rasjani/WebDriverManager/bin/chromedriver.exe', options=options)


# In[16]:


# setting up list for job information
job_id = []
post_title = []
company_name = []
post_date = []
job_location = []
job_desc = []
level = []
emp_type = []
functions = []
industries = []
skill = []
count = 0

for topic in technologies:
    sleep(5)
    print(topic)
    url = "https://www.linkedin.com/jobs/search?keywords=" + topic + "&location=Singapore&sortBy=DD"
    driver.get(url)
    sleep(3)
    action = ActionChains(driver)
    i = 0
    while i < 3:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(10)
        i+=1
#     while i <= (no_of_jobs/25): 
#         driver.find_element_by_xpath('/html/body/main/div/section/button').click()
#         i = i + 1
#         sleep(3)
# for loop for job title, company, id, location and date posted
    pageSource = driver.page_source
    lxml_soup = BeautifulSoup(pageSource, 'lxml')

    # searching for all job containers
    job_container = lxml_soup.find('ul', class_ = 'jobs-search__results-list')
    for job in job_container.findAll('li'):

        # job title
        job_titles = job.find("h3", class_="base-search-card__title").text
        #print(job_titles)
        post_title.append(job_titles.strip())

        # linkedin job id
        job_id.append(count)
        count += 1

        # company name
        company_names = job.find("h4", class_="base-search-card__subtitle").text
        company_name.append(company_names.strip())
        skill.append(topic)

        # posting date
    #     post_dates = job.select('time')[0]['datetime']
    #     post_date.append(post_dates)


# In[ ]:


# # for loop for job description and criterias
# for x in range(1,len(job_id)):
#     print(x)
    
#     # clicking on different job containers to view information about the job
#     job_xpath = "//main/section/ul/li[{}]/div".format(x)
#     driver.find_element_by_xpath(job_xpath).click()
#     #sleep(3)
    
#     # job description
#     job_criteria_container = lxml_soup.find('div', class_ = 'show-more-less-html__markup')
#     #find all points
#     all_job_criterias = job_criteria_container.find_all("li")
#     skills = [] 
#     for listing in all_job_criterias:
#         sentence = listing.text
#         skills.append(sentence)
#     formatted_jd = ' '.join(skills)
#     job_desc.append(formatted_jd)
        
    
#     # Get job tags
#     job_info = lxml_soup.find('ul', class_ = 'description__job-criteria-list')
#     specific_info = job_info.find_all("span")
#     try:
#         print("skip")
#         level.append(specific_info[0].text.strip())
#     except IndexError:
#         print("no senior")
#         level.append("NA")
#     try:
#         print(specific_info[1].text.strip())
#         print("skip1")
        
#         emp_type.append(specific_info[1].text.strip())
#     except IndexError:
        
#         print("no employment type")
#         emp_type.append("NA")
#     try:
#         print("skip2")
#         functions.append(specific_info[2].text.strip())
#     except IndexError:
        
#         print("no job function")
#         functions.append("NA")
#     try:
#         print("skip3")
#         industries.append(specific_info[3].text.strip())
#     except IndexError:
        
#         print("no industry")
#         industries.append("NA")


# In[ ]:


# print(post_date)
# print(len(post_date))
# print(company_name)
# print(len(company_name))
# print(post_title)
# print(len(post_title))
# print(job_desc)
# print(len(job_desc))
# print(level)
# print(len(level))
# print(emp_type)
# print(len(emp_type))
# print(functions)
# print(len(functions))
# print(industries)
# print(len(industries))


# In[17]:


# creating a dataframe
job_data = pd.DataFrame({
'Post': post_title,
'Company Name': company_name,
'Skill': skill
# 'Description': job_desc,
# 'Level': level,
# 'Type': emp_type,
# 'Function': functions,
# 'Industry': industries
})

# cleaning description column
#job_data['Description'] = job_data['Description'].str.replace('\n',' ')

#print(job_data.info())
job_data.head()


# In[18]:


job_data.to_csv("scraped_linkedin.csv")


# In[ ]:





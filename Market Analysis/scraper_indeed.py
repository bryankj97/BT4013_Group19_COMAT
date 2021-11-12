#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


#add url here
#url = "https://sg.indeed.com/jobs?q=sql&start="
#declare no. of jobs to scrape in 10s
technologies = ["scratch", "Unity", "SAP", "Wordpress", "Swift", "Django", "Spring", "Docker", "Arduino", "Angular", "Bootstrap",
               "Laravel", "Git", "Firebase", "Flutter", "node.js", "mongodb", "Ruby", "Kotlin", "tensorflow", "Vue", "redux",
               "Selenium", "jenkins", "ajax", "typescript", "postgres", "pandas", "Scala",
               "graphql", "golang", "xcode", "flask"]
#technologies = ["sql", "django"]
#no_of_jobs = 20
numberOfPages = 7 


# In[3]:



#run this code if 1st time setup
#from webdrivermanager.chrome import ChromeDriverManager
#cdm = ChromeDriverManager()
#cdm.download_and_install()


# In[4]:


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome('C:/Users/Axel/AppData/Local/rasjani/WebDriverManager/bin/chromedriver.exe', options=options)
#driver.get(url)
#sleep(3)
#action = ActionChains(driver)


# In[5]:


post_title = []
company_name = []
skill = []
for topic in technologies:
    url = "https://sg.indeed.com/jobs?q=" + topic + "&start="

    for ten in range(numberOfPages):
        #add search query
        searchurl = url + str(ten*10)
        print(searchurl)
        #open url
        driver.get(searchurl)
        sleep(3)
        action = ActionChains(driver)
        # parsing the visible webpage
        pageSource = driver.page_source
        lxml_soup = BeautifulSoup(pageSource, 'lxml')
        # searching for all job containers
        job_container = lxml_soup.find('div', class_ = 'mosaic-provider-jobcards')
        for job in job_container:
            #print("new!")
            #print(job)
            #find job title
            job_header = job.find('h2')
            #print(job_header)
            try:
                job_title = job_header.find('span', title=True).text
            except:
                continue
            #print(job_title)
            post_title.append(job_title.strip())
            #find company
            company_header = job.find('span', class_ = 'companyName')
            try: 
                company_title = company_header.find('a').text
            except:
                try:
                    company_title = company_header.text
                except:
                    company_title = "None"
            #print(company_title)
            company_name.append(company_title.strip())
            skill.append(topic)


# In[6]:


job_data = pd.DataFrame({'Job Title': post_title,
'Company Name': company_name, 
'Skill': skill
})

print(job_data.info())
job_data


# In[7]:


job_data.to_csv("scraped.csv")


# In[ ]:





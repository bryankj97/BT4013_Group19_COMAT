import streamlit as st
import pandas as pd
import os
import test
import streamlit.components.v1 as components
import pickle
from copy import deepcopy
from clustering_utils import *
from visualization import *
from master_components import *

# def firstLoader(tms):
#     with open('Streamlit/pkl/title_to_code_mapping.pkl', 'rb') as f:
#         course_code_mapper = pickle.load(f)
#     tms_dataset = pd.DataFrame()
#     new_tms_dataset = add_data(
#         tms, tms_dataset, course_code_mapper, is_csv=False)
#     processed_dataset = process_data(new_tms_dataset)
#     # 3. Recluster and store down labels
#     cluster_dict = cluster(processed_dataset)
#     labels = cluster_dict["Cluster"]
#     st.write("List of Course Clusters predicted by the model")
#     st.write(cluster_dict.head())
#     st.success("You model has been updated with the latest information successfully!")
#     st.info("Please proceed to view the course information at the Select Objective corner.")
#     pickle.dump(labels, open("Streamlit/pkl/labels.pkl", 'wb'))
#     # 4. If all cases complete, store down the new data
#     pickle.dump(new_tms_dataset, open("Streamlit/pkl/dataset.pkl", 'wb'))

def updateModel(tms):
    with open('Streamlit/pkl/title_to_code_mapping.pkl', 'rb') as f:
        course_code_mapper = pickle.load(f)
    # # 1. Trim the dataset (in TMS format) and save down
    new_tms_dataset = trim_data(tms, course_code_mapper, is_csv=False)
    # 2. Process data
    processed_dataset = process_data(new_tms_dataset)
    # 3. Recluster and store down labels
    cluster_dict = cluster(processed_dataset)
    labels = cluster_dict["Cluster"]
    st.write("List of Course Clusters predicted by the model")
    st.write(cluster_dict.head())
    st.success("You model has been updated with the latest information successfully!")
    st.info("Please proceed to view the course information at the Select Objective corner.")

    # 4. If all cases complete, store down the new data
    pickle.dump(labels, open("Streamlit/pkl/labels.pkl", 'wb'))
    pickle.dump(tms, open("Streamlit/pkl/clean_dataset.pkl", 'wb'))
    pickle.dump(new_tms_dataset, open("Streamlit/pkl/dataset.pkl", 'wb'))
    pickle.dump(cluster_dict, open("Streamlit/pkl/cluster_dict.pkl", 'wb'))
    pickle.dump(processed_dataset, open("Streamlit/pkl/processed_dataset.pkl", 'wb'))
    return tms

def retrieveData():
    with open('Streamlit/pkl/cluster_dict.pkl', 'rb') as f:
        cluster_dict = pickle.load(f)
    with open('Streamlit/pkl/processed_dataset.pkl', 'rb') as f:
        processed_dataset = pickle.load(f)
    with open('Streamlit/pkl/dataset.pkl', 'rb') as f:
        tms_dataset = pickle.load(f)
    with open('Streamlit/pkl/course_details.pkl', 'rb') as f:
        course_details = pickle.load(f)
    with open('Streamlit/pkl/clean_dataset.pkl', 'rb') as f:
        clean_dataset = pickle.load(f)
    
    return processed_dataset, tms_dataset, cluster_dict, course_details, clean_dataset

def dumpCourseData(course_details, course_categories):
    pickle.dump(course_details, open("Streamlit/pkl/course_details.pkl", 'wb'))
    pickle.dump(course_categories, open("Streamlit/pkl/course_categories.pkl", 'wb'))

def studentDemo(course_code, cluster_dict, processed_dataset, tms_data):
    course_cluster = get_course_cluster(course_code, cluster_dict)[0]
    cluster_df = get_courses_in_cluster(course_cluster, cluster_dict["Cluster"], processed_dataset)
    student_by_cluster = get_students_from_cluster(cluster_df, tms_data)

    st.markdown('<h4>Average Education Level (Median)</h4>', unsafe_allow_html=True)
    eduPlot=plot_education(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(eduPlot)
    st.markdown('<h4>Average Salary</h4>', unsafe_allow_html=True)
    salaryPlot=plot_salary(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(salaryPlot)
    st.markdown('<h4>Average Age</h4>', unsafe_allow_html=True)
    agePlot=plot_age(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(hv.render(agePlot[0], backend='bokeh'))
    st.bokeh_chart(hv.render(agePlot[1], backend='bokeh'))
    st.markdown('<h4>Race, Gender & Nationality Composition</h4>', unsafe_allow_html=True)
    RNGtabs = demographics(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(RNGtabs)
    st.markdown('<h4>Top Company Sectors Within Cluster</h4>', unsafe_allow_html=True)
    sectors = get_sectors(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(sectors)


def courseDemo(course_code, cluster_dict, processed_dataset, tms_data, course_details):
    course_cluster = get_course_cluster(course_code, cluster_dict)[0]
    cluster_df = get_courses_in_cluster(course_cluster, cluster_dict["Cluster"], processed_dataset)
    student_by_cluster = get_students_from_cluster(cluster_df, tms_data)
    st.markdown('<h4>Average Course Expenditure/Revenue</h4>', unsafe_allow_html=True)
    revPlot=average_course_revenue_cluster(course_cluster, course_code, student_by_cluster, tms_data, course_details)
    st.bokeh_chart(revPlot)
    st.markdown('<h4>Average Enrollment Over Time for Course</h4>', unsafe_allow_html=True)
    enrollPlot=plot_enrolment_wrapper(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(enrollPlot)
    st.markdown('<h4>Enrollment Breakdown for Courses in Cluster</h4>', unsafe_allow_html=True)
    diffPlot = plot_enrollment_difference(course_cluster, course_code, student_by_cluster, tms_data)
    st.bokeh_chart(diffPlot)

def showClustersByCourse(course_code, cluster_dict, processed_dataset, tms_data, course_details):
    if course_code:
        if selected == "Student Demographics":
            st.subheader(selected)
            studentDemo(course_code, cluster_dict, processed_dataset, tms_data)
        else:
            st.subheader(selected)
            courseDemo(course_code, cluster_dict, processed_dataset, tms_data, course_details)


def app():
    changeCSS()
    select_options = ["Train Course Clustering Model",
                      "Course Information"]
    error = st.empty()
    with st.sidebar.header('Select Objective'):
        choice = st.sidebar.selectbox(
            "What do you want to do?", options=select_options)

    if choice == "Train Course Clustering Model":
        with st.sidebar.header('Upload TMS data'):
            tms_file = st.sidebar.file_uploader(
                "Upload your file", type=["csv"], key=1)
            tms = None
            if tms_file is not None:
                try:
                    tms = pd.read_csv(tms_file)
                except:
                    error.error("Please ensure that you are uploading the correct dataset. File Expected Example for TMS data: TMS- -PrincessTrainees-2014-2020(Apr)_forDAprjUse_11May20-P.csv")

        with st.sidebar.header('Upload Course Details data'):
            course_file = st.sidebar.file_uploader(
                "Upload your file", type=["xlsx", "xls"], key=2)
            course_details, course_categories = None, None
            if course_file is not None:
                try:
                    course_details = pd.read_excel(course_file, sheet_name=1, engine="openpyxl")
                    course_categories = pd.read_excel(course_file, sheet_name='WBS', engine="openpyxl")
                except:
                    error.error("Please ensure that you are uploading the correct dataset. File Expected Example for Course Details data: TMS_Course_Code_Princess_28May20_pris_Group_same_course_23Jun20.xlsx")
                    
        if tms is not None and course_details is not None and course_categories is not None:         
            if st.sidebar.button("Press to Train Model"):
                try:
                    st.header(choice)
                    tms = updateModel(tms)
                    dumpCourseData(course_details, course_categories)
                except:
                    error.error("Please ensure that you are uploading the correct dataset. File Expected Example for TMS data: TMS- -PrincessTrainees-2014-2020(Apr)_forDAprjUse_11May20-P.csv.")
            else:
                showTrainState()
        else:
            st.info("Please upload the relevant dataset on the side to continue..")
            showEmptyState()
            
    elif choice == "Course Information" :
        processed_dataset, tms_data, cluster_dict, course_details, clean_dataset = retrieveData()
        global selected
        select_demo_options = ["Student Demographics", "Course Demographics"]
        st.header(choice)

        courseform = st.form("Please fill in the form")
        course_code = courseform.text_input("Enter a Course Code:")
        selected = courseform.selectbox(
            "Filter", options=select_demo_options, index=0)
        coursesubmitted = courseform.form_submit_button("Go")
        if coursesubmitted:
            if len(course_code) == 0:
                courseform.error("Please fill up all the fields")
            else:
                try:
                    showClustersByCourse(course_code, cluster_dict, processed_dataset, clean_dataset, course_details)
                except:
                    courseform.error("Please fill in the correct course code")
        else:
            showEmptySearch()

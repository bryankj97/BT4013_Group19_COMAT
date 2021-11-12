import pandas as pd
import pickle
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import streamlit as st

def cluster(data):
    """
    Performs clustering of courses through removal of outliers, followed by a 
    optimised KNN model to split courses into 6 distinct clusters based on
    customer demographic
    """
    df_scaled = scale(data)
    pca_1 = get_pca_data(df_scaled)
    kmeans_1 = KMeans(n_clusters=2)
    kmeans_1.fit(pca_1)
    labels = kmeans_1.predict(pca_1) # before removing outliers

    # Extract majority class
    result = {}
    for i in range(len(labels)):
        if labels[i] == 0:
            index = data.iloc[i].name
            result[index] = data.iloc[i].to_numpy()       
    final_df = pd.DataFrame.from_dict(result, orient='index', columns=list(data.columns))

    df_normalized = normalize(final_df)
    pca_2 = get_pca_data(df_normalized)
    kmeans_2 = KMeans(n_clusters=6)
    kmeans_2.fit(pca_2)

    final_df["Cluster"] = kmeans_2.predict(pca_2)
    # Final clustering labels
    return final_df

def trim_data(data, course_code_mapper, is_csv=True):
    """
    To add data to the existing dataset from .csv files

    Essential Columns:
    - Name (As in NRIC)
    - Start Date
    - Course Reference Number
    - Company Sector
    - Salary Range
    - Education Level 
    """
    data = pd.read_csv(data) if is_csv else data
    #Perform mapping if needed
    data['CourseCode'] = data['Course Reference Number'].apply(lambda x: course_code_mapper[x] if x in course_code_mapper \
                                                          else x)
    columns = ['CourseCode', 'Company Sector', 'Salary Range', 'Education Level']
    data = data[columns]

    return data

def process_data(user_course_df):
    """
    Perform processing on new data set, with new data entries, through one-hot encoding and aggregations
    """
    # One-hot encode data
    one_hot = pd.get_dummies(user_course_df['Company Sector'], prefix="industry")
    user_course_df = user_course_df.drop('Company Sector',axis = 1)
    user_course_df = user_course_df.join(one_hot)

    one_hot_salary = pd.get_dummies(user_course_df['Salary Range'], prefix="salary")
    user_course_df = user_course_df.drop('Salary Range',axis = 1)
    user_course_df = user_course_df.join(one_hot_salary)

    one_hot_education = pd.get_dummies(user_course_df['Education Level'], prefix="education")
    user_course_df = user_course_df.drop('Education Level',axis = 1)
    user_course_df = user_course_df.join(one_hot_education)
    
    req_col = ['CourseCode',
             'industry_Association',
             'industry_COMAT',
             'industry_Commercial',
             'industry_Education/Training',
             'industry_Govt',
             'industry_Govt-Defense',
             'industry_Govt-Education',
             'industry_Govt-Overseas',
             'industry_Hospital/Medical',
             'industry_Personal',
             'industry_STEE',
             'salary_$1000 - $1499 / mth',
             'salary_$1500 - $2999 / mth',
             'salary_$750 - $999 / mth',
             'salary_Below $750 / mth',
             'salary_Over $3000 / mth',
             "education_'A' Levels / ITC or equivalent",
             "education_'O' Levels / NTC-2 or equivalent",
             'education_Degree & above',
             'education_Diploma or equivalent',
             'education_Others',
             'education_PSLE below',
             'education_Postgraduate',
             "education_Sec. Edn. / NTC-3 (< 'O' Levels)"]
    
    # Only get required columns
    user_course_df = user_course_df[req_col]
    
    # Group by
    user_course_df = user_course_df.groupby(['CourseCode']).sum()
    
    return user_course_df

def scale(user_course_df_t):
    """
    Perform scaling of data
    """
    scaler = MinMaxScaler()
    # transform data
    scaled = scaler.fit_transform(user_course_df_t)
    df_scaled = pd.DataFrame(scaled,index = user_course_df_t.index, columns = user_course_df_t.columns)
    return df_scaled

def normalize(user_course_df_t):
    """
    Perform normalization of data
    """
    normalized = preprocessing.normalize(user_course_df_t)
    df_normalized = pd.DataFrame(normalized,index = user_course_df_t.index, columns = user_course_df_t.columns)
    return df_normalized

def get_pca_data(data, n_components=0.95):
    """
    Perform PCA on data
    """
    pca = PCA(n_components = n_components)
    pc = pca.fit_transform(data)
    num_of_components = len(pc[0])
    columns = []
    for i in range(1, num_of_components + 1):
        columns.append(f'principal component {i}')
    pc_df = pd.DataFrame(data = pc
                 , columns = columns)
    return pc_df

def get_course_cluster(course_name, user_course_df):
    selected_df = user_course_df.loc[[course_name]]
    return selected_df["Cluster"]

def get_courses_in_cluster(cluster, proba_lists, user_course_df):
    result = {}
    for i in range(len(proba_lists)):
        if proba_lists[i] == cluster:
            index = user_course_df.iloc[i].name
            result[index] = user_course_df.iloc[i].to_numpy()
    return pd.DataFrame.from_dict(result, orient='index', columns=list(user_course_df.columns))
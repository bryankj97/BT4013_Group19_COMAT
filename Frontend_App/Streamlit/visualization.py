from bokeh.models import ColumnDataSource, CustomJS, Range1d, Select, Tabs, Panel, TableColumn, DataTable, Div
from bokeh.models.annotations import Title
from bokeh.plotting import figure, output_notebook, show
from bokeh.models import HoverTool
from bokeh.layouts import column, row
from bokeh.palettes import Category10
from bokeh.transform import cumsum
from tqdm import tqdm
from bokeh.io import curdoc
import holoviews as hv
from holoviews import opts
from math import pi
import pandas as pd
import numpy as np
import streamlit as st
hv.extension('bokeh', 'matplotlib')

# general function to get clusters
# master_df: cleaned user_df


def get_students_from_cluster(cluster, master_df):
    res = pd.DataFrame()
    for course in cluster.index:
        temp = master_df.loc[master_df['Course Reference Number'] == course]
        res = pd.concat([res, temp])
    return res


def extract_data(tab, df, student_df, selected_course):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]
    df_cluster = df_cluster[tab].value_counts()
    df_course = df_course[tab].value_counts()
    cluster_data = df_cluster.to_dict()
    ind_data = df_course.to_dict()
    cluster_data = pd.Series(cluster_data).reset_index(
        name='value').rename(columns={'index': 'key'})
    cluster_data['percent'] = round(
        cluster_data['value']/cluster_data['value'].sum()*100)
    cluster_data['angle'] = cluster_data['value'] / \
        cluster_data['value'].sum() * 2*pi
    if len(cluster_data) == 2:
        cluster_data['color'] = [Category10[3][0], Category10[3][1]]
    else:
        cluster_data['color'] = Category10[len(cluster_data)]
    ind_data = pd.Series(ind_data).reset_index(
        name='value').rename(columns={'index': 'key'})
    ind_data['percent'] = round(ind_data['value']/ind_data['value'].sum()*100)
    ind_data['angle'] = ind_data['value']/ind_data['value'].sum() * 2*pi
    if len(ind_data) == 1:
        ind_data['color'] = Category10[3][0]
    elif len(ind_data) == 2:
        ind_data['color'] = [Category10[3][0], Category10[3][1]]
    else:
        ind_data['color'] = Category10[len(ind_data)]
    return cluster_data, ind_data


def get_average_education(df, student_df, selected_course):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]
    df_cluster = df_cluster[['Education Level', 'Gender']]
    df_course = df_course[['Education Level', 'Gender']]
    df_cluster = df_cluster.fillna("Others")
    df_course = df_course.fillna("Others")
    df_cluster = df_cluster.groupby(
        by=['Education Level', "Gender"]).size().reset_index()
    df_course = df_course.groupby(
        by=['Education Level', "Gender"]).size().reset_index()
    df_cluster.columns = [*df_cluster.columns[:-1], 'No. of Students']
    df_course.columns = [*df_course.columns[:-1], 'No. of Students']
    df_cluster["Education Level"] = df_cluster["Education Level"].apply(
        lambda x: "'A' Levels / ITC" if x == "'A' Levels / ITC or equivalent" else x)
    df_cluster["Education Level"] = df_cluster["Education Level"].apply(
        lambda x: "'O' Levels / NTC-2" if x == "'O' Levels / NTC-2 or equivalent" else x)
    df_cluster["Education Level"] = df_cluster["Education Level"].apply(
        lambda x: "Sec. Edn. / NTC-3" if x == "Sec. Edn. / NTC-3 (< 'O' Levels)" else x)
    df_cluster["Education Level"] = df_cluster["Education Level"].apply(
        lambda x: "Diploma" if x == "Diploma or equivalent" else x)
    df_course["Education Level"] = df_course["Education Level"].apply(
        lambda x: "'A' Levels / ITC" if x == "'A' Levels / ITC or equivalent" else x)
    df_course["Education Level"] = df_course["Education Level"].apply(
        lambda x: "'O' Levels / NTC-2" if x == "'O' Levels / NTC-2 or equivalent" else x)
    df_course["Education Level"] = df_course["Education Level"].apply(
        lambda x: "Sec. Edn. / NTC-3" if x == "Sec. Edn. / NTC-3 (< 'O' Levels)" else x)
    df_course["Education Level"] = df_course["Education Level"].apply(
        lambda x: "Diploma" if x == "Diploma or equivalent" else x)
    education_dict = {"Others": 0,
                      "PSLE below": 1,
                      "Sec. Edn./NTC-3": 2,
                      "O' Levels/NTC-2": 3,
                      "'A' Levels/ITC": 4,
                      "Diploma": 5,
                      "Degree": 6,
                      "Postgraduate": 7}
    df_cluster = df_cluster.sort_values(
        by='Education Level', key=lambda x: x.map(education_dict))
    df_course = df_course.sort_values(
        by='Education Level', key=lambda x: x.map(education_dict))
    return df_cluster, df_course


def get_average_salary(df, student_df, selected_course):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]
    df_cluster = df_cluster["Salary Range"].value_counts()
    df_course = df_course["Salary Range"].value_counts()
    return df_cluster, df_course


def plot_education(cluster_num, selected_course, cluster, student_df, width_=1000, height_=500):
    cluster_df, course_df = get_average_education(
        cluster, student_df, selected_course)

    def load_symbol(symbol, title, df_):
        df = None
        if symbol != "Total":
            df = df_[df_['Gender'] == symbol]
        else:
            df = df_
        columns = df['Education Level'].drop_duplicates().to_list()
        tops = df.groupby("Education Level")[
            'No. of Students'].agg('sum').to_list()
        p_bar = figure(plot_height=350, plot_width=width_, title=title,
                       tools="hover,pan,wheel_zoom,box_zoom,reset,save", tooltips=[("Education Level", "@x"), ("Number of Students", "@top")], x_range=columns)
        p_bar.vbar(x=columns, top=tops, width=0.9)
        return p_bar

    male_bar_clust = load_symbol(
        "Male", "Education Level (Male): Cluster {}".format(cluster_num), cluster_df)
    male_bar_ind = load_symbol(
        "Male", "Education Level (Male): Course {}".format(selected_course), course_df)
    female_bar_clust = load_symbol(
        "Female", "Education Level (Female): Cluster {}".format(cluster_num), cluster_df)
    female_bar_ind = load_symbol(
        "Female", "Education Level (Female): Course {}".format(selected_course), course_df)
    total_bar_clust = load_symbol(
        "Total", "Education Level (Total): Cluster {}".format(cluster_num), cluster_df)
    total_bar_ind = load_symbol(
        "Total", "Education Level (Total): Course {}".format(selected_course), course_df)
    #layout = column(total_bar,male_bar,female_bar)
    return Tabs(tabs=[Panel(child=column(total_bar_clust, total_bar_ind), title="Total"),
                      Panel(child=column(male_bar_clust,
                                         male_bar_ind), title="Male"),
                      Panel(child=column(female_bar_clust, female_bar_ind), title="Female")])


def plot_salary(cluster_num, selected_course, cluster, student_df, width_=1000, height_=900):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        cluster['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]
    df_cluster = df_cluster["Salary Range"].value_counts()
    df_course = df_course["Salary Range"].value_counts()

    cluster_columns = df_cluster.index.to_list()
    cluster_tops = df_cluster.to_list()
    course_columns = df_course.index.to_list()
    course_tops = df_course.to_list()
    p_bar_cluster = figure(plot_height=350, plot_width=int(width_/2), title="Salary Range: Cluster {}".format(cluster_num),
                           tools="hover,pan,wheel_zoom,box_zoom,reset,save", tooltips=[("Salary Range", "@x"), ("Number of Students", "@top")], x_range=cluster_columns)
    p_bar_cluster.vbar(x=cluster_columns, top=cluster_tops, width=0.9)
    p_bar_course = figure(plot_height=350, plot_width=int(width_/2), title="Salary Range: Course {}".format(selected_course),
                          tools="hover,pan,wheel_zoom,box_zoom,reset,save", tooltips=[("Salary Range", "@x"), ("Number of Students", "@top")], x_range=course_columns)
    p_bar_course.vbar(x=course_columns, top=course_tops, width=0.9)

    return Tabs(tabs=[Panel(child=row(p_bar_cluster, p_bar_course), title="Salary Range of Students")])


def plot_age(cluster_num, selected_course, cluster, student_df, width_=1000, height_=500):
    # get histogram of age
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        cluster['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]

    df_cluster['Age'] = df_cluster['Date of Birth'].apply(
        lambda x: int(x[-2:]))
    df_course['Age'] = df_course['Date of Birth'].apply(lambda x: int(x[-2:]))
    df_cluster['Age'] = df_cluster['Age'].apply(
        lambda x: x if x <= 21 else 121 - x)
    df_course['Age'] = df_course['Age'].apply(
        lambda x: x if x <= 21 else 121 - x)
    dict_cluster = df_cluster['Age'].value_counts().to_dict()
    dict_course = df_course['Age'].value_counts().to_dict()
    dict_cluster = sorted(dict_cluster.items(),
                          key=lambda x: x[0], reverse=True)
    dict_course = sorted(dict_course.items(), key=lambda x: x[0], reverse=True)
    output_cluster = []
    output_course = []
    while dict_cluster:
        temp = dict_cluster[-1]
        if output_cluster:
            if output_cluster[-1][0] != temp[0] - 1:
                output_cluster.append((output_cluster[-1][0]+1, 0))
            else:
                output_cluster.append(temp)
                dict_cluster.pop()
        else:
            output_cluster.append(temp)
            dict_cluster.pop()
    while dict_course:
        temp = dict_course[-1]
        if output_course:
            if output_course[-1][0] != temp[0] - 1:
                output_course.append((output_course[-1][0]+1, 0))
            else:
                output_course.append(temp)
                dict_course.pop()
        else:
            output_course.append(temp)
            dict_course.pop()

    cluster_values = [x[1] for x in output_cluster]
    course_values = [x[1] for x in output_course]
    cluster_ages = [x[0] for x in output_cluster]
    course_ages = [x[0] for x in output_course]
    cluster_max = max(cluster_values)
    course_max = max(course_values)
    cluster_histogram = hv.Histogram((cluster_ages, cluster_values), extents=(
        None, None, len(cluster_ages), cluster_max+2))
    course_histogram = hv.Histogram((course_ages, course_values), extents=(
        None, None, len(course_ages), course_max+2))
    cluster_histogram = cluster_histogram.options(
        xlabel='Age', ylabel='Number of Users', title='Age of Students: Cluster: {}'.format(cluster_num))
    course_histogram = course_histogram.options(
        xlabel='Age', ylabel='Number of Users', title='Age of Students: Course: {}'.format(selected_course))
    hover = HoverTool(
        tooltips=[("Age", "@x"), ("Number of Students", "@Frequency")])
    cluster_histogram.opts(tools=[hover], width=int(width_/2), height=height_)
    course_histogram.opts(tools=[hover], width=int(width_/2), height=height_)
    # get summary statistics
    cluster_mode = cluster_ages[cluster_values.index(max(cluster_values))]
    course_mode = course_ages[course_values.index(max(course_values))]
    stats_df = pd.DataFrame({"Metric": ["Cluster {} Mode".format(cluster_num), "Course {} Mode".format(selected_course)],
                             "Age": [cluster_mode, course_mode],
                             "Number of Students": [cluster_max, course_max]})

    def hide_index(plot, element):
        plot.handles['table'].index_position = None
    table = hv.Table(stats_df).opts(hooks=[hide_index], height=100)

    return [(cluster_histogram + course_histogram).opts(opts.Histogram(axiswise=True)), table]


def pie_plot(cluster_num, tab, cluster_data, ind_data, ind_course, width_=500, height_=400):
    curdoc().clear()
    # fix the y_range to be the same for two lines
    p = figure(plot_height=height_, title="{}: Cluster {}".format(tab, cluster_num),
               tools="hover,pan,wheel_zoom,box_zoom,reset,save", tooltips="@key: @percent%", x_range=(-0.5, 1.0), plot_width=width_)
    p_i = figure(plot_height=height_, title="{}: Course {}".format(tab, ind_course),
                 tools="hover,pan,wheel_zoom,box_zoom,reset,save", tooltips="@key: @percent%", x_range=(-0.5, 1.0), plot_width=width_)
    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='key', source=cluster_data)
    p_i.wedge(x=0, y=1, radius=0.4,
              start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
              line_color="white", fill_color='color', legend_field='key', source=ind_data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    p_i.axis.axis_label = None
    p_i.axis.visible = False
    p_i.grid.grid_line_color = None
    layout = row(p, p_i)
    return layout


def demographics(cluster_num, selected_course, cluster, student_df, width_=1000, height_=500):
    nat_cluster_data, nat_ind_data = extract_data(
        "Nationality ", cluster, student_df, selected_course)
    gen_cluster_data, gen_ind_data = extract_data(
        "Gender", cluster, student_df, selected_course)
    race_cluster_data, race_ind_data = extract_data(
        "Race", cluster, student_df, selected_course)

    race_plot = pie_plot(cluster_num, "Race Demographic",
                         race_cluster_data, race_ind_data, selected_course)
    gender_plot = pie_plot(cluster_num, "Gender Demographic",
                           gen_cluster_data, gen_ind_data, selected_course)
    nationality_plot = pie_plot(
        cluster_num, "Nationality Demographic", nat_cluster_data, nat_ind_data, selected_course)
    tabs = Tabs(tabs=[Panel(child=gender_plot, title="Gender"),
                      Panel(child=race_plot, title="Race"),
                      Panel(child=nationality_plot, title="Nationality")])
    return tabs


def get_sectors(cluster_num, selected_course, df, student_df, width_=1000):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    df_course = df_cluster[df_cluster["CourseCode"] == selected_course]
    df_cluster = df_cluster['Company Sector'].value_counts(
    ).sort_values(ascending=False)
    df_cluster = pd.DataFrame(
        {'Sector': df_cluster.index, 'Number of Students': df_cluster.values})
    df_cluster['Percentage'] = round(
        (df_cluster['Number of Students']/df_cluster['Number of Students'].sum())*100, 1)
    df_cluster['Percentage'] = df_cluster["Percentage"].apply(
        lambda x: str(x)+"%")
    df_course = df_course['Company Sector'].value_counts(
    ).sort_values(ascending=False)
    df_course = pd.DataFrame(
        {'Sector': df_course.index, 'Number of Students': df_course.values})
    df_course['Percentage'] = round(
        (df_course['Number of Students']/df_course['Number of Students'].sum())*100, 1)
    df_course['Percentage'] = df_course["Percentage"].apply(
        lambda x: str(x)+"%")
    Columns_cluster = [TableColumn(field=Ci, title=Ci)
                       for Ci in df_cluster.columns]
    Columns_course = [TableColumn(field=Ci, title=Ci)
                      for Ci in df_course.columns]
    data_table_cluster = DataTable(
        columns=Columns_cluster, source=ColumnDataSource(df_cluster), width=int(width_/2))
    data_table_course = DataTable(
        columns=Columns_course, source=ColumnDataSource(df_course), width=int(width_/2))

    title1 = Div(text='<p style="text-align: center">' +
                 "Top Sectors in Cluster: {}".format(cluster_num) + '</p>')
    title2 = Div(text='<p style="text-align: center">' +
                 "Top Sectors in Course: {}".format(selected_course) + '</p>')

    layout = Tabs(tabs=[Panel(child=row(column(title1, data_table_cluster),
                                        column(title2, data_table_course)), title="Top Sectors of Students")])
    return layout


#######################
# COURSE DEMOGRAPHICS #
#######################

# run function after u run get_students_in_cluster()
def average_course_revenue_cluster(cluster_num, selected_course, cluster, student_df, course_df, width_=1000):
    curdoc().clear()
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        cluster['Email Address'])]
    course_ref = df_cluster[df_cluster['CourseCode'] ==
                            selected_course]['Course Reference Number'].to_list()[0]
    courses_count = df_cluster['Course Reference Number'].value_counts(
    ).to_dict()
    count = 0
    total = 0
    courses = []
    revenue_course = []
    price_per_course = []
    amt_taken = []
    for course in courses_count.keys():
        count += int(courses_count[course])
        try:
            cost = int(course_df[course_df['Code'] ==
                                 course].PerPaxFee.to_list()[0])
            courses.append(course)
            revenue_course.append(courses_count[course]*cost)
            price_per_course.append(cost)
            amt_taken.append(courses_count[course])
            total += courses_count[course]*cost
        except:
            continue
    df_course_revenue = pd.DataFrame({"Course": courses,
                                      "Revenue (S$)": revenue_course,
                                      "Price per Course (S$)": price_per_course,
                                      "Number of Times Course Taken": amt_taken})
    df_summary = pd.DataFrame({"Metric": ["Average Revenue per course for cluster {}".format(cluster_num),
                                          "Revenue from selected course: {}".format(selected_course)],
                               "Revenue (S$)": [round(total/count, 2), df_course_revenue[df_course_revenue['Course'] == course_ref]['Revenue (S$)'].to_list()[0]]})
    df_course_detail = pd.DataFrame(
        df_course_revenue[df_course_revenue['Course'] == course_ref])
    Columns_cluster = [TableColumn(field=Ci, title=Ci)
                       for Ci in df_course_revenue.columns]
    Columns_course = [TableColumn(field=Ci, title=Ci)
                      for Ci in df_summary.columns]
    Columns_course_detail = [TableColumn(
        field=Ci, title=Ci) for Ci in df_course_detail.columns]
    data_table_cluster = DataTable(columns=Columns_cluster, source=ColumnDataSource(
        df_course_revenue),selectable=True, width=width_, height=300)
    data_table_course = DataTable(columns=Columns_course, source=ColumnDataSource(
        df_summary), width=width_, height=100)
    data_table_course_detail = DataTable(columns=Columns_course_detail, source=ColumnDataSource(
        df_course_detail), width=width_, height=100)
    title1 = Div(text='<p style="text-align: center">' +
                 "Top Courses in Cluster: {}".format(cluster_num) + '</p>')
    title2 = Div(text='<p style="text-align: center">Top Courses summary</p>')
    title3 = Div(text='<p style="text-align: center">' +
                 "Revenue Detail for Course: {}".format(selected_course) + '</p>')

    layout = Tabs(tabs=[Panel(child=column(column(title1, data_table_cluster),
                                           column(title2, data_table_course),
                                           column(title3, data_table_course_detail)), title="Course Revenue of Sector")])

    return layout


def get_enrolment(cluster_num, selected_course, df, student_df, time_param='Year'):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    temp = df_cluster[['Start Date', 'CourseCode']]
    temp = temp.dropna()
    if time_param == "Year":
        temp['Date'] = temp['Start Date'].apply(
            lambda x: str(pd.to_datetime(x).year))
    else:
        temp['Date'] = temp['Start Date'].apply(
            lambda x: str(pd.to_datetime(x).to_period('M')))
    temp = temp.drop('Start Date', 1)
    temp = temp.groupby(['CourseCode', 'Date']).size().reset_index()
    course = temp[temp['CourseCode'] == selected_course]
    cluster = temp.groupby('Date').size().reset_index()
    course = course[['Date', 0]]
    for date in cluster['Date'].to_list():
        if course[course['Date'] == date].empty:
            course = course.append({"Date": date, 0: 0}, ignore_index=True)
    return course, cluster


def plot_enrolment(cluster_num, selected_course, df, student_df, time_param='Year', width_=1000, height_=600):
    course, cluster = get_enrolment(
        cluster_num, selected_course, df, student_df, time_param)
    x = cluster['Date'].to_list()

    course_y = course[0].to_list()
    cluster_y = cluster[0].to_list()

    p = figure(x_axis_label=time_param,
               y_axis_label="Number of Students Enrolled",
               tools="hover,pan,wheel_zoom,box_zoom,reset,save",
               tooltips=[(time_param, "@x"), ("Enrolment", "@y")],
               height=height_, width=width_,
               x_range=x)
    p.xaxis.major_label_orientation = "vertical"

    p.line(x, course_y, legend_label="Course {}".format(
        selected_course), line_color="green", line_width=1)
    p.circle(x, course_y)
    p.line(x, cluster_y, legend_label="Cluster {}".format(
        cluster_num), line_color="red", line_width=1)
    p.circle(x, cluster_y)
    return p


def plot_enrolment_wrapper(cluster_num, selected_course, df, student_df, width_=1000, height_=600):
    year_plot = plot_enrolment(
        cluster_num, selected_course, df, student_df, time_param="Year")
    month_plot = plot_enrolment(
        cluster_num, selected_course, df, student_df, time_param="Month")
    return Tabs(tabs=[Panel(child=year_plot, title="Year"),
                      Panel(child=month_plot, title="Month")])


def plot_enrolment_cluster(cluster_num, selected_course, df, student_df, time_param='Year', width_=1000, height_=600):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        df['Email Address'])]
    courses = list(df_cluster["CourseCode"].unique())
    for course_selected in tqdm(courses):
        course, cluster = get_enrolment(
            df, student_df, course_selected, time_param)
        x = cluster['Date'].to_list()
        course_y = course[0].to_list()
        cluster_y = cluster[0].to_list()
        p = figure(x_axis_label=time_param,
                   y_axis_label="Number of Students Enrolled",
                   tools="hover,pan,wheel_zoom,box_zoom,reset,save",
                   tooltips=[(time_param, "@x"), ("Enrolment", "@y")],
                   height=height_, width=width_)
        p.line(x, course_y, legend_label="Course {}".format(
            selected_course), line_color="green", line_width=1)
        p.circle(x, course_y)
        p.line(x, cluster_y, legend_label="Cluster {}".format(
            cluster_num), line_color="red", line_width=1)
        p.circle(x, cluster_y)
    return Panel(child=p, title="Enrolment Rate of Students")


def get_enrollment_difference(temp, courses_count, time_param='Year', diff_param=False, width_=1000):
    temp = temp.dropna()
    if time_param == "Year":
        temp['Date'] = temp['Start Date'].apply(
            lambda x: str(pd.to_datetime(x).year))
    else:
        temp['Date'] = temp['Start Date'].apply(
            lambda x: str(pd.to_datetime(x).to_period('M')))
    temp = temp.drop('Start Date', 1)
    temp = temp.groupby(['CourseCode', 'Date']).size().reset_index()
    courses = pd.DataFrame()
    sort_dates = sorted(set(temp['Date']))
    for course in courses_count.keys():
        course_data = temp[temp['CourseCode'] == course]
        course_pivot = course_data.pivot(
            'CourseCode', 'Date', 0).reset_index().rename_axis(None, axis=1)

        courses = pd.concat([courses, course_pivot])

    columns_index = [TableColumn(field=Ci, title=Ci)
               for Ci in courses.columns]
    courses = courses.set_index("CourseCode")
    courses = courses.fillna(0)

    data_table_original = DataTable(columns=columns_index, source=ColumnDataSource(
        courses),fit_columns=False, width=width_, height=400)
    data_table_difference = None
    if diff_param:
        for course in list(courses.index):
            prev = 0
            for i in range(len(sort_dates)):
                date = sort_dates[i]
                diff = 0
                diff = courses.loc[course, [date]].item() - prev
                prev = courses.loc[course, [date]].item()
                if i != 0:
                    courses.loc[course, [date]] = diff

        data_table_difference = DataTable(columns=columns_index, source=ColumnDataSource(
            courses), fit_columns=False, width=width_, height=400)

    return data_table_original, data_table_difference


def plot_enrollment_difference(cluster_num, selected_course, cluster, student_df, width_=1000):
    df_cluster = student_df.loc[student_df['Email Address'].isin(
        cluster['Email Address'])]
    course_ref = df_cluster[df_cluster['CourseCode'] ==
                            selected_course]['Course Reference Number'].to_list()[0]
    courses_count = df_cluster['Course Reference Number'].value_counts(
    ).to_dict()
    temp = df_cluster[['Start Date', 'CourseCode']]

    year_original, year_plot = get_enrollment_difference(
        temp, courses_count, time_param="Year", diff_param=True)
    month_orginal, month_plot = get_enrollment_difference(
         temp, courses_count, time_param="Month")
    return Tabs(tabs=[Panel(child=year_original, title="Year"),
                      Panel(child=month_orginal, title="Month"),
                      Panel(child=year_plot, title="Year Difference")
                    #   Panel(child=month_plot, title="Month Difference")
                      ])

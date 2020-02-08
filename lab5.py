# Do not for get to import!!!!!!
import numpy as np
import plotly.graph_objs as go
import pandas as pd
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
import plotly.express as px

# data location
name = 'data/State_University_of_New_York__SUNY__-_NYS_High_School_Attended_by_First_Time_Undergraduate_Students__Beginning_Fall_2010.csv'

# load data
csv_data = pd.read_csv(name)

# create a dataframe to store data
csv_mydata = pd.DataFrame()

# get longitude and latitude
long = []
lang = []
for index, origin_str in enumerate(csv_data['Location 1']):
    print(index)
    try:
        lang_long_str = str(origin_str).split('\n')[1]
        lang_long = lang_long_str.split(',')
        lang_str = lang_long[0][1:].strip()
        long_str = lang_long[1][:-1].strip()
        long.append(float(long_str))
        lang.append(float(lang_str))
    except Exception as e:
        long.append(0)
        lang.append(0)

# City quque in number
city = sorted(list(set(csv_data['City'])))
city_q = [city.index(c) for c in csv_data['City']]
# print('city: ', city)
# print('city q: ', city_q)

# County quque in number
county = sorted(list(set(csv_data['County'])))
county_q = [county.index(c) for c in csv_data['County']]
# print('county: ', county)
# print('county q: ', county_q)

# Reconstruct data, set all '<4' to 0
csv_mydata['school_name'] = csv_data['High School Name']
csv_mydata['Total'] = [0 if str(i).__contains__('<') else int(i) for i in csv_data['Total Attending SUNY Institutions']]
csv_mydata['Comprehensive'] = [0 if str(i).__contains__('<') else int(i) for i in csv_data['Attending SUNY Comprehensive Colleges']]
csv_mydata['Community'] = [0 if str(i).__contains__('<') else int(i) for i in csv_data['Attending SUNY Community Colleges']]
csv_mydata['Doctoral'] = [0 if str(i).__contains__('<') else int(i) for i in csv_data['Attending SUNY Doctoral Institutions']]
csv_mydata['Technology'] = [0 if str(i).__contains__('<') else int(i) for i in csv_data['Attending SUNY Technology Colleges']]
csv_mydata['long'] = long
csv_mydata['lang'] = lang
csv_mydata['city'] = city_q
csv_mydata['county'] = county_q
csv_mydata['year'] = [int(str(i).split(' ')[1]) for i in list(csv_data['Term '])]
csv_mydata['zip'] = [int(i) for i in list(csv_data['Zip Code'])]
# Start drawing
# num is '1' '2.1' '2.2' '3.1' '3.2'
# 1 : 4 visualization on dashboard (heatmap, parallel, PCA, MDS)
# 2.1 : All county trend chart
# 2.2 : 4 types of schools that student choose
# 3.1 locations for all schools
# 3.2 total students for all county
# set num here

num = 0

if num == 1:
    # heatmap
    name = list(csv_mydata)[1:]
    # no need school name
    data = csv_mydata.drop(['school_name'], 1).values
    corr = np.corrcoef(data.T)
    fig = go.Figure(
        data=go.Heatmap(
            z=corr,
            x=name,
            y=name,
        )
    )

    fig.update_layout(
        title="heat map",
        xaxis_nticks=36)

    fig.show()
    # parallel
    fig = px.parallel_coordinates(
        csv_mydata,
        color_continuous_scale=px.colors.diverging.Tealrose,
        color_continuous_midpoint=2
    )
    fig.show()

    # get PCA and MDS data
    mds = MDS(n_components=2)
    mds.fit(data)
    mds_data = mds.fit_transform(data)
    pca = PCA(n_components=2)
    pca.fit(data)
    pca_data = pca.fit_transform(data)

    # PCA
    csv_mydata['pca_x'] = np.array(pca_data).T[0]
    csv_mydata['pca_y'] = np.array(pca_data).T[1]
    fig = px.scatter(
        csv_mydata,
        x="pca_x",
        y="pca_y",
        color="year",
        title="PCA chart"
    )
    fig.show()

    # MDS
    csv_mydata['mds_x'] = np.array(mds_data).T[0]
    csv_mydata['mds_y'] = np.array(mds_data).T[1]
    fig = px.scatter(
        csv_mydata,
        x="mds_x",
        y="mds_y",
        color="year",
        title="MDS chart"
    )
    fig.show()
num = 2.1
if num == 2.1:

    series_dict = {}
    # All years
    years = sorted(csv_mydata['year'].unique())
    # All county
    Counties = csv_mydata['county'].unique()

    # different county number of students for each year
    for county_ in Counties:
        series = []
        for year in years:
            res = sum(csv_mydata[(csv_mydata['county'] == county_) & (csv_mydata['year'] == year)]['Total'])
            series.append(res)
        series_dict[county_] = series

    all = [0] * len(years)
    for y in series_dict:
        for index, value in enumerate(series_dict[y]):
            all[index] += value

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017],
            y=all,
            mode='lines+markers',
            name='all'
        )
    )
    for i in series_dict:
        fig.add_trace(
            go.Scatter(
                x=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017],
                y=np.array(series_dict[i]),
                mode='lines+markers',
                name=county[i],
            ),
        )

    buttons = []
    buttons.append(dict(
        label="All",
        method="update",
        args=[
            {
                "visible":
                    [True] * (len(county) + 1)
            },
            {
                "title": "All year trend chart",
                "annotations": []
            }
        ]
    ))
    for i in series_dict:
        show = [False] * (len(series_dict) + 1)
        show[i + 1] = True
        tmp = dict(
            label=county[i]+str(i+1),
            method="update",
            args=[
                {
                    "visible": show
                },
                {
                    "title": county[i] + " County Trend Chart",
                    "annotations": []
                }
            ]
        )
        buttons.append(tmp)
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                active=0,
                buttons=buttons)
        ]
    )
    fig.show()

num = 2.2
if num == 2.2:
    series_dict = {}
    # all years
    years = sorted(csv_mydata['year'].unique())
    # all county
    Counties = csv_mydata['county'].unique()
    for county_ in Counties:
        series = {}
        Comprehensive = sum(csv_mydata[(csv_mydata['county'] == county_)]['Comprehensive'])
        series['Comprehensive'] = Comprehensive
        Community = sum(csv_mydata[(csv_mydata['county'] == county_)]['Community'])
        series['Community'] = Community
        Doctoral = sum(csv_mydata[(csv_mydata['county'] == county_)]['Doctoral'])
        series['Doctoral'] = Doctoral
        Technology = sum(csv_mydata[(csv_mydata['county'] == county_)]['Technology'])
        series['Technology'] = Technology
        series_dict[county_] = series

    Comprehensive_ = []
    Community_ = []
    Doctoral_ = []
    Technology_ = []

    for y in series_dict:
        Comprehensive_.append(series_dict[y]['Comprehensive'])
        Community_.append(series_dict[y]['Community'])
        Doctoral_.append(series_dict[y]['Doctoral'])
        Technology_.append(series_dict[y]['Technology'])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=county,
            y=Comprehensive_,
            name='Comprehensive',
            visible=True,
        )
    )
    fig.add_trace(
        go.Bar(
            x=county,
            y=Community_,
            name='Community',
            visible=False
        )
    )
    fig.add_trace(
        go.Bar(
            x=county,
            y=Doctoral_,
            name='Doctoral',
            visible=False
        )
    )
    fig.add_trace(
        go.Bar(
            x=county,
            y=Technology_,
            name='Technology',
            visible=False
        )
    )
    buttons = [
        dict(
            label='Comprehensive',
            method="update",
            args=[
                {
                    "visible": [True, False, False, False]
                },
                {
                    "title": "Comprehensive Comparison",
                    "annotations": []
                }
            ]
        ),
        dict(
            label='Community',
            method="update",
            args=[
                {
                    "visible": [False, True, False, False]
                },
                {
                    "title": "Community Comparison",
                    "annotations": []
                }
            ]
        ),
        dict(
            label='Doctoral',
            method="update",
            args=[
                {
                    "visible": [False, False, True, False]
                },
                {
                    "title": "Doctoral Comparison",
                    "annotations": []
                }
            ]
        ),
        dict(
            label='Technology',
            method="update",
            args=[
                {
                    "visible": [False, False, False, True]
                },
                {
                    "title": "Technology Comparison",
                    "annotations": []
                }
            ]
        )
    ]
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                active=0,
                buttons=buttons)
        ]
    )
    fig.show()
    pass

num = 3.1
if num == 3.1:
    # school locations
    data = []
    layout = dict(
        title='School location on map',
        autosize=False,
        width=1000,
        height=900,
        hovermode=False,
        legend=dict(
            x=0.7,
            y=-0.1,
            bgcolor="rgba(255, 255, 255, 0)",
            font=dict(size=11),
        )
    )

    geo_key = 'geo'
    lons = list(csv_mydata['long'])
    lats = list(csv_mydata['lang'])
    data.append(
        dict(
            type='scattergeo',
            showlegend=False,
            lon=lons,
            lat=lats,
            geo=geo_key,
            marker=dict(
                color="rgb(0, 0, 255)",
                opacity=0.5
            )
        )
    )
    layout[geo_key] = dict(
        scope='usa',
        showland=True,
        landcolor='rgb(229, 229, 229)',
        showcountries=False,
        domain=dict(x=[], y=[]),
        subunitcolor="rgb(255, 255, 255)",
    )

    geo_key = 'geo'
    layout[geo_key]['domain']['x'] = [float(0) / float(1), float(1) / float(1)]
    layout[geo_key]['domain']['y'] = [float(0) / float(1), float(1) / float(1)]

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(width=800)
    fig.show()
    pass

num = 3.2
if num == 3.2:
    series_dict = {}
    # All year
    years = sorted(csv_mydata['year'].unique())
    # all county
    Counties = csv_mydata['county'].unique()
    for county_ in Counties:
        series = []
        for year in years:
            res = sum(csv_mydata[(csv_mydata['county'] == county_) & (csv_mydata['year'] == year)]['Total'])
            series.append(res)
        series_dict[county_] = series

    series_dict_all = {}
    for y in series_dict:
        series_dict_all[y] = sum(series_dict[y])
    x = [county[i] for i in series_dict_all]
    y = [series_dict_all[i] for i in series_dict_all]
    fig = go.Figure(
        data=[go.Bar(x=x, y=y)],
        layout_title_text="All county 2010-2017 total student comparison"
    )
    fig.show()
    pass

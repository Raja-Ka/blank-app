import streamlit as st
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import datetime

# import plotly.express as px

# colorscales = px.colors.named_colorscales()

# df = pd.read_csv('zoomrx.csv')

# uploaded_file = st.file_uploader("Choose a file")
uploaded_file = "data-2024-9-22-10.csv"
if uploaded_file is not None:
    
    df = pd.read_csv(uploaded_file)

    df.drop(["Athlete", 'Activity', 'Location', 'Unit', 'Pace', 'Elev', 'Calo', 'EstPace', 'EstSpeed'], axis='columns', inplace=True)
    df = df.rename(columns={df.columns[0]: "Activity_Type"})
    df = df.rename(columns={df.columns[1]: "Member_Name"})
    df = df.rename(columns={df.columns[2]: "Activity_Date"})
    df = df.rename(columns={df.columns[3]: "Activity_Distance"})
    df = df.rename(columns={df.columns[4]: "Activity_Duration"})

    df['Activity_Date'] = df['Activity_Date'].astype(str).apply(lambda x: x[0:10])
    df['Activity_Distance'] = df['Activity_Distance'].astype(str).apply(lambda x: x.replace(',',''))
    df['Activity_Duration'] = df['Activity_Duration'].astype(str).apply(lambda x: pd.to_timedelta(x))
    df['Activity_Duration'] = df['Activity_Duration'].apply(lambda x: round(x.total_seconds() / 60))

    df['Activity_Type'] = df['Activity_Type'].astype(str).apply(lambda x: 'Run/Walk' if x == 'Run' or x == 'Walk' else x)
    df['Activity_Type'] = df['Activity_Type'].astype(str).apply(lambda x: 'Other Workout' if x == 'Swim' or x == 'HIIT' or x == 'Hike' or x == 'Weight Training' or x == 'Workout' or x == 'Yoga' else x)

    df['Activity_Distance'] = df['Activity_Distance'].astype(float)
    df['Activity_Date'] = pd.to_datetime(df['Activity_Date']).dt.date

    min_date = datetime.datetime(2024, 9, 1).date() 
    # min_date = df['Activity_Date'].min()
    max_date = df['Activity_Date'].max()
    
    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)  # min_value=min_date
    end_date = st.date_input("End Date", max_date, min_value=start_date, max_value=max_date)

    filt = (df["Activity_Date"] >= start_date) & (df["Activity_Date"] <= end_date)
    df = df[filt]




    club_members_lst = df['Member_Name'].unique()
    club_members_lst.sort()

    # Summary for all members
    # summary_df = pd.DataFrame(columns=['Member_Name', 'Unique_Days', 'Total_Activities', 'Total_Distance', 'Total_Duration'])
    summary_df = pd.DataFrame(columns=['Member_Name', 'Unique_Days', 'Total_Activities', 'Total_Duration', 'RW_Activities', 'RW_Distance', 'RW_Duration', 'Ride_Activities', 'Ride_Distance', 'Ride_Duration', 'Other_Activities', 'Other_Duration'])

    for member in club_members_lst:
        filt = df["Member_Name"] == member
        rslt_df = df[filt]
        row_count = rslt_df.shape[0]
        # total_distance = rslt_df['Activity_Distance'].sum()
        total_duration = rslt_df['Activity_Duration'].sum()
        unique_days = rslt_df['Activity_Date'].unique()
        
        rw_activities = rslt_df.loc[rslt_df['Activity_Type'] == 'Run/Walk', 'Activity_Type'].count()
        rw_distance = rslt_df.loc[rslt_df['Activity_Type'] == 'Run/Walk', 'Activity_Distance'].sum()
        rw_duration = rslt_df.loc[rslt_df['Activity_Type'] == 'Run/Walk', 'Activity_Duration'].sum()

        ride_activities = rslt_df.loc[rslt_df['Activity_Type'] == 'Ride', 'Activity_Type'].count()
        ride_distance = rslt_df.loc[rslt_df['Activity_Type'] == 'Ride', 'Activity_Distance'].sum()
        ride_duration = rslt_df.loc[rslt_df['Activity_Type'] == 'Ride', 'Activity_Duration'].sum()
        
        other_activities = rslt_df.loc[rslt_df['Activity_Type'] == 'Other Workout', 'Activity_Type'].count()
        other_duration = rslt_df.loc[rslt_df['Activity_Type'] == 'Other Workout', 'Activity_Duration'].sum()
        
        new_row = {'Member_Name': member, 'Unique_Days': len(unique_days), 'Total_Activities': row_count, 'Total_Duration': total_duration, 
                'RW_Activities': rw_activities, 'RW_Distance': rw_distance, 'RW_Duration': rw_duration, 
                'Ride_Activities': ride_activities, 'Ride_Distance': ride_distance, 'Ride_Duration': ride_duration,
                'Other_Activities': other_activities, 'Other_Duration': other_duration
                }
        summary_df = summary_df._append(new_row, ignore_index=True)

    summary_df = summary_df.sort_values(by=['Unique_Days'], ascending=False)

    # numRows = summary_df.shape[0]
    # df_height = (numRows + 1) * 35 + 3
    # st.dataframe(summary_df, hide_index = True, height=df_height)


    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Unique Days")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=summary_df['Member_Name'], y=summary_df['Unique_Days'],
                            name='Unique Days'))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Run/Walk Distance")
        summary_df = summary_df.sort_values(by=['RW_Distance'], ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=summary_df['Member_Name'], y=summary_df['RW_Distance'],
                            name='RW Distance'))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)



    selected_member = st.selectbox(
        "Club Members", club_members_lst
    )
    st.write("You selected:", selected_member)

    filt = df["Member_Name"] == selected_member
    rslt_df = df[filt]
    rslt_df = rslt_df.sort_values(by=['Activity_Date'], ascending=True)
    
    # numRows = rslt_df.shape[0]
    # df_height = (numRows + 1) * 35 + 3
    # st.dataframe(rslt_df, hide_index = True, height=df_height)

    
    
    rw_df = rslt_df[(rslt_df['Activity_Type'] == 'Run/Walk')]
    if not rw_df.empty:
        st.subheader('Run/Walk')
        rw_df = rw_df.groupby('Activity_Date').sum()
        rw_df['Cumulative'] = rw_df['Activity_Distance'].cumsum()

        fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        fig.add_trace(go.Scatter(x=rw_df.index, y=rw_df['Cumulative'],
                            name='Cumulative'), secondary_y=True)
        fig.add_trace(go.Bar(x=rw_df.index, y=rw_df['Activity_Distance'], 
                            name='Activity'))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)
    
    
    
    
    ride_df = rslt_df[(rslt_df['Activity_Type'] == 'Ride')]
    if not ride_df.empty:
        st.subheader('Ride')
        ride_df = ride_df.groupby('Activity_Date').sum()
        ride_df['Cumulative'] = ride_df['Activity_Distance'].cumsum()

        fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        fig.add_trace(go.Scatter(x=ride_df.index, y=ride_df['Cumulative'],
                            name='Cumulative'), secondary_y=True)
        fig.add_trace(go.Bar(x=ride_df.index, y=ride_df['Activity_Distance'], 
                            name='Activity'))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)
    
    
    
    GSY_df = rslt_df[(rslt_df['Activity_Type'] == 'Other Workout')]
    if not GSY_df.empty:
        st.subheader('Gym/Swim/Yoga')
        GSY_df = GSY_df.groupby('Activity_Date').sum()
        GSY_df['Cumulative'] = GSY_df['Activity_Duration'].cumsum()

        fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        fig.add_trace(go.Scatter(x=GSY_df.index, y=GSY_df['Cumulative'],
                            name='Cumulative'), secondary_y=True)
        fig.add_trace(go.Bar(x=GSY_df.index, y=GSY_df['Activity_Duration'], 
                            name='Activity'))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)
    
    
    st.subheader('Comparison of Run/Walk activities between members')
    options = st.multiselect(
        "Select multiple members", club_members_lst, selected_member
    )
    if len(options) > 0:
        # st.write("You selected:", options)
        
        fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        
        for member in options:
            filt = df["Member_Name"] == member
            rslt_df = df[filt]
            rslt_df = rslt_df.sort_values(by=['Activity_Date'], ascending=True)
            
            rw_df = rslt_df[(rslt_df['Activity_Type'] == 'Run/Walk')]
            if not rw_df.empty:
                rw_df = rw_df.groupby('Activity_Date').sum()
                rw_df['Cumulative'] = rw_df['Activity_Distance'].cumsum()
                fig.add_trace(go.Scatter(x=rw_df.index, y=rw_df['Cumulative'], showlegend=True, name=member
                                    ), secondary_y=True)
                # fig.add_trace(go.Bar(x=rw_df.index, y=rw_df['Activity_Distance'], 
                #                     name=member))
        fig.update_layout(
                        legend_title_text='',
                        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.02, orientation="h"),
                        margin=dict(l=0, r=0, b=0, t=30, pad=0))
        st.plotly_chart(fig, use_container_width=True)
            
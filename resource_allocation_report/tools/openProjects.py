import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def open_projects(roles, projectMaster):
    openProjects = pd.pivot_table(roles, index=['Employee Name','Employee Email','Project Name','PID','Reporting to','State'], values='Status', aggfunc='count').reset_index()
    openProjects = openProjects.merge(projectMaster[['PID','Date of Project Start Date', 'Date of Project End Date', 'Lead PM', 'Sales SPoC', 
                                                    'CAM SPoC', 'Research SPoC', 'M&E SPoc', 'T&D SPoc', 'Proof Verifier Email']], on="PID", how='left')
    openProjects.rename(columns={'Date of Project Start Date':'Start Date',
                                'Date of Project End Date':'End Date'}, inplace=True)
    openProjects.drop(columns='Status', inplace=True)

    return openProjects

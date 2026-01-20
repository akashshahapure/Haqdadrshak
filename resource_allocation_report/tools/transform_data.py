import pandas as pd, numpy as np
import warnings
warnings.filterwarnings('ignore')

def dataXform(df, exitEmpDB, active_emp_DB):
    df = df[~(df['Employee Name'].str.contains(' NGO', case=False, na=False, regex=False))]

    delHieRep = df[(df.Status == 'In Progress') | (df.Status == 'Open')]
    delHieRep = delHieRep[(delHieRep['Employee Name'] != '-No Value-') & (delHieRep['Employee Name'] != 'Rahul Test')]
    delHieRep = delHieRep[delHieRep['Project Name'] != 'Non Project Activities']
    delHieRep = delHieRep[~(delHieRep['Project Name'].str.contains('Test', na=False, case=False))].copy()

    delHieRep = delHieRep.merge(active_emp_DB[['Official Email ID','Employee status']], left_on='Employee Email', right_on='Official Email ID', how='left')
    delHieRep.drop(columns='Official Email ID', inplace=True)
    delHieRep.rename(columns={'Employee status':'Employee Status as per HR'}, inplace=True)

    delHieRep['Employee Status as per HR'] = delHieRep[['Employee Status as per HR','Employee Status','Employee Email']].apply(lambda x: 'In - Active' if (x[0] in [np.nan]) & (x[2] in exitEmpDB['Official Email ID'].value_counts().index.tolist()) else
                                                                                                                            'In - Active' if (x[0] in [np.nan]) & (x[1] in ['In - Active','Notice Period','Terminated']) else
                                                                                                                            'Notice Period' if x[0] == 'Notice Period' else
                                                                                                                            'In - Active' if x[1] in ['In - Active','Notice Period','Terminated'] else
                                                                                                                            'Active' if (x[0] in [np.nan]) & (x[1] == 'Active') else x[0], axis=1)
    roles = delHieRep[(delHieRep['Employee Status as per HR'] != 'In - Active') & (~(delHieRep['Project Name'].str.contains('Test', na=False, case=False)))].copy()

    roles = roles.merge(active_emp_DB[['Official Email ID','Sub Vertical']], left_on='Employee Email', right_on='Official Email ID', how='left')
    roles.drop(columns='Official Email ID', inplace=True)

    pivot1 = pd.pivot_table(roles, index=['Employee Name','Employee Email','Project Name','PID'], values='Status', aggfunc='count').reset_index()
    pivot2 = pd.pivot_table(pivot1, index=['Employee Name','Employee Email'], values='PID', aggfunc='count').reset_index().sort_values(by='PID',ascending=True)
    pivot2.reset_index(drop=True, inplace=True)

    project_names = dict()

    for email in set(pivot1['Employee Email']):
        project_names[email] = " | ".join(pivot1[pivot1['Employee Email']==email]['Project Name'].tolist())

    pivot2['Project Names'] = pivot2['Employee Email'].apply(lambda x: project_names[x])
    active_emp_DB = active_emp_DB.merge(pivot2[['Employee Email','PID']], left_on='Official Email ID', right_on='Employee Email', how='left')
    active_emp_DB.drop(columns='Employee Email', inplace=True)
    missed = active_emp_DB[(active_emp_DB.PID.isna()) & (active_emp_DB.Department=='Program Delivery')].copy()
    missed = missed[~(missed['Full Name'].str.contains('NGO', case=True, na=False, regex=False))]
    if len(missed) == 0:
        pivot2.sort_values(by='PID', ascending=True, inplace=True)
        pivot2.rename(columns={'PID':'Project Count'},inplace=True)
    else:
        missed = missed[['Full Name','Official Email ID']]
        missed['PID']=[0]*len(missed)
        missed['Project Names']=['-']*len(missed)
        missed.rename(columns={'Full Name' : 'Employee Name',
                            'Official Email ID' : 'Employee Email'},
                    inplace=True)
        pivot2 = pd.concat([pivot2,missed], axis=0, ignore_index=True)
        pivot2.sort_values(by='PID', ascending=True, inplace=True)
        pivot2.rename(columns={'PID':'Project Count'},inplace=True)

    pivot2 = pivot2.merge(active_emp_DB[['Official Email ID','Title(Designation)', 'Reporting To', 'State']], left_on='Employee Email', right_on='Official Email ID', how='left')
    pivot2.rename(columns={'Title(Designation)':'Role',
                        'Reporting To':'Reporting Manager'}, inplace=True)
    pivot2.drop(columns='Official Email ID', inplace=True)
    pivot2 = pivot2[['Employee Name', 'Employee Email', 'Role', 'Reporting Manager', 'State', 'Project Count', 'Project Names']]

    return pivot2, roles[['PID', 'Status', 'Project Name', 'State', 'Project Role', 'Employee Name', 'Employee Email', 'Employee Status as per HR', 'Employee Status', 'Designaton', 'Reporting to', 'Reporting to Email', 'Sub Vertical']]


import warnings
warnings.filterwarnings('ignore')

def check_pv(activeProjectMaster, pivot2, empDB):
    pv = activeProjectMaster['Proof Verifier Email'].value_counts().index.tolist()
    pivot2['Project Names'] = pivot2[['Employee Email','Project Names']].apply(lambda x: 'Proof Verifier('+x[1]+')' if x[0] in pv else x[1], axis=1)
    #pivot2.head(10)

    Unallocated = pivot2[pivot2['Project Count'] == 0].copy()
    Allocated = pivot2[pivot2['Project Count'] != 0].copy()
    Allocated = Allocated[(Allocated['Role'] == 'Intern') | (Allocated['Role'] == 'Fellow') | (Allocated['Role'] == 'Junior Coordinator') | (Allocated['Role'] == 'Coordinator') | (Allocated['Role'] == 'Senior Coordinator') | (Allocated['Role'] == 'Associate') | (Allocated['Role'] == 'Senior Associate') | (Allocated['Role'] == 'Associate Manager') | (Allocated['Role'] == 'Assistant Manager') | (Allocated['Role'] == 'Manager')]
    Allocated = Allocated.merge(empDB[['Official Email ID','Department']], left_on='Employee Email', right_on='Official Email ID', how='left')
    Allocated.drop(columns='Official Email ID', inplace=True)
    Allocated = Allocated.merge(empDB[['Official Email ID','Sub Vertical']], left_on='Employee Email', right_on='Official Email ID', how='left')
    Allocated.drop(columns='Official Email ID', inplace=True)
    Allocated.rename(columns={'Department':'Vertical'}, inplace=True)

    return Allocated, Unallocated

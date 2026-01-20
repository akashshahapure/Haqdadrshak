import warnings
warnings.filterwarnings('ignore')

def rem_space(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna(' ')
            try:
                df[col] = df[col].apply(lambda x: ' '.join(x.split()))
            except Exception:
                pass
    return df


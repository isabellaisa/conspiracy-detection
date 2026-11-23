from paths import DatasetPaths, CT_NOVTT, VIDEOS_SAMPLE_1000
import os
import pandas as pd
from path import Path

# returns a set of ids that were classified across all modalities
#TODO/NOTA: NON AVEVO PENSATO AL FATTO CHE I PATH SONO HARDCODED SU LEONARDO. SOSTITUIRE ALMERNO QUIESTI DI ANALISI CON SEMPLICI PATH
def get_classified_ids(dataset: str):
    """ dataset è il path della c rtella ai risultati di classificazione. ad esempio per CT_NOVTT è classification_results/CT_NOVTT """
    ids = set()
    dataset = Path(dataset)
    for f in dataset.iterdir():
        df = pd.read_csv(f)

        # tengo solo le righe che hanno classificazione compliant
        df["video_id"] = df["video_id"].astype(str).str.replace(r"\.mp4$", "", regex=True)
        model_cols = [c for c in df.columns if c != "video_id"]
        df[model_cols] = df[model_cols].apply(pd.to_numeric, errors="coerce")
        #vals = df[model_cols].apply(pd.to_numeric, errors="coerce")
        df_clean = df[df[model_cols].isin([0, 1]).all(axis=1)]
        df_clean = df_clean.astype(int)

        #righe non compliant (potrebbe essere utile ritornare anche questo riusultato)
        discarded_rows = len(df) - len(df_clean)

        clean_ids = set(df_clean["video_id"])

        # (ids = clean_ids) if (len(ids) == 0) else (ids = ids & clean_ids)
        if len(ids) == 0:
            ids = clean_ids
        else:
            ids = ids & clean_ids

    return ids

def clean_result(df: pd.DataFrame):
    """returns a classification result dataframe whose columns are video_id and models used for classification, and only valids classification rows with values 0,1 """

    # clean video_id nel caso contenesse estensione .mp4
    df["video_id"] = df["video_id"].astype(str).str.replace(r"\.mp4$", "", regex=True)
    
    # clean calssification values 
    model_cols = [c for c in df.columns if c != "video_id"]
    df[model_cols] = df[model_cols].apply(pd.to_numeric, errors="coerce")
    #vals = df[model_cols].apply(pd.to_numeric, errors="coerce")
    df_clean = df[df[model_cols].isin([0, 1]).all(axis=1)]
    df_clean = df_clean.astype(int)

    return df_clean

def create_new(ct_ds: str, non_ct_ds:str, new_dataset_dir: str, ct_perc: int):
    """ ct_ds, non_ct_ds, new_dataset_dir sono tutti path alle cartelle con i risultati di classificazione"""
    # perc must be <= 100
    if ct_perc > 100:
        print("percentuale non valida, dataset non creato")
        return
    
    ct_ids = get_classified_ids(ct_ds)
    non_ct_ids = get_classified_ids(non_ct_ds)
    
    nonct_perc = (100 - ct_perc)
    num_ct = (len(non_ct_ids)*ct_perc)/nonct_perc
    num_ct = int(round(num_ct))
    #order files in the directories
    ct_sorted = sorted(os.listdir(Path(ct_ds)))
    nonct_sorted = sorted(os.listdir(Path(non_ct_ds)))

    for ctf, nonctf in zip(ct_sorted, nonct_sorted):
        ct_df = pd.read_csv(f"{ct_ds}/{ctf}")
        nonct_df = pd.read_csv(f"{non_ct_ds}/{nonctf}")

        ct_df_clean = clean_result(ct_df)
        nonct_df_clean = clean_result(nonct_df)
        
        #forse potrei spostare questo nella funzione clean
        nonct_df_clean = nonct_df_clean[nonct_df_clean["video_id"].isin(non_ct_ids)]
        ct_df_clean = ct_df_clean[ct_df_clean["video_id"].isin(ct_ids)]
        
        #add label column
        nonct_df_clean["label"] = 0
        ct_df_clean["label"] = 1

        if ct_perc != 50:
            ct_sample_df = ct_df_clean.sample(n=num_ct, replace=False, random_state=1)
        else:
            ct_sample_df = ct_df_clean

        #create the new dataset
        #file name is the same
        new_dataset_df = pd.concat([nonct_df_clean, ct_sample_df])
        new_filename = Path(ctf).stem
        new_dataset_df.to_csv(f"{new_dataset_dir}/{new_filename}.csv", index= False)
        
        
        





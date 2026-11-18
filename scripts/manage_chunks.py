#to manage outputs of chunked execution + results analysis
import pickle
import pandas as pd
from paths import MIXED_SAMPLE_1000, VIDEOS_SAMPLE_1000, CT_NOVTT

def merge_transcript_chunks(dir, num_chunks:int):

    merged = {}
    for i in range(num_chunks):  
        with open(f'{dir.transcript_simple}/transcript_chunk{i}.pkl', 'rb') as f:
            merged.update(pickle.load(f))

    with open(f'{dir.transcript_simple}/transcript', 'wb') as f:
        pickle.dump(merged, f)
   
    print(f"Totale trascrizioni unite: {len(merged)}")
    


def analyse_processed_mixed_1000(merged):
    """creates a csv with id and labels of videos that were sucessfully processed for images nd transcript, and that can be used for classification """
    
        #ricorda che merged è un unico dict con key video id, value transcript
        
    merged_ids =[]
    
    for k,v in merged.items():
        merged_ids.append({"video_id": k})
    
    merged_ids_df = pd.DataFrame(merged_ids, columns = ["video_id"])
    rows, columns = merged_ids_df.shape
    print(f"number of rows in merged: {rows}")

    merged_ids_df["video_id"] = merged_ids_df["video_id"].str.replace(".mp4", "", regex=False)
    #load csv with labels of the raw sample
    raw_sample = pd.read_csv("/leonardo_work/IscrC_MARGOT/dataset/labels/mixed_sample_1000.csv")
    
    raw_sample = raw_sample.astype({"video_id":str})
    merged_ids_df = merged_ids_df.astype({"video_id":str})

    valid_sample = pd.merge(raw_sample, merged_ids_df, on="video_id", how="inner")
    valid_rows, c = valid_sample.shape
    print(f"number of rows in valid: {valid_rows}")
    print(f"number of columns in valid: {c}")
    num_ct = valid_sample.groupby(["label"]).count()
    print(f"number of cts in valid sample: {num_ct}")


if __name__ == "__main__":
    merge_transcript_chunks(CT_NOVTT, 10)
    # transcripts_path = "/leonardo_scratch/fast/IscrC_MARGOT/processed_data/mixed_sample_1000/transcript/transcript"
    
    # with open(transcripts_path, "rb") as pk:
    #     merged = pickle.load(pk)

    # analyse_processed_mixed_1000(merged)
import os
import pandas as pd
import pickle
from paths import DatasetPaths, CT_NOVTT, VIDEOS_SAMPLE_1000

SAVE_PATH = "/leonardo_work/IscrC_MARGOT/igugliel/dataset_metrics"

def analyze_classifiable_videos(dataset:DatasetPaths):

    # estrai tutti i raw videos ids. nota che questo metodo mantiene l'estensione del file. a me serve solo l'id
    raw_ids = os.listdir(dataset.raw_videos)
    print(f"raw ids list elemento: {raw_ids[1]}", flush=True)
    raw_df =  pd.DataFrame(raw_ids, columns=["id"])

    simple_transcript = dataset.transcript_simple / "transcript"
    with open(simple_transcript, "rb") as pk:
        transcripts_dict = pickle.load(pk)

    # estrai ids dei video di cui ho transcript
    transcript_ids = []
    for k in transcripts_dict.keys():
        transcript_ids.append(k)

    transcript_df = pd.DataFrame(transcript_ids, columns=["id"])
    for df in (raw_df, transcript_df):
        df["id"] = df["id"].astype(str).str.replace(r"\.mp4$", "", regex=True)
    #ids dei video di cui ho i frames, per ogni metodo

    iframes_ids = os.listdir(dataset.iframes_frames)
    sb_ids = os.listdir(dataset.shotbased_frames)
    tn_ids = os.listdir(dataset.trnsntv2_frames)

    iframes_df = pd.DataFrame(iframes_ids, columns=["id"])
    sb_df = pd.DataFrame(sb_ids, columns=["id"])
    tn_df = pd.DataFrame(tn_ids, columns=["id"])

    for df in (iframes_df, sb_df, tn_df):
        df["id"] = df["id"].astype(str).str.replace(r"\.tar$", "", regex=True)

    idsiframes, idssb, idstn = set(iframes_df["id"]), set(sb_df["id"]), set(tn_df["id"])
    idsraw, idstranscr = set(raw_df["id"]), set(transcript_df["id"])

    solo_in_raw = idsraw - idstranscr

    not_processed_num = len(solo_in_raw)

    solo_in_transcr = idstranscr - idsiframes


    print(f"{not_processed_num} video in raws ma non in transcript: {solo_in_raw}")
    print(f"video che sono in transcript ma non in frame extraction: {solo_in_transcr}")

    solo_in_iframes = idsiframes - idstn
    solo_in_sb = idssb - idstn
    print(f"solo in iframes (TN): {solo_in_iframes}")
    print(f"solo in sb (TN): {solo_in_sb}")

    #video presenti in tutte le modalità
    correctly_processed = idsraw & idstranscr & idsiframes & idssb & idstn
    print(f"{len(correctly_processed)} videos correctly processed in {dataset.name} ")
    
    filename = f"{dataset.name}_processed_ids"
    savepath = f"{SAVE_PATH}/{filename}"
    
    with open(savepath, "wb") as f:
        pickle.dump(correctly_processed, f)

    # creare un elenco di ids che siano in tutte le modalità di processing. 
    # capire perche alcuni video che vengono processati bene in iframes e shotbased non vengono processati in transnetv2 
    # di base posso contare ids di tanscript e iframes (tutti i video che passano con iframes passano anche con shotbased)
    # out of memory andava con image-transcript ad un certo punto -  ma non mi sembra ci fossero casi contantissimi frames. nel caso provare a vedere se dai csv riescoa  risalire al video con il piu alto numero di frames estratti



if __name__ == "__main__":
    analyze_classifiable_videos(CT_NOVTT)
    analyze_classifiable_videos(VIDEOS_SAMPLE_1000)
import pandas as pd
import pickle as pk
from path import Path
from paths import DatasetPaths, CT_VIDEOS, VIDEOS_SAMPLE_100, MIXED_SAMPLE_1000, CT_NOVTT, VIDEOS_SAMPLE_1000

# function that formats input concatenating transcript and frames that are associated
# needs:
# path to keyframes timestamp csv, transcript with timestamps csv, path where to save the list of dict 
# associates keyframes to transcript phrases. if a frame does not fall within a transcript timestamp it is not used. (only case in which this happens is if the transcript has moments of silence that are not recorded and therefore skipped in the transcription.)
# result is saved in a list of dict. each dict is structured in the folloing way:
# {"images": [img1, img2, img,3], timestamp":"start-finish", "text": "text"}
def concat_transcript_frames(frames_ts_path:str, transcript_path:str, save_path:str):

    frames_df = pd.read_csv(frames_ts_path)
    transcript_df = pd.read_csv(transcript_path)

    concat = []
    
    for row in transcript_df.itertuples():
        d = {}
        d["timestamp"] = f"{row.start}-{row.end}"
        d["text"] = row.text
        images = []
        imgs_rows = frames_df.iloc[(frames_df.timestamp >= row.start) & (frames_df.timestamp <= row.end)]
        for img in imgs_rows.itertuples():
            images.append(img.frame)
        d["images"] = images
        concat.append(d)
    with open(save_path, 'ab') as output:
        pk.dump(concat, output)
    
def build_concat(dir:DatasetPaths):
    for file in dir.transcript_timestamped.iterdir():
    
        try:
            video_id = Path(file).stem
            iframes_ts = dir.iframes / f"{video_id}.csv"
            shotbased_ts = dir.shotbased / f"{video_id}.csv"
            trnsntv2_ts = dir.trnsntv2 / f"{video_id}.csv"
            timestamped = dir.transcript_timestamped / f"{video_id}.csv"
            save_path_iframes = dir.concat_iframes/ video_id
            save_path_shotbased = dir.concat_shotbased / video_id
            save_path_trnsntv2 = dir.concat_trnsntv2 / video_id
    
            concat_transcript_frames(iframes_ts, timestamped, save_path_iframes)
            concat_transcript_frames(shotbased_ts, timestamped, save_path_shotbased)
            #concat_transcript_frames(trnsntv2_ts, timestamped, save_path_trnsntv2)
            
        except Exception as e:
            print(e)
            #print(f"transcript di {video_id} non ha corrispondenza immagini") 
      
if __name__ == "__main__":

    build_concat(CT_NOVTT)
    #build_concat(VIDEOS_SAMPLE_1000)
    
        

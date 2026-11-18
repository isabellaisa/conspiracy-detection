from pathlib import Path
from paths import DatasetPaths, CT_NOVTT, VIDEOS_SAMPLE_1000
import os, io
import tarfile
from PIL import Image
import math 
import matplotlib.pyplot as plt
import cv2
import datetime
import pandas as pd
#from frames_extraction import extract_IFrames,extract_shot_based
#open tar file, extract images. count images. display images. 
# do it for some tar files. save counts. calc average

def extract_images(video_path):
    """extract image bytes from a tar file. returns the list of imgaes in bytes"""
    imgsBytes = []
    with tarfile.open(video_path, "r") as tar:
        members = tar.getmembers()
        for member in members:
            if not member.isfile():
                continue

            #print(f"{member.name}, {video_path}", flush=True)
            img_bytes = tar.extractfile(member).read()
            imgsBytes.append(img_bytes)
    return imgsBytes

def analyse_images(video_iframes_path, video_shotbased_path, sample_dir: DatasetPaths):

    iframes_bytes = extract_images(video_iframes_path)
    shotbased_bytes = extract_images(video_shotbased_path)

    #number of frames for each type is the len of the array
    num_iframes = len(iframes_bytes)
    num_shotbased = len(shotbased_bytes)

    print(f"video: {video_iframes_path.name}, number of iframes: {num_iframes}, number of shotbased frames: {num_shotbased}", flush=True)

    iframes = []
    shotbased = []
    
    
    #for img_bytes in iframes_bytes:
       # iframes.append(Image.open(io.BytesIO(img_bytes)).convert("RGB"))
    
    
    #for img_bytes in shotbased_bytes:
       #shotbased.append(Image.open(io.BytesIO(img_bytes)).convert("RGB"))

    # put all extracted frames of each video in a grid and save it as a png
    # grid will have 10 columns
    
    #i_savepath = Path (f"{sample_dir.processed}/images/{Path(video_iframes_path).stem}_iframes.png")
    #s_savepath = Path (f"{sample_dir.processed}/images/{Path(video_iframes_path).stem}_shotbased.png") 
   
    #savegrid(iframes, i_savepath)
    #savegrid(shotbased, s_savepath)

    return num_iframes, num_shotbased
    
def analyse_images(frames_path:Path, dataset:DatasetPaths, frames_type:str):

    frames_bytes = extract_images(frames_path)
    num_frames = len(frames_bytes)

# parte che salva le immgini. commentare se non necessaria
    # frames = []
    # for img_bytes in frames_bytes:
    #     frames.append(Image.open(io.BytesIO(img_bytes)).convert("RGB"))
    # savepath = Path (f"{dataset.processed}/images/{Path(frames_path).stem}_{frames_type}.png")
    # savegrid(frames, savepath)
# fine parte

    return num_frames

def savegrid(ims:list[Image.Image], savepath, cols=10):
    """Mette le immagini in formato thumbnail in una griglia e salva in PNG"""
    if not ims:
        return

    #resize all images into thumbnails
    for i, im in enumerate(ims):      
        im.thumbnail((480, 480))

    w, h = ims[0].size
    rows = math.ceil(len(ims) / cols)
    canvas = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))

    for i, im in enumerate(ims):
        if im.size != (w, h):
            im = im.resize((w, h), Image.LANCZOS)  
        
        canvas.paste(im, ((i % cols) * w, (i // cols) * h))

    canvas.save(savepath)  



#TODO:TESTARE
def calc_metrics(dataset:DatasetPaths):
    """salva un csv con videoid, lunghezza, numero iframes, numero shotbased"""
    metrics =[]

    dataset.ensure_dirs()
        
    totiframes = 0
    totshotb = 0
    tot_transnet = 0
    totvideos = 0

    tot_ifr_cvg = 0 
    tot_sb_cvg = 0
    tot_tn_cvg = 0
    for video in dataset.raw_videos.iterdir():
        video_id = video.stem 
        try:
            
            numiframes = analyse_images(Path(f"{dataset.shotbased_frames}/{video_id}.tar"),dataset, "iframes")
            numshotb = analyse_images(Path(f"{dataset.iframes_frames}/{video_id}.tar"),  dataset, "shotbased")
            num_transnet = analyse_images(Path(f"{dataset.trnsntv2_frames}/{video_id}.tar"),  dataset, "transnetv2")
                        
            totiframes = totiframes + numiframes
            totshotb = totshotb + numshotb
            tot_transnet = tot_transnet + num_transnet

            
            #video duration metrics
            video_item = cv2.VideoCapture(video)
            frames = video_item.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video_item.get(cv2.CAP_PROP_FPS)
            seconds = round(frames / fps)
            video_time = datetime.timedelta(seconds=seconds)
            i_cvrg = (numiframes/frames) * 100
            sb_cvrg = (numshotb/frames) * 100
            tn_cvrg = (num_transnet/frames) * 100
            
            # print(f"{video_id} iframes coverage: {i_cvrg}")
            
            tot_ifr_cvg = tot_ifr_cvg + i_cvrg
            tot_sb_cvg = tot_sb_cvg + sb_cvrg
            tot_tn_cvg = tot_tn_cvg + tn_cvrg
            #count only non corrupted videos
            totvideos = totvideos + 1
            video_metrics = {
                "video_id" : video_id,
                "fps": fps,
                "duration": video_time,
                "num_iframes": numiframes,
                "iframes_coverage": i_cvrg,
                "num_shotbased": numshotb,
                "shotbased_coverage": sb_cvrg,
                "num_transnet": num_transnet,
                "transnet_coverage": tn_cvrg
            }
            metrics.append(video_metrics)
        except Exception as e:
            print(e, flush=True)
    
    #dataset metrics 
    
    datasets_metrics_file = Path("/leonardo_work/IscrC_MARGOT/dataset_metrics/datasets_metrics.csv")
       
    avgiframes = round(totiframes/totvideos) 
    avgshotbased = round(totshotb/totvideos)
    avgtransnet = round(tot_transnet/totvideos)

    #average coverage of videos
    avg_i_cvg = round(tot_ifr_cvg/totvideos, 3)
    avg_sb_cvg = round(tot_sb_cvg/totvideos, 3)
    avg_tn_cvg = round(tot_tn_cvg/totvideos, 3)

    print(f"tot iframe coverage {tot_ifr_cvg}")

    datasets_metrics = [{
        "dataset": dataset.name,
        "avg_iframes": avgiframes,
        "avg_shotbased": avgshotbased,
        "avg_transnet":avgtransnet,
        "avg_iframes_coverage_percentage": avg_i_cvg,
        "avg_shotbased_coverage_percentage":avg_sb_cvg,
        "avg_transnet_coverage_percentage": avg_tn_cvg      
    } ]
    print(f"totiframes:{totiframes}, totshotbased: {totshotb}")
    print(f"average iframes coverage:{avg_i_cvg}, average shtobased coverage: {avg_sb_cvg}")
    
    df = pd.DataFrame(metrics, columns=[
        "video_id", "fps", "duration", "num_iframes", "iframes_coverage", "num_shotbased", "shotbased_coverage","iframes_coverage","num_transnet", "transnet_coverage"])
    
    res_df = df.nlargest(5, "num_shotbased")
    print(f"top five videos from {dataset.name} with the highest number of shotbased frames {res_df[['video_id', 'num_shotbased']]}")

    res_df = df.nlargest(5, "num_iframes")
    print(f"top five videos from {dataset.name} with the highest number of iframes {res_df[['video_id', 'num_iframes']]}")

    df.to_csv(f"/leonardo_work/IscrC_MARGOT/dataset_metrics/metrics_{dataset.name}.csv", index=False)


    df = pd.DataFrame(datasets_metrics, columns=["dataset", "avg_iframes", "avg_shotbased", "avg_transnet","avg_iframes_coverage_percentage", "avg_shotbased_coverage_percentage", "avg_transnet_coverage_percentage" ])
    
   # header = False if datasets_metrics_file.exists() else True
    df.to_csv(f"/leonardo_work/IscrC_MARGOT/dataset_metrics/datasets_metrics_final.csv", mode="a", index=False )

def main():
    calc_metrics(VIDEOS_SAMPLE_1000)
    

        

if __name__ == "__main__":
  main()
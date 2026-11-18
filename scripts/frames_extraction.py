import os
import ffmpeg
from path import Path
import json
import pandas as pd
import av
import av.datasets
import cv2 as cv
from PIL import Image
from scenedetect import detect, AdaptiveDetector, FrameTimecode
import tarfile, shutil
import random
from transnetv2_pytorch import TransNetV2
import torch
import argparse
import traceback
import sys
from paths import DatasetPaths, CT_VIDEOS, VIDEOS_SAMPLE_100, VIDEOS_SAMPLE_1000, MIXED_SAMPLE_1000, CT_TMP, BALANCED_SAMPLE_2K, CT_NOVTT



def extract_IFrames(video_file: Path, dataset_paths:DatasetPaths):
  filename = video_file.stem
  content = av.datasets.curated(str(video_file))
  results = []

  #in iframes folder, create a new folder for each video to store its keyframes
  
  video_keyframes_dir = dataset_paths.iframes / filename
  tarfiles_dir = dataset_paths.iframes_frames
  os.makedirs(video_keyframes_dir, exist_ok=True)
  #os.makedirs(tarfiles_dir, exist_ok=True)
  try:
     
    with av.open(content) as container:
        
        stream = container.streams.video[0]
        stream.codec_context.skip_frame = "NONKEY"

        for i, frame in enumerate(container.decode(stream)):
            frame_name= f"frame.{i:04d}.jpg"
            frame_path = f"{video_keyframes_dir}/{frame_name}"

            #provare a estrarre anche il timestamp. time in seconds = pts x time_base
            #sistemare questa cosa del timestamp e la formattazione del csv
            ts = round(float(frame.pts * frame.time_base), 2)

            results.append({'frame':frame_name,'timestamp':ts})

            frame.to_image().save(frame_path, quality=80)

    tar_path = f"{tarfiles_dir}/{filename}.tar"
    with tarfile.open(tar_path, "w") as tar:
      tar.add(video_keyframes_dir, arcname=filename)

    df_results = pd.DataFrame(results, columns=['frame', 'timestamp'])
    df_results.to_csv(f"{dataset_paths.iframes}/{filename}.csv")

  except Exception as e:
    print(f"Errore durante la decodifica del video o file corrotto (iframes). video file: {video_file}")
    traceback.print_exc()
    with open(f"corrupted_iframes.txt", "a") as f:
        f.write(f"{filename}\n")
  shutil.rmtree(video_keyframes_dir)

# NON USATA 
def extract_IFrames_rand(video_file: Path, dataset_paths:DatasetPaths, num_of_frames: int):
  filename = video_file.stem
  content = av.datasets.curated(str(video_file))
  results = []
  frames = []
  #in iframes folder, create a new folder for each video to store its keyframes
  
  video_keyframes_dir = dataset_paths.iframes / filename
  tarfiles_dir = dataset_paths.iframes_frames
  os.makedirs(video_keyframes_dir, exist_ok=True)
  #os.makedirs(tarfiles_dir, exist_ok=True)
  try:
    
    with av.open(content) as container:
        
        stream = container.streams.video[0]
        stream.codec_context.skip_frame = "NONKEY"

        for i, frame in enumerate(container.decode(stream)):
            #frame_name= f"frame.{i:04d}.jpg"
            #frame_path = f"{video_keyframes_dir}/{frame_name}"

            #provare a estrarre anche il timestamp. time in seconds = pts x time_base
            #sistemare questa cosa del timestamp e la formattazione del csv
            #ts = round(float(frame.pts * frame.time_base), 2)

            #results.append({'frame':frame_name,'timestamp':ts})
            frames.append(frame)
            #frame.to_image().save(frame_path, quality=80)
    
    # randomly select frames in the same number of shotbased
    # #TODO:TESTARE  
    if(num_of_frames < len(frames)):
      frames = random.sample(frames, num_of_frames)
    
    for i,frame in enumerate(frames):
      frame_name= f"frame.{i:04d}.jpg"
      frame_path = f"{video_keyframes_dir}/{frame_name}"
      ts = round(float(frame.pts * frame.time_base), 2)
       
      results.append({'frame':frame_name,'timestamp':ts})
      frame.to_image().save(frame_path, quality=80)
       
    tar_path = f"{tarfiles_dir}/{filename}.tar"
    with tarfile.open(tar_path, "w") as tar:
      tar.add(video_keyframes_dir, arcname=filename)

    df_results = pd.DataFrame(results, columns=['frame', 'timestamp'])
    df_results.to_csv(f"{dataset_paths.iframes}/{filename}.csv")

  except av.error.InvalidDataError as e:
    print(f"Errore durante la decodifica del video o file corrotto (iframes). video file: {video_file}")
  
  shutil.rmtree(video_keyframes_dir)

# NON USATA
def extract_uniform(video_file, max_frames):
  #extract frames from video with uniform sampling for a maximum of max_frames along the whole video
  cap = cv.VideoCapture(video_file)
  video_fps = cap.get(cv.CAP_PROP_FPS)
  video_framecount = cap.get(cv.CAP_PROP_FRAME_COUNT)
  video_duration = video_framecount / video_fps
  fps = max_frames / video_duration
  frame_interval = int(video_fps / fps)  #ogni quanti frame originali campionare

  filename = Path(video_file).stem
  frames = []
  frame_idx = 0

  while True:
      ret, frame = cap.read()
      if not ret:
          break

      if frame_idx % frame_interval == 0:
          timestamp = frame_idx / video_fps  #secondi
          frames.append({
              "frame": frame_idx,
              "timestamp": timestamp,
          })
          Image.open(frame).save(f"{UNIFORM_DIR}/{filename}/{frame_idx}.jpg")

      frame_idx += 1

  cap.release()
  frames_df = pd.DataFrame(frames, columns = ["frame", "timestamp"])
  frames_df.to_csv(f"{UNIFORM_DIR}/{filename}.csv")
     
def extract_shot_based(video_file:Path, dataset_paths:DatasetPaths):

  filename = video_file.stem
  video_keyframes_dir = dataset_paths.shotbased / video_file.stem
  tarfiles_dir = dataset_paths.shotbased_frames
  os.makedirs(video_keyframes_dir, exist_ok=True)
  #os.makedirs(tarfiles_dir, exist_ok=True)
  try:
    # NOTA: MODIFICATO START IN SCENE = TRUE. SERVE PER AVERE UNA SINGOLA SCENA NEL CASO IN CUI CI SIANO TAGLI, INVECE CHE 0.
    scene_list = detect(video_file, AdaptiveDetector(), start_in_scene=True)

    result = []

    for i, scene in enumerate(scene_list):
      first_frame_time = scene[0].get_timecode()
      first_frame_name = f"scene_{i+1:03d}_first.jpg"
      first_frame_path = f"{video_keyframes_dir}/{first_frame_name}"
      
      (
          ffmpeg
          .input(video_file, ss=first_frame_time)  # ss = seek al timestamp di inizio scena
          .output(first_frame_path, vframes=1)      # TODO:first frame path da scegliere
          .overwrite_output()
          .run(quiet=True)
      )
      #timestamp in seconds
      ts = scene[0].seconds
      #save timestamp/frame pair in df
      result.append({'frame': first_frame_name,'timestamp':ts})

    
    tar_path = f"{tarfiles_dir}/{filename}.tar"
    with tarfile.open(tar_path, "w") as tar:
      tar.add(video_keyframes_dir, arcname=filename)
    

    df_results = pd.DataFrame(result, columns=['frame', 'timestamp']) 
    
    df_results.to_csv(f"{dataset_paths.shotbased}/{filename}.csv")
  except Exception as e:
    print(f"Errore durante la decodifica del video o file corrotto (shotbased). video file: {video_file}")
    print(e, flush=True)
    traceback.print_exc(sys.exc_info())
    with open(f"corrupted_shotbased.txt", "a") as f:
      f.write(f"{filename}\n")
  shutil.rmtree(video_keyframes_dir)


def extract_trnsntv2_shots(video_file:Path, dataset_paths:DatasetPaths):
  
  """extract scenes with transnet v2 and save the first one as keyframe"""
  
  filename = video_file.stem
  video_keyframes_dir = dataset_paths.trnsntv2 / filename
  tarfiles_dir = dataset_paths.trnsntv2_frames
  os.makedirs(video_keyframes_dir, exist_ok=True)
  model = TransNetV2(device='auto')
  model.eval()
  # Load weights
  weights_path = os.path.join(
    os.path.dirname(__import__('transnetv2_pytorch').__file__),
    "transnetv2-pytorch-weights.pth")
  state_dict = torch.load(weights_path, map_location=model.device)
  model.load_state_dict(state_dict)
  result = []
  try:
    with torch.no_grad():
      # Primary method: Scene detection
      scenes = model.detect_scenes(video_file)
      
    # print(f"Found {len(scenes)} scenes", flush=True)
    for scene in scenes:
      print(f"Scene {scene['shot_id']}: {scene['start_time']}s - {scene['end_time']}s")
      start_time = scene['start_time']
      scene_id = scene['shot_id']
      frame_name = f"scene_{scene_id}_first.jpg"
      frame_path = f"{video_keyframes_dir}/{frame_name}"

      (
          ffmpeg
          .input(video_file, ss=start_time)  # ss = seek al timestamp di inizio scena. nota che se non specificata unità di misura vale in secondi
          .output(frame_path, vframes=1, pix_fmt='yuvj420p', **{'q:v': 2})      
          .overwrite_output()
          .run(quiet=True)
      )
      
      result.append({'frame': frame_name,'timestamp':start_time})    
    
    tar_path = f"{tarfiles_dir}/{filename}.tar" 
    with tarfile.open(tar_path, "w") as tar:
      tar.add(video_keyframes_dir, arcname=filename)     
        # Convenience methods
        #scene_count = model.get_scene_count(video_file)
        #timestamps = model.get_scene_timestamps(video_file)
    df_results = pd.DataFrame(result, columns=['frame', 'timestamp']) 
        
    df_results.to_csv(f"{dataset_paths.trnsntv2}/{filename}.csv")    
  except Exception as e:
    print(f"Errore durante la decodifica del video o file corrotto (transnetv2). video file: {video_file}")
    print(e, flush=True)
    print("ffmpeg stdout:", e.stdout.decode("utf-8", errors="replace"))
    print("ffmpeg stderr:", e.stderr.decode("utf-8", errors="replace"))
    traceback.print_exc() 
  shutil.rmtree(video_keyframes_dir)     

def extract_all(dir:DatasetPaths):
   dir.ensure_dirs()
   for file in dir.raw_videos.iterdir():
      extract_trnsntv2_shots(file, dir)
      extract_IFrames(file, dir)
      extract_shot_based(file, dir)
      
   

    


if __name__ == "__main__":

  extract_all(VIDEOS_SAMPLE_1000)
  extract_all(CT_NOVTT)
 
  
import pandas as pd
from path import Path
import pickle as pk
from transformers.video_utils import load_video
import av
import tarfile
import io
from PIL import Image

class ChatHistory:


    @staticmethod
    def init_chat_history_v(video_file:str, prompt:str):
       
        # campionamento uniforme max 60 frames su tutto il video, che è la limitazione imposta da gemma4. 
        # questo per avere dei risultati confrontabili su questo tipo di classificazione
        video_object, metadata = load_video(video = video_file, backend="pyav", num_frames = 60)
        chat_history = [
            {
                "role": "user",
                "content":[
                    {"type": "video", "video": video_object},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        return chat_history, metadata


    @staticmethod
    def init_chat_history_vt(video_file:str, transcript:str, prompt:str):
        
        #video intero e transcript
        video_object, metadata = load_video(video = video_file, backend="pyav", num_frames = 60) 
    

        chat_history = [
            {
                "role": "user",
                "content":[
                    {"type": "video", "video": video_object},
                    {"type": "text", "text": transcript},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        return chat_history, metadata

    @staticmethod
    def init_chat_history_t(transcript: str, prompt:str):
          
        chat_history = [
            {
                "role": "user",
                "content":[
                    {"type": "text", "text": transcript},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        return chat_history

    #prima tutte le immgini con il loro timestamp, poi il transcript con timestamp. non allineati
    #keyframes è il path al tar file
    @staticmethod
    def init_chat_history_it(keyframes:str, keyframes_ts:str, transcript:str, prompt:str):
        
        content = []
        keyframes_ts_df = pd.read_csv(keyframes_ts)
        
        with tarfile.open(keyframes, "r") as tar:
            members = sorted(tar.getmembers(), key=lambda m: m.name)
            for member in members:
                if not member.isfile():
                    continue

        
                img_id = Path(member.name).name
                img_ts_row = keyframes_ts_df.loc[keyframes_ts_df['frame']== img_id]
                
                timestamp = str(img_ts_row["timestamp"].iloc[0])
                img_bytes = tar.extractfile(member).read()
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

                content.append({"type":"image", "image": img})
                
                content.append({"type": "text", "text": timestamp})
            
            

        #ora parte transcript
        transcript_df = pd.read_csv(transcript)
        ts = ""

        for row in transcript_df.itertuples():
            ts = ts + f"[{row.start}-{row.end}] {row.text} "
    
        content.append({"type":"text", "text": ts})     

        content.append({"type":"text", "text":
        "Video keyframes are followed by the timestamp in which they appear in the video, in the following format: [image1] [timestamp]. After all the keyframes, there is the transcript of the video, each section is preceded by its timestamp in the video, in the following format: [start-end] [transcript]. " 
        })
        content.append({"type":"text", "text": prompt})  

        chat_history = [
            {
                "role": "user",
                "content": content
            }
        ] 
    
        return chat_history

    # immagini e transcript con timestamp concatenati con funzione in concat.py
    # concat_path è il path al pickle file in cui sono allineati frames e transcript
    #frames_path è il path alla cartella con i frame del video 
    
    @staticmethod
    def init_chat_history_it_concat(frames_tar, concat_path, prompt):

        with open(concat_path, "rb") as file:
            concat = pk.load(file)

        content = []

        with tarfile.open(frames_tar, "r") as tar:
            
            members_by_name = {Path(m.name).name: m for m in tar.getmembers() if m.isfile()}

            for d in concat:
                for img in d["images"]:
                    img_filename = f"{img}"

                    if img_filename not in members_by_name:
                        print(f"ATTENZIONE: '{img_filename}' non trovato nel tar, salto")
                        continue

                    member = members_by_name[img_filename]
                    img_bytes = tar.extractfile(member).read()
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

                    content.append({"type": "image", "image": pil_img})

                content.append({"type": "text", "text": d["timestamp"]})
                content.append({"type": "text", "text": d["text"]})

        content.append({"type": "text", "text":
            "Video keyframes are followed by the start and end timestamp in which they appear in the video, and the associated transcription of the audio, in the following format: [image1, image2, image3, ...] [start-end] [transcript]"
        })
        content.append({"type": "text", "text": prompt})

        chat_history = [
            {
                "role": "user",
                "content": content
            }
        ]

        return chat_history

    @staticmethod
    def init_chat_history_test(question:str):
        #to test if the model works
        chat_history = [
            {
                "role": "user",
                "content":[
                    {"type": "text", "text": question},
                ]
            }
        ]
        return chat_history

    @staticmethod
    def init_chat_history_image_test(image_path):
        chat_history = [
                    {
                        "role": "user",
                        "content":[
                            {"type": "image", "image":image_path},
                            {"type": "text", "text": "describe the image"},
                        ]
                    }
                ]
        return chat_history

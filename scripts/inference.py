from path import Path
import traceback
import os
import gc
import torch
import av
import pandas as pd
import pickle
import tarfile
from transformers import AutoProcessor, AutoModelForMultimodalLM
from prompt import Prompt, PROMPTS
from chat import ChatHistory
from paths import DatasetPaths, CT_VIDEOS, VIDEOS_SAMPLE_100, VIDEOS_SAMPLE_1000, CT_NOVTT



DATASET_METRICS = "/leonardo_work/IscrC_MARGOT/igugliel/dataset_metrics"

PROBLEMS_LOG = "/leonardo_work/IscrC_MARGOT/igugliel/classification_results/problems.txt"
#MODEL_ID = f"{os.environ['FAST']}/models/gemma-4-E4B-it" 
MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"
#MODEL_ID = "Qwen/Qwen3-VL-32B-Instruct"


#TODO: sostituire iterazione su elenco transcript con iterazione su id validi

def get_model_response(chat_history, model, processor, metadata={}):

  inputs = processor.apply_chat_template(
    chat_history,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    add_generation_prompt=True,
    processor_kwargs ={
      #"num_frames" : 60
      "do_sample_frames":False,
      "video_metadata" : [metadata]
    }
    
    
  ).to(model.device)

  # with torch.no_grad():
  with torch.inference_mode():
    outputs =model.generate(**inputs, max_new_tokens=140)
  
  
  
  generated_ids = outputs[:, inputs["input_ids"].shape[-1]:]
  response = processor.decode(generated_ids[0], skip_special_tokens=True)

  del outputs, inputs, generated_ids
  gc.collect()
  torch.cuda.empty_cache()

  return response


#TODO:trovare modo di parametrizzare il nome del modello usato nel tipo di classificazione
def transcript_classification(model, processor, prompt:Prompt, dataset_paths:DatasetPaths, model_name:str):
  #unpickle transcripts
  
  simple_transcript = dataset_paths.transcript_simple / "transcript"
  with open(simple_transcript, "rb") as pk:
    transcripts_dict = pickle.load(pk)

  classification = []

  for key, value in transcripts_dict.items():
    ch = ChatHistory.init_chat_history_t(value, prompt.prompt_body)

    response = get_model_response(ch, model, processor)
    classification.append({"video_id": key, f"classification_{model_name}": response})

  #try to open results to append if the csv exists, otherwise create it 
  results_file_path = Path(f"{dataset_paths.results}/classification_t_{prompt.prompt_type.value}")
  
  #TODO:TESTARE
  if results_file_path.exists():

    results_file = pd.read_csv(results_file_path)
    new_results = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
    # to be sure: cast video_id to string on both dataframes
    results_file = results_file.astype({"video_id":str})
    new_results = new_results.astype({"video_id":str})
    df = results_file.merge(new_results, how="outer", on="video_id")
  else:
    df = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
  
  df.to_csv(results_file_path, index = False)

def video_classification(model, processor, prompt:Prompt, dataset_paths:DatasetPaths, model_name:str):
  #in realta non dovrei usare le key del transcript come indice perchè potrebbe non esserci un transcript, nella versione finale iterare sulla cartella contenente i video
  simple_transcript = dataset_paths.transcript_simple / "transcript"
  with open(simple_transcript, "rb") as pk:
    transcripts_dict = pickle.load(pk)

  classification = []
  problematic_videos = []
  for key in transcripts_dict.keys():
    try:
      video_path = dataset_paths.raw_videos / key
      print(video_path, flush=True)
      ch, metadata = ChatHistory.init_chat_history_v(str(video_path), prompt.prompt_body)
      response = get_model_response(ch, model, processor, metadata)
      print(response, flush=True)
      classification.append({"video_id": key, f"classification_{model_name}": response})
    except Exception as e :
      print(e, flush=True)
      traceback.print_exc()
      gc.collect()
      torch.cuda.empty_cache()
      #problematic_videos.append(f"problem with {key} in video classification {prompt.prompt_type.value}")
    
  with open(PROBLEMS_LOG, "a") as f:
    f.write("\n".join(problematic_videos))

  results_file_path = Path(f"{dataset_paths.results}/classification_v_{prompt.prompt_type.value}")
  
  if results_file_path.exists():
  
    results_file = pd.read_csv(results_file_path)
    new_results = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
    # to be sure: cast video_id to string on both dataframes
    results_file = results_file.astype({"video_id":str})
    new_results = new_results.astype({"video_id":str})
    df = results_file.merge(new_results, how="outer", on="video_id")
  else:
    df = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
  
  df.to_csv(results_file_path, index = False)


def handle_exception(e: Exception, problematic_videos: set, video_id):
  traceback.print_exc()
  print(e)
  problematic_videos.add(video_id)


#video con uniform sampling a max 30 frame tot, transcript senza timestamp
def vt_classification(model, processor, prompt:Prompt, dataset_paths:DatasetPaths, model_name:str):

  simple_transcript = dataset_paths.transcript_simple / "transcript"
  with open(simple_transcript, "rb") as pk:
      transcripts_dict = pickle.load(pk)
  
  classification = []
  problematic_videos = []

  for key, value in transcripts_dict.items():
    try:
      video_path = dataset_paths.raw_videos / key
      
      ch, metadata = ChatHistory.init_chat_history_vt(str(video_path), value, prompt.prompt_body)
      response = get_model_response(ch, model, processor, metadata)
      classification.append({"video_id": key, f"classification_{model_name}": response})
    except Exception as e :
      print(e, flush=True)
      traceback.print_exc()
      gc.collect()
      torch.cuda.empty_cache()
      #problematic_videos.append(f"problem with {key} in video transcript classification {prompt.prompt_type.value}")

  with open(PROBLEMS_LOG, "a") as f:
    f.write("\n".join(problematic_videos))
  
  results_file_path = Path(f"{dataset_paths.results}/classification_vt_{prompt.prompt_type.value}")
  if results_file_path.exists():
    
    results_file = pd.read_csv(results_file_path)
    new_results = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
    
    # to be sure: cast video_id to string on both dataframes
    results_file = results_file.astype({"video_id":str})
    new_results = new_results.astype({"video_id":str})
    
    df = results_file.merge(new_results, how="outer", on="video_id")
  else:
    df = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
  
  df.to_csv(results_file_path, index = False)
# testo e immagini con timestamp ma non concatenati
# keyframes_dir è la directory del tipo di frames che si vogliono utilizzare 
# problema con DatasetPaths: contiene tutte le directory e quindi sia iframes che shotbaes. come indicare quale delle due usare? sarebbe meglio
# duplicare il codice e fare due funzioni dicverse o passare eparatamente le dir, rendendo inutile la comodità di avere in un solo oggetto tutti i path? 
# 
def it_classification(model, processor, keyframes_dir:Path, prompt:Prompt, dataset_paths:DatasetPaths, model_name:str):

  keyframes_type = keyframes_dir.stem
  classification = []
  problematic_videos=[]  
  results_file_path = Path(f"{dataset_paths.results}/classification_it_{prompt.prompt_type.value}_{keyframes_type}")
  
  
  for file in dataset_paths.transcript_timestamped.iterdir():
    
    video_id = Path(file).stem
    
    try:
      keyframes = str(keyframes_dir / "frames" / f"{video_id}.tar")
      keyframes_ts = str(keyframes_dir/ f"{video_id}.csv")
      ch = ChatHistory.init_chat_history_it(keyframes, keyframes_ts, file, prompt.prompt_body)
      response = get_model_response(ch, model, processor)
      print(f"video id: {video_id}, classification:{response}")
      classification.append({"video_id": video_id, f"classification_{model_name}": response})
    
    except Exception as e :
      print(f"problem with video {video_id} \n chat history passed: {ch}")
      print(e, flush=True)
      traceback.print_exc()
      #problematic_videos.append(f"problem with {video_id} in image-transcript classification {prompt.prompt_type.value}")
      
  with open(PROBLEMS_LOG, "a") as f:
    f.write("\n".join(problematic_videos))

  

  if results_file_path.exists():
      
    results_file = pd.read_csv(results_file_path)
    new_results = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
    # to be sure: cast video_id to string on both dataframes
    results_file = results_file.astype({"video_id":str})
    new_results = new_results.astype({"video_id":str})
    df = results_file.merge(new_results, how="outer", on="video_id")
  else:
    df = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])

  df.to_csv(results_file_path, index = False)





#keyframes dir e concat dir sono per scegliere se usare i frame shotbased o iframe
def it_concat_classification(model, processor, keyframes_dir:Path, concat_dir:Path, prompt:Prompt, dataset_paths:DatasetPaths, model_name:str):
  keyframes_type = keyframes_dir.stem
  classification = []
  problematic_videos=[]  
  for file in concat_dir.iterdir():
    video_id = Path(file).stem
    try:
      
      #GET THE FOLDER WITH THE IMAGES
      keyframes = str(keyframes_dir/"frames"/ f"{video_id}.tar")
      
      ch = ChatHistory.init_chat_history_it_concat(keyframes, file, prompt.prompt_body)
      response = get_model_response(ch, model, processor)
      classification.append({"video_id": video_id, f"classification_{model_name}": response})
    except Exception as e :
      print(e, flush=True)
      traceback.print_exc()
      #problematic_videos.append(f"problem with {video_id} in image transcript concat classification {prompt.prompt_type.value}")

  with open(PROBLEMS_LOG, "a") as f:
    f.write("\n".join(problematic_videos))

  results_file_path = Path(f"{dataset_paths.results}/classification_it_concat_{prompt.prompt_type.value}_{keyframes_type}")
  if results_file_path.exists():
      
    results_file = pd.read_csv(results_file_path)
    new_results = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
    # to be sure: cast video_id to string on both dataframes
    results_file = results_file.astype({"video_id":str})
    new_results = new_results.astype({"video_id":str})
    df = results_file.merge(new_results, how="outer", on="video_id")
  else:
    df = pd.DataFrame(classification, columns = ["video_id", f"classification_{model_name}"])
  df.to_csv(results_file_path, index = False)


def main():
  #import gemma model
  processor = AutoProcessor.from_pretrained(MODEL_ID)
  model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    device_map="auto",
    

  ).eval()

  it_classification(model, processor, VIDEOS_SAMPLE_1000.shotbased, PROMPTS[1], VIDEOS_SAMPLE_1000, "qwen3VL_8BI")


  

  

  
  


if __name__ == "__main__":
  main()

  # #test per capire problema con video class passando solo il link
  # processor = AutoProcessor.from_pretrained(MODEL_ID)
  # model = AutoModelForMultimodalLM.from_pretrained(
  #   MODEL_ID,
  #   dtype="auto",
  #   device_map="auto",
    

  # ).eval()
  # vp = processor.video_processor
  # print(vp.num_frames, vp.fps, vp.do_sample_frames, flush=True)
  # #se c'è un numero di frames max (num_frames) allora settale a 60, altrimenti niente
  # #TODO: la logica non è molto corretta percè non sto tenendo conto di modelli che accettano meno di 60 frames. modificare in caso
  # if vp.num_frames:
  #   vp.num_frames = 60 
  # print(vp.num_frames, vp.fps, vp.do_sample_frames, flush=True)
  # video_path = "/leonardo_work/IscrC_MARGOT/dataset/ct_tmp/6995807655415614726.mp4"
  # ch, metadata = ChatHistory.init_chat_history_v(video_path, "Shortly describe what happens in the video", vp.num_frames, vp.fps)
  # try:
  #   result = get_model_response(ch, model, processor, metadata)
  #   print(result, flush=True)
  # except Exception as e:
  #   print(e, flush = True)
  #   traceback.print_exc()


from path import Path
import torch
import pandas as pd
import whisper
import nltk
import pickle
from tqdm import tqdm
import argparse
from paths import DatasetPaths, VIDEOS_SAMPLE_1000, CT_NOVTT, CT_VIDEOS, VIDEOS_SAMPLE_100, MIXED_SAMPLE_1000, BALANCED_SAMPLE_2K


PROBLEMS = "/leonardo_work/IscrC_MARGOT/igugliel/corrupted_videos.txt"

def get_transcript(input_file:Path, whisper_model):
    
    transcript = whisper_model.transcribe(input_file)
    text = transcript.get("text")
    return text



#get both simple and timestamped transcript running whisper only once
def get_transcripts(input_file:Path, whisper_model):

  transcript = whisper_model.transcribe(str(input_file))
  #result =[]
  simple_transcript = transcript.get("text")
  #result.append(transcript.get("text"))

  timestamped = []

  for segment in transcript["segments"]:
    
    timestamped.append({'start':round(segment['start'],2), 'end': round(segment['end'],2), 'text':segment['text']})

  timestamped_df = pd.DataFrame(timestamped, columns = ['start','end', 'text'])
  convert_dict = {'start': float, 'end': float, 'text': str}
  timestamped_df = timestamped_df.astype(convert_dict)

  #result.append(df)

  return simple_transcript, timestamped_df



#language detection
def is_half_in_english(transcript:str):

  words = nltk.word_tokenize(transcript.lower())
  english_vocab = set(nltk.corpus.words.words())
  num_english_words = sum(1 for word in words if word in english_vocab)

  # Check if at least half of the words are in the English vocabulary
  return num_english_words >= len(words) / 2 and len(words) >=10


  


def extract_all(dir:DatasetPaths):

  dir.ensure_dirs()
  not_english_count = 0
  corrupted_count = 0
  
  #NOTA: PER IL SAMPLE DA 1000 USO FASTER WHISPER

  whisper_model = whisper.load_model("large")


  processed_dict = {}
  
 
  for files in dir.raw_videos.iterdir():
    try:
    
      simple_transcript, timestamped_df = get_transcripts(files, whisper_model)
      
      res = is_half_in_english(simple_transcript)

      if(res):

        #salva semplice transcript in processed. dict avrà transcript di tutti i video nel sample
        print(files.name, flush=True)
        processed_dict[f'{files.name}'] = simple_transcript

        #il timestamped di ogni video è salvato in un dataframe
        timestamped_df.to_csv(f"{dir.transcript_timestamped}/{files.stem}.csv")
      else:
         not_english_count += not_english_count
    except Exception as e:
       print(f"errore durante l'estrazione del transcript di {files.name}", flush=True)
       corrupted_count += corrupted_count

  problems_string = f"dataset {dir.name} -> non-english videos: {not_english_count}, corrupted videos: {corrupted_count} \n"
  
  with open(PROBLEMS, "a") as p:
     p.write(problems_string)
  
  with open(f'{dir.transcript_simple}/transcript', 'ab') as tr_file:
    pickle.dump(processed_dict, tr_file)
  
def extract_all_chunked(dir: DatasetPaths, chunk_id: int = 0, num_chunks: int = 1):
    dir.ensure_dirs()
      
    not_english_count = 0
    corrupted_count = 0
    whisper_model = whisper.load_model("large", device="cuda")

    all_files = sorted(dir.raw_videos.iterdir())
    my_files = all_files[chunk_id::num_chunks]   # slicing a interleaving distribuisce equamente

    processed_dict = {}

    for files in my_files:
        try:
            simple_transcript, timestamped_df = get_transcripts(files, whisper_model,)
            res = is_half_in_english(simple_transcript)
            if res:
              print(files.name, flush=True)
              processed_dict[f'{files.name}'] = simple_transcript
              timestamped_df.to_csv(f"{dir.transcript_timestamped}/{files.stem}.csv")
            else:
              print(f"scartato video {files.name} perchè non in lingua inglese", flush=True)      
              not_english_count += not_english_count
        except Exception as e:
            print(f"errore durante l'estrazione del transcript di {files.name}: {e}", flush=True)
            corrupted_count += corrupted_count
    
    #non posso scrivere su un unico file perchè ho esecuzione parallela, quindi scrivi su output del singolo job
    problems_string = f"dataset {dir.name} -> non-english videos: {not_english_count}, corrupted videos: {corrupted_count} \n"
    print(problems_string)
    
    # file separato per chunk, per evitare scritture concorrenti sullo stesso file
    with open(f'{dir.transcript_simple}/transcript_chunk{chunk_id}.pkl', 'wb') as tr_file:
        pickle.dump(processed_dict, tr_file)



if __name__ == "__main__":
  #extract_all(MIXED_SAMPLE_1000)

  #se esecuzione parallela
  parser = argparse.ArgumentParser()
  parser.add_argument("--chunk_id", type=int, default=0)
  parser.add_argument("--num_chunks", type=int, default=1)
  args = parser.parse_args()

  extract_all_chunked(CT_NOVTT, chunk_id=args.chunk_id, num_chunks=args.num_chunks)


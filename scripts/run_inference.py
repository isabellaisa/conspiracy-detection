from inference import video_classification, vt_classification, it_classification, it_concat_classification, transcript_classification
from paths import DatasetPaths, MIXED_SAMPLE_1000, CT_VIDEOS, CT_NOVTT, VIDEOS_SAMPLE_1000
from transformers import AutoProcessor, AutoModelForMultimodalLM
from prompt import Prompt, SIMPLE_PROMPT, DEFINITION_PROMPT
import os
import torch
import gc
import traceback
import argparse

OOM_LOG = "/leonardo_work/IscrC_MARGOT/igugliel/classification_results/oom_log.txt"
PROBLEMS_LOG = "/leonardo_work/IscrC_MARGOT/igugliel/classification_results/problems.txt"
#MODEL_ID = f"{os.environ['FAST']}/models/gemma-4-E4B-it"
# MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"
MODEL_ID = "Qwen/Qwen3-VL-32B-Instruct"
# in totale devo eseguire 14 funzioni - 7 simple, 7 con def. dato che non posso dividerei in chunk i video per il modo in cui ho scritto le funzioni 
# di inferenza (capire se è possibile modificare questa cosa senza disruggere il progetto) posso almeno spostare ogni funzione su un job diverso. 
# la funzione run inference può avere un case switch con id dei chingk, in base a id esegeu funzione diversa?

def run_inference_chunked(dir: DatasetPaths, model_name:str, model_id:str, chunk_id: int = 0, num_chunks: int = 1):
    
    dir.ensure_dirs()
    
    #load the model

    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForMultimodalLM.from_pretrained(
        model_id,
        dtype="auto",
        device_map="auto",
        
    
    ).eval()

    
    tasks = {
        0: lambda : transcript_classification(model, processor, SIMPLE_PROMPT, dir, model_name),
        1: lambda: transcript_classification(model, processor, DEFINITION_PROMPT , dir, model_name),
        2: lambda: video_classification(model, processor, SIMPLE_PROMPT, dir, model_name),
        3: lambda: video_classification(model, processor, DEFINITION_PROMPT, dir, model_name),
        4: lambda: vt_classification(model, processor, SIMPLE_PROMPT, dir, model_name),
        5: lambda: vt_classification(model, processor, DEFINITION_PROMPT, dir, model_name),
        6: lambda: it_classification(model, processor, dir.iframes, SIMPLE_PROMPT, dir, model_name) ,
        7: lambda: it_classification(model, processor, dir.iframes, DEFINITION_PROMPT, dir, model_name),
        8: lambda: it_classification(model, processor, dir.shotbased, SIMPLE_PROMPT, dir, model_name) ,
        9: lambda: it_classification(model, processor, dir.shotbased, DEFINITION_PROMPT, dir, model_name),
        10: lambda: it_concat_classification(model, processor, dir.iframes, dir.concat_iframes, SIMPLE_PROMPT, dir, model_name) ,
        11: lambda: it_concat_classification(model, processor, dir.iframes, dir.concat_iframes, DEFINITION_PROMPT, dir, model_name),
        12: lambda: it_concat_classification(model, processor, dir.shotbased, dir.concat_shotbased, SIMPLE_PROMPT, dir, model_name),
        13: lambda: it_concat_classification(model, processor, dir.shotbased, dir.concat_shotbased, DEFINITION_PROMPT, dir, model_name),
        14: lambda: it_classification(model, processor, dir.trnsntv2, SIMPLE_PROMPT, dir, model_name),
        15: lambda: it_classification(model, processor, dir.trnsntv2, DEFINITION_PROMPT, dir, model_name),
        16: lambda: it_concat_classification(model, processor, dir.trnsntv2, dir.concat_trnsntv2, SIMPLE_PROMPT, dir, model_name),
        17: lambda: it_concat_classification(model, processor, dir.trnsntv2, dir.concat_trnsntv2, DEFINITION_PROMPT, dir, model_name)
        
    }

    problem_tasks = {

        0: lambda: it_classification(model, processor, dir.trnsntv2, SIMPLE_PROMPT, dir, model_name),
        1: lambda: it_classification(model, processor, dir.trnsntv2, DEFINITION_PROMPT, dir, model_name),
        2:lambda: it_classification(model, processor, dir.shotbased, SIMPLE_PROMPT, dir, model_name) ,
        3: lambda: it_classification(model, processor, dir.shotbased, DEFINITION_PROMPT, dir, model_name),
        4: lambda: it_classification(model, processor, dir.iframes, SIMPLE_PROMPT, dir, model_name) ,
        5: lambda: it_classification(model, processor, dir.iframes, DEFINITION_PROMPT, dir, model_name)

    }


    try :
        tasks[chunk_id]()
        #problem_tasks[chunk_id]()
    except torch.cuda.OutOfMemoryError:
       #log_failure(video_id, "oom")
       with open(OOM_LOG, "a") as p:
           p.write(f"oom error at chunk {chunk_id}. trace: {traceback.print_exc()}")
       gc.collect()
       torch.cuda.empty_cache()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk_id", type=int, default=0)
    parser.add_argument("--num_chunks", type=int, default=1)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model_name")
    args = parser.parse_args()

    DATASETS = {"VIDEOS_100": VIDEOS_SAMPLE_1000, "CT_NOVTT": CT_NOVTT}
    #dataset = DATASETS[args.dataset]
    MODELS = {
        "gemma4_E4B": f"{os.environ['FAST']}/models/gemma-4-E4B-it",
        "gemma4_31BIT": "google/gemma-4-31B-it", 
        "qwen3VL_8BI": "Qwen/Qwen3-VL-8B-Instruct",
        "qwen3VL_32BI": "Qwen/Qwen3-VL-32B-Instruct",

    }
    # model_name = "qwen3VL_8BI"
    model_name = args.model_name
    model_id = MODELS[model_name]
    
    # model_name = "qwen3VL_32BI"
    run_inference_chunked(VIDEOS_SAMPLE_1000, model_name, model_id, chunk_id=args.chunk_id, num_chunks=args.num_chunks)
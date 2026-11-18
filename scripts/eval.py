from path import Path
import pandas as pd
from paths import DatasetPaths, CT_VIDEOS, VIDEOS_SAMPLE_100, MIXED_SAMPLE_1000
 
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
CT_RESULTS_DIR = "/leonardo_work/IscrC_MARGOT/classification_results/CT_videos"
CT_EVALUATION_DIR = "/leonardo_work/IscrC_MARGOT/classification_results/evaluation"

#TODO: RIVEDERE TUTTO


def eval_classification_naive(dataset: DatasetPaths, truth):

  evaluation = []

  for file in dataset.results.iterdir():

    classification_method = Path(file).stem
    results_df = pd.read_csv(file)
    rows, columns = results_df.shape
    ground_truth = [1*truth]*rows

    accuracy = accuracy_score(ground_truth, results_df["classification"])
    accuracy = round(accuracy, 2)
    recall = recall_score(ground_truth, results_df["classification"], pos_label = 1)
    recall = round(recall,2)
    f1 = f1_score(ground_truth, results_df["classification"], pos_label = 1)
    f1= round(f1,2)
    evaluation.append({"classification method":classification_method, "accuracy":accuracy, "recall":recall, "f1":f1})

  df = pd.DataFrame(evaluation, columns = ["classification method", "accuracy", "recall", "f1"])
  df.to_csv(f"{CT_EVALUATION_DIR}/classification_eval_{dataset.name}.csv")

# def tmp():
#   accuracy = round(
#         accuracy_score(ground_truth["label"], results_df["classification"]),
#         2
#         )
#   recall = round(
#     recall_score(ground_truth["label"], results_df["classification"], pos_label = 1),
#     2
#   )
#   precision = round(
#     precision_score(ground_truth["label"], results_df["classification"], pos_label = 1),
#     2
#   )
#   f1 = round(
#     f1_score(ground_truth["label"], results_df["classification"], pos_label = 1),
#     2
#   )
#   evaluation.append({"classification method":classification_method, "accuracy":accuracy, "precision": precision, "recall":recall, "f1":f1})
#   df = pd.DataFrame(evaluation, columns = ["classification method", "accuracy", "precision", "recall", "f1"])
#   df.to_csv(f"{CT_EVALUATION_DIR}/classification_eval_{dataset.name}.csv")

def eval_classification(dataset: DatasetPaths, truth:str, model:str):
  """truth is the path to the csv with ids and labels"""
  # make sure that both classification and ground truth have the video_id column as string type
  ground_truth_all = pd.read_csv(truth)
  ground_truth_all = ground_truth_all.astype({"video_id":str}).sort_values(by="video_id")
  #print(f"ground truth all shape: {ground_truth_all.shape}", flush=True)
  #print(f"ground truth all columns: {ground_truth_all.columns}", flush=True)
  evaluation = []
  
  for file in dataset.results.iterdir():
    
    classification_method = Path(file).stem
    results_df = pd.read_csv(file)
    # questo deve diventare:prendi tutte le colonne e fai cast a string 
    # passaggio necessario in caso ci fosse non compliance e oltre alla classificaszione ha dato come output anche del testo
    results_df = results_df.astype({"video_id":str, f"classification_{model}":str}).sort_values(by="video_id")
    results_df["video_id"] = results_df["video_id"].str.replace(".mp4", "", regex=False)
    
    # mantieni solo la classificazione. questo deve essere parametrizzato su tutte le colonne di classificazione
    results_df[f"classification_{model}"]=results_df[f"classification_{model}"].apply(lambda x: ''.join(filter(str.isdigit, x)))
    results_df = results_df.astype({f"classification_{model}":int})
    
    ground_truth = pd.merge(results_df, ground_truth_all, on="video_id", how="inner")
    ground_truth = ground_truth.astype({"video_id":str}).sort_values(by="video_id")
    
    #print(f"{classification_method} ground truth after merge {ground_truth.shape},{ground_truth.columns}", flush=True)

    # add  code in tmp here
    accuracy = round(
            accuracy_score(ground_truth["label"], ground_truth[f"classification_{model}"]),
            2
            )
    recall = round(
      recall_score(ground_truth["label"], ground_truth[f"classification_{model}"], pos_label = 1),
      2
    )
    precision = round(
      precision_score(ground_truth["label"], ground_truth[f"classification_{model}"], pos_label = 1),
      2
    )
    f1 = round(
      f1_score(ground_truth["label"], ground_truth[f"classification_{model}"], pos_label = 1),
      2
    )
    evaluation.append({"classification method":classification_method, "accuracy":accuracy, "precision": precision, "recall":recall, "f1":f1})
  df = pd.DataFrame(evaluation, columns = ["classification method", "accuracy", "precision", "recall", "f1"])
  df.to_csv(f"{CT_EVALUATION_DIR}/eval_{dataset.name}_{model}.csv")
    
def eval_classification_complete(dataset:DatasetPaths, ground_truth_path):
  ground_truth = pd.read_csv(ground_truth_path)
  ground_truth = ground_truth.astype({"video_id":str}).sort_values(by="video_id")

  

  for file in dataset.results.iterdir():
      
    classification_method = Path(file).stem
    results_df = pd.read_csv(file)

    results_cols = results_df.columns.to_list()
    #type_dict = {"video_id":str}
    # cast video_id to string, checks if classification contains only 0/1, if not trims non compliant part, then casts classification columns to int
    for col in results_cols:
      #type_dict.update({col: str})
      results_df = results_df.astype({col:str})
      if "classification" in col:
        results_df[col]=results_df[col].apply(lambda x: ''.join(filter(str.isdigit, x)))
        results_df = results_df.astype({col:int})
        
    merged = pd.merge(results_df, ground_truth, on="video_id", how="inner")
    ground_truth = ground_truth.astype({"video_id":str}).sort_values(by="video_id")

  # "file" è il csv del tipo di classificazione(esempio:solo transcript). questo file ha cole righe i video 
  # e come colonne il risultato della classificazione con ogni modello diverso. ora per ognuno di questi file calcolo le varie metriche , per ogni colonna di classificazione.
  # alla fine vorro avere una riga del tipo class_type, metric1, metric2... per ogni modello

def main():
  #eval_classification_naive(CT_VIDEOS, 1)
  #eval_classification_naive(VIDEOS_SAMPLE_100, 0)
  mixed_1000_gt = "/leonardo_work/IscrC_MARGOT/dataset/labels/mixed_sample_1000.csv"
  ct_videos_gt = "/leonardo_work/IscrC_MARGOT/dataset/labels/ct_videos.csv"
  #eval_classification(MIXED_SAMPLE_1000, mixed_1000_gt )
  eval_classification(CT_VIDEOS, ct_videos_gt, "gemma4_E4B")
  eval_classification(CT_VIDEOS, ct_videos_gt, "qwen3VL_8BI")



############### new eval
# costruisci diversi tipi di dataset: 50-50, 70-30, 90-10
# calcola weighted precision, accuracy, recall, f1
# cohen kappa e fleiss kappa per inter annotator agreement

### PULIZIA DEI RISULTATI
# togliere estensione .mp4 dagli id
# eliminare righe che non hanno classificazione numerica, o che hanno classificazione vuota
# trasformare contenuto in int
# estrarre gli id. voglio trovare set di id che è intersezione di tutti gli id di tutte le configurazioni. questi sono gli id validi da usare per evaluation
# da ogni csv posso estrarre ila colonna id e trasformarla in set, poi fare intersezione di tutti con /, tornare indietro e eliminare le righe che non hanno id in set (anche se non mi sembra un metodo molto efficiente)

def clean_results(dataset: DatasetPaths):

  for f in dataset.results.iterdir():

    df = pd.read_csv(f)
    #cast all columns to string, so that i can find rows whose classification does not exclusively contain '0' or '1' 
    df.astype(str)
    #drop rows with empty classification
    df = df.dropna(how="any")







### COSTRUZIONE DATASET 
### prendere gli id dei video che vengono classificati in tutte le config. si trovano con inner join. questi sono gli id dei video validi.
### da questi id sceglierne un certo numero random tra quelli in minoranza / maggioranza usando index. segnarsi la ground truth

### devo trovare il modo di ottenere gli id dei video che sono classificati con tutte le config

def create_new_dataset(d1: DatasetPaths, d2: DatasetPaths, perc1: int, perc2: int, class_label_1: int, class_label_2: int):
  #TODO: capire come/dove salvare
  # d1, d2 sono gli id dei video. dato che l'unico caso in cui ci potrebbe essere una discrepanza è transcript - immagini, prendo un file di class iframes e class transcript, e estraggo gli id da li

  d1_transcript_class = pd.read_csv(d1.results / "classification_t_simple")
  d1_it_class = pd.read_csv(d1.results / "classification_it_simple_iframes")

  d2_transcript_class = pd.read_csv(d2.results / "classification_t_simple")
  d2_it_class = pd.read_csv(d2.results / "classification_it_simple_iframes")

  #build csv con id validi e class label

  d1_data = d1_transcript_class["video_id"].merge(d1_it_class["video_id"], "inner", on="video_id")
  d1_data["class_label"] = class_label_1

  d2_data = d2_transcript_class["video_id"].merge(d2_it_class["video_id"], "inner", on="video_id")
  d2_data["class_label"] = class_label_2

  





if __name__ == "__main__":
  main()
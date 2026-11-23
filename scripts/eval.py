from path import Path
import pandas as pd
from paths import DatasetPaths
 
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score

CT_EVALUATION_DIR = "/leonardo_work/IscrC_MARGOT/classification_results/evaluation"


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








### COSTRUZIONE DATASET 
### prendere gli id dei video che vengono classificati in tutte le config. si trovano con inner join. questi sono gli id dei video validi.
### da questi id sceglierne un certo numero random tra quelli in minoranza / maggioranza usando index. segnarsi la ground truth

### devo trovare il modo di ottenere gli id dei video che sono classificati con tutte le config







if __name__ == "__main__":
  main()
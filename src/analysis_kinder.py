# analyse_kinder
import pandas as pd
import matplotlib as plt
import os

#CSV-Datei einlesen
data_path = "data/kinder_0_6.csv" 
kinder = pd.read_csv(data_path)

#Überprüfen der Daten
print("Erste Zeile der CSV:")
print(kinder.head())

#Diagramm 
plt.figure(figsize=(10,6))

#Prügen, ob `Landkreis`und `Jahr`existieren
if "Landkreis" not in kinder.columns or "Jahr" not in kinder.columns or "Kinder_0_6" not in kinder.columns:
    raise ValueError("CSV muss die Spalten 'Landkreis', 'Jahr' und 'Kinder_0_6' enthalten!")

#Liniendiagramm 
for landkreis in kinder ["Landkreis"]
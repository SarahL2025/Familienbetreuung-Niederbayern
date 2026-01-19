import pandas as pd 
import matplotlib.pyplot as plt


#CSV einlesen
df = pd.read_csv("C:/Users/sarah/Documents/SDC 3 Semester/Datenvisualisierung/Familienbetreuung-Niederbayern/data/kinder_0_6.csv",sep=";", decimal=",", skiprows=[1])

#Jahre als Spalten
jahre = [str(j) for j in range (2003, 2024)]

#Diagramm erstellen
df.set_index('Raumeinheit')[jahre].plot(kind='bar', stacked=True, figsize=(14,7), colormap='tab20')

plt.ylabel('Anzahl der Kinder')
plt.title('Altersstruktur der Kinder 0-6 Jahre in Niederbayern')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

#Diagramm speichern
plt.savefig
plt.show("C:/Users/sarah/Documents/SDC 3 Semester/Datenvisualisierung/Familienbetreuung-Niederbayern/diagrams")
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

#leer excel
df = pd.read_excel('data.xlsx')

#leer los datos 
x = df['texto']
y = df['intent']

#modelo 

modelo = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', LogisticRegression(max_iter=1000))
])


#entrenar el modelo 
modelo.fit(x, y)
#guardar el modelo
joblib.dump(modelo, 'modelo_chatbot.pkl')

print("Modelo entrenado y guardado exitosamente.")


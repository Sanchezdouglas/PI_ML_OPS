import pandas as pd
from sklearn.neighbors import NearestNeighbors

def movie_recomendacion(movie_title):
    # Cargar el archivo CSV con los datos
    movie_data = pd.read_csv('dataset/recomendacion.csv')

    # Buscar la película por título en la columna 'title'
    movie = movie_data[movie_data['title'] == movie_title]

    if len(movie) == 0:
        return "La película no se encuentra en la base de datos."

    # Obtener el género y la popularidad de la película
    movie_genre = movie['genre'].values[0]
    movie_popularity = movie['popularity'].values[0]

    # Crear una matriz de características para el modelo de vecinos más cercanos
    features = movie_data[['popularity']]
    genres = movie_data['genre'].str.get_dummies(sep=' ')
    features = pd.concat([features, genres], axis=1)

    # Manejar valores faltantes (NaN) reemplazándolos por ceros
    features = features.fillna(0)

    # Crear el modelo de vecinos más cercanos
    nn_model = NearestNeighbors(n_neighbors=6, metric='euclidean')
    nn_model.fit(features)

    # Encontrar las películas más similares
    _, indices = nn_model.kneighbors([[movie_popularity] + [0] * len(genres.columns)], n_neighbors=6)

    # Obtener los títulos de las películas recomendadas
    recomendacion = movie_data.iloc[indices[0][1:]]['title']

    return recomendacion



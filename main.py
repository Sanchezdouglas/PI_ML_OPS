
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from recomendacion import movie_recomendacion



from fastapi import FastAPI
import uvicorn

# Creamos la aplicación
app = FastAPI()

# Cargamos los datos
df = pd.read_csv('dataset/cleanmovies.csv', delimiter=';')
recomendacion_df = pd.read_csv('dataset/recomendacion.csv', sep=',', encoding='utf-8')



# Inicial de saludos
@app.get('/')
async def root():
    return {"Bienvenido a nuestra API de películas!"}


#  Acceso para obtener la cantidad de películas por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes):
    mes = mes.lower()

    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    if mes not in meses:
        return {'error': 'Mes inválido'}

    nro_mes = meses.index(mes) + 1

    movies_per_month = df[pd.to_datetime(df['release_date']).dt.month == nro_mes]

    num_movies = str(len(movies_per_month['id'].unique()))
    resultado = num_movies + ' películas estrenadas mes de ' + mes

    return resultado

# Acceso para obtener la cantidad de películas por día
@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia):
    dia = dia.lower()

    dias = ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']

    if dia not in dias:
        return {'error': 'Día inválido'}

    nro_dia = dias.index(dia)

    movies_per_day = df[pd.to_datetime(df['release_date']).dt.dayofweek == nro_dia]

    num_movies = str(len(movies_per_day['id'].unique()))
    resultado = num_movies + ' películas fueron estrenadas en el día ' + dia

    return resultado


# Acceso  score_titulo para el titulo de la filmación
@app.get('/score_titulo/{titulo}')
def score_titulo(titulo):
    titulo = titulo.strip()
    mask = df['title'].str.lower() == titulo.lower()
    movies_filtered = df[mask][['title', 'popularity', 'release_year']]

    if movies_filtered.empty:
        return {'error': 'No se reconoce la película ingresada. Intenta escribirlo nuevamente'}
    else:
        result = []
        for _, row in movies_filtered.iterrows():
            score = row['popularity']
            year = row['release_year']
            result.append({'titulo': titulo, 'anio': year, 'popularidad': score})
        return result

# Acceso  votos_titulo titulo de la filmación  
@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo):
    titulo = titulo.strip()
    mask = df['title'].str.lower() == titulo.lower()
    movies_filtered = df[mask][['title', 'vote_count', 'release_year', 'vote_average']]

    if movies_filtered.empty:
        return {'error': 'No se reconoce la película ingresada. Intenta escribirlo nuevamente'}
    else:
        peliculas = {}
        peliculas['titulo'] = titulo
        votes = []
        years = []
        avg = []
        for _, row in movies_filtered.iterrows():
            vote = row['vote_count']
            if vote > 2000:
                votes.append(vote)
                years.append(int(row['release_year']))
                avg.append(round(row['vote_average'], 1))
        peliculas['anio'] = years
        peliculas['voto_total'] = votes
        peliculas['voto_promedio'] = avg
        if not votes:
            return f'La película {titulo} no cumple con la cantidad mínima de valoraciones requerida'
        else:
            return peliculas


# Acceso get_actor nombre_ de actor 
@app.get('/get_actor/{actor}')
def get_actor(actor):
    actor = actor.strip()
    cadena_texto = df['actor'].astype(str)
    encontrado = cadena_texto.str.contains(actor, case=False)
    df_actor = df[encontrado][['return']]

    if df_actor.empty:
        return {'error': 'No se reconoce el actor ingresado. Intenta escribirlo nuevamente'}
    else:
        count_films = df_actor.shape[0]
        avg_film = round(df_actor['return'].mean(), 2)
        sum_return = round(df_actor['return'].sum(), 2)
        return {'actor': actor, 'cantidad_filmaciones': count_films, 'retorno_total': sum_return, 'retorno_promedio': avg_film}

# Acceso get_director nombre director 
@app.get('/get_director/{Director}', tags=['movies'])
async def get_director(Director:str):
    name = Director.strip()
    cadena_texto = df['director'].astype(str)
    encontrado = cadena_texto.str.contains(name, case=False)
    df_director = df[encontrado][['title', 'release_year', 'return', 'revenue', 'budget']]
    if df_director.empty:
        return 'No se reconoce el director ingresado. Intenta escribirlo nuevamente'
    else:
        peliculas = {}
        df_director['revenue'] = df_director['revenue'].astype(float)
        df_director['budget'] = df_director['budget'].astype(int)
        df_director['return'] = df_director['return'].astype(float)
        sum_return = round(df_director['return'].sum(), 2)
        peliculas['director'] = Director
        peliculas['retorno_total_director'] = sum_return
        titulo = []
        anio = []
        costo = []
        retorno = []
        ganancia = []
        for indice, fila in df_director.iterrows():
            titulo.append(fila['title'])
            anio.append(fila['release_year'])
            retorno.append(round(fila['return'], 2))
            costo.append(fila['budget'])
            ganancia.append(fila['revenue'])
        peliculas['peliculas'] = titulo
        peliculas['anio'] = anio
        peliculas['retorno_pelicula'] = retorno
        peliculas['budget_pelicula'] = costo
        peliculas['revenue_pelicula'] = ganancia
        return peliculas


@app.get('/recomendacion/{titulo}')
def recomendacion(titulo: str):
    peliculas_recomendadas = movie_recomendacion(titulo)
    return {'lista recomendada': peliculas_recomendadas}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)

                                      
                                      
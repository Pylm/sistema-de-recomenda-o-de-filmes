#!/usr/bin/env python3

import pandas as pd
import warnings

# Há alguns avisos do pandas quanto ao fato da matriz de filmes possuir valores nulos, são inofensivos então
# serão ignorados

warnings.simplefilter('ignore')

# O dataset u.csv não possui colunas definidas então criaremos elas

column_names = ['user_id', 'item_id', 'rating', 'timestamp']

# O dataset é separado por tabs e não vírgulas como usual, daí o parâmetro sep no read_csv

df = pd.read_csv('u.csv', sep='\t', names=column_names)

movie_titles = pd.read_csv('Movie_Id_Titles.csv')

# É necessário fundir o dataset de nomes de filmes e usuários, a fusão é realizada na coluna item_id que é comum
# para ambos

df = pd.merge(df, movie_titles, on='item_id')

# Cria a média de avaliações para cada filme e o número de avaliações

ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
ratings['num of ratings'] = pd.DataFrame(df.groupby('title')['rating'].count())


def similar_to(movie, precision=0.5, minimum_nratings=100):

    """
    Função que retorna as recomendações
    :param movie: Nome do filme para o qual você quer as recomendações
    :param precision: Precisão de correlação, o máximo é 1
    :return: lista de filmes parecidos com o filme indicado
    """

    if precision > 1:
        print('O parâmetro precision deve ser de no máximo 1')
        exit()

    # Cria uma matriz onde o index é o ID de usuário e a coluna o filme, os valores são as avaliações em si

    moviemat = df.pivot_table(index='user_id', columns='title', values='rating')

    # Pega as avaliações específicas do filme passado para a função
    movie_ratings = moviemat[movie]

    # Retorna uma série com a correlação entre a matriz inteira de filmes e o filme passado para a função

    similar_to_movie = moviemat.corrwith(movie_ratings)

    # Cria um dataframe com a correlação do filme passado para função com a matriz, é também adicionado a coluna num of
    # ratings para melhorar os resultados, filtrando filmes com poucas avaliações que atrapalhariam a recomendação

    recommended = pd.DataFrame(data=similar_to_movie, columns=['Correlation']).join(ratings['num of ratings'])

    # Finalmente, cria um dataframe filtrado contendo as recomendações apenas de filmes que possuam mais de 100
    # avaliações (para evitar a presença de filmes que um espectador do filme passado tenha visto e avaliado bem
    # mas que não tenha real relevância no dataset. É também filtrado pela correlação onde uma correlação perfeita tem
    # valor 1.
    try:
        recommended_movies = recommended[(recommended['num of ratings'] >= minimum_nratings) & (recommended['Correlation'] >= precision)].sort_values('Correlation', ascending=False).drop(movie)
    except KeyError:
        print('Não há filmes para recomendar, tente diminuir o parâmetro minimum_nratings ou precision')
        exit()

    # Retorna o dataframe filtrado em forma de lista
    return recommended_movies.index.tolist()


movie_list = similar_to('Raiders of the Lost Ark (1981)')

# Printa os filmes um a um

for movie in movie_list:
    print(movie)
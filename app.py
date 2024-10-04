from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests
app = Flask(__name__)

# Load cosine similarity model and movies dataset
cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
movies_df = pd.read_csv('movies.csv')  
# Function to get movie poster URL from TMDB
def get_movie_poster(title):
    api_key = '06a8af23804eaf7fe69ee87882949801'
    base_url = 'https://api.themoviedb.org/3/search/movie'
    poster_base_url = 'https://image.tmdb.org/t/p/w500'

    
    params = {'api_key': api_key, 'query': title}
    response = requests.get(base_url, params=params)
    data = response.json()

    
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return poster_base_url + poster_path
    return None  


# Function to recommend movies
def recommend_movie(title, cosine_sim=cosine_sim):
    title = title.strip().lower()  # Normalize user input
    movies_df['title'] = movies_df['title'].str.lower().str.strip()  # Normalize movie titles

    if title not in movies_df['title'].values:
        return ["Movie not found. Please try another one."]
    
    idx = movies_df[movies_df['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))

    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    
    sim_scores = sim_scores[1:8]
    movie_indices = [i[0] for i in sim_scores]
    
    recommendations = movies_df['title'].iloc[movie_indices].values.tolist()

    recommended_with_posters = []
    for movie in recommendations:
        poster_url = get_movie_poster(movie)
        recommended_with_posters.append((movie, poster_url))

    return recommended_with_posters



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_title = request.form['movie_title']
    print(f"Movie title received: {movie_title}")
    recommendations = recommend_movie(movie_title)
    print(f"Recommendations: {recommendations}")
    return render_template('index.html', movie_title=movie_title, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)

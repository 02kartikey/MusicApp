import base64
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt


def popular_genres_chart(genres_count):
    matplotlib.use('Agg')
    labels = [genre[0].title() for genre in genres_count]
    values = [count[1] for count in genres_count]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    chart_image = BytesIO()
    plt.savefig(chart_image, format='png')
    chart_image.seek(0)
    chart_image_base64 = base64.b64encode(chart_image.getvalue()).decode('utf-8')

    return chart_image_base64


def top_songs_chart(top_rated_songs, likes_dict):
    song_names = [song[0].name for song in top_rated_songs]
    ratings = [song[1] for song in top_rated_songs]
    likes = [likes_dict.get(song[0].id, 0) for song in top_rated_songs]

    fig, ax = plt.subplots()
    bar_width = 0.30
    index = range(len(song_names))

    bar1 = ax.bar(index, ratings, bar_width, label='Avg Rating')
    bar2 = ax.bar([i + bar_width for i in index], likes, bar_width, label='Likes')
    
    ax.set_xlabel('Songs')
    ax.set_ylabel('Values')
    ax.set_title('Top Rated Songs and Their Num of Likes')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(song_names, rotation=45, ha='right')
    ax.legend()

    chart_img = BytesIO()
    plt.savefig(chart_img, format='png')
    chart_img.seek(0)
    chart_img_base64 = base64.b64encode(chart_img.getvalue()).decode('utf-8')

    return chart_img_base64


def top_artists_chart(top_rated_artists, songs_dict):
    artist_names = [artist[0].username for artist in top_rated_artists]
    ratings = [artist[1] for artist in top_rated_artists]
    num_songs = [songs_dict.get(artist[0].id, 0) for artist in top_rated_artists]

    fig, ax = plt.subplots()
    bar_width = 0.30
    index = range(len(artist_names))

    bar1 = ax.bar(index, ratings, bar_width, label="Avg Rating")
    bar2 = ax.bar([i + bar_width for i in index], num_songs, bar_width, label="Num of Songs Uploaded")

    ax.set_xlabel("Artists")
    ax.set_ylabel("Values")
    ax.set_title("Top Rated Artists and Num of Songs Uploaded")
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(artist_names, rotation=45, ha='right')
    ax.legend()

    chart_img = BytesIO()
    plt.savefig(chart_img, format='png')
    chart_img.seek(0)
    chart_img_base64 = base64.b64encode(chart_img.getvalue()).decode('utf-8')

    return chart_img_base64

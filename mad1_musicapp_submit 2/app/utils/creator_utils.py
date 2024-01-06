from app import db
from app.models import Song, Rating, User, likes

def calculateAvgRating(artist):
    all_songs = Song.query.filter_by(artist_id=artist.id).all()

    if not all_songs:
        return None
    
    total_ratings = 0
    num_ratings = 0

    for song in all_songs:
        ratings = Rating.query.filter_by(song_id=song.id).all()
        total_ratings += sum(rating.rating for rating in ratings)
        num_ratings += len(ratings)
    
    if num_ratings == 0:
        return 0
    
    avg_rating = total_ratings / num_ratings
    return round(avg_rating, 1)


def calclulateTotalLikes(songid):
    liking_users = db.session.query(User).join(likes).filter(likes.c.song_id == songid).all()
    total_likes = len(liking_users)

    return total_likes


def get_genres():
    return ["rap", "pop", "rock", "rnb"]
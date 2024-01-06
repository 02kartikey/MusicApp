from app import app, db
from app.models import User, Song, Rating, Playlist, Album, likes, playlist_songs
from datetime import datetime
import random

def create_dummy_user(username, role='user'):
    return User(username=username, password='password', role=role)

def create_dummy_song(name, lyrics, duration, genres, artist):
    if artist.role == 'creator':
        return Song(name=name, lyrics=lyrics, duration=duration, date_created=str(datetime.now().date()), genre=random.choice(genres), artist_id=artist.id)
    else:
        return None

def create_dummy_rating(user, song, rating):
    if user.role == 'user' and song.artist.role == 'creator':
        return Rating(user=user, song=song, rating=rating)
    else:
        return None

def create_dummy_playlist(name, user):
    if user.role == 'user':
        return Playlist(name=name, user=user)
    else:
        return None

def create_dummy_album(name, user):
    if user.role == 'creator':
        return Album(name=name, user=user, date_created=str(datetime.now().date()))
    else:
        return None

def populate_database():
    with app.app_context():
        db.drop_all()  # Drop existing tables
        db.create_all()

        # Create admin account
        admin = create_dummy_user('admin', role='admin')
        db.session.add(admin)

        users = [
            create_dummy_user(f'user_{i}') for i in range(1, 4)
        ] + [
            create_dummy_user(f'creator_{i}', role='creator') for i in range(1, 4)
        ]
        db.session.add_all(users)
        db.session.commit()

        for user in users:
            for i in range(1, 6):
                song = create_dummy_song(f'Song_{i}', f'Lyrics for Song_{i}', random.randint(180, 300), ["rap", "pop", "rock", "rnb"], user)
                if song:
                    db.session.add(song)

                    rating = create_dummy_rating(user, song, random.randint(1, 5))
                    if rating:
                        db.session.add(rating)

                    playlist = create_dummy_playlist(f'Playlist_{i}', user)
                    if playlist:
                        playlist.songs.append(song)
                        db.session.add(playlist)

                    album = create_dummy_album(f'Album_{i}', user)
                    if album:
                        album.songs.append(song)
                        db.session.add(album)

        for user in users:
            for song in Song.query.all():
                if user.role == 'user' and random.choice([True, False]):
                    user.liked_songs.append(song)

        db.session.commit()

if __name__ == '__main__':
    populate_database()

from app import db
from datetime import datetime


## Association ##
likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)


playlist_songs = db.Table(
    'playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)

## Models ##
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary=playlist_songs, backref=db.backref('playlists', lazy='dynamic'))


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.String(20), default=str(datetime.now().date()))
    songs = db.relationship('Song', backref='album', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    liked_songs = db.relationship('Song', secondary=likes, backref=db.backref('liking_users', lazy='dynamic'))
    ratings = db.relationship('Rating', backref='user', lazy=True)
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    albums = db.relationship('Album', backref='user', lazy=True)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.String(20), default=str(datetime.now().date()))
    genre = db.Column(db.String(50), nullable=False)
    ratings = db.relationship('Rating', backref='song', lazy=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

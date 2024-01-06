from flask import redirect, request, session, flash, url_for
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User, Song, Rating, Playlist, Album
from app.middlewares import login_check
from datetime import datetime

class Signup(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha1')
        print(hashed_password)
        
        if ('yes' in request.form.getlist('isCreator')):
            role = 'creator'
        else:
            role = 'user'

        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        session['user'] = {'username': username, 'role': role}

        return redirect('/')


class Login(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        if (user and password == user.password and user.role in ["user", "creator"]):
            # User authenticated successfully
            session['user'] = {'username': user.username, 'role': user.role}
        else:
            flash("Incorrect Username or Password!", 'danger')
        
        return redirect('/')


class AdminLogin(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        if (user and password == user.password and user.role == "admin"):
            # Admin authenticated successfully
            session['user'] = {'username': user.username, 'role': user.role}
            return redirect('/')
        else:
            flash("Incorrect Username or Password!", 'danger')
            return redirect('/admin/login')


class UploadSong(Resource):
    @login_check
    def post(self):
        user = session['user']

        name = request.form['title']
        duration = request.form['duration']     # in seconds
        genre = request.form['genre']
        lyrics = request.form['lyrics']

        artist = User.query.filter_by(username=user['username']).first()

        if not artist:
            flash("User not found!", "danger")
            return redirect('/logout')

        new_song = Song(
            name = name,
            lyrics = lyrics,
            duration = duration,
            date_created = str(datetime.now().date()),
            genre = genre,
            artist_id = artist.id
        )

        db.session.add(new_song)
        db.session.flush()
        new_song_id = new_song.id

        db.session.commit()

        return redirect(url_for('lyrics', songid=new_song_id))

class EditSong(Resource):
    @login_check
    def post(self, songid):
        user = session['user']

        name = request.form['title']
        duration = request.form['duration']
        genre = request.form['genre']
        lyrics = request.form['lyrics']

        artist = User.query.filter_by(username=user['username']).first()

        if not artist:
            flash("User not found!", "danger")
            return redirect('/logout')
        
        song = Song.query.filter_by(id=songid).first()

        song.name = name
        song.duration = duration
        song.genre = genre
        song.lyrics = lyrics

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            flash("Something went wrong while updating song.", "danger")
            return redirect('/')


class ManageSongLike(Resource):
    @login_check
    def get(self, songid):
        user = session['user']
        
        if user['role'] != 'user':
            flash("You are not allowed to like a song!", "danger")
            return redirect('/')
        
        user = User.query.filter_by(username=user['username']).first()

        if not user:
            flash("User not found!", "danger")
            return redirect('/logout')
        
        song = Song.query.filter_by(id=songid).first()

        if not song:
            flash("Song not found", "danger")
            return redirect('/')
        
        if song in user.liked_songs:
            # remove from liked songs if already liked
            user.liked_songs.remove(song)
        else:
            # Otherwise like the song
            user.liked_songs.append(song)

        db.session.commit()
        return redirect(url_for('lyrics', songid=songid))


class ManageSongRating(Resource):
    @login_check
    def get(self, songid, rating):
        if not (0 <= rating <= 5):
            flash("Invalid rating!", "danger")
            return redirect(url_for('lyrics', songid=songid))

        user = session['user']

        if user['role'] != 'user':
            flash("You are not allowed to rate a song!", "danger")
            return redirect('/')

        user = User.query.filter_by(username=user['username']).first()

        if not user:
            flash("User not found!", "danger")
            return redirect('/logout')

        song = Song.query.filter_by(id=songid).first()

        if not song:
            flash("Song not found", "danger")
            return redirect('/')

        # Check if user had already rated this song
        existing_rating = Rating.query.filter_by(user_id=user.id, song_id=song.id).first()

        if existing_rating:
            # update existing rating
            existing_rating.rating = rating
        else:
            new_rating = Rating(user_id=user.id, song_id=song.id, rating=rating)
            db.session.add(new_rating)

        db.session.commit()

        return redirect(url_for('lyrics', songid=songid))


class ManagePlaylist(Resource):
    @login_check
    def post(self, playlistid):
        user = session['user']

        if user['role'] != 'user':
            flash("You can't manage playlists", "danger")
            return redirect('/')
        
        user = User.query.filter_by(username=user['username']).first()
        playlist = Playlist.query.get(playlistid) if playlistid else Playlist()

        name = request.form.get('name')
        selected_ids = request.form.getlist('selected_songs')

        if not name or not selected_ids:
            flash("Please provide a name for the playlist and select at least one song.", "danger")
            return redirect(url_for('playlist_create'))

        playlist.name = name
        playlist.user_id = user.id
        playlist.songs.clear()  # Remove existing

        for song_id in selected_ids:
            song = Song.query.get(song_id)
            if song:
                playlist.songs.append(song)


        db.session.add(playlist)
        db.session.flush()

        new_playlist_id = playlist.id
        db.session.commit()

        return redirect(url_for('playlist_info', playlistid=new_playlist_id))


class ManageAlbum(Resource):
    @login_check
    def post(self, albumid):
        user = session['user']
        
        if user['role'] != "creator":
            flash("You can't manage albums", "danger")
            return redirect('/')

        user = User.query.filter_by(username=user['username']).first()
        if not user:
            flash("User not found!", "danger")
            return redirect('/logout')
        
        album = Album.query.get(albumid) if albumid else Album()

        name = request.form.get('name')
        selected_ids = request.form.getlist('selected_songs')

        if not name or not selected_ids:
            flash("Please provide a name for the album and select at least one song!", "danger")
            return redirect(url_for('album_create'))
        
        album.name = name
        album.user_id = user.id
        album.songs.clear()

        for song_id in selected_ids:
            song = Song.query.get(song_id)
            if song:
                album.songs.append(song)
        
        db.session.add(album)
        db.session.flush()

        new_album_id = album.id
        db.session.commit()

        return redirect(url_for('album_info', albumid=new_album_id))


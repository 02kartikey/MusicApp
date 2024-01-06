from flask import render_template, session, redirect, flash
from flask_restful import Api
from app.api import (
    Signup,
    Login,
    UploadSong,
    EditSong,
    ManageSongLike,
    ManageSongRating,
    ManagePlaylist,
    ManageAlbum,
    AdminLogin
)

from app import app
from app import db
from app.models import User, Song, Rating, Playlist, Album, likes
from app.middlewares import login_check, admin_check
from random import shuffle
from app.utils.creator_utils import calculateAvgRating, calclulateTotalLikes, get_genres
from app.utils.graphs import popular_genres_chart, top_songs_chart, top_artists_chart

api = Api(app)
genres = get_genres()

@app.route("/")
@login_check
def home_page():
    user = session["user"]

    user = db.session.query(User).filter_by(username=user["username"]).first()
    if user.role == "user":
        # songs = db.session.query(Song).all()
        # songs_data = [
        #     {
        #         'id': song.id,
        #         'name': song.name,
        #         'genre': song.genre
        #     } for song in songs
        # ]
        # # Shuffle the songs data
        # shuffle(songs_data)

        playlists = db.session.query(Playlist).filter_by(user_id=user.id).all()
        playlist_data = [
            {"id": playlist.id, "name": playlist.name} for playlist in playlists
        ]

        liked_songs = user.liked_songs
        liked_songs_data = [{"id": song.id, "name": song.name} for song in liked_songs]

        # genres = ["lofi", "epicore", "pop", "edm", "rock", "jazz", "rnb", "techno"]
        songs_by_genre = {}

        for genre in genres:
            songs_genre = db.session.query(Song).filter_by(genre=genre).all()
            songs_genre_data = [
                {"id": song.id, "name": song.name} for song in songs_genre
            ]
            songs_by_genre[genre] = songs_genre_data

        top_rated_songs = (
            db.session.query(Song, db.func.avg(Rating.rating).label("avg_rating"))
            .join(Rating, Song.id == Rating.song_id)
            .group_by(Song.id)
            .order_by(db.desc("avg_rating"))
            .limit(10)
            .all()
        )

        top_rated_songs_data = [
            {"id": song.id, "name": song.name, "avg_rating": avg_rating}
            for song, avg_rating in top_rated_songs
        ]

        albums = db.session.query(Album).all()
        albums_data = [{"id": album.id, "name": album.name} for album in albums]

        _songs = {
            "playlists": playlist_data,
            "liked": liked_songs_data,
            "genre": songs_by_genre,
            "top_rated": top_rated_songs_data,
            "albums": albums_data
        }

        return render_template("user_dash.html", songs=_songs)
    elif user.role == "creator":
        artist = db.session.query(User).filter(User.username == user.username).first()

        if not artist:
            flash("Something Went Wrong, Login Again!", "danger")
            return redirect("/logout")

        songs = db.session.query(Song).filter(Song.artist_id == artist.id).all()
        songs_data = [
            {"id": song.id, "name": song.name, "genre": song.genre} for song in songs
        ]

        avg_rating = calculateAvgRating(artist)
        albums = db.session.query(Album).filter(Album.user_id == artist.id).all()

        albums_data = [{"id": album.id, "name": album.name} for album in albums]

        data = {"songs": songs_data, "avg_rating": avg_rating, "albums": albums_data}

        return render_template("creator_dash.html", data=data)
    elif user.role == "admin":
        user_count = db.session.query(User).filter_by(role='user').count()
        creator_count = db.session.query(User).filter_by(role='creator').count()
        tracks_count = db.session.query(Song).count()
        albums_count = db.session.query(Album).count()

        genres_count = db.session.query(Song.genre, db.func.count(Song.id)).group_by(Song.genre).all()
        genres_count_chart = popular_genres_chart(genres_count)

        top_rated_songs = db.session.query(Song, db.func.avg(Rating.rating).label('avg_rating')) \
            .join(Rating).group_by(Song.id).order_by(db.desc('avg_rating')).limit(5).all()
        
        top_songs_likes = db.session.query(Song, db.func.coalesce(db.func.count(likes.c.song_id), 0).label('num_likes')) \
            .outerjoin(likes, Song.id == likes.c.song_id) \
            .filter(Song.id.in_([song[0].id for song in top_rated_songs])) \
            .group_by(Song.id).order_by(db.desc('num_likes')).all()
    
        likes_dict = {song[0].id: song[1] for song in top_songs_likes}
        rating_likes_chart = top_songs_chart(top_rated_songs, likes_dict)

        top_rated_artists = db.session.query(User, db.func.avg(Rating.rating).label('avg_rating')) \
            .join(Song, User.id == Song.artist_id) \
            .join(Rating, Song.id == Rating.song_id) \
            .group_by(User.id).order_by(db.desc('avg_rating')).limit(5).all()
        
        top_artists_songs = db.session.query(User, db.func.count(Song.id).label('num_songs')) \
            .outerjoin(Song, User.id == Song.artist_id) \
            .filter(User.id.in_([artist[0].id for artist in top_rated_artists])) \
            .group_by(User.id).order_by(db.desc('num_songs')).all()
        
        songs_dict = {artist[0].id: artist[1] for artist in top_artists_songs}
        artists_chart = top_artists_chart(top_rated_artists, songs_dict)

        data = {
            'user_count': user_count,
            'creator_count': creator_count,
            'tracks_count': tracks_count,
            'albums_count': albums_count,
            'genres': len(genres),
            'genres_count_chart': genres_count_chart,
            'rating_likes_chart': rating_likes_chart,
            'top_artists_chart': artists_chart
        }
        return render_template("admin_dash.html", data=data)
    else:
        return redirect('/logout')


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/logout")
@login_check
def logout():
    session.clear()
    return redirect("/")


@app.route("/signup")
def signup_page():
    return render_template("signup.html")


# ----- Song Starts ------
@app.route("/song/upload")
@login_check
def upload_song():
    user = session["user"]

    if user["role"] != "creator":
        flash("Only creators can upload song!")
        return redirect("/")

    return render_template("song_upload.html", song=False, genres=genres)


@app.route("/song/delete/<int:songid>")
@login_check
def delete_song(songid):
    user = session["user"]

    artist = db.session.query(User).filter(User.username == user["username"]).first()

    if user['role'] == "admin":
        song = db.session.query(Song).get(songid)
    else:
        song = (
            db.session.query(Song)
            .filter(Song.id == songid, Song.artist_id == artist.id)
            .first()
        )

    if not song:
        flash("Song Not Found!", "danger")
        return redirect("/")
    
    for playlist in song.playlists:
        playlist.songs.remove(song)
    
    if song.album:
        song.album.songs.remove(song)
    
    for user in song.liking_users:
        user.liked_songs.remove(song)
    
    for rating in song.ratings:
        db.session.delete(rating)

    db.session.delete(song)
    db.session.commit()

    return redirect("/")


@app.route("/song/edit/<int:songid>")
@login_check
def edit_song(songid):
    user = session["user"]

    artist = db.session.query(User).filter(User.username == user["username"]).first()
    song = (
        db.session.query(Song)
        .filter(Song.id == songid, Song.artist_id == artist.id)
        .first()
    )

    if not song:
        flash("Song Not Found!", "danger")
        return redirect("/")

    song_data = {
        "id": song.id,
        "name": song.name,
        "duration": song.duration,
        "genre": song.genre,
        "lyrics": song.lyrics,
    }

    return render_template("song_upload.html", song=song_data, genres=genres)


@app.route("/lyrics/<int:songid>")
@login_check
def lyrics(songid):
    username = session["user"]["username"]
    song = (
        db.session.query(Song, User.username.label("artist"))
        .join(User, Song.artist_id == User.id)
        .filter(Song.id == songid)
        .first()
    )
    user = db.session.query(User).filter(User.username == username).first()

    if not user:
        flash("User not found!", "danger")
        return redirect("/logout")

    if song:
        song_data = {
            "id": song.Song.id,
            "name": song.Song.name,
            "lyrics": song.Song.lyrics,
            "date_created": song.Song.date_created,
            "genre": song.Song.genre,
            "artist": song.artist,
        }

        has_liked = song.Song in user.liked_songs
        song_rating = (
            db.session.query(Rating)
            .filter_by(user_id=user.id, song_id=song.Song.id)
            .first()
        )
        ratings = db.session.query(Rating).filter_by(song_id=song.Song.id).all()

        if ratings:
            total_ratings = sum(rating.rating for rating in ratings)
            avg_rating = total_ratings / len(ratings)

            song_data["avg_rating"] = avg_rating
        else:
            song_data["avg_rating"] = "N/A"

        song_data["has_liked"] = has_liked

        if song_rating:
            song_data["rating"] = song_rating.rating
        else:
            song_data["rating"] = 0

        song_data["total_likes"] = calclulateTotalLikes(songid)

        return render_template("lyrics.html", song=song_data)
    else:
        flash("Song not found!", "danger")
        return redirect("/")


# ---------------- Playlist Starts --------------
@app.route("/playlist/<int:playlistid>")
@login_check
def playlist_info(playlistid):
    user = session["user"]

    user = db.session.query(User).filter_by(username=user["username"]).first()
    playlist = db.session.query(Playlist).get(playlistid)

    if user.id != playlist.user_id:
        flash("Forbidden", "danger")
        return redirect("/")

    playlist_songs = playlist.songs

    playlist_songs_list = [
        {"id": song.id, "name": song.name, "genre": song.genre}
        for song in playlist_songs
    ]

    _playlist = {"id": playlist.id, "name": playlist.name, "songs": playlist_songs_list}

    return render_template("playlist_info.html", playlist=_playlist)


@app.route("/playlist/create")
@login_check
def playlist_create():
    user = session["user"]

    if user["role"] != "user":
        flash("You can't create playlist", "danger")
        return redirect("/")

    songs = db.session.query(Song).all()

    songs_data = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in songs
    ]

    shuffle(songs_data)
    playlist = {"id": 0, "name": "", "playlist_songs": [], "songs": songs_data}

    return render_template("manage_playlist.html", playlist=playlist)


@app.route("/playlist/edit/<int:playlistid>")
@login_check
def playlist_edit(playlistid):
    user = session["user"]

    if user["role"] != "user":
        flash("You can't manage playlist", "danger")
        return redirect("/")

    playlist = db.session.query(Playlist).get(playlistid)
    playlist_songs = playlist.songs

    playlist_songs_list = [
        {"id": song.id, "name": song.name, "genre": song.genre}
        for song in playlist_songs
    ]

    songs = Song.query.filter(
        Song.id.notin_([song.id for song in playlist_songs])
    ).all()
    songs_data = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in songs
    ]

    shuffle(songs_data)

    _playlist = {
        "id": playlistid,
        "name": playlist.name,
        "playlist_songs": playlist_songs_list,
        "songs": songs,
    }

    return render_template("manage_playlist.html", playlist=_playlist)


@app.route("/playlist/delete/<int:playlistid>")
@login_check
def playlist_delete(playlistid):
    user = session["user"]

    if user["role"] != "user":
        flash("You can't perform this operation", "danger")
        return redirect("/")

    user = db.session.query(User).filter_by(username=user["username"]).first()
    if not user:
        flash("User not found")
        return redirect("/logout")

    playlist = (
        db.session.query(Playlist).filter_by(id=playlistid, user_id=user.id).first()
    )

    if not playlist:
        flash("Playlist not found!", "danger")
        return redirect("/")

    db.session.delete(playlist)
    db.session.commit()

    return redirect("/")


# ----------- Playlist Ends ----------------------

# ------------ Album Starts ----------------------
@app.route("/album/<int:albumid>")
@login_check
def album_info(albumid):
    user = session["user"]

    user = db.session.query(User).filter_by(username=user["username"]).first()
    album = db.session.query(Album).get(albumid)

    album_songs = album.songs
    album_songs_list = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in album_songs
    ]

    _album = {"id": album.id, "name": album.name, "songs": album_songs_list }

    return render_template("album_info.html", album=_album)


@app.route("/album/create")
@login_check
def album_create():
    user = session["user"]

    if user["role"] != "creator":
        flash("You can't create Albums, Please create a creator account!", "danger")
        return redirect("/")

    user = db.session.query(User).filter_by(username=user["username"]).first()
    if not user:
        flash("User not found", "danger")
        return redirect("/logout")

    # Current logged in artist's songs which are not in any other album
    songs = (
        db.session.query(Song)
        .filter(Song.artist_id == user.id, Song.album_id.is_(None))
        .all()
    )

    songs_data = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in songs
    ]

    shuffle(songs_data)
    album = {"id": 0, "name": "", "album_songs": [], "songs": songs_data}

    return render_template("manage_album.html", album=album)


@app.route("/album/edit/<int:albumid>")
@login_check
def album_edit(albumid):
    user = session["user"]

    if user["role"] != "creator":
        flash("You can't manage album", "danger")
        return redirect("/")

    user = db.session.query(User).filter_by(username=user["username"]).first()

    album = db.session.query(Album).get(albumid)
    album_songs = album.songs

    album_songs_list = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in album_songs
    ]

    songs = (
        db.session.query(Song)
        .filter(Song.artist_id == user.id, Song.album_id.is_(None))
        .all()
    )

    songs_data = [
        {"id": song.id, "name": song.name, "genre": song.genre} for song in songs
    ]

    _album = {
        "id": albumid,
        "name": album.name,
        "album_songs": album_songs_list,
        "songs": songs_data,
    }

    return render_template("manage_album.html", album=_album)


@app.route("/album/delete/<int:albumid>")
@login_check
def album_delete(albumid):
    user = session["user"]

    if user["role"] != "creator":
        flash("You can't manage album", "danger")
        return redirect("/")

    user = db.session.query(User).filter_by(username=user["username"]).first()
    if not user:
        flash("User not found!", "danger")
        return redirect("/")

    album = db.session.query(Album).filter_by(id=albumid, user_id=user.id).first()
    if not album:
        flash("Album not found!", "danger")
        return redirect("/")

    db.session.delete(album)
    db.session.commit()

    return redirect("/")
# ------------ Album Ends ------------------------

# ------------ Admin Starts ----------------------
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/admin/alltracks')
@login_check
@admin_check
def all_tracks():
    songs_by_genre = {}

    for genre in genres:
        songs_genre = db.session.query(Song).filter_by(genre=genre).all()
        songs_genre_data = [
            {"id": song.id, "name": song.name} for song in songs_genre
        ]
        songs_by_genre[genre] = songs_genre_data

    return render_template("all_tracks.html", genres=songs_by_genre)


@app.route('/admin/allusers')
@login_check
@admin_check
def all_users():
    users = db.session.query(User).filter_by(role='user').all()
    creators = db.session.query(User).filter_by(role='creator').all()

    data = {
        'users': users,
        'creators': creators
    }

    return render_template("all_users.html", users=data)


@app.route('/admin/deleteuser/<int:userid>')
@login_check
@admin_check
def delete_user(userid):
    user = db.session.query(User).get(userid)

    # Delete liked songs
    for song in user.liked_songs:
        song.liking_users.remove(user)
    
    # Remove ratings
    for rating in user.ratings:
        db.session.delete(rating)
    
    # Remove playlist created by user
    for playlist in user.playlists:
        for song in playlist.songs:
            playlist.songs.remove(song)
        db.session.delete(playlist)
    
    # Remove albums created by user
    for album in user.albums:
        for song in album.songs:
            album.songs.remove(song)
        db.session.delete(album)
    
    songs = db.session.query(Song).filter_by(artist_id=user.id).all()
    for song in songs:
        for liking_user in song.liking_users:
            liking_user.liked_songs.remove(song)
        
        for rating in song.ratings:
            db.session.delete(rating)
        
        db.session.delete(song)
    
    db.session.delete(user)
    db.session.commit()

    return redirect('/')


# ------------ Admin Ends ------------------------


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(UploadSong, "/song")
api.add_resource(EditSong, "/song/edit/<int:songid>")
api.add_resource(ManageSongLike, "/song/like/<int:songid>")
api.add_resource(ManageSongRating, "/song/rate/<int:songid>/<int:rating>")
api.add_resource(ManagePlaylist, "/playlist/create/<int:playlistid>")
api.add_resource(ManageAlbum, "/album/create/<int:albumid>")
api.add_resource(AdminLogin, '/admin/login')

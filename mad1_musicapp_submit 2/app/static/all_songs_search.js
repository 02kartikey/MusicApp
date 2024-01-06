document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const songs = document.querySelectorAll('.all-songs');

    searchInput.addEventListener('input', function () {
        const searchTerm = searchInput.value.trim().toLowerCase();

        songs.forEach(function (song) {
            const songText = song.textContent.toLowerCase().split("read lyrics")[0].trim();
            const shouldShow = songText.includes(searchTerm);
            if (shouldShow) {
                song.style.display = 'block'
                song.classList.add('d-flex');
            } else {
                song.style.display = 'none';
                song.classList.remove('d-flex');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('album_search');
    const albums = document.querySelectorAll('.all-albums');

    searchInput.addEventListener('input', function () {
        const searchTerm = searchInput.value.trim().toLowerCase();

        albums.forEach(function (album) {
            const albumText = album.textContent.toLowerCase().split("view album")[0].trim();;
            const shouldShow = albumText.includes(searchTerm);
            if (shouldShow) {
                album.style.display = 'block'
                album.classList.add('d-flex');
            } else {
                album.style.display = 'none';
                album.classList.remove('d-flex');
            }
        });
    });
});
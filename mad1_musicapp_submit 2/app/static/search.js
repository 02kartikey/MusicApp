document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search');
    const songs = document.querySelectorAll('.bg-song');

    searchInput.addEventListener('input', function () {
        const searchTerm = searchInput.value.trim().toLowerCase();

        songs.forEach(function (song) {
            const songText = song.textContent.toLowerCase().split('-')[0].trim();
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
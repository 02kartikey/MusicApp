document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-users');
    const users = document.querySelectorAll('.all-users');

    searchInput.addEventListener('input', function () {
        const searchTerm = searchInput.value.trim().toLowerCase();

        users.forEach(function (user) {
            const userText = user.textContent.toLowerCase().trim();
            const shouldShow = userText.includes(searchTerm);
            if (shouldShow) {
                user.style.display = 'block'
                user.classList.add('d-flex');
            } else {
                user.style.display = 'none';
                user.classList.remove('d-flex');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-track');
    const albums = document.querySelectorAll('.all-tracks');

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
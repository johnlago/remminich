/**
 * Swipe interface for Remminich.
 *
 * ALBUM_DATA is injected by the template as an array of album objects.
 * Each album: { id, albumName, thumbnailUrl, dates, locations, assetCount,
 *               neediness, total, no_captions, no_dates, no_locations }
 */

(function () {
    'use strict';

    const queue = Array.isArray(ALBUM_DATA) ? [...ALBUM_DATA] : [];
    let currentIndex = 0;
    let isBusy = false;

    // DOM refs
    const card = document.getElementById('swipeCard');
    const cardImage = document.getElementById('cardImage');
    const cardTitle = document.getElementById('cardTitle');
    const cardDates = document.getElementById('cardDates');
    const cardCaptions = document.getElementById('cardCaptions');
    const cardLocations = document.getElementById('cardLocations');
    const passBtn = document.getElementById('passBtn');
    const editBtn = document.getElementById('editBtn');

    if (!card) return;

    // --- Render ---

    function renderCard(album) {
        cardImage.src = album.thumbnailUrl;
        cardTitle.textContent = album.albumName;

        // Dates
        if (album.dates) {
            cardDates.innerHTML = album.dates;
        } else {
            cardDates.innerHTML = '<span class="missing">Unknown</span>';
        }

        // Captions count
        var captionsCount = (album.total || 0) - (album.no_captions || 0);
        cardCaptions.textContent = captionsCount;

        // Locations
        if (album.locations && album.locations !== 'No locations.') {
            cardLocations.innerHTML = album.locations;
        } else {
            cardLocations.innerHTML = '<span class="missing">Unknown</span>';
        }
    }

    function showDone() {
        var stack = document.getElementById('cardStack');
        var infoBox = document.getElementById('infoBox');
        stack.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;text-align:center;padding:40px;"><div>' +
            '<p style="font-size:18px;font-weight:600;color:var(--color-text);">All caught up!</p>' +
            '<p style="color:var(--color-text-secondary);">You\'ve seen all the albums.</p>' +
            '<a href="/api/reset-queue/" style="color:var(--color-blue);text-decoration:underline;">Start over</a>' +
            '</div></div>';
        if (infoBox) infoBox.style.display = 'none';
        passBtn.style.display = 'none';
        editBtn.style.display = 'none';
    }

    // --- Swipe actions ---

    function swipePass() {
        if (isBusy) return;
        isBusy = true;

        var album = queue[currentIndex];
        card.classList.add('swipe-left');

        fetch('/api/pass-album/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ album_id: album.id }),
        }).catch(function () {});

        setTimeout(function () {
            currentIndex++;
            if (currentIndex < queue.length) {
                card.classList.remove('swipe-left');
                card.classList.add('dragging');
                card.style.transform = '';
                card.style.opacity = '';
                renderCard(queue[currentIndex]);
                void card.offsetWidth;
                card.classList.remove('dragging');
            } else {
                fetchNextAlbum();
            }
            isBusy = false;
        }, 350);
    }

    function swipeEdit() {
        if (isBusy) return;
        isBusy = true;

        var album = queue[currentIndex];
        card.classList.add('swipe-right');

        setTimeout(function () {
            window.location.href = '/albums/' + album.id + '/';
        }, 300);
    }

    // --- Fetch more ---

    function fetchNextAlbum() {
        fetch('/api/next-album/')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.done || !data.album) {
                    showDone();
                } else {
                    queue.push(data.album);
                    card.classList.remove('swipe-left', 'swipe-right');
                    card.classList.add('dragging');
                    card.style.transform = '';
                    card.style.opacity = '';
                    renderCard(data.album);
                    void card.offsetWidth;
                    card.classList.remove('dragging');
                }
            })
            .catch(function () { showDone(); });
    }

    // --- Buttons ---

    passBtn.addEventListener('click', swipePass);
    editBtn.addEventListener('click', swipeEdit);

    // --- Touch / pointer drag ---

    var startX = 0;
    var currentX = 0;
    var isDragging = false;

    function onPointerDown(e) {
        if (isBusy) return;
        isDragging = true;
        startX = e.clientX || (e.touches && e.touches[0].clientX);
        card.classList.add('dragging');
    }

    function onPointerMove(e) {
        if (!isDragging) return;
        currentX = (e.clientX || (e.touches && e.touches[0].clientX)) - startX;
        var rotate = currentX * 0.05;
        card.style.transform = 'translateX(' + currentX + 'px) rotate(' + rotate + 'deg)';
    }

    function onPointerUp() {
        if (!isDragging) return;
        isDragging = false;
        card.classList.remove('dragging');

        if (currentX < -80) {
            swipePass();
        } else if (currentX > 80) {
            swipeEdit();
        } else {
            card.style.transform = '';
        }
        currentX = 0;
    }

    card.addEventListener('mousedown', onPointerDown);
    document.addEventListener('mousemove', onPointerMove);
    document.addEventListener('mouseup', onPointerUp);

    card.addEventListener('touchstart', function (e) {
        onPointerDown(e.touches[0]);
    }, { passive: true });

    document.addEventListener('touchmove', function (e) {
        if (isDragging) onPointerMove(e.touches[0]);
    }, { passive: true });

    document.addEventListener('touchend', onPointerUp);

    // --- Keyboard ---

    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') swipePass();
        if (e.key === 'ArrowRight') swipeEdit();
    });

    // --- CSRF ---

    function getCSRFToken() {
        var el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }
})();

document.querySelector('form').addEventListener('submit', function() {
        document.getElementById('loading-overlay').style.display = 'flex';
    });

window.addEventListener('load', function() {
        document.getElementById('loading-overlay').style.display = 'none';
    });


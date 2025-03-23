document.addEventListener("DOMContentLoaded", function () {
    const apiUrl = 'https://api.waifu.im/search';
    const params = {
        included_tags: ['waifu'],
        height: '>=200'
    };

    const queryParams = new URLSearchParams();

    for (const key in params) {
        if (Array.isArray(params[key])) {
            params[key].forEach(value => {
                queryParams.append(key, value);
            });
        } else {
            queryParams.set(key, params[key]);
        }
    }
    const requestUrl = `${apiUrl}?${queryParams.toString()}`;

    fetch(requestUrl)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Request failed with status code: ' + response.status);
            }
        })
        .then(data => {
            const imageUrl = data.images[0].url;
            document.getElementById('userImage').src = imageUrl;
        })
        .catch(error => {
            console.error('An error occurred:', error.message);
        });
});

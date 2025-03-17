function showLoader() {
    document.getElementById('booking-confirmation').style.display = 'none';

    document.getElementById('loading').style.display = 'block';

    setTimeout(function () {
        document.querySelector('.loader').style.display = 'none';
        document.querySelector('.message').style.display = 'block';

        setTimeout(function () {
            window.location.href = '/accounts/profile/';
        }, 2000);
    }, 12000);
}
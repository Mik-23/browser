document.getElementById('sendToBasketBtn').addEventListener('click', function() {
    const token = localStorage.getItem('access_token');
    console.log(token)
    const selectedMessages = Array.from(document.querySelectorAll('.message-checkbox:checked'))
        .map(checkbox => checkbox.getAttribute('data-message-id'));

    if (selectedMessages.length === 0) {
        alert('Пожалуйста, выберите хотя бы одно сообщение.');
        return;
    }

    fetch('/api/send_in_basket/', { // Укажите правильный URL вашего API
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token // Если используете CSRF-токены
        },
        body: JSON.stringify({ list_messages: selectedMessages })
    })
    .then(response => response.json())
    .then(data => {
        if (data.messages) {
            alert('Сообщения успешно отправлены в корзину.');
            // Здесь можно обновить интерфейс или перезагрузить страницу
        } else {
            alert('Произошла ошибка при отправке сообщений в корзину.');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке сообщений в корзину.');
    });
});

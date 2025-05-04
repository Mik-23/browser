document.getElementById('sendMessageButton').addEventListener('click', () => {
    const content = document.getElementById('messageContent').value;

    // Здесь вы можете сделать AJAX-запрос для отправки сообщения
    // Пример:
    fetch('/api/send_message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
        },
        body: JSON.stringify({
          content,
          recipient_id // Укажите ID получателя
          // chat_id если нужно
        })
    })
    .then(response => response.json())
    .then(data => {
      // Обновите интерфейс после успешной отправки сообщения
      document.getElementById('messageContent').value = ''; // Очистить поле ввода
      fetchMessages(); // Обновить список сообщений
    })
    .catch(error => console.error('Ошибка:', error));
});

// Вызов функции для получения сообщений при загрузке страницы
fetchMessages();
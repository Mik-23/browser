var modal = document.getElementById("myModal");
var btn = document.getElementById("openModalBtn");
var span = document.getElementsByClassName("close")[0];

// Открываем модальное окно при нажатии на кнопку
btn.onclick = function() {
    modal.style.display = "block";
}

// Закрываем модальное окно при нажатии на "x"
span.onclick = function() {
    modal.style.display = "none";
}

// Закрываем модальное окно при клике вне его
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Обработка отправки формы
document.getElementById('sendMessageForm').onsubmit = function(event) {
    event.preventDefault(); // Предотвращаем перезагрузку страницы

    // Получаем данные из формы
    var recipientId = document.getElementById('recipient_id').value;
    var content = document.getElementById('content').value;

   // Отправляем данные на сервер
   fetch('/api/send_message/', { // Убедитесь, что этот URL соответствует вашему API
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Если вы используете JWT токен
       },
       body: JSON.stringify({
           recipient_id: recipientId,
           content: content
       })
   })
   .then(response => response.json())
   .then(data => {
       console.log('Успех:', data);
       // Закрываем модальное окно после успешной отправки
       modal.style.display = "none";
       // Здесь можно добавить логику для обновления списка сообщений или уведомления пользователя
   })
   .catch((error) => {
       console.error('Ошибка:', error);
   });
}
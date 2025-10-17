document.getElementById('codeForm').addEventListener('submit', (event) => {
    event.preventDefault(); // Предотвращаем стандартное поведение формы
    const code = document.getElementById('reg_code').value; // Получаем значение кода подтверждения

    fetch('/api/send_code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
    })
    .then(response => {
        return response.json().then(data => ({ data, status: response.status })); // Возвращаем объект с данными и статусом
    })
    .then(({ data, status }) => {
        console.log(data);
        if (status === 200) { // Проверяем статус ответа
            console.log(data.message); // Выводим сообщение об успешной регистрации
            window.location.href = data.login_url; // Перенаправляем пользователя на страницу авторизации
        } else {
            console.error(data); // Обработка ошибок
        }
        if (data.message === 'Неверный код, пожалуйста, повторите попытку.') {
            alert(data.message)
        }
    })
    .catch(error => console.error('Ошибка:', error)); // Обработка сетевых ошибок
});
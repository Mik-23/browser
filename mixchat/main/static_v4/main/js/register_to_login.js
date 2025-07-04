document.getElementById('registerForm').addEventListener('submit', (event) => {
    event.preventDefault(); // Предотвращаем стандартное поведение формы
    const email = document.getElementById('reg_email').value; // Получаем значение email
    const username = document.getElementById('reg_login').value; // Получаем значение логина
    const password = document.getElementById('reg_password').value; // Получаем значение пароля

    fetch('/api/reg/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, username, password }),
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
    })
    .catch(error => console.error('Ошибка:', error)); // Обработка сетевых ошибок
});
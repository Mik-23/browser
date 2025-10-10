const loginUser = async (email, password) => {
    const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    console.log(data)
    if (response.ok) {
        // Сохраните токены в localStorage или cookies
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user_id', data.user_id);
        // Перенаправьте пользователя на страницу почты
        window.location.href = data.redirect_url;
    } else {
        // Обработка ошибок
        console.error(data.error);
    }
};

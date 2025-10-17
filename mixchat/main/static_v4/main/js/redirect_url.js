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
    console.log(data.redirect_url)
    if (response.ok) {
        // Сохраните токены в localStorage или cookies
        if (data.error != undefined) {
           const inputs = document.querySelectorAll('.form-group input');
           inputs.forEach(input => {
               input.style.border = '2px solid red'; // например, красная граница, толщиной 2px
           });
           error = document.getElementById('errorMessage');
           error.textContent = data.error
        } else {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user_id', data.user_id);
            // Перенаправьте пользователя на страницу почты
            window.location.href = data.redirect_url;
            if (data.error) {
               alert(data.error)
            }
        }
    } else {
        // Обработка ошибок
        console.error(data.error);
    }
};

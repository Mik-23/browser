const logoutUser = async () => {
    console.log("logoutUser called with:");
    const response = await fetch('/api/logout/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    });
    const data = await response.json();
    console.log(data)
    if (response.ok) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = data.logout_redirect;
    } else {
        // Обработка ошибок
        console.error(data.error);
    }
};
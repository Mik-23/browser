document.addEventListener('DOMContentLoaded', function() {
        const token = localStorage.getItem('access_token');
        const userId = localStorage.getItem('user_id'); // Получаем id пользователя

        if (!token) {
            console.error('Токен доступа не найден');
            return;
        }

        if (!userId) {
            console.error('user_id не найден в localStorage');
            return;
        }

        function loadBasketMessages() {
        const parsedUserId = Number(userId);
        const url = `/api/get_basket/`;

        fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Данные от сервера:', data);

            // Обработка данных...

            if (data.messages && Array.isArray(data.messages)) {
                const basketMessageList = document.querySelector('.basket-message-list');
                basketMessageList.innerHTML = '';

                data.messages.forEach(message => {
                    const listItem = document.createElement('li');
                    listItem.className = 'basket-item ingoing';
                    listItem.innerHTML = `
                        <h2>${message.subject}</h2>
                        <p><strong>От:</strong> ${message.sender_id}</p>
                        <p><strong>Кому:</strong> ${message.recipient_id}</p>
                        <p><strong>Дата:</strong> ${new Date(message.date).toLocaleString()}</p>
                        <p>${message.content}</p>
                    `;
                    basketMessageList.appendChild(listItem);
                });
            } else {
                console.error('Нет сообщений или данные имеют неверный формат');
            }
        })
        .catch(error => console.error('Ошибка при выполнении fetch:', error));
    };



     document.getElementById('basketBtn').onclick = function() {
        showSection('basket');
        loadBasketMessages(); // Загружаем отправленные сообщения
    };

    function showSection(sectionId) {
        // Скрываем все секции
        const sections = document.querySelectorAll('.message-list');
        sections.forEach(section => {
            section.classList.remove('active');
        });

        // Показываем выбранную секцию
        document.getElementById(sectionId).classList.add('active');
    }
 });
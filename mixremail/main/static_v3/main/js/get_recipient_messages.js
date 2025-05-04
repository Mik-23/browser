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

        // Логируем перед отправкой запроса
        function loadRecipientMessages() {
        const parsedUserId = Number(userId);
        const url = `/api/get_recipient_message/?recipient_id=${parsedUserId}`;

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
                const ingoingMessageList = document.querySelector('.ingoing-message-list');
                ingoingMessageList.innerHTML = '';
                data.messages.forEach(message => {
                    const listItem = document.createElement('li');
                    listItem.className = 'message-item ingoing';
                    listItem.innerHTML = `
                        <input type="checkbox" class="message-checkbox" data-message-id=${message.id}>
                        <h2>${message.subject}</h2>
                        <p><strong>От:</strong> ${message.sender_id}</p>
                        <p><strong>Дата:</strong> ${new Date(message.date).toLocaleString()}</p>
                        <p>${message.content}</p>
                    `;
                    ingoingMessageList.appendChild(listItem);
                });
            } else {
                console.error('Нет сообщений или данные имеют неверный формат');
            }
        })
        .catch(error => console.error('Ошибка при выполнении fetch:', error));
    };

    // JavaScript для переключения между разделами
    document.getElementById('inboxBtn').onclick = function() {
        showSection('inbox');
        loadRecipientMessages(); // Загружаем отправленные сообщения
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
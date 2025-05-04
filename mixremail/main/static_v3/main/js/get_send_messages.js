document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');

    if (!token) {
        console.error('Токен доступа не найден');
        return;
    }

    if (!userId) {
        console.error('user_id не найден в localStorage');
        return;
    }

    // Функция для загрузки отправленных сообщений
    function loadSentMessages() {
        const parsedUserId = Number(userId);
        const url = `/api/get_send_message/?sender_id=${parsedUserId}`;

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

            if (data.messages && Array.isArray(data.messages)) {
                const outgoingMessageList = document.querySelector('.outgoing-message-list');
                outgoingMessageList.innerHTML = '';

                data.messages.forEach(message => {
                    const listItem = document.createElement('li');
                    listItem.className = 'message-item outgoing';
                    listItem.innerHTML = `
                        <input type="checkbox" class="message-checkbox" data-message-id=${message.id}>
                        <h2>${message.subject}</h2>
                        <p><strong>Кому:</strong> ${message.recipient_id}</p>
                        <p><strong>Дата:</strong> ${new Date(message.date).toLocaleString()}</p>
                        <p>${message.content}</p>
                    `;
                    outgoingMessageList.appendChild(listItem);
                });
                console.log(outgoingMessageList)
            } else {
                console.error('Нет сообщений или данные имеют неверный формат');
            }
        })
        .catch(error => console.error('Ошибка при выполнении fetch:', error));
    }
    // Обработчик клика по кнопке "Отправленные"


    document.getElementById('sentBtn').onclick = function() {
        showSection('sent');
        loadSentMessages(); // Загружаем отправленные сообщения
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
let users = []; // Изначально пустой массив пользователей
let selectedUserId = null; // Переменная для хранения ID выбранного пользователя
let currentChatId = null;
const senderId = localStorage.getItem('user_id');

console.log(senderId)
// Функция для получения пользователей из API
function fetchUsers() {
    fetch('/api/search_user/', { // Замените на ваш реальный эндпоинт
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
        }
    })
    .then(response => response.json())
    .then(data => {
        users = data.users; // Сохраняем полученных пользователей в переменную
        displayUsers(); // Отображаем пользователей
    })
    .catch(error => console.error('Ошибка при получении пользователей:', error));
}

// Функция для отображения пользователей
function displayUsers() {
    const userList = document.getElementById('users');
    userList.innerHTML = ''; // Очистить список
    if (users.length > 0) { // Проверяем, есть ли пользователи
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user.username; // Имя пользователя
            li.onclick = () => selectUser(user.id); // Выбор пользователя
            userList.appendChild(li);
        });
        userList.style.display = 'block'; // Показываем список
    } else {
        userList.style.display = 'none'; // Скрываем список, если нет пользователей
    }
}

// Функция для выбора пользователя и отображения кнопки "Открыть чат"
function selectUser(userId) {
   selectedUserId = userId; // Сохраняем ID выбранного пользователя
   console.log(selectedUserId)
   document.getElementById('openChatButton').style.display = 'inline'; // Показываем кнопку
}

// Функция для поиска пользователей
function searchUsers() {
    const input = document.getElementById('userSearch').value.toLowerCase();
    console.log(input);
    const filteredUsers = users.filter(user => user.username.toLowerCase().includes(input));

    const userList = document.getElementById('users');
    userList.innerHTML = ''; // Очистить список

    if (filteredUsers.length > 0) { // Проверяем, есть ли отфильтрованные пользователи
        filteredUsers.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user.username; // Имя пользователя
            li.onclick = () => selectUser(user.id); // Выбор пользователя
            userList.appendChild(li);
        });
        userList.style.display = 'block'; // Показываем список
    } else {
        userList.style.display = 'none'; // Скрываем список, если нет результатов
    }
}

document.addEventListener('click', function(event) {
    const userList = document.getElementById('users');
    const searchInput = document.getElementById('userSearch');

    if (!userList.contains(event.target) && event.target !== searchInput) {
        userList.style.display = 'none';
    }
});

// Функция для открытия чата с пользователем
function openChat(userId) {
    const parseUserId = Number(userId);
    const parseSenderId = Number(senderId);

    // Сначала проверяем наличие чата
    const url = `/api/get_one_chat/?sender_id=${parseSenderId}&recipient_id=${parseUserId}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.chat_id) {
            // Если чат существует, открываем его
            currentChatId = data.chat_id;
            console.log(selectUser(userId))
            loadMessages(currentChatId);
        } else {
            // Если чат не существует, создаем новый
            createChat(parseSenderId, parseUserId);
        }
         document.getElementById('chatWindow').style.display = 'block';
    })
    .catch(error => console.error('Ошибка:', error));
}

function loadMessages(chatId) {
    const messageList = document.querySelector('.message-message-list');
    messageList.innerHTML = ''; // Очистить предыдущие сообщения

    const url = `/api/get_messages/?chat_id=${chatId}`; // Эндпоинт для получения сообщений по ID чата

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        data.messages.forEach(message => {
            const li = document.createElement('li');
            const messageContainer = document.createElement('div');
            console.log(message)
            // Добавляем текстовое сообщение, если есть
            if (message.content) {
                const textSpan = document.createElement('span');
                textSpan.textContent = `${message.sender_id}: ${message.content}`;
                messageContainer.appendChild(textSpan);
            }

            // Проверяем наличие изображения
            if (message.image) {
                const messageWrapper = document.createElement('div');
                messageWrapper.style.display = 'flex'; // горизонтальное расположение
                messageWrapper.style.alignItems = 'center'; // по вертикали по центру
                messageWrapper.style.marginBottom = '10px';

                const img = document.createElement('img');
                img.src = message.image;
                img.style.maxWidth = '200px'; // Ограничение ширины для удобства
                img.style.height = 'auto';
                img.style.display = 'block'; // Чтобы изображение было на отдельной строке
                img.alt = `${message.sender_id}`;

                const senderName = document.createElement('span');
                senderName.textContent = message.sender_id; // или другое поле с именем
                senderName.style.fontSize = '14px';
                senderName.style.fontWeight = 'bold';

                // Добавляем изображение и имя в контейнер
                messageWrapper.appendChild(senderName);
                messageWrapper.appendChild(img);

                messageContainer.appendChild(messageWrapper);
            }

            if (message.video) {
                const mediaWrapper = document.createElement('div');
                mediaWrapper.style.display = 'flex';
                mediaWrapper.style.alignItems = 'center';

                const video = document.createElement('video');
                video.src = message.video;
                video.controls = true;
                video.style.maxWidth = '300px';
                video.style.height = 'auto';
                video.style.marginRight = '10px';

                const senderName = document.createElement('span');
                senderName.textContent = message.sender_name; // или другое поле
                senderName.style.fontSize = '14px';

                mediaWrapper.appendChild(video);
                mediaWrapper.appendChild(senderName);

                messageContainer.appendChild(mediaWrapper);
            }

            // Для аудио
            if (message.audio) {
                const mediaWrapper = document.createElement('div');
                mediaWrapper.style.display = 'flex';
                mediaWrapper.style.alignItems = 'center';

                const audio = document.createElement('audio');
                audio.src = message.audio;
                audio.controls = true;
                audio.style.marginRight = '10px';

                const senderName = document.createElement('span');
                senderName.textContent = message.sender_name;

                mediaWrapper.appendChild(audio);
                mediaWrapper.appendChild(senderName);

                messageContainer.appendChild(mediaWrapper);
            }

            li.appendChild(messageContainer);
            messageList.appendChild(li);
            console.log(messageList)
        });
        messageList.scrollTop = messageList.scrollHeight;
    })
    .catch(error => console.error('Ошибка:', error));
}

function createChat(senderId, recipientId) {
   fetch('/api/create_chat/', { // Эндпоинт для создания нового чата
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({
           sender_id: senderId,
           recipient_id: recipientId
       })
   })
   .then(response => response.json())
   .then(data => {
       console.log(data.message); // Сообщение о создании чата
       currentChatId = data.chat.id;
       loadMessages(currentChatId); // Загружаем сообщения нового чата
   })
   .catch(error => console.error('Ошибка:', error));
}

// Обработчик события для отправки сообщения
document.getElementById('sendMessageButton').addEventListener('click', () => {
   const content = document.getElementById('messageContent').value;
   const image = document.getElementById('imageInput').value;
   const video = document.getElementById('videoInput').value;
   const audio = document.getElementById('audioInput').value;

   const formData = new FormData();
   formData.append('content', content);
   // Добавляем файлы, если они выбраны
   if (imageInput.files.length > 0) {
       for (let i = 0; i < imageInput.files.length; i++) {
           formData.append('image', imageInput.files[i]);
       }
   }
   if (videoInput.files.length > 0) {
       for (let i = 0; i < videoInput.files.length; i++) {
           formData.append('video', videoInput.files[i]);
       }
   }
   if (audioInput.files.length > 0) {
       for (let i = 0; i < audioInput.files.length; i++) {
           formData.append('audio', audioInput.files[i]);
       }
   }
   // Добавляем остальные параметры
   formData.append('recipient_id', selectedUserId);
   formData.append('chat_id', currentChatId);
   console.log(currentChatId)
   fetch('/api/send_message/', {
       method: 'POST',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
       },
       body: formData
   })
   .then(response => response.text)
   .then(data => {
       document.getElementById('messageContent').value = ''; // Очистить поле ввода
       document.getElementById('imageInput').value = '';
       document.getElementById('videoInput').value = '';
       document.getElementById('audioInput').value = '';
       console.log(data)
       loadMessages(currentChatId); // Обновить чат с выбранным пользователем после отправки сообщения
   })
   .catch(error => console.error('Ошибка:', error));
});

// Функция для получения списка чатов
function fetchChats() {
    fetch('/api/get_chats/', { // Замените на ваш реальный эндпоинт
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        displayChats(data.chats); // Отображаем полученные чаты
    })
    .catch(error => console.error('Ошибка при получении чатов:', error));
}

// Функция для отображения списка чатов
function displayChats(chats) {
    const chatList = document.getElementById('chats');
    console.log(chatList)
    chatList.innerHTML = ''; // Очистить список
    const numSenderId = Number(senderId)
    chats.forEach(chat => {
        const li = document.createElement('li');
        li.textContent = `Чат с ${chat.username}`; // Имя пользователя в чате
        console.log(typeof chat.user_id_1)
        console.log(typeof chat.user_id_2)
        console.log(typeof numSenderId)
        console.log(chat.user_id_1 === chat.user_id_2 && chat.user_id_1 === numSenderId)
        if (chat.user_id_1 < numSenderId && chat.user_id_2 === numSenderId) {
            li.onclick = () => openChat(chat.user_id_1); // Открытие чата при клике
        } else if (chat.user_id_1 === numSenderId && chat.user_id_2 > numSenderId) {
            li.onclick = () => openChat(chat.user_id_2);
        } else if (chat.user_id_1 === chat.user_id_2 && chat.user_id_1 === numSenderId) {
            li.onclick = () => openChat(chat.user_id_1);
        }
        chatList.appendChild(li);
    });
}
// Обработчик события для кнопки "Открыть чат"
document.getElementById('openChatButton').addEventListener('click', () => {
   if (selectedUserId) {
       openChat(selectedUserId); // Открываем чат с выбранным пользователем
   }
});

// Инициализация списка пользователей при загрузке страницы
fetchUsers();
fetchChats();
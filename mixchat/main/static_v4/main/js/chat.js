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
            li.textContent = `${message.sender_id}: ${message.content}`; // Отображение сообщения
            messageList.appendChild(li);
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

   fetch('/api/send_message/', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
       },
       body: JSON.stringify({
           content,
           recipient_id: selectedUserId, // Используем ID выбранного пользователя
           chat_id: currentChatId
       })
   })
   .then(response => response.json())
   .then(data => {
       document.getElementById('messageContent').value = ''; // Очистить поле ввода
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
    chatList.innerHTML = ''; // Очистить список

    chats.forEach(chat => {
        const li = document.createElement('li');
        li.textContent = `Чат с ${chat.username}`; // Имя пользователя в чате
        li.onclick = () => openChat(chat.user_id_2); // Открытие чата при клике
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
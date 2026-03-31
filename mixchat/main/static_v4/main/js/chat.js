let users = []; // Изначально пустой массив пользователей
let selectedUserId = null; // Переменная для хранения ID выбранного пользователя
let currentChatId = null;
let type = null;
const senderId = localStorage.getItem('user_id');
let profileId = null
let chatObj = []
let selectedUserIds = [];
let lastMessageCount = 0;
let pollingInterval = null


function getCurrentUser() {
    return fetch('/api/current_user/', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(res => res.json())
    .then(userData => {
        return userData;
    });
}

getCurrentUser().then(currentUser => {
    avatar.src = currentUser.photo;
    avatar.style.width = '50px';
    avatar.style.height = '50px';
})


document.querySelector('.user-name img').addEventListener('click', () => {
    const name = document.querySelector('.user-name p').textContent
    let current_chat = {}
    //console.log(chatObj)
    for (let chat of chatObj) {
        if (chat.username === name) {
            current_chat = chat
        }
    }
    if (current_chat.type === 'user') {
        for (let user of users) {
            if (user.username === name && user.type === 'user') {
                window.location.href = `/profile_other_user/${user.username}`;
            }
        }
    } else if (current_chat.type === 'group') {
        window.location.href = `/edit_group/${current_chat.id}`;
    }
})


// Функция для получения пользователей из API
function fetchUsers() {
    fetch('/api/search_user/', { // Замените на ваш реальный эндпоинт
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Продолжаем, если ответ успешный
        } else {
            // Обработка ошибок, например, выброс исключения или возврат отклоненного промиса
             window.location.href = '/auth_in_chat';
        }
    })
    .then(data => {
        users = data.users; // Сохраняем полученных пользователей в переменную
    })
    .catch(error => console.error('Ошибка при получении пользователей:', error));
}

// Функция для выбора пользователя
function selectUser(userId) {
   selectedUserId = userId; // Сохраняем ID выбранного пользователя
   openUserChat(selectedUserId)
}

// Функция для поиска пользователей
function searchUsers() {
    const input = document.getElementById('userSearch').value.toLowerCase();
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
        userList.style.marginLeft = 'auto';
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
function openUserChat(userId) {
    let selectedUser = {}
    let selected_chat = null
    const name = null
    const photo = null
    const bio = null

    for (user of users) {
       if(user.id === userId) {
           selectedUser = user
       }
    }
    for (obj of chatObj) {
       if(obj.username === selectedUser.username) {
         selected_chat = obj
       }
    }
    if (selected_chat) {
        openChat(selected_chat.id)
    } else {
        createChat([senderId, userId], name, bio, photo, selectedUser.type)
    }

}


function openChat(currentChatId) {
     if (pollingInterval) {
        clearInterval(pollingInterval);
     }
     loadMessages(currentChatId);
     pollingInterval = setInterval(() => {
        checkForNewMessages(currentChatId);
     }, 2000);
     document.getElementById('chatWindow').style.display = 'block';
}

function checkForNewMessages(chatId) {
    fetch(`/api/message/count/?chat_id=${chatId}`, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.count !== lastMessageCount) {
            lastMessageCount = data.count;
            loadMessages(chatId);  // есть новое сообщение!
        }
    });
}


function loadMessages(chatId) {
    const messageList = document.querySelector('.message-message-list');
    const messageContainer = document.querySelector('.message-list');
    const userName = document.querySelector('.user-name');
    let button = document.querySelector('button');
    let mediaButton = document.getElementById('mediaButton');
    messageList.innerHTML = ''; // Очистить предыдущие сообщения

    const url = `/api/message/?chat_id=${chatId}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        let lastDate = null;
        const targetElement = Array.from(document.querySelectorAll('#chats li')).find((li, index) => {
            const bgColor = window.getComputedStyle(li).backgroundColor;
            return bgColor === 'rgb(31, 148, 148)';
        });

        const img = document.querySelector('.user-name img');
        const p = document.querySelector('.user-name p');

        if (targetElement) {
            const current_img = targetElement.querySelector('img').src;
            const current_p = targetElement.querySelector('span').textContent;
            p.textContent = current_p;
            p.style.color = '#D9FFFD';
            img.src = current_img;
            img.style.width = '50px';
            img.style.height = '50px';
        }

        userName.appendChild(img);
        userName.appendChild(p);

        data.messages.forEach(message => {
            const li = document.createElement('li');
            const messageContainer = document.createElement('div');

            // Создаем контейнер для времени
            const timeContainer = document.createElement('div');
            timeContainer.style.fontSize = '12px';
            timeContainer.style.marginTop = '5px';
            timeContainer.style.opacity = '0.7';

            // Форматируем время
            let messageTime = '';
            if (message.date) {
                const date = new Date(message.date);
                messageTime = message.time;

                // Проверяем, нужно ли показать дату
                const currentDate = date.toLocaleDateString();
                if (lastDate !== currentDate) {
                    // Добавляем разделитель даты
                    const dateDivider = document.createElement('div');
                    dateDivider.textContent = currentDate;
                    dateDivider.style.textAlign = 'center';
                    dateDivider.style.color = '#888';
                    dateDivider.style.fontSize = '12px';
                    dateDivider.style.margin = '10px 0';
                    dateDivider.style.padding = '5px';
                    messageList.appendChild(dateDivider);
                    lastDate = currentDate;
                }
            }

            if (message.sender_user_id === senderId) {
                li.style.backgroundColor = '#1F9494';
                li.style.alignSelf = 'flex-end';
                li.style.marginLeft = 'auto';
                timeContainer.style.textAlign = 'right';
            } else {
                li.style.backgroundColor = '#3a3a3a';
                li.style.alignSelf = 'flex-start';
                li.style.marginRight = 'auto';
                timeContainer.style.textAlign = 'left';
            }

            // Добавляем текстовое сообщение, если есть
            if (message.content) {
                if (message.content.includes("https://")) {
                    const textSpan = document.createElement('span');
                    textSpan.textContent = message.sender_bot;
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    //let jsonString = message.content.replace(/"/g, '#');
                    //jsonString = jsonString.replace(/'/g, '"');

                    let contentArray = JSON.parse(message.content);
                    messageContainer.appendChild(textSpan);
                    console.log(contentArray);

                    for (let key in contentArray) {
                        const link = document.createElement('a');
                        link.style.display = 'block';
                        link.style.maxWidth = '300px';
                        link.style.wordWrap = 'break-word';
                        link.style.color = '#D9FFFD';
                        let url = contentArray[key];
                        if (url.startsWith('http://') || url.startsWith('https://')) {
                            link.href = url;
                            link.textContent = key;
                            messageContainer.appendChild(link);
                        } else {
                            const textSpan = document.createElement('span');
                            textSpan.textContent = `${key}: ${url}`;
                            messageContainer.appendChild(textSpan);
                        }
                    }
                } else {
                    const textSpan = document.createElement('span');
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    textSpan.textContent = `${message.sender_user}: ${message.content}`;
                    messageContainer.appendChild(textSpan);
                }
            }

            // Проверяем наличие изображения
            if (message.image) {
                const messageWrapper = document.createElement('div');
                const imageLink = document.createElement('a');
                imageLink.href = message.image;
                messageWrapper.style.display = 'flex';
                messageWrapper.style.alignItems = 'center';
                messageWrapper.style.marginBottom = '10px';
                messageWrapper.style.flexDirection = 'column';
                messageWrapper.style.gap = '5px';

                const img = document.createElement('img');
                img.src = message.image;
                img.style.maxWidth = '200px';
                img.style.height = 'auto';
                img.style.display = 'block';
                img.style.borderRadius = '10px';
                img.alt = `${message.sender}`;

                const senderName = document.createElement('span');
                senderName.textContent = message.sender;
                senderName.style.fontSize = '14px';
                senderName.style.fontWeight = 'bold';

                messageWrapper.appendChild(senderName);
                imageLink.appendChild(img);
                messageWrapper.appendChild(imageLink);
                messageContainer.appendChild(messageWrapper);
            }

            // Проверяем наличие видео
            if (message.video) {
                const mediaWrapper = document.createElement('div');
                mediaWrapper.style.display = 'flex';
                mediaWrapper.style.alignItems = 'center';
                mediaWrapper.style.flexDirection = 'column';
                mediaWrapper.style.gap = '5px';

                const video = document.createElement('video');
                video.src = message.video;
                video.controls = true;
                video.style.maxWidth = '300px';
                video.style.height = 'auto';
                video.style.borderRadius = '10px';

                const senderName = document.createElement('span');
                senderName.textContent = message.sender_name;
                senderName.style.fontSize = '14px';

                mediaWrapper.appendChild(video);
                mediaWrapper.appendChild(senderName);
                messageContainer.appendChild(mediaWrapper);
            }

            // Проверяем наличие аудио
            if (message.audio) {
                if (!document.getElementById('audio-styles')) {
                    const style = document.createElement('style');
                    style.id = 'audio-styles';
                    style.textContent = `
                        audio::-webkit-media-controls-panel {
                            background: #50ADA9 !important;
                        }
                        audio::-webkit-media-controls-play-button {
                            background-color: #E31C24 !important;
                            filter: brightness(1) invert(1) !important;
                            border-radius: 50% !important;
                            transform: scale(1.3) !important;
                        }
                        audio::-webkit-media-controls-current-time-display,
                        audio::-webkit-media-controls-time-remaining-display {
                            color: white !important;
                        }
                        audio::-webkit-media-controls-timeline {
                            background-color: #AD4D51 !important;
                            filter: brightness(1) invert(1) !important;
                            border-radius: 10px !important;
                        }

                         audio::-webkit-media-controls-mute-button,
                         audio::-webkit-media-controls-volume-slider {
                            background-color: transparent !important;
                            filter: brightness(0) invert(1) !important;
                        }
                        audio::-webkit-media-controls-toggle-closed-captions-button {
                            background-color: transparent !important;
                            filter: brightness(0) invert(1) !important;
                        }
                    `;
                    document.head.appendChild(style);
                }
                const mediaWrapper = document.createElement('div');
                mediaWrapper.style.display = 'flex';
                mediaWrapper.style.alignItems = 'center';
                mediaWrapper.style.flexDirection = 'column';
                mediaWrapper.style.gap = '5px';

                const audio = document.createElement('audio');
                audio.src = message.audio;
                audio.controls = true;
                audio.style.maxWidth = '300px';

                const senderName = document.createElement('span');
                senderName.textContent = message.sender_user;
                senderName.style.fontSize = '14px';

                mediaWrapper.appendChild(senderName);
                mediaWrapper.appendChild(audio);
                messageContainer.appendChild(mediaWrapper);
            }

            // Добавляем время в конец сообщения
            if (messageTime) {
                timeContainer.textContent = messageTime;
                messageContainer.appendChild(timeContainer);
            }

            li.appendChild(messageContainer);
            messageList.appendChild(li);
        });

        messageContainer.scrollTop = messageContainer.scrollHeight;
    })

}


if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/firebase-messaging-sw.js', {scope: '/'}).then(function(registration) {

      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function(err) {
      // registration failed :(
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}

function chatUserView(chatId) {
    fetch(`/api/chat/?chat_id=${chatId}`, {
       method: 'GET',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
         },
    })
    .then(response => response.json())
}

function createChat(groupUsers, name, bio, photo, chat_type) {
   const formData = new FormData();
   for (let i = 0; i <= groupUsers.length - 1; i++) {
      formData.append(`users[${i}]`, groupUsers[i]);;
   }

   formData.append('name', name);
   formData.append('bio', bio);
   if (photo_group_input.files.length > 0) {
      for (let i = 0; i < photo_group_input.files.length; i++) {
          console.log(photo_group_input.files[i])
          formData.append('photo', photo_group_input.files[i]);
      }
   }
   formData.append('type', chat_type);
   fetch('/api/chat/', { // Эндпоинт для создания нового чата
       method: 'POST',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: formData
   })
   .then(response => response.json())
   .then(data => {
       console.log(data); // Сообщение о создании чата
       currentChatId = data.id;
       loadMessages(currentChatId); // Загружаем сообщения нового чата
       fetchChats()
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
   console.log(content)
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
   formData.append('chat_id', currentChatId);
   formData.append('type', type);
   fetch('/api/message/', {
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
       loadMessages(currentChatId); // Обновить чат с выбранным пользователем после отправки сообщения
   })
   .catch(error => console.error('Ошибка:', error));
});

document.getElementById('mediaButton').addEventListener('click', () => {
    const mediaIcons = document.getElementById('media');
    mediaIcons.style.display = 'block';
});

const mediaIcons = document.getElementById('media')
mediaIcons.addEventListener('mouseleave', () => {
    mediaIcons.style.display = 'none'

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
        displayChats(data.chats); // Отображаем полученные чаты
    })
    .catch(error => console.error('Ошибка при получении чатов:', error));
}

// Функция для отображения списка чатов
function displayChats(chats) {
    const chatList = document.getElementById('chats');
    chatList.innerHTML = ''; // Очистить список
    const numSenderId = senderId
    chatObj = chats
    chats.forEach(chat => {
        const li = document.createElement('li');

        const span = document.createElement('span');
        span.textContent = chat.username; // Имя пользователя в чате
        const p = document.createElement('p');
        const img = document.createElement('img');
        img.src = chat.photo;
        img.style.width = '50px'
        img.style.height = '50px'
        if (chat.content.length > 13) {
            p.textContent = chat.sender_name + chat.content.substring(0, 14) + '...';
        } else {
            p.textContent = chat.sender_name + chat.content;
        }
        li.onclick = () => {
            const listChat = document.getElementById('chats')
            const allLists = listChat.querySelectorAll('li')
            const mediaIcons = document.getElementById('media')
            for (const lis of allLists) {
                lis.style.backgroundColor = '#3a3a3a';
                mediaIcons.style.display = 'none'
            }
            currentChatId = chat.id
            type = chat.type
            openChat(chat.id);
            chatUserView(chat.id)
            li.style.backgroundColor = '#1F9494';

        }
        li.appendChild(span);
        li.appendChild(p);
        li.appendChild(img)
        chatList.appendChild(li);
        chatList.style.display = 'block';
    });
}

// Инициализация списка пользователей при загрузке страницы
fetchUsers();
fetchChats();

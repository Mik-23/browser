let users = []; // Изначально пустой массив пользователей
let selectedUserId = null; // Переменная для хранения ID выбранного пользователя
let currentChatId = null;
let type = null;
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
        //displayUsers(); // Отображаем пользователей

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
            console.log(user.id)
            console.log(user)
            //li.textContent = user.username; // Имя пользователя
            li.onclick = () => selectUser(user.id); // Выбор пользователя
            userList.appendChild(li);
        });
        userList.style.display = 'block'; // Показываем список
    } else {
        userList.style.display = 'none'; // Скрываем список, если нет пользователей
    }
}

// Функция для выбора пользователя
function selectUser(userId) {
   selectedUserId = userId; // Сохраняем ID выбранного пользователя
   console.log(selectedUserId)
   if (selectedUserId) {
       openChat(selectedUserId);
   }
}

// Функция для поиска пользователей
function searchUsers() {
    const input = document.getElementById('userSearch').value.toLowerCase();
    console.log(input);
    const filteredUsers = users.filter(user => user.username.toLowerCase().includes(input));
    console.log(filteredUsers)
    const userList = document.getElementById('users');
    userList.innerHTML = ''; // Очистить список

    if (filteredUsers.length > 0) { // Проверяем, есть ли отфильтрованные пользователи
        filteredUsers.forEach(user => {
            const li = document.createElement('li');
            console.log(user.id)
            li.textContent = user.username; // Имя пользователя
            li.onclick = () => selectUser(user.id); // Выбор пользователя

            userList.appendChild(li);
        });
        console.log(userList)
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
function openChat(userId) {
    const parseUserId = userId;
    const parseSenderId = senderId;
    let selectedUser = {}
    for (user of users) {
       if(user.id === parseUserId) {
           selectedUser = user
       }
   }
    // Сначала проверяем наличие чата
    const url = `/api/chat/?sender_id=${parseSenderId}&recipient_id=${parseUserId}`;

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
            console.log(data)
            loadMessages(currentChatId);
        } else {
            // Если чат не существует, создаем новый
            console.log(parseSenderId)
            console.log(parseUserId)
            createChat(parseSenderId, parseUserId, selectedUser.type);
        }
        document.getElementById('chatWindow').style.display = 'block';


    })
    .catch(error => console.error('Ошибка:', error));
}

document.getElementById('profile').addEventListener('click', () => {
    const profileForm = document.getElementById('profileForm');
    profileForm.style.display = 'block';
});

const url = `/api/profile_form/`;
fetch(url, {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
    }
})
.then(response => response.json())
.then(data => {
    console.log(data)
    const formPhoto = document.querySelector('.form-profile')
    let photo = document.getElementById('photoProfile');
    let photoFile = document.getElementById('photo_input');
    let date_birth = document.getElementById('date_birth_input');
    console.log(photoFile.files)
    date_birth.value = data.date_birth;
    console.log(date_birth)
    photo.src = data.photo;
    console.log(photo)
    photo.style.width = '150px';
    photo.style.height = '150px';
    formPhoto.appendChild(photo)
    const avatar = document.getElementById('avatar');
    console.log(photo)
    avatar.src = photo.src;
    avatar.style.width = '50px';
    avatar.style.height = '50px';
   });

function saveProfile(photo, date_birth) {
   const formData = new FormData();
   console.log(photo_input.files.length)
   if (photo_input.files.length > 0) {
      for (let i = 0; i < photo_input.files.length; i++) {
          console.log(photo_input.files[i])
          formData.append('photo', photo_input.files[i]);
      }
   }
   formData.append('date_birth', date_birth);
   const url = `/api/profile_form/`;
   console.log(formData)
   fetch(url, {
       method: 'PUT',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: formData
   })
   .then(response => response.text)
}


function loadMessages(chatId) {
    const messageList = document.querySelector('.message-message-list');
    const messageContainer = document.querySelector('.message-list');
    const userName = document.querySelector('.user-name') ;
    console.log(chatId)
    let button = document.querySelector('button');
    let mediaButton = document.getElementById('mediaButton');
    messageList.innerHTML = ''; // Очистить предыдущие сообщения

    const url = `/api/message/?chat_id=${chatId}`; // Эндпоинт для получения сообщений по ID чата

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
        const current_img = targetElement.querySelector('img').src
        const current_p = targetElement.querySelector('span').textContent
        const img = document.querySelector('.user-name img')
        const p = document.querySelector('.user-name p')
        p.textContent = current_p
        p.style.color = '#D9FFFD'
        img.src = current_img
        img.style.width = '50px'
        img.style.height = '50px'
        userName.appendChild(img)
        userName.appendChild(p)
        data.messages.forEach(message => {
            const li = document.createElement('li');
            const messageContainer = document.createElement('div');

            if (message.sender_id === senderId) {
                li.style.backgroundColor = '#1F9494'
                li.style.alignSelf = 'flex-end';
                li.style.marginLeft = 'auto';
            } else {
                li.style.alignSelf = 'flex-start';
                li.style.marginLeft = 'auto';
            }
            // Добавляем текстовое сообщение, если есть
            if (message.content) {
                if (message.content.includes("https://")) {
                    const textSpan = document.createElement('span');
                    textSpan.textContent = message.sender;
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    console.log(message.content)
                    const jsonString = message.content.replace(/'/g, '"');
                    contentArray = JSON.parse(jsonString);
                    messageContainer.appendChild(textSpan);
                    console.log(contentArray)
                    for (key in contentArray) {
                        const link = document.createElement('a');
                        console.log(key)
                        link.style.display = 'block';
                        link.style.maxWidth = '300px';
                        link.style.wordWrap = 'break-word';
                        link.href = contentArray[key];
                        link.textContent = key;
                        messageContainer.appendChild(link);
                    }
                } else {
                    const textSpan = document.createElement('span');
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    textSpan.textContent = `${message.sender}: ${message.content}`;
                    messageContainer.appendChild(textSpan);
                }
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
                img.alt = `${message.sender}`;

                const senderName = document.createElement('span');
                senderName.textContent = message.sender; // или другое поле с именем
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
        messageContainer.scrollTop = messageContainer.scrollHeight;
    })
    .catch(error => console.error('Ошибка:', error));
}

function createChat(senderId, recipientId, type) {
   fetch('/api/chat/', { // Эндпоинт для создания нового чата
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({
           sender_id: senderId,
           recipient_id: recipientId,
           type: type
       })
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
   formData.append('recipient_id', selectedUserId);
   console.log(selectedUserId)
   formData.append('chat_id', currentChatId);
   formData.append('type', type);
   console.log(currentChatId)
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
       console.log(data)
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
    const numSenderId = senderId
    console.log(chats)
    chats.forEach(chat => {
        const li = document.createElement('li');

        const span = document.createElement('span');
        span.textContent = chat.username; // Имя пользователя в чате
        const p = document.createElement('p');
        const img = document.createElement('img');
        img.src = chat.photo;
        img.style.width = '50px'
        img.style.height = '50px'
        console.log(chat)
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
            if (chat.user_id_1 < numSenderId && chat.user_id_2 === numSenderId) {
                openChat(chat.user_id_1); // Открытие чата при клике
                li.style.backgroundColor = '#1F9494';
                selectedUserId = chat.user_id_1
            } else if (chat.user_id_1 === numSenderId && chat.user_id_2 > numSenderId) {
                openChat(chat.user_id_2);
                li.style.backgroundColor = '#1F9494';
                selectedUserId = chat.user_id_2
            } else if (chat.user_id_1 === chat.user_id_2 && chat.user_id_1 === numSenderId) {
                openChat(chat.user_id_1);
                li.style.backgroundColor = '#1F9494';
                selectedUserId = chat.user_id_1
            }
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

let users = []; // Изначально пустой массив пользователей
let selectedUserId = null; // Переменная для хранения ID выбранного пользователя
let currentChatId = null;
let type = null;
const senderId = localStorage.getItem('user_id');
let profileId = senderId
let chatObj = []
let selectedUserIds = [];

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
    })
    .catch(error => console.error('Ошибка при получении пользователей:', error));
}


// Функция для отображения пользователей
function displayUsers() {
    const userList = document.getElementById('groupUsers');
    userList.innerHTML = ''; // Очистить список
    console.log(users)
    if (users.length > 0) { // Проверяем, есть ли пользователи
        users.forEach(user => {
            const li = document.createElement('li');
            console.log(user.id)
            console.log(user)
            const input = document.createElement('input')
            input.type = 'checkbox'
            input.value = user.id
            const img = document.createElement('img')
            const span = document.createElement('span')
            img.src = user.photo
            img.style.width = '20px'
            img.style.height = '20px'
            span.textContent = user.username; // Имя пользователя
            li.appendChild(input)
            li.appendChild(img)
            li.appendChild(span)
            li.onclick = function(e) {
                 if (e.target.tagName !== 'INPUT') {
                     const checkbox = this.querySelector('input');
                     checkbox.checked = !checkbox.checked;
                 }

                 const checkbox = this.querySelector('input');
                 if (checkbox.checked) {
                     this.classList.add('selected');
                     selectedUserIds.push(user.id);
                 } else {
                     this.classList.remove('selected');
                     selectedUserIds = selectedUserIds.filter(id => id !== user.id);
                 }
             };
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
   openUserChat(selectedUserId)
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
     loadMessages(currentChatId);
     document.getElementById('chatWindow').style.display = 'block';
}

document.querySelector('.user-name img').addEventListener('click', () => {
    console.log(chatObj)
    const name = document.querySelector('.user-name p').textContent
    let current_chat = {}
    for (chat of chatObj) {
        if (chat.username === name) {
            current_chat = chat
        }
    }
    for (user of users) {
        console.log(user)
        if (user.username === name && user.type === 'user') {
            profileId = user.id
        }
    }
    if (current_chat.type === 'user') {
        getProfile()
        const profileForm = document.getElementById('profileForm');
        profileForm.style.display = 'block';
        document.querySelector('.save-btn').style.display = 'none'
        document.getElementById('photo_input').style.display = 'none'
        document.getElementById('name_input').disabled = 1
        document.getElementById('date_birth_input').disabled = 1
        document.getElementById('bio_input').disabled = 1
    } else if (current_chat.type === 'group') {
        const profileGroup = document.getElementById('profileGroup');
        profileGroup.style.display = 'block';
        chatUserView(current_chat.id)
        document.querySelector('.save-group').style.display = 'none'
        document.querySelector('.edit-group').style.display = 'none'
        document.querySelector('.profile-group-form img').src = current_chat.photo;
        document.getElementById('name_group_input').value = current_chat.username
        document.getElementById('bio_group_input').value = current_chat.bio
        document.getElementById('photo_group_input').style.display = 'none'
        document.getElementById('name_group_input').disabled = 1
        document.getElementById('bio_group_input').disabled = 1
    }
});

document.getElementById('profile').addEventListener('click', () => {
    const profileForm = document.getElementById('profileForm');
    profileId = senderId
    getProfile()
    profileForm.style.display = 'block';
});

document.getElementById('group-create').addEventListener('click', () => {
    const profileGroup = document.getElementById('profileGroup');
    profileGroup.style.display = 'block';
    displayUsers()
});

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

function getProfile() {
    console.log('profileId:', profileId);
    console.log('users array length:', users.length);
    console.log('users array:', users); // Посмотрите, что в массиве
    const url = `/api/profile_form/?user_id=${profileId}`;
    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        getCurrentUser().then(currentUser => {
            const formPhoto = document.querySelector('.form-profile')
            let photo = document.getElementById('photoProfile');
            let photoFile = document.getElementById('photo_input');
            let name_of_user = document.getElementById('name_input');
            let date_birth = document.getElementById('date_birth_input');
            let bio = document.getElementById('bio_input');
            name_of_user.value = data.name;
            date_birth.value = data.date_birth;
            bio.value = data.bio;
            photo.src = data.photo;
            photo.style.width = '150px';
            photo.style.height = '150px';
            formPhoto.appendChild(photo)
            const avatar = document.getElementById('avatar');
            avatar.src = currentUser.photo;
            avatar.style.width = '50px';
            avatar.style.height = '50px';
            });
       });
    }

function saveProfile(photo, name, date_birth, bio) {
   const formData = new FormData();
   if (photo_input.files.length > 0) {
      for (let i = 0; i < photo_input.files.length; i++) {
          console.log(photo_input.files[i])
          formData.append('photo', photo_input.files[i]);
      }
   }
   formData.append('name', name);
   formData.append('date_birth', date_birth);
   formData.append('bio', bio);
   const url = `/api/profile_form/`;
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
        console.log(data)
        const img = document.querySelector('.user-name img')
        const p = document.querySelector('.user-name p')
        if (targetElement) {
            const current_img = targetElement.querySelector('img').src
            const current_p = targetElement.querySelector('span').textContent
            p.textContent = current_p
            p.style.color = '#D9FFFD'
            img.src = current_img
            img.style.width = '50px'
            img.style.height = '50px'
        } else {
        }
        userName.appendChild(img)
        userName.appendChild(p)
        data.messages.forEach(message => {
            const li = document.createElement('li');
            const messageContainer = document.createElement('div');

            if (message.sender_user_id === senderId) {
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
                    console.log(message.sender_bot)
                    textSpan.textContent = message.sender_bot;
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    console.log(message.content)
                    let jsonString = message.content.replace(/"/g, '#');
                    jsonString = jsonString.replace(/'/g, '"');
                    console.log(jsonString)
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
                    textSpan.textContent = `${message.sender_user}: ${message.content}`;
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
    console.log(chatId)
    fetch(`/api/chat/?chat_id=${chatId}`, {
       method: 'GET',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
         },
    })
    .then(response => response.json())
    .then(data => {
        const userList = document.getElementById('groupUsers');
        userList.innerHTML = ''; // Очистить список
        const usersGroup = data.users

        // Добавляем стили для списка
        userList.style.listStyle = 'none';
        userList.style.padding = '0';
        userList.style.margin = '0';

        usersGroup.forEach(user => {
            const li = document.createElement('li');

            // Стили для каждого элемента
            li.style.display = 'flex';
            li.style.alignItems = 'center';
            li.style.padding = '12px 16px';
            li.style.marginBottom = '8px';  // ← Отступ между элементами
            li.style.borderRadius = '8px';
            li.style.borderBottom = '1px solid #e0e0e0';  // ← Разделительная линия

            const img = document.createElement('img')
            img.src = user[1]
            img.style.width = '40px';  // Увеличил размер
            img.style.height = '40px';
            img.style.borderRadius = '50%';  // Круглая аватарка
            img.style.marginRight = '12px';
            img.style.objectFit = 'cover';

            const span = document.createElement('span')
            span.textContent = user[0]; // Имя пользователя
            span.style.flex = '1';  // Занимает все доступное место
            span.style.fontSize = '16px';
            span.style.fontWeight = '500';

            const role = document.createElement('span')
            role.textContent = user[2];
            role.style.padding = '4px 12px';
            role.style.backgroundColor = '#1F9494';
            role.style.color = 'white';
            role.style.borderRadius = '20px';
            role.style.fontSize = '12px';
            role.style.fontWeight = '600';

            li.appendChild(img)
            li.appendChild(span)
            li.appendChild(role)
            userList.appendChild(li);
            getCurrentUser().then(currentUser => {
                if (currentUser.name === user[0] && user[2] === 'Создатель') {
                    document.querySelector('.edit-group').style.display = 'block'
                    document.getElementById('photo_group_input').style.display = 'block'
                    document.getElementById('name_group_input').disabled = 0
                    document.getElementById('bio_group_input').disabled = 0
                }
            })
        });
    })
}

function editChat(chat_id, name, bio, photo, type) {
   const formData = new FormData();
   formData.append('chat_id', chat_id);
   formData.append('name', name);
   formData.append('bio', bio);
   if (photo_group_input.files.length > 0) {
      for (let i = 0; i < photo_group_input.files.length; i++) {
          console.log(photo_group_input.files[i])
          formData.append('photo', photo_group_input.files[i]);
      }
   }
   formData.append('type', type);
   fetch('/api/chat/', { // Эндпоинт для создания нового чата
       method: 'PUT',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: formData
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
   console.log(type)
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
            currentChatId = chat.id
            type = chat.type
            console.log(chat.type)
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
getProfile();

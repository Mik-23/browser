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
let msgId = null
let msgContent = null
let msgChatId = null
let activeEditButton = null;
let isEditMode = false;
let oldChatID = null;
let isInActionMode = false;


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
    const menu_photo = document.getElementById('menu-photo');
    menu_photo.src = avatar.src;
    menu_photo.style.width = '50px';
    menu_photo.style.height = '50px';
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
    if (isInActionMode) return;
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
    editButton = document.querySelector('.temp-edit-btn')
    if (editButton) {
       editButton.style.display = 'none'
    }
    answerButton = document.querySelector('.temp-answer-btn')
    if (answerButton) {
       answerButton.style.display = 'none'
    }
    transmissionButton = document.querySelector('.temp-transmission-btn')
    if (transmissionButton) {
       transmissionButton.style.display = 'none'
    }
    document.querySelector('.sent').style.display = 'block'
    document.getElementById('messageContent').value = '';
    document.querySelector('.message-dropdown').style.display = 'none'
    document.querySelector('.delete-form').style.display = 'none'
    document.querySelector('.sent').style.display = 'block'
    const messageList = document.querySelector('.message-message-list');
    const messageContainer = document.querySelector('.message-list');
    const userName = document.querySelector('.user-name');
    let button = document.querySelector('button');
    let mediaButton = document.getElementById('mediaButton');
    messageList.innerHTML = ''; // Очистить предыдущие сообщения
    let chat_type = ''
    for (chat of chatObj) {
        if (chat.id === Number(chatId)) {
             chat_type = chat.type
        }
    }
    let message_url = ''
    if (chat_type === 'user' || chat_type === 'group') {
         message_url = '/api/message/'
    } else if (chat_type === 'bot') {
         message_url = '/api/message_bot/'
    }

    const url = `${message_url}?chat_id=${chatId}`; // Эндпоинт для просметра сообщений

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
        if (p.textContent === 'SmartMix') {
            document.getElementById('openMqtt').style.display = 'block'
            fetch('/api/check_mqtt/', {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === 'Вы не подключены к MQTT. Введите данные.') {
                        document.querySelector('.mqtt-text-panel').style.display = 'block'
                        document.querySelector('.input-panel').style.display = 'none'
                    } else {
                        document.querySelector('.mqtt-text-panel').style.display = 'none'
                        document.querySelector('.input-panel').style.display = 'flex'
                    }
                })
        } else {
            document.querySelector('.open-mqtt').style.display = 'none'
            document.querySelector('.mqtt-text-panel').style.display = 'none'
            document.querySelector('.input-panel').style.display = 'flex'
        }
        if (targetElement) {
            const current_img = targetElement.querySelector('img').src;
            const current_p = targetElement.querySelector('span').textContent;
            p.textContent = current_p;
            p.style.color = '#D9FFFD';
            img.src = current_img;
            img.style.width = '50px';
            img.style.height = '50px';
            img.style.borderRadius = "30px"
        }

        userName.appendChild(img);
        userName.appendChild(p);

        data.messages.forEach(message => {
            const li = document.createElement('li');
            const messageContainer = document.createElement('div');
            const menuBtn = document.createElement('button');
            menuBtn.innerHTML = '⋮';
            menuBtn.style.background = 'transparent'
            menuBtn.style.cssText = `
                background: transparent;
                cursor: pointer;
                width: 8px;
                height: 8px;
                align-items: center;
                justify-content: center;
                right: 25px;
                top: -25px;
            `;
            menuBtn.classList.add('message-menu-btn');
            menuBtn.setAttribute('data-message-id', message.id);
            menuBtn.setAttribute('data-chat-id', message.chat_id);
            menuBtn.setAttribute('data-message-content', message.content);
            const dropdown = document.querySelector('.message-dropdown')
            const editItem = document.querySelector('.edit-item');
            const deleteItem = document.querySelector('.delete-item');
            const answerItem = document.querySelector('.answer-item');
            const transmissionItem = document.querySelector('.transmission-item');
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
                    const title = document.createElement('span');
                    title.style.fontSize = '12px';
                    title.style.color = '#99BEFF';
                    title.style.fontWeight = 'bold';
                    title.textContent = message.sender_bot;

                    textSpan.textContent = message.sender_bot;
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    let contentArray = JSON.parse(message.content);
                    messageContainer.appendChild(textSpan);
                    li.appendChild(title)
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
                } else if (message.sender_bot === 'Mixrobot'){
                    const textSpan = document.createElement('span');
                    const title = document.createElement('span');
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    title.style.fontSize = '12px';
                    title.style.color = '#99BEFF';
                    title.style.fontWeight = 'bold';
                    title.textContent = message.sender_bot;
                    textSpan.style.whiteSpace = 'pre-line'
                    textSpan.textContent = message.content;
                    console.log(textSpan);
                    li.appendChild(title);
                    messageContainer.appendChild(textSpan);
                } else if (message.sender_bot === 'SmartMix'){
                    const textSpan = document.createElement('span');
                    const title = document.createElement('span');
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    title.style.fontSize = '12px';
                    title.style.color = '#99BEFF';
                    title.style.fontWeight = 'bold';
                    title.textContent = message.sender_bot;
                    textSpan.style.whiteSpace = 'pre-line'
                    textSpan.textContent = message.content;
                    li.appendChild(title);
                    messageContainer.appendChild(textSpan);
                } else {
                    const textSpan = document.createElement('span');
                    const title = document.createElement('span');
                    textSpan.style.maxWidth = '300px';
                    textSpan.style.wordWrap = 'break-word';
                    title.style.fontSize = '12px';
                    title.style.color = '#99BEFF';
                    title.style.fontWeight = 'bold';
                    title.textContent = message.sender_user;

                    textSpan.textContent = message.content;
                    li.appendChild(title);
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

            let answer_message = {}
            const answer_to = message.answer_to
            if (answer_to) {
                const replyWrapper = document.createElement('div');
                replyWrapper.style.display = 'flex';
                replyWrapper.style.alignItems = 'stretch';
                replyWrapper.style.background = '#197575';
                replyWrapper.style.gap = '8px';
                replyWrapper.style.marginBottom = '6px';
                replyWrapper.style.paddingLeft = '4px';

                // Вертикальная линия
                const line = document.createElement('div');
                line.style.width = '2px';
                line.style.background = '#4a90e2';
                line.style.borderRadius = '2px';
                line.style.margin = '2px 0';

                const replyInfo = document.createElement('div');
                replyInfo.style.flex = '1';
                let found = false;
                for (let mess of data.messages) {
                    if (mess.id === answer_to) {
                        answer_message = mess;
                        const name = document.createElement('div');
                        name.style.fontSize = '11px';
                        name.style.color = '#90C5FF';
                        name.style.marginBottom = '2px';
                        name.textContent = `Ответ для ${answer_message.sender_user}`;

                        const preview = document.createElement('div');
                        preview.style.fontSize = '11px';
                        preview.style.color = '#D1D1D1';
                        preview.style.overflow = 'hidden';
                        preview.textContent = answer_message.content;
                        replyInfo.appendChild(name);
                        replyInfo.appendChild(preview);
                        found = true;
                        break
                    } else if (mess.is_forwarded) {
                        answer_message = message;
                        const name = document.createElement('div');
                        name.style.fontSize = '11px';
                        name.style.color = '#90C5FF';
                        name.style.marginBottom = '2px';
                        name.textContent = `Переслано от ${answer_message.transmission_by}`;

                        const preview = document.createElement('div');
                        preview.style.fontSize = '11px';
                        preview.style.color = '#D1D1D1';
                        preview.style.overflow = 'hidden';
                        preview.textContent = answer_message.transmission_content;

                        replyInfo.appendChild(name);
                        replyInfo.appendChild(preview);
                        found = true;
                        break
                    }
                }
                if (found) {
                   replyWrapper.appendChild(line);
                   replyWrapper.appendChild(replyInfo);

                   messageContainer.appendChild(replyWrapper);
                }
            }


            // Добавляем время в конец сообщения
            if (messageTime) {
                timeContainer.textContent = messageTime;
                messageContainer.appendChild(timeContainer);
            }

            if (message.is_edit) {
                const editedSpan = document.createElement('div');
                editedSpan.textContent = '(ред.)';
                editedSpan.style.fontSize = '15px'
                editedSpan.classList.add('message-edited');
                messageContainer.appendChild(editedSpan);
            }

            menuBtn.onclick = (e) => {
                e.stopPropagation();
                msgId = e.currentTarget.getAttribute('data-message-id');
                msgContent = e.currentTarget.getAttribute('data-message-content');
                msgChatId = e.currentTarget.getAttribute('data-chat-id');
                if (dropdown.style.display === 'block') {
                    dropdown.style.display = 'none';
                } else {
                    dropdown.style.display = 'block';
                }
            }
            if (message.sender_user_id === senderId) {
                 editItem.onclick = (e) => {
                    loadMessageToEdit(msgContent, msgChatId, msgId)
                    dropdown.style.display = 'none'
                 }
            }
            deleteItem.onclick = (e) => {
                document.querySelector('.delete-form').style.display = 'block'
                const delete_at_home = document.querySelector('.delete_at_home')
                const delete_at_all = document.querySelector('.delete_at_all')
                const close = document.querySelector('.close')
                delete_at_home.onclick = (e) => {
                   deleteMessage([msgId], msgContent, msgChatId, 'Только у себя')
                }
                delete_at_all.onclick = (e) => {
                   deleteMessage([msgId], msgContent, msgChatId, 'У всех')
                }
                close.onclick = (e) => {
                   document.querySelector('.delete-form').style.display = 'none'
                }
                dropdown.style.display = 'none'
            }
            answerItem.onclick = (e) => {
                loadMessageToAnswer(msgContent, msgChatId, msgId)
                dropdown.style.display = 'none'
            }
            transmissionItem.onclick = (e) => {
                document.querySelector('.transmission-form').style.display = 'block'
                fetch('/api/get_chats/', { // Замените на ваш реальный эндпоинт
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Используйте токен доступа
                    }
                })
                .then(response => response.json())
                .then(data => {
                    selectChatForTransmission(data.chats, msgContent, msgId, msgChatId);
                })
            }
            li.appendChild(menuBtn);
            li.appendChild(messageContainer);
            messageList.appendChild(li);
        });

        messageContainer.scrollTop = messageContainer.scrollHeight;
    })

}

function loadMessageToAnswer(content, chat_id, messageId) {
    const sendButton = document.getElementById('sendMessageButton');
    const messageInput = document.getElementById('messageContent');

    // Удаляем старую кнопку
    const oldBtn = document.querySelector('.temp-answer-btn');
    if (oldBtn) oldBtn.remove();

    // Создаём кнопку
    const answerButton = document.createElement('button');
    answerButton.className = 'temp-answer-btn';
    answerButton.innerHTML = `
        <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: none; stroke: white; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;">
            <path d="M3 10H13C17 10 19 12 19 16"/>
            <polyline points="8 5 3 10 8 15"/>
        </svg>
    `;
    answerButton.style.cssText = 'background:#4a90e2; border:none; border-radius:50%; width:40px; height:40px; font-size:20px; cursor:pointer; margin-left:10px;';

    sendButton.style.display = 'none';
    document.querySelector('.input-panel').appendChild(answerButton);
    messageInput.focus();
    // Сохраняем
    answerButton.onclick = () => {
        const answer = messageInput.value
        answerMessage(answer, chat_id, messageId);
        answerButton.remove();
        sendButton.style.display = 'block';
        messageInput.value = '';
        messageInput.style.border = '';
        messageInput.style.backgroundColor = '';
    };
}

function loadMessageToTransmission(content, to_chat_id, messageId, chat_id) {
    isInActionMode = true;
    const sendButton = document.getElementById('sendMessageButton');
    const messageInput = document.getElementById('messageContent');

    // Удаляем старую кнопку
    const oldBtn = document.querySelector('.temp-transmission-btn');
    if (oldBtn) oldBtn.remove();

    // Создаём кнопку
    const transmissionButton = document.createElement('button');
    transmissionButton.className = 'temp-transmission-btn';
    transmissionButton.innerHTML = `
        <svg viewBox="0 0 24 24" style="width: 20px; height: 20px;">
            <path fill="white" d="M12,4L10.59,5.41L16.17,11H4V13H16.17L10.59,18.59L12,20L20,12L12,4Z"/>
        </svg>
    `;
    transmissionButton.style.cssText = 'background:#4a90e2; border:none; border-radius:50%; width:40px; height:40px; font-size:20px; cursor:pointer; margin-left:10px;';

    sendButton.style.display = 'none';
    document.querySelector('.input-panel').appendChild(transmissionButton);

    messageInput.focus();

    // Сохраняем
    transmissionButton.onclick = () => {
        const answer = messageInput.value
        transmissionMessage(answer, chat_id, to_chat_id, messageId);
        transmissionButton.remove();
        sendButton.style.display = 'block';
        messageInput.value = '';
        messageInput.style.border = '';
        messageInput.style.backgroundColor = '';
        isInActionMode = false
    };
}

function answerMessage(answer, chat_id, message_id) {
    fetch('/api/message_answer/', { // Эндпоинт для создания нового чата
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({ answer, chat_id, message_id}),
   })
   .then(response => response.json())
   .then (data => {
        loadMessages(chat_id);
   })
}

function transmissionMessage(answer, chat_id, to_chat_id, message_id) {
    fetch('/api/message_transmission/', { // Эндпоинт для создания нового чата
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({ answer, chat_id, to_chat_id, message_id}),
   })
   .then(response => response.json())
   .then (data => {
        loadMessages(chat_id);
   })
}

function loadMessageToEdit(content, chat_id, messageId) {
    const sendButton = document.getElementById('sendMessageButton');
    const messageInput = document.getElementById('messageContent');

    // Удаляем старую кнопку
    const oldBtn = document.querySelector('.temp-edit-btn');
    if (oldBtn) oldBtn.remove();

    // Создаём кнопку
    const editButton = document.createElement('button');
    editButton.className = 'temp-edit-btn';
    editButton.innerHTML = `
        <svg viewBox="0 0 24 24" style="width: 20px; height: 20px;">
            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            <path d="M0 0h24v24H0z" fill="none"/>
        </svg>
    `;
    editButton.style.cssText = 'background:#4a90e2; border:none; border-radius:50%; width:40px; height:40px; font-size:20px; cursor:pointer; margin-left:10px;';

    sendButton.style.display = 'none';
    document.querySelector('.input-panel').appendChild(editButton);

    messageInput.value = content;
    messageInput.focus();

    // Сохраняем
    editButton.onclick = () => {
        if (messageInput.value.trim()) {
            editMessage(messageInput.value, chat_id, messageId);
        }
        // Очищаем
        editButton.remove();
        sendButton.style.display = 'block';
        messageInput.value = '';
        messageInput.style.border = '';
        messageInput.style.backgroundColor = '';
    };
}

function editMessage(content, chat_id, message_id) {
    fetch('/api/message/', { // Эндпоинт для редактирования сообщения
       method: 'PUT',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({ content, chat_id, message_id}),
   })
   .then(response => response.json())
   .then (data => {
        loadMessages(chat_id);
   })
}

function deleteMessage(message_ids, content, chat_id, delete_type) {
    const formData = new FormData();
    for (let i = 0; i <= message_ids.length - 1; i++) {
       formData.append(`message_ids[${i}]`, message_ids[i]);;
    }
    if (content === '') {
        formData.append('content', 'Media')
    } else {
        formData.append('content', content)
    }
    formData.append('chat_id', chat_id)
    formData.append('delete_type', delete_type)
    fetch('/api/message/', { // Эндпоинт для удаления сообщения
       method: 'DELETE',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: formData,
    })
    .then(response => response.json())
    .then (data => {
         loadMessages(chat_id);
    })
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/firebase-messaging-sw.js', {scope: '/'}).then(function(registration) {

      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function(err) {
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
   if (photo) {
       if (photo_group_input.files.length > 0) {
           for (let i = 0; i < photo_group_input.files.length; i++) {
               console.log(photo_group_input.files[i])
               formData.append('photo', photo_group_input.files[i]);
           }
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
   let chat_type = ''
   for (chat of chatObj) {
       if (chat.id === currentChatId) {
            chat_type = chat.type
       }
   }
   let message_url = ''
   if (chat_type === 'user' || chat_type === 'group') {
        message_url = '/api/message/'
   } else if (chat_type === 'bot') {
        message_url = '/api/message_bot/'
   }
   fetch(message_url, { // Эндпоинт для создания сообщения
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
        img.style.borderRadius = "30px"
        if (chat.content.length > 13) {
            p.textContent = chat.sender_name + chat.content.substring(0, 14) + '...';
        } else {
            p.textContent = chat.sender_name + chat.content;
        }
        li.onclick = () => {
            const listChat = document.getElementById('chats')
            const allLists = listChat.querySelectorAll('li')
            const mediaIcons = document.getElementById('media')
            document.querySelector('.option-form').style.display = 'none';
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

function selectChatForTransmission(chats, msgContent, msgId, msgChatId) {
    const chatList = document.getElementById('chats_for_transmission');
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
        img.style.borderRadius = "30px"
        li.onclick = () => {
            const listChat = document.getElementById('chats_for_transmission')
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
            if (msgContent && msgId) {
                loadMessageToTransmission(msgContent, chat.id, msgId, msgChatId)
            }
            li.style.backgroundColor = '#1F9494';
            document.querySelector('.transmission-form').style.display = 'none'
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

let users = [];
let selectedUserIds = [];
let selectedUser = null;
let rest_usernames = []
let currentChatId = null


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
        displayUsers(users)
    })
    .catch(error => console.error('Ошибка при получении пользователей:', error));
}

function displayUsers(users) {
    const userList = document.getElementById('groupUsers');
    if (userList) {
        userList.innerHTML = ''; // Очистить список
        if (users.length > 0) { // Проверяем, есть ли пользователи
            users.forEach(user => {
                const li = document.createElement('li');
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
    } else {
    }

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
   .catch(error => console.error('Ошибка:', error));
}

function editChat(groupUsers, chat_id, name, bio, photo, type) {
   const formData = new FormData();
   for (let i = 0; i <= groupUsers.length - 1; i++) {
      formData.append(`users[${i}]`, groupUsers[i]);;
   }
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

function chatUserView(chatId) {
    fetch(`/api/chat/?chat_id=${chatId}`, {
       method: 'GET',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
         },
    })
    .then(response => response.json())
    .then(data => {
        const userList = document.getElementById('groupUsersEdit');
        userList.innerHTML = ''; // Очистить список
        const usersGroup = data.users
        let photo = document.getElementById('photoGroup');
        photo.src = data.photo;
        photo.style.width = '150px';
        photo.style.height = '150px';
        let name_of_group = document.getElementById('name_group_input');
        let bio = document.getElementById('bio_group_input');
        name_of_group.value = data.name;
        bio.value = data.bio;
        // Добавляем стили для списка
        userList.style.listStyle = 'none';
        userList.style.padding = '0';
        userList.style.margin = '0';
        let current_chat_usernames = []
        for (user of usersGroup) {
            current_chat_usernames.push(user[0])
        }
        for (user of users) {
            if (current_chat_usernames.includes(user.username) == false) {
                rest_usernames.push(user)
            }
        }
        currentChatId = chatId
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
            const button = document.createElement('span')
            li.appendChild(img)
            li.appendChild(span)
            li.appendChild(role)
            if (user[2] == '') {
                const button = document.createElement('button')
                button.id = 'delete-user'
                button.textContent = 'Удалить';
                button.style.backgroundColor = 'transparent';
                button.style.color = 'red';
                button.style.borderRadius = '20px';
                button.style.fontSize = '12px';
                button.style.fontWeight = '600';
                button.onclick = function(e) {
                    e.preventDefault();
                    document.querySelector('.delete-or-no').style.display = 'block';
                    for (us of users) {
                        if (us.username === user[0]) {
                            selectedUser = us.id
                        }
                    }
                }
                li.appendChild(button)
            }
            userList.appendChild(li);
            getCurrentUser().then(currentUser => {
                if (currentUser.name === user[0] && user[2] === 'Создатель') {
                    document.querySelector('.edit-group').style.display = 'block'
                    document.getElementById('photo_group_input').style.display = 'block'
                    document.getElementById('name_group_input').disabled = 0
                    document.getElementById('bio_group_input').disabled = 0
                    document.querySelector('.select-user').disabled = 0
                }
            })
        });
    })
}

function deleteUserFromGroup(chat_id, user_id) {
    fetch('/api/delete_user_from_group/', { // Эндпоинт для создания нового чата
       method: 'DELETE',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({ chat_id, user_id }),
   })
   .then(response => response.json())
}


fetchUsers()

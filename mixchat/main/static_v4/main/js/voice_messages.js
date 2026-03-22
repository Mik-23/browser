document.getElementById('writeVoice').addEventListener('click', () => {
  let mediaRecorder;
  let audioChunks = [];

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const options = { mimeType: 'audio/webm;codecs=opus' };
      let recorderOptions = options;

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.warn(`${options.mimeType} не поддерживается, оставляем без типов`);
        recorderOptions = {}; // без типа
      } else {
        recorderOptions = { mimeType: options.mimeType };
      }

      // Создаем Recorder с поддерживаемым типом
      mediaRecorder = new MediaRecorder(stream, recorderOptions);

      mediaRecorder.onstart = () => console.log('Запись началась');
      mediaRecorder.ondataavailable = event => {
        console.log('Поступили данные:', event.data);
        audioChunks.push(event.data);
      };
      mediaRecorder.onstop = () => {
        console.log('Длина массива:', audioChunks.length);
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // или другой поддерживаемый тип
        audioChunks = [];

        const formData = new FormData();
        formData.append('chat_id', currentChatId);
        formData.append('type', type);
        console.log(type)
        console.log(currentChatId)
        formData.append('content', '');
        formData.append('audio', audioBlob, 'audio.webm');
        console.log(formData.get('audio'));
        console.log(audioBlob);
        console.log(audioChunks);
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
     };

      console.log('Начинаем запись...');
      mediaRecorder.start();
      document.getElementById('writeVoice').addEventListener('click', () => {
          mediaRecorder.stream.getTracks().forEach(track => track.stop());
      })
    })
 });

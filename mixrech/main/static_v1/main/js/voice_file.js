document.getElementById('writeVoice').addEventListener('click', () => {
  let mediaRecorder;
  let audioChunks = [];

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const options = { mimeType: 'audio/webm;codecs=opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.warn(`${options.mimeType} не поддерживается, попробуйте оставить без типа`);
      }
      
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.onstart = () => console.log('Запись началась');
      mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
      };
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioChunks = [];
        console.log(audioChunks)
        // Отправка файла на сервер
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');
        console.log(formData)
        console.log('Медиа пластина:', mediaRecorder.mimeType);

        fetch('https://voice.mixrech.com/start-recording', { // ваш URL для приема аудио
          method: 'POST',
          body: formData,
        }).then(response => response.text())
          .then(text => console.log('Распознанный текст:', text))
          .catch(console.error);
      };
      // Запуск записи, остановка через N секунд или по кнопке
      console.log('Начинаем запись...');
      mediaRecorder.start();
      setTimeout(() => {
        console.log('Останавливаем запись');
        mediaRecorder.stop();
      }, 5000);
    })
    .catch(err => console.error('Ошибка доступа к микрофону:', err));
});





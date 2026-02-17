document.getElementById('writeVoice').addEventListener('click', () => {
  let mediaRecorder;
  let audioChunks = [];

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
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

        fetch('https://voice.mixrech.com/start-recording', { // ваш URL для приема аудио
          method: 'POST',
          body: formData,
        }).then(response => response.text())
          console.log(formData)
          .then(text => console.log('Распознанный текст:', text))
          .catch(console.error);
      };

      // Запуск записи, остановка через N секунд или по кнопке
      mediaRecorder.start();
      setTimeout(() => mediaRecorder.stop(), 30000); // например, 30 сек
    })
    .catch(err => console.error('Ошибка доступа к микрофону:', err));
});

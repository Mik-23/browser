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
        formData.append('file', audioBlob, 'audio.webm'); // заменил расширение и тип
        console.log('Медиа пластина:', mediaRecorder.mimeType);

        fetch('https://voice.mixrech.com/start-recording', {
          method: 'POST',
          body: formData,
        }).then(response => {
          console.log('Статус ответа:', response);
          return response.text();
          })
          .then(text => console.log('Распознанный текст:', text))
          .catch(console.error);
      };

      console.log('Начинаем запись...');
      mediaRecorder.start();

      setTimeout(() => {
        console.log('Останавливаем запись');
        mediaRecorder.stop();
      }, 5000);
    })
    .catch(err => console.error('Ошибка доступа к микрофону:', err));
});




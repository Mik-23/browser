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
        console.log(formData.get('file'));
        fetch('/search/api/voice', {
          method: 'POST',
          body: formData,
        }).then(response => {
          console.log('Статус ответа:', response);
          return response.json();
          })
          .then(text => {
              console.log('Распознанный текст:', text)
              const input = document.querySelector('input[name="query"]');
              input.value = text.data.result;
              const searchButton = document.querySelector('button.btn.btn-outline-success[type="submit"]');
              if (input.value != '') {
                searchButton.click()
              } else {
              }

          })
          .catch(console.error);
      };

      console.log('Начинаем запись...');
      mediaRecorder.start();

      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      let silenceStart = null;      // Время начала тишины
      const silenceThreshold = 30;  // Порог громкости (0-255), ниже которого считаем тишину
      const maxSilenceTime = 1500;  // Максимальное время тишины (мс), после которого остановим запись

      function checkSilence() {
        analyser.getByteFrequencyData(dataArray);
        const volume = dataArray.reduce((a,b) => a + b) / dataArray.length;
        // console.log('Громкость:', volume.toFixed(2));

        if (volume < silenceThreshold) {
          if (silenceStart === null) {
            silenceStart = Date.now();
          } else {
            let silenceDuration = Date.now() - silenceStart;
            if (silenceDuration > maxSilenceTime) {
              console.log('Обнаружена тишина, останавливаем запись');
              mediaRecorder.stop();
              audioContext.close();
              return; // прекратить вызов таймера
            }
          }
        } else {
          silenceStart = null; // звук появился — сброс таймера тишины
        }

        requestAnimationFrame(checkSilence);
      }

      checkSilence();
    })
    .catch(err => console.error('Ошибка доступа к микрофону:', err));
});



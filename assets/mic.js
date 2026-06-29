(function() {
  'use strict';

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    console.warn('MentorAI: grabacion de audio no soportada en este navegador.');
    return;
  }

  var __audioStream = null;
  var __mediaRecorder = null;
  var __audioChunks = [];

  window.startMicRecording = function() {
    if (__mediaRecorder && __mediaRecorder.state === 'recording') {
      return Promise.resolve();
    }
    return navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function(stream) {
        __audioStream = stream;
        __mediaRecorder = new MediaRecorder(stream);
        __audioChunks = [];
        __mediaRecorder.ondataavailable = function(e) {
          if (e.data.size > 0) __audioChunks.push(e.data);
        };
        __mediaRecorder.start();
      })
      .catch(function(err) {
        console.error('MentorAI: error al acceder al microfono:', err.message);
      });
  };

  window.stopMicRecording = function() {
    return new Promise(function(resolve) {
      if (!__mediaRecorder || __mediaRecorder.state === 'inactive') {
        resolve('');
        return;
      }
      __mediaRecorder.onstop = function() {
        var blob = new Blob(__audioChunks, { type: 'audio/webm' });
        var reader = new FileReader();
        reader.onload = function() {
          if (__audioStream) {
            __audioStream.getTracks().forEach(function(t) { t.stop(); });
          }
          __audioStream = null;
          __mediaRecorder = null;
          resolve(reader.result);
        };
        reader.onerror = function() {
          console.error('MentorAI: error al leer blob de audio');
          resolve('');
        };
        reader.readAsDataURL(blob);
      };
      __mediaRecorder.stop();
    });
  };
})();

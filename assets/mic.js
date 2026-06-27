window.__audioStream = null;
window.__mediaRecorder = null;
window.__audioChunks = [];

window.startMicRecording = function() {
    return navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            window.__audioStream = stream;
            window.__mediaRecorder = new MediaRecorder(stream);
            window.__audioChunks = [];
            window.__mediaRecorder.ondataavailable = function(e) {
                if (e.data.size > 0) window.__audioChunks.push(e.data);
            };
            window.__mediaRecorder.start();
        })
        .catch(function(err) {
            console.error('Error de micrófono:', err);
        });
};

window.stopMicRecording = function() {
    return new Promise(function(resolve) {
        if (!window.__mediaRecorder || window.__mediaRecorder.state === 'inactive') {
            resolve('');
            return;
        }
        window.__mediaRecorder.onstop = function() {
            var blob = new Blob(window.__audioChunks, { type: 'audio/webm' });
            var reader = new FileReader();
            reader.onload = function() {
                if (window.__audioStream) {
                    window.__audioStream.getTracks().forEach(function(t) { t.stop(); });
                }
                resolve(reader.result);
            };
            reader.readAsDataURL(blob);
        };
        window.__mediaRecorder.stop();
    });
};

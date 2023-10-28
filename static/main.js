document.getElementById("playBtn").addEventListener("click", playGame);

async function playGame() {
    const video = document.getElementById('webcam');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    const imgData = canvas.toDataURL();
    
    const response = await fetch('/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `imgData=${encodeURIComponent(imgData)}`
    });

    const result = await response.json();
    const resultDiv = document.getElementById('result');
    
    if (result.error) {
        resultDiv.innerHTML = result.error;
    } else {
        resultDiv.innerHTML = `
            You chose: ${result.user_choice} <br>
            Computer chose: ${result.computer_choice} <br>
            Result: ${result.result}
        `;
    }
}

// Initialize webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        document.getElementById('webcam').srcObject = stream;
    });

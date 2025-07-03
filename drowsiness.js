const videoElement = document.getElementById("inputVideo");
const canvasElement = document.getElementById("outputCanvas");
const canvasCtx = canvasElement.getContext("2d");

const faceMesh = new FaceMesh({
  locateFile: (file) =>
    `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5,
});

faceMesh.onResults(onResults);

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
  videoElement.srcObject = stream;
  videoElement.play();

  videoElement.onloadedmetadata = () => {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;

    async function detectFrame() {
      await faceMesh.send({ image: videoElement });
      requestAnimationFrame(detectFrame);
    }

    detectFrame();
  };
});

function onResults(results) {
  if (!results.multiFaceLandmarks) return;

  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(
    results.image,
    0,
    0,
    canvasElement.width,
    canvasElement.height
  );

  for (const landmarks of results.multiFaceLandmarks) {
    drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, {
      color: "#00FF00",
      lineWidth: 0.5,
    });
    drawLandmarks(canvasCtx, landmarks, { color: "#FF0000", radius: 1 });
  }
}

const videoElement = document.createElement("video");
const canvasElement = document.createElement("canvas");
canvasElement.id = "outputCanvas";
const canvasCtx = canvasElement.getContext("2d");

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("demo-container");
  if (!container) return;

  videoElement.id = "inputVideo";
  container.appendChild(videoElement);
  container.appendChild(canvasElement);

  startWebcam();
});

async function startWebcam() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  videoElement.srcObject = stream;
  videoElement.play();

  const faceMesh = new FaceMesh({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
  });

  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });

  faceMesh.onResults(onResults);

  async function onFrame() {
    await faceMesh.send({ image: videoElement });
    requestAnimationFrame(onFrame);
  }

  videoElement.onloadeddata = async () => {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    onFrame();
  };
}

function onResults(results) {
  if (!results.multiFaceLandmarks) return;

  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

  for (const landmarks of results.multiFaceLandmarks) {
    drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, { color: "#00FF00", lineWidth: 0.5 });
    drawLandmarks(canvasCtx, landmarks, { color: "#FF0000", radius: 1 });
  }
}

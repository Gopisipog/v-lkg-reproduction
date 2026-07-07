"""
Browser-based recording component for Streamlit.
Uses the MediaRecorder API via embedded HTML/JS.
Supports audio, video (webcam), and screen recording.
"""

RECORDER_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: transparent; color: #262730; }

  .recorder-container { max-width: 640px; }

  .mode-selector { display: flex; gap: 8px; margin-bottom: 16px; }
  .mode-btn {
    flex: 1; padding: 10px 16px; border: 2px solid #e0e0e0; border-radius: 8px;
    background: #fafafa; cursor: pointer; text-align: center; font-size: 14px;
    font-weight: 500; transition: all 0.2s;
  }
  .mode-btn:hover { border-color: #2196F3; background: #e3f2fd; }
  .mode-btn.active { border-color: #2196F3; background: #2196F3; color: white; }

  .preview-area {
    width: 100%; aspect-ratio: 16/9; background: #1a1a2e; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; margin-bottom: 12px;
    overflow: hidden; position: relative;
  }
  .preview-area video { width: 100%; height: 100%; object-fit: contain; border-radius: 10px; }
  .preview-area.audio-mode { aspect-ratio: auto; min-height: 120px; }

  .placeholder-text { color: #6c7293; font-size: 14px; text-align: center; padding: 20px; }

  .controls { display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }

  .rec-btn {
    padding: 10px 24px; border: none; border-radius: 8px; font-size: 14px;
    font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex;
    align-items: center; gap: 6px;
  }
  .rec-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-record { background: #ff4444; color: white; }
  .btn-record:hover:not(:disabled) { background: #cc0000; }
  .btn-stop { background: #333; color: white; }
  .btn-stop:hover:not(:disabled) { background: #111; }
  .btn-pause { background: #FF9800; color: white; }
  .btn-pause:hover:not(:disabled) { background: #e68900; }
  .btn-download { background: #4CAF50; color: white; }
  .btn-download:hover:not(:disabled) { background: #388E3C; }

  .timer {
    font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold;
    color: #262730; min-width: 80px;
  }
  .timer.recording { color: #ff4444; }

  .recording-indicator {
    display: inline-flex; align-items: center; gap: 6px;
    color: #ff4444; font-weight: 600; font-size: 13px;
  }
  .rec-dot {
    width: 10px; height: 10px; background: #ff4444; border-radius: 50%;
    animation: pulse 1s infinite;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

  .status-bar {
    font-size: 12px; color: #888; padding: 6px 0; border-top: 1px solid #eee;
    margin-top: 8px;
  }

  .audio-visualizer {
    width: 100%; height: 80px; border-radius: 8px;
  }

  .settings { margin-bottom: 12px; }
  .settings label { font-size: 13px; color: #555; margin-right: 12px; }
  .settings select { padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; font-size: 13px; }
</style>
</head>
<body>
<div class="recorder-container">

  <!-- Mode Selector -->
  <div class="mode-selector">
    <div class="mode-btn active" data-mode="audio" onclick="selectMode('audio')">
      🎙️ Audio
    </div>
    <div class="mode-btn" data-mode="video" onclick="selectMode('video')">
      📹 Video
    </div>
    <div class="mode-btn" data-mode="screen" onclick="selectMode('screen')">
      🖥️ Screen
    </div>
  </div>

  <!-- Settings -->
  <div class="settings" id="settings">
    <label>Quality:
      <select id="qualitySelect">
        <option value="low">Low (smaller file)</option>
        <option value="medium" selected>Medium</option>
        <option value="high">High (larger file)</option>
      </select>
    </label>
  </div>

  <!-- Preview Area -->
  <div class="preview-area audio-mode" id="previewArea">
    <div class="placeholder-text" id="placeholder">
      Click <strong>Start Recording</strong> to begin
    </div>
    <video id="livePreview" autoplay muted playsinline style="display:none;"></video>
    <video id="playback" controls playsinline style="display:none;"></video>
    <canvas id="audioCanvas" class="audio-visualizer" style="display:none;"></canvas>
  </div>

  <!-- Controls -->
  <div class="controls">
    <button class="rec-btn btn-record" id="btnRecord" onclick="startRecording()">
      ⏺ Start Recording
    </button>
    <button class="rec-btn btn-pause" id="btnPause" onclick="togglePause()" disabled>
      ⏸ Pause
    </button>
    <button class="rec-btn btn-stop" id="btnStop" onclick="stopRecording()" disabled>
      ⏹ Stop
    </button>
    <button class="rec-btn btn-download" id="btnDownload" onclick="downloadRecording()" disabled style="display:none;">
      ⬇️ Download
    </button>
    <span class="timer" id="timer">0:00</span>
    <span class="recording-indicator" id="recIndicator" style="display:none;">
      <span class="rec-dot"></span> REC
    </span>
  </div>

  <div class="status-bar" id="statusBar">Ready — select a recording mode and press Start</div>
</div>

<script>
  let mediaRecorder = null;
  let recordedChunks = [];
  let currentStream = null;
  let currentMode = 'audio';
  let timerInterval = null;
  let seconds = 0;
  let isPaused = false;
  let recordedBlob = null;
  let audioContext = null;
  let analyser = null;
  let animationId = null;

  const QUALITY = {
    low:    { audio: 64000,  video: 500000 },
    medium: { audio: 128000, video: 1500000 },
    high:   { audio: 256000, video: 4000000 },
  };

  function selectMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

    const previewArea = document.getElementById('previewArea');
    previewArea.classList.toggle('audio-mode', mode === 'audio');

    resetUI();
    updateStatus(`Mode: ${mode} — ready to record`);
  }

  function getQuality() {
    return document.getElementById('qualitySelect').value;
  }

  function getMimeType() {
    // Prefer webm; fallback for Safari
    const types = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4', 'audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'];
    if (currentMode === 'audio') {
      const audioTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
      for (const t of audioTypes) { if (MediaRecorder.isTypeSupported(t)) return t; }
    }
    for (const t of types) { if (MediaRecorder.isTypeSupported(t)) return t; }
    return '';
  }

  async function getStream() {
    const q = getQuality();

    if (currentMode === 'audio') {
      return await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 44100 }
      });
    }
    if (currentMode === 'video') {
      const videoConstraints = {
        low:    { width: 640, height: 480, frameRate: 15 },
        medium: { width: 1280, height: 720, frameRate: 24 },
        high:   { width: 1920, height: 1080, frameRate: 30 },
      };
      return await navigator.mediaDevices.getUserMedia({
        video: videoConstraints[q],
        audio: { echoCancellation: true, noiseSuppression: true }
      });
    }
    if (currentMode === 'screen') {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: 'always' },
        audio: true
      });
      // Try to add microphone audio
      try {
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioCtx = new AudioContext();
        const dest = audioCtx.createMediaStreamDestination();
        // Mix screen audio (if any) + mic audio
        screenStream.getAudioTracks().forEach(t => {
          audioCtx.createMediaStreamSource(new MediaStream([t])).connect(dest);
        });
        micStream.getAudioTracks().forEach(t => {
          audioCtx.createMediaStreamSource(new MediaStream([t])).connect(dest);
        });
        const combined = new MediaStream([
          ...screenStream.getVideoTracks(),
          ...dest.stream.getAudioTracks()
        ]);
        return combined;
      } catch (e) {
        // Microphone denied, use screen stream as-is
        return screenStream;
      }
    }
  }

  async function startRecording() {
    try {
      resetUI();
      updateStatus('Requesting permissions...');

      currentStream = await getStream();
      recordedChunks = [];
      recordedBlob = null;
      seconds = 0;

      // Show live preview
      const livePreview = document.getElementById('livePreview');
      const audioCanvas = document.getElementById('audioCanvas');
      const placeholder = document.getElementById('placeholder');

      placeholder.style.display = 'none';

      if (currentMode === 'audio') {
        audioCanvas.style.display = 'block';
        livePreview.style.display = 'none';
        startAudioVisualizer(currentStream);
      } else {
        livePreview.style.display = 'block';
        audioCanvas.style.display = 'none';
        livePreview.srcObject = currentStream;
      }

      // Configure MediaRecorder
      const q = getQuality();
      const mimeType = getMimeType();
      const options = { mimeType };

      if (currentMode === 'audio') {
        options.audioBitsPerSecond = QUALITY[q].audio;
      } else {
        options.videoBitsPerSecond = QUALITY[q].video;
      }

      mediaRecorder = new MediaRecorder(currentStream, options);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) recordedChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
        const type = currentMode === 'audio' ? `audio/${ext}` : `video/${ext}`;
        recordedBlob = new Blob(recordedChunks, { type });
        showPlayback();
        stopTimer();
        stopAudioVisualizer();
        updateStatus(`Recording complete — ${formatBytes(recordedBlob.size)} | ${formatTime(seconds)}`);
      };

      mediaRecorder.start(1000); // collect data every second
      startTimer();

      // Update UI
      document.getElementById('btnRecord').disabled = true;
      document.getElementById('btnPause').disabled = false;
      document.getElementById('btnStop').disabled = false;
      document.getElementById('recIndicator').style.display = 'inline-flex';

      updateStatus(`Recording ${currentMode}...`);

      // Handle screen share stop (user clicks browser's "Stop sharing")
      if (currentMode === 'screen') {
        currentStream.getVideoTracks()[0].onended = () => stopRecording();
      }

    } catch (err) {
      console.error('Recording error:', err);
      updateStatus(`Error: ${err.message}`);
      if (err.name === 'NotAllowedError') {
        updateStatus('Permission denied — please allow microphone/camera access');
      } else if (err.name === 'NotFoundError') {
        updateStatus('No recording device found — check your microphone/camera');
      }
    }
  }

  function togglePause() {
    if (!mediaRecorder) return;
    if (mediaRecorder.state === 'recording') {
      mediaRecorder.pause();
      isPaused = true;
      document.getElementById('btnPause').textContent = '▶ Resume';
      document.getElementById('recIndicator').style.display = 'none';
      updateStatus('Paused');
    } else if (mediaRecorder.state === 'paused') {
      mediaRecorder.resume();
      isPaused = false;
      document.getElementById('btnPause').textContent = '⏸ Pause';
      document.getElementById('recIndicator').style.display = 'inline-flex';
      updateStatus(`Recording ${currentMode}...`);
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    if (currentStream) {
      currentStream.getTracks().forEach(t => t.stop());
      currentStream = null;
    }
    document.getElementById('btnRecord').disabled = false;
    document.getElementById('btnPause').disabled = true;
    document.getElementById('btnStop').disabled = true;
    document.getElementById('recIndicator').style.display = 'none';
    document.getElementById('livePreview').style.display = 'none';
  }

  function showPlayback() {
    if (!recordedBlob) return;
    const playback = document.getElementById('playback');
    const audioCanvas = document.getElementById('audioCanvas');

    audioCanvas.style.display = 'none';
    playback.style.display = 'block';
    playback.src = URL.createObjectURL(recordedBlob);

    document.getElementById('btnDownload').style.display = 'inline-flex';
    document.getElementById('btnDownload').disabled = false;
  }

  function downloadRecording() {
    if (!recordedBlob) return;
    const ext = recordedBlob.type.includes('mp4') ? 'mp4' : 'webm';
    const prefix = currentMode === 'audio' ? 'audio' : currentMode === 'screen' ? 'screen' : 'video';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const filename = `vlkg-${prefix}-${timestamp}.${ext}`;

    const a = document.createElement('a');
    a.href = URL.createObjectURL(recordedBlob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    updateStatus(`Downloaded: ${filename}`);
  }

  // Timer
  function startTimer() {
    timerInterval = setInterval(() => {
      if (!isPaused) {
        seconds++;
        document.getElementById('timer').textContent = formatTime(seconds);
        document.getElementById('timer').classList.add('recording');
      }
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    document.getElementById('timer').classList.remove('recording');
  }

  function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  // Audio Visualizer
  function startAudioVisualizer(stream) {
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    const canvas = document.getElementById('audioCanvas');
    const ctx = canvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
      animationId = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = '#1a1a2e';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;
        const hue = (i / bufferLength) * 120 + 200; // blue to purple
        ctx.fillStyle = `hsl(${hue}, 70%, ${50 + dataArray[i] / 8}%)`;
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    }
    draw();
  }

  function stopAudioVisualizer() {
    if (animationId) cancelAnimationFrame(animationId);
    if (audioContext) audioContext.close();
    audioContext = null;
    analyser = null;
  }

  function resetUI() {
    const playback = document.getElementById('playback');
    const livePreview = document.getElementById('livePreview');
    const audioCanvas = document.getElementById('audioCanvas');
    const placeholder = document.getElementById('placeholder');

    playback.style.display = 'none';
    playback.src = '';
    livePreview.style.display = 'none';
    audioCanvas.style.display = 'none';
    placeholder.style.display = 'block';

    document.getElementById('btnDownload').style.display = 'none';
    document.getElementById('timer').textContent = '0:00';
    document.getElementById('timer').classList.remove('recording');

    stopAudioVisualizer();
  }

  function updateStatus(msg) {
    document.getElementById('statusBar').textContent = msg;
  }
</script>
</body>
</html>
"""

def get_recorder_height(mode="audio"):
    """Return appropriate iframe height for the recorder component."""
    if mode == "audio":
        return 320
    return 520

import React, { useRef, useState, useEffect } from 'react';
import { Camera, Image as ImageIcon, Flashlight, RefreshCw, Sparkles, HelpCircle } from 'lucide-react';

export default function CameraScanner({ onCapture, isLoading, onError }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [torch, setTorch] = useState(false);
  const [hasCameraAccess, setHasCameraAccess] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  // Quick preset exercises for quick testing
  const presets = [
    { label: 'Derivada 3x² + sin(x)', formula: '3*x^2 + sin(x)' },
    { label: 'Integral ∫ x² dx [0, 3]', formula: '\\int_{0}^{3} x^{2} dx' },
    { label: 'Rotacional ∇ × F (y, -x, z)', formula: 'curl(y, -x, z)' },
    { label: 'Gradiente ∇f (x²y + sin(z))', formula: 'x**2*y + sin(z)' },
  ];

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    setCameraError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      setStream(mediaStream);
      setHasCameraAccess(true);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.warn("No camera access or permission denied:", err);
      setHasCameraAccess(false);
      setCameraError("Cámara no disponible. Puedes subir una foto desde tus archivos o probar los ejercicios de ejemplo.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const toggleTorch = async () => {
    if (!stream) return;
    const track = stream.getVideoTracks()[0];
    if (track && track.getCapabilities && track.getCapabilities().torch) {
      try {
        await track.applyConstraints({
          advanced: [{ torch: !torch }]
        });
        setTorch(!torch);
      } catch (err) {
        console.warn("Torch failed:", err);
      }
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
    onCapture(dataUrl, 'image/jpeg');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      onCapture(event.target.result, file.type || 'image/jpeg');
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="camera-scanner-container">
      {/* Top Header */}
      <header className="scanner-header">
        <div className="logo-badge">
          <Sparkles className="sparkle-icon" size={20} />
          <span>Photomath Vectorial</span>
        </div>
        {hasCameraAccess && (
          <button
            className={`icon-btn ${torch ? 'active' : ''}`}
            onClick={toggleTorch}
            title="Linterna"
          >
            <Flashlight size={20} />
          </button>
        )}
      </header>

      {/* Main Scanner Viewport */}
      <div className="viewport-wrapper">
        {hasCameraAccess ? (
          <div className="video-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="camera-video"
            />
            {/* Photomath Bounding Box & Target Frame */}
            <div className="scan-overlay">
              <div className="target-box">
                <div className="corner top-left"></div>
                <div className="corner top-right"></div>
                <div className="corner bottom-left"></div>
                <div className="corner bottom-right"></div>
                <div className="laser-line"></div>
                <p className="scan-instruction">Apunta con la cámara a la ecuación</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="no-camera-fallback">
            <div className="fallback-card">
              <Camera size={48} className="fallback-icon" />
              <h3>Apunta la Cámara a tu Ejercicio</h3>
              <p>{cameraError || "Selecciona una imagen de tu dispositivo o usa los ejemplos."}</p>
              <button className="secondary-btn" onClick={startCamera}>
                <RefreshCw size={18} /> Reintentar Cámara
              </button>
            </div>
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />

      {/* Controls Bar */}
      <div className="controls-bar">
        <button
          className="gallery-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
        >
          <ImageIcon size={24} />
          <span>Galería</span>
        </button>

        <button
          className="shutter-btn"
          onClick={capturePhoto}
          disabled={isLoading || !hasCameraAccess}
        >
          <div className="shutter-inner">
            <Camera size={32} />
          </div>
        </button>

        <div className="dummy-spacer"></div>
      </div>

      {/* Quick Example Presets for Testing */}
      <div className="presets-section">
        <span className="presets-title">
          <HelpCircle size={16} /> Ejemplos de prueba rápidos:
        </span>
        <div className="presets-grid">
          {presets.map((preset, idx) => (
            <button
              key={idx}
              className="preset-chip"
              onClick={() => onCapture(null, null, preset.formula)}
              disabled={isLoading}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

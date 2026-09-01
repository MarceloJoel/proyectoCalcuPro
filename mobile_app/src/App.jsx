import React, { useState, useEffect } from 'react';
import CameraScanner from './components/CameraScanner';
import LatexEditor from './components/LatexEditor';
import SolutionViewer from './components/SolutionViewer';
import { transcribeImageToLatex, solveMathProblem, checkBackendHealth } from './services/api';
import { AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import './App.css';

export default function App() {
  const [view, setView] = useState('SCANNER'); // 'SCANNER' | 'EDITOR' | 'SOLUTION'
  const [capturedImage, setCapturedImage] = useState(null);
  const [detectedLatex, setDetectedLatex] = useState('');
  const [solutionData, setSolutionData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  // Check backend connectivity on mount
  useEffect(() => {
    async function verifyBackend() {
      const res = await checkBackendHealth();
      setIsBackendOnline(res.status === 'ok');
    }
    verifyBackend();
    const interval = setInterval(verifyBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Handle photo captured from camera or gallery
  const handleCapture = async (imageBase64, mimeType, presetFormula = null) => {
    setErrorMessage(null);

    // If preset formula selected directly
    if (presetFormula) {
      setCapturedImage(null);
      setDetectedLatex(presetFormula);
      setView('EDITOR');
      return;
    }

    if (!imageBase64) return;

    setCapturedImage(imageBase64);
    setIsLoading(true);

    try {
      // Call /ocr endpoint
      const latexResult = await transcribeImageToLatex(imageBase64, mimeType);
      setDetectedLatex(latexResult);
      setView('EDITOR');
    } catch (err) {
      console.warn("OCR failed, switching to editor so user can input formula:", err);
      setErrorMessage(
        "No se pudo extraer el texto de la imagen automáticamente. Puedes escribir la fórmula manualmente a continuación."
      );
      setDetectedLatex('');
      setView('EDITOR');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle solving formula
  const handleSolve = async (latexFormula, variable = 'x') => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await solveMathProblem(latexFormula, variable);
      setSolutionData(result);
      setView('SOLUTION');
    } catch (err) {
      console.error("Solve error:", err);
      setErrorMessage(err.message || "Error al resolver la ecuación. Verifica la sintaxis.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setCapturedImage(null);
    setDetectedLatex('');
    setSolutionData(null);
    setErrorMessage(null);
    setView('SCANNER');
  };

  return (
    <div className="app-main-container">
      {/* Backend Status Banner */}
      {!isBackendOnline && (
        <div className="offline-banner">
          <WifiOff size={16} />
          <span>Servidor Backend fuera de línea. Inicia `uvicorn app.main:app` en puerto 8000.</span>
        </div>
      )}

      {/* Global Error Banner */}
      {errorMessage && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          <span>{errorMessage}</span>
          <button className="close-error-btn" onClick={() => setErrorMessage(null)}>✕</button>
        </div>
      )}

      {/* Active View Render */}
      {view === 'SCANNER' && (
        <CameraScanner
          onCapture={handleCapture}
          isLoading={isLoading}
        />
      )}

      {view === 'EDITOR' && (
        <LatexEditor
          imagePreview={capturedImage}
          initialLatex={detectedLatex}
          onSolve={handleSolve}
          onBack={handleReset}
          isLoading={isLoading}
        />
      )}

      {view === 'SOLUTION' && (
        <SolutionViewer
          solutionData={solutionData}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

/**
 * Client service to communicate with Photomath Vectorial FastAPI Backend
 */

// Auto-detect backend host using location.hostname for local network mobile testing
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl;

  const hostname = window.location.hostname || 'localhost';
  return `http://${hostname}:8000/api/v1`;
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Transcribe image base64 to LaTeX math string using /ocr endpoint
 */
export async function transcribeImageToLatex(imageBase64, mimeType = 'image/jpeg') {
  const cleanBase64 = imageBase64.includes(',')
    ? imageBase64.split(',')[1]
    : imageBase64;

  const response = await fetch(`${API_BASE_URL}/ocr`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_base64: cleanBase64,
      mime_type: mimeType,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail?.message || `Error ${response.status}: No se pudo procesar la imagen.`;
    throw new Error(message);
  }

  const data = await response.json();
  return data.latex;
}

/**
 * Generic solver endpoint: classifies problem automatically & solves step-by-step
 */
export async function solveMathProblem(expression, variable = 'x') {
  const response = await fetch(`${API_BASE_URL}/solve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      expression,
      variable,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail?.message || `Error ${response.status}: No se pudo resolver el problema.`;
    throw new Error(message);
  }

  return await response.json();
}

/**
 * Specialized endpoints for explicit math operations
 */
export async function solveSpecialized(endpointPath, payload) {
  const response = await fetch(`${API_BASE_URL}/solve/${endpointPath}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail?.message || `Error ${response.status}: Falló el cálculo especializado.`;
    throw new Error(message);
  }

  return await response.json();
}

/**
 * Check backend health
 */
export async function checkBackendHealth() {
  try {
    const hostname = window.location.hostname || 'localhost';
    const response = await fetch(`http://${hostname}:8000/health`, {
      signal: AbortSignal.timeout(3000)
    });
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    return { status: 'offline', error: e.message };
  }
  return { status: 'offline' };
}

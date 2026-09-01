# 📐 Photomath Vectorial — Backend & Aplicativo Móvil

**Photomath Vectorial** es una solución completa (Backend Python + Aplicativo Móvil Web PWA en React) que permite capturar fotografías de ejercicios matemáticos desde un teléfono celular y obtener su **resolución explicada paso a paso** con soporte para:
- **Álgebra**: Simplificación de expresiones y solución de ecuaciones lineales y cuadráticas.
- **Cálculo Univariable**: Derivadas de cualquier orden e integrales definidas/indefinidas.
- **Cálculo Vectorial**: Gradiente (\(\nabla f\)), Divergencia (\(\nabla \cdot \mathbf{F}\)), Rotacional (\(\nabla \times \mathbf{F}\)), Integrales Dobles (\(\iint\)) e Integrales Triples (\(\iiint\)).

---

## 📱 ¿Cómo Iniciar y Abrir en tu Celular (Paso a Paso)?

Para ejecutar la aplicación completa, abre **3 terminales** en tu computadora:

### Paso 1: Iniciar el Backend (Servidor Python)
En la **Terminal 1**:
```powershell
cd photomath_vectorial
```
```
.\venv\Scripts\activate
```
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 2: Iniciar la Aplicación Móvil (Frontend React)
En la **Terminal 2**:
```powershell
cd mobile_app
```
```
npm run dev -- --host
```

### Paso 3: Generar el Enlace para el Celular
En la **Terminal 3**:
```powershell
ssh -R 80:localhost:5173 serveo.net
```
Copia el enlace `https://xxxx.serveousercontent.com` que aparecerá en pantalla y ábrelo desde el navegador de tu celular. **¡La cámara se activará al instante para escanear ecuaciones!**

---

## 📁 Estructura del Proyecto

```
photomath_vectorial/
├── app/
│   ├── main.py                     # Entry point de FastAPI + CORS
│   ├── core/
│   │   └── config.py                # Configuración (.env, API keys)
│   ├── models/
│   │   └── schemas.py               # Contratos Pydantic (request/response)
│   ├── services/
│   │   ├── classifier.py            # Clasificador de tipo de problema
│   │   ├── ocr_service.py           # Adaptador OCR (Mathpix / Gemini Vision / GPT-4o)
│   │   └── solver/                  # ── EL MOTOR MATEMÁTICO ──
│   │       ├── base.py              #   Step / SolverResult / SolverError
│   │       ├── algebra.py           #   Parseo seguro + álgebra
│   │       ├── calculus.py          #   Derivadas e integrales univariable
│   │       └── vector_calculus.py   #   Gradiente, divergencia, rotacional, ∬, ∭
│   └── api/
│       └── routes.py                # Endpoints REST (/solve, /ocr, /health)
├── tests/
│   └── test_solver.py               # Suite de 10 tests unitarios con pytest
└── requirements.txt
```

---

## 🛠️ Endpoints Principales (API REST)

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/solve` | Clasifica automáticamente y resuelve (texto libre) |
| `POST` | `/api/v1/solve/algebra` | Simplificación / ecuaciones algebraicas |
| `POST` | `/api/v1/solve/derivative` | Derivadas de orden \(n\) |
| `POST` | `/api/v1/solve/integral` | Integrales indefinidas / definidas |
| `POST` | `/api/v1/solve/vector/gradient` | Gradiente \(\nabla f\) |
| `POST` | `/api/v1/solve/vector/divergence` | Divergencia \(\nabla \cdot \mathbf{F}\) |
| `POST` | `/api/v1/solve/vector/curl` | Rotacional \(\nabla \times \mathbf{F}\) |
| `POST` | `/api/v1/solve/vector/double-integral` | Integrales dobles \(\iint\) |
| `POST` | `/api/v1/solve/vector/triple-integral` | Integrales triples \(\iiint\) |
| `POST` | `/api/v1/ocr` | Transcribe imagen codificada en base64 a LaTeX |
| `GET` | `/health` | Estado del servicio |

---

## 🧪 Pruebas Unitarias

```powershell
pytest tests/ -v
```

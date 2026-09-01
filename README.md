# 📐 Photomath Vectorial — Aplicación Móvil & Backend

**Photomath Vectorial** es una aplicación móvil web (PWA) impulsada por inteligencia artificial y cálculo simbólico (**SymPy** + **FastAPI**), diseñada para resolver problemas matemáticos de **Álgebra, Cálculo Univariable y Cálculo Vectorial** (Gradiente \(\nabla f\), Divergencia \(\nabla \cdot \mathbf{F}\), Rotacional \(\nabla \times \mathbf{F}\), Integrales Dobles y Triples) **directamente desde la cámara de tu celular** con explicaciones paso a paso en formato LaTeX (**KaTeX**).

---

## 📱 ¿Cómo funciona la Aplicación?

1. **Captura con la Cámara**: Apuntas la cámara de tu celular hacia una ecuación o problema escrito a mano o impreso.
2. **Reconocimiento OCR (IA)**: El sistema analiza la foto y transcribe automáticamente la expresión matemática a código LaTeX.
3. **Resolución Simbólica Paso a Paso**: El motor de SymPy resuelve la ecuación matemáticamente y genera la demostración paso a paso.
4. **Visualización con KaTeX**: La pantalla de tu celular muestra la solución formateada de manera elegante con notación matemática avanzada.

---

## 📁 Estructura del Proyecto

```
proyectoCalcuPro/
├── photomath_vectorial/          # 🐍 BACKEND (Python / FastAPI / SymPy / OCR)
│   ├── app/
│   │   ├── main.py               # Servidor FastAPI + configuración CORS
│   │   ├── api/routes.py         # Endpoints REST (/solve, /ocr, /health)
│   │   ├── services/ocr_service.py # OCR para transcripción de fotos (Mathpix / Gemini / GPT-4o)
│   │   └── services/solver/      # Motor matemático paso a paso (Álgebra, Cálculo, Vectorial)
│   ├── tests/                    # Tests de corrección matemática con pytest
│   └── requirements.txt          # Dependencias de Python
│
└── mobile_app/                   # 📱 FRONTEND MÓVIL (React + Vite + KaTeX)
    ├── src/
    │   ├── components/
    │   │   ├── CameraScanner.jsx # Visor de cámara en vivo con recuadro láser rojo tipo Photomath
    │   │   ├── LatexEditor.jsx   # Editor y vista previa de expresiones con KaTeX
    │   │   └── SolutionViewer.jsx# Explicación del resultado paso a paso con confeti
    │   └── services/api.js       # Conexión con el servidor backend
    └── package.json
```

---

## 🚀 Guía de Inicio Paso a Paso (Para usar en tu Celular)

Para ejecutar toda la aplicación necesitas tener **3 terminales** abiertas en tu computadora:

### 1️⃣ Terminal 1: Iniciar el Servidor Backend (Matemática)
```powershell
cd photomath_vectorial
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*(Documentación interactiva disponible en `http://localhost:8000/docs`)*

---

### 2️⃣ Terminal 2: Iniciar la App Móvil (Frontend)
```powershell
cd mobile_app
npm run dev -- --host
```

---

### 3️⃣ Terminal 3: Generar el Enlace para tu Celular
Elige una de las siguientes dos opciones para conectar tu teléfono:

#### **Opción A (Recomendada): Usar Túnel SSH Instantáneo**
```powershell
ssh -R 80:localhost:5173 serveo.net
```
*(Te dará un enlace que empieza con `https://xxxx.serveousercontent.com`. Cópialo y ábrelo en el navegador de tu celular).*

#### **Opción B: Usar tu Red WiFi Local**
Ingresa desde el navegador de tu celular a:
`https://TU_IP_LOCAL:5173` *(ejemplo: `https://192.168.1.15:5173`)*.

---

## 🧪 Pruebas Unitarias
Para verificar la exactitud del motor matemático:
```powershell
cd photomath_vectorial
.\venv\Scripts\activate
pytest tests/ -v
```

"""
ocr_service.py
--------------
Capa de integración con el proveedor de OCR/Visión que convierte una
imagen (ecuación manuscrita o impresa) en LaTeX.

Este archivo es intencionalmente un "adaptador": expone una única función
`image_to_latex()` para que el resto del backend nunca dependa del
proveedor concreto. Cambiar de Mathpix a GPT-4o Vision (o usar ambos con
fallback) implica editar SOLO este archivo.

Para el MVP se implementa el adaptador de Mathpix (el más preciso y
económico específicamente para OCR matemático) y se deja el esqueleto
listo para GPT-4o Vision / Gemini como alternativa o fallback.
"""

import base64
import httpx
from app.core.config import settings


class OcrError(Exception):
    pass


async def image_to_latex_mathpix(image_base64: str, mime_type: str = "image/jpeg") -> str:
    """
    Usa la API de Mathpix (https://docs.mathpix.com/) especializada en OCR
    de matemáticas. Devuelve el LaTeX detectado en la imagen.
    """
    if not settings.MATHPIX_APP_ID or not settings.MATHPIX_APP_KEY:
        raise OcrError("Credenciales de Mathpix no configuradas (MATHPIX_APP_ID / MATHPIX_APP_KEY).")

    payload = {
        "src": f"data:{mime_type};base64,{image_base64}",
        "formats": ["latex_styled"],
        "ocr": ["math", "text"],
    }
    headers = {
        "app_id": settings.MATHPIX_APP_ID,
        "app_key": settings.MATHPIX_APP_KEY,
        "Content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.mathpix.com/v3/text", json=payload, headers=headers)

    if response.status_code != 200:
        raise OcrError(f"Mathpix respondió con error {response.status_code}: {response.text}")

    data = response.json()
    latex = data.get("latex_styled")
    if not latex:
        raise OcrError("Mathpix no detectó ninguna expresión matemática en la imagen.")
    return latex


async def image_to_latex_vision_llm(image_base64: str, mime_type: str = "image/jpeg") -> str:
    """
    Alternativa/fallback: usa un modelo de visión (GPT-4o o Gemini Vision)
    con un prompt estricto para extraer SOLO el LaTeX, sin resolverlo
    (la resolución la hace SymPy, no el LLM, para garantizar exactitud
    matemática determinista).

    Implementación de referencia con la API de Anthropic/OpenAI-compatible;
    ajustar `client` según el proveedor elegido en producción.
    """
    if not settings.VISION_LLM_API_KEY:
        raise OcrError("VISION_LLM_API_KEY no configurada para el fallback de visión.")

    system_prompt = (
        "Eres un motor de OCR matemático. Tu única tarea es transcribir la expresión "
        "matemática de la imagen a código LaTeX exacto. No resuelvas el ejercicio, "
        "no agregues explicaciones, no agregues signos de $ ni bloques de código. "
        "Responde ÚNICAMENTE con el LaTeX crudo."
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.VISION_LLM_API_KEY}"},
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                            }
                        ],
                    },
                ],
                "max_tokens": 500,
                "temperature": 0,
            },
        )

    if response.status_code != 200:
        raise OcrError(f"Proveedor de visión respondió con error {response.status_code}: {response.text}")

    data = response.json()
    latex = data["choices"][0]["message"]["content"].strip()
    if not latex:
        raise OcrError("El modelo de visión no detectó ninguna expresión en la imagen.")
    return latex


async def image_to_latex_gemini(image_base64: str, mime_type: str = "image/jpeg") -> str:
    """
    Usa la API de Google Gemini (gemini-2.5-flash / gemini-1.5-flash) para OCR visual de matemática.
    """
    api_key = settings.VISION_LLM_API_KEY
    if not api_key:
        raise OcrError("VISION_LLM_API_KEY no configurada.")

    prompt = (
        "Eres un motor de OCR matemático. Tu única tarea es transcribir la expresión "
        "matemática de la imagen a código LaTeX exacto. No resuelvas el ejercicio, "
        "no agregues explicaciones, no agregues signos de $ ni bloques de código markdown. "
        "Responde ÚNICAMENTE con la notación LaTeX o texto matemático plano."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)

    if response.status_code != 200:
        # Fallback a gemini-1.5-flash si 2.5 da error de endpoint
        url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        async with httpx.AsyncClient(timeout=30) as client_fallback:
            response = await client_fallback.post(url_fallback, json=payload)

    if response.status_code != 200:
        raise OcrError(f"Gemini Vision respondió con error {response.status_code}: {response.text}")

    data = response.json()
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise OcrError("Gemini no devolvió ninguna respuesta.")
        text = candidates[0]["content"]["parts"][0]["text"].strip()
        # Limpiar bloques markdown ```latex ... ``` si el LLM los incluye
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1]).strip()
            else:
                text = text.replace("```latex", "").replace("```", "").strip()
        return text
    except Exception as exc:
        raise OcrError(f"Error procesando la respuesta de Gemini: {exc}")


async def image_to_latex(image_base64: str, mime_type: str = "image/jpeg") -> str:
    """
    Punto de entrada único usado por la API. Intenta Mathpix -> Gemini -> OpenAI GPT-4o.
    """
    try:
        return await image_to_latex_mathpix(image_base64, mime_type)
    except OcrError:
        pass

    try:
        return await image_to_latex_gemini(image_base64, mime_type)
    except OcrError:
        pass

    return await image_to_latex_vision_llm(image_base64, mime_type)


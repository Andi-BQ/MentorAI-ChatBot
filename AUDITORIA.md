# INFORME DE AUDITORÍA — MENTORAI

**Auditoría**: 2026-06-27 (última actualización: 2026-06-29)
**Proyecto**: MentorAI — Orientador Vocacional con IA Generativa + ML Clásico
**Estado general**: EN PRODUCCIÓN (recomendaciones corregidas aplicadas)

---

## RESUMEN EJECUTIVO

MentorAI combina un LLM (Groq/Llama-3.3) para entrevista adaptativa con Machine Learning clásico (XGBoost) para recomendación de carreras. La arquitectura es sólida: frontend Reactivo (Reflex v0.9.x + Tailwind JIT + Radix Themes), backend Python con estado reactivo vía WebSocket, y un pipeline ML serializado con joblib.

De los **16 hallazgos originales** (5 ALTOS, 5 MEDIOS, 6 BAJOS), **14 están corregidos** y 2 permanecen como mejoras futuras.

---

## HALLAZGOS CORREGIDOS

### Severidad ALTA (5/5 corregidos)

| ID | Hallazgo | Estado | Solución |
|----|----------|--------|----------|
| **H-01** | Atributo `label_encoder` incorrecto | ✅ Corregido | `CareerEngineES` usa `self.encoder`. `CareerRecommendationEngine` eliminado (ahora es alias). |
| **H-02** | Stubs de deserialización vacíos (`CalibratedWrapper`) | ✅ Corregido | `predict_proba()` ahora delega al modelo base (fallback a `model.predict_proba()`). |
| **H-03** | `.env` contiene comando shell en línea 2 | ✅ Corregido | Limpiado a solo `GROQ_API_KEY=...`. |
| **H-04** | Versiones irreales en `requirements.txt` | ✅ Corregido | Rangos reales: `scikit-learn>=1.3.0,<1.6`, `xgboost>=2.0.0,<2.1`, etc. |
| **H-05** | Python 3.11 en CI vs 3.14 local | ✅ Corregido | CI usa 3.12. Se agregó `.python-version` con 3.12. |

### Severidad MEDIA (5/5 corregidos)

| ID | Hallazgo | Estado | Solución |
|----|----------|--------|----------|
| **M-01** | `Optional` importado pero no usado | ✅ Verificado | `Optional` sí se usa en `extract_json()` — se mantiene. |
| **M-02** | `send_message()` nunca llamado | ✅ Corregido | Método eliminado (código muerto). |
| **M-03** | Sin imports explícitos para joblib | ✅ Corregido | `BASE_DIR` agregado a `sys.path`. Registro en `__main__` + import directo. |
| **M-04** | Dos implementaciones paralelas | ✅ Corregido | `mentor_app.py` movido a `legacy/mentor_app_streamlit.py`. |
| **M-05** | `build_radar_chart()` vulnerable a lista vacía | ✅ Corregido | Guard clause: `if not values: return go.Figure().to_json()`. |

### Severidad BAJA (4/6 corregidos, 2 pendientes)

| ID | Hallazgo | Estado | Solución |
|----|----------|--------|----------|
| **L-01** | `render_message(msg)` sin tipo | ✅ Corregido | Type hints agregados a todas las funciones. |
| **L-02** | `suggestion_btn(text, label)` sin tipo | ✅ Corregido | `def suggestion_card(text: str, label: str, icon: str)` |
| **L-03** | `rxconfig.py` minimalista | ✅ Corregido | Se agregaron `backend_port=8080`, `frontend_port=3000`, `host="0.0.0.0"`. |
| **L-04** | Comentarios confusos en `calibracion.py` | ✅ Corregido | Código reestructurado, comentarios eliminados. |
| **L-05** | `!important` excesivo en CSS | ✅ Verificado | El CSS actual (14 líneas) no contiene `!important`. |
| **L-06** | Variables globales sin namespace en `mic.js` | ✅ Corregido | Envuelto en IIFE, manejo de errores, detección de soporte. |

---

## MEJORAS ADICIONALES IMPLEMENTADAS

| Mejora | Archivo | Descripción |
|--------|---------|-------------|
| Alerta visual de MockEngine | `mentorai/mentorai.py` + `state.py` | Banner ámbar cuando el motor real no carga. |
| CI pipeline con lint + test | `.github/workflows/deploy.yml` | `ruff check` + `pytest` antes del deploy. |
| `.python-version` | raíz | Especifica Python 3.12 para herramientas como pyenv. |
| `legacy/` | raíz | `mentor_app_streamlit.py` movido a directorio legacy. |
| `engine_ready` computed var | `mentorai/state.py` | Flag reactivo para detectar MockEngine en UI. |

---

## PENDIENTE (Mejoras futuras)

| ID | Acción | Prioridad |
|----|--------|-----------|
| **A-13** | Layout condicional para gráficos Plotly en dark mode | Baja (UX polish) |

---

## RESUMEN DE MÉTRICAS

| Categoría | ALTA | MEDIA | BAJA | Total |
|-----------|------|-------|------|-------|
| Hallazgos originales | 5 | 5 | 6 | 16 |
| Corregidos | 5 | 5 | 4 | 14 |
| Pendientes | 0 | 0 | 2 | 2 |
| **Tasa de resolución** | **100%** | **100%** | **67%** | **87.5%** |

**Conclusión**: El proyecto está listo para operar en producción. Todos los bloqueos críticos (Fase 1) y estabilización (Fase 2) están resueltos. Queda 1 ítem de escalabilidad (dark mode en gráficos) como mejora futura.

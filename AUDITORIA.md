# AUDITORIA DE PROYECTO: MentorAI

**Fecha**: 2026-06-27
**Version**: Reflex (migrado desde Streamlit)
**Estado general**: NECESITA ATENCION

---

## 1. ESTRUCTURA DEL PROYECTO

```
D:\MentorAI-main/
├── .env                          # API key de Groq (gitignored)
├── .gitignore
├── .github/workflows/deploy.yml  # CI/CD a Reflex Cloud
├── assets/
│   ├── mic.js                    # Grabacion de audio (cliente)
│   └── style.css                 # Estilos globales
├── mentorai/
│   ├── __init__.py               # Vacio
│   ├── mentorai.py               # UI con Reflex (componentes y pagina)
│   └── state.py                  # Estado, API Groq, graficos, modelo ML
├── modelos/
│   └── motor_completo.joblib     # Modelo serializado (entrenado)
├── requirements.txt
├── rxconfig.py                   # Configuracion Reflex + Tailwind
├── src/
│   ├── __init__.py
│   ├── evaluacion/
│   │   ├── __init__.py
│   │   └── calibracion.py        # Clases para deserializar el .joblib
│   └── recomendacion/
│       ├── __init__.py
│       └── motor_recomendacion.py # Motor de recomendacion (stub)
└── mentor_app.py                 # Version Streamlit original (gitignored)
```

---

## 2. HALLAZGOS POR SEVERIDAD

### SEVERIDAD ALTA

| ID | Hallazgo | Archivo | Detalle |
|----|----------|---------|---------|
| **H-01** | Atributo `label_encoder` incorrecto | `src/recomendacion/motor_recomendacion.py:8` | El modelo serializado tiene `encoder` (no `label_encoder`). Al cargar el modelo real, `recommend()` lanza `AttributeError`. Solo funciona porque usa MockEngine (fallback). |
| **H-02** | Stubs de deserialización vacios | `src/evaluacion/calibracion.py:24-28` | `CalibratedWrapper` y `TemperatureScaler` son clases vacias. Si el modelo real las invoca en runtime, falla con `AttributeError`. |
| **H-03** | `.env` contiene comando shell en linea 2 | `.env:2` | Tiene `python -m venv venv & reflex deploy ...` mezclado con la API key. |
| **H-04** | Versiones irreales en requirements.txt | `requirements.txt` | `scikit-learn==1.8.0`, `numpy>=2.4.0`, `pandas>=3.0.0`, `xgboost>=3.2.0` no existen en PyPI. |
| **H-05** | Python 3.11 en CI vs 3.14 local | `.github/workflows/deploy.yml:16` | Workflow usa 3.11, el entorno local usa 3.14. Pueden haber incompatibilidades de bytecode/API. |

### SEVERIDAD MEDIA

| ID | Hallazgo | Archivo | Detalle |
|----|----------|---------|---------|
| **M-01** | `Optional` importado pero no usado | `mentorai/state.py:6` | Import huérfano de refactorización. |
| **M-02** | `send_message()` nunca llamado | `mentorai/state.py:222` | Código muerto; la UI usa `send_from_input()` y `send_suggestion()`. |
| **M-03** | Sin imports explicitos de `src.*` para joblib | `mentorai/state.py:27` | `joblib.load()` depende de que `src/` esté en `sys.path`, lo que no está garantizado en Reflex Cloud. |
| **M-04** | Dos implementaciones paralelas | `mentor_app.py` vs `mentorai/` | Streamlit (original, gitignored) y Reflex (actual). Riesgo de duplicacion de mantenimiento. |
| **M-05** | `build_radar_chart()` vulnerable a lista vacia | `mentorai/state.py:106` | `values[0]` lanza `IndexError` si `values` esta vacio. |

### SEVERIDAD BAJA

| ID | Hallazgo | Archivo | Detalle |
|----|----------|---------|---------|
| **L-01** | `render_message(msg)` sin tipo | `mentorai/mentorai.py:5` | Falta `: Dict[str, str]` |
| **L-02** | `suggestion_btn(text, label)` sin tipo | `mentorai/mentorai.py:23` | Falta `: str` en parametros |
| **L-03** | rxconfig.py minimalista | `rxconfig.py` | Sin puerto, host, ni config de produccion |
| **L-04** | Comentarios confusos en calibracion.py | `src/evaluacion/calibracion.py:18-31` | "clases antiguas apuntan a tu logica actual" pero estan vacias |
| **L-05** | `!important` excesivo en CSS | `assets/style.css` | Todas las reglas usan `!important` |
| **L-06** | Variables globales sin namespace en mic.js | `assets/mic.js` | Sin manejo de errores ni deteccion de soporte |

---

## 3. DEPENDENCIAS: requirements.txt vs imports reales

| Libreria | En requirements | Se importa? | Estado |
|----------|-----------------|-------------|--------|
| reflex | >=0.6.0 | Si | OK |
| openai | (sin version) | Si | OK |
| scikit-learn | ==1.8.0 | Si (src/) | Version inexistente |
| xgboost | >=3.2.0 | No directo | Necesario para modelo, version inexistente |
| numpy | >=2.4.0 | Si (src/) | Version inexistente |
| pandas | >=3.0.0 | Solo en mentor_app.py | Innecesario en version Reflex, version inexistente |
| joblib | >=1.4.0 | Si | OK |
| plotly | (sin version) | Si | OK |
| python-dotenv | (sin version) | Si | OK |

---

## 4. CONFIGURACIONES

### rxconfig.py
- Solo define `app_name` y `tailwind`
- No especifica puerto, host, ni modo dev/prod

### .gitignore
- Incluye: `.env`, `.web/`, `__pycache__/`, `*.pyc`, `mentor_app.py`, `.streamlit/`
- Correcto y completo

### .github/workflows/deploy.yml
- Trigger: push a main
- Python 3.11
- `pip install -r requirements.txt` + `reflex deploy --no-input`
- Usa `REFLEX_TOKEN` y `GROQ_API_KEY` desde secrets
- Sin paso de linting/testing previo

---

## 5. MODELO SERIALIZADO

**Archivo**: `modelos/motor_completo.joblib`
**Existe**: Si
**Clase**: `src.recomendacion.motor_recomendacion.CareerRecommendationEngine`
**Atributos internos**:
- `model`: `xgboost.sklearn.XGBClassifier`
- `scaler`: `sklearn.preprocessing.StandardScaler`
- `encoder`: `sklearn.preprocessing.LabelEncoder` (NO `label_encoder`)
- `calibrated_model`: `CalibratedWrapper` (stub vacio)
- `career_map`, `config`, `_career_names`, `_cluster_sim_matrix`, etc.

---

## 6. RECOMENDACIONES PRIORIZADAS

### Urgente (antes del proximo deploy)

1. **Renombrar `label_encoder` a `encoder`** en `src/recomendacion/motor_recomendacion.py` (lineas 8 y 22)
2. **Implementar metodos reales o `__getattr__` en `CalibratedWrapper`** en `src/evaluacion/calibracion.py`
3. **Limpiar `.env`**: eliminar linea 2 (comando shell)
4. **Corregir versiones en `requirements.txt`**:
   ```
   scikit-learn>=1.3.0,<1.6
   xgboost>=2.0.0,<2.2
   numpy>=1.26.0,<2.1
   pandas>=2.1.0,<2.3
   ```
5. **Unificar version de Python** (3.11, 3.12, o 3.13) entre CI y local

### Corto plazo (proximas 2 semanas)

6. Agregar imports explicitos de `src.*` en `state.py` para joblib
7. Eliminar `mentor_app.py` del disco o moverlo a `legacy/`
8. Agregar guard clause en `build_radar_chart()` para lista vacia
9. Eliminar `send_message()` (codigo muerto)

### Medio plazo (proximos 1-2 meses)

10. Type hints completos en `mentorai/mentorai.py`
11. Refactorizar `assets/mic.js` con manejo de errores
12. Reducir `!important` en `assets/style.css`
13. Agregar config de puerto/host en `rxconfig.py`
14. Agregar pipeline de CI con linter (ruff) y tests

---

## 7. RESUMEN

| Categoria | ALTA | MEDIA | BAJA | Total |
|-----------|------|-------|------|-------|
| Bugs/Logica | 2 | 3 | 0 | 5 |
| Seguridad/Config | 2 | 1 | 0 | 3 |
| Dependencias/CI | 1 | 0 | 0 | 1 |
| Estilo/Mantenibilidad | 0 | 1 | 6 | 7 |
| **Total** | **5** | **5** | **6** | **16** |

**Conclusion**: El proyecto tiene una arquitectura solida (Reflex + Groq + modelo ML) pero los **5 hallazgos de severidad ALTA** impiden su funcionamiento correcto en produccion. Se recomienda priorizar su correccion antes del proximo deploy.

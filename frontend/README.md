# BioControl — interfaz

Consulta el motor de biocontrol (FastAPI) desde el navegador. Los cultivos, las plagas, el agente, la ventana y la fuente salen de la API. No hay cifras fijas en la pantalla.

## Requisitos

- Node.js 20 o superior
- La API en marcha, desde la raíz del repositorio:

```bash
uvicorn app.main:app --reload
```

## Arranque

```bash
cp .env.example .env
npm install
npm run dev
```

En Windows, si `cp` no está disponible, copia `.env.example` a `.env`. La variable es:

```text
VITE_API_URL=http://localhost:8000
```

La interfaz queda en <http://localhost:5173>.

## Qué envía el formulario

`POST /consultar` con `plaga`, `temperatura` y `humedad`. El cultivo solo filtra las plagas que la ontología asocia a ese hospedero; el motor no recibe un cultivo aparte.

La humedad se muestra como umbral únicamente cuando la respuesta trae `condiciones.humedad`. Si llega `humedad_ensayo`, la pantalla la marca como condición de ensayo.

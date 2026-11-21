# P4 - Implementación de Langfuse para SSEP-Fraude

## Instalación completa desde cero

> Objetivo: instalar Langfuse OSS localmente usando Docker Desktop, PostgreSQL, Redis, ClickHouse y MinIO, crear la organización y proyecto inicial, generar las API Keys necesarias e instrumentar completamente el proyecto para habilitar observabilidad end-to-end.

---

# 1. Verificar e instalar Docker Desktop

## Verificar instalación

```powershell
docker --version
```

Resultado esperado:

```text
Docker version 28.x.x
```

---

## Si Docker no está instalado

Descargar:

https://www.docker.com/products/docker-desktop/

Instalar con las opciones:

```text
✅ Use WSL 2 instead of Hyper-V
✅ Add shortcut to desktop
✅ Start Docker Desktop when you log in
```

Reiniciar Windows.

---

## Verificar Docker Engine

```powershell
docker ps
```

Resultado esperado:

```text
CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
```

---

# 2. Verificar e instalar WSL 2

## Verificar instalación

```powershell
wsl --status
```

Resultado esperado:

```text
Default Version: 2
```

---

## Si WSL no está instalado

Abrir PowerShell como Administrador y ejecutar:

```powershell
wsl --install
```

Reiniciar Windows.

---

## Actualizar WSL

```powershell
wsl --update
```

---

## Reiniciar WSL

```powershell
wsl --shutdown
```

---

# 3. Verificar e instalar Python

## Verificar Python

```powershell
python --version
```

Resultado esperado:

```text
Python 3.11.x
```

o superior.

---

## Si Python no está instalado

Descargar:

https://www.python.org/downloads/

Durante la instalación marcar:

```text
✅ Add Python to PATH
✅ Install launcher for all users
```

---

## Verificar pip

```powershell
pip --version
```

---

# 4. Verificar SDK Langfuse

## Verificar instalación

```powershell
pip show langfuse
```

---

## Si no está instalado

```powershell
pip install langfuse
```

---

## Verificar versión

```powershell
pip show langfuse
```

Resultado esperado:

```text
Version: 4.x.x
```

---

# 5. Crear carpeta de trabajo

```powershell
mkdir langfuse
cd langfuse
```

---

# 6. Crear archivo .env

Crear:

```text
.env
```

Contenido:

```env
# =========================
# Langfuse
# =========================

LANGFUSE_IMAGE_TAG=4
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_BASE_URL=http://localhost:3000

# Reemplazar por las claves reales luego de crear el proyecto
LANGFUSE_PUBLIC_KEY=pk-lf-ssep
LANGFUSE_SECRET_KEY=sk-lf-ssep

# =========================
# Seguridad
# =========================

NEXTAUTH_SECRET=517a72f2-0b53-4f3b-931e-fa06609dc721
SALT=33d41ae8-1acc-4110-8405-5537dab380e3

# Generar con:
# python -c "import secrets; print(secrets.token_hex(32))"
ENCRYPTION_KEY=eaffb2989edd60829365169b5a0b0a8cb0d5b66ef2bfdda1ad10419a8fbef94d

# =========================
# PostgreSQL
# =========================

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres

# =========================
# ClickHouse
# =========================

CLICKHOUSE_USER=clickhouse
CLICKHOUSE_PASSWORD=clickhouse

# =========================
# Redis
# =========================

REDIS_AUTH=myredissecret

# =========================
# MinIO
# =========================

MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=miniosecret

# =========================
# Event Upload
# =========================

LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse
LANGFUSE_S3_EVENT_UPLOAD_REGION=auto
LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID=minio
LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=miniosecret
LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT=http://minio:9000
LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE=true

# =========================
# Media Upload
# =========================

LANGFUSE_S3_MEDIA_UPLOAD_BUCKET=langfuse
LANGFUSE_S3_MEDIA_UPLOAD_REGION=auto
LANGFUSE_S3_MEDIA_UPLOAD_ACCESS_KEY_ID=minio
LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY=miniosecret
LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT=http://minio:9000
LANGFUSE_S3_MEDIA_UPLOAD_FORCE_PATH_STYLE=true
```

---

# 7. Crear docker-compose.langfuse.yml

Crear:

```text
docker-compose.langfuse.yml
```

Copiar el archivo YAML validado y funcional.

---

# 8. Validar sintaxis del compose

```powershell
docker compose -f docker-compose.langfuse.yml config
```

Resultado esperado:

```text
services:
...
```

Sin errores.

---

# 9. Limpiar despliegues anteriores

```powershell
docker compose -f docker-compose.langfuse.yml down -v
```

---

# 10. Descargar imágenes

```powershell
docker compose -f docker-compose.langfuse.yml pull
```

---

# 11. Levantar la infraestructura

```powershell
docker compose -f docker-compose.langfuse.yml up -d
```

---

# 12. Verificar estado de los servicios

```powershell
docker compose -f docker-compose.langfuse.yml ps
```

Resultado esperado:

```text
langfuse-clickhouse   Up
langfuse-minio        Up
langfuse-postgres     Up (healthy)
langfuse-redis        Up
langfuse-web          Up
langfuse-worker       Up
```

---

# 13. Verificar logs

## Langfuse Web

```powershell
docker logs langfuse-web --tail 50
```

Resultado esperado:

```text
All migrations have been successfully applied.
```

---

## Langfuse Worker

```powershell
docker logs langfuse-worker --tail 50
```

Sin errores críticos.

---

# 14. Verificar variables S3

```powershell
docker exec -it langfuse-web env | findstr LANGFUSE_S3
```

Resultado esperado:

```text
LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse
LANGFUSE_S3_MEDIA_UPLOAD_BUCKET=langfuse
...
```

---

# 15. Acceder a la interfaz

Abrir:

```text
http://localhost:3000
```

---

# 16. Crear usuario

En la pantalla inicial:

```text
Sign Up
```

Completar:

```text
Email
Password
```

---

# 17. Crear Organización

Pantalla:

```text
Setup
Create Organization
```

Nombre recomendado:

```text
SSEP
```

Presionar:

```text
Create
```

---

# 18. Crear Proyecto

Nombre:

```text
ssep-fraude
```

Presionar:

```text
Create Project
```

---

# 19. Obtener API Keys

Ir a:

```text
Project Settings
```

Luego:

```text
API Keys
```

Aparecerán:

```text
Public Key
Secret Key
```

---

# 20. Actualizar el .env

Reemplazar:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-ssep
LANGFUSE_SECRET_KEY=sk-lf-ssep
```

por las claves reales obtenidas.

---

# 21. Reiniciar Langfuse

```powershell
docker compose -f docker-compose.langfuse.yml down
```

```powershell
docker compose -f docker-compose.langfuse.yml up -d
```

---

# 22. Instalar python-dotenv

Instalar:

```powershell
pip install python-dotenv
```

Verificar:

```powershell
pip show python-dotenv
```

---

# 23. Configurar carga automática del archivo .env

Archivo:

```text
observability/langfuse_client.py
```

Agregar:

```python
from dotenv import load_dotenv

load_dotenv()
```

Validar:

```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('HOST=', os.getenv('LANGFUSE_HOST')); print('PK=', os.getenv('LANGFUSE_PUBLIC_KEY')); print('SK=', os.getenv('LANGFUSE_SECRET_KEY'))"
```

Resultado esperado:

```text
HOST= http://localhost:3000
PK= pk-lf-xxxxxxxx
SK= sk-lf-xxxxxxxx
```

---

# 24. Validar SDK Langfuse 4.18.0

Verificar:

```powershell
pip show langfuse
```

Resultado validado:

```text
Name: langfuse
Version: 4.18.0
```

Inspeccionar API disponible:

```powershell
python -c "import langfuse; print(dir(langfuse))"
```

## Compatibilidad identificada

Implementación incorrecta:

```python
from langfuse.decorators import observe
```

Error observado:

```text
No module named 'langfuse.decorators'
```

Implementación correcta:

```python
from langfuse import observe
from langfuse import propagate_attributes
```

---

# 25. Instrumentar el pipeline principal

Archivo:

```text
main.py
```

Inicialización:

```python
init_langfuse()
```

Validación:

```python
from observability import enabled

print("Langfuse enabled:", enabled())
```

Decorador principal:

```python
@observe(name="pipeline-ssep")
```

Propagación de atributos:

```python
with propagate_attributes(
    session_id=card_id
):
```

Persistencia:

```python
flush()
```

---

# 26. Ejecutar prueba de observabilidad

```powershell
python main.py
```

Resultado validado:

```text
[Langfuse] enabled
Langfuse enabled: True
```

---

# 27. Validar recepción de trazas

Abrir:

```text
http://localhost:3000
```

Acceder a:

```text
Project
→ Tracing
```

Validar:

✅ Desaparición de:

```text
Waiting for first trace
```

✅ Visualización de:

```text
pipeline-ssep
```

✅ Caso normal

```text
CARD-7891
datos/trans_normal.txt
```

✅ Caso sospechoso

```text
CARD-4532
datos/trans_sospechosa.txt
```

✅ Caso fraude

```text
CARD-1024
datos/trans_fraude.txt
```

---

# Validación final

Confirmar:

```text
✅ Usuario creado
✅ Organización creada
✅ Proyecto creado
✅ API Keys generadas

✅ PostgreSQL operativo
✅ Redis operativo
✅ ClickHouse operativo
✅ MinIO operativo

✅ Langfuse Web operativo
✅ Langfuse Worker operativo

✅ Cliente Python configurado
✅ Trazas visibles en Langfuse
```

---

# Resultado

Infraestructura de observabilidad completamente operativa.

Validaciones completadas:

✅ Docker

✅ PostgreSQL

✅ Redis

✅ ClickHouse

✅ MinIO

✅ Langfuse Web

✅ Langfuse Worker

✅ Organización creada

✅ Proyecto creado

✅ API Keys generadas

✅ Cliente Python configurado

✅ Compatibilidad validada con Langfuse 4.18.0

✅ Decorador `@observe` operativo

✅ Trazas registradas y visibles en Langfuse

✅ Observabilidad end-to-end validada para SSEP-Fraude

---

# Estado Final de P4

Artefactos validados:

```text
docker-compose.langfuse.yml
.env
observability/langfuse_client.py
observability/__init__.py
main.py
```

Resultados obtenidos:

✅ Plataforma desplegada

✅ SDK integrado

✅ API Keys configuradas

✅ Pipeline instrumentado

✅ Tracing operativo

✅ Tres ejecuciones registradas correctamente

✅ Flujo end-to-end validado

✅ P4 completado al 100%
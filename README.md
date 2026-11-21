# ETL de Opiniones de Clientes: Proceso de Extracción

Este proyecto corresponde a la primera etapa del proceso ETL (Extracción, Transformación y Carga) del Sistema de Análisis de Opiniones de Clientes. Su objetivo es obtener información de diferentes fuentes y almacenarla temporalmente para poder utilizarla posteriormente en las etapas de transformación y carga.

El proyecto está desarrollado en Python y está organizado en tres capas: `domain`, `application` e `infrastructure`, con el propósito de mantener el código organizado y facilitar futuros cambios.

## ¿Qué hace el proyecto?

El worker se encarga de recopilar opiniones de clientes desde distintas fuentes de información. Actualmente, permite trabajar con las siguientes:

- **Archivos CSV:** obtiene las respuestas de las encuestas internas de satisfacción.
- **Archivos Excel (.xlsx):** busca y lee todos los archivos que se encuentren dentro de la carpeta `excels/`.
- **Base de datos SQL Server:** consulta las reseñas de los clientes almacenadas en la tabla `web_reviews`.
- **API REST:** obtiene comentarios provenientes de redes sociales. Para las pruebas se desarrolló una API simulada.

Las fuentes se procesan en paralelo para reducir el tiempo de ejecución. Además, si ocurre algún error al consultar una de ellas, las demás pueden continuar trabajando sin que se detenga todo el proceso.

Los eventos y errores que ocurren durante la ejecución se guardan en el archivo `logs/etl.log`, lo que permite revisar posteriormente cómo se comportó el worker.

Una vez obtenida la información, los registros se guardan en una zona temporal llamada staging. Este almacenamiento puede realizarse mediante archivos JSON en la carpeta `staging/` o directamente en tablas `stg_*` de SQL Server. La opción utilizada se define en el archivo `settings.json`.

## Requisitos para ejecutar el proyecto

Antes de iniciar, es necesario contar con:

- Python 3.10 o una versión superior.
- SQL Server con la base de datos `analisis_opiniones`.
- ODBC Driver 17 for SQL Server.

## Instalación

Primero, se debe abrir una terminal en la carpeta del proyecto y crear un entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

Luego, se instalan las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Configuración del proyecto

Para conectar las fuentes de datos, se deben realizar algunos ajustes antes de ejecutar el worker.

1. Crear el archivo `.env` a partir de la plantilla incluida en el proyecto:

```bash
copy .env.example .env
```

2. Abrir el archivo `.env` y completar los datos de conexión:

```env
DB_USER=
DB_PASSWORD=
API_TOKEN=token-demo-123
```

Si los campos `DB_USER` y `DB_PASSWORD` se dejan vacíos, el sistema utilizará la autenticación de Windows para conectarse a SQL Server.

3. Revisar el archivo `settings.json`. Allí se pueden configurar los datos del servidor, las rutas de los archivos, las fuentes que estarán activas y la forma en que se guardarán los registros extraídos.

4. Colocar los archivos CSV y Excel que se desean procesar en las carpetas `csvs/` y `excels/`, respectivamente.

Es importante tener en cuenta que el archivo `.env` contiene información de conexión, por lo que no debe subirse a GitHub. En el repositorio solamente se incluye el archivo `.env.example` como referencia para configurar el proyecto.

## Ejecución

Para probar el funcionamiento se deben abrir dos terminales dentro de la carpeta del proyecto.

**Primera terminal: iniciar la API simulada**

```bash
cd api_simulada
uvicorn app:app --port 8000
```

Esta API se utiliza para simular la obtención de comentarios desde una fuente externa.

**Segunda terminal: ejecutar el worker**

```bash
venv\Scripts\activate
python main.py
```

Al finalizar la ejecución, se muestra un resumen con el resultado de cada fuente, la cantidad de registros obtenidos y el tiempo que tomó su procesamiento.

Los datos extraídos quedan almacenados en la carpeta `staging/`, siempre que se haya seleccionado el modo de almacenamiento mediante archivos.

También es posible configurar el worker para que se ejecute automáticamente cada cierto tiempo. Para esto, se modifica el parámetro `run_interval_seconds` del archivo `settings.json`.

Por ejemplo, si se establece en `300`, el proceso se repetirá cada cinco minutos. Si se configura en `0`, el worker se ejecutará una sola vez.

## ¿Cómo agregar una nueva fuente de datos?

Una de las ventajas de la estructura utilizada es que permite incorporar nuevas fuentes sin tener que modificar todo el proceso de extracción.

Para agregar una fuente se deben seguir estos pasos:

1. Crear una nueva clase dentro de `infrastructure/extractors/` que implemente la interfaz `IExtractor`.
2. Registrar la nueva clase en `infrastructure/extractor_factory.py`.
3. Agregar su configuración en `settings.json`, indicando los parámetros necesarios y si estará activa.

De esta manera, cada fuente mantiene su propia lógica de extracción y el servicio principal puede seguir funcionando sin necesidad de realizar cambios.

## Estructura del proyecto

El código está dividido en carpetas según la responsabilidad de cada componente:

```text
├── main.py                  # Punto de entrada del worker
├── settings.json            # Configuración general del proceso
├── domain/                  # Interfaces del proyecto
│   ├── IExtractor
│   └── IDataLoader
├── application/             # Lógica del proceso de extracción
├── infrastructure/          # Conexiones y extractores de datos
│   ├── extractors/
│   ├── extractor_factory.py
│   ├── staging/
│   └── logger/
└── api_simulada/            # API utilizada para las pruebas
```

Esta organización permite mantener separadas las responsabilidades. Por ejemplo, las clases encargadas de leer archivos CSV no necesitan conocer cómo se consultan los datos de SQL Server o cómo se consumen los comentarios de la API.

Con esta estructura se busca que el proyecto sea más fácil de mantener y que, en caso de necesitar una nueva fuente de información, se pueda agregar sin afectar el funcionamiento de las demás.

# Agente Chatbot Datapath

## Descripción General

Este es un agente de chatbot inteligente desarrollado con LangGraph que funciona como asistente comercial para Datapath. El agente cuenta con memoria persistente, herramientas especializadas y capacidades de integración con Google Sheets para gestión de clientes.

## Características Principales

### 🧠 Sistema de Memoria Dual
- **Memoria a corto plazo**: Mantiene el contexto dentro de una conversación
- **Memoria a largo plazo**: Recuerda información del usuario entre diferentes sesiones
- **Personalización**: Adapta las respuestas basándose en la información recopilada del usuario

### 🔧 Herramientas Especializadas
El agente cuenta con 4 herramientas principales que le permiten realizar acciones específicas:

1. **Registro de Clientes**
2. **Consulta de Estadísticas**
3. **Información Temporal**

### 🌐 Integración con Google Sheets
- Conectividad directa con Google Sheets para almacenamiento de datos
- Autenticación flexible (local y cloud)
- Operaciones en tiempo real

## Arquitectura del Agente

### Flujo de Trabajo (LangGraph)

```
INICIO → Llamar Modelo → ¿Necesita Herramientas?
                  ↓                    ↓
            Escribir Memoria    →    Ejecutar Herramientas
                  ↓                    ↓
                 FIN           ←    Llamar Modelo
```

### Componentes Principales

#### 1. **ChatbotGraph** (`src/agent/agent.py`)
- **Propósito**: Núcleo del agente que maneja el flujo de conversación
- **Funcionalidades**:
  - Procesamiento de mensajes
  - Gestión de memoria dual
  - Coordinación de herramientas
  - Mantenimiento del historial de chat

#### 2. **Sistema de Herramientas** (`src/agent/tools.py`)
Conjunto de funciones especializadas que extienden las capacidades del agente:

##### 🏢 **registrar_cliente**
- **Función**: Registra nuevos clientes en Google Sheets
- **Parámetros**:
  - `email`: Correo electrónico del cliente
  - `nombres`: Nombre(s) del cliente
  - `apellidos`: Apellido(s) del cliente
  - `numero_documento`: Número de identificación
  - `telefono`: Número de teléfono
- **Salida**: Confirmación 'ok' si el registro fue exitoso
- **Características**:
  - Timestamp automático de registro
  - Inserción inteligente (evita sobreescribir formato)
  - Manejo de errores robusto

##### 📊 **contar_registros**
- **Función**: Cuenta el número total de clientes registrados
- **Parámetros**: Ninguno
- **Salida**: Mensaje con el número de registros (excluyendo headers)
- **Características**:
  - Excluye automáticamente la fila de encabezados
  - Acceso de solo lectura a los datos

##### 📅 **get_current_date**
- **Función**: Obtiene la fecha actual
- **Formato**: YYYY-MM-DD
- **Uso**: Para referencias temporales y registros con fecha

##### ⏰ **get_current_time**
- **Función**: Obtiene la hora actual
- **Formato**: HH:MM:SS
- **Uso**: Para timestamps precisos y referencias temporales

#### 3. **Sistema de Prompts** (`src/agent/prompts.py`)

##### **MODEL_SYSTEM_MESSAGE**
Define la personalidad y comportamiento del agente:
- **Identidad**: Asistente comercial de Datapath
- **Conocimiento**: Información sobre la empresa (fundada en 2020, +25,000 graduados)
- **Comportamiento**: Uso de memoria para personalización

##### **CREATE_MEMORY_INSTRUCTION**
Instrucciones para la gestión de memoria:
- Recopilación de información del usuario
- Actualización de memoria existente
- Formato estructurado en viñetas

#### 4. **Servicio de Chatbot** (`src/service/chatbot_service.py`)
- **Propósito**: Capa de servicio que encapsula la funcionalidad del agente
- **Métodos**:
  - `process_question()`: Procesa preguntas del usuario
  - `get_chat_history()`: Recupera historial de conversación
  - `get_memory()`: Accede a la memoria del usuario

## Configuración y Variables de Entorno

### Variables Requeridas para Google Sheets
```bash
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_NAME=your_sheet_name
GOOGLE_CREDENTIALS_FILE=path/to/credentials.json  # Para desarrollo local
```

### Variables del Modelo
```bash
MODEL_PROVIDER=huggingface  # o el proveedor de LLM preferido
```

## Casos de Uso

### 1. **Atención al Cliente**
- Respuestas personalizadas basadas en historial
- Información sobre Datapath y sus programas
- Escalamiento a registro cuando hay interés

### 2. **Generación de Leads**
- Captura automática de información de contacto
- Registro inmediato en Google Sheets
- Seguimiento de métricas de conversión

### 3. **Consultas de Información**
- Estadísticas de clientes registrados
- Información temporal para referencias
- Datos de la empresa y programas

## Flujo de Interacción Típico

1. **Usuario hace una pregunta**
   ```
   Usuario: "Quiero información sobre sus cursos"
   ```

2. **Agente consulta memoria**
   - Recupera información previa del usuario
   - Personaliza la respuesta

3. **Agente responde con información relevante**
   ```
   Agente: "Hola [nombre], basándome en tu interés previo en programación, 
           te recomiendo nuestros cursos de desarrollo web..."
   ```

4. **Si hay interés en registro**
   - Agente solicita información de contacto
   - Utiliza herramienta `registrar_cliente`
   - Confirma registro exitoso

5. **Actualización de memoria**
   - Almacena nueva información del usuario
   - Prepara contexto para futuras interacciones

## Ventajas del Sistema

### ✅ **Memoria Persistente**
- Continuidad entre conversaciones
- Personalización creciente
- Mejor experiencia del usuario

### ✅ **Integración Directa**
- Sin intermediarios para registro de datos
- Sincronización en tiempo real
- Datos centralizados

### ✅ **Escalabilidad**
- Arquitectura modular
- Fácil adición de nuevas herramientas
- Manejo concurrent de usuarios

### ✅ **Flexibilidad**
- Adaptable a diferentes proveedores de LLM
- Configuración mediante variables de entorno
- Deployment local o en cloud

## Estructura de Archivos

```
src/
├── agent/
│   ├── agent.py          # Lógica principal del agente
│   ├── tools.py          # Herramientas especializadas
│   └── prompts.py        # Prompts del sistema
├── service/
│   └── chatbot_service.py # Capa de servicio
└── llm/
    └── llm_factory.py    # Factory para modelos LLM
```

## Consideraciones Técnicas

### **Autenticación Google Sheets**
- **Local**: Archivo JSON de credenciales
- **Cloud**: Application Default Credentials
- **Scopes**: `spreadsheets` y `drive.file`

### **Gestión de Estado**
- **Thread ID**: Identificador único por usuario
- **Checkpointer**: Memoria dentro de la conversación
- **Store**: Memoria persistente entre sesiones

### **Manejo de Errores**
- Logging detallado de operaciones
- Fallbacks para credenciales
- Validación de datos de entrada

---

**Datapath** - Transformando vidas a través de la educación tecnológica desde 2020
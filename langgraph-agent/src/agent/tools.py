# Datos del Google Sheet
import os
from google.oauth2.service_account import Credentials
from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime

GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")

def registrar_cliente(email: str, nombres: str, apellidos: str, numero_documento: str, telefono: str):
    """
    Registra una nueva fila en Google Sheets

    Args:
        email: Correo electrónico del usuario
        nombres: Nombre del usuario
        apellidos: Apellido del usuario
        numero_documento: Número de documento
        telefono: Número de teléfono

    Returns:
        str: 'ok' si la operación fue exitosa
    """
    try:
        # Configuración de credenciales
        credentials_file = GOOGLE_CREDENTIALS_FILE
        spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
        sheet_name = GOOGLE_SHEETS_NAME

        # Scopes necesarios
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]

        # Autenticación
        if credentials_file and os.path.exists(credentials_file):
            # Local: usar archivo JSON
            credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            print("Usando archivo JSON local")
        else:
            # Cloud Run: usar Application Default Credentials
            credentials, _ = default(scopes=scopes)
            
        print("Usando Application Default Credentials")
        #credentials = Credentials.from_service_account_file(scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)

        fecha_registro = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Preparar los datos de la nueva fila
        new_row = [
            fecha_registro,
            email,
            nombres,
            apellidos,
            numero_documento,
            telefono
        ]

        # Rango donde agregar la nueva fila
        range_to_append = f"{sheet_name}!A:F"

        # Cuerpo de la petición
        body = {
            'values': [new_row]
        }

        # Encontrar la próxima fila vacía para evitar copiar formato
        # Primero obtenemos los datos existentes para saber cuántas filas hay
        existing_data = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:A"
        ).execute()

        # Calcular la próxima fila vacía
        existing_rows = len(existing_data.get('values', []))
        next_row = existing_rows + 1

        # Insertar en la fila específica (esto evita copiar formato)
        specific_range = f"{sheet_name}!A{next_row}:F{next_row}"

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=specific_range,
            valueInputOption='RAW',
            body=body
        ).execute()

        rows_added = result.get("updates", {}).get("updatedRows", 0)
        print(f'Usuario registrado correctamente')
        print(f'Fecha de registro: {fecha_registro}')

        return 'ok'

    except Exception as error:
        print(f'Error al registrar el usuario: {error}')
        raise error

def contar_registros():
    """
    Cuenta cuántos registros (filas) hay en el Google Sheet

    Returns:
        str: Mensaje con el número de registros
    """
    include_headers = False

    # Configuración de credenciales
    credentials_file = GOOGLE_CREDENTIALS_FILE
    spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
    sheet_name = GOOGLE_SHEETS_NAME
    
    try:
        # Scopes necesarios para Google Sheets
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]

        # Autenticación
        if credentials_file and os.path.exists(credentials_file):
            # Local: usar archivo JSON
            credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            print("Usando archivo JSON local")
        else:
            # Cloud Run: usar Application Default Credentials
            credentials, _ = default(scopes=scopes)

        # Crear el servicio de Google Sheets
        service = build('sheets', 'v4', credentials=credentials)

        # Obtener todas las filas con datos (columna A como referencia)
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEETS_SPREADSHEET_ID,
            range=f"{GOOGLE_SHEETS_NAME}!A:A"
        ).execute()

        # Contar filas con datos
        rows_with_data = result.get('values', [])
        total_rows = len(rows_with_data)

        if include_headers:
            registros = total_rows
            print(f'Total de filas (incluyendo headers): {registros}')
        else:
            # Restar 1 para excluir la fila de headers
            registros = max(0, total_rows - 1)
            print(f'Total de registros (sin headers): {registros}')
            print(f'Total de filas (con headers): {total_rows}')

        return f"Hay {registros} clientes registrados"

    except Exception as error:
        print(f'Error al contar registros: {error}')
        raise error

def get_current_date() -> dict:
    """
    Obtener la fecha actual en el formato YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}
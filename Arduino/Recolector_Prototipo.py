import serial
import csv
import time
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configura el puerto serial y la velocidad de baudios
ser = serial.Serial('COM11', 9600)  # Cambia 'COM9' al puerto correcto

# Función para obtener la fecha actual en el formato deseado
def get_current_date():
    return time.strftime('%d.%m.%Y')

# Función para obtener la hora actual en el formato deseado
def get_current_time():
    return time.strftime('%H:%M:%S')

# Función para obtener la fecha y hora actuales en un formato adecuado para el nombre del archivo
def get_filename_timestamp():
    return time.strftime('%Y%m%d_%H%M%S')

# Genera el nombre del archivo con la fecha y hora actuales
filename = f"data_{get_filename_timestamp()}.csv"

# Función para subir el archivo CSV a Google Drive
def upload_to_drive(file_name, folder_id):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    # Cargar las credenciales desde el archivo token.json
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/joseg/OneDrive/Escritorio/SENSORES/sensores_combinados/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Crear el servicio de Google Drive
    service = build('drive', 'v3', credentials=creds)
    
    # Buscar el archivo en Google Drive para actualizarlo o crear uno nuevo
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if items:
        # Si el archivo existe, usa su ID para actualizarlo
        file_id = items[0]['id']
        media = MediaFileUpload(file_name, mimetype='text/csv')
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Archivo actualizado con ID: {file_id}")
    else:
        # Si el archivo no existe, crea uno nuevo
        media = MediaFileUpload(file_name, mimetype='text/csv')
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]  # Especifica la carpeta de destino
        }
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Archivo creado con ID: {file.get('id')}")

try:
    # Abre un archivo CSV para escribir
    csv_file = open(filename, 'w', newline='')
    fieldnames = ['id', 'Date', 'Complete_hour', 'latitude', 'longitude', 'altitude', 'PM1', 'PM2.5', 'PM10', 'CO2', 'VOC', 'O3', 'CO', 'NO2', 'CH2O', 'temperature', 'humidity']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()  # Escribe los encabezados del CSV

    id_counter = 1  # Inicializa el contador de ID

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()  # Lee una línea de la conexión serial y la decodifica
            if line:  # Si hay datos válidos
                if "+CGPSINF: " in line:  # Si la línea contiene datos GPS
                    parts = line.split(',')
                    if len(parts) >= 4:
                        try:
                            latitude_raw = float(parts[1])
                            longitude_raw = float(parts[2])
                            altitude = float(parts[3])  # Captura la altitud
                            
                            # Convertir latitud y longitud desde formato grados y minutos a decimal
                            latitude_deg = int(latitude_raw / 100)
                            latitude_min = latitude_raw - (latitude_deg * 100)
                            latitude_decimal = latitude_deg + (latitude_min / 60)
                            
                            longitude_deg = int(longitude_raw / 100)
                            longitude_min = longitude_raw - (longitude_deg * 100)
                            longitude_decimal = longitude_deg + (longitude_min / 60)

                            # Ajusta el signo para la longitud en México (usualmente negativa)
                            longitude_decimal = -longitude_decimal
                            
                        except ValueError:
                            print("Error en la conversión de datos GPS")
                            continue
                        
                else:  # Procesa los datos del sensor Winsen
                    data = line.split(',')  # Separa los datos en una lista
                    if len(data) == 11:  # Asegúrate de que haya 11 campos (el número correcto de datos)
                        row = {
                            'id': id_counter,
                            'Date': get_current_date(),
                            'Complete_hour': get_current_time(),
                            'latitude': latitude_decimal if 'latitude_decimal' in locals() else '',
                            'longitude': longitude_decimal if 'longitude_decimal' in locals() else '',
                            'altitude': altitude if 'altitude' in locals() else '',
                            'CO2': data[0],
                            'VOC': data[1],
                            'temperature': data[2],
                            'humidity': data[3],
                            'CH2O': data[4],
                            'CO': data[5],
                            'O3': data[6],
                            'NO2': data[7],
                            'PM1': data[8],
                            'PM2.5': data[9],
                            'PM10': data[10]
                        }
                        print("Guardando datos:", row)  # Muestra los datos que está guardando
                        writer.writerow(row)  # Escribe la fila en el archivo CSV
                        id_counter += 1  # Incrementa el contador de ID
                        
                        # Asegúrate de que el archivo CSV se cierre correctamente antes de subirlo
                        csv_file.flush()  # Asegúrate de que todos los datos se escriban en el archivo
                        os.fsync(csv_file.fileno())  # Forzar el sistema a escribir los datos en disco
                        
                        # Subir el archivo CSV a Google Drive
                        folder_id = '1l3C7mBZt9XSjNgdINkg3w5JAAyJOYdW-'  # ID de tu carpeta de Google Drive
                        upload_to_drive(filename, folder_id)
                        
                        # Opcionalmente puedes esperar un breve período antes de leer la siguiente línea
                        time.sleep(2)  # Espera 2 segundos antes de la siguiente lectura
        except UnicodeDecodeError:
            print("Error al decodificar la línea recibida, se omite la línea.")
            continue

except KeyboardInterrupt:
    print("Programa terminado por el usuario.")

finally:
    ser.close()
    csv_file.close()
    print("Archivo CSV cerrado.")
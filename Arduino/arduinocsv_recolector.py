import serial
import csv
import time

# Abre la conexión serial, asegúrate de cambiar el puerto serie según tu configuración
ser = serial.Serial('COM5', 9600)  # Cambia 'COM6' al puerto serie correcto

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

# Abre un archivo CSV para escribir
with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['id', 'Date', 'Complete_hour', 'latitude', 'longitude', 'PM1', 'PM2.5', 'PM10', 'CO2', 'VOC', 'O3', 'CO', 'NO2', 'CH2O', 'temperature', 'humidity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()  # Escribe los encabezados del CSV

    id_counter = 1  # Inicializa el contador de ID

    while True:
        line = ser.readline().decode().strip()  # Lee una línea de la conexión serial y la decodifica
        if line:  # Si hay datos válidos
            data = line.split(',')  # Separa los datos en una lista
            if len(data) == 11:  # Asegúrate de que haya 11 campos (el número correcto de datos)
                row = {
                    'id': id_counter,
                    'Date': get_current_date(),
                    'Complete_hour': get_current_time(),
                    'latitude': 1,
                    'longitude': 1,
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

# Aplicación del Clima (Open-Meteo)

## Resumen del Proyecto
Esta aplicación permite a los usuarios consultar el clima actual de cualquier ciudad ingresando su nombre. Utiliza la API de Open-Meteo para obtener la temperatura, velocidad del viento y humedad. El sistema maneja errores de entrada y registra las respuestas en un archivo para su posterior análisis.

## Instrucciones de Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo/ruta/a/clima_app/app
   ```
2. Instala las dependencias necesarias ejecutando:
   ```bash
   pip install requests pytest
   ```

## Guía de Uso
1. Ejecuta la aplicación principal:
   ```bash
   python main.py
   ```
2. Ingresa el nombre de la ciudad cuando se solicite.
3. El resultado se mostrará en consola y se registrará en un archivo.

## Ejecución de Pruebas
Para ejecutar las pruebas unitarias y de integración:
```bash
pytest test_main.py -v
```
## Tecnologías Utilizadas
- Python 3
- requests
- pytest
- Open-Meteo API

## Ejemplo de Resultados
```
Ingrese el nombre de una ciudad: Madrid

Resultado en JSON:
{
  "nombre_ciudad": "Madrid",
  "temperatura_celsius": 20.5,
  "temperatura_fahrenheit": 68.9
}
```

## Funcionalidades
- Consulta de temperatura, humedad y velocidad del viento por ciudad.
- Conversión automática de Celsius a Fahrenheit.
- **Almacenamiento en caché de resultados durante 1 hora** para mejorar rendimiento.
- Manejo de errores para ciudades inválidas o problemas de red.
- Registro de resultados en archivo JSON.
- Pruebas unitarias y de integración con `pytest`.

## Mejoras Futuras
- Soporte para predicción meteorológica a varios días.
- Interfaz gráfica de usuario (GUI) o versión web.
- Selección automática de idioma según la ciudad o país.
- Soporte para múltiples proveedores de datos meteorológicos.
- Visualización de datos históricos y gráficos.
- Mejor manejo de ciudades duplicadas o ambiguas.
- Internacionalización y soporte para más idiomas.

---

**Desarrollado con Python y Open-Meteo API.**

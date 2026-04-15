import pytest
import json
import math
from unittest.mock import patch, MagicMock
from .main import obtener_coordenadas, obtener_temperatura, celsius_a_fahrenheit, main


class TestObtenerCoordenadasEdgeCases:
    """Pruebas de casos límite para obtener_coordenadas"""

    @patch('app.main.requests.get')
    def test_entrada_vacia(self, mock_get):
        """Caso límite: Entrada vacía"""
        result = obtener_coordenadas("")
        assert result is None

    @patch('app.main.requests.get')
    def test_entrada_solo_espacios(self, mock_get):
        """Caso límite: Solo espacios"""
        result = obtener_coordenadas("   ")
        # La API recibirá "   " como parámetro; verifica que se maneje
        mock_get.assert_called()

    @patch('app.main.requests.get')
    def test_nombre_ciudad_muy_largo(self, mock_get):
        """Caso límite: Nombre muy largo"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        nombre_largo = "A" * 1000
        result = obtener_coordenadas(nombre_largo)
        assert result is None

    @patch('app.main.requests.get')
    def test_caracteres_especiales(self, mock_get):
        """Caso límite: Caracteres especiales"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("@#$%^&*()")
        assert result is None

    @patch('app.main.requests.get')
    def test_caracteres_unicode_extremos(self, mock_get):
        """Caso límite: Caracteres Unicode (emojis)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("🌍🌎🌏")
        assert result is None

    @patch('app.main.requests.get')
    def test_numeros_como_entrada(self, mock_get):
        """Caso límite: Números como entrada"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("123")
        assert result is None

    @patch('app.main.requests.get')
    def test_respuesta_con_multiples_resultados(self, mock_get):
        """Caso límite: Múltiples resultados (debe retornar el primero)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"name": "Springfield", "latitude": 39.7817, "longitude": -89.6501},
                {"name": "Springfield", "latitude": 37.5244, "longitude": -122.2712}
            ]
        }
        mock_get.return_value = mock_response

        result = obtener_coordenadas("Springfield")
        # Debe retornar el primer resultado
        assert result == ("Springfield", 39.7817, -89.6501)

    @patch('app.main.requests.get')
    def test_respuesta_sin_clave_results(self, mock_get):
        """Caso límite: JSON sin clave 'results'"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Invalid"}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("Madrid")
        assert result is None

    @patch('app.main.requests.get')
    def test_respuesta_results_vacio(self, mock_get):
        """Caso límite: Results es una lista vacía"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("CiudadFantasma")
        assert result is None

    @patch('app.main.requests.get')
    def test_resultado_sin_latitud(self, mock_get):
        """Caso límite: Resultado sin latitud"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"name": "Madrid", "longitude": -3.7038}]
        }
        mock_get.return_value = mock_response

        with pytest.raises(KeyError):
            obtener_coordenadas("Madrid")

    @patch('app.main.requests.get')
    def test_json_inválido(self, mock_get):
        """Caso límite: JSON inválido"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        result = obtener_coordenadas("Madrid")
        assert result is None


class TestObtenerTemperaturaEdgeCases:
    """Pruebas de casos límite para obtener_temperatura"""

    @patch('app.main.requests.get')
    def test_coordenadas_polos(self, mock_get):
        """Caso límite: Coordenadas en los polos"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": -40.0}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(90, 0)  # Polo Norte
        assert result == -40.0

        result = obtener_temperatura(-90, 0)  # Polo Sur
        assert result == -40.0

    @patch('app.main.requests.get')
    def test_coordenadas_antimeridiano(self, mock_get):
        """Caso límite: Coordenadas en el antimeridiano (180/-180)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": 15.5}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(0, 180)
        assert result == 15.5

    @patch('app.main.requests.get')
    def test_coordenadas_cero(self, mock_get):
        """Caso límite: Coordenadas en el Golfo de Guinea (0, 0)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": 25.0}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(0, 0)
        assert result == 25.0

    @patch('app.main.requests.get')
    def test_temperatura_extrema_alta(self, mock_get):
        """Caso límite: Temperatura extremadamente alta (récord mundial)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": 58.8}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(36.4669, 116.8662)  # Valle de la Muerte
        assert result == 58.8

    @patch('app.main.requests.get')
    def test_temperatura_extrema_baja(self, mock_get):
        """Caso límite: Temperatura extremadamente baja (récord en Antártida)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": -89.2}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(-78.4680, 106.8362)  # Estación Vostok
        assert result == -89.2

    @patch('app.main.requests.get')
    def test_temperatura_zero(self, mock_get):
        """Caso límite: Temperatura en punto de congelación"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": 0.0}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(40.4168, -3.7038)
        assert result == 0.0

    @patch('app.main.requests.get')
    def test_current_weather_vacio(self, mock_get):
        """Caso límite: current_weather es un diccionario vacío"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(40.4168, -3.7038)
        assert result is None

    @patch('app.main.requests.get')
    def test_temperatura_null(self, mock_get):
        """Caso límite: Temperatura es null"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": None}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(40.4168, -3.7038)
        assert result is None


class TestCelsiusAFahrenheitEdgeCases:
    """Pruebas de casos límite para celsius_a_fahrenheit"""

    def test_temperatura_minima_fisica(self):
        """Caso límite: Cero absoluto (-273.15°C)"""
        resultado = celsius_a_fahrenheit(-273.15)
        assert resultado == -459.67

    def test_temperatura_muy_alta(self):
        """Caso límite: Temperatura muy alta"""
        resultado = celsius_a_fahrenheit(1000)
        assert resultado == 1832.0

    def test_temperatura_con_muchos_decimales(self):
        """Caso límite: Muchos decimales"""
        resultado = celsius_a_fahrenheit(25.123456789)
        assert isinstance(resultado, float)
        assert resultado > 77.0 and resultado < 78.0

    def test_temperatura_negativa_cercana_cero(self):
        """Caso límite: Temperatura negativa muy cercana a cero"""
        resultado = celsius_a_fahrenheit(-0.001)
        assert resultado < 32.0

    def test_temperatura_positiva_cercana_cero(self):
        """Caso límite: Temperatura positiva muy cercana a cero"""
        resultado = celsius_a_fahrenheit(0.001)
        assert resultado > 32.0


class TestIntegrationEdgeCases:
    """Pruebas de integración con casos límite"""

    @patch('builtins.input', return_value='Madrid')
    @patch('app.main.obtener_coordenadas', return_value=('Madrid', 40.4168, -3.7038))
    @patch('app.main.obtener_temperatura', return_value=0.0)
    @patch('builtins.print')
    def test_temperatura_cero_en_salida(self, mock_print, mock_temp, mock_coords, mock_input):
        """Caso límite: Temperatura 0°C en salida JSON"""
        main()

        expected_json = {
            "nombre_ciudad": "Madrid",
            "temperatura_celsius": 0.0,
            "temperatura_fahrenheit": 32.0
        }
        mock_print.assert_any_call("\nResultado en JSON:")
        mock_print.assert_any_call(json.dumps(expected_json, indent=2, ensure_ascii=False))

    @patch('builtins.input', return_value='Madrid')
    @patch('app.main.obtener_coordenadas', return_value=('Madrid', 40.4168, -3.7038))
    @patch('app.main.obtener_temperatura', return_value=-89.2)
    @patch('builtins.print')
    def test_temperatura_extrema_baja_en_salida(self, mock_print, mock_temp, mock_coords, mock_input):
        """Caso límite: Temperatura extrema baja en salida JSON"""
        main()

        # Verificar que se imprimió correctamente
        mock_print.assert_any_call("\nResultado en JSON:")

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_entrada_vacia_en_main(self, mock_print, mock_input):
        """Caso límite: Entrada vacía en main()"""
        main()
        # Debería manejar gracefully la entrada vacía

    @patch('builtins.input', return_value='   ')
    @patch('app.main.obtener_coordenadas', return_value=None)
    @patch('builtins.print')
    def test_entrada_solo_espacios_en_main(self, mock_print, mock_coords, mock_input):
        """Caso límite: Solo espacios en entrada"""
        main()
        # Debería manejar el caso


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

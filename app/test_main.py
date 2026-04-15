import pytest
import json
from unittest.mock import patch, MagicMock
from .main import obtener_coordenadas, obtener_temperatura, celsius_a_fahrenheit, main


class TestObtenerCoordenadas:
    """Pruebas para la función obtener_coordenadas"""

    @patch('app.main.requests.get')
    def test_ciudad_valida(self, mock_get):
        """Caso exitoso: Ciudad válida"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"name": "Madrid", "latitude": 40.4168, "longitude": -3.7038}]
        }
        mock_get.return_value = mock_response

        result = obtener_coordenadas("Madrid")
        assert result == ("Madrid", 40.4168, -3.7038)

    @patch('app.main.requests.get')
    def test_ciudad_con_acentos(self, mock_get):
        """Caso exitoso: Ciudad con acentos"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"name": "México", "latitude": 19.4326, "longitude": -99.1332}]
        }
        mock_get.return_value = mock_response

        result = obtener_coordenadas("México")
        assert result == ("México", 19.4326, -99.1332)

    @patch('app.main.requests.get')
    def test_ciudad_no_encontrada(self, mock_get):
        """Caso de error: Ciudad no encontrada"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No results"}
        mock_get.return_value = mock_response

        result = obtener_coordenadas("CiudadInexistente")
        assert result is None

    @patch('app.main.requests.get')
    def test_error_red_timeout(self, mock_get):
        """Caso de error: Timeout en la petición"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Timeout")

        result = obtener_coordenadas("Madrid")
        assert result is None

    @patch('app.main.requests.get')
    def test_respuesta_http_no_exitosa(self, mock_get):
        """Caso de error: Respuesta HTTP 404"""
        from requests.exceptions import HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
        mock_get.return_value = mock_response

        result = obtener_coordenadas("Madrid")
        assert result is None


class TestObtenerTemperatura:
    """Pruebas para la función obtener_temperatura"""

    @patch('app.main.requests.get')
    def test_coordenadas_validas(self, mock_get):
        """Caso exitoso: Coordenadas válidas"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_weather": {"temperature": 20.5}}
        mock_get.return_value = mock_response

        result = obtener_temperatura(40.4168, -3.7038)
        assert result == 20.5

    @patch('app.main.requests.get')
    def test_error_red_conexion(self, mock_get):
        """Caso de error: Error de conexión"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")

        result = obtener_temperatura(40.4168, -3.7038)
        assert result is None

    @patch('app.main.requests.get')
    def test_respuesta_sin_current_weather(self, mock_get):
        """Caso de error: JSON sin current_weather"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No weather data"}
        mock_get.return_value = mock_response

        result = obtener_temperatura(40.4168, -3.7038)
        assert result is None


class TestCelsiusAFahrenheit:
    """Pruebas para la función celsius_a_fahrenheit"""

    def test_temperatura_positiva(self):
        """Caso exitoso: Temperatura positiva"""
        result = celsius_a_fahrenheit(20.5)
        assert result == 68.9

    def test_temperatura_negativa(self):
        """Caso exitoso: Temperatura negativa"""
        result = celsius_a_fahrenheit(-10.0)
        assert result == 14.0

    def test_temperatura_cero(self):
        """Caso exitoso: Temperatura cero"""
        result = celsius_a_fahrenheit(0.0)
        assert result == 32.0

    def test_temperatura_con_decimales(self):
        """Caso edge: Valor con decimales"""
        result = celsius_a_fahrenheit(25.678)
        assert round(result, 2) == 78.22


class TestMain:
    """Pruebas para la función main (integración)"""

    @patch('builtins.input', return_value='Madrid')
    @patch('app.main.obtener_clima_con_cache', return_value={
        "nombre_ciudad": "Madrid",
        "temperatura_celsius": 20.5,
        "temperatura_fahrenheit": 68.9
    })
    @patch('builtins.print')
    def test_flujo_completo_exitoso(self, mock_print, mock_cache, mock_input):
        """Caso exitoso: Flujo completo válido"""
        main()

        # Verificar que se imprimió el JSON correcto
        expected_json = {
            "nombre_ciudad": "Madrid",
            "temperatura_celsius": 20.5,
            "temperatura_fahrenheit": 68.9
        }
        mock_print.assert_any_call("\nResultado en JSON:")
        mock_print.assert_any_call(json.dumps(expected_json, indent=2, ensure_ascii=False))

    @patch('builtins.input', return_value='CiudadInexistente')
    @patch('app.main.obtener_clima_con_cache', return_value=None)
    @patch('builtins.print')
    def test_ciudad_no_encontrada(self, mock_print, mock_cache, mock_input):
        """Caso de error: Ciudad no encontrada"""
        main()

        # Verificar que no se imprimió el JSON
        assert not any("Resultado en JSON" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.input', return_value='Madrid')
    @patch('app.main.obtener_clima_con_cache', return_value=None)
    @patch('builtins.print')
    def test_error_en_temperatura(self, mock_print, mock_cache, mock_input):
        """Caso de error: Error en obtención de temperatura"""
        main()

        # Verificar que no se imprimió el JSON
        assert not any("Resultado en JSON" in str(call) for call in mock_print.call_args_list)


if __name__ == "__main__":
    pytest.main([__file__])

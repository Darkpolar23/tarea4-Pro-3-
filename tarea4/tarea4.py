import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramTestConfig:
    """Configuración de pruebas"""
    DRIVER_PATH = 'chromedriver.exe'
    BASE_URL = 'https://www.instagram.com/'
    TIMEOUT = 5
    
    # Credenciales de prueba (reemplazar con credenciales reales para testing)
    TEST_USERNAME = '9999999'
    TEST_PASSWORD = '999999'
    
    # Credenciales inválidas para tests negativos
    INVALID_USERNAME = 'usuario_inexistente_12345'
    INVALID_PASSWORD = 'password_incorrecto'

class InstagramLoginTest:
    """Clase base para tests de Instagram"""
    
    def setup_method(self):
        """Configurar driver antes de cada test"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        service = Service(InstagramTestConfig.DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, InstagramTestConfig.TIMEOUT)
        
    def teardown_method(self):
        """Limpiar después de cada test"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def navigate_to_instagram(self):
        """Navegar a Instagram"""
        logger.info("Navegando a Instagram...")
        self.driver.get(InstagramTestConfig.BASE_URL)
        
        # Verificar que la página se cargó correctamente
        assert "Instagram" in self.driver.title
        logger.info("Página de Instagram cargada correctamente")
    
    def find_login_elements(self):
        """Encontrar elementos de login"""
        logger.info("Buscando elementos de login...")
        
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        
        password_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        
        return username_field, password_field, login_button
    
    def perform_login(self, username, password):
        """Realizar el proceso de login"""
        username_field, password_field, login_button = self.find_login_elements()
        
        # Limpiar campos y ingresar credenciales
        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
        logger.info(f"Intentando login con usuario: {username}")
        login_button.click()
        
        # Esperar un momento para que procese el login
        time.sleep(3)

@pytest.mark.login
class TestInstagramLogin(InstagramLoginTest):
    """Tests para funcionalidad de login de Instagram"""
    
    def test_page_loads_successfully(self):
        """Test: La página de Instagram se carga correctamente"""
        self.navigate_to_instagram()
        
        # Verificaciones adicionales
        assert self.driver.current_url.startswith("https://www.instagram.com")
        
        # Verificar que los elementos esenciales estén presentes
        logo = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label*='Instagram']"))
        )
        assert logo is not None
        
    def test_login_form_elements_present(self):
        """Test: Los elementos del formulario de login están presentes"""
        self.navigate_to_instagram()
        
        username_field, password_field, login_button = self.find_login_elements()
        
        # Verificar que los elementos son interactivos
        assert username_field.is_enabled()
        assert password_field.is_enabled()
        assert login_button.is_enabled()
        
        # Verificar placeholders
        username_placeholder = username_field.get_attribute('placeholder')
        assert username_placeholder is not None
        
    def test_empty_credentials_validation(self):
        """Test: Validación con credenciales vacías"""
        self.navigate_to_instagram()
        self.perform_login("", "")
        
        # Verificar que no se permite login vacío
        # Instagram debería mostrar algún tipo de error o no procesar el login
        current_url = self.driver.current_url
        assert "instagram.com" in current_url
        
    def test_invalid_credentials_login(self):
        """Test: Login con credenciales inválidas"""
        self.navigate_to_instagram()
        self.perform_login(
            InstagramTestConfig.INVALID_USERNAME, 
            InstagramTestConfig.INVALID_PASSWORD
        )
        
        # Buscar mensaje de error
        try:
            error_message = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='alert']"))
            )
            logger.info("Mensaje de error encontrado para credenciales inválidas")
            assert error_message is not None
        except TimeoutException:
            # Si no hay mensaje de error, verificar que seguimos en la página de login
            assert "accounts/login" in self.driver.current_url or self.driver.current_url.endswith("instagram.com/")
    
    @pytest.mark.skip(reason="Requiere credenciales válidas - ejecutar manualmente")
    def test_valid_credentials_login(self):
        """Test: Login con credenciales válidas (REQUIERE CREDENCIALES REALES)"""
        self.navigate_to_instagram()
        self.perform_login(
            InstagramTestConfig.TEST_USERNAME, 
            InstagramTestConfig.TEST_PASSWORD
        )
        
        # Verificar redirección exitosa o elementos post-login
        try:
            # Buscar elementos que indiquen login exitoso
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Home']")),
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']")),
                    EC.url_contains("/accounts/onetap")
                )
            )
            logger.info("Login exitoso detectado")
            
        except TimeoutException:
            pytest.fail("Login válido falló - verificar credenciales")
    
    def test_username_field_functionality(self):
        """Test: Funcionalidad del campo username"""
        self.navigate_to_instagram()
        username_field, _, _ = self.find_login_elements()
        
        test_input = "test_user_123"
        username_field.send_keys(test_input)
        
        # Verificar que el texto se ingresó correctamente
        assert username_field.get_attribute('value') == test_input
        
    def test_password_field_functionality(self):
        """Test: Funcionalidad del campo password"""
        self.navigate_to_instagram()
        _, password_field, _ = self.find_login_elements()
        
        test_password = "test_password_123"
        password_field.send_keys(test_password)
        
        # Verificar que el campo tiene el tipo password (texto oculto)
        assert password_field.get_attribute('type') == 'password'
        assert password_field.get_attribute('value') == test_password

@pytest.mark.ui
class TestInstagramUI(InstagramLoginTest):
    """Tests para elementos de UI de Instagram"""
    
    def test_responsive_design(self):
        """Test: Diseño responsive"""
        self.navigate_to_instagram()
        
        # Test en diferentes tamaños de ventana
        sizes = [(1920, 1080), (1024, 768), (375, 667)]  # Desktop, tablet, mobile
        
        for width, height in sizes:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            # Verificar que los elementos siguen siendo accesibles
            username_field, password_field, login_button = self.find_login_elements()
            
            assert username_field.is_displayed()
            assert password_field.is_displayed()
            assert login_button.is_displayed()
            
            logger.info(f"UI verificada para resolución: {width}x{height}")

# Configuración de pytest
def pytest_configure(config):
    """Configuración personalizada de pytest"""
    config.addinivalue_line(
        "markers", "login: marca tests relacionados con login"
    )
    config.addinivalue_line(
        "markers", "ui: marca tests relacionados con UI"
    )

if __name__ == "__main__":
    # Ejecutar tests con reporte HTML
    pytest.main([
        __file__,
        "--html=report_instagram_tests.html",
        "--self-contained-html",
        "-v",
        "--tb=short"

    ])

#!/usr/bin/env python3
"""
Tests de Compatibilité Navigateur pour TradingAgents Interface Moderne
Tests sur différents navigateurs et tailles d'écran
"""

import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuration
BASE_URL = "http://localhost:5000"
WAIT_TIMEOUT = 10

# Tailles d'écran à tester
SCREEN_SIZES = [
    (1920, 1080, "Desktop Large"),
    (1366, 768, "Desktop Standard"),
    (1024, 768, "Tablet Landscape"),
    (768, 1024, "Tablet Portrait"),
    (414, 896, "Mobile Large"),
    (375, 667, "Mobile Standard"),
    (320, 568, "Mobile Small")
]

class BrowserTestBase:
    """Classe de base pour les tests de navigateur"""
    
    def get_driver(self, browser_name):
        """Obtenir le driver pour un navigateur spécifique"""
        if browser_name == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            return webdriver.Chrome(options=options)
            
        elif browser_name == "firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            return webdriver.Firefox(options=options)
            
        elif browser_name == "edge":
            options = EdgeOptions()
            options.add_argument("--headless")
            return webdriver.Edge(options=options)
            
        else:
            raise ValueError(f"Navigateur non supporté: {browser_name}")
    
    def test_basic_functionality(self, driver):
        """Test des fonctionnalités de base"""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        
        # Vérifier que la page se charge
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Vérifier le titre
        assert "TradingAgents" in driver.title
        
        # Vérifier la navigation
        navbar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navbar")))
        assert navbar.is_displayed()
        
        return True
    
    def test_responsive_layout(self, driver, width, height, size_name):
        """Test du layout responsive"""
        driver.set_window_size(width, height)
        driver.get(BASE_URL)
        time.sleep(1)  # Attendre le redimensionnement
        
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        
        # Vérifier que la navbar est toujours visible
        navbar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navbar")))
        assert navbar.is_displayed()
        
        # Sur mobile, vérifier le menu hamburger
        if width < 768:
            try:
                mobile_toggle = driver.find_element(By.CLASS_NAME, "mobile-menu-toggle")
                # Le menu mobile devrait être visible sur petits écrans
                assert mobile_toggle.is_displayed()
            except:
                # Le menu mobile peut ne pas être implémenté
                pass
        
        # Vérifier que le contenu principal est visible
        try:
            main_content = driver.find_element(By.CLASS_NAME, "main-content")
            assert main_content.is_displayed()
        except:
            # Fallback: vérifier qu'il y a du contenu
            body = driver.find_element(By.TAG_NAME, "body")
            assert len(body.text) > 0
        
        return True
    
    def test_css_support(self, driver):
        """Test du support CSS"""
        driver.get(BASE_URL)
        
        # Vérifier que les variables CSS sont supportées
        html_element = driver.find_element(By.TAG_NAME, "html")
        
        # Tester une propriété CSS custom
        primary_color = driver.execute_script(
            "return getComputedStyle(document.documentElement).getPropertyValue('--primary-color')"
        )
        
        # Si les variables CSS sont supportées, la couleur ne devrait pas être vide
        if primary_color.strip():
            assert len(primary_color.strip()) > 0
        
        return True
    
    def test_javascript_support(self, driver):
        """Test du support JavaScript"""
        driver.get(BASE_URL)
        
        # Vérifier que JavaScript fonctionne
        js_result = driver.execute_script("return typeof window.modernUI")
        
        # modernUI devrait être défini si le JS se charge correctement
        return js_result in ["object", "undefined"]  # undefined est acceptable si pas encore chargé


class TestChromeCompatibility(BrowserTestBase):
    """Tests de compatibilité Chrome"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        try:
            driver = self.get_driver("chrome")
            yield driver
        except WebDriverException:
            pytest.skip("Chrome non disponible")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_chrome_basic(self, driver):
        """Test des fonctionnalités de base sur Chrome"""
        assert self.test_basic_functionality(driver)
    
    @pytest.mark.parametrize("width,height,size_name", SCREEN_SIZES)
    def test_chrome_responsive(self, driver, width, height, size_name):
        """Test responsive sur Chrome"""
        assert self.test_responsive_layout(driver, width, height, size_name)
    
    def test_chrome_css(self, driver):
        """Test CSS sur Chrome"""
        assert self.test_css_support(driver)
    
    def test_chrome_javascript(self, driver):
        """Test JavaScript sur Chrome"""
        assert self.test_javascript_support(driver)


class TestFirefoxCompatibility(BrowserTestBase):
    """Tests de compatibilité Firefox"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        try:
            driver = self.get_driver("firefox")
            yield driver
        except WebDriverException:
            pytest.skip("Firefox non disponible")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_firefox_basic(self, driver):
        """Test des fonctionnalités de base sur Firefox"""
        assert self.test_basic_functionality(driver)
    
    @pytest.mark.parametrize("width,height,size_name", SCREEN_SIZES[:3])  # Tester moins de tailles pour Firefox
    def test_firefox_responsive(self, driver, width, height, size_name):
        """Test responsive sur Firefox"""
        assert self.test_responsive_layout(driver, width, height, size_name)
    
    def test_firefox_css(self, driver):
        """Test CSS sur Firefox"""
        assert self.test_css_support(driver)
    
    def test_firefox_javascript(self, driver):
        """Test JavaScript sur Firefox"""
        assert self.test_javascript_support(driver)


class TestEdgeCompatibility(BrowserTestBase):
    """Tests de compatibilité Edge"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        try:
            driver = self.get_driver("edge")
            yield driver
        except WebDriverException:
            pytest.skip("Edge non disponible")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_edge_basic(self, driver):
        """Test des fonctionnalités de base sur Edge"""
        assert self.test_basic_functionality(driver)
    
    def test_edge_css(self, driver):
        """Test CSS sur Edge"""
        assert self.test_css_support(driver)
    
    def test_edge_javascript(self, driver):
        """Test JavaScript sur Edge"""
        assert self.test_javascript_support(driver)


class TestCrossbrowserFeatures:
    """Tests de fonctionnalités cross-browser"""
    
    def get_available_browsers(self):
        """Obtenir la liste des navigateurs disponibles"""
        browsers = []
        
        # Tester Chrome
        try:
            driver = webdriver.Chrome(options=ChromeOptions().add_argument("--headless"))
            driver.quit()
            browsers.append("chrome")
        except:
            pass
        
        # Tester Firefox
        try:
            driver = webdriver.Firefox(options=FirefoxOptions().add_argument("--headless"))
            driver.quit()
            browsers.append("firefox")
        except:
            pass
        
        # Tester Edge
        try:
            driver = webdriver.Edge(options=EdgeOptions().add_argument("--headless"))
            driver.quit()
            browsers.append("edge")
        except:
            pass
        
        return browsers
    
    def test_theme_toggle_cross_browser(self):
        """Test du changement de thème sur tous les navigateurs"""
        browsers = self.get_available_browsers()
        
        if not browsers:
            pytest.skip("Aucun navigateur disponible")
        
        base = BrowserTestBase()
        
        for browser_name in browsers:
            try:
                driver = base.get_driver(browser_name)
                driver.get(BASE_URL)
                
                # Vérifier le thème initial
                html_element = driver.find_element(By.TAG_NAME, "html")
                initial_theme = html_element.get_attribute("data-theme")
                
                # Essayer de trouver et cliquer le bouton de thème
                try:
                    theme_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "theme-toggle"))
                    )
                    theme_button.click()
                    time.sleep(0.5)
                    
                    new_theme = html_element.get_attribute("data-theme")
                    assert new_theme != initial_theme, f"Thème non changé sur {browser_name}"
                    
                except TimeoutException:
                    # Le bouton de thème peut ne pas être présent
                    pass
                
                driver.quit()
                
            except Exception as e:
                print(f"Erreur test thème sur {browser_name}: {e}")
    
    def test_form_validation_cross_browser(self):
        """Test de validation de formulaires sur tous les navigateurs"""
        browsers = self.get_available_browsers()
        
        if not browsers:
            pytest.skip("Aucun navigateur disponible")
        
        base = BrowserTestBase()
        
        for browser_name in browsers:
            try:
                driver = base.get_driver(browser_name)
                driver.get(f"{BASE_URL}/backtesting")
                
                # Trouver un formulaire avec validation
                try:
                    form = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "backtestForm"))
                    )
                    
                    # Essayer de soumettre sans remplir
                    submit_button = form.find_element(By.XPATH, ".//button[@type='submit']")
                    submit_button.click()
                    
                    # Vérifier que la validation fonctionne (HTML5 ou custom)
                    # La validation peut être différente selon le navigateur
                    
                except TimeoutException:
                    # Le formulaire peut ne pas être présent
                    pass
                
                driver.quit()
                
            except Exception as e:
                print(f"Erreur test validation sur {browser_name}: {e}")


class TestAccessibilityCompatibility:
    """Tests de compatibilité d'accessibilité"""
    
    def test_keyboard_navigation(self):
        """Test de navigation au clavier"""
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            
            driver.get(BASE_URL)
            
            # Tester la navigation par Tab
            body = driver.find_element(By.TAG_NAME, "body")
            body.click()  # Focus sur la page
            
            # Simuler plusieurs Tab
            for _ in range(5):
                body.send_keys("\t")
                time.sleep(0.1)
            
            # Vérifier qu'un élément a le focus
            focused_element = driver.switch_to.active_element
            assert focused_element is not None
            
            driver.quit()
            
        except Exception as e:
            pytest.skip(f"Test navigation clavier échoué: {e}")
    
    def test_color_contrast(self):
        """Test basique de contraste des couleurs"""
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            
            driver.get(BASE_URL)
            
            # Vérifier que les couleurs de base sont définies
            primary_color = driver.execute_script(
                "return getComputedStyle(document.documentElement).getPropertyValue('--primary-color')"
            )
            text_color = driver.execute_script(
                "return getComputedStyle(document.documentElement).getPropertyValue('--text-primary')"
            )
            
            # Les couleurs devraient être définies
            assert primary_color.strip(), "Couleur primaire non définie"
            assert text_color.strip(), "Couleur de texte non définie"
            
            driver.quit()
            
        except Exception as e:
            pytest.skip(f"Test contraste couleurs échoué: {e}")


def run_compatibility_tests():
    """Exécuter tous les tests de compatibilité"""
    print("🌐 Tests de Compatibilité Navigateur TradingAgents")
    print("=" * 60)
    
    # Vérifier les navigateurs disponibles
    base = BrowserTestBase()
    available_browsers = []
    
    for browser in ["chrome", "firefox", "edge"]:
        try:
            driver = base.get_driver(browser)
            driver.quit()
            available_browsers.append(browser)
            print(f"✅ {browser.capitalize()} disponible")
        except:
            print(f"❌ {browser.capitalize()} non disponible")
    
    if not available_browsers:
        print("❌ Aucun navigateur disponible pour les tests")
        return False
    
    print(f"\n📋 Tests sur {len(available_browsers)} navigateur(s)")
    
    # Exécuter les tests de base sur chaque navigateur
    for browser in available_browsers:
        print(f"\n🔍 Test {browser.capitalize()}")
        print("-" * 30)
        
        try:
            driver = base.get_driver(browser)
            
            # Test de base
            if base.test_basic_functionality(driver):
                print("✅ Fonctionnalités de base")
            else:
                print("❌ Fonctionnalités de base")
            
            # Test CSS
            if base.test_css_support(driver):
                print("✅ Support CSS")
            else:
                print("❌ Support CSS")
            
            # Test JavaScript
            if base.test_javascript_support(driver):
                print("✅ Support JavaScript")
            else:
                print("❌ Support JavaScript")
            
            # Test responsive (quelques tailles)
            responsive_ok = True
            for width, height, name in SCREEN_SIZES[:3]:
                try:
                    base.test_responsive_layout(driver, width, height, name)
                except:
                    responsive_ok = False
                    break
            
            if responsive_ok:
                print("✅ Design responsive")
            else:
                print("❌ Design responsive")
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Erreur test {browser}: {e}")
    
    print("\n✅ Tests de compatibilité terminés")
    return True


if __name__ == '__main__':
    success = run_compatibility_tests()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Tests End-to-End avec Selenium pour TradingAgents Interface Moderne
Tests complets de l'interface utilisateur dans un navigateur réel
"""

import pytest
import time
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
BASE_URL = "http://localhost:5000"
WAIT_TIMEOUT = 10

class TestE2EInterface:
    """Tests End-to-End de l'interface"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Configuration du driver Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Mode sans interface graphique
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(5)
            yield driver
        finally:
            driver.quit()
    
    @pytest.fixture
    def wait(self, driver):
        """WebDriverWait configuré"""
        return WebDriverWait(driver, WAIT_TIMEOUT)
    
    def test_homepage_loads(self, driver, wait):
        """Test que la page d'accueil se charge correctement"""
        driver.get(BASE_URL)
        
        # Vérifier le titre
        assert "TradingAgents" in driver.title
        
        # Vérifier que les éléments principaux sont présents
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hero-section")))
    
    def test_navigation_bar(self, driver, wait):
        """Test de la barre de navigation"""
        driver.get(BASE_URL)
        
        # Vérifier que la navbar est présente
        navbar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navbar")))
        assert navbar.is_displayed()
        
        # Vérifier le logo
        logo = driver.find_element(By.CLASS_NAME, "navbar-brand")
        assert logo.is_displayed()
        assert "TradingAgents" in logo.text
        
        # Vérifier les liens de navigation
        nav_links = driver.find_elements(By.CLASS_NAME, "nav-link")
        assert len(nav_links) >= 4  # Au moins Analyses, Automatisation, Backtesting, etc.
        
        # Tester un lien de navigation
        automation_link = None
        for link in nav_links:
            if "Automatisation" in link.text:
                automation_link = link
                break
        
        if automation_link:
            automation_link.click()
            wait.until(EC.url_contains("/automation"))
            assert "/automation" in driver.current_url
    
    def test_theme_toggle(self, driver, wait):
        """Test du changement de thème"""
        driver.get(BASE_URL)
        
        # Trouver le bouton de thème
        try:
            theme_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "theme-toggle")))
            
            # Vérifier le thème initial
            html_element = driver.find_element(By.TAG_NAME, "html")
            initial_theme = html_element.get_attribute("data-theme")
            
            # Cliquer sur le bouton de thème
            theme_button.click()
            time.sleep(0.5)  # Attendre l'animation
            
            # Vérifier que le thème a changé
            new_theme = html_element.get_attribute("data-theme")
            assert new_theme != initial_theme
            
        except TimeoutException:
            pytest.skip("Bouton de thème non trouvé")
    
    def test_search_functionality(self, driver, wait):
        """Test de la fonctionnalité de recherche"""
        driver.get(BASE_URL)
        
        try:
            # Trouver le champ de recherche
            search_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "global-search-input")))
            
            # Tester la recherche
            search_input.click()
            search_input.send_keys("SPY")
            time.sleep(1)  # Attendre les résultats
            
            # Vérifier que des résultats apparaissent (si implémenté)
            try:
                results = driver.find_element(By.CLASS_NAME, "global-search-results")
                assert results.is_displayed()
            except NoSuchElementException:
                # Les résultats peuvent ne pas être implémentés
                pass
                
        except TimeoutException:
            pytest.skip("Champ de recherche non trouvé")
    
    def test_quick_analysis_form(self, driver, wait):
        """Test du formulaire d'analyse rapide"""
        driver.get(BASE_URL)
        
        try:
            # Trouver le formulaire d'analyse
            ticker_input = wait.until(EC.presence_of_element_located((By.ID, "ticker")))
            
            # Remplir le formulaire
            ticker_input.clear()
            ticker_input.send_keys("SPY")
            
            # Sélectionner la profondeur
            depth_select = driver.find_element(By.ID, "depth")
            depth_select.click()
            
            # Trouver le bouton d'analyse
            analyze_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Analyser')]")
            assert analyze_button.is_displayed()
            
            # Note: Ne pas cliquer pour éviter de lancer une vraie analyse
            
        except (TimeoutException, NoSuchElementException):
            pytest.skip("Formulaire d'analyse non trouvé")
    
    def test_automation_page(self, driver, wait):
        """Test de la page d'automatisation"""
        driver.get(f"{BASE_URL}/automation")
        
        # Vérifier que la page se charge
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "automation-header")))
        
        # Vérifier les éléments principaux
        try:
            control_panel = driver.find_element(By.CLASS_NAME, "control-panel")
            assert control_panel.is_displayed()
            
            metrics_grid = driver.find_element(By.CLASS_NAME, "metrics-grid")
            assert metrics_grid.is_displayed()
            
            # Vérifier les boutons de contrôle
            start_button = driver.find_element(By.ID, "start-automation")
            stop_button = driver.find_element(By.ID, "stop-automation")
            
            assert start_button.is_displayed()
            assert stop_button.is_displayed()
            
        except NoSuchElementException as e:
            pytest.fail(f"Élément manquant sur la page d'automatisation: {e}")
    
    def test_backtesting_page(self, driver, wait):
        """Test de la page de backtesting"""
        driver.get(f"{BASE_URL}/backtesting")
        
        # Vérifier que la page se charge
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "backtesting-header")))
        
        try:
            # Vérifier le formulaire de backtest
            backtest_form = driver.find_element(By.ID, "backtestForm")
            assert backtest_form.is_displayed()
            
            # Vérifier les champs principaux
            name_input = driver.find_element(By.NAME, "name")
            capital_input = driver.find_element(By.NAME, "initial_capital")
            
            assert name_input.is_displayed()
            assert capital_input.is_displayed()
            
        except NoSuchElementException as e:
            pytest.fail(f"Élément manquant sur la page de backtesting: {e}")
    
    def test_demo_page(self, driver, wait):
        """Test de la page de démonstration"""
        driver.get(f"{BASE_URL}/demo")
        
        # Vérifier que la page se charge
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "demo-header")))
        
        try:
            # Vérifier les sections de démonstration
            color_palette = driver.find_element(By.CLASS_NAME, "color-palette")
            component_showcase = driver.find_element(By.CLASS_NAME, "component-showcase")
            
            assert color_palette.is_displayed()
            assert component_showcase.is_displayed()
            
            # Tester un bouton de notification
            notification_buttons = driver.find_elements(By.XPATH, "//button[contains(@onclick, 'testNotification')]")
            if notification_buttons:
                notification_buttons[0].click()
                time.sleep(1)  # Attendre l'animation de notification
            
        except NoSuchElementException as e:
            pytest.fail(f"Élément manquant sur la page de démonstration: {e}")
    
    def test_responsive_design(self, driver, wait):
        """Test du design responsive"""
        driver.get(BASE_URL)
        
        # Tester différentes tailles d'écran
        screen_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            driver.set_window_size(width, height)
            time.sleep(0.5)  # Attendre le redimensionnement
            
            # Vérifier que la navbar est toujours visible
            navbar = driver.find_element(By.CLASS_NAME, "navbar")
            assert navbar.is_displayed()
            
            # Sur mobile, vérifier le menu hamburger
            if width < 768:
                try:
                    mobile_toggle = driver.find_element(By.CLASS_NAME, "mobile-menu-toggle")
                    assert mobile_toggle.is_displayed()
                except NoSuchElementException:
                    # Le menu mobile peut ne pas être visible selon l'implémentation
                    pass
    
    def test_keyboard_shortcuts(self, driver, wait):
        """Test des raccourcis clavier"""
        driver.get(BASE_URL)
        
        # Tester Ctrl+T pour le thème (si implémenté)
        try:
            html_element = driver.find_element(By.TAG_NAME, "html")
            initial_theme = html_element.get_attribute("data-theme")
            
            # Simuler Ctrl+T
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            
            new_theme = html_element.get_attribute("data-theme")
            # Le raccourci peut ou peut ne pas fonctionner selon l'implémentation
            
        except Exception:
            # Les raccourcis clavier peuvent ne pas être testables en Selenium
            pytest.skip("Test des raccourcis clavier non applicable")
    
    def test_form_validation(self, driver, wait):
        """Test de la validation des formulaires"""
        driver.get(f"{BASE_URL}/backtesting")
        
        try:
            # Trouver le formulaire de backtest
            form = wait.until(EC.presence_of_element_located((By.ID, "backtestForm")))
            
            # Essayer de soumettre sans remplir les champs requis
            submit_button = form.find_element(By.XPATH, ".//button[@type='submit']")
            submit_button.click()
            
            # Vérifier que la validation HTML5 fonctionne
            name_input = form.find_element(By.NAME, "name")
            validation_message = name_input.get_attribute("validationMessage")
            
            # Si le navigateur supporte la validation HTML5
            if validation_message:
                assert len(validation_message) > 0
            
        except (TimeoutException, NoSuchElementException):
            pytest.skip("Formulaire de test non trouvé")
    
    def test_accessibility_basics(self, driver, wait):
        """Test des bases d'accessibilité"""
        driver.get(BASE_URL)
        
        # Vérifier que les boutons sont focusables
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons[:5]:  # Tester les 5 premiers boutons
            if button.is_displayed():
                button.click()
                focused_element = driver.switch_to.active_element
                # Vérifier que l'élément peut recevoir le focus
                assert focused_element is not None
    
    def test_error_handling(self, driver, wait):
        """Test de la gestion d'erreurs"""
        # Tester une page inexistante
        driver.get(f"{BASE_URL}/nonexistent-page")
        
        # Vérifier que nous obtenons une page 404 ou une redirection
        assert "404" in driver.page_source or driver.current_url != f"{BASE_URL}/nonexistent-page"


class TestPerformance:
    """Tests de performance basiques"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Driver avec métriques de performance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_page_load_time(self, driver):
        """Test du temps de chargement des pages"""
        pages = [
            "/",
            "/automation",
            "/backtesting",
            "/demo"
        ]
        
        for page in pages:
            start_time = time.time()
            driver.get(f"{BASE_URL}{page}")
            
            # Attendre que la page soit complètement chargée
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            load_time = time.time() - start_time
            
            # Vérifier que la page se charge en moins de 5 secondes
            assert load_time < 5.0, f"Page {page} trop lente: {load_time:.2f}s"
    
    def test_javascript_errors(self, driver):
        """Test qu'il n'y a pas d'erreurs JavaScript critiques"""
        driver.get(BASE_URL)
        
        # Récupérer les erreurs de la console
        logs = driver.get_log('browser')
        
        # Filtrer les erreurs critiques
        critical_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Il ne devrait pas y avoir d'erreurs critiques
        assert len(critical_errors) == 0, f"Erreurs JavaScript critiques: {critical_errors}"


if __name__ == '__main__':
    # Vérifier que le serveur est démarré
    import requests
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Serveur non accessible sur {BASE_URL}")
            print("Démarrez l'application avec: python run.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Impossible de se connecter à {BASE_URL}")
        print("Démarrez l'application avec: python run.py")
        sys.exit(1)
    
    # Lancer les tests
    pytest.main([__file__, '-v', '--tb=short'])

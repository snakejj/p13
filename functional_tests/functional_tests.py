from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bubble.settings import BASE_DIR
firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = True
firefox_options.add_argument('--window-size=1920x1080')


class FunctionalTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Firefox(
            executable_path=str(BASE_DIR / 'webdrivers' / 'geckodriver'),
            options=firefox_options,
        )
        cls.driver.implicitly_wait(30)
        cls.driver.maximize_window()
        mixer.blend('videos.Video', pk=3548, link="Qa7w5KeNsxc", status="IN", average_interest_rating=4.50,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=6846, link="HqyJ7-ibUmo", status="IN", average_interest_rating=5.50,
                    average_quality_rating=4.30)
        mixer.blend('videos.Video', pk=8813, link="OgDZ3szraiY", status="IN", average_interest_rating=6.50,
                    average_quality_rating=5.30)
        mixer.blend('videos.Video', pk=9102, link="Yut87qR_thM", status="IN", average_interest_rating=7.50,
                    average_quality_rating=2.30)
        mixer.blend('videos.Video', pk=9358, link="jUdlNsgjJRY", status="IN", average_interest_rating=8.50,
                    average_quality_rating=9.30)
        mixer.blend('videos.Video', pk=9998, link="6JLgWX9iqgo", status="IN", average_interest_rating=9.50,
                    average_quality_rating=7.30)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.driver.quit()

    def test_submit_video(self):
        self.driver.get(self.live_server_url)
        WebDriverWait(self.driver, 10)

        assert "Accueil" in self.driver.title

        # Submit an incorrect link
        try:
            link_to_login_page = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.NAME, "link_sent"))
            )

            # Filling the video form
            self.driver.find_element_by_name('video-link').send_keys('https://www.youtuhM')
            # Submitting the form
            link_to_login_page.click()

        except:
            print("The page loading was greater than 10 seconds, hence the test was stopped")
            self.driver.quit()

        assert "Vidéo aléatoire" in self.driver.title
        assert "Le lien est incorrect, merci de founir un lien Youtube valide" in self.driver.page_source

        # Submit a video which already exists in db
        try:
            link_to_login_page = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.NAME, "link_sent"))
            )

            # Filling the video form
            self.driver.find_element_by_name('video-link').send_keys('https://www.youtube.com/watch?v=Yut87qR_thM')
            # Submitting the form
            link_to_login_page.click()

        except:
            print("The page loading was greater than 10 seconds, hence the test was stopped")
            self.driver.quit()

        assert "Vidéo aléatoire" in self.driver.title
        assert "merci de proposer une autre" in self.driver.page_source

        # Submit a video which doesn't exist
        try:
            link_to_login_page = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.NAME, "link_sent"))
            )

            # Filling the video form
            self.driver.find_element_by_name('video-link').send_keys('https://www.youtube.com/watch?v=uvf0lD5xzH0')
            # Submitting the form
            link_to_login_page.click()

        except:
            print("The page loading was greater than 10 seconds, hence the test was stopped")
            self.driver.quit()

        assert "Vidéo aléatoire" in self.driver.title
        assert "L'API de randomisation a répondu en" in self.driver.page_source

    def test_login_dashboard(self):

        user = mixer.blend('auth.User', username='administrateur', is_active='True')
        user.set_password('my_password123')
        user.save()

        self.driver.get(self.live_server_url)
        WebDriverWait(self.driver, 10)

        assert "Accueil" in self.driver.title

        # Go to the login page
        try:
            link_to_login_page = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.ID, "login_link"))
            )
            link_to_login_page.click()

        except:
            print("The page loading was greater than 10 seconds, hence the test was stopped")
            self.driver.quit()

        # Filling the login form

        self.driver.find_element_by_name('username').send_keys('administrateur')
        self.driver.find_element_by_name('password').send_keys('my_password123')

        # Submitting the form to test if the warning about unvalidated account is active, and thus redirect to login

        self.driver.find_element_by_id("button_send").click()

        WebDriverWait(self.driver, 10)

        assert "Bienvenue administrateur !" in \
               self.driver.page_source
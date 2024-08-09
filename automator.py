from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException
from time import sleep
from urllib.parse import quote

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# Set up Chrome options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")
options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

# Define the delay time
delay = 30  # seconds

# Load message from file
with open("message.txt", "r", encoding="utf8") as f:
    message = f.read().strip()
message = quote(message)  # URL encode the message

# Load numbers from file
with open("numbers.txt", "r") as f:
    numbers = [line.strip() for line in f.read().splitlines() if line.strip()]

total_number = len(numbers)
print(style.RED + f'Found {total_number} numbers in the file.' + style.RESET)

# Process each number
for idx, number in enumerate(numbers):
    number = number.strip()
    if number == "":
        continue

    print(style.YELLOW + '{}/{} => Sending message to {}.'.format((idx + 1), total_number, number) + style.RESET)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Open WhatsApp Web
        driver.get('https://web.whatsapp.com')

        # Wait for the WhatsApp Web interface to be fully loaded
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
        )

        url = f'https://web.whatsapp.com/send?phone={number}&text={message}'
        driver.get(url)
        
        try:
            # Wait for the send button to be clickable and click it
            click_btn = WebDriverWait(driver, delay).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']"))
            )
            click_btn.click()
            
            # Wait for the message to be sent
            WebDriverWait(driver, delay).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@aria-label='Sending…']"))
            )
            
            print(style.GREEN + 'Message sent to: ' + number + style.RESET)
            sleep(3)  # Wait a bit before proceeding to the next number

        except TimeoutException:
            print(style.RED + f"Timeout while trying to send message to {number}. Moving to next number." + style.RESET)
        except NoAlertPresentException:
            print(style.RED + f"No alert present after timeout with {number}. Moving to next number." + style.RESET)

    except UnexpectedAlertPresentException:
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(style.RED + f"Unexpected alert present: {alert_text}. Accepting alert and continuing..." + style.RESET)
            alert.accept()
        except NoAlertPresentException:
            print(style.RED + "Alert was not found when trying to handle it, continuing..." + style.RESET)
    except Exception as e:
        print(style.RED + f'Failed to send message to {number}: {str(e)}' + style.RESET)

    finally:
        driver.quit()  # Ensure the driver quits each time

    sleep(5)  # Wait to ensure the process is complete before moving to the next number

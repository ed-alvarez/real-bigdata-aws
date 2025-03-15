import logging
import os
import signal
import time
from datetime import datetime, timedelta

import aws_lambda_context
import aws_lambda_logging
import pyotp
import selenium.common.exceptions
import settings as settings
import slack_parse.download_export.slack_export_to_s3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slack_parse.download_export.headless_chrome import create_driver

log = logging.getLogger(__name__)

# Settings
DOWNLOAD_PATH = settings.SLACK_EXPORT_DOWNLOAD_PATH  # '/tmp/slack/exports/'


class NoDataFoundException(Exception):
    pass


class NoExportHistoryException(Exception):
    pass


class NoOTPSecretForOTPAccountException(Exception):
    pass


def create_webdriver() -> Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/opt/chrome/chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("window-size=2560x1440")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    chrome_options.add_argument("--remote-debugging-port=9222")
    # chrome_options.add_argument("--data-path=/tmp/chrome-user-data")
    # chrome_options.add_argument("--disk-cache-dir=/tmp/chrome-user-data")
    chrome: Chrome = webdriver.Chrome("/opt/chromedriver", options=chrome_options)
    return chrome


def lambda_handler(event: dict, context: aws_lambda_context.LambdaContext) -> dict:
    if os.environ.get("AWS_EXECUTION_ENV") is not None:
        aws_lambda_logging.setup(
            level=settings.LOG_LEVEL,
            boto_level=settings.BOTO_LOG_LEVEL,
            aws_request_id=context.aws_request_id,
            module="%(module)s",
        )
    log.debug(event)
    log.debug(context)
    # Request should have client_name and date_y_m_d parameters
    res: dict = download_from_lambda_event(event=event)
    log.info(res)
    return res


def chromedriver_freeze_handler(signum, frame):
    err_str: str = "Chromedriver froze. Let Lambda retry."
    log.error(f"{err_str}{chr(10)}Signal handler called with signal {signum}")
    raise OSError(err_str)


def clear_path(download_path: str):
    if os.path.isdir(download_path):
        for item in os.listdir(download_path):
            file_item = os.path.join(download_path, item)
            log.debug(f"Removing {file_item}")
            os.remove(file_item)


def download_from_lambda_event(event: dict) -> dict:
    client_name: str = event.get("client_name", None)
    date_y_m_d: str = event.get("date_y_m_d", None)
    result: dict = download(client_name=client_name, date_y_m_d=date_y_m_d)
    return result


def attempt_sign_in(driver: Chrome, slack_email_login: str, slack_password: str):
    log.info("Attempting to fill in Sign In Form")
    try:
        log.debug("Waiting for email field to become visible")
        elem: WebElement = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "email")))
    except TimeoutException as ex:
        err_str: str = f"Did not receive expected Slack login page"
        log.error(err_str)
        driver.quit()
        raise TimeoutException(err_str)

    elem.clear()
    log.debug("clearing email field of data")
    elem.send_keys(slack_email_login)
    log.debug(f"sending email address of {slack_email_login}")

    try:
        log.debug("trying to find password field")
        pw_elem = driver.find_element(By.NAME, "password")
    except Exception as ex:
        err_str: str = f"Could not find Password field"
        log.error(err_str)
        driver.quit()
        raise NoSuchElementException(err_str)

    pw_elem.clear()
    log.debug("clearing password field of data")
    pw_elem.send_keys(slack_password)
    log.debug(f"sending password of {slack_password}")

    pw_elem.send_keys(Keys.ENTER)
    log.debug("Clicked Enter on page")
    log.info("Completed sign in form")
    return


def attempt_otp(driver: Chrome, slack_otp_secret: str, client_name: str, delay: int = 4, this_attempt: int = 1):
    if this_attempt > 1:
        log.info(f"OTP attempt {this_attempt}")
    try:
        otp_elem: WebElement = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.NAME, "2fa_code")
            )  # ID is different between enterprise grid and enterprise select (direct login)
        )

        if otp_elem:
            log.info("Found 2FA element, entering OTP code")
            if slack_otp_secret == "":  # nosec
                err_msg: str = f"No OTP for {client_name} configured in AWS Parameter Store but account is OTP/2FA-enabled"
                log.exception(err_msg)
                raise NoOTPSecretForOTPAccountException(err_msg)

            time.sleep(2)
            log.debug(slack_otp_secret)
            log.info("Generate OTP")
            totp: pyotp.totp.TOTP = pyotp.TOTP(s=slack_otp_secret)
            otp: str = totp.now()
            log.debug(otp)

            item: int = 1
            digit: str
            for digit in otp:
                aria_label: str = f"input[aria-label='digit {item} of 6']"
                log.debug(aria_label)
                try:
                    aria: WebElement = driver.find_element(By.CSS_SELECTOR, aria_label)
                except Exception as ex:
                    log.error(f"Could not find {aria_label}{chr(10)}{ex}")
                    driver.quit()
                    raise ex
                aria.send_keys(digit)
                item = item + 1
            time.sleep(3)
            log.info("OTP Entered fully")

    except TimeoutException as ex:
        log.info('No "2fa_code" id element, no OTP 2FA page, continuing')

    return


def download(client_name: str, date_y_m_d: str) -> dict:  # noqa: C901
    if date_y_m_d is None:
        # Default to day before
        date_y_m_d = (datetime.now() - timedelta(2)).strftime("%Y-%m-%d")
        log.warning(f"No Date found in event so setting date to {date_y_m_d}")

    # Settings
    SLACK_EMAIL_LOGIN = settings.get_slack_email_login(client_name)
    SLACK_PASSWORD = settings.get_slack_password(client_name)
    SLACK_TEAM_NAME = settings.get_slack_team_name(client_name)
    SLACK_OTP_SECRET = settings.try_get_slack_otp_secret(client_name)  # for 2fa
    ROOT_URL = f"https://{SLACK_TEAM_NAME}.slack.com"

    # Clear download path in case files from previous existing.
    log.info("Clearing Download Path")
    clear_path(DOWNLOAD_PATH)

    # set a time limit of 20 secs for chromedriver to load, otherwise assume frozen and raise exception
    signal.signal(signal.SIGALRM, chromedriver_freeze_handler)
    signal.alarm(20)

    driver: Chrome = create_driver()
    # driver: Chrome = create_webdriver()

    signal.alarm(0)

    export_url: str = f"{ROOT_URL}/sign_in_with_password?redir=%2Fservices%2Fexport"
    try:
        driver.get(export_url)
        log.info(f"Getting data from {export_url}")
    except (TimeoutException, WebDriverException) as ex:
        log.error(ex)
        raise ex

    try:
        elem: WebElement = driver.find_element(By.LINK_TEXT, "sign in here")
        if elem:
            elem.click()
            time.sleep(2)
    except NoSuchElementException as ex:
        log.info('No "sign in here" element, not Enterprise Grid page, continuing')
        log.info(ex)

    time.sleep(2)
    attempt_sign_in(driver, SLACK_EMAIL_LOGIN, SLACK_PASSWORD)
    time.sleep(2)

    # Check for OTP 2FA elements and fill if necessary
    attempt_otp(driver, SLACK_OTP_SECRET, client_name, delay=4)
    #    Sometimes OTP asked for again
    attempt_otp(driver, SLACK_OTP_SECRET, client_name, delay=3, this_attempt=2)

    # Sometimes sign in just fails and bounced out to sign in page
    try:
        elem = driver.find_element(By.NAME, "email")
    except NoSuchElementException:
        log.info("Non-login page found, proceed as normal")
    else:
        log.info("Was bounced out, try sign in again")
        time.sleep(2)
        attempt_sign_in(driver, SLACK_EMAIL_LOGIN, SLACK_PASSWORD)
        time.sleep(2)

        # Check for OTP 2FA elements and fill if necessary
        attempt_otp(driver, SLACK_OTP_SECRET, client_name, delay=4)
        attempt_otp(driver, SLACK_OTP_SECRET, client_name, delay=3, this_attempt=2)

    # Parse for Export History
    try:
        filename = ""

        try:
            elem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "export_history")))
        except Exception as ex:
            log.error(f"{driver.page_source.encode('utf-8')}{chr(10)}{ex}")
            driver.quit()
            raise NoExportHistoryException("Could not load export_history" + str(ex))
        elem = driver.find_element(By.ID, "export_history")

        html = elem.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        eh_table_body = soup.find_all("tbody")[0]
        found_date = False
        for row in eh_table_body.find_all("tr"):
            tds = row.find_all("td")
            date_range = tds[2].text
            log.info(f"{tds[3].text}")
            a = tds[3].find("a")
            log.debug(f"a is {a}")
            if (
                a is None
            ):  # Slack changed message from Processing to Waiting, future proof this check by assuming no link provided if export not ready
                # "Processing" in tds[3].text:  # Special ellipsis sometimes used
                # Sometimes a Slack export never gets out of Processing/Waiting stage
                # Will still error if it's the latest date and that's wanted,
                # but historical downloads will be able to get past this line
                continue
            href = tds[3].find("a")["href"]
            log.debug(f"href is {href}")
            dates = date_range.split("–")  # Special char, copy and paste
            log.debug(f"dates are {dates}")
            start_date = dates[0].strip()
            log.debug(f"start_date is {start_date}")
            end_date = dates[1].strip()
            log.debug(f"end_date is {end_date}")
            if "," in start_date:  # Enterprise Grid interface
                start_date = datetime.strptime(start_date, "%B %d, %Y")
                log.debug(f"updated start_date is {start_date}")
                end_date = datetime.strptime(end_date, "%B %d, %Y")
                log.debug(f"updated end_date is {end_date}")
            else:  # Plus interface
                start_date = datetime.strptime(start_date, "%d %B %Y")
                log.debug(f"updated start_date is {start_date}")
                end_date = datetime.strptime(end_date, "%d %B %Y")
                log.debug(f"updated end_date is {end_date}")
            date = datetime.strptime(date_y_m_d, "%Y-%m-%d")

            log.debug(f"{date_range}, {href}")
            log.debug(f"{start_date}, {date}, {end_date}")
            log.debug(f"{start_date} <= {date} <= {end_date}")
            if start_date <= date < end_date:
                found_date = True
                break
        if not found_date:
            raise NoDataFoundException("Could not find requested date in exports")
        # https://ipsentinel.slack.com/services/export/download/1854657145589/74a85fee
        download_url = f"{ROOT_URL}{href}"
        log.debug(f"download_url is {download_url}")
        # Allow download into directory on Chrome. It is this that matters along with a couple of the settings in the options
        # https://stackoverflow.com/questions/57599776/download-file-through-google-chrome-in-headless-mode
        params = {"behavior": "allow", "downloadPath": DOWNLOAD_PATH}
        log.debug(f"params is {params}")
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

        driver.get(download_url)
        log.info(f"downloading_url {download_url} and waiting ")  # python 3.6 f-strings
        log.info(os.listdir(DOWNLOAD_PATH))
        while True:
            files = os.listdir(DOWNLOAD_PATH)
            if len(files) == 0:
                time.sleep(5)
                continue
            elif len(files) > 1:
                raise Exception(f"Too many files in {DOWNLOAD_PATH}")

            filename = files[0]
            if filename.endswith("crdownload") or filename == "":
                time.sleep(5)
                continue
            elif filename.endswith("zip"):
                log.info(filename)
                export_local_path = os.path.join(DOWNLOAD_PATH, filename)
                break
    except (NoDataFoundException, NoExportHistoryException) as e:
        log.error("In No Data Found exception")
        log.error(str(e))
        raise (e)
    except Exception as e:
        log.error("In General Exception" + str(e))
        log.error("General Exception:" + str(e))
        raise (e)
    finally:
        log.info("Quitting browser")
        driver.quit()
    try:
        results = slack_parse.download_export.slack_export_to_s3.to_s3(client_name, date_y_m_d, export_local_path)
    finally:
        if filename != "":
            log.info(f"Deleting DL {filename}")
            os.remove(export_local_path)
    return results

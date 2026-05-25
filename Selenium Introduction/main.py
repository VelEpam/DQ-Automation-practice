import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = r"C:\Users\ThanigaivelSekar\Desktop\Learning\DEQ Automation\generated_report"

class SeleniumContextManager:
    def __init__(self, headless=True, window_size=(1920, 1080)):
        self.headless = headless
        self.window_size = window_size
        self.driver = None

    def __enter__(self):
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
            logger.info("WebDriver initialized successfully")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver quit successfully")
            except Exception as e:
                logger.error(f"Error while quitting WebDriver: {e}")
        if exc_type is not None:
            logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")

def save_to_csv(filename, header, data):
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, filename)
        df = pd.DataFrame(data, columns=header)
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error occurred while saving to CSV: {e}", exc_info=True)
        return False

def extract_table_to_csv(driver, wait):
    try:
        logger.info("Starting table extraction...")

        table_elem = None
        try:
            table_elem = wait.until(EC.presence_of_element_located((By.ID, "table_id")))  # Replace with actual ID
            logger.info("Table found by ID")
        except Exception:
            try:
                table_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
                logger.info("Table found by XPATH")
            except Exception:
                try:
                    table_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.plotly-graph-div")))
                    logger.info("Table found by CSS_SELECTOR")
                except Exception:
                    logger.error("Table not found by any locator")
                    return False

        if "plotly-graph-div" in table_elem.get_attribute("class"):
            table_data = driver.execute_script(
                """
                const gd = arguments[0];
                const data = gd._fullData || gd.data || [];
                const trace = data.find(t => t.type === 'table');
                if (!trace) return null;
                const headers = Array.isArray(trace.header?.values) ? trace.header.values : [];
                const cells = Array.isArray(trace.cells?.values) ? trace.cells.values : [];
                if (!cells.length) return {headers, rows: []};
                const rows = [];
                const rowCount = cells[0].length;
                for (let r = 0; r < rowCount; r++) {
                  const row = [];
                  for (let c = 0; c < cells.length; c++) {
                    row.push(cells[c][r] != null ? String(cells[c][r]) : '');
                  }
                  rows.push(row);
                }
                return {headers, rows};
                """,
                table_elem
            )
            if not table_data or not table_data.get("rows"):
                logger.warning("No table data extracted")
                return False
            headers = table_data.get("headers") or []
            rows = table_data.get("rows") or []
            save_to_csv("table.csv", headers, rows)
            logger.info("Table successfully saved to table.csv")
            return True
        else:
            headers = [th.text for th in table_elem.find_elements(By.TAG_NAME, "th")]
            rows = []
            for tr in table_elem.find_elements(By.TAG_NAME, "tr"):
                cells = tr.find_elements(By.TAG_NAME, "td")
                if cells:
                    rows.append([cell.text for cell in cells])
            save_to_csv("table.csv", headers, rows)
            logger.info("Table successfully saved to table.csv")
            return True

    except TimeoutException:
        logger.error("Timeout waiting for table to load")
        return False
    except Exception as e:
        logger.error(f"Error extracting table: {e}", exc_info=True)
        return False

def iterate_doughnut_filters(driver, wait):
    screenshot_paths = []
    csv_paths = []

    try:
        logger.info("Starting doughnut chart filter iteration...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Wait for the chart to be present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.plotly-graph-div")))
        time.sleep(2)

        # --- Initial CSV and screenshot (unfiltered) ---
        def extract_svg_pie_data(csv_filename):
            wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "g.pielayer g.slicetext"))
            time.sleep(1)
            slicetexts = driver.find_elements(By.CSS_SELECTOR, "g.pielayer g.slicetext")
            data_rows = []
            for slicetext in slicetexts:
                tspans = slicetext.find_elements(By.TAG_NAME, "tspan")
                if len(tspans) >= 2:
                    label = tspans[0].text.strip()
                    value = tspans[1].text.strip()
                    data_rows.append([label, value])
            if data_rows:
                save_to_csv(csv_filename, ["Facility Type", "Min Average Time Spent"], data_rows)
                csv_paths.append(os.path.join(OUTPUT_DIR, csv_filename))
                logger.info(f"Saved CSV: {csv_filename}")
            else:
                logger.warning("No data found in SVG pie chart.")

        # Save initial CSV and screenshot
        extract_svg_pie_data("doughnut0.csv")
        pie_graph = driver.find_element(By.CSS_SELECTOR, "div.plotly-graph-div")
        initial_screenshot = os.path.join(OUTPUT_DIR, "screenshot0.png")
        pie_graph.screenshot(initial_screenshot)
        screenshot_paths.append(initial_screenshot)
        logger.info("Saved initial screenshot screenshot0.png")

        # --- Legend items ---
        legend_items = []
        try:
            legend_items = driver.find_elements(By.CSS_SELECTOR, "g.legend .traces .legendtoggle")
            if not legend_items:
                legend_items = driver.find_elements(By.CSS_SELECTOR, ".legendtoggle")
            if not legend_items:
                legend_items = driver.find_elements(By.XPATH, "//*[contains(@class,'legendtoggle')]")
        except Exception as e:
            logger.error(f"Error finding legend items: {e}")

        logger.info(f"Found {len(legend_items)} legend items")

        for idx, legend in enumerate(legend_items):
            try:
                logger.info(f"Clicking legend {idx}")
                ActionChains(driver).move_to_element(legend).click().perform()
                time.sleep(2)  # Wait for chart to update

                csv_filename = f"doughnut{idx+1}.csv"
                extract_svg_pie_data(csv_filename)

                # Screenshot after filter
                filtered_screenshot = os.path.join(OUTPUT_DIR, f"screenshot{idx+1}.png")
                pie_graph.screenshot(filtered_screenshot)
                screenshot_paths.append(filtered_screenshot)
                logger.info(f"Saved filtered screenshot screenshot{idx+1}.png")

                # Unclick (restore) the legend for the next iteration
                ActionChains(driver).move_to_element(legend).click().perform()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error clicking legend {idx}: {e}")

        return screenshot_paths, csv_paths

    except Exception as e:
        logger.error(f"Fatal error in iterate_doughnut_filters: {e}", exc_info=True)
        return screenshot_paths, csv_paths



def main():
    html_file_path = r"C:\Users\ThanigaivelSekar\Desktop\Learning\DEQ Automation\generated_report\report.html"
    file_url = f"file:///{html_file_path.replace(chr(92), '/')}"

    logger.info(f"Starting automation with report: {file_url}")

    try:
        with SeleniumContextManager(headless=False, window_size=(1400, 900)) as driver:
            wait = WebDriverWait(driver, 20)
            driver.get(file_url)
            logger.info("Report loaded in browser")
            time.sleep(5)

            logger.info("=" * 50)
            logger.info("PHASE 1: TABLE EXTRACTION")
            logger.info("=" * 50)
            table_success = extract_table_to_csv(driver, wait)
            logger.info(f"Table extraction: {'SUCCESS' if table_success else 'FAILED'}")

            logger.info("=" * 50)
            logger.info("PHASE 2: DOUGHNUT CHART ANALYSIS")
            logger.info("=" * 50)
            screenshots, csvs = iterate_doughnut_filters(driver, wait)
            logger.info(f"Doughnut analysis completed: {len(screenshots)} screenshots, {len(csvs)} CSVs")

            logger.info("=" * 50)
            logger.info("EXECUTION SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Table CSV: {os.path.join(OUTPUT_DIR, 'table.csv') if table_success else 'FAILED'}")
            logger.info(f"Screenshots saved: {len(screenshots)}")
            for i, path in enumerate(screenshots):
                logger.info(f"  {path}")
            logger.info(f"Doughnut CSVs saved: {len(csvs)}")
            for i, path in enumerate(csvs):
                logger.info(f"  {path}")

    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
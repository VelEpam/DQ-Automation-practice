*** Settings ***
Library           SeleniumLibrary
Library           ./helper.py

Suite Teardown    Close Browser

*** Variables ***
${REPORT_FILE}    C:/Users/ThanigaivelSekar/Desktop/Learning/DEQ Automation/Robotic_Framework/report.html
${PARQUET_FOLDER}    C:/Users/ThanigaivelSekar/Desktop/Learning/DEQ Automation/parquet_data/facility_type_avg_time_spent_per_visit_date/partition_date=2026-03
${FILTER_DATE}    2026-03-27

*** Test Cases ***
Validate HTML Report Against Parquet
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${options}    add_argument    --allow-file-access-from-files
    Call Method    ${options}    add_argument    --disable-web-security
    Create WebDriver    Chrome    options=${options}
    Go To    file:///${REPORT_FILE}
    Sleep    3s
    Wait Until Page Contains    plotly.js v3.0.1    timeout=60s
    Wait Until Keyword Succeeds    12 times    5s    Execute Javascript    return document.getElementsByTagName('svg').length > 0
    ${html}=    Get Source
    ${df_html}=    Extract Html Table Data    ${html}
    ${df_parquet}=    Read Filtered Parquet    ${PARQUET_FOLDER}    ${FILTER_DATE}
    ${matches}    ${diffs}=    Compare Dataframes    ${df_html}    ${df_parquet}    ${FILTER_DATE}
    Run Keyword If    not ${matches}    Fail    Dataframes mismatch:\n${diffs}
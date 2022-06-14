import gspread
from decouple import config


def load_csv_sheet() -> None:
    """This loads the outputted csv into a google sheet
    so users can copy paste the data in a sheet format easier."""

    serviceAccount = gspread.service_account(filename='google-credentials.json')

    with open('output.csv', 'r') as f:
        content = f.read()
        serviceAccount.import_csv(config('GOOGLE_SHEET_URL_KEY'), content)


def clear_sheet() -> None:
    """This clears the google sheet before adding in new data."""

    serviceAccount = gspread.service_account(filename='google-credentials.json')
    sheet = serviceAccount.open_by_key(config('GOOGLE_SHEET_URL_KEY'))
    worksheet = sheet.sheet1
    worksheet.clear()


def get_sheet_by_url(url):
    serviceAccount = gspread.service_account(filename='google-credentials.json')
    sheet = serviceAccount.open_by_url(url)
    return sheet

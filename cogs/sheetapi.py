import gspread
from decouple import config


def load_csv_sheet():
    """This loads the outputted csv into a google sheet
    so users can copy paste the data in a sheet format easier."""

    serviceAccount = gspread.service_account(filename='google-credentials.json')

    with open('output.csv', 'r') as f:
        content = f.read()
        serviceAccount.import_csv(config('GOOGLE_SHEET_URL_KEY'), content)


def clear_sheet():
    """This clears the google sheet before adding in new data."""
    worksheet = _load_worksheet()
    worksheet.clear()


def _load_worksheet():

    """Gets the worksheet in our google doc
    so we can start performing operations on it."""

    # load in the credentials file / json
    serviceAccount = gspread.service_account(filename='google-credentials.json')

    # grab the sheet I'm sharing by opening with the key in the url
    sheet = serviceAccount.open_by_key(config('GOOGLE_SHEET_URL_KEY'))

    # grab the first sheet
    worksheet = sheet.sheet1

    return worksheet

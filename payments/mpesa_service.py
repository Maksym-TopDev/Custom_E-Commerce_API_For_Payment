import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from datetime import datetime
import base64
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MpesaAPI:
    # Set base URL depending on the environment
    base_url = "https://sandbox.safaricom.co.ke" if settings.MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke"

    # Use default sandbox credentials if no passkey is provided
    DEFAULT_SANDBOX_SHORTCODE = "174379"
    DEFAULT_SANDBOX_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

    @staticmethod
    def get_access_token():
        """Generates an access token for M-Pesa API authentication."""
        try:
            url = f"{MpesaAPI.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
            response_data = response.json()

            if response.status_code == 200 and "access_token" in response_data:
                return response_data["access_token"]
            else:
                logger.error(f"Failed to get M-Pesa access token: {response_data}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error while fetching M-Pesa access token: {str(e)}")
            return None

    @staticmethod
    def initiate_stk_push(phone_number, amount, account_reference="OrderPayment", transaction_desc="Payment for order"):
        """Initiates Lipa Na M-Pesa Online (STK Push)."""
        access_token = MpesaAPI.get_access_token()
        if not access_token:
            return {"error": "Failed to retrieve M-Pesa access token"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Use the provided shortcode and passkey, or fallback to default sandbox credentials
        shortcode = settings.MPESA_SHORTCODE if settings.MPESA_SHORTCODE else MpesaAPI.DEFAULT_SANDBOX_SHORTCODE
        passkey = settings.MPESA_PASSKEY if settings.MPESA_PASSKEY else MpesaAPI.DEFAULT_SANDBOX_PASSKEY

        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        url = f"{MpesaAPI.base_url}/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL if hasattr(settings, "MPESA_CALLBACK_URL") else "https://yourdomain.com/api/payments/mpesa-callback/",
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                return response_data
            else:
                logger.error(f"Failed to initiate STK Push: {response_data}")
                return {"error": "STK Push request failed", "details": response_data}
        except requests.RequestException as e:
            logger.error(f"Error during STK Push request: {str(e)}")
            return {"error": "STK Push request error", "details": str(e)}

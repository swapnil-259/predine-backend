import razorpay
import secret
# Initialize the Razorpay client
razorpay_client = razorpay.Client(auth=(secret.PROD_RAZORPAY_KEY_ID, secret.PROD_RAZORPAY_KEY_SECRET))

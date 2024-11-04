import razorpay
import secret
# Initialize the Razorpay client
razorpay_client = razorpay.Client(auth=(secret.RAZORPAY_KEY_ID, secret.RAZORPAY_KEY_SECRET))

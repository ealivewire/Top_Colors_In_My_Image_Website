# PROFESSIONAL PROJECT: "Top Colors in My Image" website (for image processing)

# OBJECTIVE: To implement a website which allows a user to select an image and find out what the most common colors are in that image.

# Import necessary library(ies):
from datetime import datetime
from dotenv import load_dotenv
import email_validator
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
import numpy as np
import os
from PIL import Image, UnidentifiedImageError
import smtplib
import traceback
from wtforms import EmailField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Email
import wx


# Define variable to be used for showing user dialog and message boxes:
dlg = wx.App()

# Initialize the Flask app. object:
app = Flask(__name__)

# Initialize global constant to store secret information:
SENDER_EMAIL_GMAIL = ""
SENDER_PASSWORD_GMAIL = ""
SENDER_HOST = ""
SENDER_PORT = 0

# Initialize global variable to be used for "contact us" form:
ContactForm = None

# Initialize global constant to be used for specifying what are considered valid image files:
ALLOWED_FILE_TYPES = "image/*"

# Initialize global variable to be used for displaying website template-design recognition:
recognition_web_template = f"Website template created by the Bootstrap team · © {datetime.now().year}"

# NOTE: Additional configurations are launched via the "run_app" function defined below.


# CONFIGURE ROUTES FOR WEB PAGES (LISTED IN HIERARCHICAL ORDER STARTING WITH HOME PAGE, THEN ALPHABETICALLY):
# ***********************************************************************************************************
# Configure route for home page:
@app.route('/',methods=["GET", "POST"])
def home():
    global app, dlg, ALLOWED_FILE_TYPES

    try:
        # Go to the home page:
        return render_template("index.html", allowed_file_types=ALLOWED_FILE_TYPES, recognition_web_template=recognition_web_template)

    except:
        dlg = wx.App()
        dlg = wx.MessageBox(f"Error (route: '/'): {traceback.format_exc()}", 'Error', wx.OK | wx.ICON_INFORMATION)
        update_system_log("route: '/'", traceback.format_exc())


# Configure route for "About" web page:
@app.route('/about')
def about():
    global app, dlg

    try:
        # Go to the "About" page:
        return render_template("about.html", recognition_web_template=recognition_web_template)

    except:
        dlg = wx.App()
        dlg = wx.MessageBox(f"Error (route: '/about'): {traceback.format_exc()}", 'Error', wx.OK | wx.ICON_INFORMATION)
        update_system_log("route: '/about'", traceback.format_exc())
        return redirect(url_for("home"))


# Configure route for "Contact Us" web page:
@app.route('/contact',methods=["GET", "POST"])
def contact():
    global app, dlg, ContactForm

    try:
        # Instantiate an instance of the "ContactForm" class:
        form = ContactForm()

        # Validate form entries upon submittal. If validated, send message:
        if form.validate_on_submit():
            # Send message via e-mail:
            msg_status = email_from_contact_page(form)

            # Go to the "Contact Us" page and display the results of e-mail execution attempt:
            return render_template("contact.html", msg_status=msg_status, recognition_web_template=recognition_web_template)

        # Go to the "Contact Us" page:
        return render_template("contact.html", form=form, msg_status="<<Message Being Drafted.>>", recognition_web_template=recognition_web_template)

    except:  # An error has occurred.
        dlg = wx.App()
        dlg = wx.MessageBox(f"Error (route: '/contact'): {traceback.format_exc()}", 'Error', wx.OK | wx.ICON_INFORMATION)
        update_system_log("route: '/contact'", traceback.format_exc())
        return redirect(url_for("home"))


# Configure route for page which displays image-processing results:
@app.route('/results',methods=["GET", "POST"])
def results():
    global app, dlg

    try:
        if request.method == 'POST':
            num_top_colors = 0
            file = request.files['file']
            if file:
                proc_results = process_image(file)
                if proc_results == "error":
                    proc_results = "An error has occurred.  Selected image could not be processed at this time."
                    success = False
                elif proc_results == "notimage":
                    proc_results = "Selected file is not an image file.  Please select another file."
                    success = False
                else:
                    num_top_colors = len(proc_results["top_colors_keys"])
                    success = True
            else:
                proc_results = "No file was selected.  Please try again."
                success = False

            # Show web page with image-processing results:
            return render_template('results.html', results=proc_results, success=success, file=file, num_top_colors=num_top_colors,recognition_web_template=recognition_web_template)

    except:
        dlg = wx.App()
        dlg = wx.MessageBox(f"Error (route: '/results'): {traceback.format_exc()}", 'Error', wx.OK | wx.ICON_INFORMATION)
        update_system_log("route: '/results'", traceback.format_exc())
        return redirect(url_for("home"))


# DEFINE FUNCTIONS TO BE USED FOR THIS APPLICATION (LISTED IN ALPHABETICAL ORDER BY FUNCTION NAME):
# *************************************************************************************************
def config_web_forms():
    """Function for configuring the web forms supporting this website"""
    global ContactForm

    try:
        # CONFIGURE WEB FORMS (LISTED IN ALPHABETICAL ORDER):
        # Configure 'contact us' form:
        class ContactForm(FlaskForm):
            txt_name = StringField(label="Your Name:", validators=[InputRequired(), Length(max=50)])
            txt_email = EmailField(label="Your E-mail Address:", validators=[InputRequired(), Email()])
            txt_message = TextAreaField(label="Your Message:", validators=[InputRequired()])
            button_submit = SubmitField(label="Send Message")

        # At this point, function is presumed to have executed successfully.  Return\
        # successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        update_system_log("config_web_forms", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


def email_from_contact_page(form):
    """Function to process a message that user wishes to e-mail from this website to the website administrator."""
    global SENDER_EMAIL_GMAIL, SENDER_HOST, SENDER_PASSWORD_GMAIL, SENDER_PORT
    try:
        # E-mail the message using the contents of the "Contact Us" web page form as input:
        with smtplib.SMTP(SENDER_HOST, port=SENDER_PORT) as connection:
            try:
                # Make connection secure, including encrypting e-mail.
                connection.starttls()
            except:
                # Return failed-execution message to the calling function:
                return "Error: Could not make connection to send e-mails. Your message was not sent."
            try:
                # Login to sender's e-mail server.
                connection.login(SENDER_EMAIL_GMAIL, SENDER_PASSWORD_GMAIL)
            except:
                # Return failed-execution message to the calling function:
                return "Error: Could not log into e-mail server to send e-mails. Your message was not sent."
            else:
                # Send e-mail.
                connection.sendmail(
                    from_addr=SENDER_EMAIL_GMAIL,
                    to_addrs=SENDER_EMAIL_GMAIL,
                    msg=f"Subject: Top Colors In My Image - E-mail from 'Contact Us' page\n\nName: {form.txt_name.data}\nE-mail address: {form.txt_email.data}\n\nMessage:\n{form.txt_message.data}"
                )
                # Return successful-execution message to the calling function::
                return "Your message has been successfully sent."

    except:  # An error has occurred.
        update_system_log("email_from_contact_page", traceback.format_exc())

        # Return failed-execution message to the calling function:
        return "An error has occurred. Your message was not sent."


def process_image(img):
    """Function for extracting and processing color information for an image"""
    try:
        # Open the selected image:
        try:
            image = Image.open(img).convert("RGB")
        except UnidentifiedImageError:
            return ("notimage")

        # Convert the image to a NumPy array:
        image_array = np.array(image)

        # Obtain the dimensions of the array:
        array_height = image_array.shape[0]
        array_width = image_array.shape[1]

        # Initialize variable to count how many pixels have had their color accounted for:
        pixel_count = 0

        # Initialize variable to store info. on the colors present for all pixels in the image:
        colors_in_image = []

        # Loop through each pixel in the image and record its color:
        for i in range(0, array_height):
            for j in range(0, array_width):
                r = image_array[i,j,0]  # red
                g = image_array[i,j,1]  # green
                b = image_array[i,j,2]  # blue
                colors_in_image.append((int(r),int(g),int(b)))
                pixel_count += 1

        # Count up unique colors represented, and get count of instances for each.
        # Store results in a directory:
        dict_unique_colors = {}
        for item in colors_in_image:
            dict_unique_colors[item] = dict_unique_colors.get(item, 0) + 1

        # Sort directory by # of instances per color (descending order):
        sorted_dict = dict(sorted(dict_unique_colors.items(), key=lambda x: x[1], reverse=True))

        # Loop through the dictionary and identify the top colors (max = 10) used in the image.
        # If less than 10 colors are represented in the image, report all colors used:
        i = 0
        top_colors_keys = []
        top_colors_values = []
        for key in sorted_dict.keys():
            if i < len(sorted_dict) and i < 10:
                top_colors_keys.append(key)
                top_colors_values.append([sorted_dict[key], round(sorted_dict[key] / pixel_count * 100,2), "#{:02x}{:02x}{:02x}".format(key[0],key[1],key[2])])
                i += 1
            else:
                break

        # Gather final metrics to be returned to the calling function:
        results = {
            "filename": img.filename,
            "image_type": img.content_type,
            "pic_mode": image.mode,
            "num_pixels_present": array_height * array_width,
            "num_pixels_processed": pixel_count,
            "unique_colors": len(sorted_dict.keys()),
            "top_colors_keys": top_colors_keys,
            "top_colors_values": top_colors_values
        }

        # Return successful-execution indication to the calling function:
        return results

    except:  # An error has occurred.
        update_system_log("process_image", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return "error"


def run_app():
    """Main function for this application"""
    global app, SENDER_EMAIL_GMAIL, SENDER_HOST, SENDER_PASSWORD_GMAIL, SENDER_PORT

    try:
        # Load environmental variables from the ".env" file:
        load_dotenv()

        # Define constants to be used for e-mailing messages submitted via the "Contact Us" web page:
        SENDER_EMAIL_GMAIL = os.getenv("SENDER_EMAIL_GMAIL")
        SENDER_PASSWORD_GMAIL = os.getenv("SENDER_PASSWORD_GMAIL")  # App password (for the app "Python e-mail", NOT the normal password for the account).
        SENDER_HOST = os.getenv("SENDER_HOST")
        SENDER_PORT = os.getenv("SENDER_PORT")

        # Initialize an instance of Bootstrap5, using the "app" object defined above as a parameter:
        Bootstrap5(app)

        # Retrieve the secret key to be used for CSRF protection:
        app.secret_key = os.getenv("SECRET_KEY_FOR_CSRF_PROTECTION")

        # Configure web forms.  If function failed, update system log and return
        # failed-execution indication to the calling function:
        if not config_web_forms():
            update_system_log("run_app", "Error: Web forms configuration failed.")
            return False

    except:  # An error has occurred.
        update_system_log("run_app", traceback.format_exc())
        return False


def update_system_log(activity, log):
    """Function to update the system log with errors encountered"""
    global dlg

    try:
        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_file = current_date_time.strftime("%Y-%m-%d")

        # Update log file.  If log file does not exist, create it:
        with open("log_top_colors_in_my_image_" + current_date_time_file + ".txt", "a") as f:
            f.write(datetime.now().strftime("%Y-%m-%d @ %I:%M %p") + ":\n")
            f.write(activity + ": " + log + "\n")

        # Close the log file:
        f.close()

    except:
        dlg = wx.App()
        dlg = wx.MessageBox(f"Error: System log could not be updated.\n{traceback.format_exc()}", 'Error', wx.OK | wx.ICON_INFORMATION)


# Run main function for this application:
run_app()

# Destroy the object that was created to show user dialog and message boxes:
dlg.Destroy()

if __name__ == "__main__":
    app.run(debug=True, port=5003)
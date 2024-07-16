from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import MinValueValidator

from socialnetwork.models import Profile
import datetime
import json 
from datetime import datetime


MAX_UPLOAD_SIZE = 2500000

AIPORT_CHOICES =( 
    ("CDG", "Paris Charles de Gaulle Airport (CDG)"), 
    ("AUS", "Austin-Bergstrom International Airport (AUS)"), 
) 

LANGUAGE_CHOICES = ( 
    ("EN", "English (default)"),  
)

CURRENCY_CHOICES = ( 
    ("USD", "US Dollar (USD) (default)"),  
)

CLASS_CHOICES = ( 
    ("1", "Economy (default)"),
    ("2", "Premium economy"),  
    ("3", "Business"),  
    ("4", "First"),  
)

STOPS_CHOICES = ( 
    ("0", "Any number of stops (default)"),  
    ("1", "Nonstop only"),
    ("2", "1 stop or fewer"),  
    ("3", "2 stops or fewer"),  
)

LANGUAGE_CHOICES = (
    ("EN", "English (default)"), 
    ("af", "Afrikaans"),
    ("ak", "Akan"),
    ("sq", "Albanian"),
    ("ws", "Samoa"),
    ("am", "Amharic"),
    ("ar", "Arabic"),
    ("hy", "Armenian"),
    ("az", "Azerbaijani"),
    ("eu", "Basque"),
    ("be", "Belarusian"),
    ("bem", "Bemba"),
    ("bn", "Bengali"),
    ("bh", "Bihari"),
    ("xx-bork", "Bork, bork, bork!"),
    ("bs", "Bosnian"),
    ("br", "Breton"),
    ("bg", "Bulgarian"),
    ("bt", "Bhutanese"),
    ("km", "Cambodian"),
    ("ca", "Catalan"),
    ("chr", "Cherokee"),
    ("ny", "Chichewa"),
    ("zh-cn", "Chinese (Simplified)"),
    ("zh-tw", "Chinese (Traditional)"),
    ("co", "Corsican"),
    ("hr", "Croatian"),
    ("cs", "Czech"),
    ("da", "Danish"),
    ("nl", "Dutch"),
    ("xx-elmer", "Elmer Fudd"),
    ("en", "English"),
    ("eo", "Esperanto"),
    ("et", "Estonian"),
    ("ee", "Ewe"),
    ("fo", "Faroese"),
    ("tl", "Filipino"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("fy", "Frisian"),
    ("gaa", "Ga"),
    ("gl", "Galician"),
    ("ka", "Georgian"),
    ("de", "German"),
    ("el", "Greek"),
    ("kl", "Greenlandic"),
    ("gn", "Guarani"),
    ("gu", "Gujarati"),
    ("xx-hacker", "Hacker"),
    ("ht", "Haitian Creole"),
    ("ha", "Hausa"),
    ("haw", "Hawaiian"),
    ("iw", "Hebrew"),
    ("hi", "Hindi"),
    ("hu", "Hungarian"),
    ("is", "Icelandic"),
    ("ig", "Igbo"),
    ("id", "Indonesian"),
    ("ia", "Interlingua"),
    ("ga", "Irish"),
    ("it", "Italian"),
    ("ja", "Japanese"),
    ("jw", "Javanese"),
    ("kn", "Kannada"),
    ("kk", "Kazakh"),
    ("rw", "Kinyarwanda"),
    ("rn", "Kirundi"),
    ("xx-klingon", "Klingon"),
    ("kg", "Kongo"),
    ("ko", "Korean"),
    ("kri", "Krio (Sierra Leone)"),
    ("ku", "Kurdish"),
    ("ckb", "Kurdish (Soranî)"),
    ("ky", "Kyrgyz"),
    ("lo", "Laothian"),
    ("la", "Latin"),
    ("lv", "Latvian"),
    ("ln", "Lingala"),
    ("lt", "Lithuanian"),
    ("loz", "Lozi"),
    ("lg", "Luganda"),
    ("ach", "Luo"),
    ("mk", "Macedonian"),
    ("mg", "Malagasy"),
    ("ms", "Malay"),
    ("ml", "Malayalam"),
    ("mt", "Maltese"),
    ("mv", "Maldives"),
    ("mi", "Maori"),
    ("mr", "Marathi"),
    ("mfe", "Mauritian Creole"),
    ("mo", "Moldavian"),
    ("mn", "Mongolian"),
    ("sr-me", "Montenegrin"),
    ("my", "Myanmar"),
    ("ne", "Nepali"),
    ("pcm", "Nigerian Pidgin"),
    ("nso", "Northern Sotho"),
    ("no", "Norwegian"),
    ("nn", "Norwegian (Nynorsk)"),
    ("oc", "Occitan"),
    ("or", "Oriya"),
    ("om", "Oromo"),
    ("ps", "Pashto"),
    ("fa", "Persian"),
    ("xx-pirate", "Pirate"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("pt-br", "Portuguese (Brazil)"),
    ("pt-pt", "Portuguese (Portugal)"),
    ("pa", "Punjabi"),
    ("qu", "Quechua"),
    ("ro", "Romanian"),
    ("rm", "Romansh"),
    ("nyn", "Runyakitara"),
    ("ru", "Russian"),
    ("gd", "Scots Gaelic"),
    ("sr", "Serbian"),
    ("sh", "Serbo-Croatian"),
    ("st", "Sesotho"),
    ("tn", "Setswana"),
    ("crs", "Seychellois Creole"),
    ("sn", "Shona"),
    ("sd", "Sindhi"),
    ("si", "Sinhalese"),
    ("sk", "Slovak"),
    ("sl", "Slovenian"),
    ("so", "Somali"),
    ("es", "Spanish"),
    ("es-419", "Spanish (Latin American)"),
    ("su", "Sundanese"),
    ("sw", "Swahili"),
    ("sv", "Swedish"),
    ("tg", "Tajik"),
    ("ta", "Tamil"),
    ("tt", "Tatar"),
    ("te", "Telugu"),
    ("th", "Thai"),
    ("ti", "Tigrinya"),
    ("to", "Tonga"),
    ("lua", "Tshiluba"),
    ("tum", "Tumbuka"),
    ("tr", "Turkish"),
    ("tk", "Turkmen"),
    ("tw", "Twi"),
    ("ug", "Uighur"),
    ("uk", "Ukrainian"),
    ("ur", "Urdu"),
    ("uz", "Uzbek"),
    ("vu", "Vanuatu"),
    ("vi", "Vietnamese"),
    ("cy", "Welsh"),
    ("wo", "Wolof"),
    ("xh", "Xhosa"),
    ("yi", "Yiddish"),
    ("yo", "Yoruba"),
    ("zu", "Zulu"),
)

CURRENCY_CHOICES = (
    ("USD", "US Dollar (USD) (default)"),
    ("ALL", "Albanian Lek (ALL)"),
    ("DZD", "Algerian Dinar (DZD)"),
    ("ARS", "Argentine Peso (ARS)"),
    ("AMD", "Armenian Dram (AMD)"),
    ("AWG", "Aruban Florin (AWG)"),
    ("AUD", "Australian Dollar (AUD)"),
    ("AZN", "Azerbaijani Manat (AZN)"),
    ("BSD", "Bahamian Dollar (BSD)"),
    ("BHD", "Bahraini Dinar (BHD)"),
    ("BYN", "Belarusian Ruble (BYN)"),
    ("BMD", "Bermudan Dollar (BMD)"),
    ("BAM", "Bosnia-Herzegovina Convertible Mark (BAM)"),
    ("BRL", "Brazilian Real (BRL)"),
    ("GBP", "British Pound (GBP)"),
    ("BGN", "Bulgarian Lev (BGN)"),
    ("XPF", "CFP Franc (XPF)"),
    ("CAD", "Canadian Dollar (CAD)"),
    ("CLP", "Chilean Peso (CLP)"),
    ("CNY", "Chinese Yuan (CNY)"),
    ("COP", "Colombian Peso (COP)"),
    ("CRC", "Costa Rican Colón (CRC)"),
    ("CUP", "Cuban Peso (CUP)"),
    ("CZK", "Czech Koruna (CZK)"),
    ("DKK", "Danish Krone (DKK)"),
    ("DOP", "Dominican Peso (DOP)"),
    ("EGP", "Egyptian Pound (EGP)"),
    ("EUR", "Euro (EUR)"),
    ("GEL", "Georgian Lari (GEL)"),
    ("HKD", "Hong Kong Dollar (HKD)"),
    ("HUF", "Hungarian Forint (HUF)"),
    ("ISK", "Icelandic Króna (ISK)"),
    ("INR", "Indian Rupee (INR)"),
    ("IDR", "Indonesian Rupiah (IDR)"),
    ("IRR", "Iranian Rial (IRR)"),
    ("ILS", "Israeli New Shekel (ILS)"),
    ("JMD", "Jamaican Dollar (JMD)"),
    ("JPY", "Japanese Yen (JPY)"),
    ("JOD", "Jordanian Dinar (JOD)"),
    ("KZT", "Kazakhstani Tenge (KZT)"),
    ("KWD", "Kuwaiti Dinar (KWD)"),
    ("LBP", "Lebanese Pound (LBP)"),
    ("MKD", "Macedonian Denar (MKD)"),
    ("MYR", "Malaysian Ringgit (MYR)"),
    ("MXN", "Mexican Peso (MXN)"),
    ("MDL", "Moldovan Leu (MDL)"),
    ("MAD", "Moroccan Dirham (MAD)"),
    ("TWD", "New Taiwan Dollar (TWD)"),
    ("NZD", "New Zealand Dollar (NZD)"),
    ("NOK", "Norwegian Krone (NOK)"),
    ("OMR", "Omani Rial (OMR)"),
    ("PKR", "Pakistani Rupee (PKR)"),
    ("PAB", "Panamanian Balboa (PAB)"),
    ("PEN", "Peruvian Sol (PEN)"),
    ("PHP", "Philippine Peso (PHP)"),
    ("PLN", "Polish Zloty (PLN)"),
    ("QAR", "Qatari Riyal (QAR)"),
    ("RON", "Romanian Leu (RON)"),
    ("RUB", "Russian Ruble (RUB)"),
    ("SAR", "Saudi Riyal (SAR)"),
    ("RSD", "Serbian Dinar (RSD)"),
    ("SGD", "Singapore Dollar (SGD)"),
    ("ZAR", "South African Rand (ZAR)"),
    ("KRW", "South Korean Won (KRW)"),
    ("SEK", "Swedish Krona (SEK)"),
    ("CHF", "Swiss Franc (CHF)"),
    ("THB", "Thai Baht (THB)"),
    ("TRY", "Turkish Lira (TRY)"),
    ("USD", "US Dollar (USD)"),
    ("UAH", "Ukrainian Hryvnia (UAH)"),
    ("AED", "United Arab Emirates Dirham (AED)"),
    ("VND", "Vietnamese Dong (VND)"),
)


# # Load the JSON data 
# with open("json/languages.json") as f: 
#     data = json.load(f) 
#     # Iterate through the language JSON array to add to language tuple of tuples for choicefield
#     for item in data: 
#         LANGUAGE_CHOICES += ((item["language_code"], item["language_name"]),)

# # Load the JSON data 
# with open("json/currency.json") as f: 
#     data = json.load(f) 
#     # Iterate through the currency JSON array to add to currency tuple of tuples for choicefield
#     for item in data: 
#         CURRENCY_CHOICES += ((item, f"{data[item]} ({item})"),)

class FlightSearchForm(forms.Form): 
    outbound_date = forms.DateField(label="Outbound Date:", 
                                    required=True, 
                                    widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    return_date = forms.DateField(label="Return Date:", 
                                  required=True, 
                                  widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    hl = forms.ChoiceField(choices = LANGUAGE_CHOICES,
                                  label="Search Language (optional):", 
                                  required=False)
    currency = forms.ChoiceField(choices = CURRENCY_CHOICES,
                                  label="Currency (optional):", 
                                  required=False)
    travel_class = forms.ChoiceField(choices = CLASS_CHOICES,
                                  label="Travel Class (optional):", 
                                  required=False)
    adults = forms.IntegerField(label="# of Adults (optional):", 
                                initial=1)
    children = forms.IntegerField(label="# of Children (optional):", 
                                initial=0)
    infants_in_seat = forms.IntegerField(label="# of Infants in Seat (optional):", 
                                initial=0)
    infants_on_lap = forms.IntegerField(label="# of Infants on Lap (optional):", 
                                initial=0)
    stop = forms.ChoiceField(choices = STOPS_CHOICES,
                                  label="# of Stops (optional):", 
                                  required=False)
    bags = forms.IntegerField(label="# of Carry-On Bags (optional):", 
                                initial=0)
    minimum_layover = forms.IntegerField(label="Minimum Layover in MINUTES (optional):", 
                                initial=0)
    maximum_layover = forms.IntegerField(label="Minimum Layover in MINUTES (optional):", 
                                initial=1440)
    max_duration = forms.IntegerField(label="Maximum Duration in MINUTES (optional):", 
                                initial=1440)
    
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        outbound_date = cleaned_data.get('outbound_date')
        return_date = cleaned_data.get('return_date')

        if outbound_date < datetime.today().date():
            raise forms.ValidationError("Outbound Date should be in the future")
        
        if return_date < datetime.today().date():
            raise forms.ValidationError("Return Date should be in the futured")
        
        if return_date < outbound_date:
            raise forms.ValidationError("Return Date should be after Outbound Date")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
      
class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    # email      = forms.CharField(max_length=50,
    #                              widget = forms.EmailInput())
    username   = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                  widget = forms.EmailInput())
    password  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput())
    confirm_password  = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']

        widgets = {
            # 'bio': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': '3'}),
            'picture': forms.FileInput(attrs={'id':'id_profile_picture'})
        }
        
        labels = {
            # 'bio': "",
            'picture': ''
        }
    
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class ActivityForm(forms.Form):
    name  = forms.CharField(max_length=100)
    addr      = forms.CharField(max_length=200)
    notes   = forms.CharField(max_length=300)

class GemActivityForm(forms.Form):
    notes   = forms.CharField(max_length=500)
    start_date = forms.DateField(label="Start Date:", 
                                    required=True, 
                                    widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    end_date = forms.DateField(label="End Date:", 
                                  required=True, 
                                  widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date < datetime.today().date():
            raise forms.ValidationError("Start Date should be in the future")
        
        if end_date < datetime.today().date():
            raise forms.ValidationError("End Date should be in the futured")
        
        if end_date < start_date:
            raise forms.ValidationError("End Date should be after Start Date")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    



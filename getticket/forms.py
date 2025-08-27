from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import TicketTransferRequest, RailwayStaff


# Passenger Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class TicketTransferForm(forms.ModelForm):
    journey_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    )

    class Meta:
        model = TicketTransferRequest
        fields = [
            'passenger_name', 'train_number', 'journey_date',
            'seat_number', 'transferred_to',
            'ticket_file', 'ticket_image'
        ]

    def clean_ticket_file(self):
        f = self.cleaned_data.get('ticket_file')
        if f and not f.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise forms.ValidationError('Only PDF, JPG, or PNG allowed.')
        return f

    def clean_ticket_image(self):
        img = self.cleaned_data.get('ticket_image')
        if img and not img.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise forms.ValidationError('Only JPG or PNG images allowed.')
        return img



# Railway Staff Login (HRMS ID)
class StaffLoginForm(forms.Form):
    hrms_id = forms.CharField(label="HRMS ID")
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        hrms_id = cleaned.get("hrms_id")
        password = cleaned.get("password")

        try:
            staff = RailwayStaff.objects.get(hrms_id=hrms_id)
            user = authenticate(username=staff.user.username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid HRMS ID or password.")
            cleaned["user"] = user
        except RailwayStaff.DoesNotExist:
            raise forms.ValidationError("No staff found with this HRMS ID.")
        return cleaned

from django.contrib.auth.forms import UserCreationForm
from .models import User, Review
from django import forms
from .models import TradeInRequest
from .models import TestDriveRequest,Order,Car

class TradeInForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = ['brand', 'model', 'year', 'mileage', 'estimated_price']
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  
        fields = ('username', 'email', 'password1', 'password2') 

class ReviewForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Review.objects.all(), required=False, widget=forms.HiddenInput())

    class Meta:
        model = Review
        fields = ['text', 'rating', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.parent: 
            self.fields.pop('rating', None)

from .models import TestDriveRequest

class TestDriveForm(forms.ModelForm):
    class Meta:
        model = TestDriveRequest
        fields = ['car', 'date', 'time', 'phone']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ваш телефон'}),
        }
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'address', 'phone']
        

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) != 10:
            raise forms.ValidationError("Телефон должен содержать 10 цифр.")
        return phone
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model  # This imports the user model dynamically
from .models import Review, TradeInRequest, TestDriveRequest, Order, Car

# Use get_user_model() to reference your custom user model dynamically
User = get_user_model()

class TradeInForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = ['brand', 'model', 'year', 'mileage', 'estimated_price', 'photo']  # Добавляем поле фото
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'multiple': False}),  # Поддержка одного файла
        }

    def __init__(self, *args, **kwargs):
        super(TradeInForm, self).__init__(*args, **kwargs)
        self.fields['photo'].required = False  # Сделаем поле фотографий необязательным

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Now using the custom user model dynamically
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

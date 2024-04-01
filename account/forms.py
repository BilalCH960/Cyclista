from django import forms
from .models import UserProfile
from .models import Address

 
class ImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_pic',)

class AddressForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name,filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['user','created_At']
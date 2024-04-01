from django import forms
from django.forms import ModelForm
from .models import *


class ProductForm(forms.ModelForm):

    # color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = ' '


    class Meta:
        model=Product
        fields = '__all__'
        exclude = ['product_slug']
        widgets ={
           'product_img': forms.ClearableFileInput(attrs={'required': True}),
        }



class AttributeForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = 'ENTER HERE'
        self.fields['is_active'].widget.attrs['class'] = ''

    class Meta:
        model = Attribute
        fields = '__all__'
        widgets ={
           'Attribute': forms.TextInput(attrs={'required': True}),
        }
        

    
class AttributeValueForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = 'ENTER HERE'
        self.fields['is_active'].widget.attrs['class'] = ''

    class Meta:
        model = AttributeValue
        fields = '__all__'
        widgets ={
            'Attribute_value': forms.TextInput(attrs={'required': True}), 
        }

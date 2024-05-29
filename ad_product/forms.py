from django import forms
from django.forms import ModelForm
from .models import *
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm


class ProductOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = 'Enter here'
        self.fields['is_active'].widget.attrs['class'] = ''

    class Meta:
        model = ProductOffer
        fields = '__all__'
    valid_to = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
    )


class ProductForm(forms.ModelForm):

    # color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        if self.instance.product_img:
            # If an image exists, remove the 'required' attribute for the product_img field
            self.fields['product_img'].widget.attrs.pop('required', None)


        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = ' '


    class Meta:
        model=Product
        fields = '__all__'
        exclude = ['product_slug']
        widgets ={
           'product_img': forms.ClearableFileInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        product_img = cleaned_data.get('product_img')

        # Check if product_img is empty (no image uploaded)
        if not product_img:
            raise ValidationError("Image is required.")  # Show error message if no image is uploaded

        return cleaned_data



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

    def clean_Attribute_value(self):
        attribute_value = self.cleaned_data.get('Attribute_value')
        if attribute_value and attribute_value.strip() == '':
            raise ValidationError('Attribute value cannot be empty.')
        return attribute_value

    class Meta:
        model = AttributeValue
        fields = '__all__'
        widgets ={
            'Attribute_value': forms.TextInput(attrs={'required': True}), 
        }

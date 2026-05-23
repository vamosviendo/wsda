from django import forms


class ContactForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-input"}),
    )
    asunto = forms.CharField(
        label="Asunto",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    mensaje = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(attrs={"class": "form-input"}),
    )

from django import forms


class ContactForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=255)
    email = forms.EmailField(label="Email")
    asunto = forms.CharField(label="Asunto", max_length=255)
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)

import os
from django import forms

class My_chat_botForm(forms.Form):
    text = forms.CharField(label='テキスト', max_length=50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['text'].widget.attrs['class'] = 'form-control'
        self.fields['text'].widget.attrs['placeholder'] = 'テキストをここに入力してください。'

    def send_message(self):
        text = self.cleaned_data['text']
        return text
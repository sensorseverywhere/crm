from django import forms

from .models import Blog


class BlogForm(forms.Form):
    title = forms.CharField()
    post = forms.CharField(widget=forms.Textarea)
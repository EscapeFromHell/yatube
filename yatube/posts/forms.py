from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)

    def clean_subject(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError('Поле текст не может быть пустым!')

        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError('Комментарий не может быть пустым!')

        return data

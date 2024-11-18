from django import forms
# from common.models import User  # 커스텀 사용자 모델


class ProfileUpdateForm(forms.ModelForm):
    """
    사용자 프로필 업데이트 폼.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'bank', 'phone_number', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bank': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

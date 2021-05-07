from django import forms

from .models import Group


class GroupCreateForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        label='Gruppenname',
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'placeholder': "Gruppenname",
            }
        )
    )

    description = forms.CharField(
        required=False,
        label='Beschreibung',
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': "Beschreibung",
            }
        )
    )

    class Meta:
        model = Group
        fields = ['name', 'description']

    def create_new(self, user, commit=True):
        instance = Group.objects.create(
            creator=user.profile,

            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
        )

        instance.save()

        return instance

    def save_existing(self, user, group):
        group.creator = user.profile

        group.name = self.cleaned_data.get('name')
        group.description = self.cleaned_data.get('description')

        group.save()
        return group

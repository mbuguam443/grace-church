from django import forms

from accounts.models import User
from .models import Member, Family


def suggest_username(member):
    """Build a free username for a member from their member number."""
    base = (member.member_number or '').strip().lower().replace('-', '').replace(' ', '')
    if not base:
        base = (member.first_name or 'member').strip().lower() + (member.last_name or '').strip().lower()
    base = base or 'member'
    candidate = base
    counter = 1
    while User.objects.filter(username__iexact=candidate).exists():
        counter += 1
        candidate = '%s%d' % (base, counter)
    return candidate


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'middle_name', 'last_name', 'gender',
            'date_of_birth', 'phone', 'email', 'address', 'photo',
            'date_joined', 'membership_status', 'membership_type',
            'baptism_status', 'baptism_date', 'salvation_date',
            'marital_status', 'occupation', 'emergency_contact_name',
            'emergency_contact_phone', 'family', 'user', 'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'membership_status': forms.Select(attrs={'class': 'form-control'}),
            'membership_type': forms.Select(attrs={'class': 'form-control'}),
            'baptism_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baptism_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salvation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'family': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member = self.instance.pk and self.instance
        # only offer accounts that are not already linked to another member
        self.fields['user'].queryset = User.objects.filter(
            member_profile__isnull=True,
        ).order_by('username')
        if member:
            current = User.objects.filter(pk=self.instance.user_id)
            if current.exists():
                self.fields['user'].queryset = self.fields['user'].queryset | current


class MemberLoginForm(forms.Form):
    """Create a login account for a member, or link an existing one, so the
    person can be pulled into classes (ministry / age group targeting)."""

    action = forms.ChoiceField(
        choices=[('create', 'Create a new login account'), ('link', 'Link an existing user account')],
        widget=forms.RadioSelect,
        initial='create',
        required=False,
    )
    username = forms.CharField(max_length=150, required=False)
    existing_user = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    age_group = forms.ChoiceField(choices=User.AGE_GROUP_CHOICES, required=False)

    def __init__(self, *args, member=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['existing_user'].queryset = User.objects.filter(
            member_profile__isnull=True, is_active=True,
        ).order_by('username')
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['existing_user'].widget.attrs.update({'class': 'form-select'})
        self.fields['age_group'].widget.attrs.update({'class': 'form-select'})
        if member is not None and not self.is_bound:
            self.fields['username'].initial = suggest_username(member)


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'address', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

from django import forms

from members.models import Member

from .models import FundedPerson


class DeaconChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.member_number})"


class FundedPersonForm(forms.ModelForm):
    assigned_deacon = DeaconChoiceField(
        queryset=Member.objects.filter(membership_status='active').order_by('first_name', 'last_name'),
        required=False,
        empty_label='— None assigned —',
        help_text='Deacon or deaconess for follow-up, prayer and discipleship.',
    )

    class Meta:
        model = FundedPerson
        fields = [
            'name', 'category', 'date_helped', 'status', 'date_of_birth', 'phone_number',
            'household_size', 'location', 'assigned_deacon', 'story', 'image', 'is_public', 'note',
        ]

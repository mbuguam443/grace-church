from django import forms

from members.models import Member

from .models import Child


class TeacherChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.member_number})"


class ChildForm(forms.ModelForm):
    teacher = TeacherChoiceField(
        queryset=Member.objects.filter(membership_status='active').order_by('first_name', 'last_name'),
        required=False,
        empty_label='— None assigned —',
        label='Teacher',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Choose the teacher from the member list.',
    )

    class Meta:
        model = Child
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'parent',
            'school_class', 'teacher', 'allergies', 'emergency_contact', 'photo', 'is_active',
        ]

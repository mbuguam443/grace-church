from django.db import models
from members.models import Family, Member


class FamilyRelationship(models.Model):
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('child', 'Child'),
        ('spouse', 'Spouse'),
        ('other', 'Other'),
    ]
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='relationships')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='family_relationships')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    class Meta:
        unique_together = ['family', 'member']

    def __str__(self):
        return f"{self.member} - {self.get_relationship_display()} in {self.family}"

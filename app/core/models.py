# core/models.py
from django.db import models

class Flag(models.Model):
    """
    Represents a country's flag.
    Used by the Ship model.
    """
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(
        upload_to='flags/',
        blank=True,
        null=True,
        help_text="Optional: Upload the country's flag icon."
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VesselType(models.Model):
    """
    Represents a type of vessel (e.g., Bulk Carrier).
    Used by the Ship model.
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


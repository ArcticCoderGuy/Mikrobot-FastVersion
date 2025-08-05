from django.db import models


class MikrobotConfig(models.Model):
    """Placeholder model for admin integration"""
    name = models.CharField(max_length=100, default="MIKROBOT Configuration")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "MIKROBOT Configuration"
        verbose_name_plural = "MIKROBOT Configuration"
        
    def __str__(self):
        return self.name
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import calendar

class LabourEntry(models.Model):
    # User association
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labour_entries', null=True, blank=True)
    
    # Date and Time fields (editable)
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    day = models.CharField(max_length=20, blank=True, editable=False, verbose_name=_("Day"))
    day_marathi = models.CharField(max_length=20, blank=True, editable=False, verbose_name=_("Day in Marathi"))
    
    # In and Out time tracking
    in_time = models.TimeField(default=timezone.now, verbose_name=_("In Time"))
    out_time = models.TimeField(null=True, blank=True, verbose_name=_("Out Time"))
    
    # Labour details (Pargi - section name)
    pargi_name = models.CharField(max_length=100, verbose_name=_("Pargi Name"), help_text=_("Name of the labour group/section"))
    labour_name = models.CharField(max_length=100, verbose_name=_("Labour Name"))
    
    # Work details
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name=_("Quantity"))
    rupees_per_head = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Rate per Head"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name=_("Total Amount"))
    
    # Location details
    land_crop_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Land/Crop Name"))
    owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Owner Name"))
    
    # Additional info
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto calculate day from date with Marathi names
        if self.date:
            weekday = self.date.weekday()
            # English day names
            self.day = calendar.day_name[weekday]
            # Marathi day names
            marathi_days = {
                0: 'सोमवार',    # Monday
                1: 'मंगळवार',   # Tuesday
                2: 'बुधवार',    # Wednesday
                3: 'गुरुवार',   # Thursday
                4: 'शुक्रवार',  # Friday
                5: 'शनिवार',    # Saturday
                6: 'रविवार'     # Sunday
            }
            self.day_marathi = marathi_days.get(weekday, '')
        
        # Auto calculate total amount
        self.total_amount = self.quantity * self.rupees_per_head
        super().save(*args, **kwargs)
    
    def get_work_duration(self):
        """Calculate work duration in hours"""
        if self.in_time and self.out_time:
            in_dt = timezone.datetime.combine(timezone.now().date(), self.in_time)
            out_dt = timezone.datetime.combine(timezone.now().date(), self.out_time)
            duration = out_dt - in_dt
            hours = duration.total_seconds() / 3600
            return round(hours, 2)
        return None
    
    def __str__(self):
        return f"{self.pargi_name} - {self.labour_name} - {self.date} - ₹{self.total_amount}"
    
    class Meta:
        ordering = ['-date', '-in_time']
        verbose_name = _("Labour Entry")
        verbose_name_plural = _("Labour Entries")
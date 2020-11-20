from django.contrib.postgres.fields import ArrayField
from django.db import models
from .v1.managers import MenuManager

# Create your models here.

class MenuType(models.Model):
    menu_type = models.CharField("Tipe Menu", max_length=100)
    description = models.CharField("Deskripsi", max_length=200, null=True,blank=True)

    def __str__(self):
        return u'%s' % (self.menu_type)
        
    def __unicode__(self):
        return u'%s' % (self.menu_type)

    class Meta:
        verbose_name='Menu Type'
        verbose_name_plural='Menu Type'


class Menu(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='menu_parent', verbose_name="Parent")
    menu_type = models.ForeignKey(MenuType, on_delete=models.CASCADE, verbose_name='Menu Type')
    title = models.CharField("Title", max_length=100)
    icon = models.CharField("Icon", max_length=25, blank=True, null=True)
    furl = models.CharField("Feature URL", max_length=50,blank=True, null=True)
    seq = models.IntegerField("Sequence", blank=True, null=True)
    enable = models.BooleanField("Enable", default=False)
    permissions = ArrayField(models.CharField(max_length=200), verbose_name="Permissions", blank=True, null=True)
    objects = MenuManager()
    v1 = MenuManager()

    def __str__(self):
        return u'%s - %s' % (self.menu_type, self.title)
        
    def __unicode__(self):
        return u'%s - %s' % (self.menu_type, self.title)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menu'
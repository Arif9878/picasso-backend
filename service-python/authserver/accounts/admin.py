from django.contrib import admin

from .models import Account, AccountOtherInformation, AccountEmergencyContact, AccountEducation, AccountFiles

admin.site.register(Account)
admin.site.register(AccountOtherInformation)
admin.site.register(AccountEmergencyContact)
admin.site.register(AccountEducation)
admin.site.register(AccountFiles)

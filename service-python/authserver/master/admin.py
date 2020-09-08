# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
import json,datetime


# from admin_view.location_admin import NegaraAdmin

from master.models import JenisNomorIdentitas, Settings, Agama, JenisKelamin, Berkas

# Register your models here.

action_names = {
	ADDITION: _('Addition'),
	DELETION: _('Deletion'),
	CHANGE: _('Change'),
}

# Register your models here.
class ActionListFilter(admin.SimpleListFilter):
	title = _('Action')
	parameter_name = 'action_flag'

	def lookups(self, request, model_admin):
		return action_names.items()

	def queryset(self, request, queryset):
		if self.value():
			queryset = queryset.filter(action_flag=self.value())
		return queryset

class LogEntryAdmin(admin.ModelAdmin):
	"""docstring for LogEntryAdmin"""
	
	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

	actions = None    
	search_fields = ['=user__username', ]
	fieldsets = [
		(None, {'fields':()}), 
		]

	list_filter = [
		ActionListFilter
	]

	search_fields = [
		'object_repr',
		'change_message'
	]

	def action_time_type(self, obj):
		return obj.action_time.strftime('%d %B %Y , Waktu %X')
	action_time_type.short_description = 'Waktu Aksi'
	action_time_type.admin_order_field = 'action_time'

	def action_type(self, obj):
		an = str(action_names[obj.action_flag])
		if obj.is_addition():
			return mark_safe('<span class="fa fa-plus-circle fa-fw" title="'+an+'" style="color: #5cb85c"></span>')
		elif obj.is_change():
			return mark_safe('<span class="fa fa-edit fa-fw" title="'+an+'" style="color: #f0ad4e"></span>')
		elif obj.is_deletion():
			return mark_safe('<span class="fa fa-times fa-fw" title="'+an+'" style="color: #d9534f"></span>')
		else:
			return an
	action_type.short_description = 'Jenis Aksi'
	action_type.admin_order_field = 'action_flag'

	def change_message_type(self, obj):
		an = str(action_names[obj.action_flag])
		pesan_ = obj.get_change_message()
		fields_ = '-'
		if pesan_ != '':
			pesan = pesan_.split(' ')
			fields_ = pesan[0]
			if fields_ == "Tidak":
				fields_ = ''
		if obj.is_addition():
			return mark_safe('<span class="fa fa-plus-circle fa-fw" title="'+an+'" style="color: #5cb85c">'+ fields_+'</span>')
		elif obj.is_change():
			return mark_safe('<span class="fa fa-edit fa-fw" title="'+an+'" style="color: #f0ad4e">'+ fields_+'</span>')
		elif obj.is_deletion():
			return mark_safe('<span class="fa fa-times fa-fw" title="'+an+'" style="color: #d9534f">'+ fields_+'</span>')
		else:
			return an
	change_message_type.short_description = 'Pesan Jenis Aksi  '
	change_message_type.admin_order_field = 'change_message'

	def get_list_display(self, request):
		if request.user.is_superuser or request.user.groups.filter(name='Admin Sistem').exists():
			list_display = ('action_time_type', 'user', 'content_type', 'object_repr','change_message_type')
		else:
			list_display = ('action_time_type', 'content_type', 'object_repr','change_message_type')
		return list_display

	def get_queryset(self, request):
		qs = super(LogEntryAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		elif request.user.groups.filter(name='Admin Sistem').exists():
			qs.filter(user__is_superuser=False)
		return qs.filter(user=request.user)
		# return super(LogEntryAdmin, self).queryset(request).prefetch_related('content_type')

	def __init__(self, *args, **kwargs):
		super(LogEntryAdmin, self).__init__(*args, **kwargs)
		# self.list_display_links = (None, )

	def suit_cell_attributes(self, obj, column):
		if column in ['action_time_type', 'action_type', ]:
			return {'class': 'text-center'}
		else:
			return None

	def json_riwayat(self, request):
		logs = LogEntry.objects.all()
		total = logs.count()
		penghapusan = 0
		pengubahan = 0
		penambahan = 0
		lainnya = 0
		if total > 0:
			penghapusan = logs.filter(action_flag=DELETION).count()*100/total
			pengubahan = logs.filter(action_flag=CHANGE).count()*100/total
			penambahan = logs.filter(action_flag=ADDITION).count()*100/total
			lainnya = logs.exclude(action_flag=ADDITION).exclude(action_flag=CHANGE).exclude(action_flag=DELETION).count()*100/total

		data = [
			{'label': 'Penghapusan Data', 'value': penghapusan, 'color': '#d9544f'},
			{'label': 'Pengubahan Data', 'value': pengubahan, 'color': '#ffc100'},
			{'label': 'Penambahan Data', 'value': penambahan, 'color': '#1693A5'},
			{'label': 'Lainnya', 'value': lainnya, 'color': '#00a3d8'}
		]
		return HttpResponse(json.dumps(data))

	def change_view(self, request, obj_id=None, form_url="", extra_context={}):
		response = super(LogEntryAdmin, self).change_view(request, obj_id, form_url="", extra_context=extra_context)
		if not request.user.is_superuser:
			self.message_user(request, "Akses ditolak.")
			return HttpResponseRedirect(reverse('admin:admin_logentry_changelist'))
		return response

	# def get_urls(self):
	# 	from django.conf.urls import url
	# 	urls = super(LogEntryAdmin, self).get_urls()
	# 	my_urls = [
	# 		url(r'^json/$', self.admin_site.admin_view(self.json_riwayat), name='json_riwayat'),
	# 		]
	# 	return my_urls + urls
		
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(JenisNomorIdentitas)
admin.site.register(Settings)
admin.site.register(Agama)
admin.site.register(JenisKelamin)
admin.site.register(Berkas)
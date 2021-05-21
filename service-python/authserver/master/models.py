# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.indexes import GinIndex
import django.contrib.postgres.search as pg_search
from django.conf import settings
from datetime import datetime
from django.db import models

import uuid
from accounts.utils import STATUS, get_status_color
from authServer.storage_backends import get_path_file

# Create your models here.
class MetaAtribut(models.Model):
	status = models.PositiveSmallIntegerField(verbose_name='Status Data', choices=STATUS, default=6, db_index=True)
	created_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_create_by_user", verbose_name="Dibuat Oleh", blank=True, null=True)
	created_at = models.DateTimeField(editable=False,null=True)
	verified_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_verify_by_user", verbose_name="Diverifikasi Oleh", blank=True, null=True)
	verified_at = models.DateTimeField(editable=False, blank=True, null=True)
	rejected_by = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_rejected_by_user", verbose_name="Dibatalkan Oleh", blank=True, null=True)
	rejected_at = models.DateTimeField(editable=False, blank=True, null=True)

	updated_at = models.DateTimeField(auto_now=True)
	
	def get_color_status(self):
		return get_status_color(self)
		
	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		if not self.id:
			self.created_at = datetime.now()
		self.updated_at = datetime.now()
		return super(MetaAtribut, self).save(*args, **kwargs)

	# def __unicode__(self):
	# 	return u'%s' % (str(self.status))

	class Meta:
		# indexes = [GinIndex(fields=['sv','status'])]
		abstract = True

class JenisNomorIdentitas(models.Model):
	jenis_nomor_identitas = models.CharField(max_length=30, verbose_name='Jenis Nomor Identitas')
	note = models.CharField(max_length=255, blank=True, null=True)

	sv = pg_search.SearchVectorField(null=True, blank=True) 
	def __unicode__(self):
		return u'%s. %s' % (self.id, self.jenis_nomor_identitas)

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		ordering = ['id']
		verbose_name = 'Jenis Nomor Identitas'
		verbose_name_plural = 'Jenis Nomor Identitas'
class FileField(models.FileField):
	def save_form_data(self, instance, data):
		if data is not None: 
			file = getattr(instance, self.attname)
			if file != data:
				file.delete(save=False)
		super(FileField, self).save_form_data(instance, data)

class Files(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	file_name = models.CharField("Nama Berkas", max_length=100, blank=True, null=True, db_index=True)
	file_number = models.CharField("Nomor Berkas", max_length=30, blank=True, null=True, help_text="Masukkan Nomor Surat / Berkas jika ada.", db_index=True)
	file = FileField(upload_to=get_path_file, blank=True, null=True)

	note = models.CharField("Catatan", blank=True, null=True, max_length=255)
	sv = pg_search.SearchVectorField(blank=True, null=True)
	 
	def get_file_url(self):
		if self.file:
			return settings.MEDIA_URL+str(self.file)
		return "#"

	def __unicode__(self):
		if self.file:
			return str(self.file)
		return str(self.file_name)

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		verbose_name='Files'
		verbose_name_plural='Files'
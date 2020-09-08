# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.deconstruct import deconstructible
from django.contrib.postgres.indexes import GinIndex
import django.contrib.postgres.search as pg_search
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings
from datetime import datetime
from django.db import models
from uuid import uuid4

import os

from accounts.utils import STATUS, get_status_color

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

	# sv = pg_search.SearchVectorField(null=True, blank=True) 
	
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
	keterangan = models.CharField(max_length=255, blank=True, null=True)

	sv = pg_search.SearchVectorField(null=True, blank=True) 
	def __unicode__(self):
		return u'%s. %s' % (self.id, self.jenis_nomor_identitas)

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		ordering = ['id']
		verbose_name = 'Jenis Nomor Identitas'
		verbose_name_plural = 'Jenis Nomor Identitas'

class Settings(models.Model):
	parameter = models.CharField("Nama Parameter", max_length=100)
	value = models.CharField("Nilai", max_length=100)
	url = models.URLField("Url", max_length=200, null=True,blank=True)

	class Meta:
		verbose_name='Setting'
		verbose_name_plural='Setting'

class Agama(models.Model):
	agama = models.CharField("Agama", max_length=100, unique=True, db_index=True)
	keterangan = models.CharField("Keterangan", blank=True, null=True, max_length=255)

	sv = pg_search.SearchVectorField(null=True, blank=True) 
	def __unicode__(self):
		return self.agama

	class Meta:
		indexes = [GinIndex(fields=['sv'])]	
		verbose_name='Agama'
		verbose_name_plural='Agama'


class JenisKelamin(models.Model):
	jenis_kelamin = models.CharField("Jenis Kelamin", max_length=100, db_index=True)
	keterangan = models.CharField("Keterangan", blank=True, null=True, max_length=255)
	sv = pg_search.SearchVectorField(null=True, blank=True) 
	
	def __unicode__(self):
		return self.jenis_kelamin

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		verbose_name='Jenis Kelamin'
		verbose_name_plural='Jenis Kelamin'


@deconstructible
class PathAndRename(object):

	def __init__(self, sub_path):
		self.path = sub_path

	def __call__(self, instance, filename):
		ext = filename.split('.')[-1]
		# set filename as random string
		filename = '{}.{}'.format(uuid4().hex, ext)
		# return the whole path to the file
		return os.path.join(self.path, filename)

path_and_rename = PathAndRename("berkas/")

class FileField(models.FileField):
	def save_form_data(self, instance, data):
		if data is not None: 
			file = getattr(instance, self.attname)
			if file != data:
				file.delete(save=False)
		super(FileField, self).save_form_data(instance, data)

class Berkas(MetaAtribut):
	nama_berkas = models.CharField("Nama Berkas", max_length=100, blank=True, null=True, db_index=True)
	berkas = FileField(upload_to=path_and_rename, max_length=255)
	no_berkas = models.CharField("Nomor Berkas", max_length=30, blank=True, null=True, help_text="Masukkan Nomor Surat / Berkas jika ada.", db_index=True)

	keterangan = models.CharField("Keterangan", blank=True, null=True, max_length=255)
	sv = pg_search.SearchVectorField(null=True, blank=True)
	 
	def get_file_url(self):
		if self.berkas:
			return settings.MEDIA_URL+str(self.berkas)
		return "#"

	def __unicode__(self):
		return str(self.nama_berkas)

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		verbose_name='Berkas'
		verbose_name_plural='Berkas'
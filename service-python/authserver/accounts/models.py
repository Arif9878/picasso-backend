# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from dateutil.relativedelta import relativedelta
from django.contrib.postgres.indexes import GinIndex
import django.contrib.postgres.search as pg_search

from authServer.storage_backends import ProfileMediaStorage, get_path_file

from master.models import JenisNomorIdentitas, MetaAtribut, Files
from menu.models import MenuType

from datetime import datetime, date

from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)

from .utils import LIST_GENDER, LIST_EDUCATION, LIST_RELIGION, LIST_BLOOD_TYPE

from django.contrib.auth.models import PermissionsMixin

import os, re, uuid

class AccountManager(BaseUserManager):
	def create_user(self, email, username, first_name=None, last_name=None, photo=None, password=None):
		"""
			Creates and saves a User with the given email, date of
			birth and password.
		"""

		if not username:
			raise ValueError('Users must have an username address')

		user = self.model(
			email=email,
			username=username,
			first_name=first_name,
			last_name=last_name,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		"""
		Creates and saves a superuser with the given email, date of
		birth and password.
		"""
		user = self.create_user(
			email,
			username,
			password=password
		)
		user.is_superuser = True
		user.is_admin = True
		user.save(using=self._db)
		return user

class Account(AbstractBaseUser,PermissionsMixin, MetaAtribut):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	email = models.EmailField(unique=True, blank=True, null=True)
	username = models.CharField(max_length=40, unique=True, db_index=True)
	first_name = models.CharField("Nama Depan", max_length=100, null=True, blank=True, db_index=True)
	last_name = models.CharField("Nama Belakang", max_length=100, null=True, blank=True, db_index=True)

	birth_place = models.CharField(max_length=30, verbose_name='Tempat Lahir', null=True, blank=True)
	birth_date = models.DateField(verbose_name='Tanggal Lahir', null=True, blank=True)
	telephone = models.CharField(verbose_name='Telepon', max_length=50, null=True, blank=True)

	id_divisi = models.CharField(verbose_name='ID Divisi', max_length=40, null=True, blank=True)
	divisi = models.CharField(verbose_name='Divisi', max_length=64, null=True, blank=True)
	id_jabatan = models.CharField(verbose_name='ID Jabatan', max_length=40, null=True, blank=True)
	jabatan = models.CharField(verbose_name='Jabatan', max_length=64, null=True, blank=True)

	marital_status = models.CharField(verbose_name='Status Pernikahan', max_length=50, null=True, blank=True)
	religion = models.CharField(verbose_name='Agama', choices=LIST_RELIGION, max_length=50, null=True, blank=True)
	blood_type = models.CharField(verbose_name='Golongan Darah', choices=LIST_BLOOD_TYPE, max_length=4, null=True, blank=True)
	gender = models.CharField(verbose_name='Jenis Kelamin', choices=LIST_GENDER, max_length=10, null=True, blank=True)

	manager_category = models.CharField(verbose_name="Kategori Pengelola", max_length=150, null=True, blank=True)
	join_date = models.DateTimeField(verbose_name="Tanggal Bergabung", null=True, blank=True)
	resign_date = models.DateTimeField(verbose_name="Tanggal Pengunduran Diri", null=True, blank=True)
	reason_resignation = models.CharField(verbose_name="Alasan Pengunduran Diri", max_length=255, null=True, blank=True)

	npwp = models.CharField(verbose_name="NPWP", max_length=20, null=True, blank=True)
	bank_account_number = models.CharField(verbose_name="Nomor Rekening Bank", max_length=20, null=True, blank=True)
	bank_branch = models.CharField(verbose_name="Cabang Bank", max_length=100, null=True, blank=True)

	id_province = models.CharField(verbose_name="ID Provinsi", max_length=40, null=True, blank=True)
	province = models.CharField(verbose_name="Provinsi", max_length=80, null=True, blank=True)
	id_districts = models.CharField(verbose_name="ID Kabupaten", max_length=40, null=True, blank=True)
	districts = models.CharField(verbose_name="Kabupaten", max_length=100, null=True, blank=True)
	id_sub_district = models.CharField(verbose_name="ID Kecamatan", max_length=40, null=True, blank=True)
	sub_district = models.CharField(verbose_name="Kecamatan", max_length=100, null=True, blank=True)
	id_village = models.CharField(verbose_name="ID Desa", max_length=40, null=True, blank=True)
	village = models.CharField(verbose_name="Desa", max_length=150, null=True, blank=True)

	address = models.CharField(verbose_name="Alamat", max_length=255, null=True, blank=True)

	lt = models.CharField(max_length=50, verbose_name='lt', blank=True, null=True)
	lg = models.CharField(max_length=50, verbose_name='lg', blank=True, null=True)

	photo = models.ImageField(upload_to=get_path_file, storage=ProfileMediaStorage(), verbose_name="Foto", null=True, blank=True)
	sv = pg_search.SearchVectorField(null=True, blank=True)

	menu = models.ForeignKey(MenuType, on_delete=models.CASCADE, blank=True, null=True)

	is_active = models.BooleanField(default=True)
	is_show_education_degree = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)

	objects = AccountManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email',]

	def get_complete_location_dictionary(self):
		province = ''
		districts = ''
		sub_district = ''
		village = ''
		id_province = ''
		id_districts = ''
		id_sub_district= ''
		id_village = ''

		return dict(
			province=province,
			districts=districts,
			sub_district=sub_district,
			village=village,
			id_province=id_province,
			id_districts=id_districts,
			id_sub_district=id_sub_district,
			id_village=id_village
		)

	# @property
	def get_years_birthday(self):
		years = "-"
		if self.birth_date:
			rdelta = relativedelta(date.today(), self.birth_date)
			years = rdelta.years
			return years
		return years

	def get_month_birthday(self):
		months = "-"
		if self.birth_date:
			rdelta = relativedelta(date.today(), self.birth_date)
			months = rdelta.months
			return months
		return months

	def get_day_birthday(self):
		days = "-"
		if self.birth_date:
			rdelta = relativedelta(date.today(), self.birth_date)
			days = rdelta.days
			return days
		return days

	def is_staff(self):
		"Allow All Member to Login"
		# Simplest possible answer: All admins are staff

		return self.is_active

	def get_full_name(self):
		# The user is identified by their nama
		fullname = ''
		if self.first_name:
			fullname = self.first_name +' '+ self.last_name
			if self.is_show_education_degree and self.account_educations.last():
				return fullname +' '+ self.account_educations.last().get_education_degree()
			return fullname
		return fullname

	def get_alamat(self):
		a = "-"
		if self.address:
			a = self.address
		if self.desa:
			a = a+' '+self.get_complete_location_dictionary()
		return a

	def __str__(self):
		return u'%s' % (self.email)

	class Meta:
		indexes = [GinIndex(fields=['sv'])]
		ordering = ['id']
		verbose_name = 'Akun'
		verbose_name_plural = 'Akun'

class NomorIdentitasPengguna(models.Model):
	number = models.CharField(max_length=100, unique=True, db_index=True)
	account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Account')
	type_identity = models.ForeignKey(JenisNomorIdentitas, on_delete=models.CASCADE, verbose_name='Jenis Nomor Identitas')

	def set_as_username(self):
		self.account.username = re.sub('[^0-9a-zA-Z]+', '', self.nomor)
		self.account.save()

	def __unicode__(self):
		return u'%s' % (self.nomor)

	class Meta:
		verbose_name = 'Nomor Identitas Pengguna'
		verbose_name_plural = 'Nomor Identitas Pengguna'

class AccountOtherInformation(models.Model):
	account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        primary_key=True,
    )
	hobby = models.CharField(verbose_name="Hobi", max_length=100, null=True, blank=True)
	other_skills_possessed = models.CharField(verbose_name="Keterampilan Lain Yang Dimiliki", max_length=100, null=True, blank=True)
	future_goals = models.CharField(verbose_name="Cita-cita", max_length=100, null=True, blank=True)
	life_motto = models.CharField(verbose_name="Motto hidup", max_length=100, null=True, blank=True)
	favorite_food = models.CharField(verbose_name="Makanan favorit", max_length=100, null=True, blank=True)
	favorite_drink = models.CharField(verbose_name="Minuman favorit", max_length=100, null=True, blank=True)
	instagram = models.CharField(verbose_name="Instagram", max_length=60, null=True, blank=True)
	facebook = models.CharField(verbose_name="Facebook", max_length=60, null=True, blank=True)
	linkedin = models.CharField(verbose_name="Linkedin", max_length=60, null=True, blank=True)

	def __unicode__(self):
		return u'%s' % str(self.npwp)

	class Meta:
		verbose_name = 'Informasi Lain Pengguna'
		verbose_name_plural = 'Informasi Lain Pengguna'

class AccountEducation(MetaAtribut):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	account = models.ForeignKey(Account, related_name='account_educations', on_delete=models.CASCADE, verbose_name='Account')
	educational_level = models.CharField(verbose_name='Jenjang Pendidikan', choices=LIST_EDUCATION, max_length=4, null=True, blank=True)
	name_educational_institution = models.CharField(verbose_name="Nama Institusi Pendidikan", max_length=80, null=True, blank=True)
	majors = models.CharField(verbose_name="Jurusan", max_length=80, null=True, blank=True)
	education_degree = models.CharField(verbose_name="Gelar Pendidikan", max_length=20, null=True, blank=True)
	graduation_year = models.IntegerField(verbose_name="Tahun Lulus", null=True, blank=True)
	file = models.ForeignKey(Files, on_delete=models.CASCADE, verbose_name='Files', null=True, blank=True)

	def get_file(self):
		if self.file:
			return self.file.get_file_url()
		return '#'

	def get_education_degree(self):
		if self.education_degree:
			return self.education_degree
		return ''

	def __unicode__(self):
		return u'%s' % str(self.name_educational_institution)

	class Meta:
		ordering = ['graduation_year']
		verbose_name = 'Pendidikan Pengguna'
		verbose_name_plural = 'Pendidikan Pengguna'

class AccountEmergencyContact(MetaAtribut):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	account = models.ForeignKey(Account, related_name='account_emergency_contacts', on_delete=models.CASCADE, verbose_name='Account')
	emergency_contact_name = models.CharField(verbose_name="Nama kontak darurat", max_length=20, null=True, blank=True)
	relationship_emergency_contacts = models.CharField(verbose_name="Hubungan dengan kontak darurat", max_length=20, null=True, blank=True)
	emergency_contact_number = models.CharField(verbose_name="Nomor kontak darurat", max_length=20, null=True, blank=True)

	def __unicode__(self):
		return u'%s' % self.emergency_contact_name
	class Meta:
		verbose_name = 'Kontak Darurat Pengguna'
		verbose_name_plural = 'Kontak Darurat Pengguna'

class AccountFiles(MetaAtribut):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	account = models.ForeignKey(Account, related_name='account_files', on_delete=models.CASCADE, verbose_name='Account')
	file = models.ForeignKey(Files, on_delete=models.CASCADE, verbose_name='Files')

	def __unicode__(self):
		return u'%s' % str(self.user.email)

	class Meta:
		verbose_name = 'Berkas Pengguna'
		verbose_name_plural = 'Berkas Pengguna'

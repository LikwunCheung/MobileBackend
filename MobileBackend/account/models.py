# -*- coding: utf-8 -*-

from django.db import models


class Account(models.Model):

    account_id = models.AutoField(db_column='id', primary_key=True)
    email = models.CharField(max_length=128, blank=False, null=False)
    password = models.CharField(max_length=256, blank=False, null=False)
    avatar_url = models.CharField(max_length=256)
    nickname = models.CharField(max_length=64)
    major = models.CharField(max_length=128)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'account'


class RegisterRecord(models.Model):

    record_id = models.AutoField(db_column='id', primary_key=True)
    account_id = models.IntegerField(blank=False, null=False, db_index=True)
    code = models.CharField(max_length=6, blank=False, null=False)
    expired = models.BigIntegerField(blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'register_record'


class ForgetPassword(models.Model):

    record_id = models.AutoField(db_column='id', primary_key=True)
    account_id = models.IntegerField(blank=False, null=False, db_index=True)
    code = models.CharField(max_length=6, blank=False, null=False)
    expired = models.BigIntegerField(blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'forget_password'


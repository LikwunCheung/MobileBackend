# -*- coding: utf-8 -*-

from django.db import models


class SocialRelation(models.Model):

    relation_id = models.AutoField(db_column='id', primary_key=True)
    account_id = models.IntegerField(db_index=True, blank=False, null=False)
    friend_id = models.IntegerField(blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'social_relation'


class SocialApply(models.Model):

    apply_id = models.AutoField(db_column='id', primary_key=True)
    account_id = models.IntegerField(db_index=True, blank=False, null=False)
    target_id = models.IntegerField(db_index=True, blank=False, null=False)
    message = models.CharField(max_length=128, blank=True)
    expired = models.BigIntegerField(blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'social_apply'

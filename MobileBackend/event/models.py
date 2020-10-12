# -*- coding: utf-8 -*-

from django.db import models


class Event(models.Model):

    event_id = models.AutoField(db_column='id', primary_key=True)
    host_id = models.IntegerField(db_index=True, blank=False, null=False)
    topic = models.CharField(max_length=128, blank=False, null=False)
    description = models.CharField(max_length=512)
    location_x = models.FloatField()
    location_y = models.FloatField()
    location_name = models.CharField(max_length=128)
    event_date = models.BigIntegerField(blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'event'


class EventParticipate(models.Model):

    record_id = models.AutoField(db_column='id', primary_key=True)
    event_id = models.IntegerField(db_index=True, blank=False, null=False)

    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'event_participate'

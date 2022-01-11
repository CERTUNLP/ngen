from django.db import models


class Message(models.Model):
    data = models.JSONField()
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    pending = models.IntegerField()
    case = models.ForeignKey('Case', models.DO_NOTHING, blank=True, null=True)
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'message'

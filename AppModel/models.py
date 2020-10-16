from django.db import models

# Create your models here.

class Compound(models.Model):
    cid = models.CharField(db_column='CID', max_length=255)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=4095, blank=True, null=True)  # Field name made lowercase.
    formula = models.CharField(db_column='Formula', max_length=255, blank=True, null=True)  # Field name made lowercase.
    smile = models.CharField(db_column='Smile', max_length=4095, blank=True, null=True)  # Field name made lowercase.
    toxicity = models.TextField(db_column='Toxicity', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    weight = models.TextField(db_column='Weight', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    sdf = models.TextField(db_column='SDF', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        db_table = 'COMPOUND'


class Enzyme(models.Model):
    pid = models.CharField(db_column='PID', max_length=255)  # Field name made lowercase.
    ecnum = models.CharField(db_column='ECnum', max_length=255)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    organism = models.CharField(db_column='Organism', max_length=255, blank=True, null=True)  # Field name made lowercase.
    localization = models.TextField(db_column='Localization', blank=True, null=True)  # Field name made lowercase.
    ph = models.TextField(db_column='PH', blank=True, null=True)  # Field name made lowercase.
    phr = models.TextField(db_column='PHR', blank=True, null=True)  # Field name made lowercase.
    t = models.TextField(db_column='T', blank=True, null=True)  # Field name made lowercase.
    tr = models.TextField(db_column='TR', blank=True, null=True)  # Field name made lowercase.
    km = models.TextField(db_column='KM', blank=True, null=True)  # Field name made lowercase.
    kkm = models.TextField(db_column='KKM', blank=True, null=True)  # Field name made lowercase.
    fromprediction = models.IntegerField(db_column='FromPrediction')  # Field name made lowercase.
    plabel = models.TextField(db_column='PLabel', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    sequence = models.TextField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        db_table = 'ENZYME'


class Reaction(models.Model):
    rid = models.CharField(db_column='RID', max_length=255)  # Field name made lowercase.
    equation = models.CharField(db_column='Equation', max_length=255)  # Field name made lowercase.
    ecnum = models.CharField(db_column='ECnum', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reactionclass = models.CharField(db_column='ReactionClass', max_length=255, blank=True, null=True)  # Field name made lowercase.
    energy = models.CharField(db_column='Energy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    frequency = models.TextField(db_column='Frequency', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        db_table = 'REACTION'


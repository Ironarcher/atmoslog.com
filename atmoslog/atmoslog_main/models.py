from django.db import models

# Create your models here.

class Feedback(models.Model):
	text = models.TextField()
	date_published = models.DateTimeField(auto_now_add=True)
	username_author = models.CharField(max_length=50)

	def __unicode__(self):
		return self.text
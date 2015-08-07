from django.db import models

# Create your models here.

class Post(models.Model):
	title = models.CharField(max_length=300)
	pub_date = models.DateTimeField(auto_now_add=True)
	text = models.TextField()

	def __unicode__(self):
		return self.title
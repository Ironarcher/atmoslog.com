from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import json

# Create your models here.

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	about_me = models.CharField(max_length=500)
	LANGUAGES = (
		('?', 'Undecided'),
		('py', 'Python'),
		('c++', 'C++'),
		('c#', "C#"),
		('java', 'Java'),
		('php', 'PHP'),
		('ruby', 'Ruby'),
		('obj-c', 'Objective-C'),
		('c', 'C'),
		('vb', 'Visual Basic'),
		('javasc', 'Javascript'),
		('perl', 'Perl'),
		('assem', 'Assembly'),
		('r', 'R'),
		('swift', 'Swift'),
		('pascal', 'Pascal'),
		('scala', 'Scala'),
		('go', 'Go'),
	)
	fav_language = models.CharField(max_length=6, choices=LANGUAGES)
	joined_on = models.DateField(auto_now_add=True)
	#picture = models.ImageField(upload_to='profile_images', blank=True)
	liked_projects = models.TextField()

	def addProject(self, project):
		ls = self.getProjects()
		ls.append(project)
		self.writeProjects(ls)

	def deleteProject(self, project):
		ls = self.getProjects()
		ls.remove(project)
		self.writeProjects(ls)

	def getProjects(self):
		return json.loads(self.liked_projects)

	def writeProjects(self, replacement):
		self.liked_projects = json.dumps(replacement)

	def __unicode__ (self):
		return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

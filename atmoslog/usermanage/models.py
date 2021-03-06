from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import json
import hashlib

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
	about_me = models.CharField(max_length=500)
	showemail = models.BooleanField(default=False)
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
	COUNTRIES = (
		('?', 'Unknown'),
		('afghanistan', 'Afghanistan'),
		('albania', 'Albania'),
		('algeria', 'Algeria'),
		('andorra', 'Andorra'),
		('antiguadeps', 'Antigua & Deps'),
		('argentina', 'Argentina'),
		('armenia', 'Armenia'),
		('australia', 'Australia'),
		('austria', 'Austria'),
		('azerbaijan', 'Azerbaijan'),
		('bahamas', 'Bahamas'),
		('bahrain', 'Bahrain'),
		('bangladesh', 'Bangladesh'),
		('barbados', 'Barbados'),
		('belarus', 'Belarus'),
		('belgium', 'Belgium'),
		('belize', 'Belize'),
		('benin', 'Benin'),
		('bhutan', 'Bhutan'),
		('bolivia', 'Bolivia'),
		('bosniaherze', 'Bosnia Herzegovina'),
		('botswana', 'Botswana'),
		('brazil', 'Brazil'),
		('brunei', 'Brunei'),
		('bulgaria', 'Bulgaria'),
		('burkina', 'Burkina'),
		('burundi', 'Burundi'),
		('cambodia', 'Cambodia'),
		('cameroon', 'Cameroon'),
		('canada', 'Canada'),
		('capeverde', 'Cape Verde'),
		('centafrica', 'Central African Republic'),
		('chad', 'Chad'),
		('chile', 'Chile'),
		('colombia', 'Colombia'),
		('comoros', 'Comoros'),
		('congo', 'Congo'),
		('demcongo', 'Congo, Democratic Republic'),
		('costarica', 'Costa Rica'),
		('croatia', 'Croatia'),
		('cuba', 'Cuba'),
		('cyprus', 'Cyprus'),
		('czechrepublic', 'Czech Republic'),
		('denmark', 'Denmark'),
		('djibouti', 'Djibouti'),
		('dominica', 'Dominica'),
		('dominicanrep', 'Dominican Republic'),
		('easttimor', 'East Timor'),
		('ecuador', 'Ecuador'),
		('egypt', 'Egypt'),
		('elsalvador', 'El Salvador'),
		('equatorialguinea', 'Equatorial Guinea'),
		('eritrea', 'Eritrea'),
		('estonia', 'Estonia'),
		('fiji', 'Fiji'),
		('finland', 'Finland'),
		('france', 'France'),
		('gabon', 'Gabon'),
		('gambia', 'Gambia'),
		('georgia', 'Georgia'),
		('germany', 'Germany'),
		('ghana', 'Ghana'),
		('greece', 'Greece'),
		('grenada', 'Grenada'),
		('guatemala', 'Guatemala'),
		('guinea', 'Guinea'),
		('guineabissau', 'Guinea-Bissau'),
		('guyana', 'Guyana'),
		('haiti', 'Haiti'),
		('honduras', 'Honduras'),
		('hungary', 'Hungary'),
		('iceland', 'Iceland'),
		('india', 'India'),
		('indonesia', 'Indonesia'),
		('iran', 'Iran'),
		('iraq', 'Iraq'),
		('ireland', 'Ireland (republic)'),
		('israel', 'Israel'),
		('italy', 'Italy'),
		('ivorycoast', 'Ivory Coast'),
		('jamaica', 'Jamaica'),
		('japan', 'Japan'),
		('jordan', 'Jordan'),
		('kazakhstan', 'Kazakhstan'),
		('kenya', 'Kenya'),
		('kiribati', 'Kiribati'),
		('northkorea', 'Korea North'),
		('southkorea', 'Korea South'),
		('kosovo', 'Kosovo'),
		('kuwait', 'Kuwait'),
		('kyrgyzstan', 'Kyrgyzstan'),
		('laos', 'Laos'),
		('latvia', 'Latvia'),
		('lebanon', 'Lebanon'),
		('lesotho', 'Lesotho'),
		('liberia', 'Liberia'),
		('libya', 'Libya'),
		('liechtenstein', 'Liechtenstein'),
		('lithuania', 'Lithuania'),
		('luxembourg', 'Luxembourg'),
		('macedonia', 'Macedonia'),
		('madagascar', 'Madagascar'),
		('malawi', 'Malawi'),
		('malaysia', 'Malaysia'),
		('maldives', 'Maldives'),
		('mali', 'Mali'),
		('malta', 'Malta'),
		('marshallislands', 'Marshall Islands'),
		('mauritania', 'Mauritania'),
		('mauritius', 'Mauritius'),
		('mexico', 'Mexico'),
		('micronesia', 'Micronesia'),
		('moldova', 'Moldova'),
		('monaco', 'Monaco'),
		('mongolia', 'Mongolia'),
		('montenegro', 'Montenegro'),
		('morocco', 'Morocco'),
		('mozambique', 'Mozambique'),
		('myanmar', 'Myanmar (Burma)'),
		('namibia', 'Namibia'),
		('nauru', 'Nauru'),
		('netherlands', 'Netherlands'),
		('newzealand', 'New Zealand'),
		('nicaragua', 'Nicaragua'),
		('niger', 'Niger'),
		('norway', 'Norway'),
		('oman', 'Oman'),
		('pakistan', 'Pakistan'),
		('palau', 'Palau'),
		('panama', 'Panama'),
		('papuanewguinea', 'Papa New Guinea'),
		('paraguay', 'Paraguay'),
		('peru', 'Peru'),
		('philippines', 'Philippines'),
		('poland', 'Poland'),
		('portugal', 'Portugal'),
		('qatar', 'Qatar'),
		('romania', 'Romania'),
		('russia', 'Russian Federation'),
		('rwanda', 'Rwanda'),
		('stkitts', 'St Kitts & Nevis'),
		('stlucia', 'St Lucia'),
		('saintvincent', 'Saint Vincent & the Grenadines'),
		('samoa', 'Samoa'),
		('sanmarino', 'San Marino'),
		('saotome', 'Sao Tome & Principe'),
		('saudiarabia', 'Saudi Arabia'),
		('southsudan', 'South Sudan'),
		('spain', 'Spain'),
		('srilanka', 'Sri Lanka'),
		('sudan', 'Sudan'),
		('suriname', 'Suriname'),
		('swaziland', 'Swaziland'),
		('sweden', 'Sweden'),
		('switzerland', 'Switzerland'),
		('syria', 'Syria'),
		('taiwan', 'Taiwan'),
		('tajikistan', 'Tajikistan'),
		('tanzania', 'Tanzania'),
		('thailand', 'Thailand'),
		('togo', 'Togo'),
		('tonga', 'Tonga'),
		('trinidad', 'Trinidad & Tobago'),
		('tunisia', 'Tunisia'),
		('turkey', 'Turkey'),
		('turkmenistan', 'Turkmenistan'),
		('tuvalu', 'Tuvalu'),
		('uganda', 'Uganda'),
		('ukraine', 'Ukraine'),
		('unitedarabemirates', 'United Arab Emirates'),
		('uk', 'United Kingdom'),
		('usa', 'United States of America'),
		('uruguay', 'Uruguay'),
		('uzbekistan', 'Uzbekistan'),
		('vanuatu', 'Vanuatu'),
		('vatican', 'Vatican City'),
		('venezuela', 'Venezuela'),
		('vietnam', 'Vietnam'),
		('yemen', 'Yemen'),
		('zambia', 'Zambia'),
		)
	country = models.CharField(max_length=50, choices=COUNTRIES, default="?")
	fav_language = models.CharField(max_length=6, choices=LANGUAGES, default="?")
	joined_on = models.DateField(auto_now_add=True)
	picture = models.TextField()
	liked_projects = models.TextField(default="[]")
	recently_viewed_projects = models.TextField(default="[]")

	def __unicode__ (self):
		return self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
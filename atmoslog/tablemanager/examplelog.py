from random import randint
import db_interface

amt = int(raw_input("Enter amount of times to add logs"))
colors = ['Red', 'Yellow', 'Green', 'Orange', 'Purple', 'White', 'Blue', 'Black', 'Grey']

counter = 0
while counter < amt:
	rand = randint(0, 8)
	selection = colors[rand]
	db_interface.log('Colors', 'Test2', selection)
	counter = counter + 1

print('Logged %s colors' % amt)
raw_input("Press any key to end the program.")
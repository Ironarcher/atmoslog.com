import timeit
setup = '''
import hashlib
import random
random.seed('supkidsitsmethebest')
'''
print min(timeit.Timer('hashlib.md5(str(random.random()) + "&0123456789").hexdigest()', setup=setup).repeat(7, 1000000))
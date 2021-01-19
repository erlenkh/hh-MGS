import random
import Composer

seed = random.random()

song = Composer.Composer(seed)

print(song.__dict__)



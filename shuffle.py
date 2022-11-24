import random
lines = open('solutii_algoritm_2.yaml').readlines()
random.shuffle(lines)
open('solutii_algoritm_2.yaml', 'w').writelines(lines)
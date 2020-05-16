import pandas as pd
import numpy as np
from parsenames import closeMatches


data = pd.read_csv('data/new.csv')
score = np.array([])
nonescore = 0
nnscore = 0


falsesocore = 1
truescore = 1

for index, row in data.iterrows():
    matches = closeMatches(row['username'])
    if matches is None:
        nonescore += 1
        if row['gender'] == 'none':
            nnscore += 1
            score = np.append(score, np.array([1]))
        else:
            score = np.append(score, np.array([0]))
    else:

        if row['gender'] == 'female' and matches[0][0] == 'F':
            score = np.append(score, np.array([1]))
            if matches[0][2] < falsesocore:
                truescore = matches[0][2]
        elif row['gender'] == 'male' and matches[0][0] == 'M':
            score = np.append(score, np.array([1]))
            if matches[0][2] < falsesocore:
                truescore = matches[0][2]
        else:
            if matches[0][2] < falsesocore:
                falsesocore = matches[0][2]
            score = np.append(score, np.array([0]))


print('Score: ', np.mean(score))
print('Nonescore: ', nonescore)
print('But nnscore: ', nnscore)
print('falsesocore: ', falsesocore)
print('truescore: ', truescore)

import sys
import pickle
if sys.argv:
    with open(sys.argv[1], 'rb') as f:
           print(pickle.load(f))
else :
    with open('sisa_db.pkl', 'rb') as f:
           print(pickle.load(f))

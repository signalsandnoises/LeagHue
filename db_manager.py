import sqlite3
import os

databaseName = "states.db"


'''
I should structure the database so that given a skin..
I can store a state {3:[this], 4:[that]} as a JSON. 
and then when retrieved in main control loop (use `json.loads(data)`), 
only execute for the lights in active_lightIDs.
this requires that anish and I configure with disjoint sets.
So I get {4,5} and he gets {3}
'''

if __name__ == "__main__":
	print("If you continue, this will overwrite the internal database.")
	print("All skin configurations will be lost.")
	x = input("Are you sure you want to continue? (y/N) >>>")
	x = x.lower()
	if x == "y" or x == "yes":
		if os.path.exists(databaseName):
			os.remove(databaseName)

		con = sqlite3.connect(databaseName)
		cur = con.cursor()

		cur.execute('''CREATE TABLE states (
			skinName text NOT NULL PRIMARY KEY,
			state text NOT NULL
			)''')
		con.commit()
		con.close()


def get_state(skinName):
	# Return the stored colors as a dict of lightIDs
	# e.g. {3: [0.5, 0.5], 4: [0.45, 0.25]}

	# we can instantiate con/cur in these methods because
	# they are called ~once per game
	con = sqlite3.connect(databaseName)
	cur = con.cursor()
	query = '''SELECT state FROM states
		WHERE skinName == \'{}\''''.format(skinName)
	cur.execute(query)
	state = cur.fetchone()
	if state is None:
		return None
	else:
		return state[0]  # state is a tuple with one element


def set_state(skinName, state):
	con = sqlite3.connect(databaseName)
	cur = con.cursor()
	
	# Remove entry for skin if it exists
	query = "DELETE FROM states WHERE states.skinName == \'{}\'".format(skinName)
	cur.execute(query)

	# Then insert the new entry for the skin
	query = "INSERT INTO states VALUES (\'{}\', \'{}\')".format(skinName, state)
	cur.execute(query)

	con.commit()
	con.close()

# To confirm that a state is correctly overwritten
def test_getSetStates():
	set_state("TestName1", "state1old")
	set_state("TestName2", "state2")
	set_state("TestName1", "state1new")

	return get_state("TestName1") == "state1new"

def test_GetNonexistentState():
	return get_state("NonexistentState") is None
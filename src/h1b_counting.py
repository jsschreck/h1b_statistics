import sys, os, csv

class Histogram:
	
	"""
	Custom dictionary class. 
	
	- add_to_dict: check if a key in self.dictionary; update (dictionary) item accordingly.
				   dict item: number of jobs, number certified 

	"""
	
	def __init__(self, name):
		self.dict = {}
		self.name = name 
	
	def add_to_dict(self, key, increment):
		if key not in self.dict:
			self.dict[key] = {
						      'N_JOBS': 1, 
						      'N_CERTIFIED': increment,
						      }
		else:
			_item = self.dict[key]
			_item['N_JOBS'] += 1
			_item['N_CERTIFIED'] += increment

class Census:

	"""
	Class for loading and sorting text files.

	"""

	def __init__(self, year = None, fileName = None):
		
		self.year = year
		self.fileName = fileName 
		
		def load_file():
			
			"""
				Local file csv loader called upon instantiation. Adds data to self as dict
				Take the top line and create dict fields, then add the columns as items.
			"""
			
			with open(self.fileName, 'r') as infile:
				reader = csv.reader(infile, delimiter=';')
				stats = {c[0]: c[1:] for c in zip(*reader)}
			self.stats = stats 
		load_file()

	def create_histograms(self):
		
		"""
			Grab the relevant fields from self data. 
			Tested on:
				- insight_testsuite/temp/input/h1b_input.csv
				- input/H1B_FY_*.csv (you must supply the file).
		"""

		try:
			SOC_LST 	= list(self.stats['LCA_CASE_SOC_NAME']) 
			STATUS_LST 	= list(self.stats['STATUS']) 
			STATE_LST 	= list(self.stats['LCA_CASE_WORKLOC1_STATE']) #LCA_CASE_EMPLOYER_STATE 
		except:
			SOC_LST 	= list(self.stats['SOC_NAME']) 
			STATUS_LST 	= list(self.stats['CASE_STATUS'])
			STATE_LST 	= list(self.stats['WORKSITE_STATE'])
		COMBINED 		= zip(SOC_LST, STATUS_LST, STATE_LST)

		"""
		
		For a file containing millions of lines, may want to avoid repeat passes to fill containers
		Below I chose to fill up two container dicts in one pass.

		"""
		
		self.total_certified = 0 
		self.states_histogram = Histogram('states')
		self.occupation_histogram = Histogram('occupations')

		for record_no, (occupation, certification, state) in enumerate(COMBINED):
			cert = int((certification == 'CERTIFIED'))
			self.total_certified += cert
			self.occupation_histogram.add_to_dict(occupation,cert)
			self.states_histogram.add_to_dict(state,cert)

	def get_top(self, key_str, histogram, top = 10, verbose = False, write_file = False):
		
		"""
		
		Function for sorting a histogram (Histogram instance) by key_str.

		Uses lambda functions for performance / ease.

		Writes data as requested.

		"""

		_top = sorted(histogram.dict.items(), 
					  key = lambda x: (-x[1]['N_CERTIFIED'], -x[1]['N_JOBS'], x[0].lower()))
		
		if not write_file:
			#logger.warning
			write_file = '../output/top_{}_{}.txt'.format(top,histogram.name)
			print "Output file not specified. Using default", write_file

		if verbose:
			print key_str

		if os.path.isfile(write_file):
			os.remove(write_file)
		
		with open(write_file, "a+") as writer:
			writer.write(key_str+'\n')
			for (key, data) in _top[:top]:
				njobs = data['N_JOBS']
				ncertified = data['N_CERTIFIED']
				percent = float("%0.1f" % (100.0 * float(ncertified) / self.total_certified)) if bool(ncertified) else 0.0
				stats_str = '{};{};{}%'.format(key, njobs, percent)
				
				if verbose:
					print stats_str

				writer.write(stats_str+'\n')

	"""
	
	The two functions below are used to call self.get_top() to solve the posed problems.

	This could be generalized into one call with fields passed in appropriately. 
	For now avoiding repeat passes over a (potentially) large input file. 

	"""

	def get_top_occupations(self, top = 10, verbose = False, write_file = False):
		key_str = 'TOP_OCCUPATIONS;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE'
		self.get_top(key_str, 
					 self.occupation_histogram, 
					 top = top, 
					 verbose = verbose, 
					 write_file = write_file)
		
	def get_top_states(self, top = 10, verbose = False, write_file = False):
		key_str = 'TOP_STATES;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE'
		self.get_top(key_str, 
					 self.states_histogram, 
					 top = top, 
					 verbose = verbose, 
					 write_file = write_file)
 
if __name__ == "__main__":

	inputfile = sys.argv[1]
	output_occup = sys.argv[2]
	output_states = sys.argv[3]

	if len(sys.argv) <= 3:
		print('Usage %s ./input/*.csv ./output/top_10_occupations.txt ./output/top_10_states.txt' % (sys.argv[0]))
		sys.exit(1)

	if not os.path.isfile(inputfile):
		print "You must supply a data file. Exiting."
		sys.exit(1)

	verbose = False

	f = Census(fileName = inputfile)
	f.create_histograms()
	f.get_top_occupations(top = 10, verbose = verbose, write_file = output_occup)
	f.get_top_states(top = 10, verbose = verbose, write_file = output_states)

#! /usr/bin/env python3

# basic stuff
from archive import InitialModels, InitialResults, ChosenExperiment, NewResults, AcceptedResults, RefutedModels, RevisedModel, UpdatedModelQuality, AdditionalModels, RevisionFail, AdditModProdFail, ExpDesignFail, CheckPointFail, CheckPointSuccess, RevisedIgnoredUpdate
import pickle
from mnm_repr import Activity
from os import listdir
from os.path import isfile, join

# plotting
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot, colors, cm
from mpl_toolkits.axes_grid1 import AxesGrid
from math import ceil


#######################################
def print_pretty_all_matrices():
	file_suffixes = {matrix_best_improvement:'best', matrix_worst_improvement:'worst', matrix_average_improvement:'average'}

	paths = get_all_paths()
	mtx = create_archives_matrix_small(paths)
	functions = [matrix_best_improvement, matrix_worst_improvement, matrix_average_improvement]

	for fun in functions:
		data_mtx = fun(mtx)
		pretty_matrix_plot(data_mtx, file_suffixes[fun])


def print_not_so_pretty_all_matrices():
	file_suffixes = {matrix_best_improvement:'best',
		matrix_worst_improvement:'worst',
		matrix_average_improvement:'average',
		matrix_number_cycles:'number_of_cycles',
		matrix_total_time:'total_time'}

	paths = get_all_paths()
	mtx = create_archives_matrix_small(paths)
	functions = [matrix_best_improvement, matrix_worst_improvement,
		matrix_average_improvement, matrix_number_cycles, matrix_total_time]

	for fun in functions:
		copied_mtx = [list(row) for row in mtx]
		data_mtx = fun(copied_mtx)
		not_so_pretty_matrix_plot(data_mtx, file_suffixes[fun])


####################################### tools:
def not_so_pretty_matrix_plot(matrix, suffix):
	all_values = [abs(val) for sublist in matrix for val in sublist if not np.isnan(val)]
	max_value = ceil(max(all_values))
	my_cmap = cm.coolwarm
	my_cmap.set_bad('k',1.)
	
	plt.imshow(matrix, cmap=my_cmap, interpolation='none', vmin=-max_value, vmax=max_value)
	plt.colorbar(cmap=my_cmap)
	plt.savefig('mtx_%s' % suffix, bbox_inches='tight')
	plt.clf()


def pretty_matrix_plot(matrix):
	flat = [val for sublist in matrix for val in sublist]
	minimum = min(flat)
	maximum = max(flat)
	mid = abs(minimum)/(abs(minimum) + maximum)
	
	if (minimum > 0) or (maximum < 0):
		raise ValueError('cannot use the pretty method: no zero point')
	
	my_cmap = cm.coolwarm
	shrunk_cmap = shiftedColorMap(my_cmap, start=0.0, midpoint=mid, stop=1.0, name='shrunk')
	shrunk_cmap.set_bad('k',1.)
	
	img = plt.imshow(matrix, cmap=shrunk_cmap, interpolation='none')
	plt.colorbar(img, cmap=shrunk_cmap)
	plt.show()


def matrix_total_time(matrix):
	return matrix_apply_function_to_archives(matrix, total_time)

def matrix_number_cycles(matrix):
	return matrix_apply_function_to_archives(matrix, number_of_run_cycles)

def matrix_best_improvement(matrix):
	return matrix_apply_function_to_archives(matrix, best_improvement)

def matrix_worst_improvement(matrix):
	return matrix_apply_function_to_archives(matrix, worst_improvement)

def matrix_average_improvement(matrix):
	return matrix_apply_function_to_archives(matrix, average_improvement)


def matrix_apply_function_to_archives(matrix, function):
	for row in matrix:
		for archive in row:
			if not isinstance(archive, float):
				row_index = matrix.index(row)
				archive_index = row.index(archive)
				try:
					matrix[row_index][archive_index] = function(archive)
				except Exception as err:
					matrix[row_index][archive_index] = np.nan
					print("matrix_apply_function_to_archives: problem with applying function: %s" % function)
					print("replaced row:%s col:%s value with NaN" % (row_index, archive_index))
					print(err)
			else:
				pass

	return matrix


# also error area

def total_time(archive): # number of minutes
	return (archive.development_history[-1].timestamp / 60)


def number_of_run_cycles(archive):# full cycles!
	check_points = [event for event in archive.development_history if (isinstance(event,CheckPointSuccess) or isinstance(event,CheckPointFail))]
	return len(check_points)-1


def best_improvement(archive):
	init_scores, final_scores = get_initl_and_final_scores(archive)
	avg_init = sum(init_scores)/float(len(init_scores))
	return (max(final_scores) - avg_init)


def worst_improvement(archive):
	init_scores, final_scores = get_initl_and_final_scores(archive)
	avg_init = sum(init_scores)/float(len(init_scores))
	return (min(final_scores) - avg_init)


def average_improvement(archive):
	init_scores, final_scores = get_initl_and_final_scores(archive)
	avg_init = sum(init_scores)/float(len(init_scores))
	avg_fin = sum(final_scores)/float(len(final_scores))
	return avg_fin - avg_init


def get_initl_and_final_scores(archive):
	ref_activities = archive.model_of_ref.intermediate_activities
	# initial scores:
	init_models = get_initial_models(archive.development_history)
	init_scores = [len(model.intermediate_activities ^ ref_activities) for model in init_models]
	# final scores:
	final_scores = [len(model.intermediate_activities ^ ref_activities) for model in archive.working_models]
	return init_scores, final_scores


def get_initial_models(dev_history):
	for event in dev_history:
		if isinstance(event, CheckPointSuccess):
			first_check_point = event
			break

	preparation_period = dev_history[:dev_history.index(first_check_point)]
	init_models = []
	revised = []
	for event in preparation_period:
		if isinstance(event, InitialModels):
			init_models.extend(event.models)
		# InitialModels is recorded before any revision can take place,
		# so this setup is safe.
		elif isinstance(event, RevisedModel):
			revised.extend(event.revised_models)
			init_models.remove(event.old_model)
		else:
			pass
	# returns only consistent models:
	# initial models that dind't need revision
	# + all produced during revisions in the preparation period
	return init_models + revised
	

def read_archive(path):
	pkl_file = open(path, 'rb')
	archive = pickle.load(pkl_file)
	pkl_file.close()
	return archive


def get_all_paths():
	folder = 'pickled_archives'
	return [ file_ for file_ in listdir(folder) if isfile(join(folder,file_))] # filters out subdirectories


def create_archives_matrix_small(all_paths):
	folder = 'pickled_archives'
	template_matrix = create_small_template_matrix()

	# eliminate case-configuration combinations w/o 
	for row in template_matrix:
		for file_sfx in row:
			file_name = get_matching_file_name_small(all_paths, file_sfx)
			if file_name == None:
				row_index = template_matrix.index(row)
				file_sfx_index = row.index(file_sfx)
				template_matrix[row_index][file_sfx_index] = np.nan
			else:
				pass

	# load and save data
	for row in template_matrix:
		for file_sfx in row:
			if isinstance(file_sfx, float): # here only float can be NaN
				pass
			else:
				# load file
				file_name = get_matching_file_name_small(all_paths, file_sfx)
				full_path = join(folder, file_name)
				archive = read_archive(full_path)
				# save data in the matrix
				row_index = template_matrix.index(row)
				file_sfx_index = row.index(file_sfx)
				template_matrix[row_index][file_sfx_index] = archive

	return template_matrix



def get_matching_file_name_small(all_paths, file_sfx): # assumes only 14 last characters are important
	for file_name in all_paths:
		if file_name[-14:] == file_sfx:
			return file_name
		else:
			pass
	return None


def create_small_template_matrix(): # only 36 system configurations tested for the paper
	matrix = []
	for tc in range(17):
		for rep in range(3):
			row = []
			for conf in range(36):
				if len(str(conf)) == 1:
					conf_pfx = 'conf0%s_' % conf # one digit
				else:
					conf_pfx = 'conf%s_' % conf # two digit

				if len(str(tc)) == 1:
					tc_pfx = 'tc0%s_' % tc # one digit
				else:
					tc_pfx = 'tc%s_' % tc # two digit

				rep_sfx = 'r%s' % rep

				row.append("".join([conf_pfx, tc_pfx, rep_sfx]))

			matrix.append(row)
	return matrix



def print_development_history(archive):
	for event in archive.development_history:

		print('time: %s' % event.timestamp)

		if isinstance(event, InitialModels):
			for mod in event.models:
				print('initial model: %s' % mod.ID)

		elif isinstance(event, InitialResults):
			print('initial results:')
			for exp in event.experiments:
				print_exp_results(exp)

		elif isinstance(event, ChosenExperiment):
			print('chosen experiment:')
			for description in event.experiment_descriptions:
				print_exp_description(description)
			
		elif isinstance(event, NewResults):
			print('new results:')
			print_exp_results(event.experiment)
			
		elif isinstance(event, AcceptedResults):
			print('accepted results:')
			print('experiment ID: %s' % event.experiment.ID)
			
		elif isinstance(event, RefutedModels):
			print('refuted models:')
			for model in event.refuted_models:
				print('model ID: %s' % model.ID)
			
		elif isinstance(event, RevisedModel):
			print('revised model:')
			print('base model ID: %s' % event.old_model.ID)
			for model in event.revised_models:
				print('new model ID: %s' % model.ID)
				difference_added = set(model.intermediate_activities) - set(event.old_model.intermediate_activities)
				difference_removed = set(event.old_model.intermediate_activities) - set(model.intermediate_activities)
				for act in difference_added:
					print('added activity: %s' % act.ID)
				for act in difference_removed:
					print('removed activity: %s' % act.ID)
			
		elif isinstance(event, UpdatedModelQuality):
			print('updated model quality:')
			print('model ID: %s' % event.model.ID)
			print('new quality: %s' % event.new_quality)

		elif isinstance(event, AdditionalModels):
			print('addtitional models:')
			for model in event.additional_models:
				print('model ID: %s' % model.ID)
			
		elif isinstance(event, RevisionFail):
			print('revision fail')
			
		elif isinstance(event, AdditModProdFail):
			print('additional model fail')
			
		elif isinstance(event, ExpDesignFail):
			print('experiment design fail')
			
		elif isinstance(event, CheckPointFail):
			print('check point fail')
			print('criterion: %s' % event.criterion)
			
		elif isinstance(event, CheckPointSuccess):
			print('check point success')
			
		elif isinstance(event, RevisedIgnoredUpdate):
			print('revision: only ignored set changed:')
			print('model ID: %s' % event.model.ID)

		else:
			raise TypeError('unknown event: %s' % type(event))

		print('\n')

	print('final models:')
	for model in archive.working_models:
		print('model: %s' % model.ID)
		print("model's accuracy: -%s" % len(model.intermediate_activities ^ archive.model_of_ref.intermediate_activities))
		print([a.ID for a in model.intermediate_activities])


def print_exp_description(exp_des):
	print('experiment type: %s' % type(exp_des.experiment_type))
	for interv in exp_des.interventions:
		print('intervention type: %s' % type(interv))
		if isinstance(interv.condition_or_activity, Activity):
			print('added/removed activity: %s' % interv.condition_or_activity.ID)
		else:
			ent_id = interv.condition_or_activity.entity.ID
			comp_id = interv.condition_or_activity.compartment.ID
			print('added/removed entity: %s; compartment: %s' % (ent_id, comp_id))


def print_exp_results(experiment):
	print('experiment ID: %s' % experiment.ID)
	for res in experiment.results:
		print('result ID: %s' % res.ID)
		print('outcome: %s' % res.outcome)
		print_exp_description(res.exp_description)



# the function below was taken from:
# http://stackoverflow.com/a/20528097/2090840
# made by Paul H
def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to 
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap


#print_not_so_pretty_all_matrices()

archive = read_archive('pickled_archives/archive_2015_3_25_20_48_36_conf05_tc16_r0')
print_development_history(archive)

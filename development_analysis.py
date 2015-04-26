#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

# basic stuff
from archive import InitialModels, InitialResults, ChosenExperiment, NewResults, AcceptedResults, RefutedModels, RevisedModel, UpdatedModelQuality, AdditionalModels, RevisionFail, AdditModProdFail, ExpDesignFail, CheckPointFail, CheckPointSuccess, RevisedIgnoredUpdate, AllModelsEmpiricallyEquivalent, RedundantModel
import pickle
from mnm_repr import Activity, Condition, Add, Remove, Reaction, Transport, ComplexFormation, Expression
from os import listdir
from os.path import isfile, join

# plotting
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot, colors, cm
from mpl_toolkits.axes_grid1 import AxesGrid
from math import ceil
import matplotlib as mtpltlib

# stats
from statistics import mean, pstdev
from scipy import stats


#### whole history

def plot_best_abg_worst():
	folder = 'pickled_archives'
	paths = get_all_paths()
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		full_sequence = get_working_model_sets_throught_development(arch.development_history)
		best = get_sequence_of_best_absolute_difference(arch.model_of_ref, full_sequence)
		avg = get_sequence_of_avg_absolute_difference(arch.model_of_ref, full_sequence)
		worst = get_sequence_of_worst_absolute_difference(arch.model_of_ref, full_sequence)
		plot_sequence(best, 'plots/absolute_difference_%s_best' % path)
		plot_sequence(avg, 'plots/absolute_difference_%s_avg' % path)
		plot_sequence(worst, 'plots/absolute_difference_%s_worst' % path)
		

def plot_sequence(sequence, filename):
	cycles = range(len(sequence))
	plt.plot(cycles, sequence)
	plt.savefig(filename) # , bbox_inches='tight'
	plt.clf()


def plot_all_archives_3_reps():
	# get filename fragments (config + test case info; no repetition info!)
	all_filenames = []
	for tc in range(17):
		for conf in range(36):
			if len(str(conf)) == 1:
				conf_pfx = 'conf0%s_' % conf # one digit
			else:
				conf_pfx = 'conf%s_' % conf # two digit

			if len(str(tc)) == 1:
				tc_pfx = 'tc0%s_' % tc # one digit
			else:
				tc_pfx = 'tc%s_' % tc # two digit

			all_filenames.append("".join([conf_pfx, tc_pfx]))

	# get all files in pickled archives
	all_paths = get_all_paths('pickled_archives')

	# process files
	for file_name_part in all_filenames:
		# find all repetitions (separate files)
		all_3_reps = []
		for file_name in all_paths:
			if file_name[-14:-2] == file_name_part:
				all_3_reps.append(file_name)
		if all_3_reps == []:
			continue
		# get data
		all_3_best = []
		all_3_avg = []
		all_3_worst = []
		all_3_timestamps = []
		for rep_file in all_3_reps:
			arch = read_archive('pickled_archives/%s' % rep_file)
			full_sequence = get_working_model_sets_throught_development(arch.development_history)
			all_3_best.append(get_sequence_of_best_absolute_difference(arch.model_of_ref, full_sequence))
			all_3_avg.append(get_sequence_of_avg_absolute_difference(arch.model_of_ref, full_sequence))
			all_3_worst.append(get_sequence_of_worst_absolute_difference(arch.model_of_ref, full_sequence))
			all_3_timestamps.append(get_timestamps_development(arch.development_history))
		# format best/worst into format suitable for errorbars
		all_3_error_lower = []
		all_3_error_higher = []
		for n in range(3):
			lower_cache = []
			higher_cache = []
			for value in all_3_avg[n]:
				new_low_value = value - all_3_best[n][all_3_avg[n].index(value)]
				lower_cache.append(new_low_value)
				new_high_value = all_3_worst[n][all_3_avg[n].index(value)] - value
				higher_cache.append(new_high_value)
			all_3_error_lower.append(lower_cache)
			all_3_error_higher.append(higher_cache)

		# and plot
#		print(file_name_part)
#		print(all_3_avg)
#		print(all_3_best)
#		print(all_3_worst)
#		print(all_3_timestamps)
#
#		plot_3_sequences(all_3_timestamps, all_3_avg, all_3_error_lower, all_3_error_higher, 'plots/absolute_difference_%s' % file_name_part)

		# printing just difference in %:
		print(file_name_part)
		for n in range(3):
			print('rep %s' % n)
			print('difference: %s' % (all_3_avg[n][0] - all_3_avg[n][-1]))
			difference_in_error = (all_3_avg[n][0] - all_3_avg[n][-1]) / all_3_avg[n][0]
			print('in %% %s' % difference_in_error)
		print('\n')



def plot_3_sequences(Xs, Ys, errors_low, errors_high, filename):
	for n in range(3):
		plt.errorbar(Xs[n], Ys[n], [errors_low[n], errors_high[n]], marker='o')
		plt.savefig("".join([filename, '.svg']))
	plt.clf()



def print_abs_difference_to_the_last_successful_cycle():
	# get filename fragments (config + test case info; no repetition info!)
	all_filenames = []
	for tc in range(17):
		for conf in range(36):
			if len(str(conf)) == 1:
				conf_pfx = 'conf0%s_' % conf # one digit
			else:
				conf_pfx = 'conf%s_' % conf # two digit

			if len(str(tc)) == 1:
				tc_pfx = 'tc0%s_' % tc # one digit
			else:
				tc_pfx = 'tc%s_' % tc # two digit

			all_filenames.append("".join([conf_pfx, tc_pfx]))

	# get all files in pickled archives
	all_paths = get_all_paths()

	# process files
	for file_name_part in all_filenames:
		# find all repetitions (separate files)
		all_3_reps = []
		for file_name in all_paths:
			if file_name[-14:-2] == file_name_part:
				all_3_reps.append(file_name)
		if all_3_reps == []:
			continue
		# get data
		for rep_file in all_3_reps:
			arch = read_archive('pickled_archives/%s' % rep_file)
			print(rep_file)
			get_working_model_event_types(arch.development_history, arch.model_of_ref)
			print('\n\n')



def get_working_model_event_types(dev_history, model_of_ref):
# RedundantModel not included, since these models are not put in the pool of working models anyway
	whole_sequence = []
	events = []
	for event in dev_history:
		if isinstance(event, InitialModels):
			first_set = set(event.models)
			whole_sequence.append(first_set)
			events.append(event)
			break
	# get the rest
	for event in dev_history:
		if isinstance(event, RefutedModels):
			next_set = set(list(whole_sequence[-1])) - set(event.refuted_models)
			if next_set == set([]):
				pass
			else:
				whole_sequence.append(next_set)
				events.append(event)
		elif isinstance(event, RevisedModel):
			next_set = set(list(whole_sequence[-1])) | set(event.revised_models)
			whole_sequence.append(next_set)
			events.append(event)
		elif isinstance(event, AdditionalModels):
			next_set = set(list(whole_sequence[-1])) | set(event.additional_models)
			whole_sequence.append(next_set)
			events.append(event)
		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			whole_sequence.append(set([event.model_left]))
			events.append(event)
		else:
			pass
	# print absolute avg improvement:
	abs_diff_scores_initial = [len(model_of_ref.intermediate_activities ^ m.intermediate_activities) for m in whole_sequence[0]]
	abs_diff_scores_final = [len(model_of_ref.intermediate_activities ^ m.intermediate_activities) for m in whole_sequence[-1]]
	initial_avg = sum(abs_diff_scores_initial)/float(len(abs_diff_scores_initial))
	last_avg = sum(abs_diff_scores_final)/float(len(abs_diff_scores_final))
	improvement = initial_avg - last_avg
	print('initial avg: %s' % initial_avg)
	print('last avg: %s' % last_avg)
	print('total change %s; %s %%' % (improvement, improvement*100/initial_avg))

#	print(events[-1])
	# get indices
	if not (isinstance(events[-1], AdditionalModels) or isinstance(events[-1], AllModelsEmpiricallyEquivalent)):
		print('ended with timeout')
		return None

	for event in events[::-1]:
		if (isinstance(event, AdditionalModels) or isinstance(event, AllModelsEmpiricallyEquivalent)):
			pass
		else:
			break_index = events.index(event)
			break_event = event
			break

	# print absolute avg improvement for proper development and random part:
	abs_diff_scores_at_break_point = [len(model_of_ref.intermediate_activities ^ m.intermediate_activities) for m in whole_sequence[break_index]]
	break_point_avg = sum(abs_diff_scores_at_break_point)/float(len(abs_diff_scores_at_break_point))
	change_up_to = initial_avg - break_point_avg
	change_after = break_point_avg - last_avg
	print('change up to the break point: %s; %s %%' % (change_up_to, change_up_to*100/initial_avg))
	print('change after the break point: %s; %s %%' % (change_after, change_after*100/initial_avg))
	print('break point timestamp: %s' % (break_event.timestamp/60))
	



def get_timestamps_development(dev_history):
	whole_sequence = []
	timestamps = []
	for event in dev_history:
		if isinstance(event, InitialModels):
			first_set = set(event.models)
			whole_sequence.append(first_set)
			timestamps.append(event.timestamp)
			break
	# get the rest
	for event in dev_history:
		if isinstance(event, RefutedModels):
			next_set = set(list(whole_sequence[-1])) - set(event.refuted_models)
			if next_set == set([]):
				pass
			else:
				whole_sequence.append(next_set)
				timestamps.append(event.timestamp)
		elif isinstance(event, RevisedModel):
			next_set = set(list(whole_sequence[-1])) | set(event.revised_models)
			whole_sequence.append(next_set)
			timestamps.append(event.timestamp)
		elif isinstance(event, AdditionalModels):
			next_set = set(list(whole_sequence[-1])) | set(event.additional_models)
			whole_sequence.append(next_set)
			timestamps.append(event.timestamp)
		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			whole_sequence.append(set([event.model_left]))
			timestamps.append(event.timestamp)
		else:
			pass

	minutes = []
	for timestamp in timestamps:
		minutes.append(timestamp/60)

	return minutes



#####


def print_all_avg_and_best_absolute_scores():
	folder = 'pickled_archives'
	paths = get_all_paths()
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		full_sequence = get_working_model_sets_throught_development(arch.development_history)

		best = get_sequence_of_best_absolute_difference(arch.model_of_ref, full_sequence)
		print('best')
		print(best)
		avg = get_sequence_of_avg_absolute_difference(arch.model_of_ref, full_sequence)
		print('avg')
		print(avg)


def get_sequence_of_best_absolute_difference(model_of_ref, sequence_of_working_models):
	ref_activities = model_of_ref.intermediate_activities

	sequence = []
	for model_set in sequence_of_working_models:
		abs_diff_scores = [len(ref_activities ^ m.intermediate_activities) for m in model_set]
		best_score = min(abs_diff_scores)
		sequence.append(best_score)
		
	return sequence


def get_sequence_of_avg_absolute_difference(model_of_ref, sequence_of_working_models):
	ref_activities = model_of_ref.intermediate_activities
	
	sequence = []
	for model_set in sequence_of_working_models:
		abs_diff_scores = [len(ref_activities ^ m.intermediate_activities) for m in model_set]
		avg_score = sum(abs_diff_scores)/float(len(abs_diff_scores))
		sequence.append(avg_score)
		
	return sequence


def get_sequence_of_worst_absolute_difference(model_of_ref, sequence_of_working_models):
	ref_activities = model_of_ref.intermediate_activities
	
	sequence = []
	for model_set in sequence_of_working_models:
		abs_diff_scores = [len(ref_activities ^ m.intermediate_activities) for m in model_set]
		worst_score = max(abs_diff_scores)
		sequence.append(worst_score)
		
	return sequence


def get_working_model_sets_throught_development(dev_history):
# RedundantModel not included, since these models are not put in the pool of working models anyway
	# get first set
	whole_sequence = []
	for event in dev_history:
		if isinstance(event, InitialModels):
			first_set = set(event.models)
			whole_sequence.append(first_set)
			break
	# get the rest
	for event in dev_history:
		if isinstance(event, RefutedModels):
			next_set = set(list(whole_sequence[-1])) - set(event.refuted_models)
			if next_set == set([]):
				pass
			else:
				whole_sequence.append(next_set)
		elif isinstance(event, RevisedModel):
			next_set = set(list(whole_sequence[-1])) | set(event.revised_models)
			whole_sequence.append(next_set)
		elif isinstance(event, AdditionalModels):
			next_set = set(list(whole_sequence[-1])) | set(event.additional_models)
			whole_sequence.append(next_set)
		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			whole_sequence.append(set([event.model_left]))
		else:
			pass

	sequence_of_working_models = whole_sequence # not necessary, but longer name gives more info
	return sequence_of_working_models

####



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
	init_models = get_revised_initial_models(archive.development_history)
	init_scores = [len(model.intermediate_activities ^ ref_activities) for model in init_models]
	# final scores:
	final_scores = [len(model.intermediate_activities ^ ref_activities) for model in archive.working_models]
	return init_scores, final_scores


def get_revised_initial_models(dev_history):
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


def get_all_paths(folder):
#	folder = 'pickled_archives'
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

		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			print('all models empirically equivalent')
			print('remaining model: %s' % event.model_left.ID)
			
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

		elif isinstance(event, RedundantModel):
			print('revision produced redundant model')
			print('base_model ID: %s' % event.base_model.ID)

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


def print_all_histories():
	folder = 'pickled_archives'
	paths = get_all_paths()
	for path in paths:
		print(path)
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		print_development_history(arch)
		print('\n\n\n\n\n\n')


def print_all_exps():
	folder = 'pickled_archives_main' # pickled_archives_just_two_factor pickled_archives
	paths = get_all_paths(folder)
	all_exps = []
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		exps = get_list_of_exps(arch)
		all_exps.append(exps)
		# analyse this list
		print(path)
		exp_stats_analysis(exps)
		print('\n')
	# analyse all exps
	all_exps = [val for sublist in all_exps for val in sublist]
	print("summary:")
	exp_stats_analysis(all_exps)


def get_list_of_exps(archive):
	exps = []
	for event in archive.development_history:
		if isinstance(event, ChosenExperiment):
			exps.append(event.experiment_descriptions[0])
		else:
			pass
	return exps


def exp_stats_analysis(exp_list):
	exps = []
	# get exps descriptions
	for exp_descr in exp_list:
		add_ent = 0
		rem_ent = 0
		add_act = 0
		for interv in exp_descr.interventions:
			if isinstance(interv, Add):
				if isinstance(interv.condition_or_activity, Condition):
					add_ent += 1
				else:
					add_act += 1
			elif isinstance(interv, Remove):
				if isinstance(interv.condition_or_activity, Condition):
					rem_ent += 1
				else:
					raise TypeError("exp_stats_analysis: remove activity!") # unexpected
			else:
				raise TypeError("exp_stats_analysis: not a proper intervetion: %s" % type(interv))
		#  
		exps.append((type(exp_descr.experiment_type), add_ent, rem_ent, add_act))
	# count different types of exps:
	dict_of_exps = {}
	for exp in exps:
		if exp in dict_of_exps.keys():
			dict_of_exps[exp] +=1
		else:
			dict_of_exps[exp] = 1
	# print:
	for exp in dict_of_exps.keys():
		print('%s: %s' % (exp, dict_of_exps[exp]))



def detect_all_import_of_setup():
	folder = 'pickled_archives'
	paths = get_all_paths()
	for path in paths:
		print(path)
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		detect_import_of_setup(arch)
		print('\n\n\n')



def detect_import_of_setup(archive):
	# detects if import activity that imports setup_condition's entity (compartment included) was added to the experiment
	setup_conds = archive.model_of_ref.setup_conditions
	#
	for event in archive.development_history:
		if isinstance(event, ChosenExperiment):
			for description in event.experiment_descriptions:
				for interv in description.interventions:
					if isinstance(interv.condition_or_activity, Activity):
						activity = interv.condition_or_activity.required_conditions
						common_species = activity & setup_conds
						if len(common_species) > 0:
							print(common_species)
							print_exp_description(description)
						else:
							pass
					else:
						pass
		else:
			pass



def plotting_all_with_drifts():
	folder = 'pickled_archives_addit_runs'
	paths = get_all_paths(folder)
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
#		print(path)
#		print(arch.development_history)
#		print('\n\n')
		Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift = plot_with_drifts(arch)
		plot_with_drift_lines(Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift, path[-14:])


def plot_with_drifts(arch):
	X_sequences_dev = []
	X_sequences_drift = []
	Y_sequences_dev = []
	Y_sequences_drift = []

	event_sequence_cache = []
	models_sequence_cache = []
	models_cache = set([])
	flag_drift = False

	for event in arch.development_history:
		if isinstance(event, CheckPointSuccess): # save and clear cache
			event_sequence_cache.append(event)
			models_sequence_cache.append(models_cache)

		elif isinstance(event, CheckPointFail): # save and clear cache; end
			event_sequence_cache.append(event)
			models_sequence_cache.append(models_cache)
			if flag_drift == False:
				X_sequences_dev.append(event_sequence_cache)
				Y_sequences_dev.append(models_sequence_cache)
			else:
				X_sequences_drift.append(event_sequence_cache)
				Y_sequences_drift.append(models_sequence_cache)
			break

		elif isinstance(event, AllModelsEmpiricallyEquivalent): # start drift, modifies cache set
			if flag_drift == False:
				X_sequences_dev.append(event_sequence_cache)
				Y_sequences_dev.append(models_sequence_cache)
				event_sequence_cache = []
				models_sequence_cache = []
				flag_drift = True
				models_cache = set([event.model_left])####
			else:
				models_cache = set([event.model_left])####


		elif isinstance(event, ChosenExperiment): # ends drift
			if flag_drift == False:
				pass
			else:
				X_sequences_drift.append(event_sequence_cache)
				Y_sequences_drift.append(models_sequence_cache)
				event_sequence_cache = []
				models_sequence_cache = []
				flag_drift = False

		elif isinstance(event, RefutedModels):
			models_cache = models_cache - set(event.refuted_models)

		elif isinstance(event, RevisedModel):
			models_cache = models_cache | set(event.revised_models)

		elif isinstance(event, AdditionalModels):
			models_cache = models_cache | set(event.additional_models)

		elif isinstance(event, InitialModels):
			models_cache = models_cache | set(event.models)
			event_sequence_cache.append(event)
			models_sequence_cache.append(models_cache)

		else:
			pass

	# timeout
	if not (isinstance(arch.development_history[-1], CheckPointFail) or isinstance(arch.development_history[-2], CheckPointFail)):
		event_sequence_cache.append(arch.development_history[-1]) # the last one
		models_sequence_cache.append(models_cache)
		if flag_drift == False:
			X_sequences_dev.append(event_sequence_cache)
			Y_sequences_dev.append(models_sequence_cache)
		else:
			X_sequences_drift.append(event_sequence_cache)
			Y_sequences_drift.append(models_sequence_cache)

	# preprocess data
	r = arch.model_of_ref.intermediate_activities
	Y_sequences_dev = [[[len(r^m.intermediate_activities) for m in st] for st in sequence] for sequence in Y_sequences_dev]
	Y_sequences_dev = [[sum(st)/len(st) for st in sequence] for sequence in Y_sequences_dev]
	X_sequences_dev = [[event.timestamp/60 for event in sequence] for sequence in X_sequences_dev]

	Y_sequences_drift = [[[len(r^m.intermediate_activities) for m in st] for st in sequence] for sequence in Y_sequences_drift]
	Y_sequences_drift = [[sum(st)/len(st) for st in sequence] for sequence in Y_sequences_drift]
	X_sequences_drift = [[event.timestamp/60 for event in sequence] for sequence in X_sequences_drift]


	return Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift

#	print(sum([len(s) for s in X_sequences_dev]) + sum([len(s) for s in X_sequences_drift]))
#	print(len([x for x in arch.development_history if isinstance(x, CheckPointSuccess)]))
#	print(len([x for x in arch.development_history if isinstance(x, CheckPointFail)]))

#	print(X_sequences_dev)
#	print(Y_sequences_dev)
#	print(X_sequences_drift)
#	print(Y_sequences_drift)


def plot_with_drift_lines(Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift, path):
	# filling in connections
	X_connections_green = []
	Y_connections_green = []
	X_connections_grey = []
	Y_connections_grey = []

	for x_sequence, y_sequence in zip(X_sequences_dev[1:], Y_sequences_dev[1:]):
		connection_x = [x_sequence[0]]
		connection_y = [y_sequence[0]]
		try:
			connection_x.append(X_sequences_drift[X_sequences_dev.index(x_sequence)-1][-1])
			connection_y.append(Y_sequences_drift[X_sequences_dev.index(x_sequence)-1][-1])
			X_connections_green = [connection_x] + X_connections_green
			Y_connections_green = [connection_y] + Y_connections_green
		except:
			pass

	for x_sequence, y_sequence in zip(X_sequences_drift, Y_sequences_drift):
		connection_x = [x_sequence[0]]
		connection_y = [y_sequence[0]]
		try:
			connection_x.append(X_sequences_dev[X_sequences_drift.index(x_sequence)][-1])
			connection_y.append(Y_sequences_dev[X_sequences_drift.index(x_sequence)][-1])
			X_connections_grey = [connection_x] + X_connections_grey
			Y_connections_grey = [connection_y] + Y_connections_grey
		except:
			pass

	# plotting
	for x, y in zip(X_connections_green, Y_connections_green):
		plt.plot(x, y, color='green')
	for x, y in zip(X_connections_grey, Y_connections_grey):
	    plt.plot(x, y, color='grey')

	for x, y in zip(X_sequences_dev, Y_sequences_dev):
		plt.plot(x, y, color='green', marker='.')
	for x, y in zip(X_sequences_drift, Y_sequences_drift):
	    plt.plot(x, y, color='grey', marker='.')

	plt.savefig("".join(['plots/', path, '.svg']))
	plt.clf()



def analyse_all_development_and_drift():
	folder = 'pickled_archives_just_two_factor' # pickled_archives pickled_archives_just_two_factor pickled_archives_addit_runs
	paths = get_all_paths(folder)

	paths.sort(key = lambda x: x.split('conf05_')[1])

	results_collection = {}

	for path in paths: #paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
		# tests: test_dev_drift_totals, test_drifting_useful, test_last_drifting_useful
		before_drift, tot_dev, tot_drft, prop_dev, last_drift, t_dev_drift, t_drift, t_last_drift = analyse_development_and_drift_one_run(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift)
		initial_err = Y_sq_dev[0][0]
		if tot_drft != None:
			total_decrease = -(tot_dev + tot_drft)
		else:
			total_decrease = -tot_dev
		total_decrease_perc = total_decrease/initial_err
		tot_dev_perc = -(tot_dev/initial_err)
		if tot_drft != None:
			tot_drft_perc = -(tot_drft/initial_err)
		else:
			tot_drft_perc = None
		before_drift_perc = -(before_drift/initial_err)
		#
		print(path)
		print('initial error %s' % initial_err)
		print('total improvement %s' % total_decrease)
		print('total improvement (%%) %s' % total_decrease_perc)
		print('')
		print('total development (%%): %s' % tot_dev_perc)
		print('total drift (%%): %s' % tot_drft_perc)
		print('')
		print('before first drift (%%): %s' % before_drift_perc)

		if prop_dev != None:
			prop_dev_perc = -(prop_dev/initial_err)
			last_drift_perc = -(last_drift/initial_err)
			print('up to final drift (%%): %s' % prop_dev_perc)
			print('final drift (%%): %s' % last_drift_perc)
		else:
			prop_dev_perc = None
			last_drift_perc = None
			print('up to final drift (%%): N/A')
			print('final drift (%%): N/A')
		print('\n\n')

		if prop_dev != None:
			results_dict = {'tot_impr_prc':total_decrease_perc, 'tot_dev_prc':tot_dev_perc, 'tot_drft_prc':tot_drft_perc,
						'before_first_drft':before_drift_perc, 'after_first_drift_no_last_drift':prop_dev_perc,
						'up_to_final_drft':prop_dev_perc, 'final_drft':last_drift_perc,
						'test_dev_drift_totals':t_dev_drift, 'test_drifting_useful':t_drift, 'test_last_drifting_useful':t_last_drift}
		#'test_dev_drift_totals', 'test_drifting_useful', 'test_last_drifting_useful'
		else:
			results_dict = {'tot_impr_prc':total_decrease_perc, 'tot_dev_prc':tot_dev_perc, 'tot_drft_prc':tot_drft_perc,
						'before_first_drft':before_drift_perc, 'after_first_drift_no_last_drift':total_decrease_perc, 
						'up_to_final_drft':prop_dev_perc, 'final_drft':last_drift_perc,
						'test_dev_drift_totals':t_dev_drift, 'test_drifting_useful':t_drift, 'test_last_drifting_useful':t_last_drift}

		if path[-7:-3] in results_collection.keys():
			results_collection[path[-7:-3]].append(results_dict)
		else:
			results_collection[path[-7:-3]] = [results_dict]

	global_total_decrease_perc = []
	global_tot_dev_perc = []
	global_tot_drft_perc = []
	global_before_drift_perc = []
	global_after_drift_perc = []
	global_prop_dev_perc = []
	global_last_drift_perc = []
	global_test_dev_drift_totals = []
	global_test_drifting_useful = []
	global_test_last_drifting_useful = []

	for test_case in sorted(list(results_collection.keys())):
		total_decrease_perc = [x['tot_impr_prc'] for x in results_collection[test_case]]
		global_total_decrease_perc.extend(total_decrease_perc)
		tot_dev_perc = [x['tot_dev_prc'] for x in results_collection[test_case]]
		global_tot_dev_perc.extend(tot_dev_perc)
		tot_drft_perc = [x['tot_drft_prc'] for x in results_collection[test_case] if x['tot_drft_prc'] != None]
		global_tot_drft_perc.extend(tot_drft_perc)
		before_drift_perc = [x['before_first_drft'] for x in results_collection[test_case]]
		global_before_drift_perc.extend(before_drift_perc)
		after_drift_perc = [x['after_first_drift_no_last_drift'] for x in results_collection[test_case]]
		global_after_drift_perc.extend(after_drift_perc)
		prop_dev_perc = [x['up_to_final_drft'] for x in results_collection[test_case] if x['up_to_final_drft'] != None]
		global_prop_dev_perc.extend(prop_dev_perc)
		last_drift_perc = [x['final_drft'] for x in results_collection[test_case] if x['final_drft'] != None]
		global_last_drift_perc.extend(last_drift_perc)
		# tests:
		global_test_dev_drift_totals.extend([x['test_dev_drift_totals'] for x in results_collection[test_case] if x['test_dev_drift_totals'] != None])
		global_test_drifting_useful.extend([x['test_drifting_useful'] for x in results_collection[test_case] if x['test_drifting_useful'] != None])
		global_test_last_drifting_useful.extend([x['test_last_drifting_useful'] for x in results_collection[test_case] if x['test_last_drifting_useful'] != None])
		# analysis for this problem:
		print(test_case)
		print('total improvement')
		print('mean: %s' % mean(total_decrease_perc))
		print('population std dev: %s' % pstdev(total_decrease_perc))
		print('\n')
		print('improvement during development')
		print('mean: %s' % mean(tot_dev_perc))
		print('population std dev: %s' % pstdev(tot_dev_perc))
		print('improvement during random drift')
		print('mean: %s' % mean(tot_drft_perc))
		print('population std dev: %s' % pstdev(tot_drft_perc))
		print('\n')
		print('improvement before first drift')
		print('mean: %s' % mean(before_drift_perc))
		print('population std dev: %s' % pstdev(before_drift_perc))
		print('improvement w/o the final drift (or total improvement, if no drift / doesnt end in drift)')
		print('mean: %s' % mean(after_drift_perc))
		print('population std dev: %s' % pstdev(after_drift_perc))
		print('\n')
		print('improvement up to final drift')
		print('mean: %s' % mean(prop_dev_perc))
		print('population std dev: %s' % pstdev(prop_dev_perc))
		print('improvement during the last drift')
		print('mean: %s' % mean(last_drift_perc))
		print('population std dev: %s' % pstdev(last_drift_perc))
		print('\n\n')

	print('GLOBAL:')
	print('total improvement')
	print('mean: %s' % mean(global_total_decrease_perc))
	print('population std dev: %s' % pstdev(global_total_decrease_perc))
	print('')
	print('improvement during development')
	print('mean: %s' % mean(global_tot_dev_perc))
	print('population std dev: %s' % pstdev(global_tot_dev_perc))
	print('improvement during random drift')
	print('mean: %s' % mean(global_tot_drft_perc))
	print('population std dev: %s' % pstdev(global_tot_drft_perc))
	print('')
	print('improvement before first drift')
	print('mean: %s' % mean(global_before_drift_perc))
	print('population std dev: %s' % pstdev(global_before_drift_perc))
	print('improvement w/o the final drift (or total improvement, if no drift / doesnt end in drift)')
	print('mean: %s' % mean(global_after_drift_perc))
	print('population std dev: %s' % pstdev(global_after_drift_perc))
	print('')
	print('improvement up to final drift')
	print('mean: %s' % mean(global_prop_dev_perc))
	print('population std dev: %s' % pstdev(global_prop_dev_perc))
	print('improvement during the last drift')
	print('mean: %s' % mean(global_last_drift_perc))
	print('population std dev: %s' % pstdev(global_last_drift_perc))
	print('\n\n')
	print('test: is development better than drifting (total)?')
	successes = 0
	failures = 0
	for result in global_test_dev_drift_totals:
		if result == True:
			successes += 1
		else:
			failures += 1
	print('successes: %s' % successes)
	print('failures: %s' % failures)
	print('p-value: %s' % stats.binom_test([successes, failures]))
	print('')
	#
	print('test: is drifting useful?')
	successes = 0
	failures = 0
	for result in global_test_drifting_useful:
		if result == True:
			successes += 1
		else:
			failures += 1
	print('successes: %s' % successes)
	print('failures: %s' % failures)
	print('p-value: %s' % stats.binom_test([successes, failures]))
	print('')
	#
	print('is last drifting useful?')
	successes = 0
	failures = 0
	for result in global_test_last_drifting_useful:
		if result == True:
			successes += 1
		else:
			failures += 1
	print('successes: %s' % successes)
	print('failures: %s' % failures)
	print('p-value: %s' % stats.binom_test([successes, failures]))
	print('\n\n')



	print('global_total_decrease_perc: %s %s' % (len(global_total_decrease_perc), global_total_decrease_perc))
	print('global_prop_dev_perc: %s %s' % (len(global_prop_dev_perc), global_prop_dev_perc))


def analyse_development_and_drift_one_run(Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift):
	# filling in connections
	X_connections_green = []
	Y_connections_green = []
	X_connections_grey = []
	Y_connections_grey = []

	for x_sequence, y_sequence in zip(X_sequences_dev[1:], Y_sequences_dev[1:]):
		connection_x = [x_sequence[0]]
		connection_y = [y_sequence[0]]
		try:
			connection_x = [X_sequences_drift[X_sequences_dev.index(x_sequence)-1][-1]] + connection_x
			connection_y = [Y_sequences_drift[X_sequences_dev.index(x_sequence)-1][-1]] + connection_y
			X_connections_green.append(connection_x)
			Y_connections_green.append(connection_y)
		except:
			pass

	for x_sequence, y_sequence in zip(X_sequences_drift, Y_sequences_drift):
		connection_x = [x_sequence[0]]
		connection_y = [y_sequence[0]]
		try:
			connection_x = [X_sequences_dev[X_sequences_drift.index(x_sequence)][-1]] + connection_x
			connection_y = [Y_sequences_dev[X_sequences_drift.index(x_sequence)][-1]] + connection_y
			X_connections_grey.append(connection_x)
			Y_connections_grey.append(connection_y)
		except:
			pass


	# change before the first drift:
	change_before_first_drift = Y_sequences_dev[0][-1] - Y_sequences_dev[0][0]

	# total development vs. total drift analysis:
	# dev
	total_dev_change = 0.0
	for sequence in Y_sequences_dev + Y_connections_green:
		total_dev_change += (sequence[-1] - sequence[0])
	# drift
	if len(Y_sequences_drift + Y_connections_grey) > 0:
		total_drift_change = 0.0
		for sequence in Y_sequences_drift + Y_connections_grey:
			total_drift_change += (sequence[-1] - sequence[0])
			test_dev_drift_totals = (-total_dev_change) > (-total_drift_change) # test
	else:
		total_drift_change = None
		test_dev_drift_totals = None # test

	# development vs. last drift analysis:
	if len(Y_sequences_drift + Y_connections_grey) == 0: # no drift
		return change_before_first_drift, total_dev_change, total_drift_change, None, None, test_dev_drift_totals, None, None
	# ended during development (no last drift)
	if ((X_sequences_dev[-1][-1] > X_sequences_drift[-1][-1]) and (X_sequences_dev[-1][-1] > Y_connections_grey[-1][-1])):
		test_drifting_useful = (-change_before_first_drift) < (-(total_dev_change+total_drift_change)) # version if dev process DIDN'T end with drift
		return change_before_first_drift, total_dev_change, total_drift_change, None, None, test_dev_drift_totals, test_drifting_useful, None
	# change without last drift:
	change_up_to_last_drift = 0.0
	for sequence in Y_sequences_dev + Y_connections_green + Y_sequences_drift[:-1] + Y_connections_grey[:-1]:
		change_up_to_last_drift += (sequence[-1] - sequence[0])
	# change during last drift:
	change_during_last_drift = Y_sequences_drift[-1][-1] - Y_connections_grey[-1][0]

	# tests
	test_drifting_useful = (-change_before_first_drift) < (-change_up_to_last_drift) # version if dev process ended with drift
	test_last_drifting_useful = (-change_up_to_last_drift) < (-(total_dev_change+total_drift_change))

	return change_before_first_drift, total_dev_change, total_drift_change, change_up_to_last_drift, change_during_last_drift, test_dev_drift_totals, test_drifting_useful, test_last_drifting_useful






def print_all_revisions():
	folder = 'pickled_archives_main' # pickled_archives_just_two_factor pickled_archives
	paths = get_all_paths(folder)
	all_revs = []
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		revs = get_list_of_revisions(arch)
		all_revs.extend(revs)
		# analyse this list
#		print(path)
#		rev_data = get_revision_data(revs)
#		analyse_revision(rev_data)
#		print('\n')
	# analyse all exps
	print("summary:")
	rev_data = get_revision_data(all_revs)
#	analyse_revision(rev_data)
	print('')
	# some additional analysis
	additional_revision_analysis(rev_data)



def additional_revision_analysis(rev_data):
	# number of revisions with:
	# total:
	total = len(rev_data)
	print('total number: %s' % total)
	# changes in more than expression:
	not_only_expression = len([x for x in rev_data if (x[0] != 0 or x[1] != 0 or x[2] != 0 or x[4] != 0 or x[5] != 0 or x[6] != 0)])
	print('not only expression: %s' % not_only_expression)
	# something removed:
	sth_removed = len([x for x in rev_data if (x[4] != 0 or x[5] != 0 or x[6] != 0 or x[7] != 0) ])
	print('with sth removed: %s' % sth_removed)
	# more than one change:
	more_than_one = len([x for x in rev_data if (sum(x) > 1)])
	print('more than one change: %s' % more_than_one)
	# removal and additions combined:
	removal_and_add = len([x for x in rev_data if ((x[0] != 0 or x[1] != 0 or x[2] != 0 or x[3] != 0) and (x[4] != 0 or x[5] != 0 or x[6] != 0 or x[7] != 0))])
	print('removal and addition: %s' % removal_and_add)
	#
	# data for histogram: number of revisions with a given number of changes:
	histo_dict_all = [sum(x) for x in rev_data]
	histo_dict_add = tuple([sum(x[0:4]) for x in rev_data])
	histo_dict_rem = tuple([sum(x[4:]) for x in rev_data])

	for data in [histo_dict_add, histo_dict_rem]:
		mtpltlib.rcParams.update({'font.size': 18})
		bins_dict = {histo_dict_add:21, histo_dict_rem:7}
		label_dict = {histo_dict_add:'additions', histo_dict_rem:'removals'}
		bins = np.histogram(np.hstack((histo_dict_all, data)), bins=30)[1] #get the bin edges
		plt.hist(histo_dict_all, bins=bins, log=True, histtype='stepfilled', color='b', label='all changes')
		plt.hist(data, bins=bins, log=True, histtype='stepfilled', color='r', alpha=0.5, label=label_dict[data])

#		plt.title("model revisions")
		plt.xlabel("nb. of changes")
		plt.ylabel("nb. of revisions")
		plt.legend()
		plt.savefig('revision_hist_%s.svg' % label_dict[data])
		plt.clf()


def analyse_revision(rev_data):
	# count different configurations of revisions:
	dict_of_revs = {}
	for rev in rev_data:
		if rev in dict_of_revs.keys():
			dict_of_revs[rev] +=1
		else:
			dict_of_revs[rev] = 1
	# print:
	for rev in dict_of_revs.keys():
		print('%s: %s' % (rev, dict_of_revs[rev]))



def get_list_of_revisions(archive):
	rev = []
	for event in archive.development_history:
		if isinstance(event, RevisedModel):
			rev.append(event)
		else:
			pass
	return rev


def get_revision_data(events_list):
	rev_for_all_events = []
	for event in events_list:
		for model in event.revised_models:
			added_reactions = 0
			added_transport = 0
			added_complex_formation = 0
			added_expression = 0
			removed_reactions = 0
			removed_transport = 0
			removed_complex_formation = 0
			removed_expression = 0
			difference_added = set(model.intermediate_activities) - set(event.old_model.intermediate_activities)
			difference_removed = set(event.old_model.intermediate_activities) - set(model.intermediate_activities)
			for act in difference_added:
				if isinstance(act, Reaction):
					added_reactions += 1
				elif isinstance(act, Transport):
					added_transport += 1
				elif isinstance(act, ComplexFormation):
					added_complex_formation += 1
				elif isinstance(act, Expression):
					added_expression += 1
				else:
					raise TypeError("analyse_revision: activity type not recognised: type(act)")
			for act in difference_removed:
				if isinstance(act, Reaction):
					removed_reactions += 1
				elif isinstance(act, Transport):
					removed_transport += 1
				elif isinstance(act, ComplexFormation):
					removed_complex_formation += 1
				elif isinstance(act, Expression):
					removed_expression += 1
				else:
					raise TypeError("analyse_revision: activity type not recognised: type(act)")

			rev_for_all_events.append((added_reactions, added_transport, added_complex_formation, 
				added_expression, removed_reactions, removed_transport, removed_complex_formation, removed_expression))

	return rev_for_all_events



#plotting_all_with_drifts()
#analyse_all_development_and_drift()
print_all_revisions()


#print_abs_difference_to_the_last_successful_cycle()
#print_all_histories()
#print_all_exps()
#detect_all_import_of_setup()
#print_all_avg_and_best_absolute_scores()
#plot_best_abg_worst()
#plot_all_archives_3_reps()

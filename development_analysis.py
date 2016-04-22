#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

# basic stuff
from archive import InitialModels, InitialResults, ChosenExperiment, NewResults, AcceptedResults, RefutedModels, RevisedModel, UpdatedModelQuality, AdditionalModels, RevisionFail, AdditModProdFail, ExpDesignFail, CheckPointFail, CheckPointSuccess, RevisedIgnoredUpdate, AllModelsEmpiricallyEquivalent, RedundantModel
import pickle
import re
from mnm_repr import Activity, Condition, Add, Remove, Reaction, Transport, ComplexFormation, Expression, Growth
from mnm_repr import Gene, Metabolite
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


def read_archive(path):
	pkl_file = open(path, 'rb')
	archive = pickle.load(pkl_file)
	pkl_file.close()
	return archive

def get_all_paths(folder):
	# filters out subdirectories
	return [file_ for file_ in listdir(folder) if isfile(join(folder,file_))]

#
# development history analysis
#
def print_all_histories():
	folder = 'pickled_archives'
	paths = get_all_paths()
	for path in paths:
		print(path)
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		print_development_history(arch)
		print('\n\n\n\n\n\n')

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

#
# plotting
#
def plotting_all_with_drifts(folder):
	paths = get_all_paths(folder)
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift = plot_with_drifts(arch)
		plot_with_drift_lines(Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift, folder, path[-14:])

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
		# save and clear cache
		if isinstance(event, CheckPointSuccess):
			event_sequence_cache.append(event)
			models_sequence_cache.append(models_cache)

		# save and clear cache; end
		elif isinstance(event, CheckPointFail):
			event_sequence_cache.append(event)
			models_sequence_cache.append(models_cache)
			if flag_drift == False:
				X_sequences_dev.append(event_sequence_cache)
				Y_sequences_dev.append(models_sequence_cache)
			else:
				X_sequences_drift.append(event_sequence_cache)
				Y_sequences_drift.append(models_sequence_cache)
			break

		# start drift, modifies cache set
		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			if flag_drift == False:
				X_sequences_dev.append(event_sequence_cache)
				Y_sequences_dev.append(models_sequence_cache)
				event_sequence_cache = []
				models_sequence_cache = []
				flag_drift = True
				models_cache = set([event.model_left])
			else:
				models_cache = set([event.model_left])

		# ends drift
		elif isinstance(event, ChosenExperiment):
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
		# the last one
		event_sequence_cache.append(arch.development_history[-1])
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

def plot_with_drift_lines(Y_sequences_dev, X_sequences_dev, Y_sequences_drift, X_sequences_drift, folder, path):
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

	plt.ylim(ymin=0)

	plt.savefig("".join([folder, '/', path, '.svg']))
	plt.clf()


def plot_simple(x, y, folder, path):
	plt.plot(x, y, color='blue', marker='.')
	plt.plot([x[0], x[-1]],[0,0], color='red')
	plt.savefig("".join([folder, '/', path[-14:], '.svg']))
	plt.clf()

def simple_scatter(x, y, folder):
	plt.scatter(x, y)
	plt.xlim(xmin=0)
	neg_y = [True for nb in y if nb < 0]

	if len(neg_y) == 0:
		plt.ylim(ymin=0)

	plt.savefig("".join(['./', folder, '.svg']))
	plt.clf()

def plot_three_noise_comparisons(tpls, tc):
	colours = {0:'r', 1:'g', 2:'b'}
	diffs = {0:'vs0_30', 1:'vs30_60', 2:'vs0_60'}
	counter = 0
	for tpl in tpls:
		assert len(tpl[0]) == len(tpl[1]), 'mean and std dev not the same lenght'
		# calculating std dev lines:
		y1 = [x[0] - x[1] for x in zip(tpl[0], tpl[1])]#
		y2 = [x[0] + x[1] for x in zip(tpl[0], tpl[1])]#
		#
		plot_fill(y1, y2, colours[counter], diffs[counter])
		counter += 1
	p1 = plt.Rectangle((0, 0), 1, 1, fc=colours[0], alpha=.5)
	p2 = plt.Rectangle((0, 0), 1, 1, fc=colours[1], alpha=.5)
	p3 = plt.Rectangle((0, 0), 1, 1, fc=colours[2], alpha=.5)

	plt.legend([p1, p2, p3], [diffs[0], diffs[1], diffs[2]])
	plt.grid(True)
	plt.savefig('./tc_%s.svg' % tc)
	plt.clf()

def plot_fill(y1, y2, colour, what_is_it):
	# assumes y1 and y2 are of equal lenght
	x = [a for a in range(len(y1))]
	plt.fill_between(x, y1, y2, facecolor=colour, alpha=.5)
	# fill_between doesn't support legends


#
# model development analysis
#
def analyse_all_development_and_drift(folder):
	paths = get_all_paths(folder)

	paths.sort(key = lambda x: re.split('conf.._', x)[1])

	results_collection = {}

	for path in paths:
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

		else:
			results_dict = {'tot_impr_prc':total_decrease_perc, 'tot_dev_prc':tot_dev_perc, 'tot_drft_prc':tot_drft_perc,
						'before_first_drft':before_drift_perc, 'after_first_drift_no_last_drift':total_decrease_perc,
						'up_to_final_drft':total_decrease_perc, 'final_drft':last_drift_perc,
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
		# there is no None: proper dev is then total
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
		if len(tot_drft_perc) == 0:
			print('mean: N/A')
			print('population std dev: N/A')
		else:
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
		if len(prop_dev_perc) == 0:
			print('mean: N/A')
			print('population std dev: N/A')
		else:
			print('mean: %s' % mean(prop_dev_perc))
			print('population std dev: %s' % pstdev(prop_dev_perc))
		print('improvement during the last drift')
		if len(last_drift_perc) == 0:
			print('mean: N/A')
			print('population std dev: N/A')
		else:
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
	# connections from the end of drifts
	# to the beginning of devs are green (included in dev)
	# connections from end of devs
	# to begining of drifts are grey (included in drift)
	X_connections_green = []
	Y_connections_green = []
	X_connections_grey = []
	Y_connections_grey = []
	# ends of drifts, beginnings of devs
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
	# ends of devs, beginnings of drifts
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

	# CHANGE IN MODELS' ERROR: negative => improvement!
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
	# no drift (checking Y_sequences_drift would do, but hey)
	if len(Y_sequences_drift + Y_connections_grey) == 0:
		return change_before_first_drift, total_dev_change, total_drift_change, None, None, test_dev_drift_totals, None, None
	# ended during development (no last drift)
	# and (X_sequences_dev[-1][-1] > Y_connections_grey[-1][-1])) WTF???
	if (X_sequences_dev[-1][-1] > X_sequences_drift[-1][-1]):
		# version if dev process DIDN'T end with drift
		test_drifting_useful = (-change_before_first_drift) < (-(total_dev_change+total_drift_change))
		return change_before_first_drift, total_dev_change, total_drift_change, None, None, test_dev_drift_totals, test_drifting_useful, None
	# change without last drift:
	change_up_to_last_drift = 0.0
	for sequence in Y_sequences_dev + Y_connections_green + Y_sequences_drift[:-1] + Y_connections_grey[:-1]:
		change_up_to_last_drift += (sequence[-1] - sequence[0])
	# change during last drift:
	change_during_last_drift = Y_sequences_drift[-1][-1] - Y_connections_grey[-1][0]

	# tests
	# version if dev process ended with drift
	test_drifting_useful = (-change_before_first_drift) < (-change_up_to_last_drift)
	test_last_drifting_useful = (-change_up_to_last_drift) < (-(total_dev_change+total_drift_change))

	return change_before_first_drift, total_dev_change, total_drift_change, change_up_to_last_drift, change_during_last_drift, test_dev_drift_totals, test_drifting_useful, test_last_drifting_useful

#
# experiments analysis
#
def experiment_analysis(list_of_folders, print_single_sims=False):
	all_exps = []
	for folder in list_of_folders:
		# tpl = exps, path
		for tpl in get_exps_one_folder(folder):
			all_exps.extend(tpl[0])
			if print_single_sims:
				print(folder)
				print(tpl[1])
				# will print
				exp_stats_analysis(tpl[0])
				print('')
			else:
				pass
	# will print
	exp_stats_analysis(all_exps)

def get_exps_one_folder(folder):
	paths = get_all_paths(folder)
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		exps = get_list_of_exps(arch)
		yield exps, path

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
		rem_gene = 0
		rem_nutrient = 0
		add_act = 0
		for interv in exp_descr.interventions:
			if isinstance(interv, Add):
				if isinstance(interv.condition_or_activity, Condition):
					add_ent += 1
				else:
					add_act += 1
			elif isinstance(interv, Remove):
				if isinstance(interv.condition_or_activity, Condition):
					if isinstance(interv.condition_or_activity.entity, Gene):
						rem_gene += 1
					elif isinstance(interv.condition_or_activity.entity, Metabolite):
						rem_nutrient += 1
					else:
						raise TypeError("exp_stats_analysis: removed neither gene not metabolite?")
				else:
					# unexpected
					raise TypeError("exp_stats_analysis: remove activity! %s" % interv.condition_or_activity)
			else:
				raise TypeError("exp_stats_analysis: not a proper intervetion: %s" % type(interv))
		#
		exps.append((type(exp_descr.experiment_type), add_ent, rem_gene, rem_nutrient, add_act))
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

#
# revision analysis:
#
def revision_analysis(list_of_folders):
	all_revs = []
	for folder in list_of_folders:
		all_revs.extend(get_all_revisions(folder))
	rev_data = get_revision_data(all_revs)
	print_revision_configurations(rev_data)
	revisions_stats(rev_data)
	changes_stats(rev_data)
	plot_histogram_revision_distribution(rev_data)

def get_all_revisions(folder):
	paths = get_all_paths(folder)
	all_revs = []
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		revs = get_list_of_revisions(arch)
		all_revs.extend(revs)
	return all_revs

def changes_stats(rev_data):
	total_changes = sum(sum(x) for x in rev_data)
	added_reactions = sum(x[0] for x in rev_data)
	added_transport = sum(x[1] for x in rev_data)
	added_complex_formation = sum(x[2] for x in rev_data)
	added_expression = sum(x[3] for x in rev_data)
	removed_reactions = sum(x[4] for x in rev_data)
	removed_transport = sum(x[5] for x in rev_data)
	removed_complex_formation = sum(x[6] for x in rev_data)
	removed_expression = sum(x[7] for x in rev_data)
	print('total number of changes: %s' % total_changes)
	print('added reactions: %s' % added_reactions)
	print('added transport: %s' % added_transport)
	print('added complex formation: %s' % added_complex_formation)
	print('added expression: %s' % added_expression)
	print('removed reactions: %s' % removed_reactions)
	print('removed transport: %s' % removed_transport)
	print('removed complex formation %s' % removed_complex_formation)
	print('removed expression: %s' % removed_expression)

def revisions_stats(rev_data):
	# total number of revisions
	total_revisions = len(rev_data)
	print('total number of revisions: %s' % total_revisions)
	# number of revisions with:
	# changes in more than expression:
	not_only_expression = len([x for x in rev_data if (x[0] != 0 or x[1] != 0 or x[2] != 0 or x[4] != 0 or x[5] != 0 or x[6] != 0)])
	print('not only expression: %s' % not_only_expression)
	# something added:
	sth_added = len([x for x in rev_data if (x[0] != 0 or x[1] != 0 or x[2] != 0 or x[3] != 0)])
	print('with sth added: %s' % sth_added)
	# something removed:
	sth_removed = len([x for x in rev_data if (x[4] != 0 or x[5] != 0 or x[6] != 0 or x[7] != 0) ])
	print('with sth removed: %s' % sth_removed)
	# more than one change:
	more_than_one = len([x for x in rev_data if (sum(x) > 1)])
	print('more than one change: %s' % more_than_one)
	# removal and additions combined:
	removal_and_add = len([x for x in rev_data if ((x[0] != 0 or x[1] != 0 or x[2] != 0 or x[3] != 0) and (x[4] != 0 or x[5] != 0 or x[6] != 0 or x[7] != 0))])
	print('removal and addition: %s' % removal_and_add)

def plot_histogram_revision_distribution(rev_data):
	# data for histogram: number of revisions with a given number of changes:
	# need the '!= 0' check because growth was added/removed a few times
	# due to a bug (it shouldn't be possible actually)
	histo_dict_all = [sum(x) for x in rev_data if sum(x) != 0]
	histo_dict_add = tuple([sum(x[0:4]) for x in rev_data if sum(x) != 0])
	histo_dict_rem = tuple([sum(x[4:]) for x in rev_data if sum(x) != 0])
	print("all:\n")
	print(histo_dict_all)
	print("additions:\n")
	print(histo_dict_add)
	print("subtractions:\n")
	print(histo_dict_rem)

	for data in [histo_dict_add, histo_dict_rem]:
		mtpltlib.rcParams.update({'font.size': 18})
		bins_dict = {histo_dict_add:21, histo_dict_rem:7}
		label_dict = {histo_dict_add:'additions', histo_dict_rem:'subtractions'}
		bins = np.histogram(np.hstack((histo_dict_all, data)), bins=28)[1] #get the bin edges
		plt.hist(histo_dict_all, bins=bins, log=True, histtype='stepfilled', color='b', label='all changes')
		plt.hist(data, bins=bins, log=True, histtype='stepfilled', color='r', alpha=0.5, label=label_dict[data])

#		plt.title("model revisions")
		plt.xlabel("nb. of changes")
		plt.ylabel("nb. of revisions")
		plt.legend()
		plt.savefig('revision_hist_%s.svg' % label_dict[data])
		plt.clf()

def print_revision_configurations(rev_data):
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
			added_growth = 0
			removed_reactions = 0
			removed_transport = 0
			removed_complex_formation = 0
			removed_expression = 0
			removed_growth = 0
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
				elif isinstance(act, Growth):
					added_growth += 1
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
				elif isinstance(act, Growth):
					removed_growth += 1
				else:
					raise TypeError("analyse_revision: activity type not recognised: %s" % type(act))

			if added_growth != 0:
				print('added growth: %s' % added_growth)
			if removed_growth != 0:
				print('removed_growth: %s' % removed_growth)

			rev_for_all_events.append((added_reactions, added_transport, added_complex_formation,
				added_expression, removed_reactions, removed_transport, removed_complex_formation, removed_expression))

	return rev_for_all_events


#
# November analysis
#
def analyse_old_development_data():
	#for the initial batch of simulations
	# capture with >
	results = {}
	for folder in ['./not_crashed/first_batch_all_exps', './not_crashed/first_batch_two_factor']:
		results[folder] = get_data_for_development_and_drift_one_folder(folder)
	answer_folder_level_questions(results)

def analyse_all_development_data():
	# overall analysis, text output
	# capture with >
	results = get_data_for_development_and_drift_all_folders()
	influence_of_additional_working_models(results, 0)
	print('\n\n')
	influence_of_additional_working_models(results, 30)
	print('\n\n')
	influence_of_additional_working_models(results, 60)
	print('\n\n')
	is_err_decreasing_performance(results, 0, 30)
	print('\n\n')
	is_err_decreasing_performance(results, 30, 60)
	print('\n\n')
	is_err_decreasing_performance(results, 0, 60)
	print('\n\n')
	compare_rates_mods_trimmed(0, False)
	print('\n\n')
	compare_rates_mods_trimmed(30, False)
	print('\n\n')
	compare_rates_mods_trimmed(60, False)
	print('\n\n')
	compare_rates_mods_trimmed(0, True)
	print('\n\n')
	compare_rates_mods_trimmed(30, True)
	print('\n\n')
	compare_rates_mods_trimmed(60, True)
	print('\n\n')
	answer_folder_level_questions(results)
	print('\n\n')
	stats_of_TCs(results)

	for folder in get_folders_november_analysis():
		print("\n\n %s \n\n" % folder[-10:])
		analyse_all_development_and_drift(folder)

def get_data_for_development_and_drift_all_folders():
	folders = [
		'not_crashed/err0_mod2',
		'not_crashed/err0_mod4',
		'not_crashed/err0_mod6',
		'not_crashed/err30_mod2',
		'not_crashed/err30_mod4',
		'not_crashed/err30_mod6',
		'not_crashed/err60_mod2',
		'not_crashed/err60_mod4',
		'not_crashed/err60_mod6']
	results = {}
	for folder in folders:
		results[folder] = get_data_for_development_and_drift_one_folder(folder)
	return results

def get_data_for_development_and_drift_one_folder(folder):
	paths = get_all_paths(folder)
	paths.sort(key = lambda x: re.split('conf.._', x)[1])

	current_tc = paths[0][-7:-3]
	results_collection = {}
	results_collection[current_tc] = {}
	for path in paths: #paths:
		#
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
		tot_time = X_sq_dev[0][-1]
		nb_of_cycles = len([val for sublist in X_sq_dev for val in sublist])
		#
		improv_rate_abs_cycles = calculate_improv_rate([val for sublist in Y_sq_dev for val in sublist])
		if prop_dev != None:
			prop_dev_perc = -(prop_dev/initial_err)
			last_drift_perc = -(last_drift/initial_err)
			improv_rate_abs_time = -(prop_dev/tot_time)
		else:
			prop_dev_perc = None
			last_drift_perc = None
			improv_rate_abs_time = -(tot_dev/tot_time)

		if prop_dev != None:
			results_dict = {'tot_impr_prc':total_decrease_perc, 'tot_dev_prc':tot_dev_perc, 'tot_drft_prc':tot_drft_perc,
						'before_first_drft':before_drift_perc, 'after_first_drift_no_last_drift':prop_dev_perc,
						'up_to_final_drft':prop_dev_perc, 'final_drft':last_drift_perc,
						'test_dev_drift_totals':t_dev_drift, 'test_drifting_useful':t_drift, 'test_last_drifting_useful':t_last_drift,
						'improv_rate_abs_cycles':improv_rate_abs_cycles, 'improv_rate_abs_time':improv_rate_abs_time}
		#'test_dev_drift_totals', 'test_drifting_useful', 'test_last_drifting_useful'
		else:
			results_dict = {'tot_impr_prc':total_decrease_perc, 'tot_dev_prc':tot_dev_perc, 'tot_drft_prc':tot_drft_perc,
						'before_first_drft':before_drift_perc, 'after_first_drift_no_last_drift':total_decrease_perc,
						'up_to_final_drft':total_decrease_perc, 'final_drft':last_drift_perc,
						'test_dev_drift_totals':t_dev_drift, 'test_drifting_useful':t_drift, 'test_last_drifting_useful':t_last_drift,
						'improv_rate_abs_cycles':improv_rate_abs_cycles, 'improv_rate_abs_time':improv_rate_abs_time}

		# grouping reps of one tc together:
		# the same tc as previously
		if path[-7:-3] == current_tc:
			results_collection[current_tc][path[-2:]] = results_dict
		else: # new tc
			current_tc = path[-7:-3]
			results_collection[current_tc] = {path[-2:] : results_dict}

	return results_collection

def compare_diff_noise_levels_over_time(mod_number):
# created to check if differences between different noise levels
# increase over time
# (as they should: noisy results should accumulate)
# 0 vs 30; 30 vs 60; 0 vs 60 (one plot per TC)

	# prepare data
	seq = compare_diff_noise_prepare_data(mod_number)
	# initialise generators
	vs0_30 = compare_results(seq[0], seq[30])
	vs30_60 = compare_results(seq[30], seq[60])
	vs0_60 = compare_results(seq[0], seq[60])
	# plot
	counter = 1
	for tpls in zip(vs0_30, vs30_60, vs0_60):
		plot_three_noise_comparisons(tpls, counter)
		counter +=1

def compare_results(smaller_noise_res, bigger_noise_res):
	for tc in ['tc01', 'tc02', 'tc03', 'tc04', 'tc05', 'tc06', 'tc07', 'tc08', 'tc09', 'tc10', 'tc11', 'tc12']:
		cache = []
		for rep in ['r%s' % x for x in range(3)]:
			lvl1_y = smaller_noise_res[tc][rep]
			lvl2_y = bigger_noise_res[tc][rep]
			#
			lvl1_y, lvl2_y = trim_sequences(lvl1_y, lvl2_y)
			diff = []
			for counter in range(len(lvl1_y)):
				diff.append(lvl2_y[counter] - lvl1_y[counter])
			cache.append(diff)
		#
		diff_mean = []
		diff_std_dev = []
		for counter in range(len(cache[0])):
		# solves the problem of the number of cycles not being equal
			try:
				current_tick = [cache[0][counter], cache[1][counter], cache[2][counter]]
			except:
				break
			diff_mean.append(mean(current_tick))
			diff_std_dev.append(pstdev(current_tick))
		yield diff_mean, diff_std_dev

def compare_diff_noise_prepare_data(mod_number):
	# prepare data
	relevant_folders = {
		2:('not_crashed/err0_mod2', 'not_crashed/err30_mod2', 'not_crashed/err60_mod2'),
		4:('not_crashed/err0_mod6', 'not_crashed/err30_mod6', 'not_crashed/err60_mod6'),
		6:('not_crashed/err0_mod4', 'not_crashed/err30_mod4', 'not_crashed/err60_mod4')
		}
	noise_dict = {
		'not_crashed/err0_':0,
		'not_crashed/err30':30,
		'not_crashed/err60':60
		}
	#
	sequences = {}
	for folder in relevant_folders[mod_number]:
		#
		paths = get_all_paths(folder)
		paths.sort(key = lambda x: re.split('conf.._', x)[1])
		#
		results_cache = {}
		for path in paths:
			full_path = '/'.join([folder,path])
			arch = read_archive(full_path)
			Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
			Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
			try:
				results_cache[path[-7:-3]][path[-2:]] = Y_flattened
			except:
				results_cache[path[-7:-3]] = {}
				results_cache[path[-7:-3]][path[-2:]] = Y_flattened
		sequences[noise_dict[folder[:17]]] = results_cache
	return sequences

def compare_rates_mods_trimmed(err_lvl, TC_by_TC = False):
# compares improvement rate (per cycle) between mod2, mod4 and mod6 versions
# for the equal number of cycles (i.e. all trimmed to the smallest one)
# created to check whether more mods is better if slower development (time-wise)
# is taken into account
	print('comparing improvement rates between mod versions: err_lvl: %s; TC_by_TC: %s' % (err_lvl, TC_by_TC))

	relevant_folders = {
		0:('not_crashed/err0_mod2','not_crashed/err0_mod4','not_crashed/err0_mod6'),
		30:('not_crashed/err30_mod2','not_crashed/err30_mod4','not_crashed/err30_mod6'),
		60:('not_crashed/err60_mod2','not_crashed/err60_mod4','not_crashed/err60_mod6')
		}
	#
	Y_sequences = {}
	for folder in relevant_folders[err_lvl]:
		#
		paths = get_all_paths(folder)
		paths.sort(key = lambda x: re.split('conf.._', x)[1])
		#
		current_tc = paths[0][-7:-3]
		results_cache = {}
		results_cache[current_tc] = {}
		#
		for path in paths:
			full_path = '/'.join([folder,path])
			arch = read_archive(full_path)
			Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
			Y_sq_dev = [val for sublist in Y_sq_dev for val in sublist]
			# grouping reps of one tc together:
			# the same tc as previously
			if path[-7:-3] == current_tc:
				results_cache[current_tc][path[-2:]] = Y_sq_dev
			else: # new tc
				current_tc = path[-7:-3]
				results_cache[current_tc] = {path[-2:] : Y_sq_dev}
		# modX (X == 2/4/6)
		Y_sequences[folder[-4:]] = results_cache

	if TC_by_TC == False:
		rates_2_vs_4 = extract_and_compare_rates(Y_sequences['mod2'], Y_sequences['mod4'])
		rates_4_vs_6 = extract_and_compare_rates(Y_sequences['mod4'], Y_sequences['mod6'])
		rates_2_vs_6 = extract_and_compare_rates(Y_sequences['mod2'], Y_sequences['mod6'])
		#
		print('2 vs 4: \nttest: %s \nbinom: %s \n succ: %s/%s' % rates_2_vs_4[:4])
		print('mod2 rates trimmed: avg %s; std %s' % (mean(rates_2_vs_4[4]), pstdev(rates_2_vs_4[4])))
		print('mod4 rates trimmed: avg %s; std %s\n' % (mean(rates_2_vs_4[5]), pstdev(rates_2_vs_4[5])))
		print('4 vs 6: \nttest: %s \nbinom: %s \n succ: %s/%s' % rates_4_vs_6[:4])
		print('mod4 rates trimmed: avg %s; std %s' % (mean(rates_4_vs_6[4]), pstdev(rates_4_vs_6[4])))
		print('mod6 rates trimmed: avg %s; std: %s\n' % (mean(rates_4_vs_6[5]), pstdev(rates_4_vs_6[5])))
		print('2 vs 6: \nttest: %s \nbinom: %s \n succ: %s/%s' % rates_2_vs_6[:4])
		print('mod2 rates trimmed: avg %s; std %s' % (mean(rates_2_vs_6[4]), pstdev(rates_2_vs_6[4])))
		print('mod6 rates trimmed: avg %s; std: %s' % (mean(rates_2_vs_6[5]), pstdev(rates_2_vs_6[5])))
	else:
		# TC by TC
		extract_and_compare_rates_one_TC_at_a_time(Y_sequences['mod2'], Y_sequences['mod4'])
		extract_and_compare_rates_one_TC_at_a_time(Y_sequences['mod4'], Y_sequences['mod6'])
		extract_and_compare_rates_one_TC_at_a_time(Y_sequences['mod2'], Y_sequences['mod6'])

def extract_and_compare_rates(results_cache1, results_cache2):
	rates1 = []
	rates2 = []
	for tpl in yield_tc_rep():
		seq1 = results_cache1[tpl[0]][tpl[1]]
		seq2 = results_cache2[tpl[0]][tpl[1]]
		# trim_sequences(seq1, seq2)
		seq1, seq2 = trim_sequences(seq1, seq2)
		# calculate_improv_rate(seq)
		rate1 = calculate_improv_rate(seq1)
		rate2 = calculate_improv_rate(seq2)
		rates1.append(rate1)
		rates2.append(rate2)
	# is there a significant difference?
	ttest = stats.ttest_rel(rates1, rates2)
	# is more better?
	successes = 0
	counter = 0
	while counter < len(rates1):
		if rates1[counter] < rates2[counter]:
			successes += 1
		else:
			pass
		counter += 1
	#
	binom = stats.binom_test(successes, counter)
	return (ttest, binom, successes, counter, rates1, rates2)

def extract_and_compare_rates_one_TC_at_a_time(results_cache1, results_cache2):
	for tc in ['tc01', 'tc02', 'tc03', 'tc04', 'tc05', 'tc06', 'tc07', 'tc08', 'tc09', 'tc10', 'tc11', 'tc12']:
		reps_1 = []
		reps_2 = []
		for rep in ['r%s' % x for x in range(3)]:
			seq1 = results_cache1[tc][rep]
			seq2 = results_cache2[tc][rep]
			seq1, seq2 = trim_sequences(seq1, seq2)
			reps_1.append(calculate_improv_rate(seq1))
			reps_2.append(calculate_improv_rate(seq2))
		print(tc)
		print('t_stat: %s p_value: %s' % stats.stats.ttest_ind(reps_1, reps_2))

def trim_sequences(seq1, seq2):
	if len(seq1) > len(seq2):
		return seq1[:len(seq2)], seq2
	elif len(seq1) < len(seq2):
		return seq1, seq2[:len(seq1)]
	else:
		return seq1, seq2

def calculate_improv_rate(seq):
	return (seq[0] - seq[-1])/len(seq)

def influence_of_additional_working_models(results, err_lvl):
	# different? beneficial?
	# compare mod2, 4, 6 for a given err_lvl
	relevant_folders = {
		0:('not_crashed/err0_mod2','not_crashed/err0_mod4','not_crashed/err0_mod6'),
		30:('not_crashed/err30_mod2','not_crashed/err30_mod4','not_crashed/err30_mod6'),
		60:('not_crashed/err60_mod2','not_crashed/err60_mod4','not_crashed/err60_mod6')
		}

	mod2_perc = []
	for tpl in yield_tc_rep():
		if 'after_first_drift_no_last_drift' != None:
			mod2_perc.append(results[relevant_folders[err_lvl][0]][tpl[0]][tpl[1]]['after_first_drift_no_last_drift'])
		else:
			mod2_perc.append(results[relevant_folders[err_lvl][0]][tpl[0]][tpl[1]]['tot_impr_prc'])
	mod2_rate_cyc = [results[relevant_folders[err_lvl][0]][tpl[0]][tpl[1]]['improv_rate_abs_cycles'] for tpl in yield_tc_rep()]
	mod2_rate_time = [results[relevant_folders[err_lvl][0]][tpl[0]][tpl[1]]['improv_rate_abs_time'] for tpl in yield_tc_rep()]

	mod4_perc = []
	for tpl in yield_tc_rep():
		if 'after_first_drift_no_last_drift' != None:
			mod4_perc.append(results[relevant_folders[err_lvl][1]][tpl[0]][tpl[1]]['after_first_drift_no_last_drift'])
		else:
			mod4_perc.append(results[relevant_folders[err_lvl][1]][tpl[0]][tpl[1]]['tot_impr_prc'] for tpl in yield_tc_rep())
	mod4_rate_cyc = [results[relevant_folders[err_lvl][1]][tpl[0]][tpl[1]]['improv_rate_abs_cycles'] for tpl in yield_tc_rep()]
	mod4_rate_time = [results[relevant_folders[err_lvl][1]][tpl[0]][tpl[1]]['improv_rate_abs_time'] for tpl in yield_tc_rep()]

	mod6_perc = []
	for tpl in yield_tc_rep():
		if 'after_first_drift_no_last_drift' != None:
			mod6_perc.append(results[relevant_folders[err_lvl][2]][tpl[0]][tpl[1]]['after_first_drift_no_last_drift'])
		else:
			mod6_perc.append(results[relevant_folders[err_lvl][2]][tpl[0]][tpl[1]]['tot_impr_prc'] for tpl in yield_tc_rep())
	mod6_rate_cyc = [results[relevant_folders[err_lvl][2]][tpl[0]][tpl[1]]['improv_rate_abs_cycles'] for tpl in yield_tc_rep()]
	mod6_rate_time = [results[relevant_folders[err_lvl][2]][tpl[0]][tpl[1]]['improv_rate_abs_time'] for tpl in yield_tc_rep()]

	assert len(mod2_perc) == len(mod2_rate_cyc) == len(mod2_rate_time) == len(mod4_perc) == len(mod4_rate_cyc) == len(mod4_rate_time) == len(mod6_perc) == len(mod6_rate_cyc) == len(mod6_rate_time)

	#
	mod2_vs_mod4_perc_different = stats.ttest_rel(mod2_perc, mod4_perc)
	mod2_vs_mod4_rate_cyc_different = stats.ttest_rel(mod2_rate_cyc, mod4_rate_cyc)
	mod2_vs_mod4_rate_time_different = stats.ttest_rel(mod2_rate_time, mod4_rate_time)

	mod4_vs_mod6_perc_different = stats.ttest_rel(mod4_perc, mod6_perc)
	mod4_vs_mod6_rate_cyc_different = stats.ttest_rel(mod4_rate_cyc, mod6_rate_cyc)
	mod4_vs_mod6_rate_time_different = stats.ttest_rel(mod4_rate_time, mod6_rate_time)

	mod2_vs_mod6_perc_different = stats.ttest_rel(mod2_perc, mod6_perc)
	mod2_vs_mod6_rate_cyc_different = stats.ttest_rel(mod2_rate_cyc, mod6_rate_cyc)
	mod2_vs_mod6_rate_time_different = stats.ttest_rel(mod2_rate_time, mod6_rate_time)

	#
	mod2_mod4_perc = 0
	mod2_mod4_rate_cyc = 0
	mod2_mod4_rate_time = 0

	mod4_mod6_perc = 0
	mod4_mod6_rate_cyc = 0
	mod4_mod6_rate_time = 0

	mod2_mod6_perc = 0
	mod2_mod6_rate_cyc = 0
	mod2_mod6_rate_time = 0

	counter = 0
	while counter < len(mod2_perc):
		if mod2_perc[counter] < mod4_perc[counter]:
			mod2_mod4_perc += 1
		if mod2_rate_cyc[counter] < mod4_rate_cyc[counter]:
			mod2_mod4_rate_cyc += 1
		if mod2_rate_time[counter] < mod4_rate_time[counter]:
			mod2_mod4_rate_time += 1
		#
		if mod4_perc[counter] < mod6_perc[counter]:
			mod4_mod6_perc += 1
		if mod4_rate_cyc[counter] < mod6_rate_cyc[counter]:
			mod4_mod6_rate_cyc += 1
		if mod4_rate_time[counter] < mod6_rate_time[counter]:
			mod4_mod6_rate_time += 1
		#
		if mod2_perc[counter] < mod6_perc[counter]:
			mod2_mod6_perc += 1
		if mod2_rate_cyc[counter] < mod6_rate_cyc[counter]:
			mod2_mod6_rate_cyc += 1
		if mod2_rate_time[counter] < mod6_rate_time[counter]:
			mod2_mod6_rate_time += 1
		counter += 1

	mod2_mod4_perc_binom = stats.binom_test(mod2_mod4_perc, counter)/2
	mod2_mod4_rate_cyc_binom = stats.binom_test(mod2_mod4_rate_cyc, counter)/2
	mod2_mod4_rate_time_binom = stats.binom_test(mod2_mod4_rate_time, counter)/2

	mod4_mod6_perc_binom = stats.binom_test(mod4_mod6_perc, counter)/2
	mod4_mod6_rate_cyc_binom = stats.binom_test(mod4_mod6_rate_cyc, counter)/2
	mod4_mod6_rate_time_binom = stats.binom_test(mod4_mod6_rate_time, counter)/2

	mod2_mod6_perc_binom = stats.binom_test(mod2_mod6_perc, counter)/2
	mod2_mod6_rate_cyc_binom = stats.binom_test(mod2_mod6_rate_cyc, counter)/2
	mod2_mod6_rate_time_binom = stats.binom_test(mod2_mod6_rate_time, counter)/2

	# magnitude info
	tplmod2 = (mean(mod2_perc), pstdev(mod2_perc), mean(mod2_rate_cyc), pstdev(mod2_rate_cyc), mean(mod2_rate_time), pstdev(mod2_rate_time))
	print('mod2: improv %s std %s; rate/cyc %s std %s; rate/time %s std %s' % tplmod2)
	tplmod4 = (mean(mod4_perc), pstdev(mod4_perc), mean(mod4_rate_cyc), pstdev(mod4_rate_cyc), mean(mod4_rate_time), pstdev(mod4_rate_time))
	print('mod4: improv %s std %s; rate/cyc %s std %s; rate/time %s std %s' % tplmod4)
	tplmod6 = (mean(mod6_perc), pstdev(mod6_perc), mean(mod6_rate_cyc), pstdev(mod6_rate_cyc), mean(mod6_rate_time), pstdev(mod6_rate_time))
	print('mod6: improv %s std %s; rate/cyc %s std %s; rate/time %s std %s' % tplmod6)
	print('\n')

	print('Influence of additional working models for the error level: %s' % err_lvl)
	print('is there a difference in performance?')
	print('mod2_vs_mod4_perc_different: t-stats: %s; p-val: %s' % (mod2_vs_mod4_perc_different[0], mod2_vs_mod4_perc_different[1]/2))
	print('mod2_vs_mod4_rate_cyc_different: t-stats: %s; p-val: %s' % (mod2_vs_mod4_rate_cyc_different[0], mod2_vs_mod4_rate_cyc_different[1]/2))
	print('mod2_vs_mod4_rate_time_different: t-stats: %s; p-val: %s' % (mod2_vs_mod4_rate_time_different[0], mod2_vs_mod4_rate_time_different[1]/2))
	print('')
	print('mod4_vs_mod6_perc_different: t-stats: %s; p-val: %s' % (mod4_vs_mod6_perc_different[0], mod4_vs_mod6_perc_different[1]/2))
	print('mod4_vs_mod6_rate_cyc_different: t-stats: %s; p-val: %s' % (mod4_vs_mod6_rate_cyc_different[0], mod4_vs_mod6_rate_cyc_different[1]/2))
	print('mod4_vs_mod6_rate_time_different: t-stats: %s; p-val: %s' % (mod4_vs_mod6_rate_time_different[0], mod4_vs_mod6_rate_time_different[1]/2))
	print('')
	print('mod2_vs_mod6_perc_different: t-stats: %s; p-val: %s' % (mod2_vs_mod6_perc_different[0], mod2_vs_mod6_perc_different[1]/2))
	print('mod2_vs_mod6_rate_cyc_different: t-stats: %s; p-val: %s' % (mod2_vs_mod6_rate_cyc_different[0], mod2_vs_mod6_rate_cyc_different[1]/2))
	print('mod2_vs_mod6_rate_time_different: t-stats: %s; p-val: %s' % (mod2_vs_mod6_rate_time_different[0], mod2_vs_mod6_rate_time_different[1]/2))
	print('\n\n')
	print('is using more working models better?')
	print('mod2_mod4_perc successes: %s / %s' % (mod2_mod4_perc, counter))
	print('mod2_mod4_perc_binom: %s' % mod2_mod4_perc_binom)
	print('mod2_mod4_rate_cyc successes: %s / %s' % (mod2_mod4_rate_cyc, counter))
	print('mod2_mod4_rate_cyc_binom: %s' % mod2_mod4_rate_cyc_binom)
	print('mod2_mod4_rate_time successes: %s / %s' % (mod2_mod4_rate_time, counter))
	print('mod2_mod4_rate_time_binom: %s' % mod2_mod4_rate_time_binom)
	print('')
	print('mod4_mod6_perc successes: %s / %s' % (mod4_mod6_perc, counter))
	print('mod4_mod6_perc_binom: %s' % mod4_mod6_perc_binom)
	print('mod4_mod6_rate_cyc successes: %s / %s' % (mod4_mod6_rate_cyc, counter))
	print('mod4_mod6_rate_cyc_binom: %s' % mod4_mod6_rate_cyc_binom)
	print('mod4_mod6_rate_time successes: %s / %s' % (mod4_mod6_rate_time, counter))
	print('mod4_mod6_rate_time_binom: %s' % mod4_mod6_rate_time_binom)
	print('')
	print('mod2_mod6_perc successes: %s / %s' % (mod2_mod6_perc, counter))
	print('mod2_mod6_perc_binom: %s' % mod2_mod6_perc_binom)
	print('mod2_mod6_rate_cyc successes: %s / %s' % (mod2_mod6_rate_cyc, counter))
	print('mod2_mod6_rate_cyc_binom: %s' % mod2_mod6_rate_cyc_binom)
	print('mod2_mod6_rate_time successes: %s / %s' % (mod2_mod6_rate_time, counter))
	print('mod2_mod6_rate_time_binom: %s' % mod2_mod6_rate_time_binom)

def is_err_decreasing_performance(results, err_lvl_1, err_lvl_2):
# and how much
# for all working models versions
	relevant_folders = {
		0:('not_crashed/err0_mod2','not_crashed/err0_mod4','not_crashed/err0_mod6'),
		30:('not_crashed/err30_mod2','not_crashed/err30_mod4','not_crashed/err30_mod6'),
		60:('not_crashed/err60_mod2','not_crashed/err60_mod4','not_crashed/err60_mod6')
		}

	# first error level
	err1_perc = []
	for folder in relevant_folders[err_lvl_1]:
		for tpl in yield_tc_rep():
			if 'after_first_drift_no_last_drift' != None:
				err1_perc.append(results[folder][tpl[0]][tpl[1]]['after_first_drift_no_last_drift'])
			else:
				err1_perc.append(results[folder][tpl[0]][tpl[1]]['tot_impr_prc'])

	err1_rate_cyc = []
	for folder in relevant_folders[err_lvl_1]:
		for tpl in yield_tc_rep():
			err1_rate_cyc.append(results[folder][tpl[0]][tpl[1]]['improv_rate_abs_cycles'])

	err1_rate_time = []
	for folder in relevant_folders[err_lvl_1]:
		for tpl in yield_tc_rep():
			err1_rate_time.append(results[folder][tpl[0]][tpl[1]]['improv_rate_abs_time'])

	# second error level
	err2_perc = []
	for folder in relevant_folders[err_lvl_2]:
		for tpl in yield_tc_rep():
			if 'after_first_drift_no_last_drift' != None:
				err2_perc.append(results[folder][tpl[0]][tpl[1]]['after_first_drift_no_last_drift'])
			else:
				err2_perc.append(results[folder][tpl[0]][tpl[1]]['tot_impr_prc'])

	err2_rate_cyc = []
	for folder in relevant_folders[err_lvl_2]:
		for tpl in yield_tc_rep():
			err2_rate_cyc.append(results[folder][tpl[0]][tpl[1]]['improv_rate_abs_cycles'])

	err2_rate_time = []
	for folder in relevant_folders[err_lvl_2]:
		for tpl in yield_tc_rep():
			err2_rate_time.append(results[folder][tpl[0]][tpl[1]]['improv_rate_abs_time'])

	#
	assert len(err1_perc) == len(err1_rate_cyc) == len(err1_rate_time) == len(err2_perc) == len(err2_rate_cyc) == len(err2_rate_time)

	#
	err1_vs_err2_perc_different = stats.ttest_rel(err1_perc, err2_perc)
	err1_vs_err2_rate_cyc_different = stats.ttest_rel(err1_rate_cyc, err2_rate_cyc)
	err1_vs_err2_rate_time_different = stats.ttest_rel(err1_rate_time, err2_rate_time)

	#
	err1_vs_err2_perc = 0
	err1_vs_err2_rate_cyc = 0
	err1_vs_err2_rate_time = 0
	#
	counter = 0
	while counter < len(err1_perc):
		if err1_perc[counter] > err2_perc[counter]:
			err1_vs_err2_perc += 1
		if err1_rate_cyc[counter] > err2_rate_cyc[counter]:
			err1_vs_err2_rate_cyc += 1
		if err1_rate_time[counter] > err2_rate_time[counter]:
			err1_vs_err2_rate_time += 1

		counter += 1
	#
	err1_vs_err2_perc_binom = stats.binom_test(err1_vs_err2_perc, counter)
	err1_vs_err2_rate_cyc_binom = stats.binom_test(err1_vs_err2_rate_cyc, counter)
	err1_vs_err2_rate_time_binom = stats.binom_test(err1_vs_err2_rate_time, counter)
	#
	print('Influence of error level on performance: %s vs %s' % (err_lvl_1, err_lvl_2))
	print('err lvl %s: ' % err_lvl_1)
	print('improv : %s; std: %s' % (mean(err1_perc), pstdev(err1_perc)))
	print('rate/cyc.: %s; std: %s' % (mean(err1_rate_cyc), pstdev(err1_rate_cyc)))
	print('rate/time: %s; std: %s\n' % (mean(err1_rate_time), pstdev(err1_rate_time)))
	print('err lvl %s: ' % err_lvl_2)
	print('improv : %s; std: %s' % (mean(err2_perc), pstdev(err2_perc)))
	print('rate/cyc.: %s; std: %s' % (mean(err2_rate_cyc), pstdev(err2_rate_cyc)))
	print('rate/time: %s; std: %s\n' % (mean(err2_rate_time), pstdev(err2_rate_time)))

	print('is there a difference in performance?')
	print('err1_vs_err2_perc_different: t-stats: %s; p-val: %s' % err1_vs_err2_perc_different)
	print('err1_vs_err2_rate_cyc_different: t-stats: %s; p-val: %s' % err1_vs_err2_rate_cyc_different)
	print('err1_vs_err2_rate_time_different: t-stats: %s; p-val: %s' % err1_vs_err2_rate_time_different)
	print('')
	print('is lower error better?')
	print('err1_vs_err2_perc successes: %s / %s' % (err1_vs_err2_perc, counter))
	print('err1_vs_err2_perc_binom: %s' % err1_vs_err2_perc_binom)
	print('err1_vs_err2_rate_cyc successes: %s / %s' % (err1_vs_err2_rate_cyc, counter))
	print('err1_vs_err2_rate_cyc_binom: %s' % err1_vs_err2_rate_cyc_binom)
	print('err1_vs_err2_rate_time successes: %s / %s' % (err1_vs_err2_rate_time, counter))
	print('err1_vs_err2_rate_time_binom: %s\n\n' % err1_vs_err2_rate_time_binom)

def yield_tc_rep():
	for tc in ['tc01', 'tc02', 'tc03', 'tc04', 'tc05', 'tc06', 'tc07', 'tc08', 'tc09', 'tc10', 'tc11', 'tc12']:
		for rep in ['r0', 'r1', 'r2']:
			yield (tc, rep)

def is_dev_better_than_drift_3_folders(err_lvl):
	relevant_folders = {
		0:('not_crashed/err0_mod2','not_crashed/err0_mod4','not_crashed/err0_mod6'),
		30:('not_crashed/err30_mod2','not_crashed/err30_mod4','not_crashed/err30_mod6'),
		60:('not_crashed/err60_mod2','not_crashed/err60_mod4','not_crashed/err60_mod6')
		}
	#
	dev = []
	drift = []
	for folder in relevant_folders[err_lvl]:
		results = get_data_for_development_and_drift_one_folder(folder)
		for tpl in unpack_results_from_two_folders_skipping_None('tot_dev_prc', 'tot_drft_prc', results):
			dev.append(tpl[0])
			drift.append(tpl[1])
	print('is dev better than drift: ttest rel, two tails')
	print('folders from error lvl: %s' % err_lvl)
	print(stats.ttest_rel(dev, drift))


def answer_folder_level_questions(results):
	for folder in sorted(list(results.keys())):
		global_total_decrease_perc = [rep['tot_impr_prc'] for rep in unpack_reps_from_one_folder(results[folder])]
		global_tot_dev_perc = [rep['tot_dev_prc'] for rep in unpack_reps_from_one_folder(results[folder])]
		global_tot_drft_perc = [rep['tot_drft_prc'] for rep in unpack_reps_from_one_folder(results[folder]) if rep['tot_drft_prc'] != None]
		global_before_drift_perc = [rep['before_first_drft'] for rep in unpack_reps_from_one_folder(results[folder])]
		global_after_drift_perc = [rep['after_first_drift_no_last_drift'] for rep in unpack_reps_from_one_folder(results[folder])]
		global_prop_dev_perc = [rep['up_to_final_drft'] for rep in unpack_reps_from_one_folder(results[folder]) if rep['up_to_final_drft'] != None]
		global_last_drift_perc = [rep['final_drft'] for rep in unpack_reps_from_one_folder(results[folder]) if rep['final_drft'] != None]
		global_improv_rate_abs_cycles = [rep['improv_rate_abs_cycles'] for rep in unpack_reps_from_one_folder(results[folder])]
		global_improv_rate_abs_time = [rep['improv_rate_abs_time'] for rep in unpack_reps_from_one_folder(results[folder])]
		#
		global_test_dev_drift_totals = [x['test_dev_drift_totals']
			for x in unpack_reps_from_one_folder(results[folder])
			if x['test_dev_drift_totals'] != None]
		global_test_drifting_useful = [x['test_drifting_useful']
			for x in unpack_reps_from_one_folder(results[folder])
			if x['test_drifting_useful'] != None]
		global_test_last_drifting_useful = [x['test_last_drifting_useful']
			for x in unpack_reps_from_one_folder(results[folder])
			if x['test_last_drifting_useful'] != None]
		#
		print('FOLDER level: %s' % folder)
		print('total improvement')
		print('mean: %s' % mean(global_total_decrease_perc))
		print('population std dev: %s' % pstdev(global_total_decrease_perc))
		print('')
		print('improvement rate (# of cycles)')
		print('mean: %s' % mean(global_improv_rate_abs_cycles))
		print('population std dev: %s' % pstdev(global_improv_rate_abs_cycles))
		print('')
		print('improvement rate (time)')
		print('mean: %s' % mean(global_improv_rate_abs_time))
		print('population std dev: %s' % pstdev(global_improv_rate_abs_time))
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
		print('p-value binom test: %s' % stats.binom_test([successes, failures]))
		print('ttest_rel, two-tails:')
		dev = []
		drift = []
		for tpl in unpack_results_from_two_folders_skipping_None('tot_dev_prc', 'tot_drft_prc', results[folder]):
			dev.append(tpl[0])
			drift.append(tpl[1])
		print(stats.ttest_rel(dev, drift))
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

def unpack_reps_from_one_folder(folder_results):
	tcs = [x for x in folder_results.keys()]
	tcs.sort()
	for tc in tcs:
		reps = folder_results[tc].keys()
		for rep in sorted(reps):
			yield folder_results[tc][rep]

def unpack_results_from_two_folders_skipping_None(key_1, key_2, results):
	tcs = [x for x in results.keys()]
	tcs.sort()
	for tc in tcs:
		reps = results[tc].keys()
		for rep in sorted(reps):
			if results[tc][rep][key_1] != None and results[tc][rep][key_2] != None:
				yield results[tc][rep][key_1], results[tc][rep][key_2]

def stats_of_TCs(results):
	# calculate stats for all tc's (mean, std. dev for: absolute and % improvement; )
	for folder in sorted(list(results.keys())):
		for tc in sorted(list(results[folder].keys())):
			#
			run_dicts = [results[folder][tc][key] for key in results[folder][tc].keys()]
			#
			total_decrease_perc = [x['tot_impr_prc'] for x in run_dicts]
			tot_dev_perc = [x['tot_dev_prc'] for x in run_dicts]
			tot_drft_perc = [x['tot_drft_prc'] for x in run_dicts if x['tot_drft_prc'] != None]
			before_drift_perc = [x['before_first_drft'] for x in run_dicts]
			after_drift_perc = [x['after_first_drift_no_last_drift'] for x in run_dicts]
			prop_dev_perc = [x['up_to_final_drft'] for x in run_dicts if x['up_to_final_drft'] != None]
			last_drift_perc = [x['final_drft'] for x in run_dicts if x['final_drft'] != None]
			improv_rate_abs_cycles = [x['improv_rate_abs_cycles'] for x in run_dicts]
			improv_rate_abs_time = [x['improv_rate_abs_time'] for x in run_dicts]

			# analysis for this problem:
			print('folder: %s; test_case: %s;' % (folder, tc))
			print('total improvement')
			print('mean: %s' % mean(total_decrease_perc))
			print('population std dev: %s' % pstdev(total_decrease_perc))
			print('\n')
			print('improvement rate (# of cycles)')
			print('mean: %s' % mean(improv_rate_abs_cycles))
			print('population std dev: %s' % pstdev(improv_rate_abs_cycles))
			print('\n')
			print('improvement rate (time)')
			print('mean: %s' % mean(improv_rate_abs_time))
			print('population std dev: %s' % pstdev(improv_rate_abs_time))
			print('\n')
			print('improvement during development')
			print('mean: %s' % mean(tot_dev_perc))
			print('population std dev: %s' % pstdev(tot_dev_perc))
			print('improvement during random drift')
			print('\n')
			if len(tot_drft_perc) == 0:
				print('mean: N/A')
				print('population std dev: N/A')
			else:
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
			if len(prop_dev_perc) == 0:
				print('mean: N/A')
				print('population std dev: N/A')
			else:
				print('mean: %s' % mean(prop_dev_perc))
				print('population std dev: %s' % pstdev(prop_dev_perc))
			print('improvement during the last drift')
			if len(last_drift_perc) == 0:
				print('mean: N/A')
				print('population std dev: N/A')
			else:
				print('mean: %s' % mean(last_drift_perc))
				print('population std dev: %s' % pstdev(last_drift_perc))
			print('\n\n')

def get_folders_november_analysis():
	configs = [
		'err0_mod2',
		'err0_mod4',
		'err0_mod6',
		'err30_mod2',
		'err30_mod4',
		'err30_mod6',
		'err60_mod2',
		'err60_mod4',
		'err60_mod6']
	for configuration in configs:
		yield '/'.join(['not_crashed', configuration])

def change_in_rate_over_time_all_runs():
	print('\n\n\n\n\nchange in the change rate for all runs:\n\n')

	for folder in get_folders_november_analysis():
		paths = get_all_paths(folder)
		paths.sort(key = lambda x: re.split('conf.._', x)[1])
		for path in paths: #paths:
			full_path = '/'.join([folder,path])
			arch = read_archive(full_path)
			Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
			flattened_Y, flattened_X = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
			rate = calculate_change_in_rate_over_time(flattened_Y, flattened_X)
			plot_simple(rate[1][1:], rate[0][1:], folder, path)

def calculate_change_in_rate_over_time(flattened_Y, flattened_X):
	rates = []
	#stop before the last one
	for index in range(len(flattened_Y)-1):
		# rate per cycle at this point
		rates.append(flattened_Y[index] - flattened_Y[index+1])
	#last time-point doesn't have a matching rate
	return rates, flattened_X[:-1]

def flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, incl_last_drift=True):
	if incl_last_drift == False:
		#had drift at all
		if len(X_sq_drift) != 0:
			# didn't end in a drift
			if X_sq_dev[-1][-1] > X_sq_drift[-1][-1]:
				pass
			# ended with a drift
			else:
				Y_sq_drift = Y_sq_drift[:-1]
				X_sq_drift = X_sq_drift[:-1]
	else:
		pass
	#
	Y_flattened = []
	X_flattened = []
	if len(X_sq_drift) != 0:
		# development shouldn't start with drift
		assert X_sq_dev[0][0] < X_sq_drift[0][0], 'development started with drift: \n%s\n%s' % (X_sq_dev, X_sq_drift)
	for index in range(len(Y_sq_dev)):
		Y_flattened.extend(Y_sq_dev[index])
		X_flattened.extend(X_sq_dev[index])
		if index >= len(Y_sq_drift):
			pass
		else:
			Y_flattened.extend(Y_sq_drift[index])
			X_flattened.extend(X_sq_drift[index])
	return Y_flattened, X_flattened

def was_improvement_after_prep_significant_one_folder(folder):
	avg_init_errs = []
	avg_fin_errs = []
	are_devs_successfull = []
	paths = get_all_paths(folder)
	for path in paths:
		avg_init_err, avg_fin_err, was_dev_successfull = improvement_after_preparatory_period('/'.join([folder, path]))
		avg_init_errs.append(avg_init_err)
		avg_fin_errs.append(avg_fin_err)
		are_devs_successfull.append(was_dev_successfull)
	#
	successess = len([x for x in are_devs_successfull if x==True])
	binom_res = stats.binom_test(successess, len(are_devs_successfull))
	ttest_res = stats.ttest_rel(avg_init_errs, avg_fin_errs)
	print(folder)
	print('avg init %s; std %s' % (mean(avg_init_errs), pstdev(avg_init_errs)))
	print('avg fin %s; std %s' % (mean(avg_fin_errs), pstdev(avg_fin_errs)))
	print('succ: %s, trials: %s' % (successess, len(are_devs_successfull)))
	print(binom_res)
	print(ttest_res)


def improvement_after_preparatory_period(path):
	arch = read_archive(path)
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
	Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
	was_dev_successfull = Y_flattened[1] > Y_flattened[-1]
	return Y_flattened[1], Y_flattened[-1], was_dev_successfull

def test_differences_drifting(err_lvl):
	relevant_folders = {
		0:('not_crashed/err0_mod2','not_crashed/err0_mod4','not_crashed/err0_mod6'),
		30:('not_crashed/err30_mod2','not_crashed/err30_mod4','not_crashed/err30_mod6'),
		60:('not_crashed/err60_mod2','not_crashed/err60_mod4','not_crashed/err60_mod6')
		}

	chosen_folders = relevant_folders[err_lvl]
	test_difference_drifting_two_folders(chosen_folders[0], chosen_folders[1])
	test_difference_drifting_two_folders(chosen_folders[1], chosen_folders[2])
	test_difference_drifting_two_folders(chosen_folders[0], chosen_folders[2])

def test_difference_drifting_two_folders(folder1, folder2):
	nbs_cycles1, nbs_drifts1, nbs_drifts_per_cycle1 = analyse_random_drifts_one_folder(folder1)
	nbs_cycles2, nbs_drifts2, nbs_drifts_per_cycle2 = analyse_random_drifts_one_folder(folder2)
	test_result_nb = stats.ttest_rel(nbs_drifts1, nbs_drifts2)
	test_result_rate = stats.ttest_rel(nbs_drifts_per_cycle1, nbs_drifts_per_cycle2)

	print('folder 1:%s; folder 2:%s' % (folder1, folder2))
	print('stats:')
	print('average nb of drifts: folder 1:%s; folder 2: %s' % (mean(nbs_drifts1), mean(nbs_drifts2)))
	print('std deviation: folder1: %s; folder2: %s' % (pstdev(nbs_drifts1), pstdev(nbs_drifts2)))
	print('average drifting rate per cycle: folder 1:%s; folder 2: %s' % (mean(nbs_drifts_per_cycle1), mean(nbs_drifts_per_cycle2)))
	print('std deviation: folder1:%s; folder2:%s' % (pstdev(nbs_drifts_per_cycle1), pstdev(nbs_drifts_per_cycle2)))
	print('are the numbers of drifts different?')
	print(test_result_nb)
	print('are the numbers of drifting rates (per cycle) different?')
	print(test_result_rate)
	print('')

def analyse_random_drifts_one_folder(folder):
	nbs_drifts = []
	nbs_drifts_per_cycle = []
	nbs_cycles = []
	paths = get_all_paths(folder)
	paths.sort(key = lambda x: re.split('conf.._', x)[1])
	for path in paths:
		nb_drifts, nb_cycles = analyse_random_drifts_one_path('/'.join([folder, path]))
		nb_drifts_per_cycle = nb_drifts/nb_cycles
		nbs_drifts.append(nb_drifts)
		nbs_cycles.append(nb_cycles)
		nbs_drifts_per_cycle.append(nb_drifts_per_cycle)
	return nbs_cycles, nbs_drifts, nbs_drifts_per_cycle

def analyse_random_drifts_one_path(path):
	arch = read_archive(path)
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
	nb_cycles = len([val for sublist in Y_sq_dev for val in sublist])
	nb_drifts = len(Y_sq_drift)
	return nb_drifts, nb_cycles

def rate_of_improv_vs_TC_size(folder):
	improv = []
	rates = []
	tc_sizes = []
	ref_mod_sizes = []
	paths = get_all_paths(folder)
	for path in paths:
		archive = read_archive('/'.join([folder, path]))
		rates.append(get_improv_rate(archive))
		ref_mod_sizes.append(get_ref_mod_size(archive))
		tc_sizes.append(get_TC_size(archive))
		improv.append(get_improv(archive))
	print(folder)
	print('spearman correlation tests:')
	print('TC size vs. improvement')
	print('corr coefficient:%s; p-value:%s' % stats.spearmanr(tc_sizes, improv))
	print('model of ref size vs. improvement')
	print('corr coefficient:%s; p-value:%s' % stats.spearmanr(ref_mod_sizes, improv))
	print('TC size vs. improv rate per cycle')
	print('corr coefficient:%s; p-value:%s' % stats.spearmanr(tc_sizes, rates))
	print('model of ref size vs. improv rate per cycle')
	print('corr coefficient:%s; p-value:%s' % stats.spearmanr(ref_mod_sizes, rates))
	print('')
#	simple_scatter(tc_sizes, rates, folder)

def get_improv_rate(archive):
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(archive)
	nb_cycles = len([val for sublist in Y_sq_dev for val in sublist])
	Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
	improv = Y_flattened[0] - Y_flattened[-1]
	improv_rate = improv/nb_cycles
	return improv_rate

def get_improv(archive):
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(archive)
	nb_cycles = len([val for sublist in Y_sq_dev for val in sublist])
	Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
	improv = Y_flattened[0] - Y_flattened[-1]
	rel_improv = improv/Y_flattened[0]
	return rel_improv

def get_ref_mod_size(archive):
	size = len(archive.model_of_ref.intermediate_activities)
	return size

def get_TC_size(archive):
	size = len(archive.mnm_activities)
	return size

def test_differences_all_exps_vs_two_factor():
	all_exps = get_data_for_development_and_drift_one_folder('not_crashed/first_batch_all_exps')
	two_factor = get_data_for_development_and_drift_one_folder('not_crashed/first_batch_two_factor')
	#
	#remove tc12
	tc_rep = [tpl for tpl in yield_tc_rep()][:-3]
	all_exps_improv = []
	all_exps_rate = []
	all_exps_rate_time = []
	# 'tot_impr_prc'
	all_exps_total = []
	two_factor_improv = []
	two_factor_rate = []
	two_factor_rate_time = []
	two_factor_total = []
	#
	for tpl in tc_rep:
		if all_exps[tpl[0]][tpl[1]]['up_to_final_drft'] != None and two_factor[tpl[0]][tpl[1]]['up_to_final_drft'] != None:
			all_exps_improv.append(all_exps[tpl[0]][tpl[1]]['up_to_final_drft'])
			two_factor_improv.append(two_factor[tpl[0]][tpl[1]]['up_to_final_drft'])
		else:
			pass
		if all_exps[tpl[0]][tpl[1]]['improv_rate_abs_cycles'] != None and two_factor[tpl[0]][tpl[1]]['improv_rate_abs_cycles'] != None:
			all_exps_rate.append(all_exps[tpl[0]][tpl[1]]['improv_rate_abs_cycles'])
			two_factor_rate.append(two_factor[tpl[0]][tpl[1]]['improv_rate_abs_cycles'])
		else:
			pass
		if all_exps[tpl[0]][tpl[1]]['improv_rate_abs_time'] != None and two_factor[tpl[0]][tpl[1]]['improv_rate_abs_time'] != None:
			all_exps_rate_time.append(all_exps[tpl[0]][tpl[1]]['improv_rate_abs_time'])
			two_factor_rate_time.append(two_factor[tpl[0]][tpl[1]]['improv_rate_abs_time'])
		else:
			pass
		if all_exps[tpl[0]][tpl[1]]['tot_impr_prc'] != None and two_factor[tpl[0]][tpl[1]]['tot_impr_prc'] != None:
			all_exps_total.append(all_exps[tpl[0]][tpl[1]]['tot_impr_prc'])
			two_factor_total.append(two_factor[tpl[0]][tpl[1]]['tot_impr_prc'])
		else:
			pass
	#
	res_improv = stats.ttest_rel(all_exps_improv, two_factor_improv)
	res_rate = stats.ttest_rel(all_exps_rate, two_factor_rate)
	res_rate_time = stats.ttest_rel(all_exps_rate_time, two_factor_rate_time)
	res_total = stats.ttest_rel(all_exps_total, two_factor_total)

	print('test difference all experiments vs only two factor growth exp (two-tail rel t-test)')
	print('improvement: (w/o last drift)')
	print(res_improv)
	print('improvement rate per cycle')
	print(res_rate)
	print('improvement rate in time')
	print(res_rate_time)
	print('improvement: total change')
	print(res_total)

def ttest_drifting_useful_one_folder(folder):
	# get data
	before = []
	total = []
	paths = get_all_paths(folder)
	for path in paths:
		improv_before_first_drift, improv_total = get_info_drifting_useful('/'.join([folder, path]))
		before.append(improv_before_first_drift)
		total.append(improv_total)
	res = stats.ttest_rel(before, total)
	# calculate number of times when drifting was useful,
	# made no dif, or was detrimental
	success = 0
	equiv = 0
	fails = 0
	for bef, tot in zip(before, total):
		if tot > bef:
			success += 1
		elif tot < bef:
			fails += 1
		else:
			equiv += 1
	# calculate avgs
	avg_std_before = (mean(before), pstdev(before))
	avg_std_total = (mean(total), pstdev(total))
	#
	print('is drifting useful (ttest)? %s' % folder)
	print('before: avg %s; stddev %s' % avg_std_before)
	print('total: avg %s; stddev %s' % avg_std_total)
	print('succ.: %s/%s/%s' % (success, fails, equiv))
	print(res)
	print('')

def get_info_drifting_useful(path):
	# collects data also for situations where there is no drift
	# this makes sense, since if drifting would be very rare
	# I should report no significant difference in practice
	arch = read_archive(path)
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
	Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
	improv_before_first_drift = Y_sq_dev[0][0] - Y_sq_dev[0][-1]
	improv_total = Y_sq_dev[0][0] - Y_flattened[-1]
	return improv_before_first_drift, improv_total

def compare_time_err30_err60():
	err_30_folders = [
	'not_crashed/err30_mod2',
	'not_crashed/err30_mod4',
	'not_crashed/err30_mod6']
	err_60_folders = [
	'not_crashed/err60_mod2',
	'not_crashed/err60_mod4',
	'not_crashed/err60_mod6']

	err_30_times = get_time_data_mult_folders(err_30_folders)
	err_60_times = get_time_data_mult_folders(err_60_folders)

	res_ttest = stats.ttest_rel(err_30_times, err_60_times)
	succ, trials, res_binom = compare_time_binom(err_30_times, err_60_times)

	print('total time w/o last drift 30 vs 60')
	print('ttest:')
	print(res_ttest)
	print('binom test')
	print('60 is shorter: %s/%s' % (succ, trials))
	print('binom: %s' % res_binom)
	print('stats:')
	print('30 avg: %s; std dev: %s' % (mean(err_30_times), pstdev(err_30_times)))
	print('60 avg: %s; std dev: %s' % (mean(err_60_times), pstdev(err_60_times)))


def compare_time_binom(folder1, folder2):
	t2_was_shorter = 0
	t2_was_not_shorter = 0
	for t1, t2 in zip(folder1, folder2):
		if t1 > t2:
			t2_was_shorter += 1
		else:
			t2_was_not_shorter += 1
	res_binom = stats.binom_test([t2_was_shorter, t2_was_not_shorter])
	return t2_was_shorter, t2_was_not_shorter+t2_was_shorter, res_binom

def get_time_data_mult_folders(folders):
	times = []
	for folder in folders:
		times.extend(get_time_data_one_folder(folder))
	return times

def get_time_data_one_folder(folder):
	paths = get_all_paths(folder)
	# sorting to get the order repeatable (ttest rel!)
	paths.sort(key = lambda x: re.split('conf.._', x)[1])
	times = []
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(arch)
		Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
		# w/o last drift
		time = X_flattened[-1]
		times.append(time)
	return times

def compare_best_initial_with_avg_final_folder(folder):
	# collect data
	successess = 0
	failures = 0
	differences = []
	best_inits = []
	final_avgs = []
	paths = get_all_paths(folder)
	for path in paths:
		full_path = '/'.join([folder,path])
		is_final_better, difference, best_init, final_avg = compare_best_initial_with_avg_final(full_path)
		best_inits.append(best_init)
		final_avgs.append(final_avg)
		differences.append(difference)
		if is_final_better == True:
			successess += 1
		else:
			failures += 1
	# analyse
	res_binom = stats.binom_test([successess, failures])
	avg_diff = mean(differences)
	std_dev_diff = pstdev(differences)
	res_ttest = stats.ttest_rel(best_inits, final_avgs)
	#print
	print(folder)
	print('stats:')
	print('best inits: mean %s; std %s' % (mean(best_inits), pstdev(best_inits)))
	print('final_avg: mean %s; std %s' % (mean(final_avgs), pstdev(final_avgs)))
	print('successes: %s/%s' % (successess, successess + failures))
	print('binom. test:')
	print(res_binom)
	print('avg difference: %s; std.dev: %s' % (avg_diff, std_dev_diff))
	print('ttest rel:')
	print(res_ttest)
	print('')

def compare_best_initial_with_avg_final(path):
	# get initial models
	archive = read_archive(path)
	model_of_ref = archive.model_of_ref
	all_initial_models = get_all_initial_models(archive.development_history)
	# calculate initial errors
	init_errors = [len(model_of_ref.intermediate_activities ^ m.intermediate_activities) for m in all_initial_models]
	best_init = min(init_errors)
	# get final avg error
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(archive)
	Y_flattened, X_flattened = flatten_plot_with_drifts_output(Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift, False)
	# difference
	is_final_better = Y_flattened[-1] < best_init
	difference = (best_init/Y_flattened[0]) - (Y_flattened[-1]/Y_flattened[0])
	return is_final_better, difference, best_init, Y_flattened[-1]

def test_is_drifting_improving_models(folder):
	drifting_info = extract_drifting_phase_changes_folder(folder)
	print(folder)
	test_is_drifting_improving_models_binom(drifting_info)
	test_is_drifting_improving_models_ttest(drifting_info)
	print('')

def test_is_drifting_improving_models_binom(drifting_info):
	successes = 0
	failures = 0
	for tpl in drifting_info:
		#if improved (error lowered)
		if tpl[0] > tpl[1]:
			successes += 1
		else:
			failures += 1
	res_binom = stats.binom_test([successes, failures])
	print('successes: %s/%s' % (successes, successes + failures))
	print('binom. test:')
	print(res_binom)

def test_is_drifting_improving_models_ttest(drifting_info):
	beginings = [x[0] for x in drifting_info]
	ends = [x[1] for x in drifting_info]
	res_ttest = stats.ttest_rel(beginings, ends)
	print('ttest:')
	print(res_ttest)

def extract_drifting_phase_changes_folder(folder):
	drifting_info = []
	paths = get_all_paths(folder)
	for path in paths:
		full_path = '/'.join([folder,path])
		drifting_info.extend(extract_drifting_phase_changes_path(full_path))
	return drifting_info

def extract_drifting_phase_changes_path(path):
	# [(before_drft, end_drft), (,), (,), ...]
	drifting_info = []
	archive = read_archive(path)
	Y_sq_dev, X_sq_dev, Y_sq_drift, X_sq_drift = plot_with_drifts(archive)
	# extract drifting info tuples
	counter = 0
	for drift_period in Y_sq_drift:
		end = drift_period[-1]
		begining = Y_sq_dev[counter][-1]
		drifting_info.append((begining,end))
		counter += 1
	return drifting_info


#
# analysing models
#
def print_all_sizes_of_models(folder_list):
	for folder in folder_list:
		paths = get_all_paths(folder)
		for path in paths:
			print_sizes_of_models('/'.join([folder, path]))

def print_sizes_of_models(path):
	archive = read_archive(path)
	model_of_ref = archive.model_of_ref
	all_initial_models = get_all_initial_models(archive.development_history)
	print(path)
	print('model of reference\'s size: %s' % len(model_of_ref.intermediate_activities))
	print('all initial models:')
	for model in all_initial_models:
		print('mod id: %s; size: %s' % (model.ID, len(model.intermediate_activities)))
	print('')

def get_all_initial_models(dev_history):
	for event in dev_history:
		if isinstance(event, InitialModels):
			return event.models

def get_revised_initial_models(dev_history):
	# debugging utility
	# returns working models from the end of the preparation stage
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

#
# time analysis
#
def profile_time_usage():
	folders = [
		'not_crashed/first_batch_all_exps',
		'not_crashed/first_batch_two_factor',
		'not_crashed/err0_mod2',
		'not_crashed/err0_mod4',
		'not_crashed/err0_mod6',
		'not_crashed/err30_mod2',
		'not_crashed/err30_mod4',
		'not_crashed/err30_mod6',
		'not_crashed/err60_mod2',
		'not_crashed/err60_mod4',
		'not_crashed/err60_mod6',
		]
	#
	for folder in folders:
		print(folder)
		profile_time_usage_folder(folder)
		print('\n\n')

def profile_time_usage_folder(folder):
	paths = get_all_paths(folder)
	paths.sort(key = lambda x: re.split('conf.._', x)[1])
	# create a dictionary for results
	all_res = {path[-7:-3]: {'succ_exp_design':[], 'failed_exp_design':[], 'testing_and_revision':[], 'drifting':[]} for path in paths}
	#
	for path in paths:
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		res = profile_time_usage_archive(arch)
		for key in res.keys():
			all_res[path[-7:-3]][key].extend(res[key])
	# stats
	for TC in sorted(all_res.keys()):
		print(TC)
		for stat in sorted(all_res[TC].keys()):
			print(stat)
			if all_res[TC][stat] == []:
				continue
			print('avg: %s; std: %s;' % (mean(all_res[TC][stat]), pstdev(all_res[TC][stat])))

def profile_time_usage_archive(archive):
	# get events list w/o the last drift
	last_index = 0
	drifting = False
	for event in archive.development_history:
		# drift starts with that event
		if isinstance(event, AllModelsEmpiricallyEquivalent) and (drifting == False):
			drifting = True
			last_index = archive.development_history.index(event)-1
		# drift stops with that event
		elif isinstance(event, ChosenExperiment) and (drifting == True):
			drifting = False
			last_index = archive.development_history.index(event)
		# otherwise, if not drifting, events should be included:
		elif drifting == False:
			last_index = archive.development_history.index(event)
	# extract events w/o the last drifting
	events_wo_last_drifting = archive.development_history[0:last_index+1]
	# calculate time for each operation:
	succ_exp_design = []
	failed_exp_design = []
	testing_and_revision = []
	drifting = []
	t_and_r = False
	#
	start = None
	drifting_start = None
	for event in events_wo_last_drifting:
		# starting exp design
		if isinstance(event, CheckPointSuccess):
			start = event.timestamp
		# ending in failure (start/continuation of drifting)
		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			failed_exp_design.append(event.timestamp - start)
			start = None
		# eding successfully (if drifting, then ends)
		elif isinstance(event, ChosenExperiment):
			succ_exp_design.append(event.timestamp - start)
			start = None
		# testing consistency of models and revision of refuted ones:
		elif isinstance(event, AcceptedResults):
			start = event.timestamp
			t_and_r = True
		# end testing_and_revision:
		elif isinstance(event, UpdatedModelQuality) and (t_and_r == True):
			previous = events_wo_last_drifting[events_wo_last_drifting.index(event)-1]
			testing_and_revision.append(previous.timestamp - start)
			start = None
			t_and_r = False
		# drifting:
		if isinstance(event, AllModelsEmpiricallyEquivalent):
			if drifting_start != None:
				drifting.append(event.timestamp - drifting_start)
			drifting_start = event.timestamp
		elif isinstance(event, ChosenExperiment) and (drifting_start != None):
			drifting.append(event.timestamp - drifting_start)
			drifting_start = None
	return {
		'succ_exp_design':succ_exp_design,
		'failed_exp_design':failed_exp_design,
		'testing_and_revision':testing_and_revision,
		'drifting':drifting
		}


#
# debugging utilities
#
def detect_all_import_of_setup():
	# debugging utility
	folder = 'pickled_archives'
	paths = get_all_paths(folder)
	for path in paths:
		print(path)
		full_path = '/'.join([folder,path])
		arch = read_archive(full_path)
		detect_import_of_setup(arch)
		print('\n\n\n')

def detect_import_of_setup(archive):
	# debugging utility
	# detects if import activity that imports setup_condition's entity
	# (compartment included) was added to the experiment
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

def get_TC_size_info():
	for folder in ['not_crashed/err0_mod2', 'not_crashed/first_batch_all_exps']:
		print(folder)
		paths = get_all_paths(folder)
		for path in paths:
			arch = read_archive('/'.join([folder, path]))
			print(path)
			print('# of entities: %s' % len(arch.mnm_entities))
			print('# of activities: %s' % len(arch.mnm_activities))
		print('\n\n')



new_err_0 = ['not_crashed/err0_mod2',
	'not_crashed/err0_mod4',
	'not_crashed/err0_mod6']
new_folders = ['not_crashed/err0_mod2',
	'not_crashed/err0_mod4',
	'not_crashed/err0_mod6',
	'not_crashed/err30_mod2',
	'not_crashed/err30_mod4',
	'not_crashed/err30_mod6',
	'not_crashed/err60_mod2',
	'not_crashed/err60_mod4',
	'not_crashed/err60_mod6']
old_folders = ['not_crashed/first_batch_all_exps',
	'not_crashed/first_batch_two_factor']

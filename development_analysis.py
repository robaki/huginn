#! /usr/bin/env python3

from archive import InitialModels, InitialResults, ChosenExperiment, NewResults, AcceptedResults, RefutedModels, RevisedModel, UpdatedModelQuality, AdditionalModels, RevisionFail, AdditModProdFail, ExpDesignFail, CheckPointFail, CheckPointSuccess, RevisedIgnoredUpdate
import pickle
from mnm_repr import Activity

def read_archive(path):
	pkl_file = open(path, 'rb')
	archive = pickle.load(pkl_file)
	pkl_file.close()
	return archive

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







arch = read_archive('pickled_archives/archive_2015_3_13_17_21_48')
print_development_history(arch)
#print('\navailable activities (activities, )')
#print([x.ID for x in arch.mnm_activities])
#print([x.ID for x in arch.import_activities])

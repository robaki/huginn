#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

from mnm_repr import CellMembrane, Cytosol, EndoplasmicReticulum, ERMembrane, Medium, GolgiApparatus, GolgiMembrane, LipidParticle, MitochInnerMembrane, MitochMatrix, Nucleus, PeroxisomalMembrane, Peroxisome, VacuolarMembrane, Vacuole

from multiprocessing import Pool
from exp_cost_model import CostModel
import pickle
from archive import Archive, InitialModels
from experiment_module import BasicExpModuleNoCosts
from experiment_module import BasicExpModuleWithCosts
from oracle import Oracle, SloppyOracle
from overseer import OverseerWithModQuality
from overseer import OverseerNoQuality
from quality_module import AllCovered
from quality_module import AllCoveredMinusIgnored
from quality_module import NewCovered
from quality_module import NewCoveredMinusIgnored
from revision_module import RevCAddB
from revision_module import RevCAddR
from revision_module import RevCIAddB# template: the best
from revision_module import RevCIAddR# template: random


class Evaluator:
	def __init__(self):
		self.compartments = [CellMembrane(), Cytosol(), EndoplasmicReticulum(),
			ERMembrane(), Medium(), GolgiApparatus(), GolgiMembrane(), LipidParticle(),
			MitochInnerMembrane(), MitochMatrix(), Nucleus(), PeroxisomalMembrane(),
			Peroxisome(), VacuolarMembrane(), Vacuole()]


	def test_all_single_process(self):
		for (case, suffix) in self.test_case_loader():
			for overseer in self.system_configuration_generator(case, suffix):
				overseer.run()


	def test_all_multiprocess(self):
		with Pool(processes = 2) as pool:
			result = pool.map(self.test_generator, self.test_case_loader())
			print(result)


	def test_case_loader(self):
		# small: 1, 2, 3, 4, 5, 6
		# medium: 7, 8, 9, 10, 11
		# too big: 11+
		# serwer simulations: staring with the biggest to see RAM consumption and react if problems
		for case_number in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:# 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
			case_file = 'test_cases/case_%s' % case_number
			for repetition in range(3):
				pkl_file = open(case_file, 'rb')
				case = pickle.load(pkl_file)
				pkl_file.close()
				if len(str(case_number)) == 1:
					suffix = 'tc0%s_r%s' % (case_number, repetition)
					yield (case, suffix)
				else:
					suffix = 'tc%s_r%s' % (case_number, repetition)
					yield (case, suffix)


	def system_configuration_generator(self, case, first_suffix):
		for qual in [AllCoveredMinusIgnored]: # NewCoveredMinusIgnored
			for rev in [RevCIAddR]: # RevCIAddB
				for threshold_addit_mods in [6]: #2, 4, 6, 8
					for stop_threshold in [8]: # just 8 

						suffix = 'conf%s_%s' % (self.get_suffix((qual, rev, threshold_addit_mods, stop_threshold)), first_suffix)

						archive_ = Archive()
						archive_.mnm_compartments = self.compartments # added access to all compartments
						archive_.model_of_ref = case['model_of_ref']

						# recording entities with proper IDs: base versions and derived versions
						# these entities were involved in producing new versions and are handled below, not here
						entities_to_skip = list(case['ents_base_and_derived'].keys())
						for list_of_ents in case['ents_base_and_derived'].values():
							entities_to_skip.extend(list_of_ents)

						for ent in case['all_entities']:
							if ent in entities_to_skip:
								continue
							# not-skipped activities:
							ent.ID = archive_.get_new_ent_id()
							archive_.mnm_entities.append(ent)

						for ent in case['ents_base_and_derived'].keys():
							derv_ents = case['ents_base_and_derived'][ent]# need to copy this now, dictionary stops working after ID change
							ent.ID = archive_.get_new_ent_id()
							archive_.mnm_entities.append(ent)
							for derv_ent in derv_ents:
								derv_ent.ID = ent.ID
								archive_.mnm_entities.append(derv_ent)

						for act in case['all_activities']:
							act.ID = archive_.get_new_act_id()
							archive_.mnm_activities.append(act)

						for act in case['add_import_activities']:
							act.ID = archive_.get_new_act_id()
							archive_.import_activities.append(act)

						#####
#						for act in archive_.mnm_activities + archive_.import_activities:
#							print(act.reversibility)

						#####
		
						archive_.record(InitialModels(case['initial_models']))

						qual_m = qual(archive_)
						rev_m = rev(archive_, sfx=suffix)

						cost_model = CostModel(case['all_entities'],
							self.compartments, case['all_activities'],
							case['model_of_ref'].setup_conditions,
							case['add_import_activities'])
						cost_model.set_all_basic_costs_to_1()
						cost_model.calculate_derived_costs(case['all_activities'])
						cost_model.remove_None_valued_elements()

						exp_m = BasicExpModuleWithCosts(archive_, cost_model, sfx=suffix) # !!!!! switched from no costs

						# SloppyOracle
						oracle_ = SloppyOracle(archive_, case['entities_ref'],
							case['activities_ref'], case['model_of_ref'],
							case['all_entities'], self.compartments,
							case['all_activities'], sfx=suffix, error_parameter=0.60)# , error_parameter=0.60

						max_numb_cycles = 10000 # 
						max_time = 24 # 

						yield OverseerWithModQuality(archive_, rev_m, exp_m,
							oracle_, threshold_addit_mods, qual_m, max_numb_cycles,
							max_time, suffix, stop_threshold)


	def test_generator(self, tpl):
		for overseer in self.system_configuration_generator(tpl[0], tpl[1]):
			overseer.run()


	def get_suffix(self, tpl):
		suff_dict = {
			(AllCoveredMinusIgnored,RevCIAddR,2,8):'00',
			(AllCoveredMinusIgnored,RevCIAddR,4,8):'01',
			(AllCoveredMinusIgnored,RevCIAddR,6,8):'02',
			(AllCoveredMinusIgnored,RevCIAddR,8,8):'03'
#			(AllCoveredMinusIgnored,RevCIAddB,2,2):'',
#			(AllCoveredMinusIgnored,RevCIAddB,2,4):'',
#			(AllCoveredMinusIgnored,RevCIAddB,2,8):'',
#			(AllCoveredMinusIgnored,RevCIAddB,4,2):'',
#			(AllCoveredMinusIgnored,RevCIAddB,4,4):'',
#			(AllCoveredMinusIgnored,RevCIAddB,4,8):'',
#			(AllCoveredMinusIgnored,RevCIAddB,8,2):'',
#			(AllCoveredMinusIgnored,RevCIAddB,8,4):'',
#			(AllCoveredMinusIgnored,RevCIAddB,8,8):'',
#			(NewCoveredMinusIgnored,RevCIAddR,2,2):'',
#			(NewCoveredMinusIgnored,RevCIAddR,2,4):'',
#			(NewCoveredMinusIgnored,RevCIAddR,2,8):'',
#			(NewCoveredMinusIgnored,RevCIAddR,4,2):'',
#			(NewCoveredMinusIgnored,RevCIAddR,4,4):'',
#			(NewCoveredMinusIgnored,RevCIAddR,4,8):'',
#			(NewCoveredMinusIgnored,RevCIAddR,8,2):'',
#			(NewCoveredMinusIgnored,RevCIAddR,8,4):'',
#			(NewCoveredMinusIgnored,RevCIAddR,8,8):'',
#			(NewCoveredMinusIgnored,RevCIAddB,2,2):'',
#			(NewCoveredMinusIgnored,RevCIAddB,2,4):'',
#			(NewCoveredMinusIgnored,RevCIAddB,2,8):'',
#			(NewCoveredMinusIgnored,RevCIAddB,4,2):'',
#			(NewCoveredMinusIgnored,RevCIAddB,4,4):'',
#			(NewCoveredMinusIgnored,RevCIAddB,4,8):'',
#			(NewCoveredMinusIgnored,RevCIAddB,8,2):'',
#			(NewCoveredMinusIgnored,RevCIAddB,8,4):'',
#			(NewCoveredMinusIgnored,RevCIAddB,8,8):''
			}

		return suff_dict[tpl]



evaluator = Evaluator()
evaluator.test_all_single_process()
#evaluator.test_all_multiprocess()

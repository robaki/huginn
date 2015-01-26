#! /usr/bin/env python3

from archive import UpdatedModelQuality# model, new_quality

class QualityModule:
	def __init__(self, archive):
		self.archive = archive


class NumberAllCovered(QualityModule):
	def __init__(self, archive):
		QualityModule.__init__(self, archive)

	def calculate_model_score(self, model): # 'negative' quality: number of ignored results
		model.score = len(model.results_covered)

	def calculate_models_quality(self):
		for model in self.archive.working_models:
			if model.quality == model.score:
				pass
			else:
				model.quality = model.score
				self.archive.record(UpdatedModelQuality(model, model.quality))


class NumberAllCoveredMinusIgnored(QualityModule):
	def __init__(self, archive):
		QualityModule.__init__(self, archive)

	def calculate_model_score(self, model): # number of all results covered - ignored
		model.score = len(model.results_covered) - len(model.ignored_results)

	def calculate_models_quality(self):
		all_scores = [models.score for model in self.archive.working_models]
		smallest = min(all_scores)
		if smallest <= 1:# needs normalisation
			for model in self.archive.working_models:
				if model.quality == model.score + abs(smallest):
					pass
				else:
					model.quality = model.score + abs(smallest)
					self.archive.record(UpdatedModelQuality(model, model.quality))
		else:
			for model in self.archive.working_models:
				if model.quality == model.score:
					pass
				else:
					model.quality = model.score
					self.archive.record(UpdatedModelQuality(model, model.quality))


class NumberNewCovered(QualityModule):
	def __init__(self, archive):
		QualityModule.__init__(self, archive)

	def calculate_model_score(self, model): # number of _new_ results covered
		new_results = self.archive.get_results_after_model(model)
		new_covered = set(new_results) & set(model.results_covered)
		model.score = len(new_covered)

	def calculate_models_quality(self):
		for model in self.archive.working_models:
			if model.quality == model.score:
				pass
			else:
				model.quality = model.score
				self.archive.record(UpdatedModelQuality(model, model.quality))


class NumberNewCoveredMinusIgnored(QualityModule):
	def __init__(self, archive):
		QualityModule.__init__(self, archive)

	def calculate_model_score(self, model): # number of _new_ results covered - ignored
		new_results = self.archive.get_results_after_model(model)
		new_covered = set(new_results) & set(model.results_covered)
		model.score = len(new_covered) - len(model.ignored_results)

	def calculate_models_quality(self):
		all_scores = [models.score for model in self.archive.working_models]
		smallest = min(all_scores)
		if smallest <= 1:# needs normalisation
			for model in self.archive.working_models:
				if model.quality == model.score + abs(smallest):
					pass
				else:
					model.quality = model.score + abs(smallest)
					self.archive.record(UpdatedModelQuality(model, model.quality))
		else:
			for model in self.archive.working_models:
				if model.quality == model.score:
					pass
				else:
					model.quality = model.score
					self.archive.record(UpdatedModelQuality(model, model.quality))


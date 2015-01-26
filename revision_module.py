#! /usr/bin/env python3

from archive import RefutedModels
from archive import RevisedModel

class RevisionModule:
	def __init__(self, archive):
		self.archive = archive

	def <some auxiliary function>

	def <some auxiliary function>


class RevC(RevisionModule): # minimise changes
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

	def test_and_revise_all(self):
		for model in self.archive.working_models:
			self.check_consistency(model)

		for model in self.archive.working_models:
			self.revise(model)

	def check_consistency(self, model):

	def revise(self, model):



class RevCI(RevisionModule): # minimise changes and ignored
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

	def test_and_revise_all(self):
		for model in self.archive.working_models:
			self.check_consistency(model)

		for model in self.archive.working_models:
			self.revise(model)

		for model in self.archive.working_models:
			self.update_quality(model)


	def check_consistency(self, model):

	def revise(self, model):

	def update_quality(self):



class RevCwI(RevisionModule): # revision minimise changes weighted and ignored
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

	def test_and_revise_all(self):
		for model in self.archive.working_models:
			self.check_consistency(model)

		for model in self.archive.working_models:
			self.revise(model)

		for model in self.archive.working_models:
			self.update_quality(model)

	def check_consistency(self, model):

	def revise(self, model):

	def update_quality(self):



class RevCIw(RevisionModule): # revision minimise changes and ignored weighted
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

	def test_and_revise_all(self):
		for model in self.archive.working_models:
			self.check_consistency(model)

		for model in self.archive.working_models:
			self.revise(model)

		for model in self.archive.working_models:
			self.update_quality(model)

	def check_consistency(self, model):

	def revise(self, model):

	def update_quality(self):



class RevCwIw(RevisionModule): # revision minimise changes weighted and ignored weighted
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

	def test_and_revise_all(self):
		for model in self.archive.working_models:
			self.check_consistency(model)

		for model in self.archive.working_models:
			self.revise(model)

		for model in self.archive.working_models:
			self.update_quality(model)

	def check_consistency(self, model):

	def revise(self, model):

	def update_quality(self):






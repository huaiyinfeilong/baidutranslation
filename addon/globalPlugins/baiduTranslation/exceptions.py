# coding=utf-8

import addonHandler


addonHandler.initTranslation()


class TranslationException(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
			# Translators: Translation failed
			translationFailed = _("Translation failed: ")
			return f"{_(translationFailed)}{self.message}"

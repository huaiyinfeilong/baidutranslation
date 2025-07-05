# coding=utf-8

import api
import globalPluginHandler
import scriptHandler
import addonHandler
import speech
import nvwave
import os
import gui
import config
import wx
import webbrowser
from .translators import BaiduTranslator
from .languages import get_language_list
from .cacheData import CacheDataFile
from .exceptions import TranslationException
from speech.extensions import filter_speechSequence
import ui

# Path to the translation cache file.
TRANSLATION_CACHE_DATA_FILENAME = os.path.abspath(os.path.join(
	os.path.dirname(__file__), "../../../..", "baiduTranslation.cache-data"))

addonHandler.initTranslation()

_translator = BaiduTranslator()


class TranslationSettingsPanel(gui.settingsDialogs.SettingsPanel):
	# Translators: Settings panel title
	title = _("Baidu Translation")

	def makeSettings(self, sizer):
		helper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		source_language_list = target_language_list = [_(v) for k, v in get_language_list().items()]
		# Translators: Source language in the settings panel
		label_for_source_language_choice = _("Source language")
		# Translators: Target language in the settings panel
		label_for_target_language_choice = _("Target language")
		self.sourceLanguageChoice = helper.addLabeledControl(
			label_for_source_language_choice,
			wx.Choice,
			choices=source_language_list)
		self.targetLanguageChoice = helper.addLabeledControl(
			label_for_target_language_choice,
			wx.Choice,
			choices=target_language_list)
		language_code_list = [k for k in get_language_list().keys()]
		self.sourceLanguageChoice.Select(language_code_list.index(config.conf["baiduTranslation"]["from"]))
		self.targetLanguageChoice.Select(language_code_list.index(config.conf["baiduTranslation"]["to"]))
		self.autoFromLangOption = helper.addItem(
			# Translators: the label for the Auto from language checkbox
			wx.CheckBox(self, label=_("Automatically identify the source language"))
		)
		self.autoFromLangOption.SetValue(config.conf["baiduTranslation"]["autoFromLang"])
		# Automatic translation combobox
		self._automatic_translation_list = [
			# Translators: option disabled
			_("Disabled"),
			# Translations: option normal
			_("Normal"),
			# Translators: option reverse
			_("Reverse")
		]
		# Translators: the label for of the automatic translation combobox
		label_for_automatic_translation_choice = _("Automatic translation")
		self.automaticTranslationChoice = helper.addLabeledControl(
			label_for_automatic_translation_choice,
			wx.Choice,
			choices=self._automatic_translation_list
		)
		self.automaticTranslationChoice.Select(config.conf["baiduTranslation"]["autoTrans"])
		# Translators: The label for my APP ID textbox
		my_app_id_label = _("My APP ID")
		self.myAppIdTextCtrl = helper.addLabeledControl(
			_(my_app_id_label),
			wx.TextCtrl,
		)
		self.myAppIdTextCtrl.SetValue(config.conf["baiduTranslation"]["myAppId"])
		# Translators: The label for my APP secret textbox
		my_app_secret_label = _("My APP secret")
		self.myAppSecretTextCtrl = helper.addLabeledControl(
			_(my_app_secret_label),
			wx.TextCtrl,
		)
		self.myAppSecretTextCtrl.SetValue(config.conf["baiduTranslation"]["myAppSecret"])
		self.labelForRegistrationBaiduTranslationApi = _("Register Baidu Translation API")
		self.registerBaiduTranslationApiButton = helper.addItem(
			wx.Button(self, label=self.labelForRegistrationBaiduTranslationApi)
		)
		self.registerBaiduTranslationApiButton.Bind(wx.EVT_BUTTON, self.onRegisterBaiduTranslationApiButtonClick)
		# Translators: Label for the clear cache button
		self.labelForClearCacheButton = _("Clear cache (current item count: {})")
		cacheFile = CacheDataFile()
		cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		label = f"{_(self.labelForClearCacheButton)}".format(cacheFile.getItemCount())
		self.clearCacheButton = helper.addItem(
			wx.Button(self, label=label)
		)
		self.clearCacheButton.Bind(wx.EVT_BUTTON, self.onClearCacheButtonClick)

	def onRegisterBaiduTranslationApiButtonClick(self, event):
		url = "https://fanyi-api.baidu.com/"
		webbrowser.open(url)

	def onClearCacheButtonClick(self, event):
		cacheFile = CacheDataFile()
		cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		cacheFile.clear()
		label = f"{_(self.labelForClearCacheButton)}".format(cacheFile.getItemCount())
		self.clearCacheButton.SetLabel(label)

	def onSave(self):
		config.conf["baiduTranslation"]["autoFromLang"] = self.autoFromLangOption.IsChecked()
		config.conf["baiduTranslation"]["from"] = [
			key for key in get_language_list().keys()
			][
		self.sourceLanguageChoice.GetSelection()
		]
		config.conf["baiduTranslation"]["to"] = [
			key for key in get_language_list().keys()
			][
		self.targetLanguageChoice.GetSelection()
		]
		config.conf["baiduTranslation"]["autoTrans"] = self.automaticTranslationChoice.GetSelection()
		config.conf["baiduTranslation"]["myAppId"] = self.myAppIdTextCtrl.GetValue()
		config.conf["baiduTranslation"]["myAppSecret"] = self.myAppSecretTextCtrl.GetValue()
		appId = config.conf["baiduTranslation"]["myAppId"]
		appSecret = config.conf["baiduTranslation"]["myAppSecret"]
		_translator.initialize_translator(appId, appSecret)

# Translators: Category Name
CATEGORY_NAME = _("Baidu Translation")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		# Stores the last text spoken by NVDA, used for manual translation.
		self._last_spoken_text = ""
		# A flag to prevent recursive translation of our own speech output.
		self._is_speaking_translation_result = False
		# Handles caching of translation results to speed up repeated translations.
		self._cacheFile = CacheDataFile()
		self._cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		# Caches the last successful translation result for the copy command.
		self._last_translation_result = ""
		# A flag to defer the copy action until after an async translation completes.
		self._copyFlag = False
		self._consecutive_failures = 0
		confspec = {
			"from": "string(default='en')",
			"to": "string(default='zh')",
			"autoFromLang": "boolean(default=True)",
			"autoTrans": "integer(default=0)",
			"myAppId": "string(default='')",
			"myAppSecret": "string(default='')"
		}
		config.conf.spec["baiduTranslation"] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(TranslationSettingsPanel)
		appId = config.conf["baiduTranslation"]["myAppId"]
		appSecret = config.conf["baiduTranslation"]["myAppSecret"]
		_translator.initialize_translator(appId, appSecret)
		# Register speech sequence filter.
		filter_speechSequence.register(self.on_speech_sequence)

	def terminate(self):
		filter_speechSequence.unregister(self.on_speech_sequence)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(TranslationSettingsPanel)
		super(GlobalPlugin, self).terminate()

	def on_speech_sequence(self, sequence):
		"""
		The handler registered to filter_speechSequence, responsible for automatic translation.
		"""
		# If this flag is set, it means we are speaking our own translation result.
		# We must pass the sequence through unmodified and reset the flag to break the recursion loop.
		if self._is_speaking_translation_result:
			self._is_speaking_translation_result = False
			return sequence
		# Extract text to be spoken and save it for manual translation scripts.
		text_data = "".join([item for item in sequence if isinstance(item, str) and item.strip()])
		if text_data:
			self._last_spoken_text = text_data
		# Check if automatic translation is enabled.
		auto_trans_mode = config.conf["baiduTranslation"]["autoTrans"]
		if auto_trans_mode == 0 or not self._last_spoken_text:
			return sequence
		# Determine translation direction.
		is_reverse = (auto_trans_mode == 2)
		from_language, to_language = self._get_translation_languages(reverse=is_reverse)
		self._translate(from_language, to_language, self._last_spoken_text)
		# Return an empty sequence to cancel the original speech.
		# The translated result will be spoken in the self._onResult callback.
		return []

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Translate what you just heard, double click to copy translation results to the clipboard
		description=_("Translate what you just heard, double click to copy translation results to the clipboard"),
		gesture="kb:NVDA+W")
	def script_translate(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 1:
			self._copyTranslationResultToClipboard()
			return
		self._playSound()
		from_language, to_language = self._get_translation_languages(reverse=False)
		self._translate(from_language, to_language, self._last_spoken_text)

	# Translators: Reverse translate what you just heard, double click to copy translation results to the clipboard
	@scriptHandler.script(
		category=CATEGORY_NAME,
		description=_("Reverse translate what you just heard, double click to copy translation results to the clipboard"),
		gesture="kb:NVDA+SHIFT+W")
	def script_reverseTranslate(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 1:
			self._copyTranslationResultToClipboard()
			return
		self._playSound(True)
		from_language, to_language = self._get_translation_languages(reverse=True)
		self._translate(from_language, to_language, self._last_spoken_text)

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Switch automatic translation mode
		description=_("Switch automatic translation mode"),
		gesture="kb:NVDA+F8")
	def script_switchAutomaticTranslationMode(self, gesture):
		self._consecutive_failures = 0
		option_names = [
			# Translators: Automatic translation mode set to disabled
			_("Disable automatic translation"),
			# Translators: Automatic translation mode set to normal
			_("Normal automatic translation"),
			# Translators: Automatic translation mode set to reverse
			_("Reverse automatic translation")
		]
		current_mode_index = config.conf["baiduTranslation"]["autoTrans"]
		new_mode_index = (current_mode_index + 1) % len(option_names)
		config.conf["baiduTranslation"]["autoTrans"] = new_mode_index
		ui.message(option_names[new_mode_index])

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Translate the content in the clipboard, double click to copy translation results to the clipboard
		description=_("Translate the content in the clipboard, double click to copy translation results to the clipboard"),
		gesture="kb:NVDA+CONTROL+W")
	def script_clipboardTranslation(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 1:
			self._copyTranslationResultToClipboard()
			return
		self.clipboard_translation()

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Reverse translate the content in the clipboard, double click to copy translation results to the clipboard
		description=_("Reverse translate the content in the clipboard, double click to copy translation results to the clipboard"),
		gesture="kb:NVDA+CONTROL+SHIFT+W")
	def script_clipboardReverseTranslation(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 1:
			self._copyTranslationResultToClipboard()
			return
		self.clipboard_translation(True)

	def clipboard_translation(self, reverse=False):
		try:
			text = api.getClipData()
		except OSError:
			# This error can occur if the clipboard is empty or contains non-text data.
			text = None
		if not text:
			ui.message(_("No text in clipboard to translate."))
			return
		self._playSound(reverse)
		from_language, to_language = self._get_translation_languages(reverse=reverse)
		self._translate(from_language, to_language, text)

	def _get_translation_languages(self, reverse: bool = False) -> tuple[str, str]:
		"""Get the source and target languages based on configuration.
		Args:
			reverse: If True, swaps the source and target languages for reverse translation.
		Returns:
			A tuple containing the (source_language, target_language).
		"""
		source = "auto" if config.conf["baiduTranslation"]["autoFromLang"] else config.conf["baiduTranslation"]["from"]
		target = config.conf["baiduTranslation"]["to"]
		return (target, source) if reverse else (source, target)

	def _onResult(self, fromLanguage, toLanguage, source, target):
		"""Callback to handle the translation result."""
		# Set the flag before speaking the result to prevent recursion.
		self._is_speaking_translation_result = True
		if isinstance(target, TranslationException):
			self._consecutive_failures += 1
			if config.conf["baiduTranslation"]["autoTrans"] != 0 and self._consecutive_failures >= 3:
				config.conf["baiduTranslation"]["autoTrans"] = 0
				self._consecutive_failures = 0
				# Translators: Message announced when auto-translation is disabled due to repeated failures.
				ui.message(_("Auto-translation disabled due to repeated failures."))
			else:
				ui.message(str(target))
			self._copyFlag = False
			self._last_translation_result = ""
			return
		if target:
			self._consecutive_failures = 0
			if self._copyFlag:
				api.copyToClip(target, notify=True)
			else:
				ui.message(target)
			self._cacheFile.addCacheItem(fromLanguage, toLanguage, source, target)
			self._last_translation_result = target
			self._copyFlag = False

	def _playSound(self, reverse_translate=False):
		filename = "reverseTranslate.wav" if reverse_translate else "translate.wav"
		sound_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sound", filename))
		nvwave.playWaveFile(sound_filename)

	def _copyTranslationResultToClipboard(self):
		"""
			Copies the last translation result to the clipboard.
			If a translation is in progress, it sets a flag to copy the result upon completion.
		"""
		if _translator.isRunning():
			self._copyFlag = True
			ui.message(_("Will copy result when translation is complete."))
			return

		if self._last_translation_result:
			api.copyToClip(self._last_translation_result, notify=True)
			self._last_translation_result = ""
		else:
			ui.message(_("No translation results available for replication"))

	def _translate(self, fromLanguage, toLanguage, text):
		if not text:
			return
		result = self._cacheFile.getCacheItem(fromLanguage, toLanguage, text)
		if not result:
			_translator.translate(fromLanguage, toLanguage, text, self._onResult)
		else:
			self._onResult(fromLanguage, toLanguage, text, result)


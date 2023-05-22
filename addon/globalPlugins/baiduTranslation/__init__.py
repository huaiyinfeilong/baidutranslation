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
from .translators import BaiduTranslator
from .languages import get_language_list

addonHandler.initTranslation()

_translator = BaiduTranslator()


class TranslationSettingsPanel(gui.SettingsPanel):
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
		# Translators: The label for using share key checkbox
		using_share_key_label = _("Using share key")
		self.usingShareKeyCheckBox = helper.addItem(
			wx.CheckBox(self, label=_(using_share_key_label))
		)
		self.usingShareKeyCheckBox.SetValue(config.conf["baiduTranslation"]["usingShareKey"])
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
		config.conf["baiduTranslation"]["usingShareKey"] = self.usingShareKeyCheckBox.IsChecked()
		config.conf["baiduTranslation"]["myAppId"] = self.myAppIdTextCtrl.GetValue()
		config.conf["baiduTranslation"]["myAppSecret"] = self.myAppSecretTextCtrl.GetValue()
		appId = config.conf["baiduTranslation"]["shareAppId"] \
		if config.conf["baiduTranslation"]["usingShareKey"] else config.conf["baiduTranslation"]["myAppId"]
		appSecret = config.conf["baiduTranslation"]["shareAppSecret"] \
		if config.conf["baiduTranslation"]["usingShareKey"] else config.conf["baiduTranslation"]["myAppSecret"]
		_translator.initialize_translator(appId, appSecret)

# Translators: Category Name
CATEGORY_NAME = _("Baidu Translation")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		confspec = {
			"from": "string(default='en')",
			"to": "string(default='zh')",
			"autoFromLang": "boolean(default=True)",
			"autoTrans": "integer(default=0)",
			"usingShareKey": "boolean(default=True)",
			"shareAppId": "string(default='20230423001653246')",
			"shareAppSecret": "string(default='dyh8lxcVEZnBhJ8EiEwD')",
			"myAppId": "string(default='')",
			"myAppSecret": "string(default='')"
		}
		config.conf.spec["baiduTranslation"] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(TranslationSettingsPanel)
		appId = config.conf["baiduTranslation"]["shareAppId"] \
		if config.conf["baiduTranslation"]["usingShareKey"] else config.conf["baiduTranslation"]["myAppId"]
		appSecret = config.conf["baiduTranslation"]["shareAppSecret"] \
		if config.conf["baiduTranslation"]["usingShareKey"] else config.conf["baiduTranslation"]["myAppSecret"]
		_translator.initialize_translator(appId, appSecret)
		self._speak = speech.speech.speak
		speech.speech.speak = self.speak

	def __del__(self):
		speech.speech.speak = self._speak
		self._speak = None

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(TranslationSettingsPanel)

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Translate what you just heard
		description=_("Translate what you just heard"),
		gesture="kb:NVDA+W")
	def script_translate(self, gesture):
		self._playSound()
		if config.conf["baiduTranslation"]["autoFromLang"]:
			from_language = "auto"
		else:
			from_language = config.conf["baiduTranslation"]["from"]
		to_language = config.conf["baiduTranslation"]["to"]
		_translator.translate(from_language, to_language, self._data, self._onResult)

	# Translators: Reverse translate what you just heard
	@scriptHandler.script(
		category=CATEGORY_NAME,
		description=_("Reverse translate what you just heard"),
		gesture="kb:NVDA+SHIFT+W")
	def script_reverseTranslate(self, gesture):
		self._playSound(True)
		from_language = config.conf["baiduTranslation"]["from"]
		to_language = config.conf["baiduTranslation"]["to"]
		_translator.translate(to_language, from_language, self._data, self._onResult)

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Switch automatic translation mode
		description=_("Switch automatic translation mode"),
		gesture="kb:NVDA+F8")
	def script_switchAutomaticTranslationMode(self, gesture):
		option_name = [
			# Translators: Automatic translation mode set to disabled
			_("Disable automatic translation"),
			# Translators: Automatic translation mode set to normal
			_("Normal automatic translation"),
			# Translators: Automatic translation mode set to reverse
			_("Reverse automatic translation")
		]
		option_count = len(option_name)
		mode = option_name[(config.conf["baiduTranslation"]["autoTrans"] + option_count + 1) % option_count]
		self._speak([mode])
		config.conf["baiduTranslation"]["autoTrans"] = option_name.index(mode)

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Translate the content in the clipboard
		description=_("Translate the content in the clipboard"),
		gesture="kb:NVDA+CONTROL+W")
	def script_clipboardTranslation(self, gesture):
		self.clipboard_translation()

	@scriptHandler.script(
		category=CATEGORY_NAME,
		# Translators: Reverse translate the content in the clipboard
		description=_("Reverse translate the content in the clipboard"),
		gesture="kb:NVDA+CONTROL+SHIFT+W")
	def script_clipboardReverseTranslation(self, gesture):
		self.clipboard_translation(True)

	def clipboard_translation(self, reverse=False):
		text = api.getClipData()
		if not text:
			return
		self._playSound(reverse)
		from_language = "auto" if config.conf["baiduTranslation"]["autoFromLang"] \
		else config.conf["baiduTranslation"]["from"]
		to_language = config.conf["baiduTranslation"]["to"]
		if reverse:
			temp = from_language
			from_language = to_language
			to_language = temp
		_translator.translate(from_language, to_language, text, self._onResult)

	def _onResult(self, data):
		if data is not None:
			self._speak([data])

	def speak(self, sequence, *args, **kwargs):
		self._data = ""
		if isinstance(sequence, str):
			self._data = sequence
		elif isinstance(sequence, list):
			self._data = "".join([item for item in sequence if isinstance(item, str)])
		if config.conf["baiduTranslation"]["autoTrans"] != 0 and self._data:
			if config.conf["baiduTranslation"]["autoTrans"] == 1:
				from_language = "auto" if config.conf["baiduTranslation"]["autoFromLang"] else \
				config.conf["baiduTranslation"]["from"]
				to_language = config.conf["baiduTranslation"]["to"]
			else:
				from_language = config.conf["baiduTranslation"]["to"]
				to_language = config.conf["baiduTranslation"]["from"]
			_translator.translate(from_language, to_language, self._data, self._onResult)
		else:
			self._speak(sequence, *args, **kwargs)

	def _playSound(self, reverse_translate=False):
		filename = ""
		if reverse_translate is True:
			filename = "reverseTranslate.wav"
		else:
			filename = "translate.wav"
		sound_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sound", filename))
		nvwave.playWaveFile(sound_filename)

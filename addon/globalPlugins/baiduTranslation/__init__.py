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
from .cacheData import CacheDataFile
from .exceptions import TranslationException
from logHandler import log


# 翻译缓存数据文件路径
TRANSLATION_CACHE_DATA_FILENAME = 		cacheFilename = os.path.abspath(os.path.join(
			os.path.dirname(__file__), "../../../..", "baiduTranslation.cache-data"))


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
		self.usingShareKeyCheckBox.Bind(wx.EVT_CHECKBOX, self.onUsingShareKeyCheckBoxChange)
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
		enabled = not self.usingShareKeyCheckBox.IsChecked()
		self.myAppIdTextCtrl.Enable(enabled)
		self.myAppSecretTextCtrl.Enable(enabled)
		# 清除缓存按钮
		# Translators: Label for the clear cache button
		self.labelForClearCacheButton = _("Clear cache (current item count: {})")
		cacheFile = CacheDataFile()
		cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		label = f"{_(self.labelForClearCacheButton)}".format(cacheFile.getItemCount())
		log.info(f"标签={label}")
		self.clearCacheButton = helper.addItem(
			wx.Button(self, label=label)
		)
		self.clearCacheButton.Bind(wx.EVT_BUTTON, self.onClearCacheButtonClick)

	def onClearCacheButtonClick(self, event):
		cacheFile = CacheDataFile()
		cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		cacheFile.clear()
		label = f"{_(self.labelForClearCacheButton)}".format(cacheFile.getItemCount())
		self.clearCacheButton.SetLabel(label)


	def onUsingShareKeyCheckBoxChange(self, event):
		enabled = not self.usingShareKeyCheckBox.IsChecked()
		self.myAppIdTextCtrl.Enable(enabled)
		self.myAppSecretTextCtrl.Enable(enabled)

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
		# 翻译历史缓存数据夹在，用以加速相同内容的翻译
		self._cacheFile = CacheDataFile()
		self._cacheFile.loadDataFile(TRANSLATION_CACHE_DATA_FILENAME)
		# 翻译结果缓存，用以翻译结果拷贝，当拷贝成功后此缓存将被清空
		self._translationResult = ""
		# 是否拷贝翻译结果标志
		self._copyFlag = False
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
		# Translators: Translate what you just heard, double click to copy translation results to the clipboard
		description=_("Translate what you just heard, double click to copy translation results to the clipboard"),
		gesture="kb:NVDA+W")
	def script_translate(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 1:
			self._copyTranslationResultToClipboard()
			return
		self._playSound()
		if config.conf["baiduTranslation"]["autoFromLang"]:
			from_language = "auto"
		else:
			from_language = config.conf["baiduTranslation"]["from"]
		to_language = config.conf["baiduTranslation"]["to"]
		self._translate(from_language, to_language, self._data)

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
		from_language = config.conf["baiduTranslation"]["from"]
		to_language = config.conf["baiduTranslation"]["to"]
		self._translate(to_language, from_language, self._data)

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
		self._translate(to_language, from_language, self._data)

	def _onResult(self, fromLanguage, toLanguage, source, target):
		if isinstance(target, TranslationException):
			self._speak([str(target)])
			self._copyFlag = False
			self._translationResult = ""
			return
		if target:
			self._speak([target])
			self._cacheFile.addCacheItem(fromLanguage, toLanguage, source, target)
			if self._copyFlag is True:
				api.copyToClip(target)
				self._speak([target])
				# 拷贝完成清空缓存并重置拷贝标志
				self._translationResult = ""
				self._copyFlag = False
			else:
				self._translationResult = target


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
			self._translate(from_language, to_language, self._data)
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

	def _copyTranslationResultToClipboard(self):
		if _translator.isRunning():
			self._copyFlag = True
		else:
			self._copyFlag = False
			if self._translationResult:
				api.copyToClip(self._translationResult)
				self._speak([self._translationResult])
				self._translationResult = ""
			else:
				self._speak([_("No translation results available for replication")])

	def _translate(self, fromLanguage, toLanguage, text):
		if not text:
			return
		result = self._cacheFile.getCacheItem(fromLanguage, toLanguage, text)
		if not result:
			_translator.translate(fromLanguage, toLanguage, text, self._onResult)
		else:
			self._onResult(fromLanguage, toLanguage, text, result)

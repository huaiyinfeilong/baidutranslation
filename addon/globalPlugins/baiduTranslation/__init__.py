import globalPluginHandler
import ui
import scriptHandler
import addonHandler
import speech
import winsound
import os
import gui
import config
import wx
from .translators import BaiduTranslator
from .languages import get_language_list

addonHandler.initTranslation()


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

    def onSave(self):
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


# Translators: Category Name
CATEGORY_NAME = _("Baidu Translation")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super(globalPluginHandler.GlobalPlugin, self).__init__()
        confspec = {
            "from": "string(default='en')",
            "to": "string(default='zh')"
        }
        config.conf.spec["baiduTranslation"] = confspec
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(TranslationSettingsPanel)
        appid = "20230423001653246"
        appsecret = "dyh8lxcVEZnBhJ8EiEwD"
        self._translator = BaiduTranslator()
        self._translator.initialize_translator(appid, appsecret)
        self._speak = speech.speech.speak
        speech.speech.speak = self.speak

    def terminate(self):
        super(globalPluginHandler.GlobalPlugin, self).terminate()
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(TranslationSettingsPanel)
        speech.speech.speak = self._speakself._speak = None

    # Translators: Translate what you just heard
    @scriptHandler.script(
        category=CATEGORY_NAME,
        description=_("Translate what you just heard"),
        gesture="kb:NVDA+A")
    def script_translate(self, gesture):
        self._playSound()
        from_language = config.conf["baiduTranslation"]["from"]
        to_language = config.conf["baiduTranslation"]["to"]
        self._translator.translate(from_language, to_language, self._data, self._onResult)

    # Translators: Reverse translate what you just heard
    @scriptHandler.script(
        category=CATEGORY_NAME,
        description=_("Reverse translate what you just heard"),
        gesture="kb:NVDA+SHIFT+A")
    def script_reverseTranslate(self, gesture):
        self._playSound(True)
        from_language = config.conf["baiduTranslation"]["from"]
        to_language = config.conf["baiduTranslation"]["to"]
        self._translator.translate(to_language, from_language, self._data, self._onResult)

    def _onResult(self, data):
        if data is not None:
            ui.message(data)

    def speak(self, sequence, *args, **kwargs):
        self._data = ""
        if isinstance(sequence, str):
            self._data = sequence
        elif isinstance(sequence, list):
            self._data = " ".join([item for item in sequence if isinstance(item, str)])
        self._speak(sequence, *args, **kwargs)

    def _playSound(self, reverse_translate=False):
        filename = ""
        if reverse_translate is True:
            filename = "reverseTranslate.wav"
        else:
            filename = "translate.wav"
        sound_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sound", filename))
        winsound.PlaySound(sound_filename, winsound.SND_FILENAME | winsound.SND_ASYNC)

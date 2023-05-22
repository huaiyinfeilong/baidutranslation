# coding=utf-8

import threading
import urllib.request
import json
import time
import hashlib
import addonHandler

# 初始化翻译引擎
addonHandler.initTranslation()


class BaiduTranslator(object):
	_access_token = ""
	_appid = ""
	_appsecret = ""
	_text = ""
	_on_result = None
	_thread = None
	
	def initialize_translator(self, appid, appsecret):
		self._appid = appid
		self._appsecret = appsecret

	def _make_sign(self, salt):
		if not salt:
			return
		text = self._text
		appid = self._appid
		appsecret = self._appsecret
		s = appid + text + salt + appsecret
		return hashlib.md5(s.encode("utf-8")).hexdigest()

	def translate(self, from_language, to_language, text, on_result):
		if self._thread and self._thread.is_alive():
			return
		self._from_language = from_language
		self._to_language = to_language
		self._text = text
		self._on_result = on_result
		self._thread = threading.Thread(target=self.run)
		if self._thread:
			self._thread.start()

	def run(self):
		salt = str(int(time.time()))
		sign = self._make_sign(salt)
		appid = self._appid
		from_language = self._from_language
		to_language = self._to_language
		text = self._text
		on_result = self._on_result
		if not from_language or not to_language or not text or not on_result:
			return
		url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
		headers = {"Content-Type": "application/x-www-form-urlencoded"}
		payload = bytes(urllib.parse.urlencode({
			"from": from_language,
			"to": to_language,
			"q": text,
			"appid": appid,
			"salt": salt,
			"sign": sign
		}).encode("utf-8"))
		request = urllib.request.Request(url=url, data=payload, headers=headers, method="POST")
		proxy = urllib.request.ProxyHandler({})
		opener = urllib.request.build_opener(proxy)
		response = opener.open(request)
		data = json.loads(response.read().decode("utf-8"))
		if data.get("error_code"):
			errorCode = data.get("error_code")
			message = ""
			errorDescription = {
				# Translators: Request timeout
				"52001": _("Request timeout"),
				# Translators: System error
				"52002": _("System error"),
				# Translators: Unauthorized user
				"52003": _("Unauthorized user"),
				# Translators: The required parameter is empty
				"54000": _("The required parameter is empty"),
				# Translators: Signature error
				"54001": _("Signature error"),
				# Translators: Access frequency limited
				"54003": _("Access frequency limited"),
				# Translators: Insufficient account balance
				"54004": _("Insufficient account balance"),
				# Translators: Long query requests are frequent
				"54005": _("Long query requests are frequent"),
				# Translators: Illegal client IP
				"58000": _("Illegal client IP"),
				# Translators: Translation language direction not supported
				"58001": _("Translation language direction not supported")
			}
			message = errorDescription.get(errorCode)
			if message is None:
				message = f"{data.get('error_msg')}, error code={errorCode}"
			# Translators: Translation failed message
			failedMessage = _("Translation failed: ")
			result = f"{_(failedMessage)}{_(message)}"
		else:
			result = "\n".join([r.get("dst") for r in data.get("trans_result")])
		self._on_result(result)

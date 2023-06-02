# coding=utf-8

import json


class CacheDataFile(object):
	"""翻译缓存数据文件类
	针对翻译结果数据进行缓存，避免相同重复内容的频繁请求，加速翻译速度和优化翻译API请求数量
	"""

	# 翻译缓存数据，字典类型，key为原文，value为译文
	_cacheData = {}
	# 缓存数据文件路径
	_filename = ""

	# 夹在缓存数据文件
	def loadDataFile(self, filename):
		try:
			if filename:
				self._filename = filename
			with open(filename, "r") as f:
				data = f.read()
				self._cacheData = json.loads(data)
		except Exception:
			self._cacheData = {}

	# 保存缓存数据文件
	def _saveCacheDataFile(self):
		if not self._filename:
			return
		data = json.dumps(self._cacheData)
		with open(self._filename, "w") as f:
			f.write(data)

	# 添加缓存数据
	def addCacheItem(self, fromLanguage, toLanguage, source, target):
		key = f"[{fromLanguage}>{toLanguage}]{source}"
		self._cacheData[key] = target
		self._saveCacheDataFile()

	# 获取缓存项目
	def getCacheItem(self, fromLanguage, toLanguage, source):
		key = f"[{fromLanguage}>{toLanguage}]{source}"
		return self._cacheData.get(key)


	# 获取缓存条目数量
	def getItemCount(self):
		return len(self._cacheData)

	# 清除缓存
	def clear(self):
		self._cacheData = {}
		self._saveCacheDataFile()

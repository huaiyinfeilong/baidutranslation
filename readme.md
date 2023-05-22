# Baidu translator

An NVDA plugin that provides Baidu translation.

## Keyboard shortcuts:

* Translate what you just heard: NVDA+W
* Reverse translate what you just heard: NVDA+SHIFT+W
* Cycle through automatic translation modes (disabled, normal, reverse): NVDA+F8
* Translate clipboard contents forward: NVDA+CONTROL+W
* Reverse translate clipboard content: NVDA+CONTROL+SHIFT+W

## Feedback Contact

Any comments and suggestions are welcome to communicate:

* Project address: https://github.com/huaiyinfeilong/baiduTranslation
* E-mail: huaiyinfeilong@163.com
* QQ: 354522977
* WeChat: huaiyinfeilong

## Upgrade log

### Version 1.5

* Added "Use shared key" switch in settings, you can choose to use shared key or your own private key. Personal private key application address:
[https://api.fanyi.baidu.com/product/11](https://api.fanyi.baidu.com/product/11)

### Version 1.4

* Improve the help documentation and fix errors in the English help documentation.
* Optimize the automatic translation switching prompt, which is now more concise and clear.

### Version 1.3

Added clipboard forward translation and clipboard reverse translation functions.

* Forward translation of the clipboard: Translate the contents of the clipboard from the source language to the target language. If the "Automatically identify source language" option is enabled, the source language will be automatically recognized.
* Clipboard reverse translation: Translate the contents of the clipboard from the target language to the source language.

### Version 1.2

Added the automatic translation function, which supports three modes of regular automatic translation, reverse automatic translation and disabled automatic translation.

After the automatic translation function is turned on, all content read by NVDA will be automatically translated. The specific functions of the three modes are described as follows:

* Forward automatic translation: Automatically translate the content read by NVDA from the source language to the target language. If the "Automatically identify source language" option is enabled, the source language will be automatically recognized.
* Reverse automatic translation: Automatically translate the content read by NVDA from the target language to the source language.
* Disable auto-translation: Do not use the auto-translation feature.

Note: After the automatic translation function is turned on, all the reading content of NVDA will be sent to the translation server, and the response speed of NVDA reading will be slowed down to varying degrees due to the translation results.

### Version 1.1

Added reverse translation function, which can translate from the target language to the source language.

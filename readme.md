# Baidu translator

An NVDA plugin that provides Baidu translation.

## Keyboard shortcuts

* Translate what you just heard: NVDA+W
* Reverse translate what you just heard: NVDA+SHIFT+W
* Translate clipboard contents forward: NVDA+CONTROL+W
* Reverse translate clipboard content: NVDA+CONTROL+SHIFT+W
*Copy translation results to clipboard: Double click on the above gesture
* Cycle through automatic translation modes (disabled, normal, reverse): NVDA+F8

## Feedback Contact

Any comments and suggestions are welcome to communicate:

* Project address: [https://github.com/huaiyinfeilong/baiduTranslation](https://github.com/huaiyinfeilong/baiduTranslation)
* E-mail: huaiyinfeilong@163.com
* QQ: 354522977
* WeChat: huaiyinfeilong

## Upgrade log
### Version 1.7.6
* Compatible with NVDA 2025.1.
* More friendly Chinese error messages.
* If the translation attempt fails for 3 consecutive times, automatic translation will be disabled.
* Code refactoring.

### Version 1.7.5

* Removed shared key support, now only individual Baidu Translation API keys are allowed.
* Added a "Register for Baidu Translation API" button in the settings interface.

### Version 1.7.4

* Enhance error messages for using shared key.
* Improve addon stability.

### Version 1.7.3

* Adapt to NVDA 2024.1 version.

### Version 1.7.2

* Fix the issue of clipboard translation not being able to translate.

### Version 1.7.1

* Add the "Clear Cache" function in the settings to clear the translation history cache data.
* Fix some issues.

### Version 1.7

* Increase translation history cache to improve performance.

### Version 1.6

* Add translation result copying function. For forward translation, reverse translation, clipboard forward translation, and clipboard reverse translation, the translation results can be copied to the clipboard by double clicking the gesture.

### Version 1.5

* Added "Use shared key" switch in settings, you can choose to use shared key or your own private key. Personal private key application address:
[https://api.fanyi.baidu.com/product/11](https://api.fanyi.baidu.com/product/11)
* Improve localization support for error reporting information.

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

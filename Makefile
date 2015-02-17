

ui_rfreeze.py: rfreeze.ui
	pyuic5 -o ui_rfreeze.py rfreeze.ui

rc_rfreeze.py: rfreeze.qrc
	pyrcc5 rfreeze.qrc -o rc_rfreeze.py

l10n:
	pylupdate5 *py -ts RFreeze_ru.ts

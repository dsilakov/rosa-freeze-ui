

rosa_freeze_ui/ui_rfreeze.py: rosa_freeze_ui/rfreeze.ui
	pyuic5 -o rosa_freeze_ui/ui_rfreeze.py rosa_freeze_ui/rfreeze.ui

rosa_freeze_ui/rc_rfreeze.py: rosa_freeze_ui/rfreeze.qrc
	pyrcc5 rosa_freeze_ui/rfreeze.qrc -o rosa_freeze_ui/rc_rfreeze.py

l10n: rosa_freeze_ui/rc_rfreeze.py rosa_freeze_ui/ui_rfreeze.py rfreeze.py
	pylupdate5 rosa_freeze_ui/rc_rfreeze.py rosa_freeze_ui/ui_rfreeze.py rfreeze.py -ts RFreeze_ru.ts

all: rosa_freeze_ui/ui_rfreeze.py rosa_freeze_ui/rc_rfreeze.py l10n

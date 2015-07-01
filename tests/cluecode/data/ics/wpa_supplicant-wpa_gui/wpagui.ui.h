	c = getopt(qApp->argc(), qApp->argv(), "i:p:");
	if (c < 0)
	    break;
	switch (c) {
	case 'i':
	    free(ctrl_iface);
void WpaGui::helpAbout()
{
    QMessageBox::about(this, "wpa_gui for wpa_supplicant",
		       "Copyright (c) 2003-2008,\n"
		       "Jouni Malinen <j@w1.fi>\n"
		       "and contributors.\n"
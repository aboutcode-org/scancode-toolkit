//
//
// C++ Implementation: $MODULE$
//
// Description:
//
//
// Author: Lalescu Liviu <Please see http://lalescu.ro/liviu/ for details about contacting Liviu Lalescu (in particular, you can find here the e-mail address)>, (C) 2003
//
// Copyright: See COPYING file that comes with this distribution
//
//
#include <iostream>
using namespace std;

#include "centerwidgetonscreen.h"

#include "timetable_defs.h"
#include "timetable.h"
#include "solution.h"

#include "fetmainform.h"

#include "timetablegenerateform.h"
#include "timetablegeneratemultipleform.h"

#include "timetableviewstudentsform.h"
#include "timetableviewteachersform.h"
#include "timetableshowconflictsform.h"
#include "timetableviewroomsform.h"

#include "export.h"
#include "import.h"

#include "institutionnameform.h"
#include "commentsform.h"
#include "daysform.h"
#include "hoursform.h"
#include "subjectsform.h"
#include "subjectsstatisticsform.h"
#include "activitytagsform.h"
#include "teachersform.h"
#include "teachersstatisticsform.h"
#include "yearsform.h"
#include "groupsform.h"
#include "subgroupsform.h"
#include "studentsstatisticsform.h"
#include "activitiesform.h"
#include "subactivitiesform.h"
#include "roomsform.h"
#include "buildingsform.h"
#include "alltimeconstraintsform.h"
#include "allspaceconstraintsform.h"
#include "helpaboutform.h"
#include "helpfaqform.h"
#include "helptipsform.h"
#include "helpinstructionsform.h"

#include "fet.h"

#include "constraintactivityendsstudentsdayform.h"
#include "constraintactivitiesendstudentsdayform.h"
#include "constrainttwoactivitiesconsecutiveform.h"
#include "constrainttwoactivitiesgroupedform.h"
#include "constraintthreeactivitiesgroupedform.h"
#include "constrainttwoactivitiesorderedform.h"
#include "constraintactivitiespreferredtimeslotsform.h"
#include "constraintactivitiespreferredstartingtimesform.h"

#include "constraintsubactivitiespreferredtimeslotsform.h"
#include "constraintsubactivitiespreferredstartingtimesform.h"

#include "constraintactivitiessamestartingtimeform.h"
#include "constraintactivitiessamestartinghourform.h"
#include "constraintactivitiessamestartingdayform.h"
#include "constraintteachernotavailabletimesform.h"
#include "constraintbasiccompulsorytimeform.h"
#include "constraintbasiccompulsoryspaceform.h"
#include "constraintroomnotavailabletimesform.h"
#include "constraintactivitypreferredroomform.h"
#include "constraintstudentssetnotavailabletimesform.h"
#include "constraintbreaktimesform.h"
#include "constraintteachermaxdaysperweekform.h"
#include "constraintteachersmaxdaysperweekform.h"

#include "constraintteachermindaysperweekform.h"
#include "constraintteachersmindaysperweekform.h"

#include "constraintteacherintervalmaxdaysperweekform.h"
#include "constraintteachersintervalmaxdaysperweekform.h"
#include "constraintstudentssetintervalmaxdaysperweekform.h"
#include "constraintstudentsintervalmaxdaysperweekform.h"

#include "constraintteachermaxhoursdailyform.h"
#include "constraintteachersmaxhoursdailyform.h"
#include "constraintteachermaxhourscontinuouslyform.h"
#include "constraintteachersmaxhourscontinuouslyform.h"

#include "constraintteacheractivitytagmaxhourscontinuouslyform.h"
#include "constraintteachersactivitytagmaxhourscontinuouslyform.h"

#include "constraintteacheractivitytagmaxhoursdailyform.h"
#include "constraintteachersactivitytagmaxhoursdailyform.h"

#include "constraintteacherminhoursdailyform.h"
#include "constraintteachersminhoursdailyform.h"
#include "constraintactivitypreferredstartingtimeform.h"
#include "constraintstudentssetmaxgapsperweekform.h"
#include "constraintstudentsmaxgapsperweekform.h"

#include "constraintstudentssetmaxgapsperdayform.h"
#include "constraintstudentsmaxgapsperdayform.h"

#include "constraintteachersmaxgapsperweekform.h"
#include "constraintteachermaxgapsperweekform.h"
#include "constraintteachersmaxgapsperdayform.h"
#include "constraintteachermaxgapsperdayform.h"
#include "constraintstudentsearlymaxbeginningsatsecondhourform.h"
#include "constraintstudentssetearlymaxbeginningsatsecondhourform.h"
#include "constraintstudentssetmaxhoursdailyform.h"
#include "constraintstudentsmaxhoursdailyform.h"
#include "constraintstudentssetmaxhourscontinuouslyform.h"
#include "constraintstudentsmaxhourscontinuouslyform.h"

#include "constraintstudentssetactivitytagmaxhourscontinuouslyform.h"
#include "constraintstudentsactivitytagmaxhourscontinuouslyform.h"

#include "constraintstudentssetactivitytagmaxhoursdailyform.h"
#include "constraintstudentsactivitytagmaxhoursdailyform.h"

#include "constraintstudentssetminhoursdailyform.h"
#include "constraintstudentsminhoursdailyform.h"
#include "constraintactivitiesnotoverlappingform.h"
#include "constraintmindaysbetweenactivitiesform.h"
#include "constraintmaxdaysbetweenactivitiesform.h"
#include "constraintmingapsbetweenactivitiesform.h"
#include "constraintactivitypreferredtimeslotsform.h"
#include "constraintactivitypreferredstartingtimesform.h"
#include "constraintactivitypreferredroomsform.h"

#include "constraintstudentssethomeroomform.h"
#include "constraintstudentssethomeroomsform.h"
#include "constraintteacherhomeroomform.h"
#include "constraintteacherhomeroomsform.h"

#include "constraintstudentssetmaxbuildingchangesperdayform.h"
#include "constraintstudentsmaxbuildingchangesperdayform.h"
#include "constraintstudentssetmaxbuildingchangesperweekform.h"
#include "constraintstudentsmaxbuildingchangesperweekform.h"
#include "constraintstudentssetmingapsbetweenbuildingchangesform.h"
#include "constraintstudentsmingapsbetweenbuildingchangesform.h"

#include "constraintteachermaxbuildingchangesperdayform.h"
#include "constraintteachersmaxbuildingchangesperdayform.h"
#include "constraintteachermaxbuildingchangesperweekform.h"
#include "constraintteachersmaxbuildingchangesperweekform.h"
#include "constraintteachermingapsbetweenbuildingchangesform.h"
#include "constraintteachersmingapsbetweenbuildingchangesform.h"

#include "constraintsubjectpreferredroomform.h"
#include "constraintsubjectpreferredroomsform.h"
#include "constraintsubjectactivitytagpreferredroomform.h"
#include "constraintsubjectactivitytagpreferredroomsform.h"

#include "constraintactivitytagpreferredroomform.h"
#include "constraintactivitytagpreferredroomsform.h"

#include "settingstimetablehtmllevelform.h"

#include "spreadconfirmationform.h"

#include "removeredundantconfirmationform.h"
#include "removeredundantform.h"

#include "lockunlock.h"
#include "advancedlockunlockform.h"

#include <qmessagebox.h>

#include "longtextmessagebox.h"

//#include <q3filedialog.h>
#include <QFileDialog>
#include <qstring.h>
#include <qdir.h>
#include <q3popupmenu.h>
//Added by qt3to4:
#include <QTranslator>

#include <QCloseEvent>

#include <QStatusBar>

#include <QMap>

#include <QWidget>

#include "httpget.h"

#include "spreadmindaysconstraintsfivedaysform.h"

#include "statisticsexport.h"

bool simulation_running; //true if the user started an allocation of the timetable

bool simulation_running_multi;

bool students_schedule_ready;
bool teachers_schedule_ready;
bool rooms_schedule_ready;

Solution best_solution;

QString conflictsString; //the string that contains a log of the broken constraints

extern QApplication* pqapplication;

#include <QDesktopWidget>

#include <QSettings>

//for the icons of not perfect constraints
#include <QIcon>

//static HttpGet getter;

Rules rules2;

static int ORIGINAL_WIDTH, ORIGINAL_HEIGHT;

const QString COMPANY="fet";
const QString PROGRAM="fettimetabling";

bool USE_GUI_COLORS=false;

bool ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY=false;
bool ENABLE_STUDENTS_MAX_GAPS_PER_DAY=false;

bool SHOW_WARNING_FOR_NOT_PERFECT_CONSTRAINTS=true;

extern int XX;
extern const int MM;

const int STATUS_BAR_MILLISECONDS=2500;


RandomSeedDialog::RandomSeedDialog()
{
	label=new QLabel(tr("Random seed"));
	lineEdit=new QLineEdit(QString::number(XX));
	okPB=new QPushButton(tr("OK"));
	okPB->setDefault(true);
	helpPB=new QPushButton(tr("Help"));
	cancelPB=new QPushButton(tr("Cancel"));
	seedLayout=new QHBoxLayout();
	seedLayout->addWidget(label);
	seedLayout->addWidget(lineEdit);
	
	valuesLabel=new QLabel(tr("Allowed minimum %1 to maximum %2").arg(1).arg(MM-1));
	
	buttonsLayout=new QHBoxLayout();
	buttonsLayout->addWidget(helpPB);
	buttonsLayout->addWidget(okPB);
	buttonsLayout->addWidget(cancelPB);
	
	mainLayout=new QVBoxLayout(this);
	mainLayout->addLayout(seedLayout);
	mainLayout->addWidget(valuesLabel);
	mainLayout->addLayout(buttonsLayout);
	
	connect(helpPB, SIGNAL(clicked()), this, SLOT(help()));
	connect(okPB, SIGNAL(clicked()), this, SLOT(ok()));
	connect(cancelPB, SIGNAL(clicked()), this, SLOT(reject()));
	
	int w=this->sizeHint().width();
	int h=this->sizeHint().height();
	if(w<300)
		w=300;
	if(h<150)
		h=150;
	this->setGeometry(0, 0, w, h);
	
	centerWidgetOnScreen(this);
}

RandomSeedDialog::~RandomSeedDialog()
{
}

void RandomSeedDialog::help()
{
	LongTextMessageBox::largeInformation(this, tr("FET information"), 
		tr("You can control the random behaviour of FET with this function")+".\n\n"+
		tr("The random seed is a value at least %1 and at most %2.").arg(1).arg(MM-1)+
		+"\n\n"+tr("The random seed before the generation of a timetable is saved on disk in the corresponding timetables directory,"
		" so that you can simulate again the same generation after that")+"\n\n"+
		tr("Mode of operation: to obtain the same timetable twice, make the random seed"
		" a value (say 1234), then generate single, then make it again the same value (1234),"
		" then generate single again. The timetables will be the same. If you generate multiple instead of single,"
		" the first set of timetables will be the same as the second set (if you generate the same number of timetables)"
		" but of course timetables inside each set will be different. If you enter the same random seed on different computers"
		" and generate single, the timetables will be the same (if you generate multiple, the sets of timetables will correspond, "
		"the first timetable from simulation 1 with first timetable from simulation 2, etc.)")
		+"\n\n"
		+tr("Note: of course you need the exact same conditions to duplicate the same simulations (so, you need the same exact data - activities, constraints, etc.).")
		+"\n\n"
		+tr("Note: when you start FET, each time, the random seed is the number of seconds since 1 January 1970")
		+". "
		+tr("After you generate (even partially), the random seed will change (each call of the random number generator updates the random seed to the next number"
		" in the sequence, and there are many calls to this random generating routine in the generate function)")
		+"\n\n"
		+tr("This setting is useful for more things, maybe one thing is bug report: send you file along with the random seed at the start of generating"
		" (this value is saved in the timetable directory at the start of generation)")
	);
}

void RandomSeedDialog::ok()
{
	int tx=lineEdit->text().toInt();
	if(!(tx>=1 && tx<MM)){
		QMessageBox::warning(this, tr("FET warning"), tr("The random seed must be at least %1 and at most %2").arg(1).arg(MM-1));
		return;
	}
	
	accept();
}


FetMainForm::FetMainForm()
{
	setupUi(this);
	
	//statusBar()->showMessage(tr("FET started", "This is a message written in the status bar, saying that FET was started"), STATUS_BAR_MILLISECONDS);
	statusBar()->showMessage("", STATUS_BAR_MILLISECONDS); //to get the correct centralWidget for the logo, so we need status bar existing.
	
	ORIGINAL_WIDTH=width();
	ORIGINAL_HEIGHT=height();
	
	QSettings newSettings(COMPANY, PROGRAM);
	QRect rect=newSettings.value("main-form-geometry", QRect(0,0,0,0)).toRect();
	if(!rect.isValid())
		rect=newSettings.value("fetmainformgeometry", QRect(0,0,0,0)).toRect();
	
	if(!rect.isValid()){
		centerWidgetOnScreen(this);
	}
	else{
		this->setWindowFlags(this->windowFlags() | Qt::WindowMinMaxButtonsHint);
		
		resize(rect.size());
		move(rect.topLeft());
		cout<<"read rect.x()=="<<rect.x()<<", rect.y()=="<<rect.y()<<endl;
	}

	//new data
	if(gt.rules.initialized)
		gt.rules.kill();
	gt.rules.init();

	bool tmp=gt.rules.addTimeConstraint(new ConstraintBasicCompulsoryTime(100));
	assert(tmp);
	tmp=gt.rules.addSpaceConstraint(new ConstraintBasicCompulsorySpace(100));
	assert(tmp);

	students_schedule_ready=false;
	teachers_schedule_ready=false;
	rooms_schedule_ready=false;
	
	//languageMenu->setCheckable(true);
	
	checkForUpdatesAction->setCheckable(true);
	checkForUpdatesAction->setChecked(checkForUpdates);
	
	settingsUseColorsAction->setCheckable(true);
	settingsUseColorsAction->setChecked(USE_GUI_COLORS);
	
	timetablesDivideByDaysAction->setCheckable(true);
	timetablesDivideByDaysAction->setChecked(DIVIDE_HTML_TIMETABLES_WITH_TIME_AXIS_BY_DAYS);
	
	QObject::connect(&getter, SIGNAL(done(bool)), this, SLOT(httpDone(bool)));
	
	useGetter=false;
	
	if(checkForUpdates){
		useGetter=true;
		bool t=getter.getFile(QUrl("http://www.lalescu.ro/liviu/fet/crtversion/crtversion.txt"));
		if(!t){
			QMessageBox::critical(this, tr("FET information"), tr("Critical error - cannot check for updates"
			 " because of a bug in application. FET will now continue operation, but you should"
			 " visit the FET page to report this bug or to get the fixed version."));
		}
		//assert(t);
	}
	
	settingsPrintNotAvailableSlotsAction->setCheckable(true);
	settingsPrintNotAvailableSlotsAction->setChecked(PRINT_NOT_AVAILABLE_TIME_SLOTS);

	settingsPrintActivitiesWithSameStartingTimeAction->setCheckable(true);
	settingsPrintActivitiesWithSameStartingTimeAction->setChecked(PRINT_ACTIVITIES_WITH_SAME_STARTING_TIME);

	//needed to sync the view table forms
	LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
	LockUnlock::increaseCommunicationSpinBox();
	
	enableActivityTagMaxHoursDailyAction->setChecked(ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	enableStudentsMaxGapsPerDayAction->setChecked(ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	showWarningForNotPerfectConstraintsAction->setChecked(SHOW_WARNING_FOR_NOT_PERFECT_CONSTRAINTS);
	
	connect(enableActivityTagMaxHoursDailyAction, SIGNAL(toggled(bool)), this, SLOT(enableActivityTagMaxHoursDailyToggled(bool)));
	connect(enableStudentsMaxGapsPerDayAction, SIGNAL(toggled(bool)), this, SLOT(enableStudentsMaxGapsPerDayToggled(bool)));
	connect(showWarningForNotPerfectConstraintsAction, SIGNAL(toggled(bool)), this, SLOT(showWarningForNotPerfectConstraintsToggled(bool)));

	setEnabledIcon(dataTimeConstraintsTeacherActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsTeachersActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsSetActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);

	setEnabledIcon(dataTimeConstraintsStudentsSetMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	setEnabledIcon(dataTimeConstraintsStudentsMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
}

void FetMainForm::setEnabledIcon(QAction* action, bool enabled)
{
	static QIcon locked(":/icons/locked.png");
	static QIcon unlocked(":/icons/unlocked.png");
	
	if(enabled)
		action->setIcon(unlocked);
	else
		action->setIcon(locked);
}

/*
void FetMainForm::resizeEvent(QResizeEvent* event)
{
	QMainWindow::resizeEvent(event);

	updateLogo();
}

void FetMainForm::updateLogo()
{
	//cout<<"menubar height=="<<menubar->height()<<endl;

	QWidget* centralw=this->centralWidget();
	
	if(centralw){
		double w=centralw->width();
		double h=centralw->height();
		
		int bh=menubar->sizeHint().height()-menubar->size().height(); //Hack to solve a Qt bug :-(
		if(bh>0)
			h-=bh;
	
		//cout<<"w=="<<w<<", h=="<<h<<endl;
		//cout<<"x=="<<centralw->x()<<" y=="<<centralw->y()<<endl;

		double a=w/10.0; //width
		double b=2.0*a;
	
		double d=h/6.0; //height
		double c=4.0*d;
	
		int ww=3; //width of line

		//F
		line->setGeometry(int(a), int(d), int(ww), int(c));
		line_2->setGeometry(int(a), int(d), int(b), int(ww));
		line_3->setGeometry(int(a), int(d+c/2.0), int(b/2.0), int(ww));

		//E
		line_5->setGeometry(int(a+a+b), int(d), int(ww), int(c));
		line_4->setGeometry(int(a+a+b), int(d), int(b), int(ww));
		line_6->setGeometry(int(a+a+b), int(d+c/2.0), int(b/2.0), int(ww));
		line_7->setGeometry(int(a+a+b), int(d+c), int(b), int(ww));
	
		//T
		line_8->setGeometry(int(a+2*a+2*b), int(d), int(b), int(ww));
		line_9->setGeometry(int(a+2*a+2*b+b/2), int(d), int(ww), int(c));
	}
}
*/

void FetMainForm::enableNotPerfectMessage()
{
	QString s=tr("Constraint is not enabled. To use this type of constraint you must manually enable it from the Settings menu.");
	s+="\n\n";
	s+=tr("Explanation:");
	s+=" ";
	s+=tr("Constraints of this type are good, working, but they are not perfectly optimized.");
	s+=" ";
	s+=tr("For some situations, the generation of the timetable may take too long or be impossible.");
	s+="\n\n";
	s+=tr("Use with caution.");

	QMessageBox::warning(this, tr("FET warning"), s);
}

void FetMainForm::on_checkForUpdatesAction_toggled()
{
	checkForUpdates=checkForUpdatesAction->isChecked();
}

void FetMainForm::on_settingsUseColorsAction_toggled()
{
	USE_GUI_COLORS=settingsUseColorsAction->isChecked();
}

void FetMainForm::on_timetablesDivideByDaysAction_toggled()
{
	DIVIDE_HTML_TIMETABLES_WITH_TIME_AXIS_BY_DAYS=timetablesDivideByDaysAction->isChecked();
}

void FetMainForm::httpDone(bool error)
{
	if(error){
		QMessageBox::warning(this, tr("FET warning"), tr(
		 "Could not search for possible updates on internet - error message is: %1. "
		 "I am searching for the file http://www.lalescu.ro/liviu/fet/crtversion/crtversion.txt . "
		 "Maybe the current structure on web page was changed. Please visit FET web page"
		 " http://www.lalescu.ro/liviu/fet/ and get latest version or,"
		 " if the web page does not work, try to search for the new FET page on the internet."
		 " You can contact the author. Also, sometimes lalescu.ro might have temporary problems, try again later"
		 "\n\nIf you want, you can turn off automatic search for updates in Settings menu"
		 ).arg(getter.http.errorString()));
	}
	else{
		QString s;
		for(int c=0; c<internetVersion.count(); c++){
			s+=internetVersion[c];
			if((c+1)%64==0)
				s+=" ";
		}
	
		if(internetVersion!=FET_VERSION){
			QMessageBox::information(this, tr("FET information"),
			 tr("Another version: %1, is available on FET webpage: http://www.lalescu.ro/liviu/fet/\n\n"
			 "You have to manually download and install (open the FET webpage in an internet browser). "
			 "Please read the information on web page regarding the newer version and choose whether to keep your current version or upgrade "
			 "(the recommended option is to upgrade). You might need to hit Refresh in your web browser if links do not work"
			 "\n\nYou can choose to disable automatic search for updates in the Settings menu")
			 .arg(s));
		}
	}
}

void FetMainForm::closeEvent(QCloseEvent* event)
{
	QSettings settings(COMPANY, PROGRAM);
	QRect rect(x(), y(), width(), height());
	settings.setValue("main-form-geometry", rect);
	cout<<"wrote x()=="<<x()<<", y()=="<<y()<<endl;
	
	//if(event!=NULL)
	//	;

	switch(QMessageBox::question( this, tr("FET - exiting"),
	 tr("File might have been changed - do you want to save it?"),
	 tr("&Yes"), tr("&No"), tr("&Cancel"), 0 , 2 )){
	 	case 0: 
			this->on_fileSaveAction_activated();
			event->accept();
			break;
	 	case 1: 
			event->accept();
			break;
		case 2: 
			event->ignore();
			break;
	}

	//INPUT_FILENAME_XML = "";
}

FetMainForm::~FetMainForm()
{
	if(useGetter)
		getter.http.abort();
}

void FetMainForm::on_fileExitAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	close();
}

void FetMainForm::on_fileNewAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	int confirm=0;
	switch( QMessageBox::information( this, tr("FET application"),
	 tr("Are you sure you want to load new data (rules) ?"),
	 tr("&Yes"), tr("&No"), 0 , 1 ) ) {
	case 0: // Yes
		confirm=1;
		break;
	case 1: // No
		confirm=0;
		break;
	}

	if(confirm){
		INPUT_FILENAME_XML="";
	
		setWindowTitle(tr("FET - a free timetabling program"));

		if(gt.rules.initialized)
			gt.rules.kill();
		gt.rules.init();

		bool tmp=gt.rules.addTimeConstraint(new ConstraintBasicCompulsoryTime(100));
		assert(tmp);
		tmp=gt.rules.addSpaceConstraint(new ConstraintBasicCompulsorySpace(100));
		assert(tmp);

		students_schedule_ready=false;
		teachers_schedule_ready=false;
		rooms_schedule_ready=false;

		LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
		LockUnlock::increaseCommunicationSpinBox();

		statusBar()->showMessage(tr("New file generated"), STATUS_BAR_MILLISECONDS);
	}
}

void FetMainForm::on_fileOpenAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	int confirm=1;

	if(confirm){
		QString s = QFileDialog::getOpenFileName(this, tr("Choose a file"),
			WORKING_DIRECTORY, 
			tr("FET XML files", "Instructions for translators: FET XML is a type of file format (using text mode). "
			"So this field means files in the FET XML format")+" (*.fet)"+";;"+tr("All files")+" (*)");
			/*tr("FET xml files (*.fet)\nAll files (*)",
			"Instructions for translators, IMPORTANT: There are 2 file filters, on "
			"2 separate lines, so make sure you have a 'new line' character after the first filter "
			"(follow the source text format). Please keep the string *.fet unmodified, with lowercase letters."));*/
		if(s.isNull())
			return;

		int tmp2=s.findRev("/");
		QString s2=s.right(s.length()-tmp2-1);
			
		if(s2.indexOf("\"") >= 0){
			QMessageBox::warning(this, tr("FET info"), 
			 tr("Please do not use quotation marks \" in filename, the html css code does not work."
			  " File was not loaded. Please rename it, removing not allowed characters and open it after that with FET."));
			return;
		}		
		if(s2.indexOf(";") >= 0){
			QMessageBox::warning(this, tr("FET info"), 
			 tr("Please do not use semicolon ; in filename, the html css code does not work."
			  " File was not loaded. Please rename it, removing not allowed characters and open it after that with FET."));
			return;
		}
		if(s2.indexOf("#") >= 0){
			QMessageBox::warning(this, tr("FET info"), 
			 tr("Please do not use # in filename, the html css code does not work."
			  " File was not loaded. Please rename it, removing not allowed characters and open it after that with FET."));
			return;
		}
		/*if(s2.indexOf("(") >= 0 || s2.indexOf(")")>=0){
			QMessageBox::information(this, tr("FET info"), tr("Please do not use parentheses () in filename, the html css code does not work"));
			return;
		}*/
		else{
			if(gt.rules.read(s)){
				students_schedule_ready=false;
				teachers_schedule_ready=false;
				rooms_schedule_ready=false;

				INPUT_FILENAME_XML = s;
				
				LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
				LockUnlock::increaseCommunicationSpinBox();
				
				statusBar()->showMessage(tr("File opened"), STATUS_BAR_MILLISECONDS);
			}
			else{
				QMessageBox::information(this, tr("FET info"), tr("Invalid file"), tr("&OK"));
			}
		}
		//get the directory
		int tmp=s.findRev("/");
		WORKING_DIRECTORY=s.left(tmp);
		
		if(INPUT_FILENAME_XML!="")
			setWindowTitle(tr("FET - %1").arg(INPUT_FILENAME_XML.right(INPUT_FILENAME_XML.length()-INPUT_FILENAME_XML.findRev("/")-1)));
	}
}

void FetMainForm::on_fileSaveAsAction_activated()
{
	QString predefFileName=INPUT_FILENAME_XML;
	if(predefFileName=="")
		predefFileName=WORKING_DIRECTORY;

	QString s = QFileDialog::getSaveFileName(this, tr("Choose a filename to save under"),
		predefFileName, tr("FET XML files", "Instructions for translators: FET XML is a type of file format (using text mode). "
		"So this field means files in the FET XML format")+" (*.fet)"+";;"+tr("All files")+" (*)",
			/*tr("FET xml files (*.fet)\nAll files (*)",
			"Instructions for translators, IMPORTANT: There are 2 file filters, on "
			"2 separate lines, so make sure you have a 'new line' character after the first filter "
			"(follow the source text format). Please keep the string *.fet unmodified, with lowercase letters."),*/
		0, QFileDialog::DontConfirmOverwrite);
	if(s==QString::null)
		return;

	int tmp2=s.findRev("/");
	QString s2=s.right(s.length()-tmp2-1);
			
	if(s2.indexOf("\"") >= 0){
		QMessageBox::warning(this, tr("FET info"), tr("Please do not use quotation marks \" in filename, the html css code does not work"));
		return;
	}
	if(s2.indexOf(";") >= 0){
		QMessageBox::warning(this, tr("FET info"), tr("Please do not use semicolon ; in filename, the html css code does not work"));
		return;
	}
	if(s2.indexOf("#") >= 0){
		QMessageBox::warning(this, tr("FET info"), tr("Please do not use # in filename, the html css code does not work"));
		return;
	}
	/*if(s2.indexOf("(") >= 0 || s2.indexOf(")")>=0){
		QMessageBox::information(this, tr("FET info"), tr("Please do not use parentheses () in filename, the html css code does not work"));
		return;
	}*/
		
	if(s.right(4)!=".fet")
		s+=".fet";

	int tmp=s.findRev("/");
	WORKING_DIRECTORY=s.left(tmp);

	if(QFile::exists(s))
		if(QMessageBox::warning( this, tr("FET"),
		 tr("File %1 exists - are you sure you want to overwrite existing file?").arg(s),
		 tr("&Yes"), tr("&No"), 0 , 1 ) == 1)
		 	return;
			
	INPUT_FILENAME_XML = s;
	
	setWindowTitle(tr("FET - %1").arg(s.right(s.length()-tmp-1)));
	
	gt.rules.write(INPUT_FILENAME_XML);
	
	statusBar()->showMessage(tr("File saved"), STATUS_BAR_MILLISECONDS);
}

// Start of code contributed by Volker Dirr
void FetMainForm::on_fileImportCSVRoomsBuildingsAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVRoomsAndBuildings();
}

void FetMainForm::on_fileImportCSVSubjectsAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVSubjects();
}

void FetMainForm::on_fileImportCSVTeachersAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVTeachers();
}

void FetMainForm::on_fileImportCSVActivitiesAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVActivities();

	//TODO: if the import takes care of locked activities, then we need
	//to do:
	//LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
	//LockUnlock::increaseCommunicationSpinBox();
	//after the importing
}

void FetMainForm::on_fileImportCSVActivityTagsAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVActivityTags();
}

void FetMainForm::on_fileImportCSVYearsGroupsSubgroupsAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Import::importCSVStudents();
}

void FetMainForm::on_fileExportCSVAction_activated(){
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	Export::exportCSV();
}
// End of code contributed by Volker Dirr

void FetMainForm::on_timetableSaveTimetableAsAction_activated()
{
	if(!students_schedule_ready || !teachers_schedule_ready || !rooms_schedule_ready){
		QMessageBox::warning(this, tr("FET - Warning"), tr("You have not yet generated a timetable - please generate firstly"));
		return;	
	}

	Solution* tc=&best_solution;
	
	for(int ai=0; ai<gt.rules.nInternalActivities; ai++){
		//Activity* act=&gt.rules.internalActivitiesList[ai];
		int time=tc->times[ai];
		if(time==UNALLOCATED_TIME){
			QMessageBox::warning(this, tr("FET - Warning"), tr("It seems that you have an incomplete timetable."
			 " Saving of timetable does not work for incomplete timetables. Please generate a complete timetable"));
			 //.arg(act->id));
			return;	
		}
		
		int ri=tc->rooms[ai];
		if(ri==UNALLOCATED_SPACE){
			QMessageBox::warning(this, tr("FET - Warning"), tr("It seems that you have an incomplete timetable."
			 " Saving of timetable does not work for incomplete timetables. Please generate a complete timetable"));
			 //.arg(act->id));
			return;	
		}
	}

	QString t=tr("Please read this important information before proceeding:");
	
	t+="\n\n";
	
	t+=tr("This option is only useful if you need to lock current timetable into a file."
		" Locking means that there will be added constraints activity preferred starting time and"
		" activity preferred room with 100% importance for each activity to fix it at current place in current timetable."
		" You can save this timetable as an ordinary .fet file; when you'll open it, you'll see all old inputted data (activities, teachers, etc.)" 
		" and the locking constraints as the last time/space constraints."
		" You can unlock some of these activities (by removing constraints) if small changes appear in the configuration, and generate again"
		" and the remaining locking constraints will be respected.");
		
	t+="\n\n";
	
	t+=tr("NEW, 25 December 2008:");
	t+=" ";
	t+=tr("The added constraints will have the 'permanently locked' tag set to false, so you can also unlock the activities from the "
		"'Timetable' menu, without interfering with the initial constraints which are made by you 'permanently locked'");
	t+="\n\n";
	
	t+=tr("This option is useful for institutions where you obtain a timetable, then some small changes appear,"
		" and you need to regenerate timetable, but respecting in a large proportion the old timetable");

	t+="\n\n";
	
	t+=tr("Current data file will not be affected by anything, locking constraints will only be added to the file you select to save"
		" (you can save current datafile and open saved timetable file after that to check it)");
		
	//t+="\n\n";
	
	//t+=tr("If you need more information, contact author or mailing list");

	//QMessageBox::information(this, tr("FET - information about saving a timetable as"), t);
	LongTextMessageBox::largeInformation(this, tr("FET - information about saving a timetable as"), t);
	
	QString s;

	for(;;){
		s = QFileDialog::getSaveFileName(this, tr("Choose a filename to save under" ), 
			INPUT_FILENAME_XML, tr("FET XML files", "Instructions for translators: FET XML is a type of file format (using text mode). "
			"So this field means files in the FET XML format")+" (*.fet)"+";;"+tr("All files")+" (*)",
			/*tr("FET xml files (*.fet)\nAll files (*)",
			"Instructions for translators, IMPORTANT: There are 2 file filters, on "
			"2 separate lines, so make sure you have a 'new line' character after the first filter "
			"(follow the source text format). Please keep the string *.fet unmodified, with lowercase letters."),*/
			0, QFileDialog::DontConfirmOverwrite);
		if(s==QString::null)
			return;

		int tmp2=s.findRev("/");
		QString s2=s.right(s.length()-tmp2-1);
			
		if(s2.indexOf("\"") >= 0){
			QMessageBox::warning(this, tr("FET info"), tr("Please do not use quotation marks \" in filename, the html css code does not work"));
			return;
		}
		if(s2.indexOf(";") >= 0){
			QMessageBox::warning(this, tr("FET info"), tr("Please do not use semicolon ; in filename, the html css code does not work"));
			return;
		}
		if(s2.indexOf("#") >= 0){
			QMessageBox::warning(this, tr("FET info"), tr("Please do not use # in filename, the html css code does not work"));
			return;
		}
		/*if(s2.indexOf("(") >= 0 || s2.indexOf(")")>=0){
			QMessageBox::information(this, tr("FET info"), tr("Please do not use parentheses () in filename, the html css code does not work"));
			return;
		}*/
			
		if(s.right(4)!=".fet")
			s+=".fet";

		int tmp=s.findRev("/");
		WORKING_DIRECTORY=s.left(tmp);

		if(QFile::exists(s)){
			t=tr("File exists");
			t+="\n\n";
			t+=tr("For safety (so you don't lose work), it is not allowed to overwrite an existing file with"
				" locking and saving a current data+timetable");
			t+="\n\n";
			t+=tr("Please choose a non-existing name");
	
			QMessageBox::warning( this, tr("FET warning"), t);
		}
		else
			break;
	}
			
	//INPUT_FILENAME_XML = s; - do NOT add this
	
	//setWindowTitle(tr("FET - %1").arg(s.right(s.length()-tmp-1)));
	
	rules2.initialized=true;
	
	rules2.institutionName=gt.rules.institutionName;
	rules2.comments=gt.rules.comments;
	
	rules2.nHoursPerDay=gt.rules.nHoursPerDay;
	for(int i=0; i<gt.rules.nHoursPerDay; i++)
		rules2.hoursOfTheDay[i]=gt.rules.hoursOfTheDay[i];

	rules2.nDaysPerWeek=gt.rules.nDaysPerWeek;
	for(int i=0; i<gt.rules.nDaysPerWeek; i++)
		rules2.daysOfTheWeek[i]=gt.rules.daysOfTheWeek[i];
		
	rules2.yearsList=gt.rules.yearsList;
	
	rules2.teachersList=gt.rules.teachersList;
	
	rules2.subjectsList=gt.rules.subjectsList;
	
	rules2.activityTagsList=gt.rules.activityTagsList;

	rules2.activitiesList=gt.rules.activitiesList;

	rules2.buildingsList=gt.rules.buildingsList;

	rules2.roomsList=gt.rules.roomsList;

	rules2.timeConstraintsList=gt.rules.timeConstraintsList;
	
	rules2.spaceConstraintsList=gt.rules.spaceConstraintsList;


	//add locking constraints
	TimeConstraintsList lockTimeConstraintsList;
	SpaceConstraintsList lockSpaceConstraintsList;



	bool report=true;
	
	int addedTime=0, duplicatesTime=0;
	int addedSpace=0, duplicatesSpace=0;

	//lock selected activities
	for(int ai=0; ai<gt.rules.nInternalActivities; ai++){
		Activity* act=&gt.rules.internalActivitiesList[ai];
		int time=tc->times[ai];
		if(time>=0 && time<gt.rules.nDaysPerWeek*gt.rules.nHoursPerDay){
			int hour=time/gt.rules.nDaysPerWeek;
			int day=time%gt.rules.nDaysPerWeek;

			ConstraintActivityPreferredStartingTime* ctr=new ConstraintActivityPreferredStartingTime(100.0, act->id, day, hour, false); //permanently locked is false
			bool t=rules2.addTimeConstraint(ctr);
						
			if(t){
				addedTime++;
				lockTimeConstraintsList.append(ctr);
			}
			else
				duplicatesTime++;

			QString s;
						
			if(t)
				s=tr("Added the following constraint to saved file:")+"\n"+ctr->getDetailedDescription(gt.rules);
			else{
				s=tr("Constraint\n%1 NOT added to saved file - duplicate").arg(ctr->getDetailedDescription(gt.rules));
				delete ctr;
			}
						
			if(report){
				int k;
				if(t)
					k=QMessageBox::information(this, tr("FET information"), s,
				 	 tr("Skip information"), tr("See next"), QString(), 1, 0 );
				else
					k=QMessageBox::warning(this, tr("FET warning"), s,
				 	 tr("Skip information"), tr("See next"), QString(), 1, 0 );
																			 				 	
		 		if(k==0)
					report=false;
			}
		}
					
		int ri=tc->rooms[ai];
		if(ri!=UNALLOCATED_SPACE && ri!=UNSPECIFIED_ROOM && ri>=0 && ri<gt.rules.nInternalRooms){
			ConstraintActivityPreferredRoom* ctr=new ConstraintActivityPreferredRoom(100, act->id, (gt.rules.internalRoomsList[ri])->name, false); //false means not permanently locked
			bool t=rules2.addSpaceConstraint(ctr);

			QString s;
						
			if(t){
				addedSpace++;
				lockSpaceConstraintsList.append(ctr);
			}
			else
				duplicatesSpace++;

			if(t)
				s=tr("Added the following constraint to saved file:")+"\n"+ctr->getDetailedDescription(gt.rules);
			else{
				s=tr("Constraint\n%1 NOT added to saved file - duplicate").arg(ctr->getDetailedDescription(gt.rules));
				delete ctr;
			}
						
			if(report){
				int k;
				if(t)
					k=QMessageBox::information(this, tr("FET information"), s,
				 	 tr("Skip information"), tr("See next"), QString(), 1, 0 );
				else
					k=QMessageBox::warning(this, tr("FET warning"), s,
					 tr("Skip information"), tr("See next"), QString(), 1, 0 );
																			 				 	
				if(k==0)
					report=false;
			}
		}
	}

	QMessageBox::information(this, tr("FET information"), tr("Added %1 locking time constraints and %2 locking space constraints to saved file,"
	 " ignored %3 activities which were already fixed in time and %4 activities which were already fixed in space").arg(addedTime).arg(addedSpace).arg(duplicatesTime).arg(duplicatesSpace));
		
	bool result=rules2.write(s);
	
	while(!lockTimeConstraintsList.isEmpty())
		delete lockTimeConstraintsList.takeFirst();
	while(!lockSpaceConstraintsList.isEmpty())
		delete lockSpaceConstraintsList.takeFirst();
	/*foreach(TimeConstraint* tc, lockTimeConstraintsList)
		delete tc;
	foreach(SpaceConstraint* sc, lockSpaceConstraintsList)
		delete sc;*/

	if(result)	
		QMessageBox::information(this, tr("FET information"),
			tr("File saved successfully. You can see it on the hard disk. Current data file remained untouched (of locking constraints),"
			" so you can save it also, or generate different timetables."));

	rules2.nHoursPerDay=0;
	rules2.nDaysPerWeek=0;

	rules2.yearsList.clear();
	
	rules2.teachersList.clear();
	
	rules2.subjectsList.clear();
	
	rules2.activityTagsList.clear();

	rules2.activitiesList.clear();

	rules2.buildingsList.clear();

	rules2.roomsList.clear();

	rules2.timeConstraintsList.clear();
	
	rules2.spaceConstraintsList.clear();
}

void FetMainForm::on_fileSaveAction_activated()
{
	if(INPUT_FILENAME_XML == "")
		on_fileSaveAsAction_activated();
	else{
		gt.rules.write(INPUT_FILENAME_XML);
		statusBar()->showMessage(tr("File saved"), STATUS_BAR_MILLISECONDS);
	}
}

void FetMainForm::on_dataInstitutionNameAction_activated()
{
/*	InstitutionNameForm* form=new InstitutionNameForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();*/
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	InstitutionNameForm form;
	form.exec();
}

void FetMainForm::on_dataCommentsAction_activated()
{
/*	CommentsForm* form=new CommentsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();*/
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	CommentsForm form;
	form.exec();
}

void FetMainForm::on_dataDaysAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	DaysForm form;
	form.exec();
}

void FetMainForm::on_dataHoursAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	HoursForm form;
	form.exec();
}

void FetMainForm::on_dataTeachersAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	TeachersForm form;
	form.exec();
}

void FetMainForm::on_dataTeachersStatisticsAction_activated()
{
	TeachersStatisticsForm form;
	form.exec();
}

void FetMainForm::on_dataSubjectsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	SubjectsForm form;
	form.exec();
}

void FetMainForm::on_dataSubjectsStatisticsAction_activated()
{
	SubjectsStatisticsForm form;
	form.exec();
}

void FetMainForm::on_dataActivityTagsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ActivityTagsForm form;
	form.exec();
}

void FetMainForm::on_dataYearsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	YearsForm form;
	form.exec();
}

void FetMainForm::on_dataGroupsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	GroupsForm form;
	form.exec();
}

void FetMainForm::on_dataSubgroupsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	SubgroupsForm form;
	form.exec();
}

void FetMainForm::on_dataStudentsStatisticsAction_activated()
{
	StudentsStatisticsForm form;
	form.exec();
}

void FetMainForm::on_helpSettingsAction_activated()
{
	QString s;
	
	s+=tr("Probably some settings which are more difficult to understand are these ones:");
	s+="\n\n";
	s+=tr("Option 'Divide html timetables with time-axis by days':"
	" This means simply that the html timetables of type 'time horizontal' or 'time vertical' (see the generated html timetables)"
	" should be or not divided according to the days.");
	s+=" ";
	s+=tr("If the 'time horizontal' or 'time vertical' html timetables are too large for you, then you might need to select this option");
	
	s+="\n\n";
	s+=tr("Option 'Print activities with same starting time in timetables': selecting it means that the html timetables will contain for"
	 " each slot all the activities which have the same starting time (fact specified by your constraints) as the activity(ies) which are normally shown in this slot."
	 " If you don't use constraints activities same starting time, this option has no effect for you.");
	 
	s+="\n\n";
	s+=tr("Seed of random number generator: please read the help in the dialog of this option");
	
	s+="\n\n";
	s+=tr("Interface - use colors: the places with colors in FET interface are in:");
	s+="\n";
	s+=" -";
	s+=tr("add/modify constraints break, not available, preferred starting times or time slots (the table cells will have green or red colors).");
	s+="\n";
	s+=" -";
	s+=tr("activities and subactivities dialogs, the inactive activities will have a distinctive background color");
	
	s+="\n\n";
	s+=tr("Enable activity tag max hours daily:");
	s+="\n";
	s+=tr("This will enable the menu for 4 constraints: teacher(s) or students (set) activity tag max hours daily. These 4 constraints are good, but not perfect and"
		" may bring slow down of generation or impossible timetables if used unproperly. Select only if you know what you're doing.");
	s+="\n\n";
	s+=tr("Enable students max gaps per day:");
	s+="\n";
	s+=tr("This will enable the menu for 2 constraints: students (set) max gaps per day. These 2 constraints are good, but not perfect and"
		" may bring slow down of generation or impossible timetables if used unproperly. Select only if you know what you're doing.");
		
	s+="\n\n";
	s+=tr("Warn if using not perfect constraints:", "this is a warning if user uses not perfect constraints");
	s+="\n";
	s+=tr("If you use a not perfect constraint (activity tag max hours daily or students max gaps per day), you'll get a warning before generating"
		". Uncheck this option to get rid of that warning (it is recommended to keep the warning).");
	
	LongTextMessageBox::largeInformation(this, tr("FET information"), s);
}

void FetMainForm::on_dataHelpOnStatisticsAction_activated()
{
	QString s;
	
	s+=tr("This help by Liviu Lalescu, modified 12 September 2009");
	
	s+="\n\n";
	
	s+=tr("You will find in the statistics only active activities count. The inactive ones are not counted.");
	
	s+="\n\n";
	
	s+=tr("Statistics for students might be the most difficult to understand."
	 " If you are using divisions of years: probably the most relevant statistics"
	 " are the ones for each subgroup (so you may check only subgroups check box)."
	 " You may see more hours for the years or groups, but these are not significant, please ignore them,"
	 " because each year or group will count also activities of all contained subgroups."
	 "\n\n"
	 "Each subgroup should have a number of hours per week close to the average of"
	 " all subgroups and close to the normal number of working hours of each students set."
	 " If a subgroup has a much lower value, maybe you used incorrectly"
	 " the years/groups/subgroups for activities."
	 "\n\n"
	 "Please read FAQ for detailed description"
	 " on how divisions work. The key is that the subgroups are independent and represent the smallest unit of students."
	 " Each subgroup receives the activities of the parent year and parent group and of itself."
	 "\n\n"
	 "Having a subgroup with too little working hours per week means that you inputted activities in a wrong manner,"
	 " and also that some constraints like no gaps, early or min hours daily for this subgroup"
	 " are interpreted in a wrong manner (if subgroup has only 2 activities, then these must"
	 " be placed in the first hours, which is too hard and wrong)."
	 );
	
	s+="\n\n";
	s+=tr("New addition, 26 June 2009:");
	s+=" ";
	s+=tr("Students' statistics form contains a check box named '%1'"
	 ". This has effect only if you have overlapping groups/years, and means that FET will show the complete tree structure"
	 ", even if that means that some subgroups/groups will appear twice or more in the table, with the same information."
	 " For instance, if you have year Y1, groups G1 and G2, subgroups S1, S2, S3, with structure: Y1 (G1 (S1, S2), G2 (S1, S3)),"
	 " S1 will appear twice in the table").arg(tr("Show duplicates"));
	 
	LongTextMessageBox::largeInformation(this, tr("FET - information about statistics"), s);
}

void FetMainForm::on_dataActivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ActivitiesForm form;
	form.exec();
}

void FetMainForm::on_dataSubactivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	SubactivitiesForm form;
	form.exec();
}

void FetMainForm::on_dataRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	RoomsForm form;
	form.exec();
}

void FetMainForm::on_dataBuildingsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	BuildingsForm form;
	form.exec();
}

void FetMainForm::on_dataAllTimeConstraintsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	AllTimeConstraintsForm form;
	form.exec();
}

void FetMainForm::on_dataAllSpaceConstraintsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	AllSpaceConstraintsForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTwoActivitiesConsecutiveAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTwoActivitiesConsecutiveForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTwoActivitiesGroupedAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTwoActivitiesGroupedForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsThreeActivitiesGroupedAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintThreeActivitiesGroupedForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTwoActivitiesOrderedAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTwoActivitiesOrderedForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesPreferredTimeSlotsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesPreferredTimeSlotsForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesPreferredStartingTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesPreferredStartingTimesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsSubactivitiesPreferredTimeSlotsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubactivitiesPreferredTimeSlotsForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsSubactivitiesPreferredStartingTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubactivitiesPreferredStartingTimesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivityEndsStudentsDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityEndsStudentsDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesEndStudentsDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesEndStudentsDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesSameStartingTimeAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesSameStartingTimeForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesSameStartingHourAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesSameStartingHourForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesSameStartingDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesSameStartingDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherNotAvailableTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherNotAvailableTimesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsBasicCompulsoryTimeAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintBasicCompulsoryTimeForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsBasicCompulsorySpaceAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintBasicCompulsorySpaceForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsRoomNotAvailableTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintRoomNotAvailableTimesForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsActivityPreferredRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityPreferredRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsActivityPreferredRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityPreferredRoomsForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsSubjectPreferredRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubjectPreferredRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsSubjectPreferredRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubjectPreferredRoomsForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsSubjectActivityTagPreferredRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubjectActivityTagPreferredRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsSubjectActivityTagPreferredRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintSubjectActivityTagPreferredRoomsForm form;
	form.exec();
}

///added 6 apr 2009
void FetMainForm::on_dataSpaceConstraintsActivityTagPreferredRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityTagPreferredRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsActivityTagPreferredRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityTagPreferredRoomsForm form;
	form.exec();
}
///

void FetMainForm::on_dataSpaceConstraintsStudentsSetHomeRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetHomeRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsSetHomeRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetHomeRoomsForm form;
	form.exec();
}


void FetMainForm::on_dataSpaceConstraintsStudentsSetMaxBuildingChangesPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMaxBuildingChangesPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsMaxBuildingChangesPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMaxBuildingChangesPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsSetMaxBuildingChangesPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMaxBuildingChangesPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsMaxBuildingChangesPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMaxBuildingChangesPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsSetMinGapsBetweenBuildingChangesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMinGapsBetweenBuildingChangesForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsStudentsMinGapsBetweenBuildingChangesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMinGapsBetweenBuildingChangesForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeacherMaxBuildingChangesPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxBuildingChangesPerDayForm form;
	form.exec();
}
void FetMainForm::on_dataSpaceConstraintsTeachersMaxBuildingChangesPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxBuildingChangesPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeacherMaxBuildingChangesPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxBuildingChangesPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeachersMaxBuildingChangesPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxBuildingChangesPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeacherMinGapsBetweenBuildingChangesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMinGapsBetweenBuildingChangesForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeachersMinGapsBetweenBuildingChangesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMinGapsBetweenBuildingChangesForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeacherHomeRoomAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherHomeRoomForm form;
	form.exec();
}

void FetMainForm::on_dataSpaceConstraintsTeacherHomeRoomsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherHomeRoomsForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetNotAvailableTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetNotAvailableTimesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsBreakTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintBreakTimesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMinDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMinDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMinDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMinDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherIntervalMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherIntervalMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersIntervalMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersIntervalMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetIntervalMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetIntervalMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsIntervalMaxDaysPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsIntervalMaxDaysPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersActivityTagMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersActivityTagMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherActivityTagMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherActivityTagMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersActivityTagMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	
	if(!ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintTeachersActivityTagMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherActivityTagMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	if(!ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintTeacherActivityTagMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMinHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMinHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMinHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMinHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivityPreferredStartingTimeAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityPreferredStartingTimeForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetMaxGapsPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMaxGapsPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsMaxGapsPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMaxGapsPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetMaxGapsPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	if(!ENABLE_STUDENTS_MAX_GAPS_PER_DAY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintStudentsSetMaxGapsPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsMaxGapsPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	
	if(!ENABLE_STUDENTS_MAX_GAPS_PER_DAY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintStudentsMaxGapsPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMaxGapsPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxGapsPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMaxGapsPerWeekAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxGapsPerWeekForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeachersMaxGapsPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeachersMaxGapsPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsTeacherMaxGapsPerDayAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintTeacherMaxGapsPerDayForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsEarlyMaxBeginningsAtSecondHourAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsEarlyMaxBeginningsAtSecondHourForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetEarlyMaxBeginningsAtSecondHourAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetEarlyMaxBeginningsAtSecondHourForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetActivityTagMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetActivityTagMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsActivityTagMaxHoursContinuouslyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsActivityTagMaxHoursContinuouslyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetActivityTagMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	if(!ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintStudentsSetActivityTagMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsActivityTagMaxHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	if(!ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY){
		enableNotPerfectMessage();
		return;
	}

	ConstraintStudentsActivityTagMaxHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsSetMinHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsSetMinHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsStudentsMinHoursDailyAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintStudentsMinHoursDailyForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivitiesNotOverlappingAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivitiesNotOverlappingForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsMinDaysBetweenActivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintMinDaysBetweenActivitiesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsMaxDaysBetweenActivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintMaxDaysBetweenActivitiesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsMinGapsBetweenActivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintMinGapsBetweenActivitiesForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivityPreferredTimeSlotsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityPreferredTimeSlotsForm form;
	form.exec();
}

void FetMainForm::on_dataTimeConstraintsActivityPreferredStartingTimesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	ConstraintActivityPreferredStartingTimesForm form;
	form.exec();
}

void FetMainForm::on_helpAboutAction_activated()
{
	HelpAboutForm* form=new HelpAboutForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
}

void FetMainForm::on_helpForumAction_activated()
{
	QString s=tr("FET has a forum where you can ask questions or talk about FET");
	s+="\n\n";
	s+=tr("The current address is: %1").arg("http://lalescu.ro/liviu/fet/forum/");
	s+="\n";
	s+=tr("Please open this address in a web browser");
	s+="\n\n";
	s+=tr("If it does not work, please search the FET web page, maybe the address was changed");

	//QMessageBox::information(this, tr("FET forum"), s);
	
	QDialog dialog;
	
	dialog.setWindowTitle(tr("FET forum"));

	QVBoxLayout* vl=new QVBoxLayout(&dialog);
	QTextEdit* te=new QTextEdit();
	te->setPlainText(s);
	te->setReadOnly(true);
	QPushButton* pb=new QPushButton(tr("OK"));

	QHBoxLayout* hl=new QHBoxLayout(0);
	hl->addStretch(1);
	hl->addWidget(pb);

	vl->addWidget(te);
	vl->addLayout(hl);
	connect(pb, SIGNAL(clicked()), &dialog, SLOT(close()));

	/*dialog.setWindowFlags(windowFlags() | Qt::WindowMinMaxButtonsHint);
	QRect rect = QApplication::desktop()->availableGeometry(&dialog);
	int xx=rect.width()/2 - 200;
	int yy=rect.height()/2 - 125;
	dialog.setGeometry(xx, yy, 400, 250);*/
	dialog.setGeometry(0, 0, 400, 250);
	centerWidgetOnScreen(&dialog);

	dialog.exec();

}

void FetMainForm::on_helpFAQAction_activated()
{
	HelpFaqForm* form=new HelpFaqForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
}

void FetMainForm::on_helpTipsAction_activated()
{
	HelpTipsForm* form=new HelpTipsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
}

void FetMainForm::on_helpInstructionsAction_activated()
{
	HelpInstructionsForm* form=new HelpInstructionsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
}

void FetMainForm::on_helpManualAction_activated()
{
	QString s=tr("You can read a contributed user's manual in the %1 directory of FET.").arg(QDir::toNativeSeparators("doc/manual/"));
	s+="\n\n";
	s+=tr("This manual is contributed by Volker Dirr (timetabling.de).");
	s+="\n\n";
	s+=tr("You can read this manual using a web browser."
	 " Please open the main html file from the specified directory in a web browser.");
	s+="\n\n";
	s+=tr("See the website timetabling.de for possible updated version of this manual.");

	//show the message in a dialog
	QDialog dialog;
	
	dialog.setWindowTitle(tr("FET - contributed user's manual"));

	QVBoxLayout* vl=new QVBoxLayout(&dialog);
	QTextEdit* te=new QTextEdit();
	te->setPlainText(s);

	te->setReadOnly(true);
	QPushButton* pb=new QPushButton(tr("OK"));

	QHBoxLayout* hl=new QHBoxLayout(0);
	hl->addStretch(1);
	hl->addWidget(pb);

	vl->addWidget(te);
	vl->addLayout(hl);
	connect(pb, SIGNAL(clicked()), &dialog, SLOT(close()));

	/*dialog.setWindowFlags(windowFlags() | Qt::WindowMinMaxButtonsHint);
	QRect rect = QApplication::desktop()->availableGeometry(&dialog);
	int xx=rect.width()/2 - 300;
	int yy=rect.height()/2 - 200;
	dialog.setGeometry(xx, yy, 600, 400);*/
	dialog.setGeometry(0,0,600,400);
	centerWidgetOnScreen(&dialog);

	dialog.exec();
}

void FetMainForm::on_helpInOtherLanguagesAction_activated()
{
	QString s=tr("You can see help translated into other languages in the directory %1 of FET").arg(QDir::toNativeSeparators("doc/international/"));
	s+="\n\n";	
	s+=tr("Currently (17 July 2008), there are:");	
	s+="\n\n";	
	s+=tr("1. ar - Arabic - Manual");
	s+="\n\n";	
	s+=tr("2. es - Spanish - Instructions");
	s+="\n\n";	
	s+=tr("3. it - Italian - Instructions, FAQ");
	s+="\n\n";	
	s+=tr("4. ro - Romanian - Import/Export Help");
	s+="\n\n";	
	s+=tr("5. ca - Catalan - Manual");
	s+="\n\n";	
	s+=tr("6. fa - Persian - Manual");

	//show the message in a dialog
	QDialog dialog;
	
	dialog.setWindowTitle(tr("FET - help in other languages"));

	QVBoxLayout* vl=new QVBoxLayout(&dialog);
	QTextEdit* te=new QTextEdit();
	te->setPlainText(s);

	te->setReadOnly(true);
	QPushButton* pb=new QPushButton(tr("OK"));

	QHBoxLayout* hl=new QHBoxLayout(0);
	hl->addStretch(1);
	hl->addWidget(pb);

	vl->addWidget(te);
	vl->addLayout(hl);
	connect(pb, SIGNAL(clicked()), &dialog, SLOT(close()));

	/*dialog.setWindowFlags(windowFlags() | Qt::WindowMinMaxButtonsHint);
	QRect rect = QApplication::desktop()->availableGeometry(&dialog);
	int xx=rect.width()/2 - 350;
	int yy=rect.height()/2 - 250;
	dialog.setGeometry(xx, yy, 700, 500);*/
	dialog.setGeometry(0,0,700,500);
	centerWidgetOnScreen(&dialog);

	dialog.exec();
}

void FetMainForm::on_timetableGenerateAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	int count=0;
	for(int i=0; i<gt.rules.activitiesList.size(); i++){
		Activity* act=gt.rules.activitiesList[i];
		if(act->active){
			//cout<<"here: i=="<<i<<endl;
			count++;
		}
	}
	if(count<1){
		QMessageBox::information(this, tr("FET information"), tr("Please input at least one active activity before generating"));
		return;
	}
	TimetableGenerateForm form;
	form.exec();
	
	//LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
	LockUnlock::increaseCommunicationSpinBox();
}

void FetMainForm::on_timetableGenerateMultipleAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	if(INPUT_FILENAME_XML==""){
		QMessageBox::information(this, tr("FET information"),
			tr("Current file (data) has no name. Please save file under a certain name before proceeding"));
		return;
	}

	int count=0;
	for(int i=0; i<gt.rules.activitiesList.size(); i++){
		Activity* act=gt.rules.activitiesList[i];
		if(act->active){
			//cout<<"here: i=="<<i<<endl;
			count++;
		}
	}
	if(count<1){
		QMessageBox::information(this, tr("FET information"), tr("Please input at least one active activity before generating multiple"));
		return;
	}
	TimetableGenerateMultipleForm form;
	form.exec();

	//LockUnlock::computeLockedUnlockedActivitiesTimeSpace();
	LockUnlock::increaseCommunicationSpinBox();
}

void FetMainForm::on_timetableViewStudentsAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	if(gt.rules.nInternalRooms!=gt.rules.roomsList.count()){
		QMessageBox::warning(this, tr("FET warning"), tr("Cannot display the timetable, because you added or removed some rooms. Please regenerate the timetable and then view it"));
		return;
	}

	TimetableViewStudentsForm *form=new TimetableViewStudentsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
	form->resizeRowsAfterShow();
}

void FetMainForm::on_timetableViewTeachersAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	if(gt.rules.nInternalRooms!=gt.rules.roomsList.count()){
		QMessageBox::warning(this, tr("FET warning"), tr("Cannot display the timetable, because you added or removed some rooms. Please regenerate the timetable and then view it"));
		return;
	}
	if(gt.rules.nInternalTeachers!=gt.rules.teachersList.count()){
		QMessageBox::warning(this, tr("FET warning"), tr("Cannot display the timetable, because you added or removed some teachers. Please regenerate the timetable and then view it"));
		return;
	}
	
	TimetableViewTeachersForm *form=new TimetableViewTeachersForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
	form->resizeRowsAfterShow();
}

void FetMainForm::on_timetableShowConflictsAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	TimetableShowConflictsForm *form=new TimetableShowConflictsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
}

void FetMainForm::on_timetableViewRoomsAction_activated()
{
	if(!rooms_schedule_ready){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	if(gt.rules.nInternalRooms!=gt.rules.roomsList.count()){
		QMessageBox::warning(this, tr("FET warning"), tr("Cannot display the timetable, because you added or removed some rooms. Please regenerate the timetable and then view it"));
		return;
	}

	TimetableViewRoomsForm* form=new TimetableViewRoomsForm();
	form->setAttribute(Qt::WA_DeleteOnClose);
	form->show();
	form->resizeRowsAfterShow();
}


void FetMainForm::on_timetableLockAllActivitiesAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::lockAll();
}

void FetMainForm::on_timetableUnlockAllActivitiesAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::unlockAll();
}

void FetMainForm::on_timetableLockActivitiesDayAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::lockDay();
}

void FetMainForm::on_timetableUnlockActivitiesDayAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::unlockDay();
}

void FetMainForm::on_timetableLockActivitiesEndStudentsDayAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::lockEndStudentsDay();
}

void FetMainForm::on_timetableUnlockActivitiesEndStudentsDayAction_activated()
{
	if(!(students_schedule_ready && teachers_schedule_ready && rooms_schedule_ready)){
		QMessageBox::information(this, tr("FET information"), tr("Please generate, firstly"));
		return;
	}

	AdvancedLockUnlockForm::unlockEndStudentsDay();
}

void FetMainForm::on_languageAction_activated()
{
	QDialog dialog(this);
	dialog.setWindowTitle(tr("Please select FET language"));
	
	QVBoxLayout* taMainLayout=new QVBoxLayout(&dialog);

	QPushButton* tapb1=new QPushButton(tr("Cancel"));
	QPushButton* tapb2=new QPushButton(tr("OK"));
				
	QHBoxLayout* buttons=new QHBoxLayout();
	buttons->addStretch();
	buttons->addWidget(tapb1);
	buttons->addWidget(tapb2);
	
	QComboBox* languagesComboBox=new QComboBox();
	
	QSize tmp=languagesComboBox->minimumSizeHint();
	Q_UNUSED(tmp);
	
	//this is the other place (out of 2) in which you need to add a new language
	QMap<QString, QString> languagesMap;
	languagesMap.insert("en_GB", tr("British English"));
	languagesMap.insert("ar", tr("Arabic"));
	languagesMap.insert("ca", tr("Catalan"));
	languagesMap.insert("de", tr("German"));
	languagesMap.insert("el", tr("Greek"));
	languagesMap.insert("es", tr("Spanish"));
	languagesMap.insert("fr", tr("French"));
	languagesMap.insert("hu", tr("Hungarian"));
	languagesMap.insert("id", tr("Indonesian"));
	languagesMap.insert("it", tr("Italian"));
	languagesMap.insert("lt", tr("Lithuanian"));
	languagesMap.insert("mk", tr("Macedonian"));
	languagesMap.insert("ms", tr("Malay"));
	languagesMap.insert("nl", tr("Dutch"));
	languagesMap.insert("pl", tr("Polish"));
	languagesMap.insert("ro", tr("Romanian"));
	languagesMap.insert("tr", tr("Turkish"));
	languagesMap.insert("ru", tr("Russian"));
	languagesMap.insert("fa", tr("Persian"));
	
	//assert(languagesMap.count()==N_LANGUAGES);
	
	QMapIterator<QString, QString> it(languagesMap);
	int i=0;
	int j=-1;
	int eng=-1;
	while(it.hasNext()){
		it.next();
		languagesComboBox->insertItem( it.key() + " (" + it.value() + ")" );
		if(it.key()==FET_LANGUAGE)
			j=i;
		if(it.key()=="en_GB")
			eng=i;
		i++;
	}
	assert(eng>=0);
	if(j==-1){
		QMessageBox::warning(this, tr("FET warning"), tr("Invalid current language - making it en_GB (British English)"));
		FET_LANGUAGE="en_GB";
		j=eng;
	}
	languagesComboBox->setCurrentItem(j);
	
	QLabel* label=new QLabel(tr("Please select FET language"));
	
	QHBoxLayout* languagesLayout=new QHBoxLayout();
	languagesLayout->addWidget(languagesComboBox);
	//languagesLayout->addStretch();
	
	taMainLayout->addStretch();
	taMainLayout->addWidget(label);
	//taMainLayout->addWidget(languagesComboBox);
	taMainLayout->addLayout(languagesLayout);
	taMainLayout->addStretch();
	taMainLayout->addLayout(buttons);

	QObject::connect(tapb2, SIGNAL(clicked()), &dialog, SLOT(accept()));
	QObject::connect(tapb1, SIGNAL(clicked()), &dialog, SLOT(reject()));
	
	tapb2->setDefault(true);
	tapb2->setFocus();

	int w=dialog.sizeHint().width();
	if(w<350)
		w=350;
	int h=dialog.sizeHint().height();
	if(h<180)
		h=180;
	dialog.setGeometry(0,0,w,h);
	centerWidgetOnScreen(&dialog);
					
	bool ok=dialog.exec();
	if(!ok)
		return;
		
	//QString newLang=languagesComboBox->currentText();
	int k=languagesComboBox->currentItem();
	i=0;
	bool found=false;
	QMapIterator<QString, QString> it2(languagesMap);
	while(it2.hasNext()){
		it2.next();
		if(i==k){
			FET_LANGUAGE=it2.key();
			found=true;
		}
		i++;
	}
	if(!found){
		QMessageBox::warning(this, tr("FET warning"), tr("Invalid language selected - making it en_GB (British English)"));
		FET_LANGUAGE="en_GB";
	}

	QMessageBox::information(this, tr("FET information"), tr("Language %1 selected").arg( FET_LANGUAGE+" ("+languagesMap.value(FET_LANGUAGE)+")" )+"\n\n"+
	 tr("Please exit and restart FET to activate language change"));
}

void FetMainForm::on_settingsRestoreDefaultsAction_activated()
{
	QString default_working_directory="examples";
	QDir d2(default_working_directory);
	if(!d2.exists())
		default_working_directory=QDir::homePath();
	else
		default_working_directory=d2.absolutePath();

	QString s=tr("Are you sure you want to reset all settings to defaults?");
	s+="\n\n";
	
	s+=tr("That means");
	s+="\n";
	s+=tr("1. Mainform geometry will be reset to default");
	s+="\n";
	s+=tr("2. Check for updates at startup will be disabled");
	s+="\n";
	s+=tr("3. Language will be en_GB (restart needed to activate language change)");
	s+="\n";
	s+=tr("4. Working directory will be '%1'").arg(QDir::toNativeSeparators(default_working_directory));
	s+="\n";
	s+=tr("5. Html level of the timetables will be 2");
	s+="\n";
	s+=tr("6. Import directory will be %1").arg(QDir::toNativeSeparators(QDir::homePath()+FILE_SEP+"fet-results"));
	s+="\n";
	s+=tr("7. Mark not available slots with -x- in timetables will be true");
	s+="\n";
	s+=tr("8. Divide html timetables with time-axis by days will be false");
	s+="\n";
	s+=tr("9. Output (results) directory will be %1").arg(QDir::toNativeSeparators(QDir::homePath()+FILE_SEP+"fet-results"));
	s+="\n";
	s+=tr("10. Print activities with same starting time will be %1", "%1 is true or false").arg(tr("false"));
	s+="\n";
	s+=tr("11. Use colors in FET graphical user interface will be %1", "%1 is true or false").arg(tr("false"));
	s+="\n";

	s+=tr("12. Enable activity tag max hours daily will be %1", "%1 is true or false").arg(tr("false"));
	s+="\n";
	s+=tr("13. Enable students max gaps per day will be %1", "%1 is true or false").arg(tr("false"));
	s+="\n";
	s+=tr("14. Warn if using not perfect constraints will be %1", "%1 is true or false, this is a warning if user uses not perfect constraints").arg(tr("true"));

	//s+="    ";
	//s+=tr("Explanation: $HOME is usually '/home/username' under UNIX and Mac and 'Documents and Settings\\username' or 'Users\\username' under Windows");
	//s+="\n";
	
	switch( LongTextMessageBox::largeConfirmation( this, tr("FET confirmation"), s,
	 tr("&Yes"), tr("&No"), QString(), 0 , 1 ) ) {
	case 0: // Yes
		break;
	case 1: // No
		return;
	}

	resize(ORIGINAL_WIDTH, ORIGINAL_HEIGHT);
	/*QDesktopWidget* desktop=QApplication::desktop();
	int xx=desktop->width()/2 - frameGeometry().width()/2;
	int yy=desktop->height()/2 - frameGeometry().height()/2;
	move(xx, yy);*/
	centerWidgetOnScreen(this);

	/*for(int i=0; i<NUMBER_OF_LANGUAGES; i++)
		languageMenu->setItemChecked(languageMenu->idAt(i), false);
	languageMenu->setItemChecked(languageMenu->idAt(LANGUAGE_EN_GB_POSITION), true);*/
	FET_LANGUAGE="en_GB";
	
	checkForUpdatesAction->setChecked(false);
	checkForUpdates=0;
	
	USE_GUI_COLORS=false;
	settingsUseColorsAction->setChecked(USE_GUI_COLORS);
	
	///////////
	ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY=false;
	enableActivityTagMaxHoursDailyAction->setChecked(ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);

	ENABLE_STUDENTS_MAX_GAPS_PER_DAY=false;
	enableStudentsMaxGapsPerDayAction->setChecked(ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	
	SHOW_WARNING_FOR_NOT_PERFECT_CONSTRAINTS=true;
	showWarningForNotPerfectConstraintsAction->setChecked(SHOW_WARNING_FOR_NOT_PERFECT_CONSTRAINTS);
	
	setEnabledIcon(dataTimeConstraintsTeacherActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsTeachersActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsSetActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);

	setEnabledIcon(dataTimeConstraintsStudentsSetMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	setEnabledIcon(dataTimeConstraintsStudentsMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	///////////
	
	timetablesDivideByDaysAction->setChecked(false);
	DIVIDE_HTML_TIMETABLES_WITH_TIME_AXIS_BY_DAYS=false;
	
	WORKING_DIRECTORY=default_working_directory;
	
	OUTPUT_DIR=QDir::homePath()+FILE_SEP+"fet-results";
	QDir dir;
	if(!dir.exists(OUTPUT_DIR))
		dir.mkpath(OUTPUT_DIR);
	IMPORT_DIRECTORY=OUTPUT_DIR;
	
	TIMETABLE_HTML_LEVEL=2;
	
	settingsPrintNotAvailableSlotsAction->setChecked(true);
	PRINT_NOT_AVAILABLE_TIME_SLOTS=true;

	settingsPrintActivitiesWithSameStartingTimeAction->setChecked(false);
	PRINT_ACTIVITIES_WITH_SAME_STARTING_TIME=false;
}

void FetMainForm::on_settingsTimetableHtmlLevelAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	SettingsTimetableHtmlLevelForm form;
	form.exec();
}

void FetMainForm::on_settingsPrintNotAvailableSlotsAction_toggled()
{
	PRINT_NOT_AVAILABLE_TIME_SLOTS=settingsPrintNotAvailableSlotsAction->isChecked();
}

void FetMainForm::on_settingsPrintActivitiesWithSameStartingTimeAction_toggled()
{
	PRINT_ACTIVITIES_WITH_SAME_STARTING_TIME=settingsPrintActivitiesWithSameStartingTimeAction->isChecked();
}

void FetMainForm::on_spreadActivitiesAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	
	if(gt.rules.nDaysPerWeek>=7){
		QString s;
		s=tr("You have more than 6 days per week, so probably you won't need this feature. Do you still want to continue?");
		
		int cfrm=0;
		switch( QMessageBox::question( this, tr("FET question"),
		 s,
		 tr("&Continue"), tr("&Cancel"), 0 , 1 ) ) {
		case 0: // Yes - continue
			cfrm=1;
			break;
		case 1: // No - cancel
			cfrm=0;
			break;
		}

		if(!cfrm){
			return;
		}
	}
	
	if(gt.rules.nDaysPerWeek<=4){
		QString s;
		s=tr("You have less than 5 days per week, so probably you won't need this feature. Do you still want to continue?");
		
		int cfrm=0;
		switch( QMessageBox::question( this, tr("FET question"),
		 s,
		 tr("&Continue"), tr("&Cancel"), 0 , 1 ) ) {
		case 0: // Yes - continue
			cfrm=1;
			break;
		case 1: // No - cancel
			cfrm=0;
			break;
		}

		if(!cfrm){
			return;
		}
	}
	
	int confirm;
	
	SpreadConfirmationForm form;
	confirm=form.exec();

	if(confirm==QDialog::Accepted){
		SpreadMinDaysConstraintsFiveDaysForm form;
		form.exec();
	}
}

void FetMainForm::on_statisticsExportToDiskAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}

	StatisticsExport::exportStatistics();
}

void FetMainForm::on_removeRedundantConstraintsAction_activated()
{
	if(simulation_running){
		QMessageBox::information(this, tr("FET information"),
			tr("Allocation in course.\nPlease stop simulation before this."));
		return;
	}
	
	int confirm;
	
	RemoveRedundantConfirmationForm form;
	confirm=form.exec();

	if(confirm==QDialog::Accepted){
		RemoveRedundantForm form;
		form.exec();
	}
}

void FetMainForm::on_selectOutputDirAction_activated()
{
	QString od;
	
	od = QFileDialog::getExistingDirectory(this, tr("Choose results (output) directory"), OUTPUT_DIR);
	
	if(!od.isNull()){
		QFile test(od+FILE_SEP+"test_write_permissions_3.tmp");
		bool existedBefore=test.exists();
		bool t=test.open(QIODevice::ReadWrite);
		//if(!test.exists())
		//	t=false;
		if(!t){
			QMessageBox::warning(this, tr("FET warning"), tr("You don't have write permissions in this directory"));
			return;
		}
		test.close();
		if(!existedBefore)
			test.remove();
	
		OUTPUT_DIR=od;
	}
}

void FetMainForm::on_randomSeedAction_activated()
{
	RandomSeedDialog dialog;
	
	int te=dialog.exec();
	
	if(te==QDialog::Accepted){
		int tx=dialog.lineEdit->text().toInt();
		if(!(tx>=1 && tx<MM)){
			assert(0);
			//QMessageBox::warning(this, tr("FET warning"), tr("The random seed must be at least %1 and at most %2").arg(1).arg(MM-1));
			//return;
		}
		XX=tx;
	}
}

void FetMainForm::enableActivityTagMaxHoursDailyToggled(bool checked)
{
	if(checked==true){
		QString s=tr("These kinds of constraints are good, but not perfectly optimized. Adding such constraints may make your"
		 " timetable solve too slow or even impossible.");
		s+=" ";
		s+=tr("It is recommended to use such constraints only at the end, after you generated successfully with all the other constraints.");
		s+="\n\n";
		s+=tr("If your timetable is too difficult, it may be from these kinds of constraints, so you may need to remove them and retry.");
		s+="\n\n";
		s+=tr("Continue only if you know what you are doing.");
	
		QMessageBox::StandardButton b=QMessageBox::warning(this, tr("FET warning"), s, QMessageBox::Ok | QMessageBox::Cancel, QMessageBox::Ok);
	
		if(b!=QMessageBox::Ok){
			disconnect(enableActivityTagMaxHoursDailyAction, SIGNAL(toggled(bool)), this, SLOT(enableActivityTagMaxHoursDailyToggled(bool)));
			enableActivityTagMaxHoursDailyAction->setChecked(false);
			connect(enableActivityTagMaxHoursDailyAction, SIGNAL(toggled(bool)), this, SLOT(enableActivityTagMaxHoursDailyToggled(bool)));
			return;
		}
	}
	
	ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY=checked;

	setEnabledIcon(dataTimeConstraintsTeacherActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsTeachersActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
	setEnabledIcon(dataTimeConstraintsStudentsSetActivityTagMaxHoursDailyAction, ENABLE_ACTIVITY_TAG_MAX_HOURS_DAILY);
}

void FetMainForm::enableStudentsMaxGapsPerDayToggled(bool checked)
{
	if(checked==true){
		QString s=tr("These kinds of constraints are good, but not perfectly optimized. Adding such constraints may make your"
		 " timetable solve too slow or even impossible.");
		s+=" ";
		s+=tr("It is recommended to use such constraints only at the end, after you generated successfully with all the other constraints.");
		s+="\n\n";
		s+=tr("If your timetable is too difficult, it may be from these kinds of constraints, so you may need to remove them and retry.");
		s+="\n\n";
		s+=tr("Continue only if you know what you are doing.");
	
		QMessageBox::StandardButton b=QMessageBox::warning(this, tr("FET warning"), s, QMessageBox::Ok | QMessageBox::Cancel, QMessageBox::Ok);
	
		if(b!=QMessageBox::Ok){
			disconnect(enableStudentsMaxGapsPerDayAction, SIGNAL(toggled(bool)), this, SLOT(enableStudentsMaxGapsPerDayToggled(bool)));
			enableStudentsMaxGapsPerDayAction->setChecked(false);
			connect(enableStudentsMaxGapsPerDayAction, SIGNAL(toggled(bool)), this, SLOT(enableStudentsMaxGapsPerDayToggled(bool)));
			return;
		}
	}
	
	ENABLE_STUDENTS_MAX_GAPS_PER_DAY=checked;
	
	setEnabledIcon(dataTimeConstraintsStudentsSetMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
	setEnabledIcon(dataTimeConstraintsStudentsMaxGapsPerDayAction, ENABLE_STUDENTS_MAX_GAPS_PER_DAY);
}

void FetMainForm::showWarningForNotPerfectConstraintsToggled(bool checked)
{
	if(checked==false){
		QString s=tr("It is recommended to keep this warning active, but if you really want, you can disable it.");
		s+="\n\n";
		s+=tr("Disable it only if you know what you are doing.");
		s+="\n\n";
		s+=tr("Are you sure you want to disable it?");
	
		QMessageBox::StandardButton b=QMessageBox::warning(this, tr("FET warning"), s, QMessageBox::Yes | QMessageBox::Cancel, QMessageBox::Yes);
	
		if(b!=QMessageBox::Yes){
			disconnect(showWarningForNotPerfectConstraintsAction, SIGNAL(toggled(bool)), this, SLOT(showWarningForNotPerfectConstraintsToggled(bool)));
			showWarningForNotPerfectConstraintsAction->setChecked(true);
			connect(showWarningForNotPerfectConstraintsAction, SIGNAL(toggled(bool)), this, SLOT(showWarningForNotPerfectConstraintsToggled(bool)));
			return;
		}
	}
	
	SHOW_WARNING_FOR_NOT_PERFECT_CONSTRAINTS=checked;
}

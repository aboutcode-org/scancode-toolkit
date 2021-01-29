// $Id: Timestamp.cc 4406 2012-03-04 14:26:16Z flaterco $

// Timestamp:  A point in time.  See also Year, Date, Interval.

/*
    Copyright (C) 1998  David Flater.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "common.hh"


// If time_t is a signed 32-bit int, you get:
//    time_t 0x80000000 = 1901-12-13 20:45:52Z
//    time_t 0x00000000 = 1970-01-01 00:00:00Z
//    time_t 0x7FFFFFFF = 2038-01-19 03:14:07Z
// Posix does not require it to be signed, so the safe range is only
// 1970 to 2037.


#ifdef TIME_WORKAROUND

// ************************************
//     Begin derivative of GNU code
// ************************************

// When TIME_WORKAROUND is engaged, time_t is redefined as a signed
// 64-bit integer in common.hh.

// This function was lifted from the file time/offtime.c in
// glibc-2.3.1, made standalone, munged in a futile effort to avoid
// overflows, and renamed to avoid conflicting with any such function
// that is present on the compiling system.

// Replaced SECS_PER_HOUR and SECS_PER_DAY with HOURSECONDS and DAYSECONDS.
// Other modifications are flagged with DWF.

/* Copyright (C) 1991, 1993, 1997, 1998, 2002 Free Software Foundation, Inc.
   This file is part of the GNU C Library.

   The GNU C Library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   The GNU C Library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the GNU C Library; if not, write to the Free
   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
   02111-1307 USA.  */

// DWF: commented out
// #include <errno.h>
// #include <time.h>

// DWF: incorporated from glibc-2.3.1 time/mktime.c
/* Nonzero if YEAR is a leap year (every 4 years,
   except every 100th isn't, and every 400th is).  */
#define __isleap(year) \
  ((year) % 4 == 0 && ((year) % 100 != 0 || (year) % 400 == 0))

// DWF: incorporated from glibc-2.3.1 time/mktime.c, declared static
/* How many days come before each month (0-12).  */
static const unsigned short int __mon_yday[2][13] =
  {
    /* Normal years.  */
    { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 },
    /* Leap years.  */
    { 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366 }
  };

/* Compute the `struct tm' representation of *T,
   offset OFFSET seconds east of UTC,
   and store year, yday, mon, mday, wday, hour, min, sec into *TP.
   Return nonzero if successful.  */
// DWF: renamed, converted to C++ declaration syntax
static const int xtide_offtime (const time_t *t, long int offset, tm *tp)
{
  int64_t days, y; // DWF: 32 bits doesn't cut it
  long int rem;
  const unsigned short int *ip;

  days = *t / DAYSECONDS;  // DWF: here's why
  rem = *t % DAYSECONDS;
  rem += offset;
  while (rem < 0)
    {
      rem += DAYSECONDS;
      --days;
    }
  while (rem >= DAYSECONDS)
    {
      rem -= DAYSECONDS;
      ++days;
    }
  tp->tm_hour = rem / HOURSECONDS;
  rem %= HOURSECONDS;
  tp->tm_min = rem / 60;
  tp->tm_sec = rem % 60;
  /* January 1, 1970 was a Thursday.  */
  tp->tm_wday = (4 + days) % 7;
  if (tp->tm_wday < 0)
    tp->tm_wday += 7;
  y = 1970;

#define DIV(a, b) ((a) / (b) - ((a) % (b) < 0))
#define LEAPS_THRU_END_OF(y) (DIV (y, 4) - DIV (y, 100) + DIV (y, 400))

  while (days < 0 || days >= (__isleap (y) ? 366 : 365))
    {
      /* Guess a corrected year, assuming 365 days per year.  */
      // DWF: 64 bits
      int64_t yg = y + days / 365 - (days % 365 < 0);

      /* Adjust DAYS and Y to match the guessed year.  */
      days -= ((yg - y) * 365
	       + LEAPS_THRU_END_OF (yg - 1)
	       - LEAPS_THRU_END_OF (y - 1));
      y = yg;
    }
  tp->tm_year = y - 1900;
  if (tp->tm_year != y - 1900)
    {
      /* The year cannot be represented due to overflow.  */
      // DWF: Don't know where __set_errno came from but I don't have it
      // __set_errno (EOVERFLOW);
      errno = EOVERFLOW;
      return 0;
    }
  tp->tm_yday = days;
  ip = __mon_yday[__isleap(y)];
  for (y = 11; days < (long int) ip[y]; --y)
    continue;
  days -= ip[y];
  tp->tm_mon = y;
  tp->tm_mday = days + 1;
  return 1;
}

// **********************************
//     End derivative of GNU code
// **********************************

// Local version of gmtime, complete with internal static buffer.
// Returns null in case of trouble.
static tm const * const xtide_gmtime (const time_t *t) {
  static tm sstm;
  if (!(xtide_offtime (t, 0, &sstm)))
    return NULL;
  return &sstm;
}

// Redirection to workaround.
#define gmtime    xtide_gmtime
#define localtime xtide_gmtime


static void installTimeZone (const Dstr &timezone unusedParameter) {
  // The only use of time zones is by strftime for %Z
  static char env_string[80];
  static bool installed = false;
  if (!installed) {
    installed = true;
    strcpy (env_string, "TZ=UTC0");
    require (putenv (env_string) == 0);
    tzset();
  }
}


const bool Timestamp::zoneinfoIsNotHorriblyObsolete () const {
  // This method is unnecessary when TIME_WORKAROUND is engaged.
  return true;
}


#else
// Not TIME_WORKAROUND


/* Declarations for zoneinfo compatibility hack */
// This is getting to be really ancient history and maybe should be
// retired, but you never know.

/* It's not worth detecting or supporting POSIX because all the platforms
   I know of that support full POSIX with floating day rules do so by
   means of adopting Olson's code, in which case we just use the zoneinfo
   extensions anyway.  POSIX without floating day rules is useless. */

enum ZoneinfoSupportLevel {NEWZONEINFO=0,
                           OLDZONEINFO=1,
                           HP=2,
                           BRAINDEAD=3,
                           TZNULL=4};

static ZoneinfoSupportLevel zoneinfoSupportLevel (TZNULL);


/* The following were originally based on tzdata96i.  Since then the
   following churn has occurred:

   1999-12-12
   Added Antarctic stations from tzdata1999j
     The Antarctic time zones had previously been guesswork.

   2000-07-16
   Added America/Iqaluit and America/Hermosillo from tzdata2000d
     Sonora and Nunavut each made changes that forced new zones to
     become necessary.

   2000-08-30
   Added America/Goose_Bay from tzdata2000f.

   2000-10-01
   Added :America/Belem, :America/Fortaleza, :America/Maceio from
   tzdata2000d; revised abbreviation for Sao_Paulo.

   It's unfortunate that these zones will be broken on platforms
   having intermediate versions of the "new" zoneinfo.

   2004-09-16
   Added :America/Juneau, :America/Nome, :America/Yakutat and
   :Pacific/Johnston.

   2012-02-21
   Changed :Pacific/Apia from SST11 to WST-13.
   Doubtless there is worse code rot than that, but the correct fix is
   to delete this entire workaround, not to try to update it.
*/

/* In many cases, these substitutions will either break DST adjustments
   or will be incorrect for historical dates.  It's not worth documenting
   every single quirk when the whole thing is an obscene hack. */

static constString subs[][4] = {
{":Africa/Abidjan",             "WAT0", "WAT0", "WAT0"},
{":Africa/Accra",               "WAT0", "WAT0", "WAT0"},
{":Africa/Addis_Ababa",         "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Algiers",             "MET-1", "MET-1", "MET-1"},
{":Africa/Asmera",              "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Bamako",              "WAT0", "WAT0", "WAT0"},
{":Africa/Bangui",              "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Banjul",              "WAT0", "WAT0", "WAT0"},
{":Africa/Bissau",              "WAT0", "WAT0", "WAT0"},
{":Africa/Blantyre",            "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Brazzaville",         "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Bujumbura",           "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Cairo",               ":Egypt", "EET-2", "EET-2"},
{":Africa/Casablanca",          "WET0", "WET0", "WET0"},
{":Africa/Conakry",             "WAT0", "WAT0", "WAT0"},
{":Africa/Dakar",               "WAT0", "WAT0", "WAT0"},
{":Africa/Dar_es_Salaam",       "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Djibouti",            "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Douala",              "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Freetown",            "WAT0", "WAT0", "WAT0"},
{":Africa/Gaborone",            "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Harare",              "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Johannesburg",        "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Kampala",             "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Khartoum",            "EET-2", "EET-2", "EET-2"},
{":Africa/Kigali",              "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Kinshasa",            "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Lagos",               "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Libreville",          "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Lome",                "WAT0", "WAT0", "WAT0"},
{":Africa/Luanda",              "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Lumumbashi",          "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Lusaka",              "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Malabo",              "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Maputo",              "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Maseru",              "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Mbabane",             "SAT-2", "SAT-2", "SAT-2"},
{":Africa/Mogadishu",           "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Monrovia",            "WAT0", "WAT0", "WAT0"},
{":Africa/Nairobi",             "EAT-3", "EAT-3", "EAT-3"},
{":Africa/Ndjamena",            "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Niamey",              "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Nouakchott",          "WAT0", "WAT0", "WAT0"},
{":Africa/Ouagadougou",         "WAT0", "WAT0", "WAT0"},
{":Africa/Porto-Novo",          "CAT-1", "CAT-1", "CAT-1"},
{":Africa/Sao_Tome",            "WAT0", "WAT0", "WAT0"},
{":Africa/Timbuktu",            "WAT0", "WAT0", "WAT0"},
{":Africa/Tripoli",             ":Libya", "EET-2", "EET-2"},
{":Africa/Tunis",               "MET-1", "MET-1", "MET-1"},
{":Africa/Windhoek",            "SAT-2", "SAT-2", "SAT-2"},

{":America/Adak",               ":US/Aleutian", "HAST10HADT",  "AST10ADT"},
{":America/Anchorage",          ":US/Alaska", "AKST9AKDT", "YST9YDT"},
{":America/Anguilla",           "AST4", "AST4", "AST4"},
{":America/Antigua",            "AST4", "AST4", "AST4"},
{":America/Aruba",              "AST4", "AST4", "AST4"},
{":America/Asuncion",           "AST4", "AST4", "AST4"},
{":America/Atka",               ":US/Aleutian", "HAST10HADT",  "AST10ADT"},
{":America/Barbados",           "AST4", "AST4", "AST4"},
{":America/Belem",              ":Brazil/East", "BRT3", "BRT3"},
{":America/Belize",             "CST6", "CST6", "CST6"},
{":America/Bogota",             "EST5", "EST5", "EST5"},
{":America/Buenos_Aires",       "ARST3", "ARST3", "AST3"},
{":America/Caracas",            "AST4", "AST4", "AST4"},
{":America/Cayenne",            "EST3", "EST3", "EST3"},
{":America/Cayman",             "EST5", "EST5", "EST5"},
{":America/Chicago",            ":US/Central", "CST6CDT", "CST6CDT"},
{":America/Costa_Rica",         "CST6", "CST6", "CST6"},
{":America/Curacao",            "AST4", "AST4", "AST4"},
{":America/Denver",             ":US/Mountain", "MST7MDT", "MST7MDT"},
{":America/Detroit",            ":US/Eastern", "EST5EDT", "EST5EDT"},
{":America/Dominica",           "AST4", "AST4", "AST4"},
{":America/Edmonton",           ":Canada/Mountain", "MST7MDT", "MST7MDT"},
{":America/El_Salvador",        "CST6", "CST6", "CST6"},
{":America/Ensenada",           ":Mexico/BajaNorte", "PST8PDT", "PST8PDT"},
{":America/Fortaleza",          ":Brazil/East", "BRT3", "BRT3"},
{":America/Godthab",            "WGT3", "WGT3", "WGT3"},
{":America/Goose_Bay",          ":Canada/Atlantic", "AST4ADT", "AST4ADT"},
{":America/Grand_Turk",         ":US/Eastern", "EST5EDT", "EST5EDT"},
{":America/Grenada",            "AST4", "AST4", "AST4"},
{":America/Guadeloupe",         "AST4", "AST4", "AST4"},
{":America/Guatemala",          "CST6", "CST6", "CST6"},
{":America/Guayaquil",          "EST5", "EST5", "EST5"},
{":America/Guyana",             "EST3", "EST3", "EST3"},
{":America/Halifax",            ":Canada/Atlantic", "AST4ADT", "AST4ADT"},
{":America/Havana",             ":Cuba", "CST5", "CST5"},
{":America/Hermosillo",         "MST7", "MST7", "MST7"},
{":America/Iqaluit",            ":Canada/Eastern", "EST5EDT", "EST5EDT"},
{":America/Jamaica",            ":Jamaica", "EST5EDT", "EST5EDT"},
{":America/Juneau",             ":US/Alaska", "AKST9AKDT", "YST9YDT"},
{":America/La_Paz",             "AST4", "AST4", "AST4"},
{":America/Lima",               "EST5", "EST5", "EST5"},
{":America/Los_Angeles",        ":US/Pacific", "PST8PDT", "PST8PDT"},
{":America/Maceio",             ":Brazil/East", "BRT3", "BRT3"},
{":America/Managua",            "CST6", "CST6", "CST6"},
{":America/Manaus",             ":Brazil/West", "WST4", "WST4"},
{":America/Martinique",         "AST4", "AST4", "AST4"},
{":America/Mazatlan",           ":Mexico/BajaSur", "MST7MDT", "MST7MDT"},
{":America/Mexico_City",        "CST6", "CST6", "CST6"},
{":America/Miquelon",           "SPST3SPDT", "SPST3SPDT", "SST3SDT"},
{":America/Montevideo",         "EST3", "EST3", "EST3"},
{":America/Montreal",           ":Canada/Eastern", "EST5EDT", "EST5EDT"},
{":America/Montserrat",         "AST4", "AST4", "AST4"},
{":America/Nassau",             ":US/Eastern", "EST5EDT", "EST5EDT"},
{":America/New_York",           ":US/Eastern", "EST5EDT", "EST5EDT"},
{":America/Nome",               ":US/Alaska", "AKST9AKDT", "YST9YDT"},
{":America/Noronha",            ":Brazil/DeNoronha", "FST2", "FST2"},
{":America/Panama",             "EST5", "EST5", "EST5"},
{":America/Paramaribo",         "EST3", "EST3", "EST3"},
{":America/Port-au-Prince",     ":US/Eastern", "EST5EDT", "EST5EDT"},
{":America/Port_of_Spain",      "AST4", "AST4", "AST4"},
{":America/Porto_Acre",         ":Brazil/Acre", "AST5", "AST5"},
{":America/Puerto_Rico",        "AST4", "AST4", "AST4"},
{":America/Regina",             ":Canada/Saskatchewan", "CST6", "CST6"},
{":America/Santiago",           ":Chile/Continental", "CST4", "CST4"},
{":America/Santo_Domingo",      "AST4", "AST4", "AST4"},
{":America/Sao_Paulo",          ":Brazil/East", "BRT3", "BRT3"},
{":America/Scoresbysund",       "EGT1", "EGT1", "EGT1"},
{":America/St_Johns",      ":Canada/Newfoundland", "NST3:30NDT", "NST3:30NDT"},
{":America/St_Kitts",           "AST4", "AST4", "AST4"},
{":America/St_Lucia",           "AST4", "AST4", "AST4"},
{":America/St_Thomas",          "AST4", "AST4", "AST4"},
{":America/St_Vincent",         "AST4", "AST4", "AST4"},
{":America/Tegucigalpa",        "CST6", "CST6", "CST6"},
{":America/Thule",              "AST4", "AST4", "AST4"},
{":America/Tijuana",            ":Mexico/BajaNorte", "PST8PDT", "PST8PDT"},
{":America/Tortola",            "AST4", "AST4", "AST4"},
{":America/Vancouver",          ":Canada/Pacific", "PST8PDT", "PST8PDT"},
{":America/Whitehorse",         ":Canada/Yukon", "PST8PDT", "PST8PDT"},
{":America/Winnipeg",           ":Canada/Central", "CST6CDT", "CST6CDT"},
{":America/Yakutat",            ":US/Alaska", "AKST9AKDT", "YST9YDT"},

{":Antarctica/Casey",           "WST-8", "WST-8", "WST-8"},
{":Antarctica/Davis",           "DAVT-7", "DAVT-7", "DAVT-7"},
{":Antarctica/DumontDUrville",  "DDUT-10", "DDUT-10", "DDUT-10"},
{":Antarctica/Mawson",          "MAWT-6", "MAWT-6", "MAWT-6"},
{":Antarctica/McMurdo",         ":NZ", "NZST-12NZDT", "NST-12"},
{":Antarctica/Palmer",          ":Chile/Continental", "CST4", "CST4"},
{":Antarctica/South_Pole",      ":NZ", "NZST-12NZDT", "NST-12"},
{":Antarctica/Syowa",           "SYOT-3", "SYOT-3", "SYOT-3"},

{":Asia/Aden",                  "AST-3", "AST-3", "AST-3"},
{":Asia/Aktau",                 "ASK-5", "ASK-5", "ASK-5"},
{":Asia/Alma-Ata",              "AASK-6", "AASK-6", "ASK-6"},
{":Asia/Amman",                 "EET-2", "EET-2", "EET-2"},
{":Asia/Anadyr",                "ASK-13", "ASK-13", "ASK-13"},
{":Asia/Ashkhabad",             "ASK-5", "ASK-5", "ASK-5"},
{":Asia/Baghdad",               "AST-3", "AST-3", "AST-3"},
{":Asia/Bahrain",               "AST-3", "AST-3", "AST-3"},
{":Asia/Baku",                  "BSK-3", "BSK-3", "BSK-3"},
{":Asia/Bangkok",               "ICT-7", "ICT-7", "ICT-7"},
{":Asia/Beirut",                "EET-2", "EET-2", "EET-2"},
{":Asia/Bishkek",               "BSK-5", "BSK-5", "BSK-5"},
{":Asia/Brunei",                "BNT-8", "BNT-8", "BNT-8"},
{":Asia/Calcutta",              "IST-5:30", "IST-5:30", "IST-5:30"},
{":Asia/Colombo",               "IST-5:30", "IST-5:30", "IST-5:30"},
{":Asia/Dacca",                 "BGT-6", "BGT-6", "BGT-6"},
{":Asia/Damascus",              "EET-2", "EET-2", "EET-2"},
{":Asia/Dubai",                 "GST-4", "GST-4", "GST-4"},
{":Asia/Dushanbe",              "DSK-6", "DSK-6", "DSK-6"},
{":Asia/Gaza",                  "IST-2", "IST-2", "IST-2"},
{":Asia/Hong_Kong",             ":Hongkong", "HKT-8", "HKT-8"},
{":Asia/Irkutsk",               "ISK-8", "ISK-8", "ISK-8"},
{":Asia/Istanbul",              ":Turkey", "EET-2EETDST", "EET-2"},
{":Asia/Jakarta",               "JVT-7", "JVT-7", "JVT-7"},
{":Asia/Jayapura",              "MLT-9", "MLT-9", "MLT-9"},
{":Asia/Jerusalem",             ":Israel", "IST-2", "IST-2"},
{":Asia/Kabul",                 "AFT-4:30", "AFT-4:30", "AFT-4:30"},
{":Asia/Kamchatka",             "PSK-12", "PSK-12", "PSK-12"},
{":Asia/Karachi",               "PKT-5", "PKT-5", "PKT-5"},
{":Asia/Katmandu",              "NPT-5:45", "NPT-5:45", "NPT-5:45"},
{":Asia/Kuala_Lumpur",          "SGT-8", "SGT-8", "SGT-8"},
{":Asia/Kuwait",                "AST-3", "AST-3", "AST-3"},
{":Asia/Macao",                 "CST-8", "CST-8", "CST-8"},
{":Asia/Magadan",               "MSK-11", "MSK-11", "MSK-11"},
{":Asia/Manila",                "PST-8", "PST-8", "PST-8"},
{":Asia/Muscat",                "GST-4", "GST-4", "GST-4"},
{":Asia/Nicosia",               "EET-2", "EET-2", "EET-2"},
{":Asia/Novosibirsk",           "NSK-6", "NSK-6", "NSK-6"},
{":Asia/Omsk",                  "OSK-6", "OSK-6", "OSK-6"},
{":Asia/Phnom_Penh",            "ICT-7", "ICT-7", "ICT-7"},
{":Asia/Pyongyang",             "KST-9", "KST-9", "KST-9"},
{":Asia/Qatar",                 "AST-3", "AST-3", "AST-3"},
{":Asia/Rangoon",               "BMT-6:30", "BMT-6:30", "BMT-6:30"},
{":Asia/Riyadh",                "AST-3", "AST-3", "AST-3"},
{":Asia/Saigon",                "ICT-7", "ICT-7", "ICT-7"},
{":Asia/Seoul",                 ":ROK", "KST-9", "KST-9"},
{":Asia/Shanghai",              ":PRC", "CST-8", "CST-8"},
{":Asia/Singapore",             ":Singapore", "SGT-8", "SGT-8"},
{":Asia/Taipei",                ":ROC", "CST-8", "CST-8"},
{":Asia/Tashkent",              "TSK-5", "TSK-5", "TSK-5"},
{":Asia/Tbilisi",               "TBSK-4", "TBSK-4", "TSK-4"},
{":Asia/Tehran",                ":Iran", "IST-3:30", "IST-3:30"},
{":Asia/Tel_Aviv",              ":Israel", "IST-2", "IST-2"},
{":Asia/Thimbu",                "BGT-6", "BGT-6", "BGT-6"},
{":Asia/Tokyo",                 ":Japan", "JST-9", "JST-9"},
{":Asia/Ujung_Pandang",         "BNT-8", "BNT-8", "BNT-8"},
{":Asia/Ulan_Bator",            "UST-8", "UST-8", "UST-8"},
{":Asia/Vientiane",             "ICT-7", "ICT-7", "ICT-7"},
{":Asia/Vladivostok",           "VSK-10", "VSK-10", "VSK-10"},
{":Asia/Yakutsk",               "YSK-9", "YSK-9", "YSK-9"},
{":Asia/Yekaterinburg",         "ESK-5", "ESK-5", "ESK-5"},
{":Asia/Yerevan",               "AMST-4", "AMST-4", "AST-4"},

{":Atlantic/Azores",            "ACT1", "ACT1", "ACT1"},
{":Atlantic/Bermuda",           "AST4ADT", "AST4ADT", "AST4ADT"},
{":Atlantic/Canary",            ":WET", "WET0WETDST", "WET0"},
{":Atlantic/Cape_Verde",        "AAT1", "AAT1", "AAT1"},
{":Atlantic/Faeroe",            ":WET", "WET0WETDST", "WET0"},
{":Atlantic/Jan_Mayen",         "EGT1", "EGT1", "EGT1"},
{":Atlantic/Madeira",           ":WET", "WET0WETDST", "WET0"},
{":Atlantic/Reykjavik",         ":Iceland", "GMT0", "GMT0"},
{":Atlantic/South_Georgia",     "FST2", "FST2", "FST2"},
{":Atlantic/St_Helena",         "GMT0", "GMT0", "GMT0"},
{":Atlantic/Stanley",           "AST4", "AST4", "AST4"},

{":Australia/Adelaide",         ":Australia/South", "CST-9:30CDT", "CST-9:30"},
{":Australia/Brisbane",         ":Australia/Queensland", "EST-10", "EST-10"},
{":Australia/Broken_Hill", ":Australia/Yancowinna", "CST-9:30CDT", "CST-9:30"},
{":Australia/Canberra",         ":Australia/ACT", "EST-10EDT", "EST-10"},
{":Australia/Darwin",           ":Australia/North", "CST-9:30CDT", "CST-9:30"},
{":Australia/Hobart",           ":Australia/Tasmania", "EST-10EDT", "EST-10"},
{":Australia/Lord_Howe",        ":Australia/LHI", "LST-10:30", "LST-10:30"},
{":Australia/Melbourne",        ":Australia/Victoria", "EST-10EDT", "EST-10"},
{":Australia/Perth",            ":Australia/West", "WST-8", "WST-8"},
{":Australia/Sydney",           ":Australia/NSW", "EST-10EDT", "EST-10"},

/* No, it's not a screwup; they really did invert the signs on the
   GMT-offset files from one version to the next in order to "agree"
   with POSIX. */

{":Etc/GMT",                    ":GMT", "GMT0", "GMT0"},
{":Etc/GMT+0",                  ":GMT-0", "GMT0", "GMT0"},
{":Etc/GMT+1",                  ":GMT-1", "LST1", "LST1"},
{":Etc/GMT+10",                 ":GMT-10", "LST10", "LST10"},
{":Etc/GMT+11",                 ":GMT-11", "LST11", "LST11"},
{":Etc/GMT+12",                 ":GMT-12", "LST12", "LST12"},
{":Etc/GMT+2",                  ":GMT-2", "LST2", "LST2"},
{":Etc/GMT+3",                  ":GMT-3", "LST3", "LST3"},
{":Etc/GMT+4",                  ":GMT-4", "LST4", "LST4"},
{":Etc/GMT+5",                  ":GMT-5", "LST5", "LST5"},
{":Etc/GMT+6",                  ":GMT-6", "LST6", "LST6"},
{":Etc/GMT+7",                  ":GMT-7", "LST7", "LST7"},
{":Etc/GMT+8",                  ":GMT-8", "LST8", "LST8"},
{":Etc/GMT+9",                  ":GMT-9", "LST9", "LST9"},
{":Etc/GMT-0",                  ":GMT+0", "GMT0", "GMT0"},
{":Etc/GMT-1",                  ":GMT+1", "LST-1", "LST-1"},
{":Etc/GMT-10",                 ":GMT+10", "LST-10", "LST-10"},
{":Etc/GMT-11",                 ":GMT+11", "LST-11", "LST-11"},
{":Etc/GMT-12",                 ":GMT+12", "LST-12", "LST-12"},
{":Etc/GMT-13",                 ":GMT+13", "LST-13", "LST-13"},
{":Etc/GMT-2",                  ":GMT+2", "LST-2", "LST-2"},
{":Etc/GMT-3",                  ":GMT+3", "LST-3", "LST-3"},
{":Etc/GMT-4",                  ":GMT+4", "LST-4", "LST-4"},
{":Etc/GMT-5",                  ":GMT+5", "LST-5", "LST-5"},
{":Etc/GMT-6",                  ":GMT+6", "LST-6", "LST-6"},
{":Etc/GMT-7",                  ":GMT+7", "LST-7", "LST-7"},
{":Etc/GMT-8",                  ":GMT+8", "LST-8", "LST-8"},
{":Etc/GMT-9",                  ":GMT+9", "LST-9", "LST-9"},
{":Etc/GMT0",                   ":GMT+0", "GMT0", "GMT0"},
{":Etc/Greenwich",              ":Greenwich", "GMT0", "GMT0"},
{":Etc/UCT",                    ":UCT", "GMT0", "GMT0"},
{":Etc/UTC",                    ":UTC", "GMT0", "GMT0"},
{":Etc/Universal",              ":Universal", "GMT0", "GMT0"},
{":Etc/Zulu",                   ":Zulu", "GMT0", "GMT0"},

/* Although the tztab file from an old HP that I have doesn't contain
   EET-2EETDST, I'm going to gamble that they have added it by now.
   It's an obvious extension. */

{":Europe/Amsterdam",           ":MET", "MET-1METDST", "MET-1"},
{":Europe/Andorra",             ":MET", "MET-1METDST", "MET-1"},
{":Europe/Athens",              ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Belfast",             ":GB-Eire", "GMT0BST", "GMT0"},
{":Europe/Belgrade",            ":MET", "MET-1METDST", "MET-1"},
{":Europe/Berlin",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Bratislava",          ":MET", "MET-1METDST", "MET-1"},
{":Europe/Brussels",            ":MET", "MET-1METDST", "MET-1"},
{":Europe/Bucharest",           ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Budapest",            ":MET", "MET-1METDST", "MET-1"},
{":Europe/Chisinau",            ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Copenhagen",          ":MET", "MET-1METDST", "MET-1"},
{":Europe/Dublin",              ":GB-Eire", "GMT0BST", "GMT0"},
{":Europe/Gibraltar",           ":MET", "MET-1METDST", "MET-1"},
{":Europe/Helsinki",            ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Istanbul",            ":Turkey", "EET-2EETDST", "EET-2"},
{":Europe/Kiev",                ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Kuybyshev",           "KSK-4", "KSK-4", "KSK-4"},
{":Europe/Lisbon",              ":WET", "WET0WETDST", "WET0"},
{":Europe/Ljubljana",           ":MET", "MET-1METDST", "MET-1"},
{":Europe/London",              ":GB-Eire", "GMT0BST", "GMT0"},
{":Europe/Luxembourg",          ":MET", "MET-1METDST", "MET-1"},
{":Europe/Madrid",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Malta",               ":MET", "MET-1METDST", "MET-1"},
{":Europe/Minsk",               ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Monaco",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Moscow",              ":W-SU", "MSK-3", "MSK-3"},
{":Europe/Oslo",                ":MET", "MET-1METDST", "MET-1"},
{":Europe/Paris",               ":MET", "MET-1METDST", "MET-1"},
{":Europe/Prague",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Riga",                ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Rome",                ":MET", "MET-1METDST", "MET-1"},
{":Europe/San_Marino",          ":MET", "MET-1METDST", "MET-1"},
{":Europe/Sarajevo",            ":MET", "MET-1METDST", "MET-1"},
{":Europe/Simferopol",          ":W-SU", "MSK-3", "MSK-3"},
{":Europe/Skopje",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Sofia",               ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Stockholm",           ":MET", "MET-1METDST", "MET-1"},
{":Europe/Tallinn",             ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Tirane",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Vaduz",               ":MET", "MET-1METDST", "MET-1"},
{":Europe/Vatican",             ":MET", "MET-1METDST", "MET-1"},
{":Europe/Vienna",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Vilnius",             ":EET", "EET-2EETDST", "EET-2"},
{":Europe/Warsaw",              ":Poland", "MET-1METDST", "MET-1"},
{":Europe/Zagreb",              ":MET", "MET-1METDST", "MET-1"},
{":Europe/Zurich",              ":MET", "MET-1METDST", "MET-1"},

{":Indian/Antananarivo",        "EAT-3", "EAT-3", "EAT-3"},
{":Indian/Chagos",              "PKT-5", "PKT-5", "PKT-5"},
{":Indian/Christmas",           "JVT-7", "JVT-7", "JVT-7"},
{":Indian/Cocos",               "CCT-6:30", "CCT-6:30", "CCT-6:30"},
{":Indian/Comoro",              "EAT-3", "EAT-3", "EAT-3"},
{":Indian/Kerguelen",           "TFT-5", "TFT-5", "TFT-5"},
{":Indian/Mahe",                "SMT-4", "SMT-4", "SMT-4"},
{":Indian/Maldives",            "PKT-5", "PKT-5", "PKT-5"},
{":Indian/Mauritius",           "SMT-4", "SMT-4", "SMT-4"},
{":Indian/Mayotte",             "EAT-3", "EAT-3", "EAT-3"},
{":Indian/Reunion",             "SMT-4", "SMT-4", "SMT-4"},

{":Pacific/Apia",               "WST-13", "WST-13", "WST-13"},
{":Pacific/Auckland",           ":NZ", "NZST-12NZDT", "NST-12"},
{":Pacific/Chatham",            "CST-12:45", "CST-12:45", "CST-12:45"},
{":Pacific/Easter",             ":Chile/EasterIsland", "CST6", "CST6"},
{":Pacific/Efate",              "NCST-11", "NCST-11", "NST-11"},
{":Pacific/Enderbury",          "TGT-13", "TGT-13", "TGT-13"},
{":Pacific/Fakaofo",            "THT10", "THT10", "THT10"},
{":Pacific/Fiji",               "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Funafuti",           "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Galapagos",          "CST6", "CST6", "CST6"},
{":Pacific/Gambier",            "GBT9", "GBT9", "GBT9"},
{":Pacific/Guadalcanal",        "NCST-11", "NCST-11", "NST-11"},
{":Pacific/Guam",               "GST-10", "GST-10", "GST-10"},
{":Pacific/Honolulu",           ":US/Hawaii", "HST10", "HST10"},
{":Pacific/Johnston",           ":US/Hawaii", "HST10", "HST10"},
{":Pacific/Kiritimati",         "KRT-14", "KRT-14", "KRT-14"},
{":Pacific/Kosrae",             "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Kwajalein",          "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Majuro",             "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Marquesas",          "MQT9:30", "MQT9:30", "MQT9:30"},
{":Pacific/Midway",             "SST11", "SST11", "SST11"},
{":Pacific/Nauru",              "NZST-12", "NZST-12", "NST-12"}, 
{":Pacific/Niue",               "SST11", "SST11", "SST11"},
{":Pacific/Norfolk",            "NRFT-11:30", "NRFT-11:30", "NFT-11:30"},
{":Pacific/Noumea",             "NCST-11", "NCST-11", "NST-11"},
{":Pacific/Pago_Pago",          "SST11", "SST11", "SST11"},
{":Pacific/Palau",              "PLT-9", "PLT-9", "PLT-9"},
{":Pacific/Pitcairn",           "PIT8:30", "PIT8:30", "PIT8:30"},
{":Pacific/Ponape",             "NCST-11", "NCST-11", "NST-11"},
{":Pacific/Port_Moresby",       "EST-10", "EST-10", "EST-10"},
{":Pacific/Rarotonga",          "THT10", "THT10", "THT10"},
{":Pacific/Saipan",             "GST-10", "GST-10", "GST-10"},
{":Pacific/Samoa",              "SST11", "SST11", "SST11"},
{":Pacific/Tahiti",             "THT10", "THT10", "THT10"},
{":Pacific/Tarawa",             "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Tongatapu",          "TGT-13", "TGT-13", "TGT-13"},
{":Pacific/Truk",               "GST-10", "GST-10", "GST-10"},
{":Pacific/Wake",               "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Wallis",             "NZST-12", "NZST-12", "NST-12"},
{":Pacific/Yap",                "GST-10", "GST-10", "GST-10"},

/* Compatibility with outdated TZ specs */

{":US/Hawaii",                  ":US/Hawaii", "HST10",  "HST10"},
{":US/Aleutian",                ":US/Aleutian", "HAST10HADT",  "AST10ADT"},
{":US/Alaska",                  ":US/Alaska", "AKST9AKDT", "YST9YDT"},
{":US/Pacific",                 ":US/Pacific", "PST8PDT", "PST8PDT"},
{":US/Mountain",                ":US/Mountain", "MST7MDT", "MST7MDT"},
{":US/Central",                 ":US/Central", "CST6CDT", "CST6CDT"},
{":US/Eastern",                 ":US/Eastern", "EST5EDT", "EST5EDT"},

{":Canada/Pacific",             ":Canada/Pacific", "PST8PDT", "PST8PDT"},
{":Canada/Yukon",               ":Canada/Yukon", "PST8PDT", "PST8PDT"},
{":Canada/Mountain",            ":Canada/Mountain", "MST7MDT", "MST7MDT"},
{":Canada/Central",             ":Canada/Central", "CST6CDT", "CST6CDT"},
{":Canada/Saskatchewan",        ":Canada/Saskatchewan", "CST6", "CST6"},
{":Canada/East-Saskatchewan",   ":Canada/East-Saskatchewan", "CST6", "CST6"},
{":Canada/Eastern",             ":Canada/Eastern", "EST5EDT", "EST5EDT"},
{":Canada/Atlantic",            ":Canada/Atlantic", "AST4ADT", "AST4ADT"},
{":Canada/Newfoundland",   ":Canada/Newfoundland", "NST3:30NDT", "NST3:30NDT"},

{":Mexico/BajaNorte",           ":Mexico/BajaNorte", "PST8PDT", "PST8PDT"},
{":Mexico/BajaSur",             ":Mexico/BajaSur", "MST7MDT", "MST7MDT"},
{":Mexico/General",             "CST6", "CST6", "CST6"},

{":Brazil/West",                ":Brazil/West", "WST4", "WST4"},
{":Brazil/DeNoronha",           ":Brazil/DeNoronha", "FST2", "FST2"},
{":Brazil/East",                ":Brazil/East", "EST3", "EST3"},

{":Chile/Continental",          ":Chile/Continental", "CST4", "CST4"},
{":Chile/EasterIsland",         ":Chile/EasterIsland", "CST6", "CST6"},

{":Australia/ACT",              ":Australia/ACT", "EST-10EDT", "EST-10"},
{":Australia/LHI",              ":Australia/LHI", "LST-10:30", "LST-10:30"},
{":Australia/North",            ":Australia/North", "CST-9:30CDT", "CST-9:30"},
{":Australia/NSW",              ":Australia/NSW", "EST-10EDT", "EST-10"},
{":Australia/Queensland",       ":Australia/Queensland", "EST-10", "EST-10"},
{":Australia/South",            ":Australia/South", "CST-9:30CDT", "CST-9:30"},
{":Australia/Tasmania",         ":Australia/Tasmania", "EST-10EDT", "EST-10"},
{":Australia/Victoria",         ":Australia/Victoria", "EST-10EDT", "EST-10"},
{":Australia/West",             ":Australia/West", "WST-8", "WST-8"},
{":Australia/Yancowinna",  ":Australia/Yancowinna", "CST-9:30CDT", "CST-9:30"},

{":WET",                        ":WET", "WET0WETDST", "WET0"},
{":MET",                        ":MET", "MET-1METDST", "MET-1"},
{":EET",                        ":EET", "EET-2EETDST", "EET-2"},
{":GB-Eire",                    ":GB-Eire", "GMT0BST", "GMT0"},
{":PRC",                        ":PRC", "CST-8", "CST-8"},
{":ROC",                        ":ROC", "CST-8", "CST-8"},
{":ROK",                        ":ROK", "KST-9", "KST-9"},
{":W-SU",                       ":W-SU", "MSK-3", "MSK-3"},

{":Cuba",                       ":Cuba", "CST5", "CST5"},
{":Egypt",                      ":Egypt", "EET-2", "EET-2"},
{":Hongkong",                   ":Hongkong", "HKT-8", "HKT-8"},
{":Iceland",                    ":Iceland", "GMT0", "GMT0"},
{":Iran",                       ":Iran", "IST-3:30", "IST-3:30"},
{":Israel",                     ":Israel", "IST-2", "IST-2"},
{":Jamaica",                    ":Jamaica", "EST5EDT", "EST5EDT"},
{":Japan",                      ":Japan", "JST-9", "JST-9"},
{":Libya",                      ":Libya", "EET-2", "EET-2"},
{":Poland",                     ":Poland", "MET-1METDST", "MET-1"},
{":Singapore",                  ":Singapore", "SGT-8", "SGT-8"},
{":Turkey",                     ":Turkey", "EET-2EETDST", "EET-2"},

/* Terminator */
{NULL, NULL, NULL, NULL}};


// Unfortunately, time zones are a session default.
static void installTimeZone (const Dstr &timezone) {
  static Dstr currentTimezone;
  Dstr timezoneLocalVar ("UTC0");
  if (Global::settings["z"].c == 'n')
    timezoneLocalVar = timezone;
  if (currentTimezone == timezoneLocalVar)
    return;
  currentTimezone = timezoneLocalVar;

  static char env_string[80];
  char junk[80];
  junk[0] = '\0';

  if (zoneinfoSupportLevel == TZNULL) {
    // This should only be needed once.
    /* Probe to determine the zoneinfoSupportLevel -- hopefully this won't hose anybody */

    time_t testtime (time(NULL));

    /* This is needed on some Solaris and IRIX machines to avoid a false
       positive on NEWZONEINFO that happens when -gstart is used.  Don't
       know exactly what's up with that, but this fixes it. */
    strcpy (env_string, "TZ=GMT0");
    require (putenv (env_string) == 0);
    tzset();

    /* New zoneinfo? */
    strcpy (env_string, "TZ=:America/New_York");
    require (putenv (env_string) == 0);
    tzset();
    ::strftime (junk, 79, "%Z", localtime (&testtime));
    if (junk[0] == 'E') {
      zoneinfoSupportLevel = NEWZONEINFO;
    } else {

      Global::log ("\
XTide Warning:  Using obsolete time zone database.  Summer Time (Daylight\n\
Savings Time) adjustments will not be done for some locations.", LOG_WARNING);

      /* Old zoneinfo? */
      strcpy (env_string, "TZ=:US/Eastern");
      require (putenv (env_string) == 0);
      tzset();
      ::strftime (junk, 79, "%Z", localtime (&testtime));
      if (junk[0] == 'E') {
	zoneinfoSupportLevel = OLDZONEINFO;
      } else {

	/* HP-UX? */
#ifdef __hpux
	zoneinfoSupportLevel = HP;
#else
	zoneinfoSupportLevel = BRAINDEAD;
#endif
      }
    }
  }

  assert (zoneinfoSupportLevel != TZNULL);

  /* If our level of support is less than NEWZONEINFO, find the
     translation for the timezone string */
  if (zoneinfoSupportLevel != NEWZONEINFO)
    for (unsigned index=0; subs[index][0]; ++index)
      if (timezoneLocalVar == subs[index][0]) {
        timezoneLocalVar = subs[index][zoneinfoSupportLevel];
        break;
      }

  // If not found, soldier on with the original value.  The user might
  // know more than we do about what works.

  /* According to the SYSV man page, I can't alter env_string ever again. */
  sprintf (env_string, "TZ=%s", timezoneLocalVar.aschar());
  require (putenv (env_string) == 0);
  tzset();
}


const bool Timestamp::zoneinfoIsNotHorriblyObsolete() const {
  if (zoneinfoSupportLevel == TZNULL)
    installTimeZone ("UTC0");
  return (zoneinfoSupportLevel == NEWZONEINFO);
}


// Visual C++ 2005 causes program termination if you invoke time
// functions with year 3000 or later.  The following wrappers avoid
// that and produce the standard behavior of localtime and gmtime.
// Most sources say that a negative value (year before 1970) does not
// cause termination, but it certainly fails in any event, so it is
// harmless to check it here.

#if _MSC_VER == 1400

// _MAX__TIME64_T is defined in ctime.h, which VC++ conveniently
// prohibits us from including (ERROR: Use of C runtime library
// internal header file).
#define _MAX__TIME64_T 0x793406fffLL

static struct tm *vc_gmtime (const time_t *timep) {
  assert (timep);
  if (*timep >= 0 && *timep <= _MAX__TIME64_T)
    return gmtime (timep);
  return NULL;
}

static struct tm *vc_localtime (const time_t *timep) {
  assert (timep);
  if (*timep >= 0 && *timep <= _MAX__TIME64_T)
    return localtime (timep);
  return NULL;
}

// Redirection to workaround.
#define gmtime    vc_gmtime
#define localtime vc_localtime

// _MSC_VER == 1400
#endif
// TIME_WORKAROUND
#endif


// Overflow trap.
static const time_t overflowCheckedSum (time_t before,
					interval_rep_t interval) {
  time_t after (before + interval);
  if ((interval > 0 && after <= before) ||
      (interval < 0 && after >= before))
    Global::barf (Error::TIMESTAMP_OVERFLOW);
  return after;
}


enum TwoStateTz {UTC, LOCAL};


// Dispatch to gmtime or localtime as appropriate to tz.  Returns null
// whenever libc does.
static tm const * const tmPtr (time_t t, TwoStateTz tz) {
  switch (tz) {

  // In case of TIME_WORKAROUND, localtime and gmtime are redeffed to
  // the same thing.

  case LOCAL:
    return localtime (&t);
  case UTC:
    return gmtime (&t);
  default:
    assert (false);
  }
  return NULL; // Silence warning
}


// Convert to tm in specified time zone; die on failure.
static const tm tmStruct (time_t t, TwoStateTz tz) {
  const tm *tempTm (tmPtr (t, tz));
  assert (tempTm);
  return *tempTm;
}


// Compare two tm's according to the fields tm_year, tm_mon,
// tm_mday, tm_hour, tm_min, and tm_sec.  Returns:
//      > 0  if a > b
//        0  if a == b
//      < 0  if a < b
#define compareInt(a,b) (((int)(a))-((int)(b)))
static const int compareTmStruct (const tm &a, const tm &b) {
  int temp;
  if ((temp = compareInt (a.tm_year, b.tm_year)))
    return temp;
  if ((temp = compareInt (a.tm_mon, b.tm_mon)))
    return temp;
  if ((temp = compareInt (a.tm_mday, b.tm_mday)))
    return temp;
  if ((temp = compareInt (a.tm_hour, b.tm_hour)))
    return temp;
  if ((temp = compareInt (a.tm_min, b.tm_min)))
    return temp;
  return compareInt (a.tm_sec, b.tm_sec);
}


// Convert a tm to a time_t.  The fields used are tm_year, tm_mon,
// tm_mday, tm_hour, tm_min, and tm_sec.  All others are ignored,
// especially tm_isdst.

// Returns true on success, false if no such time.

// Justifications for reinventing the wheel (mktime):

// 1.  The failure returns of mktime are inconsistent and useless.  If
// a timestamp is too early, it returns (time_t)-1.  This is
// documented as the error return, but is also a valid timestamp.
// SUSV3 says mktime *may* set errno to indicate the error, but in
// fact it doesn't.  OTOH, if a timestamp is too late, mktime returns
// the maximum possible time_t, which gets passed off as the correct
// value only to cause an overflow somewhere else.

// 2.  It's messy to have to change the whole time zone context just
// to switch mktime between UTC and local time.  Messy, and
// occasionally fatal:  Sun's libc used to crash if I called tzset()
// too many times.  All you need do is call gmtime instead of
// localtime.

// 3.  mktime's "normalization" of impossible time specs is more bug
// than feature when parsing user input.  Garbage in should yield an
// error.

// Note assumption that time_t is integral.

static const bool mktime (const tm &timeToMake,
			  TwoStateTz tz,
			  time_t &time_out) {
  time_out = 0;
  int loopcounter = sizeof(time_t) * CHAR_BIT;
  time_t thebit = ((time_t)1) << (loopcounter-1);
  const tm *tempTm;

  // Is time_t signed?
  if (thebit < (time_t)0) {
    require (tempTm = tmPtr ((time_t)0, tz));
    bool is_negative = (compareTmStruct (timeToMake, *tempTm) < 0);

    switch (loopcounter) {
    case 32:
      // Get this sign thing out of the way.
      if (is_negative)
	time_out |= 0x80000000;
      loopcounter = 31;
      break;
    case 64:
      // Had a lot of trouble with overflows.  40 bits should suffice for
      // all reasonable requests.
      if (is_negative)
	time_out |= 0xFFFFFF0000000000LL;
      loopcounter = 40;
      break;
    default:
      // Weird sized time_t.
      // Skip the sign bit and hope for the best.
      // You can't just shift thebit right because it propagates the sign bit.
      --loopcounter;
    }
    thebit = ((time_t)1) << (loopcounter-1);
    assert (thebit > (time_t)0);
  } else {
    // time_t is unsigned.
    // Assuming no overflows, no action required here.
    ;
  }

  for (; loopcounter; --loopcounter) {
    time_t newguess = time_out | thebit;
    // If tmPtr fails, we assume that we are too far in the future.
    if ((tempTm = tmPtr (newguess, tz))) {
      int compare;
      if ((compare = compareTmStruct (*tempTm, timeToMake)) <= 0)
        time_out = newguess;
      if (compare == 0)
        return true;
    }
    assert (thebit > (time_t)0);
    thebit >>= 1;
  }

  assert (!thebit);
  if (!(tempTm = tmPtr (time_out, tz)))
    return false;
  return (compareTmStruct (*tempTm, timeToMake) == 0);
}


static void strftime (Dstr &text_out,
                      const tm &tmStruct,
                      const Dstr &formatString) {
  // Paranoid defensive coding because I don't trust strftime.
  char tempbuf[80] = {'\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0', 
                      '\0','\0','\0','\0','\0','\0','\0','\0','\0','\0'};
  size_t ret = strftime (tempbuf, 79, formatString.aschar(), &tmStruct);
  assert (ret < 79);

  // "Otherwise, 0 shall be returned and the contents of the array are
  // unspecified."

  tempbuf[ret] = '\0';
  text_out = tempbuf;
}


/**************************************************************************/


Timestamp::Timestamp () {}


// Create a Timestamp from a Posix timestamp.
Timestamp::Timestamp (time_t posixTime):
  Nullable(false),
  _posixTime(posixTime) {}


// The beginning of time (1970-01-01 00:00:00Z) as a Julian date.
const static double beginningOfTimeJD (2440587.5);


// Create a Timestamp for the specified Julian date.
// N.B. must avoid name clash between input parameter and jd().
Timestamp::Timestamp (double julianDate):
  Nullable(false),
  _posixTime((time_t)((julianDate - beginningOfTimeJD) * DAYSECONDS)) {

  // Not sure when the end of time is, exactly, since we aren't sure
  // what the underlying type of time_t is.  But we can do this:
  if (fabs(julianDate - jd()) > 2.3e-5) // Roughly 2 seconds
    Global::barf (Error::TIMESTAMP_OVERFLOW);
}


// Convert to Julian date.
const double Timestamp::jd() const {
  assert (!_isNull);
  return ((double)_posixTime / (double)DAYSECONDS) + beginningOfTimeJD;
}


// Create a Timestamp for the beginning of the specified year in UTC
// (YEAR-01-01 00:00:00Z), or a null timestamp if not possible.
Timestamp::Timestamp (Year year) {
  tm tempTm;
  tempTm.tm_year = year.val() - 1900;
  tempTm.tm_sec = tempTm.tm_min = tempTm.tm_hour = tempTm.tm_mon = 0;
  tempTm.tm_mday = 1;
  if (mktime (tempTm, UTC, _posixTime))
    _isNull = false;
  // Else stay null
}


const Year Timestamp::year() const {
  assert (!_isNull);
  return Year (((::tmStruct(_posixTime,UTC)).tm_year) + 1900);
}


const date_t Timestamp::date (const Dstr &timezone) const {
  const tm tempTm (tmStruct (timezone));
  return (tempTm.tm_year + 1900) * 10000UL +
         (tempTm.tm_mon + 1) * 100UL +
          tempTm.tm_mday;
}


// Subtract b from a.
const Interval operator- (Timestamp a, Timestamp b) {
  if (sizeof(interval_rep_t) > sizeof(time_t))
    return Interval ((interval_rep_t)(a.timet()) -
                     (interval_rep_t)(b.timet()));
  return Interval (a.timet() - b.timet());
}


const bool operator> (Timestamp a, Timestamp b) {
  return (a.timet() > b.timet());
}


const bool operator>= (Timestamp a, Timestamp b) {
  return (a.timet() >= b.timet());
}


const bool operator< (Timestamp a, Timestamp b) {
  return (a.timet() < b.timet());
}


const bool operator<= (Timestamp a, Timestamp b) {
  return (a.timet() <= b.timet());
}


void Timestamp::operator+= (Interval b) {
  assert (!_isNull);
  _posixTime = overflowCheckedSum (_posixTime, b.s());
}


void Timestamp::operator-= (Interval b) {
  operator+= (-b);
}


const Timestamp operator+ (Timestamp a, Interval b) {
  a += b;
  return a;
}


const Timestamp operator- (Timestamp a, Interval b) {
  a -= b;
  return a;
}


const bool operator== (Timestamp a, Timestamp b) {
  return (a.timet() == b.timet());
}


const bool operator!= (Timestamp a, Timestamp b) {
  return !(a == b);
}


const tm Timestamp::tmStruct (const Dstr &timezone) const {
  assert (!_isNull);
  installTimeZone (timezone);
  return ::tmStruct (_posixTime, LOCAL);
}


void Timestamp::strftime (Dstr &text_out,
                          const Dstr &timezone,
			  const Dstr &formatString) const {
  assert (!_isNull);
  ::strftime (text_out, tmStruct(timezone), formatString);
}


// Output timestamp in format complying with RFC 2445 (iCalendar)
// zeroOutSecs:  YYYYMMDDTHHMM00Z
// keepSecs:     YYYYMMDDTHHMMSSZ
//
// RFC 2445 p. 140, Recommended Practices:
// 7.  If seconds of the minute are not supported by an implementation,
//     then a value of "00" SHOULD be specified for the seconds
//     component in a time value.
// We have seconds, but they aren't significant.

void Timestamp::print_iCalendar (Dstr &text_out, SecStyle secStyle) const {
  assert (!_isNull);
  ::strftime (text_out,
             ::tmStruct(_posixTime,UTC),
             (secStyle == zeroOutSecs ? "%Y%m%dT%H%M00Z" : "%Y%m%dT%H%M%SZ"));
}


void Timestamp::print (Dstr &text_out, const Dstr &timezone) const {
  Dstr formatString (Global::settings["df"].s);
  formatString += ' ';
  formatString += Global::settings["tf"].s;
  strftime (text_out, timezone, formatString);
}


void Timestamp::printHour (Dstr &text_out, const Dstr &timezone) const {
  strftime (text_out, timezone, Global::settings["hf"].s);
  // Kludge to get rid of leading space on hours
  if (text_out[0] == ' ')
    text_out /= 1;
}


void Timestamp::printDate (Dstr &text_out, const Dstr &timezone) const {
  strftime (text_out, timezone, Global::settings["df"].s);
}


void Timestamp::printTime (Dstr &text_out, const Dstr &timezone) const {
  strftime (text_out, timezone, Global::settings["tf"].s);
  // Kludge to get rid of leading space on hours
  if (text_out[0] == ' ')
    text_out /= 1;
}


void Timestamp::printCalendarHeading (Dstr &text_out,
                                      const Dstr &timezone) const {
  strftime (text_out, timezone, "%B %Y");
}


void Timestamp::printCalendarDay (Dstr &text_out,
                                  const Dstr &timezone) const {
  strftime (text_out, timezone, "%a %d");
}


Timestamp::Timestamp (const Dstr &timeString, const Dstr &timezone) {
  tm tempTm;
  tempTm.tm_sec = 0;
  // Deliberately using %u instead of %d so that dashes won't be
  // interpreted as minus signs.  This causes compiler warnings.
  quashWarning(-Wformat)
  if (sscanf (timeString.aschar(), "%u-%u-%u %u:%u",
    &(tempTm.tm_year),
    &(tempTm.tm_mon),
    &(tempTm.tm_mday),
    &(tempTm.tm_hour),
    &(tempTm.tm_min)) != 5) {
  unquashWarning
    Dstr details ("The offending time specification was ");
    details += timeString;
    Global::barf (Error::BAD_TIMESTAMP, details);
  }
  tempTm.tm_year -= 1900;
  tempTm.tm_mon -= 1;
  installTimeZone (timezone);
  _isNull = !(mktime (tempTm, LOCAL, _posixTime));
}


void Timestamp::floorHour (const Dstr &timezone) {
  assert (!_isNull);
  installTimeZone (timezone);

  // Assuming no leap seconds.
  time_t lowerBound (overflowCheckedSum (_posixTime, -HOURSECONDS));

  /* The easy case will work unless we are hosed by DST. */
  tm tempTm (::tmStruct (_posixTime, LOCAL));
  time_t normalGuess (overflowCheckedSum (_posixTime,
                      -(tempTm.tm_min * 60 + tempTm.tm_sec)));
  assert (normalGuess > lowerBound && normalGuess <= _posixTime);
  tempTm = ::tmStruct (normalGuess, LOCAL);
  if (tempTm.tm_min == 0 && tempTm.tm_sec == 0) {
    _posixTime = normalGuess;
    return;
  }

  /* See if we went back too far. */
  time_t overshotGuess (overflowCheckedSum (normalGuess,
	        HOURSECONDS - (tempTm.tm_min * 60 + tempTm.tm_sec)));
  if (overshotGuess > lowerBound && overshotGuess <= _posixTime) {
    tempTm = ::tmStruct (overshotGuess, LOCAL);
    if (tempTm.tm_min == 0 && tempTm.tm_sec == 0) {
      _posixTime = overshotGuess;
      return;
    }
  }

  // Go back farther.  Unlike floorDay, we do not want to find the
  // location of a discontinuity if the transition is missing but
  // instead proceed to the next transition.
  _posixTime = normalGuess;
  floorHour(timezone);
}


void Timestamp::nextHour (const Dstr &timezone) {
  assert (!_isNull);
  installTimeZone (timezone);

  // Simply adding HOURSECONDS and then falling back if we overshot
  // works in nearly all cases if nextHour is used as directed (always
  // starting on an hour boundary), but see commentary in nextDay.

  tm tempTm (::tmStruct (_posixTime, LOCAL));
  time_t normalGuess (overflowCheckedSum (_posixTime, std::max (1,
                                               HOURSECONDS - tempTm.tm_min * 60
			       				   - tempTm.tm_sec)));
  tempTm = ::tmStruct (normalGuess, LOCAL);
  if (tempTm.tm_min == 0 && tempTm.tm_sec == 0) {
    _posixTime = normalGuess;
    return;
  }

  /* See if we went forward too far. */
  time_t overshotGuess (overflowCheckedSum (normalGuess,
                        -(tempTm.tm_min * 60 + tempTm.tm_sec)));
  if (overshotGuess > _posixTime && overshotGuess < normalGuess) {
    tempTm = ::tmStruct (overshotGuess, LOCAL);
    if (tempTm.tm_min == 0 && tempTm.tm_sec == 0) {
      _posixTime = overshotGuess;
      return;
    }
  }

  // Go forward some more.  Unlike nextDay, we do not want to find the
  // location of a discontinuity if the transition is missing but
  // instead proceed to the next transition.
  _posixTime = normalGuess;
  nextHour(timezone);
  /* That will work, even though we are not starting on an hour transition. */
}


void Timestamp::floorDay (const Dstr &timezone) {
  assert (!_isNull);
  installTimeZone (timezone);

  // Assuming no leap seconds.
  time_t lowerBound (overflowCheckedSum (_posixTime, -DAYSECONDS));

  /* The easy case will work unless we are hosed by DST. */
  tm tempTm (::tmStruct (_posixTime, LOCAL));
  int today (tempTm.tm_mday);
  time_t normalGuess (overflowCheckedSum (_posixTime,
				   -(tempTm.tm_hour * HOURSECONDS +
                                     tempTm.tm_min * 60 + tempTm.tm_sec)));
  assert (normalGuess > lowerBound && normalGuess <= _posixTime);
  tempTm = ::tmStruct (normalGuess, LOCAL);
  if (tempTm.tm_hour == 0 && tempTm.tm_sec == 0 && tempTm.tm_min == 0) {
    _posixTime = normalGuess;
    return;
  }

  /* See if we went back too far. */
  if (tempTm.tm_mday != today) {

    // Most likely case:  sprung forward at 02:00,
    //                    correct result is still at 00:00 (one hour later).
    // Also possible:  sprung forward at midnight, so there is no midnight,
    //                 correct result is at 01:00 (one hour later) or
    //                 00:20 or 00:30 for 1/3 and 1/2 summer time (0:20
    //                 or 0:30 later, respectively).
    // Also possible:  sprung forward at 23:30, so there is no midnight,
    //                 correct result is at 00:30 (half an hour later).

    // The case where midnight comes twice doesn't end up here.  We
    // would have returned normally above, having no idea that there
    // was another midnight to choose from (oops).  So we are safe
    // using brute force to locate the timepoint at which the day
    // changes according to tmStruct.

    int yesterday (tempTm.tm_mday);
    assert (yesterday != today);
    assert (yesterday + 1 == today || today == 1);
    time_t lowerGuess (normalGuess);
    time_t upperGuess (overflowCheckedSum (normalGuess, std::max (1,
                                      DAYSECONDS - tempTm.tm_hour * HOURSECONDS
                                                 - tempTm.tm_min * 60
						 - tempTm.tm_sec)));
    tempTm = ::tmStruct (upperGuess, LOCAL);
    assert (tempTm.tm_mday == today);

    while (upperGuess - lowerGuess > 1) {
      time_t middleGuess (overflowCheckedSum (lowerGuess,
                                              (upperGuess - lowerGuess) / 2));
      tempTm = ::tmStruct (middleGuess, LOCAL);
      assert (tempTm.tm_mday == yesterday || tempTm.tm_mday == today);
      if (tempTm.tm_mday == yesterday)
        lowerGuess = middleGuess;
      else
        upperGuess = middleGuess;
    }
    // Note assumption that time_t is integral.
    assert (upperGuess == lowerGuess + 1);
    _posixTime = upperGuess;
    return;
  }

  /* Go back farther. */
  _posixTime = normalGuess;
  floorDay (timezone);
}


void Timestamp::nextDay (const Dstr &timezone) {
  assert (!_isNull);
  installTimeZone (timezone);

  // Step forward to the predicted location of the next day
  // transition.  Simply adding DAYSECONDS and then invoking floorDay
  // in case of overshot works in nearly all cases if nextDay is used
  // as directed (always starting on a day boundary), but it can miss
  // a day if there is more than one DST change in a 24-hour period.
  // This only occurs under artificial conditions (:Asia/Riyadh89,
  // 1989-12-31 and 1990-01-01, zoneinfo falls back 1/2 minute at noon
  // and then springs forward 3 minutes at midnight because the rules
  // expire), but it is easy to prevent the problem anyway by only
  // stepping forward as much as is expected to be necessary.

  // The minimum delta of 1 second is to protect against the
  // eventuality that somebody might enable leap seconds and we would
  // get stuck at 23:59:60.

  tm tempTm (::tmStruct (_posixTime, LOCAL));
  int today (tempTm.tm_mday);
  _posixTime = overflowCheckedSum (_posixTime, std::max (1,
                                      DAYSECONDS - tempTm.tm_hour * HOURSECONDS
                                                 - tempTm.tm_min * 60
						 - tempTm.tm_sec));
  tempTm = ::tmStruct (_posixTime, LOCAL);
  if (tempTm.tm_hour == 0 && tempTm.tm_min == 0 && tempTm.tm_sec == 0) {
    return;
  }

  /* See if we went forward too far. */
  if (tempTm.tm_mday != today) {
    floorDay (timezone);
    return;
  }

  /* Go forward farther. */
  nextDay (timezone);
  /* That will work, even though we are not starting on a day transition. */
}


const time_t Timestamp::timet() const {
  assert (!_isNull);
  return _posixTime;
}


// The moonrise and moonset logic blows up if you go before 1900 or
// after 2099.  This is just a range check for that.
const bool Timestamp::inRangeForLunarRiseSet() const {
  double skycalYear = 1900. + (jd() - 2415019.5) / 365.25;
  return (skycalYear > 1900.1 && skycalYear < 2099.9);
}

// Cleanup2006 Cruft BlamePosix

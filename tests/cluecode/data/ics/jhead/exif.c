#define TAG_CFA_REPEAT_PATTERN_DIM 0x828D
#define TAG_CFA_PATTERN1           0x828E
#define TAG_BATTERY_LEVEL          0x828F
#define TAG_COPYRIGHT              0x8298
#define TAG_EXPOSURETIME           0x829A
#define TAG_FNUMBER                0x829D
  { TAG_CFA_REPEAT_PATTERN_DIM, "CFARepeatPatternDim", 0, 0},
  { TAG_CFA_PATTERN1,           "CFAPattern", 0, 0},
  { TAG_BATTERY_LEVEL,          "BatteryLevel", 0, 0},
  { TAG_COPYRIGHT,              "Copyright", FMT_STRING, -1},
  { TAG_EXPOSURETIME,           "ExposureTime", FMT_SRATIONAL, 1},
  { TAG_FNUMBER,                "FNumber", FMT_SRATIONAL, 1},
//        }
        for (a = 0; a < length - 8; ++a) {
            unsigned char c = *(ExifSection+8+a);
            unsigned pc = isprint(c) ? c : ' ';
            printf("Map: %4d %02x %c", a, c, pc);
        }
                        printf("\n");
                    }
                }else{
                    putchar(c);
                }
            }
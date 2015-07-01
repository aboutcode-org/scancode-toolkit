// Copyright (c) 2010 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
// 98:d=1  hl=2 l=  93 cons:  SET
//100:d=2  hl=2 l=  91 cons:   SEQUENCE
//102:d=3  hl=2 l=   3 prim:    OBJECT            :organizationName
//107:d=3  hl=2 l=  84 prim:    UTF8STRING        :TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş. (c) Kasım 2005
static const uint8 TurkTrustDN[] = {
  0x30, 0x81, 0xbe, 0x31, 0x3f, 0x30, 0x3d, 0x06, 0x03, 0x55, 0x04, 0x03, 0x0c,
//125:d=3  hl=2 l=  37 cons:    SET
//127:d=4  hl=2 l=  35 cons:     SEQUENCE
//129:d=5  hl=2 l=   3 prim:      OBJECT            :organizationalUnitName
//134:d=5  hl=2 l=  28 prim:      PRINTABLESTRING   :(c) 1999 Entrust.net Limited
//164:d=3  hl=2 l=  51 cons:    SET
//166:d=4  hl=2 l=  49 cons:     SEQUENCE
  EXPECT_EQ("TR", turktrust.country_name);
  EXPECT_EQ("Ankara", turktrust.locality_name);
  ASSERT_EQ(1U, turktrust.organization_names.size());
  EXPECT_EQ("TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş. (c) Kasım 2005",
            turktrust.organization_names[0]);
}
  ASSERT_EQ(2U, entrust.organization_unit_names.size());
  EXPECT_EQ("www.entrust.net/CPS_2048 incorp. by ref. (limits liab.)",
            entrust.organization_unit_names[0]);
  EXPECT_EQ("(c) 1999 Entrust.net Limited",
            entrust.organization_unit_names[1]);
}
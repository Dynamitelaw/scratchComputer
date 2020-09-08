*SPICE netlist created from BLIF module map9v3 by blif2BSpice
.include /usr/share/qflow/tech/osu035/osu035_stdcells.sp
.subckt map9v3 vdd gnd clock reset start N<0> N<1> N<2> N<3> N<4> N<5> N<6> N<7> N<8> dp<0> dp<1> dp<2> dp<3> dp<4> dp<5> dp<6> dp<7> dp<8> done counter<0> counter<1> counter<2> counter<3> counter<4> counter<5> counter<6> counter<7> sr<0> sr<1> sr<2> sr<3> sr<4> sr<5> sr<6> sr<7> 
XBUFX4_1 vdd gnd _98_ _98__bF$buf3 BUFX4
XBUFX4_2 vdd gnd _98_ _98__bF$buf2 BUFX4
XBUFX4_3 vdd gnd _98_ _98__bF$buf1 BUFX4
XBUFX2_1 vdd gnd _98_ _98__bF$buf0 BUFX2
XBUFX2_2 vdd gnd clock clock_bF$buf4 BUFX2
XBUFX2_3 vdd gnd clock clock_bF$buf3 BUFX2
XBUFX2_4 vdd gnd clock clock_bF$buf2 BUFX2
XBUFX2_5 vdd gnd clock clock_bF$buf1 BUFX2
XBUFX2_6 vdd gnd clock clock_bF$buf0 BUFX2
XBUFX4_4 vdd gnd _56_ _56__bF$buf4 BUFX4
XBUFX4_5 vdd gnd _56_ _56__bF$buf3 BUFX4
XBUFX4_6 vdd gnd _56_ _56__bF$buf2 BUFX4
XBUFX4_7 vdd gnd _56_ _56__bF$buf1 BUFX4
XBUFX4_8 vdd gnd _56_ _56__bF$buf0 BUFX4
XBUFX2_7 vdd gnd _97_ _97__bF$buf3 BUFX2
XBUFX2_8 vdd gnd _97_ _97__bF$buf2 BUFX2
XBUFX2_9 vdd gnd _97_ _97__bF$buf1 BUFX2
XBUFX2_10 vdd gnd _97_ _97__bF$buf0 BUFX2
XINVX4_1 vdd gnd _97_ state<0> INVX4
XINVX8_1 vdd gnd state<3> _98_ INVX8
XNOR2X1_1 vdd _117_<2> gnd _99_ _117_<3> NOR2X1
XNOR2X1_2 vdd _117_<4> gnd _100_ _117_<5> NOR2X1
XNAND2X1_1 vdd _101_ gnd _99_ _100_ NAND2X1
XNOR2X1_3 vdd _117_<6> gnd _102_ _117_<7> NOR2X1
XNOR2X1_4 vdd _117_<0> gnd _103_ _117_<1> NOR2X1
XNAND2X1_2 vdd _104_ gnd _102_ _103_ NAND2X1
XNOR2X1_5 vdd _101_ gnd _105_ _104_ NOR2X1
XOAI21X1_1 gnd vdd _98__bF$buf3 _105_ _6_ _97__bF$buf3 OAI21X1
XINVX1_1 state<4> _106_ vdd gnd INVX1
XINVX1_2 state<1> _107_ vdd gnd INVX1
XINVX1_3 startbuf<0> _108_ vdd gnd INVX1
XNOR2X1_6 vdd _108_ gnd _109_ startbuf<1> NOR2X1
XOAI21X1_2 gnd vdd _107_ _109_ _7_ _106_ OAI21X1
XINVX1_4 _119_<1> _110_ vdd gnd INVX1
XNAND3X1_1 _97__bF$buf2 vdd gnd state<2> _98__bF$buf2 _111_ NAND3X1
XNOR2X1_7 vdd _111_ gnd _112_ _120_<0> NOR2X1
XAOI21X1_1 gnd vdd _110_ _111_ _2_<1> _112_ AOI21X1
XINVX1_5 _119_<2> _113_ vdd gnd INVX1
XINVX1_6 _120_<1> _114_ vdd gnd INVX1
XMUX2X1_1 _111_ vdd gnd _2_<2> _113_ _114_ MUX2X1
XINVX1_7 _119_<3> _115_ vdd gnd INVX1
XINVX1_8 _120_<2> _116_ vdd gnd INVX1
XMUX2X1_2 _111_ vdd gnd _2_<3> _115_ _116_ MUX2X1
XINVX1_9 _119_<4> _8_ vdd gnd INVX1
XINVX1_10 _120_<3> _9_ vdd gnd INVX1
XMUX2X1_3 _111_ vdd gnd _2_<4> _8_ _9_ MUX2X1
XINVX1_11 _119_<5> _10_ vdd gnd INVX1
XINVX1_12 _120_<4> _11_ vdd gnd INVX1
XMUX2X1_4 _111_ vdd gnd _2_<5> _10_ _11_ MUX2X1
XINVX1_13 _119_<6> _12_ vdd gnd INVX1
XINVX1_14 _120_<5> _13_ vdd gnd INVX1
XMUX2X1_5 _111_ vdd gnd _2_<6> _12_ _13_ MUX2X1
XINVX1_15 _119_<7> _14_ vdd gnd INVX1
XINVX1_16 _120_<6> _15_ vdd gnd INVX1
XMUX2X1_6 _111_ vdd gnd _2_<7> _14_ _15_ MUX2X1
XINVX1_17 _119_<8> _16_ vdd gnd INVX1
XINVX1_18 _120_<7> _17_ vdd gnd INVX1
XMUX2X1_7 _111_ vdd gnd _2_<8> _16_ _17_ MUX2X1
XINVX1_19 _119_<0> _18_ vdd gnd INVX1
XNOR2X1_8 vdd _111_ gnd _19_ N<0> NOR2X1
XAOI21X1_2 gnd vdd _18_ _111_ _2_<0> _19_ AOI21X1
XXNOR2X1_1 _120_<5> _120_<7> gnd vdd _20_ XNOR2X1
XNOR2X1_9 vdd _9_ gnd _21_ _120_<4> NOR2X1
XNOR2X1_10 vdd _11_ gnd _22_ _120_<3> NOR2X1
XOAI21X1_3 gnd vdd _21_ _22_ _23_ _20_ OAI21X1
XNOR2X1_11 vdd _13_ gnd _24_ _120_<7> NOR2X1
XNOR2X1_12 vdd _17_ gnd _25_ _120_<5> NOR2X1
XXNOR2X1_2 _120_<3> _120_<4> gnd vdd _26_ XNOR2X1
XOAI21X1_4 gnd vdd _24_ _25_ _27_ _26_ OAI21X1
XNAND2X1_3 vdd _28_ gnd _23_ _27_ NAND2X1
XOAI21X1_5 gnd vdd state<3> _120_<0> _29_ _97__bF$buf1 OAI21X1
XAOI21X1_3 gnd vdd _28_ state<3> _3_<0> _29_ AOI21X1
XOAI21X1_6 gnd vdd _120_<1> _98__bF$buf1 _30_ _97__bF$buf0 OAI21X1
XAOI21X1_4 gnd vdd _98__bF$buf0 _116_ _3_<2> _30_ AOI21X1
XOAI21X1_7 gnd vdd _120_<2> _98__bF$buf3 _31_ _97__bF$buf3 OAI21X1
XAOI21X1_5 gnd vdd _98__bF$buf2 _9_ _3_<3> _31_ AOI21X1
XOAI21X1_8 gnd vdd _120_<3> _98__bF$buf1 _32_ _97__bF$buf2 OAI21X1
XAOI21X1_6 gnd vdd _98__bF$buf0 _11_ _3_<4> _32_ AOI21X1
XOAI21X1_9 gnd vdd _120_<4> _98__bF$buf3 _33_ _97__bF$buf1 OAI21X1
XAOI21X1_7 gnd vdd _98__bF$buf2 _13_ _3_<5> _33_ AOI21X1
XOAI21X1_10 gnd vdd _120_<5> _98__bF$buf1 _34_ _97__bF$buf0 OAI21X1
XAOI21X1_8 gnd vdd _98__bF$buf0 _15_ _3_<6> _34_ AOI21X1
XOAI21X1_11 gnd vdd _120_<6> _98__bF$buf3 _35_ _97__bF$buf3 OAI21X1
XAOI21X1_9 gnd vdd _98__bF$buf2 _17_ _3_<7> _35_ AOI21X1
XINVX1_20 N<1> _36_ vdd gnd INVX1
XNOR2X1_13 vdd _98__bF$buf1 gnd _37_ _117_<0> NOR2X1
XAND2X2_1 vdd gnd _98__bF$buf0 _117_<0> _38_ AND2X2
XOAI21X1_12 gnd vdd _37_ _38_ _39_ _97__bF$buf2 OAI21X1
XOAI21X1_13 gnd vdd _97__bF$buf1 _36_ _0_<0> _39_ OAI21X1
XNOR2X1_14 vdd N<2> gnd _40_ N<1> NOR2X1
XNAND2X1_4 vdd _41_ gnd N<1> N<2> NAND2X1
XINVX1_21 _41_ _42_ vdd gnd INVX1
XOAI21X1_14 gnd vdd _40_ _42_ _43_ state<0> OAI21X1
XAND2X2_2 vdd gnd _103_ state<3> _44_ AND2X2
XINVX1_22 _117_<1> _45_ vdd gnd INVX1
XNOR2X1_15 vdd _37_ gnd _46_ _45_ NOR2X1
XOAI21X1_15 gnd vdd _44_ _46_ _47_ _97__bF$buf0 OAI21X1
XNAND2X1_5 vdd _0_<1> gnd _43_ _47_ NAND2X1
XNAND2X1_6 vdd _48_ gnd state<3> _103_ NAND2X1
XXOR2X1_1 _49_ vdd _117_<2> _48_ gnd XOR2X1
XINVX1_23 N<3> _50_ vdd gnd INVX1
XNAND2X1_7 vdd _51_ gnd _50_ _41_ NAND2X1
XNAND2X1_8 vdd _52_ gnd N<3> _42_ NAND2X1
XNAND3X1_2 _51_ vdd gnd state<0> _52_ _53_ NAND3X1
XOAI21X1_16 gnd vdd state<0> _49_ _0_<2> _53_ OAI21X1
XOAI21X1_17 gnd vdd N<3> _42_ _54_ N<4> OAI21X1
XINVX1_24 N<4> _55_ vdd gnd INVX1
XNAND3X1_3 _55_ vdd gnd _50_ _41_ _57_ NAND3X1
XNAND2X1_9 vdd _58_ gnd _57_ _54_ NAND2X1
XOR2X2_1 _59_ _117_<2> vdd gnd _117_<3> OR2X2
XOAI21X1_18 gnd vdd _117_<2> _48_ _60_ _117_<3> OAI21X1
XOAI21X1_19 gnd vdd _59_ _48_ _61_ _60_ OAI21X1
XNAND2X1_10 vdd _62_ gnd _97__bF$buf3 _61_ NAND2X1
XOAI21X1_20 gnd vdd _97__bF$buf2 _58_ _0_<3> _62_ OAI21X1
XINVX1_25 N<5> _63_ vdd gnd INVX1
XNOR2X1_16 vdd N<4> gnd _64_ N<3> NOR2X1
XAOI21X1_10 gnd vdd _64_ _41_ _65_ _63_ AOI21X1
XOAI21X1_21 gnd vdd N<5> _57_ _66_ state<0> OAI21X1
XNOR2X1_17 vdd _59_ gnd _67_ _117_<4> NOR2X1
XNAND2X1_11 vdd _68_ gnd _99_ _44_ NAND2X1
XAOI22X1_1 gnd vdd _117_<4> _68_ _69_ _67_ _44_ AOI22X1
XOAI22X1_1 gnd vdd _69_ state<0> _65_ _66_ _0_<4> OAI22X1
XOAI21X1_22 gnd vdd N<5> _57_ _70_ N<6> OAI21X1
XOR2X2_2 _71_ N<6> vdd gnd N<5> OR2X2
XOAI21X1_23 gnd vdd _57_ _71_ _72_ _70_ OAI21X1
XNOR2X1_18 vdd _101_ gnd _73_ _48_ NOR2X1
XINVX1_26 _117_<5> _74_ vdd gnd INVX1
XAOI21X1_11 gnd vdd _67_ _44_ _75_ _74_ AOI21X1
XOAI21X1_24 gnd vdd _73_ _75_ _76_ _97__bF$buf1 OAI21X1
XOAI21X1_25 gnd vdd _97__bF$buf0 _72_ _0_<5> _76_ OAI21X1
XINVX1_27 N<7> _77_ vdd gnd INVX1
XNOR2X1_19 vdd _57_ gnd _78_ _71_ NOR2X1
XNOR2X1_20 vdd _78_ gnd _79_ _77_ NOR2X1
XNOR2X1_21 vdd N<6> gnd _80_ N<5> NOR2X1
XNAND3X1_4 _64_ vdd gnd _41_ _80_ _81_ NAND3X1
XOAI21X1_26 gnd vdd N<7> _81_ _82_ state<0> OAI21X1
XINVX1_28 _117_<6> _83_ vdd gnd INVX1
XAND2X2_3 vdd gnd _99_ _100_ _84_ AND2X2
XNAND3X1_5 _44_ vdd gnd _83_ _84_ _85_ NAND3X1
XOAI21X1_27 gnd vdd _48_ _101_ _86_ _117_<6> OAI21X1
XAND2X2_4 vdd gnd _85_ _86_ _87_ AND2X2
XOAI22X1_2 gnd vdd _87_ state<0> _79_ _82_ _0_<6> OAI22X1
XOAI21X1_28 gnd vdd N<7> _81_ _88_ N<8> OAI21X1
XINVX1_29 N<8> _89_ vdd gnd INVX1
XNAND3X1_6 _89_ vdd gnd _77_ _78_ _90_ NAND3X1
XNAND3X1_7 _88_ vdd gnd state<0> _90_ _91_ NAND3X1
XAOI22X1_2 gnd vdd _117_<7> _85_ _92_ state<3> _105_ AOI22X1
XOAI21X1_29 gnd vdd state<0> _92_ _0_<7> _91_ OAI21X1
XINVX1_30 _118_ _93_ vdd gnd INVX1
XINVX1_31 state<2> _94_ vdd gnd INVX1
XNAND3X1_8 _98__bF$buf3 vdd gnd state<4> _94_ _95_ NAND3X1
XAOI21X1_12 gnd vdd _95_ _93_ _1_ state<0> AOI21X1
XOAI21X1_30 gnd vdd _120_<0> _98__bF$buf2 _96_ _97__bF$buf3 OAI21X1
XAOI21X1_13 gnd vdd _98__bF$buf1 _114_ _3_<1> _96_ AOI21X1
XAND2X2_5 vdd gnd _109_ state<1> _4_ AND2X2
XAND2X2_6 vdd gnd _73_ _102_ _5_ AND2X2
XINVX8_2 vdd gnd reset _56_ INVX8
XBUFX2_11 vdd gnd _117_<0> counter<0> BUFX2
XBUFX2_12 vdd gnd _117_<1> counter<1> BUFX2
XBUFX2_13 vdd gnd _117_<2> counter<2> BUFX2
XBUFX2_14 vdd gnd _117_<3> counter<3> BUFX2
XBUFX2_15 vdd gnd _117_<4> counter<4> BUFX2
XBUFX2_16 vdd gnd _117_<5> counter<5> BUFX2
XBUFX2_17 vdd gnd _117_<6> counter<6> BUFX2
XBUFX2_18 vdd gnd _117_<7> counter<7> BUFX2
XBUFX2_19 vdd gnd _118_ done BUFX2
XBUFX2_20 vdd gnd _119_<0> dp<0> BUFX2
XBUFX2_21 vdd gnd _119_<1> dp<1> BUFX2
XBUFX2_22 vdd gnd _119_<2> dp<2> BUFX2
XBUFX2_23 vdd gnd _119_<3> dp<3> BUFX2
XBUFX2_24 vdd gnd _119_<4> dp<4> BUFX2
XBUFX2_25 vdd gnd _119_<5> dp<5> BUFX2
XBUFX2_26 vdd gnd _119_<6> dp<6> BUFX2
XBUFX2_27 vdd gnd _119_<7> dp<7> BUFX2
XBUFX2_28 vdd gnd _119_<8> dp<8> BUFX2
XBUFX2_29 vdd gnd _120_<0> sr<0> BUFX2
XBUFX2_30 vdd gnd _120_<1> sr<1> BUFX2
XBUFX2_31 vdd gnd _120_<2> sr<2> BUFX2
XBUFX2_32 vdd gnd _120_<3> sr<3> BUFX2
XBUFX2_33 vdd gnd _120_<4> sr<4> BUFX2
XBUFX2_34 vdd gnd _120_<5> sr<5> BUFX2
XBUFX2_35 vdd gnd _120_<6> sr<6> BUFX2
XBUFX2_36 vdd gnd _120_<7> sr<7> BUFX2
XDFFSR_1 gnd vdd _4_ _56__bF$buf4 vdd state<0> clock_bF$buf4 DFFSR
XDFFSR_2 gnd vdd _7_ vdd _56__bF$buf3 state<1> clock_bF$buf3 DFFSR
XDFFSR_3 gnd vdd _5_ vdd _56__bF$buf2 state<2> clock_bF$buf2 DFFSR
XDFFSR_4 gnd vdd _6_ vdd _56__bF$buf1 state<3> clock_bF$buf1 DFFSR
XDFFSR_5 gnd vdd state<2> vdd _56__bF$buf0 state<4> clock_bF$buf0 DFFSR
XDFFSR_6 gnd vdd _2_<0> vdd _56__bF$buf4 _119_<0> clock_bF$buf4 DFFSR
XDFFSR_7 gnd vdd _2_<1> vdd _56__bF$buf3 _119_<1> clock_bF$buf3 DFFSR
XDFFSR_8 gnd vdd _2_<2> vdd _56__bF$buf2 _119_<2> clock_bF$buf2 DFFSR
XDFFSR_9 gnd vdd _2_<3> vdd _56__bF$buf1 _119_<3> clock_bF$buf1 DFFSR
XDFFSR_10 gnd vdd _2_<4> vdd _56__bF$buf0 _119_<4> clock_bF$buf0 DFFSR
XDFFSR_11 gnd vdd _2_<5> vdd _56__bF$buf4 _119_<5> clock_bF$buf4 DFFSR
XDFFSR_12 gnd vdd _2_<6> vdd _56__bF$buf3 _119_<6> clock_bF$buf3 DFFSR
XDFFSR_13 gnd vdd _2_<7> vdd _56__bF$buf2 _119_<7> clock_bF$buf2 DFFSR
XDFFSR_14 gnd vdd _2_<8> vdd _56__bF$buf1 _119_<8> clock_bF$buf1 DFFSR
XDFFSR_15 gnd vdd _1_ vdd _56__bF$buf0 _118_ clock_bF$buf0 DFFSR
XDFFSR_16 gnd vdd _0_<0> vdd _56__bF$buf4 _117_<0> clock_bF$buf4 DFFSR
XDFFSR_17 gnd vdd _0_<1> vdd _56__bF$buf3 _117_<1> clock_bF$buf3 DFFSR
XDFFSR_18 gnd vdd _0_<2> vdd _56__bF$buf2 _117_<2> clock_bF$buf2 DFFSR
XDFFSR_19 gnd vdd _0_<3> vdd _56__bF$buf1 _117_<3> clock_bF$buf1 DFFSR
XDFFSR_20 gnd vdd _0_<4> vdd _56__bF$buf0 _117_<4> clock_bF$buf0 DFFSR
XDFFSR_21 gnd vdd _0_<5> vdd _56__bF$buf4 _117_<5> clock_bF$buf4 DFFSR
XDFFSR_22 gnd vdd _0_<6> vdd _56__bF$buf3 _117_<6> clock_bF$buf3 DFFSR
XDFFSR_23 gnd vdd _0_<7> vdd _56__bF$buf2 _117_<7> clock_bF$buf2 DFFSR
XDFFSR_24 gnd vdd _3_<0> vdd _56__bF$buf1 _120_<0> clock_bF$buf1 DFFSR
XDFFSR_25 gnd vdd _3_<1> vdd _56__bF$buf0 _120_<1> clock_bF$buf0 DFFSR
XDFFSR_26 gnd vdd _3_<2> vdd _56__bF$buf4 _120_<2> clock_bF$buf4 DFFSR
XDFFSR_27 gnd vdd _3_<3> vdd _56__bF$buf3 _120_<3> clock_bF$buf3 DFFSR
XDFFSR_28 gnd vdd _3_<4> vdd _56__bF$buf2 _120_<4> clock_bF$buf2 DFFSR
XDFFSR_29 gnd vdd _3_<5> vdd _56__bF$buf1 _120_<5> clock_bF$buf1 DFFSR
XDFFSR_30 gnd vdd _3_<6> vdd _56__bF$buf0 _120_<6> clock_bF$buf0 DFFSR
XDFFSR_31 gnd vdd _3_<7> vdd _56__bF$buf4 _120_<7> clock_bF$buf4 DFFSR
XDFFSR_32 gnd vdd start vdd _56__bF$buf3 startbuf<0> clock_bF$buf3 DFFSR
XDFFSR_33 gnd vdd startbuf<0> vdd _56__bF$buf2 startbuf<1> clock_bF$buf2 DFFSR
.ends map9v3
 
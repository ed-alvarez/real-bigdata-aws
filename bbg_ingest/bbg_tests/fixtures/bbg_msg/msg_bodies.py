body_1 = """ Security        Price      YTW      GSpd    COD
                Bid Ask  Bid  Ask   Bid Ask       Amt Out
--- --- --      -------  ---------  -------  ---  -------
APU 5⅝ 24       90/ 95  8.52/7.03  803/654  -4   675MM
APU 5½ 25       88/ 93  8.40/7.14  787/660  -4   700MM
APU 5⅞ 26       88/ 93  8.32/7.26  767/661  -4   675MM
APU 5¾ 27       88/ 93  7.98/7.01  728/631  -4   525MM



-------------------------------------------------------------------------------
© Copyright 2016 Goldman Sachs. All rights reserved. See www.gs.com/disclaimer/email-salesandtrading.html for risk disclosure, order handling practices, conflicts of interest and other terms and conditions relating to this e-mail and your reliance on it, and www.gs.com/disclaimer/ipo/ for recent prospectuses for initial public offerings to which this message may relate. See www.gs.com/swaps-related-disclosures for important disclosures relating to CFTC-regulated swap transactions, and www.gs.com/FX-disclosures for spot foreign exchange terms of dealing. This e-mail may contain confidential or privileged information. If you are not the intended recipient, please advise us immediately and delete it. See www.gs.com/disclaimer/email/ on confidentiality and the risks of electronic communication. If you cannot access these links, please notify us by reply message and we will send the contents to you. This material is a solicitation of derivatives business generally, only for the purposes of, and to the extent it would otherwise be subject to, CFTC Regulations 1.71 and 23.605."""

body_2 = """

Security
B Px
A Px
B YTC
A YTC
B Spd
A Spd
Moody
S&amp;P	B
Sz(M)		ASz
(M)
B Axe
A Axe
Notes
BCULC 4¼ 24	97	-	98	5.06	/	4.79	454	/	427	Ba2	BB+		x	3000		/	Y
BCULC 5   25	95	-	96	6.07	/	5.85	555	/	533	B2	B+		x	2000		/	Y
BCULC 3⅞ 28	94¾	-	95¾	4.68	/	4.53	391	/	375	Ba2	BB+		x	3000		/	Y
BCULC 4⅜ 28	93½	-	94½	5.40	/	5.24	463	/	446	B2	B+		x	3000		/	Y	SLR




"""

body_3 = """

Security
Nxt Call
BSp
ASp
BPx
APx
Chg
BZs
AZs
AYTC
S&amp;P
ABANCA 6⅛   29	01/18/24	862	/	798	94.000	-	96.000	-3.000	833	/	769	7.35	NR
ABANCA 4⅝   30	04/07/25	813	/	760	88.000	-	90.000	-3.000	785	/	732	7.04	NR
AIB    4⅛   25	11/26/20	947	/	641	97.000	-	99.000	-2.000	914	/	602	5.56	BB+
AIB    Float 35		0	/	0	55.000	-	60.000	-5.000	479	/	420	4.21	NR
ALPHA  4¼   30	02/13/25	0	/	0	60.000	-	70.000	-5.000	1715	/	1315	12.86	CCC
BACRED 5     20		2280	/	1910	90.000	-	92.000	-2.000	2306	/	1913	18.25	BB+
BACRED Float 21		1396	/	908	91.000	-	96.000	-2.000	1273	/	827	8.22	BB+
BACRED 5¾   23		663	/	487	100.000	-	105.000	-2.000	612	/	437	3.99	BB+
BAMIIM 6     20		2060	/	1165	92.000	-	97.000	-2.000	2089	/	1145	10.82	NR
BAMIIM 7⅛   21		1774	/	1149	92.000	-	97.000	-2.000	1728	/	1099	10.55	NR
BAMIIM 6⅜   21		1597	/	1096	91.000	-	96.000	-3.000	1544	/	1043	10.02	NR
BAMIIM 4⅜   27	09/21/22	1173	/	918	86.000	-	91.000	-3.000	1143	/	888	8.48	NR
BAMIIM 4¼   29	10/01/24	0	/	0	86.000	-	91.000	-3.000	835	/	690	6.60	NR
BBVASM 3½   24		0	/	0	100.000	-	100.100	 0.000	0	/	0	0.00	BBB
BBVASM 3½   27		410	/	370	100.701	-	103.173	    50	359	/	319	2.98	BBB
BBVASM 2.575 29	02/22/24	450	/	430	95.992	-	96.696	    70	402	/	382	3.49	BBB
BBVASM 1     30	01/16/25	460	/	440	87.713	-	88.518	    65	412	/	392	3.63	BBB
BCPPL  4½   27	12/07/22	1037	/	944	88.000	-	90.000	-4.000	1010	/	916	8.77	B
BCPPL  3.871 30	03/27/25	733	/	681	88.000	-	90.000	-3.000	705	/	653	6.25	B
BKIASM 9     26	11/16/21	523	/	405	107.000	-	109.000	-4.888	493	/	374	3.33	NR
BKIASM 3⅜   27	03/15/22	410	/	390	100.398	-	100.780	    40	358	/	338	2.97	BB+
BKIASM 3¾   29	02/15/24	480	/	450	99.202	-	100.272	    40	431	/	401	3.67	BB+
BKIR   10    20		0	/	0	97.000	-	102.000	-3.000	0	/	0	0.00	NR
BKIR   10    22		502	/	365	115.000	-	119.000	-6.304	450	/	312	2.73	BB+
BKIR   2⅜   29	10/14/24	410	/	390	96.088	-	96.908	    35	361	/	341	3.11	BB
BKTSM  2½   27	04/06/22	350	/	300	99.004	-	100.795	    60	280	/	251	2.10	BBB-
BNSELL 5½   27	09/22/22	1037	/	798	91.000	-	96.000	-4.000	1007	/	767	7.28	NR
BNSELL 5¼   29	07/23/24	0	/	0	89.000	-	94.000	-3.000	867	/	720	6.88	NR
BOCYCY 9¼   27	01/19/22	2912	/	2453	75.000	-	80.000	-10.000	2881	/	2423	23.82	NR
BPEIM  5⅛   27	05/31/22	836	/	758	95.000	-	96.500	-3.000	807	/	728	6.88	NR
BPOPAA 5⅝   27	10/06/22	1196	/	1045	88.000	-	91.000	-4.000	1165	/	1014	9.75	NR
BPSOIM 6¼   29	07/30/24	924	/	839	86.000	-	91.000	-5.000	883	/	798	8.80	NR
CABKSM 4     22		0	/	0	107.000	-	108.000	 0.000	0	/	0	0.00	NR
CABKSM 5     23		0	/	0	99.750	-	100.000	 0.000	0	/	0	0.00	NR
CABKSM 3½   27	02/15/22	400	/	380	100.791	-	101.161	    50	348	/	328	2.87	BBB-
CABKSM 2¾   28	07/14/23	450	/	430	97.316	-	97.924	    50	398	/	378	3.42	BBB-
CABKSM 2¼   30	04/17/25	500	/	480	91.046	-	91.898	    50	452	/	432	4.05	BBB-
CAJAMA 9     26	11/03/21	3114	/	2132	75.000	-	85.000	-13.000	3084	/	2102	20.60	NR
CAJAMA 7¾   27	06/07/22	2402	/	1697	75.000	-	85.000	-11.000	2372	/	1667	16.27	NR
CAZAR  5     25	07/28/20	1710	/	848	96.000	-	99.000	-1.000	1746	/	818	7.61	B+
CAZAR  2¾   30	07/23/25	0	/	0	87.000	-	92.000	-1.000	590	/	473	4.47	B+
CRDEM  3⅝   27	07/10/22	587	/	535	92.000	-	95.000	-3.000	517	/	465	5.99	NR
CVALIM 4½   18		0	/	0	93.750	-	98.750	 0.000	0	/	0	0.00	NR
CVALIM 3¾   18		0	/	0	93.750	-	98.750	 0.000	0	/	0	0.00	NR
CVALIM 3¾   18		0	/	0	97.750	-	102.750	 0.000	0	/	0	0.00	NR
CVALIM 1.7   19		0	/	0	96.750	-	98.750	 0.000	0	/	0	0.00	NR
CVALIM 1.8   19		0	/	0	96.750	-	98.750	 0.000	0	/	0	0.00	NR
CVALIM 1.7   19		0	/	0	96.250	-	98.250	 0.000	0	/	0	0.00	NR
CVALIM 2.2   19		0	/	0	97.500	-	99.500	 0.000	0	/	0	0.00	NR
CVALIM 1½   19		0	/	0	96.500	-	98.500	 0.000	0	/	0	0.00	NR
CVALIM 4.7   21		3654	/	2399	70.000	-	80.000	-8.000	3608	/	2354	23.13	NR
CVALIM 8¼   27	04/12/22	2339	/	1614	78.000	-	88.000	-6.000	2309	/	1584	15.44	NR
CXGD   5¾   28	06/28/23	0	/	0	97.000	-	100.000	-2.000	630	/	583	5.74	NR
ETEGA  8¼   29	07/18/24	0	/	0	76.000	-	86.000	-10.000	1668	/	1292	12.60	CCC
FARMIT 5⅞   27	03/02/22	2409	/	1624	75.000	-	85.000	-8.000	2357	/	1572	15.31	NR
ICCREA 4⅛   29	11/28/24	1202	/	1101	75.000	-	78.000	-4.000	1155	/	1054	10.25	NR
IFIM   4½   27	10/17/22	1672	/	1383	77.000	-	82.000	-3.000	1641	/	1352	13.13	NR
ISPIM  5.15  20		1826	/	1191	96.000	-	98.000	-2.000	1888	/	1190	11.09	BB+
ISPIM  Float 22		0	/	0	100.900	-	102.900	 0.000	198	/	110	0.70	NR
ISPIM  6⅝   23		525	/	475	107.123	-	108.807	    50	473	/	423	3.87	BB+
ISPIM  Float 24		410	/	360	93.016	-	95.010	    45	357	/	308	2.81	NR
ISPIM  2.855 25		500	/	450	93.741	-	95.933	    45	452	/	402	3.75	BB+
ISPIM  3.928 26		570	/	520	94.442	-	97.117	    45	517	/	467	4.45	BB+
LBKSM  6⅞   27	03/14/22	813	/	595	99.000	-	103.000	-2.000	784	/	566	5.25	NR
MONTE  5⅜   28	01/18/23	4258	/	3226	45.000	-	55.000	-12.000	4230	/	3199	31.60	NR
MONTE  10½  29		1826	/	1555	68.000	-	78.000	-12.000	1788	/	1517	14.99	NR
MONTE  8     30	01/22/25	2553	/	2042	55.000	-	65.000	-13.000	2526	/	2016	19.86	NR
SABSM  6¼   20		2415	/	592	98.000	-	100.000	-1.250	2666	/	641	5.92	BB+
SABSM  5⅝   26		759	/	696	94.000	-	97.000	-6.000	709	/	647	6.22	BB+
SABSM  5⅜   28	12/12/23	888	/	788	91.000	-	94.000	-6.000	861	/	760	7.25	BB+
SABSM  2     30	01/17/25	729	/	592	81.000	-	86.000	-3.000	702	/	565	5.36	BB+
SANTAN 2½   25		370	/	350	97.959	-	98.870	    35	322	/	302	2.75	BBB+
SANTAN 3¼   26		375	/	355	101.274	-	102.380	    30	325	/	305	2.82	BBB+
SANTAN 3⅛   27		395	/	375	99.337	-	100.551	    40	345	/	325	3.03	BBB+
SANTAN 2⅛   28		393	/	373	91.915	-	93.229	    40	348	/	328	3.11	BBB+
TPEIR  9¾   29	06/26/24	0	/	0	68.000	-	78.000	-7.000	2229	/	1773	17.41	CCC
TPEIR  5½   30	02/19/25	0	/	0	42.000	-	52.000	-5.000	2932	/	2291	22.62	CCC
UBIIM  4¼   26	05/05/21	1095	/	892	94.000	-	96.000	-3.000	1051	/	848	8.07	BB
UBIIM  4.45  27	09/15/22	1050	/	950	89.000	-	91.000	-3.000	999	/	898	8.59	BB
UBIIM  5⅞   29	03/04/24	0	/	0	94.000	-	96.000	-3.000	802	/	740	7.07	BB
UBIIM  4⅜   29	07/12/24	825	/	766	89.000	-	91.000	-3.000	775	/	716	6.84	BB
UCAJLN 2⅞   29	11/13/24	0	/	0	89.500	-	92.500	-1.500	578	/	500	4.70	NR
UCGIM  6⅛   21		513	/	329	102.000	-	104.000	 0.000	460	/	276	2.35	BB+
UCGIM  6.95  22		380	/	355	110.083	-	110.755	    25	328	/	303	2.64	BB+
UCGIM  Float 25	05/03/20	3211	/	1528	96.500	-	98.500	-1.000	3173	/	1482	14.53	NR
UCGIM  5¾   25	10/28/20	982	/	481	98.000	-	101.000	-2.000	957	/	444	3.99	BB+
UCGIM  4⅜   27	01/03/22	600	/	500	98.678	-	100.360	   125	557	/	457	4.15	BB+
UCGIM  4⅞   29	02/20/24	635	/	620	97.708	-	98.219	    40	587	/	572	5.39	BB+
UCGIM  2     29	09/23/24	640	/	620	85.842	-	86.553	    45	594	/	574	5.43	BB+
UCGIM  2.731 32	01/15/27	635	/	615	83.817	-	84.818	    40	586	/	566	5.45	BB+




"""

body_4 = """Hello everyone,

ECB said it will focus on corporates in the QE expansion. Our forecasts
ECB&apos;s Corporate Focus May Mean 100 Billion Euros of 2020 Buying


Italian corporates beating European peers and BTP, while Italy banks underperform.
Banks Dive, But Most Italian Corporates Thrive Despite Covid-19


Credit Fundamentals Deteriorating Even Before Virus
A Blow for Euro Credit Fundamentals, But Oil Drag Less Crippling
Europe Significantly Less-Exposed Than U.S. to Oil Credit Risk


ECB QE and corporate buying forecast...detailed report
ECB May Buy 8 Billion Euros In March CSPP, Excluding QE Increase
CSPP-Eligible Bonds Beating Rest of Credit on Virus Impact


If the bear market continues, we expect credit to beat equities in a roll month.
Panic Alternative? Credit Beats Equity as Covid-19 Spreads Fear
In Roll Month, Main Tightens in Bull or Bear Stock Markets


Update on Global Pension Liability hit due to the AA yield moves (widely used discount rates)
After $4 Trillion AA Yield Hit, Virus May Soften Pensions Blow


Crossover is at record wide to Main and senior fins are close to series 32 tights to Main
Crossover at Record Wide, Senior Financials Look Tight vs. Main


A history of credit and viruses. Good lessons to be drawn from there for now.
Weaker Immunity? Less Cushion, Momentum for Credit as Virus Hits


Thanks in advance
.bbScopedStyle7021963759470085 .bbScopedStyle868396516521041 .bbScopedStyle2606250418267566 .bbScopedStyle6015044852908307 .bbScopedStyle7608910484800497 .bbScopedStyle4604241617699039 .bbScopedStyle1825274357183883 .bbScopedStyle726132948711244 .bbScopedStyle2600115992158702 .bbScopedStyle7957698237504218 .bbScopedStyle5381156900021618 .bbScopedStyle8766089964585213 .bbScopedStyle9979080545429318 .bbScopedStyle8228003789718026 .bbScopedStyle3292040650764078 .bbScopedStyle5937835008160646 .bbScopedStyle9150300838494536 .bbScopedStyle2244629897415229 .bbScopedStyle7603460970985518 .bbScopedStyle2322775657928932 .bbScopedStyle4994164456230374 .bbScopedStyle3071707819977427 .bbScopedStyle5944614929220937 .bbScopedStyle8166438858998382 .bbScopedStyle3531782104975574 .bbScopedStyle3685037274967428 .bbScopedStyle9676228974703136 .bbScopedStyle1933394819934737 .bbScopedStyle2892592516259240 .bbScopedStyle9358082910602878 .bbScopedStyle2772804875356880 .bbScopedStyle890492939415164 .bbScopedStyle7475959155072243 .bbScopedStyle5790626132397256 .bbScopedStyle390060992367 .bbScopedStyle2339834120739179 .bbScopedStyle4330589966923015 .bbScopedStyle5765993549402160 .bbScopedStyle1593705907757510 .bbScopedStyle3367671341476570 .bbScopedStyle4974817816593029 .bbScopedStyle6732836308420385 .bbScopedStyle5084473281186328 .bbScopedStyle1321022435466690 .bbScopedStyle2128403398383262 .bbScopedStyle5778390057814482 .bbScopedStyle5734168862269196 .bbScopedStyle6460849976568124 .bbScopedStyle6615319781784090 .bbScopedStyle9777423106893928 .bbScopedStyle6435549618742746 .bbScopedStyle4728761845197038 .bbScopedStyle8348748188934423 .bbScopedStyle7970429768515213 .bbScopedStyle5413673186337116 .bbScopedStyle9442660913207390 .bbScopedStyle9874171165799300 .bbScopedStyle7328871603957383 .bbScopedStyle954017069102617 .bbScopedStyle7527061773402739 .bbScopedStyle4723220564173374 .bbScopedStyle7953096835400484 .bbScopedStyle1571025442324984 .bbScopedStyle6841239600020459 .bbScopedStyle6469123655126678 .bbScopedStyle7380966628893673 .bbScopedStyle5311524509899979 .bbScopedStyle8508354328550791 .bbScopedStyle4927616470124156 .bbScopedStyle6710284038888981 .bbScopedStyle8826261332075196 .bbScopedStyle1531051416894810 .bbScopedStyle6478390432978434 .bbScopedStyle7471697782284705 .bbScopedStyle5060676540083928 .bbScopedStyle3592683928557789 .bbScopedStyle1052288587077892 .bbScopedStyle7309030658586089 .bbScopedStyle6249071758964460 .bbScopedStyle4998758435574195 .bbScopedStyle120363657213236 .bbScopedStyle6549049002128855 .bbScopedStyle4672221351139849 .bbScopedStyle6235897759265998 .bbScopedStyle5875485343340983 .bbScopedStyle9835542156506314 .bbScopedStyle462162670537766 .bbScopedStyle7995720120882146 .bbScopedStyle8367056821477104 .bbScopedStyle1122161170098907 .bbScopedStyle1721391903633473 .bbScopedStyle5904930619388442 .bbScopedStyle2214693983144202 .bbScopedStyle2537202764064927 .bbScopedStyle3291426165946669 .bbScopedStyle1814436931336123 .bbScopedStyle7754607085295087 .bbScopedStyle4832199345682628 .bbScopedStyle4874163110915604 .bbScopedStyle199207739513556 .bbScopedStyle2893499168473470 .bbScopedStyle3368902867938570 .bbScopedStyle1431253609829099 .bbScopedStyle7088764560484240 .bbScopedStyle1325043001954435 .bbScopedStyle7692409355390046 .bbScopedStyle231404249722990 .bbScopedStyle597855022263802 .bbScopedStyle9279528465735352 .bbScopedStyle3094306233800636 .bbScopedStyle7235346882664577 .bbScopedStyle1636474690269318 .bbScopedStyle6010485435173241 .bbScopedStyle13375375330026 .bbScopedStyle4587368906110763 .bbScopedStyle608533158089386 .bbScopedStyle8085948583903757 .bbScopedStyle6177900174001112 .bbScopedStyle7081152300826290 .bbScopedStyle594918925569722 .bbScopedStyle1189578374610718 .bbScopedStyle2832273686549058 .bbScopedStyle6386381079301067 .bbScopedStyle6483780023513923 .bbScopedStyle3744308225708512 .bbScopedStyle9686612048863910 .bbScopedStyle6815068583132990 .bbScopedStyle4653737601185504 .bbScopedStyle6511421531992614 .bbScopedStyle3957431341558430 .bbScopedStyle7640154955985712 .bbScopedStyle4893060140947865 .bbScopedStyle6624030826120517 .bbScopedStyle499363847393836 .bbScopedStyle4509794247861116 .bbScopedStyle1062610223277482 .bbScopedStyle2933762051448065 .bbScopedStyle4513521378651664 .bbScopedStyle6749341940466069 .bbScopedStyle6718293856487076 .bbScopedStyle43470649261909 .bbScopedStyle4939208771632964 .bbScopedStyle1808220383952192 .bbScopedStyle8978331962814892 .bbScopedStyle6829027662535911 .bbScopedStyle8773420589610816 .bbScopedStyle9486610899315592 .bbScopedStyle3511411468854763 .bbScopedStyle6720751880917730 .bbScopedStyle5370681231115559 .bbScopedStyle9787684430914176 .bbScopedStyle2771436264001756 .bbScopedStyle4181561208450348 .bbScopedStyle5634440075229918 .bbScopedStyle4050662973105874 .bbScopedStyle4517560693397695 .bbScopedStyle3709645338275984 .bbScopedStyle5296175611852827 .bbScopedStyle8833384293318964 .bbScopedStyle1001156714790931 .bbScopedStyle3715004758603131 .bbScopedStyle4512662384210073 .bbScopedStyle1397049407528008 .bbScopedStyle2511531120460366 .bbScopedStyle2193231413864560 .bbScopedStyle2192272875188867 .bbScopedStyle4866206127833188 .bbScopedStyle2850215946609906 .bbScopedStyle5010832119899844 .bbScopedStyle6422427001750288 .bbScopedStyle5039952615484899 .bbScopedStyle8795735178887940 .bbScopedStyle5781286455516821 .bbScopedStyle8160885934155202 .bbScopedStyle3854170703995605 .bbScopedStyle969871938893316 .bbScopedStyle2185429230409572 .bbScopedStyle1274296838166169 .bbScopedStyle2737654259292523 .bbScopedStyle1337604931128493 .bbScopedStyle1401304179559903 .bbScopedStyle638004791738202 .bbScopedStyle1662780745488357 .bbScopedStyle8700790405097039 .bbScopedStyle4670161871893368 .bbScopedStyle7250150606697796 .bbScopedStyle7532355787101850 .bbScopedStyle9255890381059148 .bbScopedStyle4534038771783668 .bbScopedStyle2309362305623461 .bbScopedStyle4952938864752665 .bbScopedStyle160786364431468 .bbScopedStyle4248642688000168 .bbScopedStyle8739035652243321 .bbScopedStyle904022644006639 .bbScopedStyle7034601507149691 .bbScopedStyle3412209101979704 .bbScopedStyle4362572725224065 .bbScopedStyle7371832117105965 .bbScopedStyle1740292019678833 .bbScopedStyle5290126393000396 .bbScopedStyle4000345837677650 .bbScopedStyle4368200709808538 .bbScopedStyle9246077320592610 .bbScopedStyle4473909859199019 .bbScopedStyle8906249527683125 .bbScopedStyle2746035902889467 .bbScopedStyle647669719668988 .bbScopedStyle162253868540238 .bbScopedStyle5478615316307465 .bbScopedStyle4921951191275165 .bbScopedStyle4950128716759759 .bbScopedStyle7938792694669232 .bbScopedStyle7324816327465609 .bbScopedStyle2851663737126213 .bbScopedStyle7324789436066836 .bbScopedStyle1045474101465799 .bbScopedStyle5406281645218376 .bbScopedStyle8935255268223026 .bbScopedStyle4385601894501760 .bbScopedStyle7051680235301994 .bbScopedStyle1870049965206346 .bbScopedStyle120975002633447 .bbScopedStyle4647370825836898 .bbScopedStyle7298065108646066 .bbScopedStyle4181967430169004 .bbScopedStyle2070407995492971 .bbScopedStyle7775323477012943  .rte-style-msg-personal-disclaimer      a[data-destination] {color: #67d8e5 !important; }
Mahesh Bhimalingam,Chief European Credit Strategist,Bloomberg Intelligence,London EC4N 4TQ.Ph: +44 20 3525 4627


































































































































.bbScopedStyle7021963759470085 .bbScopedStyle868396516521041 .bbScopedStyle2606250418267566 .bbScopedStyle6015044852908307 .bbScopedStyle7608910484800497 .bbScopedStyle4604241617699039 .bbScopedStyle1825274357183883 .bbScopedStyle726132948711244 .bbScopedStyle2600115992158702 .bbScopedStyle7957698237504218 .bbScopedStyle5381156900021618 .bbScopedStyle8766089964585213 .bbScopedStyle9979080545429318 .bbScopedStyle8228003789718026 .bbScopedStyle3292040650764078 .bbScopedStyle5937835008160646 .bbScopedStyle9150300838494536 .bbScopedStyle2244629897415229 .bbScopedStyle7603460970985518 .bbScopedStyle2322775657928932 .bbScopedStyle4994164456230374 .bbScopedStyle3071707819977427 .bbScopedStyle5944614929220937 .bbScopedStyle8166438858998382 .bbScopedStyle3531782104975574 .bbScopedStyle3685037274967428 .bbScopedStyle9676228974703136 .bbScopedStyle1933394819934737 .bbScopedStyle2892592516259240 .bbScopedStyle9358082910602878 .bbScopedStyle2772804875356880 .bbScopedStyle890492939415164 .bbScopedStyle7475959155072243 .bbScopedStyle5790626132397256 .bbScopedStyle390060992367 .bbScopedStyle2339834120739179 .bbScopedStyle4330589966923015 .bbScopedStyle5765993549402160 .bbScopedStyle1593705907757510 .bbScopedStyle3367671341476570 .bbScopedStyle4974817816593029 .bbScopedStyle6732836308420385 .bbScopedStyle5084473281186328 .bbScopedStyle1321022435466690 .bbScopedStyle2128403398383262 .bbScopedStyle5778390057814482 .bbScopedStyle5734168862269196 .bbScopedStyle6460849976568124 .bbScopedStyle6615319781784090 .bbScopedStyle9777423106893928 .bbScopedStyle6435549618742746 .bbScopedStyle4728761845197038 .bbScopedStyle8348748188934423 .bbScopedStyle7970429768515213 .bbScopedStyle5413673186337116 .bbScopedStyle9442660913207390 .bbScopedStyle9874171165799300 .bbScopedStyle7328871603957383 .bbScopedStyle954017069102617 .bbScopedStyle7527061773402739 .bbScopedStyle4723220564173374 .bbScopedStyle7953096835400484 .bbScopedStyle1571025442324984 .bbScopedStyle6841239600020459 .bbScopedStyle6469123655126678 .bbScopedStyle7380966628893673 .bbScopedStyle5311524509899979 .bbScopedStyle8508354328550791 .bbScopedStyle4927616470124156 .bbScopedStyle6710284038888981 .bbScopedStyle8826261332075196 .bbScopedStyle1531051416894810 .bbScopedStyle6478390432978434 .bbScopedStyle7471697782284705 .bbScopedStyle5060676540083928 .bbScopedStyle3592683928557789 .bbScopedStyle1052288587077892 .bbScopedStyle7309030658586089 .bbScopedStyle6249071758964460 .bbScopedStyle4998758435574195 .bbScopedStyle120363657213236 .bbScopedStyle6549049002128855 .bbScopedStyle4672221351139849 .bbScopedStyle6235897759265998 .bbScopedStyle5875485343340983 .bbScopedStyle9835542156506314 .bbScopedStyle462162670537766 .bbScopedStyle7995720120882146 .bbScopedStyle8367056821477104 .bbScopedStyle1122161170098907 .bbScopedStyle1721391903633473 .bbScopedStyle5904930619388442 .bbScopedStyle2214693983144202 .bbScopedStyle2537202764064927 .bbScopedStyle3291426165946669 .bbScopedStyle1814436931336123 .bbScopedStyle7754607085295087 .bbScopedStyle4832199345682628 .bbScopedStyle4874163110915604 .bbScopedStyle199207739513556 .bbScopedStyle2893499168473470 .bbScopedStyle3368902867938570 .bbScopedStyle1431253609829099 .bbScopedStyle7088764560484240 .bbScopedStyle1325043001954435 .bbScopedStyle7692409355390046 .bbScopedStyle231404249722990 .bbScopedStyle597855022263802 .bbScopedStyle9279528465735352 .bbScopedStyle3094306233800636 .bbScopedStyle7235346882664577 .bbScopedStyle1636474690269318 .bbScopedStyle6010485435173241 .bbScopedStyle13375375330026 .bbScopedStyle4587368906110763 .bbScopedStyle608533158089386 .bbScopedStyle8085948583903757 .bbScopedStyle6177900174001112 .bbScopedStyle7081152300826290 .bbScopedStyle594918925569722 .bbScopedStyle1189578374610718 .bbScopedStyle2832273686549058 .bbScopedStyle6386381079301067 .bbScopedStyle6483780023513923 .bbScopedStyle3744308225708512 .bbScopedStyle9686612048863910 .bbScopedStyle6815068583132990 .bbScopedStyle4653737601185504 .bbScopedStyle6511421531992614 .bbScopedStyle3957431341558430 .bbScopedStyle7640154955985712 .bbScopedStyle4893060140947865 .bbScopedStyle6624030826120517 .bbScopedStyle499363847393836 .bbScopedStyle4509794247861116 .bbScopedStyle1062610223277482 .bbScopedStyle2933762051448065 .bbScopedStyle4513521378651664 .bbScopedStyle6749341940466069 .bbScopedStyle6718293856487076 .bbScopedStyle43470649261909 .bbScopedStyle4939208771632964 .bbScopedStyle1808220383952192 .bbScopedStyle8978331962814892 .bbScopedStyle6829027662535911 .bbScopedStyle8773420589610816 .bbScopedStyle9486610899315592 .bbScopedStyle3511411468854763 .bbScopedStyle6720751880917730 .bbScopedStyle5370681231115559 .bbScopedStyle9787684430914176 .bbScopedStyle2771436264001756 .bbScopedStyle4181561208450348 .bbScopedStyle5634440075229918 .bbScopedStyle4050662973105874 .bbScopedStyle4517560693397695 .bbScopedStyle3709645338275984 .bbScopedStyle5296175611852827 .bbScopedStyle8833384293318964 .bbScopedStyle1001156714790931 .bbScopedStyle3715004758603131 .bbScopedStyle4512662384210073 .bbScopedStyle1397049407528008 .bbScopedStyle2511531120460366 .bbScopedStyle2193231413864560 .bbScopedStyle2192272875188867 .bbScopedStyle4866206127833188 .bbScopedStyle2850215946609906 .bbScopedStyle5010832119899844 .bbScopedStyle6422427001750288 .bbScopedStyle5039952615484899 .bbScopedStyle8795735178887940 .bbScopedStyle5781286455516821 .bbScopedStyle8160885934155202 .bbScopedStyle3854170703995605 .bbScopedStyle969871938893316 .bbScopedStyle2185429230409572 .bbScopedStyle1274296838166169 .bbScopedStyle2737654259292523 .bbScopedStyle1337604931128493 .bbScopedStyle1401304179559903 .bbScopedStyle638004791738202 .bbScopedStyle1662780745488357 .bbScopedStyle8700790405097039 .bbScopedStyle4670161871893368 .bbScopedStyle7250150606697796 .bbScopedStyle7532355787101850 .bbScopedStyle9255890381059148 .bbScopedStyle4534038771783668 .bbScopedStyle2309362305623461  .rte-style-msg-personal-disclaimer      a[data-destination] {color: #67d8e5 !important; }









































































































"""

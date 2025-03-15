from pathlib import Path

import pytest
from email_src.email_utils.generate_email_obj import parseMIME

BASE_DIR = Path(__file__).resolve().parent.parent


class TestMIMEObject:
    @pytest.fixture
    def get_mime_file(self):
        def _mime_file(file_id):
            mime_file_to_open = open(f"{BASE_DIR}/email_tests/sample_emails/" + str(file_id), "rb")
            msg = mime_file_to_open.read()
            return msg

        return _mime_file

    CASES = [
        pytest.param(
            "eg_utf8",
            "gdpr@egca.co.uk",
            "Help <elizabeth.cooper@shiftposts.com>",
            "=?UTF-8?B??=",
            id="eg_decode_fail",
        ),
        pytest.param(
            "eg_decode_fail",
            "d.ashurkov@egca.co.uk <d.ashurkov@egca.co.uk>",
            "טאבו ישיר  <newslettertabu@bizportal.co.il>",
            "כנסו לבדוק את הדיירים שאתם מכניסים לבית שלכם – פרסומת",
            id="eg_decode_fail",
        ),
        pytest.param(
            "MIME_with_png",
            "Kelly Austin-Brooks <kaustin-brooks@mayfairequity.com>",
            "Tom Vavrechka <tom@ip-sentinel.com>",
            "RE: Dymo Label Writer 450",
            id="MIME_with_png",
        ),
        pytest.param(
            "aster_japan",
            "Undisclosed recipients:;",
            "Robinson, Nicholas  <nicholas.robinson.2@credit-suisse.com>",
            "** Japanese Prospectus and Prospectus Wrapper & Link to NetRoadshow Presentation ** Kaizen Platform, Inc. (RegS) **",
            id="aster_japan",
        ),
        pytest.param(
            "ayora_disposition",
            "matt.johnson@ayoracapital.com",
            "Smith, Jonathan <jonathan.smith@berenberg.com>",
            "** BERENBERG TELCOS EARLY BIRD (VOD - solid H1, ORA Towers/tax, KPN/EQT, Germany Huawei, LBTY/O2, German FTTH, Freenet feedback, OFCOM) **",
            id="ayora_disposition",
        ),
        pytest.param(
            "ayres_no_bcc",
            "Ian Shepherdson <Ian@pantheonmacro.com>, Claus Vistesen <claus@pantheonmacro.com>",
            "Pantheon Macro - EZ <notes2@pantheonmacro.com>",
            "Pantheon Macro EZ Monitor:  Will the Virus Ruin Christmas in Europe?",
            id="ayres_no_bcc",
        ),
        pytest.param(
            "b64encodedmime",
            "Meraj Sepehrnia <meraj@bradburycap.com>",
            "Angelika Paszek <Angelika.Paszek@LighthousePartners.com>",
            "RE: Meraj  - Monthly Meeting - North Rock Managers",
            id="b64encodedmime",
        ),
        pytest.param(
            "broken_html_1",
            "<tom@ip-sentinel.com>",
            "<domain.admin@mayfairequity.com>",
            "Mimecast Synchronization Engine Alert - Error",
            id="broken_html_1",
        ),
        pytest.param(
            "broken_upload_1",
            "Agis Karzis-Anastasiou <agis@mirabella.uk>",
            "Joe Vittoria <joe@mirabella.uk>",
            "Joe Vittoria has invited you to 'On-boarding Master'",
            id="broken_upload_1",
        ),
        pytest.param(
            "broken_upload_2",
            "Andrew Insley <Andrew.Insley@cordium.com>, Steve Cox<Steve.Cox@cordium.com>, Maya Shah <Maya.Shah@cordium.com>, Kris Folan<Kris.Folan@cordium.com>, Matthew Crisp <Matthew.Crisp@cordium.com>, Joe Vittoria <joe@mirabella.uk>, Philip Naughton <Philip.Naughton@cordium.com>",
            "Mary Dowd <Mary.Dowd@cordium.com>",
            "Mary in office",
            id="broken_upload_2",
        ),
        pytest.param(
            "complex_meeting",
            "James Test Hogbin <james@hogbin.com>, hogbin@hotmail.com<hogbin@hotmail.com>",
            "James Hogbin <james@ip-sentinel.com>",
            "Fingerprint Test Meeting 2",
            id="complex_meeting",
        ),
        pytest.param(
            "hanetf_no_file_in_type",
            "ops@hanetf.com",
            "Equity Operations <equity.ops@solactive.com>",
            "MEDCAWEP_DCAF_2020-11-16.csv",
            id="hanetf_no_file_in_type",
        ),
        pytest.param(
            "hanetf_utf8_emailaddress",
            "<bounce-496565-426-94855-ian.hector=hanetf.com@s1.asa1.acemsb3.com>",
            "<postmaster@hanetf.com>",
            "Undeliverable: Partnership for impact indices: your expertise, our impact data",
            id="hanetf_utf8_emailaddress",
        ),
        pytest.param(
            "hatherleigh_file_part",
            "richard.hockings@hatherleighcap.com",
            "Holt, Stuart <stuart.holt@berenberg.com>",
            "...BERENBERG Breakfast - Nov 16th",
            id="hatherleigh_file_part",
        ),
        pytest.param(
            "html5lib_error",
            "james@ip-sentinel.com",
            "SC Media Industry Buzz <news@news.scmediaglobal.com>",
            "Webinar: How to design a least privilege architecture in AWS",
            id="html5lib_error",
        ),
        pytest.param(
            "ingest_01",
            "zshah@enfusionsystems.com, risk@mirabella.co.uk, luke.macdonald@system2capital.com, max.veneziani@system2capital.com",
            "No Reply <noreply@enfusionsystems.com>",
            "[EXTERNAL] System 2 - Mirabella Equity & Credit Limits Report",
            id="ingest_01",
        ),
        pytest.param(
            "investtao_bad_charset",
            "Shelley Yang <shelley.yang@investao.co.uk>, Mathias Kalmar<Mathias.Kalmar@investao.co.uk>, Hillary Su <Hillary.Su@investao.co.uk>, Devin Ziwen Huang <Devin.Huang@investao.co.uk>",
            "Rex Chongjun Zhu <rex.zhu@investao.co.uk>",
            "Weekly Call Nov 23",
            id="investtao_bad_charset",
        ),
        pytest.param(
            "kirkoswold_attachment_01",
            "'3rd Party Request' <3rdParty.Prime_Brokerage@morganstanley.com>, 'Murdoch, John' <John.Murdoch@morganstanley.com>",
            "Nicholas Hayes <NHayes@mfsadmin.com>",
            "Kirkoswald - Missing  Reports COB 11/13",
            id="kirkoswold_attachment_01",
        ),
        pytest.param(
            "kirkoswold_attachment_2",
            "OPS@KIRKOSWALD.COM <OPS@KIRKOSWALD.COM>, PBMO.NA.FIXED.INCOME.PREMATCHING@JPMORGAN.COM <PBMO.NA.FIXED.INCOME.PREMATCHING@JPMORGAN.COM>",
            "emea.clientsettlements@citi.com",
            "FICSCORE - UNMATCHED CASH TRADES FUTURE VALUE",
            id="kirkoswold_attachment_2",
        ),
        pytest.param(
            "kirkoswold_no_application_error",
            "francois lagrange <francois.lagrange@kirkoswald.com>",
            "Commodity Weather Group <team@commoditywx.com>",
            "CWG Energy Midday Quicksheet: European Operational Loses 14.6 HDDs",
            id="kirkoswold_no_application_error",
        ),
        pytest.param(
            "kirkoswold_turkish",
            "<NHayes@mfsadmin.com>, <ops@kirkoswald.com>, <ldnrepo@barclays.com>, <bob.price@kirkoswald.com>, <kirkoswald.middleoffice@mfsadmin.com>, <Kirkoswald@mfsadmin.com>",
            "<ldnrepo@barclays.com>",
            "RE: Margin Call Notice for Kirkoswald Global Macro Master Fund Limited (GMRA) as of COB 17 Nov 2020",
            id="kirkoswold_turkish",
        ),
        pytest.param(
            "kirkoswold_utf8_header",
            "Undisclosed recipients:;",
            "Ozan Tarman <ozan.tarman@db.com>",
            "Top5: Cheap? / Clarida / Compress / EM CBs / & 50 Redux.....",
            id="kirkoswold_utf8_header",
        ),
        pytest.param(
            "live_attach",
            "Stevan Simic <stevans@mirabella.co.uk>",
            "Tom Vavrechka <tom@ip-sentinel.com>",
            "Re: Group Policies",
            id="live_attach",
        ),
        pytest.param(
            "meeting_invite",
            "James Test Hogbin <james@hogbin.com>",
            "James Hogbin <james@ip-sentinel.com>",
            "Fingerprint Test Meeting",
            id="meeting_invite",
        ),
        pytest.param(
            "melqart_bcc",
            "Undisclosed recipients:;",
            "UFP Research <Research@utdfirst.com>",
            "UFP | Global Weekend Press Digest 15th November",
            id="melqart_bcc",
        ),
        pytest.param(
            "melqart_group",
            "undisclosed-recipients:",
            "News Alert (BLOOMBERG/ 731 LEX G) <nlrt@bloomberg.net>",
            "New York Post: Netflix drops carols on fireplace video, ruins Christmas for " "blogger",
            id="melqart_group",
        ),
        pytest.param(
            "melqart_thread_topic",
            "<michel.massoud@melqart.com>",
            "ABGSC Shipping & Transport Research<ABGSCShippingTransportResearch@abgsc.com>",
            "AP Møller Maersk - Buy: Heads-up for report",
            id="melqart_thread_topic",
        ),
        pytest.param(
            "mirabella_attachment_01",
            "'Richard Barnes' <Richard@vitaluna.co.uk>, 'Alison Passey' <alison@locksmithanimation.com>, 'Urquhart, Paula' <paula_urquhart@hotmail.com>, <apocalypsegoat@hotmail.com>, 'Sarah Donnelly' <sarahd@mirabella.co.uk>",
            "alan webster <alanhwebster@gmail.com>",
            "[EXTERNAL] RE: Quiz",
            id="mirabella_attachment_01",
        ),
        pytest.param(
            "mirabella_concat_str",
            "PublicFolderMailboxes.924dc51ab5c24245a8f60fafa82bdbc1<PublicFolderMailboxes.924dc51ab5c24245a8f60fafa82bdbc1@mirabella.onmicrosoft.com>",
            "Engagement Letters<EngagementLetters_f84a3e12@mirabella.onmicrosoft.com>",
            "HierarchySync_IncrementalSync_242706_26ece4c7-756d-44d2-b7a8-c7a9692d60b6",
            id="mirabella_concat_str",
        ),
        pytest.param(
            "mirabella_group_error",
            "PublicFolderMailboxes.924dc51ab5c24245a8f60fafa82bdbc1<PublicFolderMailboxes.924dc51ab5c24245a8f60fafa82bdbc1@mirabella.onmicrosoft.com>",
            "Engagement Letters<EngagementLetters_f84a3e12@mirabella.onmicrosoft.com>",
            "HierarchySync_Ping_242569_26ece4c7-756d-44d2-b7a8-c7a9692d60b6",
            id="mirabella_group_error",
        ),
        pytest.param(
            "naya_bytes_object",
            "ops@nayafund.com",
            "gsl.amrs.app@bofa.com",
            "2:NAYA_emap_loc_res_20201116.csv",
            id="naya_bytes_object",
        ),
        pytest.param(
            "naya_file",
            "<Sarah@nayafund.com>",
            "Teh, Wen <wen.teh@bofa.com>",
            "BofA EMEA INSIGHT --- BREXIT call tomorrow. EDF 80% upside potential. A&D recovery ahead. BANKINTER double u/g. FRASERS bullish reinstatement. NEW RSCH weekly.",
            id="naya_file",
        ),
        pytest.param(
            "naya_group",
            "<sarah@nayafund.com>",
            "Freshney, Mark  <mark.freshney@credit-suisse.com>",
            "Pennon Group (PNN.L) : Looking to a takeover of Southern Water (Sunday " "Times) which has £ 5.2bn RAB.",
            id="naya_group",
        ),
        pytest.param(
            "naya_multiple_payload",
            "Lindquist, Justin <justin.lindquist@jpmorgan.com>",
            "Lindquist, Justin <justin.lindquist@jpmorgan.com>",
            "IGO's AGM is this Wed- time to buy??",
            id="naya_multiple_payload",
        ),
        pytest.param(
            "naya_utf8_subject",
            "sarah@nayafund.com",
            "Citi Velocity <globalcitivelocityteam@citi.com>",
            "Citi / 外国株セールスメモ: 2021 年末のS&P500 のターゲットプライスを3,800 に",
            id="naya_utf8_subject",
        ),
        pytest.param(
            "owl_rock_body_missing",
            "Amy Ward <amy.ward@owlrock.com>",
            "Linehan, David <David.Linehan@tpifm.com>",
            "Catch-up",
            id="owl_rock_body_missing",
        ),
        pytest.param(
            "pag_no_load",
            "<mcarruth@pagasia.com>",
            "<nicolas.gaudois@ubs.com>",
            "UBS: Memory Semis Monthly \"November '20 Edition: Mobile DRAM pricing first " 'up"',
            id="pag_no_load",
        ),
        pytest.param(
            "rbh_index_out_range",
            "rob.harris@rbhcapital.net <rob.harris@rbhcapital.net>",
            "Adrian Maydew <amaydew@tourmalinellc.com>",
            "GS on MRW",
            id="rbh_index_out_range",
        ),
        pytest.param(
            "reply_chain",
            "James Hogbin <james@ip-sentinel.com>",
            "Tom Vavrechka <tom@ip-sentinel.com>",
            "Fwd: PO-0240   20-67872-11",
            id="reply_chain",
        ),
        pytest.param(
            "sample_MIME",
            "james@ip-sentinel.com",
            "Site Ground <noreply@siteground.com>",
            "Please verify your new login email",
            id="sample_MIME",
        ),
        pytest.param(
            "sample_MIME_HTML_only",
            "james@ip-sentinel.com",
            "Site Ground <noreply@siteground.com>",
            "Please verify your new login email",
            id="sample_MIME_HTML_only",
        ),
        pytest.param(
            "sample_MIME_plain_only",
            "james@ip-sentinel.com",
            "Site Ground <noreply@siteground.com>",
            "Please verify your new login email",
            id="sample_MIME_plain_only",
        ),
        pytest.param(
            "single_word_body",
            "James Hogbin <james@hogbin.com>",
            "James Hogbin <james@ip-sentinel.com>",
            "test",
            id="single_word_body",
        ),
        pytest.param(
            "single_word_body_1",
            "James Hogbin <james@hogbin.com>",
            "James Hogbin <james@ip-sentinel.com>",
            "Fred 1",
            id="single_word_body_1",
        ),
        pytest.param(
            "svelland_ascii",
            "Undisclosed recipients:;",
            "Kemanes, Harry <harry.kemanes@ubs.com>",
            "UBS Capital Introduction | Monthly Update - October 2020",
            id="svelland_ascii",
        ),
        pytest.param(
            "svelland_content_type",
            "tim@svelland.com",
            "Wealth Manager Afternoon <noreply@listserve.citywire.co.uk>",
            "Revealed: The £470m investors paid for ‘poor value’ funds",
            id="svelland_content_type",
        ),
        pytest.param(
            "system2_fail_1",
            "sean@system2capital.com",
            "Mike Prew <mprew@jefferies.com>",
            "Tritax Eurobox (BOXE LN, BUY): German Logistics with Dietz AG - PT Raised to €1.26",
            id="system2_fail_1",
        ),
        pytest.param(
            "system2_payload",
            "sean.oldfield@system2capital.com",
            "Richard Edwards <gs-portal-emails@gs.com>",
            "B&M European Value Retail SA (BMEB.L): Strong 3Q trading and special dividend are encouraging, but 15% upside to TP is below sector peers; down to Neutral",
            id="system2_payload",
        ),
        pytest.param(
            "system2_payload_plain_text",
            "<V5XFLoaderDoNotReply@spglobal.com>",
            "<postmaster@ad.lhpnr.com>",
            "Undeliverable: Summary:  Xpressfeed Loader - Info Notification",
            id="system2_payload_plain_text",
        ),
        pytest.param(
            "system2_to_string",
            "oliver.chadwick@system2capital.com",
            "ISDA Conference Department <conferences@isda.org>",
            "Miss an event? Recordings are still available, catch up now on what matters to you!",
            id="system2_to_string",
        ),
        pytest.param(
            "system2_with_attachments",
            "Undisclosed recipients:;",
            "Kahn, Lionel <Lionel.Kahn@gs.com>",
            "TODAY @ 4pm GMT/11am ET- GS Global Research Conference Call: European Equity Strategy Outlook 2021",
            id="system2_with_attachments",
        ),
        pytest.param(
            "system2_with_attachments_2",
            "Dan.brewer@system2capital.com",
            "Jefferies International Convertibles <jefferiesintlconvertibles@jefferies.com>",
            "NEW FLIGHT CENTRE - BUSY / CHINA ANTI TRUST INTERNET / DARBY ON GLOBAL MKTS / MSCI CHANGES, XRO/ESR ADD / TECH SELL OFF  - Asia CB Morning Round-Up",
            id="system2_with_attachments_2",
        ),
        pytest.param(
            "systematiq_email_non_delivery_report",
            "<V5XFLoaderDoNotReply@spglobal.com>",
            "<postmaster@ad.lhpnr.com>",
            "Undeliverable: Summary:  Xpressfeed Loader - Info Notification",
            id="systematiq_email_non_delivery_report",
        ),
        pytest.param(
            "systematiq_multiple_payload",
            "<V5XFLoaderDoNotReply@spglobal.com>",
            "<postmaster@ad.lhpnr.com>",
            "Undeliverable: Summary:  Xpressfeed Loader - Info Notification",
            id="systematiq_multiple_payload",
        ),
        pytest.param(
            "tangency_pdf_fail",
            "dh@tangencycapital.com",
            "Capital Economics <research@email.capitaleconomics.com>",
            "Capital Daily - We think that the renminbi’s appreciation has further to run",
            id="tangency_pdf_fail",
        ),
        pytest.param(
            "think-thread-decode",
            "Undisclosed recipients:;",
            "Casey Y Zhu <casey.y.zhu@us.hsbc.com>",
            "**HSBC Deal: Sirnaomics Ltd. HK IPO ¨C LAUNCH ** Approved external email",
            id="think-thread-decode",
        ),
        pytest.param(
            "valeur_calendar",
            "gabriele.leandri@valeurconcept.ch <gabriele.leandri@valeurconcept.ch>",
            "Eurotherm - Web Academy <Webacademy@eurotherm.info>",
            "Il tuo webinar: Qualità dell’aria interna: dalla filtrazione alla sanificazione",
            id="valeur_calendar",
        ),
        pytest.param(
            "valeur_header",
            "<JACOPO@aol.com>",
            "Canvas Prints <HbMUZhv-1Q5blTs-noReply@whpam.sportsyet.com>",
            "16x20 Canvas Prints ONLY $14.99",
            id="valeur_header",
        ),
        pytest.param(
            "valeur_multiple_attachments",
            "Stable AM - Investor Relations <ir@stableam.com>",
            "Stable AM - Investor Relations <ir@stableam.com>",
            "Stable Seed Fund // Quarterly Letter // Q3 2020",
            id="valeur_multiple_attachments",
        ),
        pytest.param(
            "valeur_utf8",
            "stefano.chiodini@valeur.ch",
            "Citywire Italia <noreply@listserve.citywire.co.uk>",
            "Speciale consulenti - Reti, ecco i modelli che vincono sul Covid; "
            "Reclutamenti, chi sale e chi scende nell’ultimo mese; Scelte, paure e "
            "perplessità dei cf: tutte i risultati di un sondaggio",
            id="valeur_utf8",
        ),
    ]

    @pytest.mark.parametrize("file_name, to, from_, subject", CASES)
    def test_mime_gen(self, get_mime_file, file_name, to, from_, subject):
        email = parseMIME()
        email.byteMail = get_mime_file(file_name)
        email.process_message()
        headers = email.parsedMIME["headers"]
        assert headers["to"] == to
        assert headers["from"] == from_
        assert headers["subject"] == subject

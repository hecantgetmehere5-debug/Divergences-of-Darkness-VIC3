"""Port the Vic2 DoD storylines the content audit found missing (docs/CONTENT_AUDIT.md).

Each storyline below is a compact spec of events and decisions, rebuilt from the Vic2 files
by hand (Vic2 province IDs and effects don't exist in Vic3). This script writes valid Vic3
script and English localisation from the specs, so every event and decision gets the same
layout. Events that fired by themselves in Vic2 (mean_time_to_happen) go in a yearly pulse.

Usage: py tools/port_missing.py
Writes DoD_Vic3/events/dod_<ns>_events.txt, common/decisions/dod_<ns>_decisions.txt,
       common/modifiers/dod_missing_modifiers.txt, common/on_actions/dod_missing_on_actions.txt,
       common/scripted_effects/dod_missing_effects.txt, localization/english/dod_<ns>_l_english.yml
"""
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "DoD_Vic3"
BOM = "﻿"
ICON = {"scales": "event_scales", "map": "event_map", "military": "event_military",
        "protest": "event_protest", "portrait": "event_portrait"}


def ev(id, title, desc, options, *, image="unspecific_politicians_arguing", icon="scales",
       trigger=None, immediate=None, pulse=0, flavor=None):
    """options: list of (text, effect, ai_chance)."""
    return dict(id=id, title=title, desc=desc, options=options, image=image, icon=icon,
                trigger=trigger, immediate=immediate, pulse=pulse, flavor=flavor)


def dec(key, title, desc, shown, possible, effect, ai=50):
    return dict(key=key, title=title, desc=desc, shown=shown, possible=possible, effect=effect, ai=ai)


def ind(text, n):
    return "\n".join(("\t" * n + l.strip()) if l.strip() else "" for l in text.strip().split("\n"))


# ----------------------------------------------------------------------------------------------
# Shared effects and modifiers
# ----------------------------------------------------------------------------------------------
EFFECTS = """
# A state changes hands for money. Scopes: dod_buy_buyer, dod_buy_seller (countries).
# The buyer pays in instalments (an expense modifier), the seller receives them.
dod_buy_payment = {
	scope:dod_buy_buyer = { add_modifier = { name = dod_buy_instalments months = 60 } }
	scope:dod_buy_seller = { add_modifier = { name = dod_buy_proceeds months = 60 } }
	scope:dod_buy_seller = { change_relations = { country = scope:dod_buy_buyer value = 20 } }
}

# Ask the owner of a state region to sell it: $STATE$ = state region, $SELLER$ = tag
dod_buy_offer = {
	save_scope_as = dod_buy_buyer
	c:$SELLER$ = {
		save_scope_as = dod_buy_seller
		set_variable = { name = dod_buy_region value = s:$STATE$ }
		trigger_event = { id = dod_buy.1 days = 14 }
	}
}
"""

MODIFIERS = {
    "dod_buy_instalments": ("modifier_coins_negative", {"country_expenses_add": 400}),
    "dod_buy_proceeds": ("modifier_coins_positive", {"country_minting_add": 400}),
    "dod_amz_reparations_paid": ("modifier_coins_negative", {"country_expenses_add": 300}),
    "dod_amz_reparations_received": ("modifier_coins_positive", {"country_minting_add": 300}),
    "dod_amz_military_rule": ("modifier_rifle_positive", {"country_authority_add": 100, "country_legitimacy_base_add": -10}),
    "dod_amz_civilian_rule": ("modifier_documents_positive", {"country_legitimacy_base_add": 10}),
    "dod_amz_breton_king": ("modifier_statue_positive", {"country_prestige_add": 25, "country_legitimacy_base_add": 10}),
    "dod_amz_leonie_king": ("modifier_statue_positive", {"country_legitimacy_base_add": 20}),
    "dod_amz_cythere_iron": ("modifier_coins_positive", {"building_iron_mine_throughput_add": 0.15}),
    "dod_iron_mines": ("modifier_coins_positive", {"building_iron_mine_throughput_add": 0.1}),
    "dod_ger_imperial_capital": ("modifier_flag_positive", {"country_prestige_add": 40, "country_authority_add": 50}),
    "dod_ger_kingdom": ("modifier_statue_positive", {"country_prestige_add": 30, "country_legitimacy_base_add": 10}),
    "dod_arb_jihad": ("modifier_rifle_positive", {"unit_offense_mult": 0.1, "country_infamy_decay_mult": -0.3}),
    "dod_arb_rashidi_restoration": ("modifier_statue_positive", {"country_legitimacy_base_add": 15}),
    "dod_mid_beirut_missions": ("modifier_lightbulb_positive", {"state_pop_qualifications_mult": 0.05}),
    "dod_mid_baalbeck": ("modifier_statue_positive", {"country_prestige_add": 15}),
    "dod_mid_druze_crackdown": ("modifier_fist_negative", {"country_legitimacy_base_add": -5}),
    "dod_asi_batavia_humiliation": ("modifier_statue_negative", {"country_prestige_add": -30}),
    "dod_asi_mandate_of_heaven": ("modifier_statue_positive", {"country_legitimacy_base_add": 25, "country_prestige_add": 50}),
    "dod_asi_native_protection": ("modifier_documents_positive", {"country_legitimacy_base_add": 5, "state_assimilation_mult": -0.2}),
    "dod_asi_native_integration": ("modifier_documents_positive", {"state_assimilation_mult": 0.25}),
    "dod_asi_native_suppression": ("modifier_fist_negative", {"country_legitimacy_base_add": -10, "state_mortality_mult": 0.05}),
    "dod_afs_letat_cest_moi": ("modifier_statue_positive", {"country_authority_add": 150}),
    "dod_crm_sedentarised": ("modifier_documents_positive", {"state_pop_qualifications_mult": 0.05, "country_authority_add": 50}),
    "dod_wld_world_fair": ("modifier_lightbulb_positive", {"country_prestige_add": 30}),
    "dod_wld_sports_club": ("modifier_flag_positive", {"country_prestige_add": 5}),
    "dod_wld_mostly_harmless": ("modifier_lightbulb_positive", {"country_prestige_add": 2}),
    "dod_wld_ruined_landmark": ("modifier_statue_negative", {"country_prestige_add": -20}),
    "dod_brg_capital_lost": ("modifier_documents_negative", {"country_authority_add": -50}),
    "dod_tur_troy": ("modifier_statue_positive", {"country_prestige_add": 20}),
    "dod_clm_dissolution": ("modifier_documents_positive", {"country_legitimacy_base_add": 10}),
}

GERMAN = "OR = { country_has_primary_culture = cu:north_german country_has_primary_culture = cu:south_german country_has_primary_culture = cu:rheinish }"


def german_states(n, culture=None):
    cul = f"is_homeland = cu:{culture}" if culture else "OR = { is_homeland = cu:north_german is_homeland = cu:south_german is_homeland = cu:rheinish }"
    return f"any_scope_state = {{ count >= {n} state_region = {{ {cul} }} }}"


# ----------------------------------------------------------------------------------------------
# Storylines
# ----------------------------------------------------------------------------------------------
S = {}

# --- Amazonia (Vic2: Amazonia.txt, 984XX) -----------------------------------------------------
S["amz"] = dict(events=[
    ev(1, "The Para Question",
       "The region of Para, on the west bank of the Amazon, was nominally under our protection for decades. The Amazonian settlers took advantage of the wars to seize it. Some councillors want it back, others would settle for money.",
       [("They can keep it if they pay us.", "save_scope_as = dod_amz_claimant\nc:AMA = { trigger_event = { id = dod_amz.2 days = 14 } }", 50),
        ("Send this message: Para or war.", "save_scope_as = dod_amz_claimant\nc:AMA = { trigger_event = { id = dod_amz.3 days = 14 } }", 30),
        ("Why bother with some inhospitable jungle?", "set_variable = dod_amz_para_dropped", 20)],
       image="rp1_amazon_exploitation", icon="map", pulse=4,
       trigger="OR = { c:SPA ?= this c:CLM ?= this }\nexists = c:AMA\nc:AMA = { owns_entire_state_region = STATE_PARA }\nNOT = { has_variable = dod_amz_para_dropped }\nNOT = { has_global_variable = dod_amz_para_settled }\nis_at_war = no"),
    ev(2, "Reparations for Para",
       "Envoys from [SCOPE.sCountry('dod_amz_claimant').GetName] have approached us about Para. They will drop the matter if we pay them reparations over the coming years.",
       [("Just some money? Take the deal.", "set_global_variable = dod_amz_para_settled\nadd_modifier = { name = dod_amz_reparations_paid months = 144 }\nscope:dod_amz_claimant = { add_modifier = { name = dod_amz_reparations_received months = 144 } }", 60),
        ("And what will they do if we don't?", "scope:dod_amz_claimant = { trigger_event = { id = dod_amz.4 days = 7 } }", 40)],
       image="unspecific_signed_contract", icon="scales"),
    ev(3, "Para or War",
       "[SCOPE.sCountry('dod_amz_claimant').GetName] has demanded that we give up Para. If we refuse, it means war.",
       [("We don't have a lot of choice...", "set_global_variable = dod_amz_para_settled\ns:STATE_PARA.region_state:AMA = { set_state_owner = scope:dod_amz_claimant }", 40),
        ("Let them come!", "scope:dod_amz_claimant = { trigger_event = { id = dod_amz.4 days = 7 } }", 60)],
       image="europenorthamerica_before_the_battle", icon="military"),
    ev(4, "Amazonie Refuses",
       "The Amazonians will neither pay nor leave Para. Only force will settle the matter now.",
       [("They want war? They'll get war!", "set_global_variable = dod_amz_para_settled\ns:STATE_PARA = { add_claim = root }\nchange_relations = { country = c:AMA value = -50 }", 100)],
       image="europenorthamerica_before_the_battle", icon="military"),
    ev(5, "Chaos in the Federation",
       "The loss of Atlantia has left deep distrust between the government and the army, which says it was betrayed when victory was near. A circle of officers is plotting to take power.",
       [("The military take control of Parliament.", "set_variable = dod_amz_military_rule\nadd_modifier = { name = dod_amz_military_rule months = 120 }\ntrigger_event = { id = dod_amz.6 days = 180 }", 50),
        ("The government breaks the high command.", "add_modifier = { name = dod_amz_civilian_rule months = 120 }", 50)],
       image="ip2_unruly_soldiers", icon="military", pulse=2,
       trigger="c:AMA ?= this\ngame_date >= 1842.1.1\nNOT = { has_variable = dod_amz_chaos_done }",
       immediate="set_variable = dod_amz_chaos_done"),
    ev(6, "Secession in Equinoxia",
       "The Equinoxian republic was always the most democratic part of the Federation. The end of democracy in Amazonie has its patriots talking of secession, and the Cappadocian Revolution has begun.",
       [("We will crush them!", "every_scope_state = { limit = { is_incorporated = yes } add_radicals = { value = medium_radicals } }", 100)],
       image="votp_barricade", icon="protest"),
    ev(7, "The Return of the King?",
       "Many in the military favour a monarchy for Amazonie. Two candidates have been found: the Duke of Brittany in the Old World and the Duke of Leonie in the New.",
       [("The Duke of Brittany will be king.", "activate_law = law_type:law_monarchy\nadd_modifier = { name = dod_amz_breton_king months = 240 }", 40),
        ("The Duke of Leonie will be king.", "activate_law = law_type:law_monarchy\nadd_modifier = { name = dod_amz_leonie_king months = 240 }", 40),
        ("We are fine as we are, thank you.", "", 20)],
       image="votp_monarch_holding_court", icon="portrait", pulse=2,
       trigger="c:AMA ?= this\nhas_variable = dod_amz_military_rule\nNOT = { has_law = law_type:law_monarchy }\nNOT = { has_variable = dod_amz_king_done }",
       immediate="set_variable = dod_amz_king_done"),
    ev(8, "The Cythere Iron Basin",
       "Large iron deposits in Cythere have been known since the early days of Anglois colonisation, but there was never the means to work them. Modern mining could change that.",
       [("We shall not pass over this opportunity.", "add_modifier = { name = dod_amz_cythere_iron months = 240 }", 100)],
       image="ip4_mining_scene", icon="map", pulse=3,
       trigger="OR = { c:AMA ?= this c:LOT ?= this c:EQN ?= this }\ngame_date >= 1850.1.1\nNOT = { has_global_variable = dod_amz_iron_done }",
       immediate="set_global_variable = dod_amz_iron_done"),
])

# --- Purchases (Vic2: ColonialNation 1356XX, Rebel Islands purchases, SPA, Russian Borderlands) --
BUYERS_ARC = "OR = { c:NBG ?= this c:PLA ?= this c:VIN ?= this c:DNG ?= this c:AMA ?= this c:LOT ?= this }"
S["buy"] = dict(events=[
    ev(1, "An Offer to Buy",
       "[SCOPE.sCountry('dod_buy_buyer').GetName] has offered a great deal of money for some of our overseas territory. The land costs us more than it brings, but selling it would be a sign of weakness.",
       [("We gladly accept.", "scope:dod_buy_buyer = { trigger_event = { id = dod_buy.2 days = 7 } }\nvar:dod_buy_region = { every_scope_state = { limit = { owner = root } set_state_owner = scope:dod_buy_buyer } }\ndod_buy_payment = yes", 50),
        ("We refuse.", "scope:dod_buy_buyer = { trigger_event = { id = dod_buy.3 days = 7 } }", 50)],
       image="unspecific_signed_contract", icon="scales"),
    ev(2, "The Offer Is Accepted",
       "[SCOPE.sCountry('dod_buy_seller').GetName] has accepted our offer. The territory is ours, to be paid for over the coming years.",
       [("Excellent.", "", 100)], image="unspecific_signed_contract", icon="map"),
    ev(3, "The Offer Is Refused",
       "[SCOPE.sCountry('dod_buy_seller').GetName] has refused our offer. If we still want the territory, we will have to take it.",
       [("Then we will claim it.", "var:dod_buy_region ?= { add_claim = root }", 50), ("Hm, I see.", "", 50)],
       image="unspecific_politicians_arguing", icon="scales"),
    ev(10, "News from Distant Shores",
       "With the Curonian motherland lost, the Ducal Colonial Trading Company has no one left to protect its far-flung trading posts. They pass to whoever holds Courland now.",
       [("I can't even find the place on the map.", "s:STATE_COURLAND = { random_scope_state = { owner = { save_scope_as = dod_cur_heir } } }\nif = { limit = { exists = scope:dod_cur_heir } every_scope_state = { set_state_owner = scope:dod_cur_heir } }", 100)],
       image="unspecific_steam_ship", icon="map", pulse=10,
       trigger="c:KRL ?= this\nNOT = { owns_entire_state_region = STATE_COURLAND }\nany_scope_state = { count >= 1 }"),
], decisions=[
    dec("dod_buy_athesia", "Purchase Athesia", "Venice holds the Athesian peninsula and the islands of Eleuthera and Lucaya far from home. Their viceroy might be persuaded to sell.",
        f"{BUYERS_ARC}\nexists = c:VEN\nc:VEN = {{ owns_entire_state_region = STATE_FLORIDA }}\nNOT = {{ has_variable = dod_buy_athesia }}",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_buy_athesia\ndod_buy_offer = { STATE = STATE_FLORIDA SELLER = VEN }"),
    dec("dod_buy_cuba", "Purchase Cuba", "Cuba has served Spain for centuries, but the Spanish treasury is empty and the island is far away.",
        f"{BUYERS_ARC}\nexists = c:SPA\nc:SPA = {{ owns_entire_state_region = STATE_CENTRAL_CUBA }}\nNOT = {{ has_variable = dod_buy_cuba }}",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_buy_cuba\ndod_buy_offer = { STATE = STATE_CENTRAL_CUBA SELLER = SPA }"),
    dec("dod_buy_sudurhafeyjar", "Purchase Sudurhafeyjar", "Scandinavia's Caribbean islands of Ayiti and Righavn have become a drain on its treasury.",
        f"{BUYERS_ARC}\nexists = c:SCA\nc:SCA = {{ owns_entire_state_region = STATE_HAITI }}\nNOT = {{ has_variable = dod_buy_sudurhafeyjar }}",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_buy_sudurhafeyjar\ndod_buy_offer = { STATE = STATE_HAITI SELLER = SCA }"),
    dec("dod_buy_falklands", "Purchase the South Atlantic Islands", "Scandinavia holds the South Atlantic islands but has little use for them. Beornia does.",
        "c:NAN ?= this\nexists = c:SCA\nc:SCA = { owns_entire_state_region = STATE_SOUTH_ATLANTIC_ISLANDS }\nNOT = { has_variable = dod_buy_falklands }",
        "is_at_war = no",
        "set_variable = dod_buy_falklands\ndod_buy_offer = { STATE = STATE_SOUTH_ATLANTIC_ISLANDS SELLER = SCA }"),
    dec("dod_buy_spanish_pacific", "Purchase the Spanish Pacific", "With Manila lost, Spain's Pacific holdings are hard to govern and expensive to keep. Our government wants a foothold in the Pacific.",
        "OR = { c:JAP ?= this c:SCA ?= this }\nexists = c:SPA\nc:SPA = { owns_entire_state_region = STATE_VISAYAS }\nNOT = { has_variable = dod_buy_spanish_pacific }",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_buy_spanish_pacific\ndod_buy_offer = { STATE = STATE_VISAYAS SELLER = SPA }"),
    dec("dod_buy_curonian_colonies", "Purchase the Curonian Colonies", "The Duchy of Courland's trading company holds posts across the world that the Duke can barely defend. A rich buyer could take them off his hands.",
        "country_rank >= rank_value:great_power\nexists = c:KRL\nc:KRL = { any_scope_state = { NOT = { state_region = s:STATE_COURLAND } } }\nNOT = { has_variable = dod_buy_curonian }",
        "is_at_war = no",
        "set_variable = dod_buy_curonian\nc:KRL = { random_scope_state = { limit = { NOT = { state_region = s:STATE_COURLAND } } state_region = { save_scope_as = dod_cur_region } } }\nsave_scope_as = dod_buy_buyer\nc:KRL = { save_scope_as = dod_buy_seller set_variable = { name = dod_buy_region value = scope:dod_cur_region } trigger_event = { id = dod_buy.1 days = 14 } }"),
])

# --- German formables (Vic2: Grossdeutschland, North Germany, NGF, SGF) -------------------------
S["ger"] = dict(events=[], decisions=[
    dec("dod_form_grossdeutschland", "Let the German Eagle Rise", "For the first time in a millennium, the German people are united under one flag: ours. Let us proclaim the Greater German state and take our place as the leading power of Europe.",
        f"{GERMAN}\nNOT = {{ exists = c:GER }}\nNOT = {{ c:GER ?= this }}", f"is_at_war = no\n{german_states(14)}",
        "change_tag = GER\nadd_primary_culture = cu:north_german\nadd_primary_culture = cu:south_german\nadd_primary_culture = cu:rheinish\nadd_modifier = { name = dod_ger_kingdom months = 120 }", 80),
    dec("dod_move_capital_frankfurt", "Move the Capital to Frankfurt", "The princes of the Empire did not accept our claim, but we defeated them. In Frankfurt we can be recognised as Kaiser by all the Germans.",
        "c:HLR ?= this\nNOT = { has_variable = dod_ger_frankfurt }", "is_at_war = no\nowns_entire_state_region = STATE_HESSE",
        "set_variable = dod_ger_frankfurt\nset_capital = STATE_HESSE\nadd_primary_culture = cu:north_german\nadd_primary_culture = cu:south_german\nadd_primary_culture = cu:rheinish\nadd_modifier = { name = dod_ger_imperial_capital months = 240 }", 60),
    dec("dod_integrate_prussia", "Integration of Prussia", "Prussia was never in our sphere, but the lands we conquered there are German. We can make them part of our realm.",
        "OR = { c:HLR ?= this c:CAE ?= this }\nNOT = { country_has_primary_culture = cu:north_german }", "owns_entire_state_region = STATE_EAST_PRUSSIA",
        "add_primary_culture = cu:north_german"),
    dec("dod_integrate_elsass", "Integration of Elsass", "Elsass has been outside the Empire since the first Burgundian wars. Its Rhenish people can be brought home to the Reich.",
        "c:HLR ?= this\nNOT = { country_has_primary_culture = cu:rheinish }", "owns_entire_state_region = STATE_ALSACE_LORRAINE",
        "add_primary_culture = cu:rheinish"),
    dec("dod_integrate_rhineland", "Integration of the Rhine", "We control most of the Rhine and have won the support of its people. Fur das Vaterland!",
        "OR = { c:NGF ?= this c:SGF ?= this }\nNOT = { country_has_primary_culture = cu:rheinish }", german_states(3, "rheinish"),
        "add_primary_culture = cu:rheinish"),
    dec("dod_integrate_elbe", "Integration of the North", "Our hold on the North German lands is secure. We can win the cooperation of their people.",
        "OR = { c:RHI ?= this c:SGF ?= this }\nNOT = { country_has_primary_culture = cu:north_german }", german_states(4, "north_german"),
        "add_primary_culture = cu:north_german"),
    dec("dod_integrate_south", "Integration of the South", "Our hold on the South German lands is secure. We can win the cooperation of their people.",
        "OR = { c:NGF ?= this c:RHI ?= this }\nNOT = { country_has_primary_culture = cu:south_german }", german_states(4, "south_german"),
        "add_primary_culture = cu:south_german"),
    dec("dod_form_north_german_league", "Create the North German League", "We dominate the North German states. It is time to bind them together, a step towards German unity.",
        "country_has_primary_culture = cu:north_german\nNOT = { exists = c:NGF }\nNOT = { exists = c:GER }", f"is_at_war = no\n{german_states(6, 'north_german')}",
        "change_tag = NGF\nadd_modifier = { name = dod_ger_kingdom months = 60 }"),
    dec("dod_form_danubian_confederation", "Form the Danubian Confederation", "Our hold on the southern and central German states is firm. A proper German kingdom here is a stepping stone to greater unity.",
        "country_has_primary_culture = cu:south_german\nNOT = { exists = c:SGF }\nNOT = { exists = c:GER }", f"is_at_war = no\n{german_states(5, 'south_german')}",
        "change_tag = SGF\nadd_modifier = { name = dod_ger_kingdom months = 60 }"),
    dec("dod_kingdom_of_hanover", "Proclaim the Kingdom of Hanover", "For ages we have been dukes. Recognised as a power, we shall proclaim the Kingdom of Hanover and lay claim to the German coast.",
        "c:HAN ?= this\nNOT = { has_variable = dod_ger_hanover }", "is_at_war = no\nany_scope_state = { count >= 2 }",
        "set_variable = dod_ger_hanover\nadd_modifier = { name = dod_ger_kingdom months = 120 }\ns:STATE_SCHLESWIG_HOLSTEIN = { add_claim = root }\ns:STATE_MECKLENBURG = { add_claim = root }"),
    dec("dod_united_frisia", "Frisian Unity", "Frisia survived for centuries between Burgundy and Scandinavia, but the Burgundian conquests left it divided. Now Frisia will be whole.",
        "c:FRI ?= this\nNOT = { has_variable = dod_ger_frisia }", "is_at_war = no",
        "set_variable = dod_ger_frisia\ns:STATE_WESTPHALIA = { add_claim = root }\ns:STATE_SCHLESWIG_HOLSTEIN = { add_claim = root }"),
    dec("dod_form_westphalia", "Become Westphalia", "With Westfalen in our hands we can raise our country to the Grand Duchy of Westfalen.",
        "OR = { c:LIP ?= this c:MNR ?= this c:MRK ?= this }\nNOT = { exists = c:WES }", "is_at_war = no\nowns_entire_state_region = STATE_WESTPHALIA",
        "change_tag = WES"),
    dec("dod_form_rhineland", "Become Rhineland", "We have defeated our former master Burgundy and hold both banks of the Rhine. We can proclaim the Kingdom of Rhineland.",
        "c:BEG ?= this\nNOT = { exists = c:RHI }", "is_at_war = no\nowns_entire_state_region = STATE_RHINELAND\nowns_entire_state_region = STATE_NORTH_RHINE",
        "change_tag = RHI\nadd_modifier = { name = dod_ger_kingdom months = 60 }"),
    dec("dod_greater_rhineland", "The Greater Rhineland", "We own only part of the river that gives us our name. We must secure all of the Rhine, from its sources to its delta.",
        "c:RHI ?= this\nNOT = { has_variable = dod_ger_greater_rhine }", "is_at_war = no",
        "set_variable = dod_ger_greater_rhine\ns:STATE_ALSACE_LORRAINE = { add_claim = root }\ns:STATE_BADEN = { add_claim = root }\ns:STATE_RHINELAND = { add_claim = root }\ns:STATE_NORTH_RHINE = { add_claim = root }"),
    dec("dod_reclaim_trans_krusne", "Reclaim Trans-Krusne", "We were forced to give up the lands north of the Krusne range to the League of Berlin. Some in Bohemia have never accepted it.",
        "c:BOH ?= this\nexists = c:NGF\nNOT = { owns_entire_state_region = STATE_BRANDENBURG }\nNOT = { has_variable = dod_ger_trans_krusne }", "is_at_war = no",
        "set_variable = dod_ger_trans_krusne\ns:STATE_BRANDENBURG = { add_claim = root }\ns:STATE_ANHALT = { add_claim = root }\ns:STATE_SAXONY = { add_claim = root }"),
    dec("dod_new_oostkolonisatie", "The New Oostkolonisatie", "For too long the Elbians of the Baltic have lived under foreign rule. We must restore our dominance on its shores.",
        "c:CAE ?= this\nNOT = { has_variable = dod_ger_oostkolonisatie }", "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_ger_oostkolonisatie\ns:STATE_COURLAND = { add_claim = root }\ns:STATE_EAST_PRUSSIA = { add_claim = root }"),
])

# --- Treaty Ports (Vic2: Treaty Ports.txt) ------------------------------------------------------
TP = [("pearl_river", "The Pearl River Ports", "Macao, Hong Kong and Kwangchowan guard the riches of Guangdong and southern China.", "STATE_GUANGDONG"),
      ("shanghai", "The Shanghai Treaty Port", "Shanghai's harbour on the Yangtze delta could make it the greatest port in Asia.", "STATE_JIANGSU"),
      ("shandong", "The Shandong Treaty Ports", "Qingdao and Weihaiwei guard the Bohai Gulf and the approaches to Beijing.", "STATE_SHANDONG"),
      ("lushun", "The Lushun Treaty Port", "Lushun, Port Arthur, sits at the neck of the Liaodong peninsula, guarding the Bohai Sea.", "STATE_SHENGJING"),
      ("ningbo", "The Zhejiang Treaty Ports", "Ningbo and Jiaxing, the home of silk, are among China's oldest trading cities.", "STATE_ZHEJIANG"),
      ("taiwan", "The Taiwan Concession", "Tamsui and the Taipei basin are booming on the overseas trade in tea and camphor.", "STATE_FORMOSA"),
      ("tsushima", "The Tsushima Treaty Port", "Tsushima lies between Korea and Japan: small, poor and strategically priceless.", "STATE_KYUSHU"),
      ("cheju", "The Cheju Concession", "Cheju island in the Korea Strait is a natural base for any fleet in these waters.", "STATE_BUSAN"),
      ("gwadar", "The Gwadar Treaty Port", "Gwadar, the gateway of the wind, is a warm-water port on the Arabian Sea.", "STATE_BALUCHISTAN"),
      ("qeshm", "The Qeshm Treaty Port", "Qeshm sits in the Strait of Hormuz, the key to the Persian Gulf.", "STATE_KERMAN"),
      ("zanzibar", "The Zanzibar Concession", "Zanzibar is the market of the whole East African coast.", "STATE_ZANZIBAR"),
      ("socotra", "The Socotra Concession", "Socotra guards the mouth of the Gulf of Aden.", "STATE_YEMEN"),
      ("ifni", "The Ifni Treaty Port", "Ifni's tribes trade between the Europeans and the trans-Saharan caravans.", "STATE_MARRAKECH"),
      ("fredensborg", "The Fredensborg Treaty Port", "Fredensborg was Scandinavian until the Ashanti wars spilled over in 1817.", "STATE_GOLD_COAST")]
S["tp"] = dict(events=[], decisions=[
    dec(f"dod_tp_{k}", t, d + " A treaty port there would open the region to our trade.",
        f"country_rank >= rank_value:great_power\nNOT = {{ owns_entire_state_region = {st} }}\nNOT = {{ has_variable = dod_tp_{k} }}",
        f"is_at_war = no\ns:{st} = {{ any_scope_state = {{ owner = {{ NOT = {{ country_rank >= rank_value:great_power }} NOT = {{ this = root }} }} }} }}",
        f"set_variable = dod_tp_{k}\ns:{st} = {{ random_scope_state = {{ limit = {{ owner = {{ NOT = {{ country_rank >= rank_value:great_power }} NOT = {{ this = root }} }} }} save_scope_as = dod_tp_target }} }}\ncreate_diplomatic_play = {{ target_state = scope:dod_tp_target type = dp_take_treaty_port }}", 20)
    for k, t, d, st in TP])

# --- Russia, the Middle East and Arabia ---------------------------------------------------------
S["mid"] = dict(events=[
    ev(1, "Our Claim to Sibir",
       "The Khanate of Sibir was the last true remnant of the Golden Horde, surviving only because Moscow and its neighbours were forever at war. Its lands beyond the Urals are ours to take.",
       [("To the East, brothers.", "set_variable = dod_mid_sibir\ns:STATE_TOBOLSK = { add_claim = root }\ns:STATE_TOMSK = { add_claim = root }", 100)],
       image="ep1_cossacks", icon="map", pulse=3,
       trigger="OR = { c:NOV ?= this c:MUS ?= this c:RUS ?= this }\nNOT = { has_variable = dod_mid_sibir }\nNOT = { owns_entire_state_region = STATE_TOBOLSK }"),
    ev(2, "The Druze Revolt",
       "Since the peasants' revolt of 1834 the Druze nobles have resented every overseer sent to them. Their overlords call them heretics and treat them as such, and now the mountains are in arms.",
       [("Stop this revolt by any means necessary.", "add_modifier = { name = dod_mid_druze_crackdown months = 36 }\nevery_scope_state = { limit = { OR = { state_region = s:STATE_LEBANON state_region = s:STATE_SYRIA } } add_radicals = { value = medium_radicals } }", 100)],
       image="africa_soldiers_breaking_protest", icon="protest", pulse=3,
       trigger="OR = { owns_entire_state_region = STATE_LEBANON owns_entire_state_region = STATE_SYRIA }\nNOT = { has_variable = dod_mid_druze }",
       immediate="set_variable = dod_mid_druze"),
    ev(3, "Ancient Ruins in Baalbeck",
       "Travellers in the hills around Baalbeck have found a great number of Roman ruins, preserved by the dry air. Scholars across Europe are writing about them.",
       [("Great!", "add_modifier = { name = dod_mid_baalbeck months = 120 }", 100)],
       image="africa_desert_expedition", icon="map", pulse=2,
       trigger="owns_entire_state_region = STATE_LEBANON\ngame_date >= 1840.1.1\nNOT = { has_global_variable = dod_mid_baalbeck }",
       immediate="set_global_variable = dod_mid_baalbeck"),
    ev(4, "Missionaries in Beirut",
       "Western missionaries have opened schools and printing presses in Beirut, serving the many faiths of Lebanon. The city is becoming a centre of learning.",
       [("Great!", "add_modifier = { name = dod_mid_beirut_missions months = 240 }", 100)],
       image="ep1_printing_press", icon="scales", pulse=2,
       trigger="owns_entire_state_region = STATE_LEBANON\nNOT = { has_global_variable = dod_mid_beirut }",
       immediate="set_global_variable = dod_mid_beirut"),
    ev(5, "Punjab in Open Revolt!",
       "The Punjabis have risen against our rule and rallied around the son of Ranjit Singh, who has entered Lahore in triumph. We must act fast or our Indian ambitions end here.",
       [("Damn the Punjabis!", "every_scope_state = { limit = { state_region = s:STATE_PUNJAB } add_radicals = { value = large_radicals } }", 100)],
       image="asia_sepoy_mutiny", icon="protest", pulse=3,
       trigger="c:AFG ?= this\nowns_entire_state_region = STATE_PUNJAB\nNOT = { has_variable = dod_mid_punjab }",
       immediate="set_variable = dod_mid_punjab"),
], decisions=[
    dec("dod_restore_the_rashidis", "Restore the House of Rashid", "In the wars of the early century the Saudis and their allies sought to unite Arabia. The Al Rashid rallied the north against them. Now their throne can be restored.",
        "c:ALH ?= this\nNOT = { has_variable = dod_arb_rashidi }", "is_at_war = no\nowns_entire_state_region = STATE_HAIL",
        "set_variable = dod_arb_rashidi\nadd_modifier = { name = dod_arb_rashidi_restoration months = 120 }\ns:STATE_NEJD = { add_claim = root }"),
    dec("dod_unite_arabia", "Establish the Greater Arabian Caliphate", "We have subdued every other Arabian ruler and expelled the foreigners from their courts. Let our dynasty rule the Holy Lands for a thousand years.",
        "country_has_primary_culture = cu:bedouin\nNOT = { exists = c:UAR }", "is_at_war = no\nowns_entire_state_region = STATE_NEJD\nowns_entire_state_region = STATE_HAIL\nowns_entire_state_region = STATE_YEMEN",
        "change_tag = UAR\nadd_modifier = { name = dod_arb_rashidi_restoration months = 120 }", 80),
    dec("dod_declare_permanent_jihad", "Declare Permanent Jihad", "With the Holy Cities and most of the faithful united under one flag, we can renew the old idea of the jihad. The infidels may not like it, but our path is righteous.",
        "c:UAR ?= this\nNOT = { has_variable = dod_arb_jihad }", "is_at_war = no",
        "set_variable = dod_arb_jihad\nadd_modifier = { name = dod_arb_jihad months = 240 }"),
    dec("dod_letat_cest_moi", "L'Etat C'est Moi!", "Our actions have reduced the nobility's hold on government. The Shah's rule over the country is now undisputed.",
        "c:AFS ?= this\nNOT = { has_variable = dod_afs_letat }", "is_at_war = no\nhas_law_or_variant = law_type:law_autocracy",
        "set_variable = dod_afs_letat\nadd_modifier = { name = dod_afs_letat_cest_moi months = 240 }"),
    dec("dod_sedentarise_the_khanate", "Sedentarise the Khanate", "For millennia the great nomad empires rose and fell under the same blueprint. To survive the modern age, the Khanate must settle its people.",
        "OR = { c:CRI ?= this c:TAR ?= this }\nNOT = { has_variable = dod_crm_sedentary }", "is_at_war = no",
        "set_variable = dod_crm_sedentary\nadd_modifier = { name = dod_crm_sedentarised months = 240 }"),
])

# --- Asia and the Americas ---------------------------------------------------------------------
CHINA_SHOWN = "NOT = { exists = c:CHI }\nNOT = { has_variable = dod_asi_china }"
CHINA_POS = "is_at_war = no\nany_scope_state = { count >= 12 state_region = { is_homeland = cu:han } }"
CHINA_EFF = "set_variable = dod_asi_china\nchange_tag = CHI\nadd_modifier = { name = dod_asi_mandate_of_heaven months = 120 }"
S["asm"] = dict(events=[
    ev(1, "Batavia is Lost",
       "We have failed to regain our concession in Batavia. Our inability to subdue the Sultanate of Java has made us the laughing stock of Europe.",
       [("A great humiliation for Burgundy!", "add_modifier = { name = dod_asi_batavia_humiliation months = 60 }", 100)],
       image="ep1_transfer_of_authority", icon="map"),
], decisions=[
    dec("dod_form_china_manchu", "Complete the Conquest", "The Qing who united our lands invaded China under the Kangxi Emperor, but the Ming resisted in the south. Now we have finished what he began.",
        f"c:MCK ?= this\n{CHINA_SHOWN}", CHINA_POS, CHINA_EFF, 80),
    dec("dod_form_china_claimant", "Claim the Mandate of Heaven", "After centuries of war since the Manchu invasion we have brought unity back to China. It is time to claim the Mandate of Heaven for good.",
        f"OR = {{ c:MIG ?= this c:TAI ?= this c:TNG ?= this }}\n{CHINA_SHOWN}", CHINA_POS, CHINA_EFF, 80),
    dec("dod_form_china_yuan", "Resurrect the Yuan Empire", "The Mongol Empire of Genghis Khan was divided among his sons. One branch once ruled China. Now the Yuan can rise again.",
        f"OR = {{ c:MGL ?= this c:CHG ?= this }}\n{CHINA_SHOWN}", CHINA_POS, CHINA_EFF, 80),
    dec("dod_form_china_return", "Return Home", "After centuries of isolation across the sea, we have returned to bring unity to our motherland. Let the capital move back to the mainland.",
        f"c:DNG ?= this\n{CHINA_SHOWN}", CHINA_POS, CHINA_EFF, 80),
    dec("dod_form_china_tibet", "Become the Lord of Heaven", "Centuries ago our kings led great invasions into a fractured China. We have finished what they started.",
        f"c:TIB ?= this\n{CHINA_SHOWN}", CHINA_POS, CHINA_EFF, 80),
    dec("dod_treaty_of_batavia", "The Treaty of Batavia", "Batavia is in our hands. Now we can sit down with our former colonial masters and make them recognise it as Javanese.",
        "c:JAV ?= this\nexists = c:BRG\nNOT = { has_variable = dod_asi_batavia }", "is_at_war = no\nowns_entire_state_region = STATE_WEST_JAVA",
        "set_variable = dod_asi_batavia\nc:BRG = { trigger_event = { id = dod_asm.1 days = 7 } }\nchange_relations = { country = c:BRG value = 20 }"),
    dec("dod_goa_treaty", "Treaty with Spain over Goa", "We no longer need the colonial ports of the European powers. Spain could be asked to give up its claims on the coast.",
        "OR = { c:HND ?= this c:VIJ ?= this c:BHO ?= this c:DRA ?= this }\nNOT = { has_variable = dod_asi_goa }",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_asi_goa\ns:STATE_BOMBAY = { add_claim = root }"),
    dec("dod_masulipatnam_treaty", "Treaty with Burgundy over Masulipatnam", "We no longer need the colonial ports of the European powers. Burgundy could be asked to give up Masulipatnam.",
        "OR = { c:HND ?= this c:VIJ ?= this c:HYD ?= this c:DRA ?= this c:TRA ?= this }\nNOT = { has_variable = dod_asi_masulipatnam }",
        "is_at_war = no\ncountry_rank >= rank_value:major_power",
        "set_variable = dod_asi_masulipatnam\ns:STATE_CIRCARS = { add_claim = root }"),
    dec("dod_native_protection_act", "The Natives' Status: The Protection Act", "The natives have been pushed to the edge of our society and grow more militant. A Protection Act would set aside lands and rights for them.",
        "OR = { c:NBG ?= this c:PLA ?= this c:VIN ?= this c:DNG ?= this c:NAN ?= this c:LOT ?= this c:AMA ?= this }\nNOT = { has_variable = dod_asi_native_status }", "is_at_war = no",
        "set_variable = dod_asi_native_status\nadd_modifier = { name = dod_asi_native_protection months = 240 }"),
    dec("dod_native_integration_act", "The Natives' Status: The Integration Act", "If a native becomes one of us and assimilates, he should be treated as an equal. An Integration Act would make that the law.",
        "OR = { c:NBG ?= this c:PLA ?= this c:VIN ?= this c:DNG ?= this c:NAN ?= this c:LOT ?= this c:AMA ?= this }\nNOT = { has_variable = dod_asi_native_status }", "is_at_war = no",
        "set_variable = dod_asi_native_status\nadd_modifier = { name = dod_asi_native_integration months = 240 }"),
    dec("dod_native_suppression_act", "The Natives' Status: The Suppression Act", "Some in the government call for the natives to be driven from the land altogether.",
        "OR = { c:NBG ?= this c:PLA ?= this c:VIN ?= this c:DNG ?= this c:NAN ?= this c:LOT ?= this c:AMA ?= this }\nNOT = { has_variable = dod_asi_native_status }", "is_at_war = no",
        "set_variable = dod_asi_native_status\nadd_modifier = { name = dod_asi_native_suppression months = 240 }", 10),
    dec("dod_rohnnst_question", "The Rohnnst", "When the Cree mixed with the Chinese of Qingqiu and the Vinlandic Scandinavians, a new people was born: the Rohnnst. They trade with us and have formed a proto-state of their own.",
        "OR = { c:DNG ?= this c:VIN ?= this }\nNOT = { country_has_primary_culture = cu:rohnnst }\nNOT = { has_variable = dod_asi_rohnnst }", "is_at_war = no",
        "set_variable = dod_asi_rohnnst\nadd_primary_culture = cu:rohnnst"),
    dec("dod_greater_euskadia", "Greater Euskadia", "To keep our place on the Bay of Biscay we must extend our lands to the north.",
        "c:NAV ?= this\nNOT = { has_variable = dod_ibr_euskadia }", "is_at_war = no",
        "set_variable = dod_ibr_euskadia\ns:STATE_AQUITAINE = { add_claim = root }\ns:STATE_BASQUE_COUNTRY = { add_claim = root }"),
    dec("dod_clm_controlled_dissolution", "The Controlled Dissolution of Gran Colombia", "Gran Colombia cannot hold together. Rather than let it be torn apart, the Congress can divide it peacefully: Mexico, Granada and Quito would each go their own way.",
        "c:CLM ?= this\nNOT = { has_variable = dod_clm_dissolved }", "is_at_war = no\nNOT = { country_rank >= rank_value:great_power }",
        "set_variable = dod_clm_dissolved\nadd_modifier = { name = dod_clm_dissolution months = 120 }\ndod_release_homeland = { TAG = MEX CULTURE = mexican }\ndod_release_homeland = { TAG = QUI CULTURE = ecuadorian }\nc:GRA ?= { trigger_event = { id = dod_asm.2 days = 30 } }", 5),
])
S["asm"]["events"].append(ev(2, "The Council of Granada",
    "With the fate of Gran Colombia decided, emissaries from the southern states met to form a new country. The Federation of Granada is the result.",
    [("Let them have what they want.", "add_modifier = { name = dod_clm_dissolution months = 60 }", 100)],
    image="unspecific_signed_contract", icon="scales"))

# --- The Salzach pact (Vic2: decisions/FRA-CZH.txt) --------------------------------------------
S["sal"] = dict(events=[], decisions=[
    dec("dod_bridge_over_salzach", "The Bridge over Salzach", "The ambassadors of the King of the Dual Thrones and of the Emperor in Prague could meet in Salzburg to discuss a pact against the Most Serene Republic: Venice's mainland for the Empire's friends, the Italian question for Paris.",
        "c:BOH ?= this\nexists = c:DUA\nexists = c:VEN\nNOT = { has_global_variable = dod_salzach_pact }", "is_at_war = no",
        "set_global_variable = dod_salzach_pact\nchange_relations = { country = c:DUA value = 40 }\nc:DUA = { change_relations = { country = root value = 40 } }"),
    dec("dod_partition_of_venice", "The Partition of Venice", "The fate of the Republic of Venice was decided at Salzburg. Now we only have to carry out the treaty.",
        "c:AUS ?= this\nhas_global_variable = dod_salzach_pact\nexists = c:VEN\nNOT = { has_variable = dod_salzach_partition }", "is_at_war = no",
        "set_variable = dod_salzach_partition\ns:STATE_VENETIA = { add_claim = root }\nchange_relations = { country = c:VEN value = -40 }"),
    dec("dod_meddle_in_italy", "Announce Our Interest in Italy", "With the House of Valois finally defeated, we have room to make our influence felt in Italy.",
        "c:DUA ?= this\nNOT = { exists = c:PRV }\nNOT = { has_variable = dod_salzach_italy }", "is_at_war = no\ncountry_rank >= rank_value:great_power",
        "set_variable = dod_salzach_italy\ns:STATE_PIEDMONT = { add_claim = root }\ns:STATE_LOMBARDY = { add_claim = root }\nchange_relations = { country = c:ARA value = -50 }"),
    dec("dod_the_question_of_italy", "The Question of Italy", "La Serenissima has been beaten by the Imperial forces. Under the Treaty of Salzach, Austria should take the Republic's lands, but Paris has its own interests in Italy.",
        "c:DUA ?= this\nhas_global_variable = dod_salzach_pact\nNOT = { exists = c:VEN }\nNOT = { has_variable = dod_salzach_question }", "is_at_war = no",
        "set_variable = dod_salzach_question\nadd_modifier = { name = dod_ger_kingdom months = 60 }\ns:STATE_VENETIA = { add_claim = root }"),
])

# --- World and regional flavour ----------------------------------------------------------------
S["flv"] = dict(events=[
    ev(1, "Iron Mines in Normandie",
       "Normandie, heart of the Anglois nation, is a backward, farming region. Recent surveys have found iron ore beneath it.",
       [("We shall not pass over this opportunity.", "add_modifier = { name = dod_iron_mines months = 240 }", 100)],
       image="ip4_mining_scene", icon="map", pulse=2,
       trigger="owns_entire_state_region = STATE_NORMANDY\ngame_date >= 1845.1.1\nNOT = { has_global_variable = dod_flv_normandie }",
       immediate="set_global_variable = dod_flv_normandie"),
    ev(2, "Iron Mines in Burgundy",
       "Burgundy emerged from the Great German War as Europe's leading industrial power. New techniques now make the iron of the Burgundian heartland worth mining.",
       [("We shall not pass over this opportunity.", "add_modifier = { name = dod_iron_mines months = 240 }", 100)],
       image="ip4_mining_scene", icon="map", pulse=2,
       trigger="owns_entire_state_region = STATE_BURGUNDY\ngame_date >= 1845.1.1\nNOT = { has_global_variable = dod_flv_burgundy_iron }",
       immediate="set_global_variable = dod_flv_burgundy_iron"),
    ev(3, "The Discovery of Troy",
       "Digging beside a wall in the hill of Hisarlik, an archaeologist has found a great copper vessel and, behind it, a hoard of gold. The world is calling it the Treasure of Priam.",
       [("Troy was real!", "add_modifier = { name = dod_tur_troy months = 120 }", 100)],
       image="africa_desert_expedition", icon="map", pulse=1,
       trigger="owns_entire_state_region = STATE_AYDIN\ngame_date >= 1870.1.1\nNOT = { has_global_variable = dod_flv_troy }",
       immediate="set_global_variable = dod_flv_troy"),
    ev(4, "Anvers Lost!",
       "Antwerp, our capital, is in enemy hands. The government has fled and the realm is cut off from its heart.",
       [("We are a maritime power, after all.", "add_modifier = { name = dod_brg_capital_lost months = 24 }", 100)],
       image="unspecific_devastation", icon="military", pulse=20,
       trigger="c:BRG ?= this\nNOT = { owns_entire_state_region = STATE_FLANDERS }\nNOT = { has_variable = dod_flv_anvers_lost }",
       immediate="set_variable = dod_flv_anvers_lost"),
    ev(5, "Anvers Reconquered",
       "Antwerp is ours again. The palace can be rebuilt and the government can come home.",
       [("At last.", "remove_modifier = dod_brg_capital_lost\nset_capital = STATE_FLANDERS", 100)],
       image="unspecific_military_parade", icon="military", pulse=20,
       trigger="c:BRG ?= this\nhas_variable = dod_flv_anvers_lost\nowns_entire_state_region = STATE_FLANDERS",
       immediate="remove_variable = dod_flv_anvers_lost"),
    ev(6, "A World's Fair",
       "Our capital will host a great exhibition of industry and the arts from every nation. Pavilions of iron and glass are going up, and visitors are expected by the hundred thousand.",
       [("Let the world come and see.", "add_modifier = { name = dod_wld_world_fair months = 24 }", 100)],
       image="unspecific_world_fair", icon="scales", pulse=1,
       trigger="country_rank >= rank_value:great_power\ngame_date >= 1851.1.1\nNOT = { has_variable = dod_flv_fair }",
       immediate="set_variable = dod_flv_fair"),
    ev(7, "A New Sporting Club",
       "Gentlemen in our capital have founded a club for football, rowing and athletics. The craze for sport is spreading to the factory towns.",
       [("Splendid.", "add_modifier = { name = dod_wld_sports_club months = 60 }", 100)],
       image="ip2_cross_cultural_festival", icon="scales", pulse=1,
       trigger="game_date >= 1860.1.1\nNOT = { has_variable = dod_flv_sport }",
       immediate="set_variable = dod_flv_sport"),
    ev(8, "Mostly Harmless",
       "A clerk in the ministry has filed a long report concluding that our country is, on the whole, mostly harmless. Nobody is sure whether to be insulted.",
       [("Don't panic.", "add_modifier = { name = dod_wld_mostly_harmless months = 12 }", 100)],
       image="votp_realist_household", icon="scales", pulse=1,
       trigger="game_date >= 1840.1.1\nNOT = { has_variable = dod_flv_harmless }",
       immediate="set_variable = dod_flv_harmless"),
    ev(9, "A Landmark in Ruins",
       "Fighting in our capital has left one of its great buildings in ruins. The people take it as a national humiliation.",
       [("It will be rebuilt.", "add_modifier = { name = dod_wld_ruined_landmark months = 60 }", 100)],
       image="unspecific_fire", icon="military", pulse=1,
       trigger="is_at_war = yes\nNOT = { has_variable = dod_flv_landmark }",
       immediate="set_variable = dod_flv_landmark"),
])

# ----------------------------------------------------------------------------------------------
# Writer
# ----------------------------------------------------------------------------------------------
def write_event(ns, e):
    eid = f"dod_{ns}.{e['id']}"
    out = [f"{eid} = {{", "\ttype = country_event", "\tplacement = root", f"\ttitle = {eid}.t", f"\tdesc = {eid}.d", f"\tflavor = {eid}.f",
           f'\tevent_image = {{ video = "{e["image"]}" }}', '\ton_created_soundeffect = "event:/SFX/UI/Alerts/event_appear"',
           f'\ticon = "gfx/interface/icons/event_icons/{ICON[e["icon"]]}.dds"', "\tduration = 3"]
    if e["trigger"]:
        out += ["", "\ttrigger = {", ind(e["trigger"], 2), "\t}"]
    if e["immediate"]:
        out += ["", "\timmediate = {", ind(e["immediate"], 2), "\t}"]
    for i, (text, eff, ai) in enumerate(e["options"]):
        out += ["", "\toption = {", f"\t\tname = {eid}.{'abcdef'[i]}"]
        if i == 0:
            out.append("\t\tdefault_option = yes")
        if eff.strip():
            out.append(ind(eff, 2))
        out += [f"\t\tai_chance = {{ base = {ai} }}", "\t}"]
    out.append("}")
    return "\n".join(out)


def write_decision(d):
    return "\n".join([f"{d['key']} = {{", "\tis_shown = {", ind(d["shown"], 2), "\t}", "\tpossible = {", ind(d["possible"], 2), "\t}",
                      "\twhen_taken = {", ind(d["effect"], 2), "\t}", f"\tai_chance = {{ value = {d['ai']} }}", "}"])


def q(t):
    return t.replace('"', "'")


pulse = []
for ns, spec in S.items():
    loc = [BOM + "l_english:"]
    if spec.get("events"):
        body = [BOM + f"namespace = dod_{ns}", "", f"# Generated by tools/port_missing.py from the Vic2 DoD files the content audit found missing."]
        for e in spec["events"]:
            body += ["", write_event(ns, e)]
            eid = f"dod_{ns}.{e['id']}"
            loc += [f' {eid}.t:0 "{q(e["title"])}"', f' {eid}.d:0 "{q(e["desc"])}"', f' {eid}.f:0 "{q(e["flavor"] or e["title"])}"']
            for i, (text, _, _) in enumerate(e["options"]):
                loc.append(f' {eid}.{"abcdef"[i]}:0 "{q(text)}"')
            if e["pulse"]:
                pulse.append((e["pulse"], eid))
        (MOD / f"events/dod_{ns}_events.txt").write_text("\n".join(body) + "\n", encoding="utf-8")
    if spec.get("decisions"):
        body = [BOM + "# Generated by tools/port_missing.py from the Vic2 DoD decision files the content audit found missing."]
        for d in spec["decisions"]:
            body += ["", write_decision(d)]
            loc += [f' {d["key"]}:0 "{q(d["title"])}"', f' {d["key"]}_desc:0 "{q(d["desc"])}"']
        (MOD / f"common/decisions/dod_{ns}_decisions.txt").write_text("\n".join(body) + "\n", encoding="utf-8")
    (MOD / f"localization/english/dod_{ns}_l_english.yml").write_text("\n".join(loc) + "\n", encoding="utf-8")

mods = [BOM + "# Generated by tools/port_missing.py"]
for k, (icon, vals) in MODIFIERS.items():
    mods += [f"{k} = {{", f'\ticon = "gfx/interface/icons/timed_modifier_icons/{icon}.dds"'] + [f"\t{a} = {b}" for a, b in vals.items()] + ["}"]
(MOD / "common/modifiers/dod_missing_modifiers.txt").write_text("\n".join(mods) + "\n", encoding="utf-8")
(MOD / "common/scripted_effects/dod_missing_effects.txt").write_text(BOM + EFFECTS.lstrip(), encoding="utf-8")
on = [BOM + "# Generated by tools/port_missing.py: events that fired by themselves in Vic2, checked once a year.",
      "dod_missing_pulse = {", "\trandom_events = {", "\t\t100 = 0"] + [f"\t\t{w} = {e}" for w, e in pulse] + ["\t}", "}"]
(MOD / "common/on_actions/dod_missing_on_actions.txt").write_text("\n".join(on) + "\n", encoding="utf-8")
print("storylines:", len(S), "events:", sum(len(s.get("events", [])) for s in S.values()),
      "decisions:", sum(len(s.get("decisions", [])) for s in S.values()), "pulse events:", len(pulse))

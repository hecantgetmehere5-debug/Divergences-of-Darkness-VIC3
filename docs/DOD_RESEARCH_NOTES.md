# Divergences of Darkness: research notes for the Vic3 port

Sources: the fan [Victoria 2 Divergences Wiki](https://victoria2divergences.fandom.com/wiki/Victoria_2_Divergences_Wiki) (History, Tag List, Anglois, Arcadianism, The Great German War, Holy Roman Empire, Dual Monarchy, Burgundy, Scandinavia, Ottoman Empire), and the existing [Vic3 DoD on the Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3118003368) (description and change notes).

---

## 1. The existing Vic3 version of DoD

- **What it is:** a team project by divergencesdev, KallarDuskwood and about 25 credited contributors. About 50,000 subscribers, 1.2 GB, last updated 15 October. Supports game version 1.13. Discord: discord.gg/UqZZEMtcSd.
- **Requires:** the *Voice of the People* and *Sphere of Influence* DLCs.
- **Lore:** "tweaked" compared with the Vic2 mod. Script files use the prefix `dvg_` (ours use `dod_`, so they won't clash if both are ever loaded).
- **Content its change notes mention, useful as design reference:**
  - **Russia:** anarchy before unification, ended by choosing a Tsar (including a Cossack "Ataman-Tsar"). After unification, a "national confusion" with 3 sides competing for Eurasian hegemony, a union of the Muscovite and Novgorodian churches, and a new capital.
  - **Australia / Zhourao:** an "Australien" culture (with "blanc australien", "Indo-Australien" and "Chougie-Indigene"). Journal entries on racial tensions, convict labour and forming "Australie"; the subjects Terrejean and Verland under Burgundy.
  - **Savoy and Italy:** reforming Vittorio Luigi or making Amedeo ruler, Corsica-Piedmont forming Savoy, an Italian Confederation, new Italian Wars, a Latin Union, San Marino and Monaco.
  - **Arcadia:** a Plantagenian slavery debate, a "Cowboy King" journal entry, a post-unification Arcadian Union as a hegemon, and Skraeling state names.
  - **Beornia:** the "Communion Genesis" journal entry, Presbyterian and Parisher political movements, a "King Charles arrested" event, a border-raid play against the Incas, and a Beornian-Lotharian Union that can form and break apart.
  - **Other:** Prussia and West Africa content, a Hungarian Crisis, a cut Danubian unification journal entry, Japan's economic setup, Plantagenia using a vanilla-style regency, and supply ships for every navy.
- **Known problems players report:** crashes when "springtime of the peoples" fires, copper missing from every province, a broken Colombian Alliance independence war goal, and Australien journal entries and pops appearing in the wrong places.

**What this means for us:** nothing to reuse. The port stays independent, so the map and culture setup will be built from the Vic2 mod, the wiki and the Vic3 game files. Their content and ours overlap in places (Russia, Arcadia, Beornia) but take different directions.

---

## 2. The world in 1836 (start setup)

### Dual Monarchy (DUA)
- **Population** 13.05 million. **Capital** Paris. Semi-constitutional monarchy; ruling party Parti Modéré (Liberal). **King** Henri X (since 1832). Catholic 78%, Protestant 18%. Literacy 30.5%.
- **Cultures:**
  - Anglois 25.4% (primary); Breton 4.6% and Welsh 2.9% (accepted)
  - **not accepted:** English 17.2%, French 15.9%, Provencal 14.5%, Irish 13.8%

  This matches our Anglois Dilemma meters. The Anglois live mostly near the Channel, in Bordeaux and in Dublin.
- **Government:**
  - **Parliament of the People:** 501 seats, a property-qualified male vote, elections every 4 years.
  - **Parliament of the Lords:** 200 appointed seats, split England 75, France 75, Ireland 15, Occitania 15, Wales 10, Brittany 10. Occitania is under-represented as punishment for its Protestant rebellions.
- **Diplomacy:** long-time ally of Spain. Savoy is in its sphere, and it has influence in Navarre.
- **Monarch list,** from Henri V (1420) to Henri X (1832–), usable for flavour text.

### Burgundy (BRG)
- **Population** 7.0 million. **Capital** Anvers (Antwerp). Constitutional monarchy; ruling party Parti Réformiste (Liberal). Protestant (Zwinglian). Literacy 72.4%. Primary Burgundian, accepted Dutch. Very homogeneous.
- **Sphere:** Württemberg, Switzerland, Nassau, Münster, Lippe-Detmold, Frankfurt, East Frisia, Berg and Baden. Also Hyderabad, for its Indian ports.
- **Colonies:**
  - most of Java
  - the Cape, where the restless Boer states Leeuwin, Nuweflander and Opstalia are breaking away
  - Grand Bassam
- **Paths the wiki lists:** the Rhine Confederacy, the Kingdom of France, the Kingdom of Arles, and annexing Batavia.

### Scandinavia (SCA)
- **Population** 5.34 million. **Capital** Copenhagen. Semi-constitutional, Protestant (Scandinavian Zwinglian Church). Literacy 63.5%. One merged Scandinavian culture.
- **Territory:** Scandinavia, Finland, Scotland, Estonia, much of Livonia, and Pomerania.
- **Subjects and sphere:** puppets Oldenburg and Pskov. Sphere: Courland, Lithuania, Sindh and Novgorod.
- **Colonies:** Sudurhafeyjar (Hispaniola), Christiania (Philippines), Mozambique, Malacca trade posts, Indian outposts.
- **Ambition:** Dominium Maris Baltici. Rivals Bohemia and Poland-Lithuania.

### Bohemia / the HRE (HLR)
- **After the Great German War (1795–1820), the Treaty of Paris (1820):**
  - The HRE became the "Kingdom of the Germans", with a ceremonial Reichstag.
  - Austria and Bavaria became independent; Austria lost Salzburg and Tyrol.
  - The Confederation of the Rhine was dissolved; its states keep special ties to Burgundy.
  - Freedom of religion is guaranteed in Germany.
  - The Bohemian crown keeps Bohemia, Silesia, Brandenburg and Saxony.
- **Ruler:** Wenceslas died in 1821 (the "Stone Emperor", Opa Stein), succeeded by the child Sigismund (Zsigmond) V.
- **Wiki form of the HRE:**
  - **Forming it:** HRE players typically fight wars against Scandinavia and Burgundy to free the "Imperial lands", then take the "Thousand Year Reich" decision, which leads to the Prague Proclamation. Our pilot uses the same flow.
  - **The Bohemian revolt:** moving the capital to Frankfurt accepts the Elbian, Danubian and Rhenish cultures, but triggers the Bohemian revolt.
  - **Numbers:** literacy 70–90%, population 8 million or more.
  - **Time limit:** about the late 1840s.

### Ottoman Empire (TUR)
- **Population** 5.0 million. **Capital** Constantinople. Literacy 1.7%. Primary Turkish. Ruling party Loyalists (Conservative). Status: Great Power, but collapsing.
- **At war with:** Albania, Macedonia and Egypt at the start, while also facing a Janissary coup.
- **Sphere:** Crimea, Xacitarxan, the Hafsids and Hejaz. Moldavia is slipping away.
- **Civil War history:** Selim III was murdered in 1807, starting Mustafa IV (reactionary) against Suleiman (reformer). Suleiman II took the throne in 1821 and crushed the Janissaries in 1825. The Greek Uprising (1827–30) and the Aragonese-Venetian intervention (1830–33) discredited him, and Mustafa restarted the war.
- **Independence wars during the Civil War:** Hungary (under the Duke of Nitra, 1807–10), Croatia and Bosnia (Illyria, 1810–15), Iraq (1812–17).
- **Neighbours eyeing its lands:** Hungary, Illyria and Moldavia (Dobruja), Venice (western Anatolia), and the Shaki.
- **Decisions in the Vic2 mod:** accept the Bulgarians and the Bedouin.

### Arcadia
- **The War of the Double Alliance (1829–31):** Vinland and Plantagenia lost to the Belgian Confederacy. Under the Treaty of Løfby, Plantagenia ceded Basse Valoisie, and Vinland ceded Philippa and parts of Carolina (the "Baudissin incident").
- **Since then:** the Double Alliance has collapsed, and Vinland is hostile to Arcadianism.
- **Key figures:** Marshal Louise Geloes-Randwijck (now Chancellor of the Belgian Confederacy), and the generals Lars Dubenson (Vinland) and Géraud de Faucigny (Plantagenia).
- **Arcadianism:** the ideology behind union. It's strongest in the Belgian Confederacy, then Plantagenia, and weakest in Vinland. Its ideals: union of eastern Arcadia, equality of cultures, liberty ("City on the Hill"), industrial and military might, expelling the colonisers.

### Other start facts
- **Gran Colombia** is at war with Spain after the Havana disaster of 1835 (already applied to the port).
- **Egypt** has been independent since 1833 (Muhammad I, House of Alawiyya).
- **Greece** has been under Venetian protection since 1827.
- **Macedonia** revolted in 1835 under an Aragonese prince, Alexander I (Conference of Naples, 1824).
- **Lotharingia** is ruled by the dictator De Aigle (since 1817), allied with Beornia by marriage (1827).
- **Amazonie** became independent in 1825.
- **Qingqiu** has been a federal republic since the Bloodless War (1811–12).
- **Spain** conquered Morocco in 1804–08; the last Saadi sultan is in exile in Paris and dies in 1836.

---

## 3. Lore worth turning into content later

- **Treaties to name in events:** Le Verger (Brittany into France), Løfby (1831), Neuchâtel, Pegu, the Treaty of Rome of 1498 (the Dual Monarchy confirmed; the Valois styled "Kings in France"), the Treaty of Frankfurt of 1484 (Burgundy made a kingdom).
- **Wenceslas "Opa Stein":** his statue in Prague, where soldiers toss coins and ask Grandpa Stone to wake up. A natural flavour event for the HRE.
- **"Ein Deutschland":** an in-world speculative history book about a revolutionary unified Germany, criticised as unrealistic. Good for an HRE or Elbian flavour event.
- **The Anglois:** the French resent it as an imitation of their culture, and the English as the end of England. Expected flashpoints: northern England and southern France (this already matches our revolutions).

---

## 4. Suggested next steps

1. **Decided:** the port stays fully independent of the existing Vic3 DoD. Its setup is not used as a source.
2. When the game files (or their mod) are available, set up the 1836 start from section 2: populations, culture splits, laws (Dual Monarchy property-vote parliament, Ottoman autocracy, and so on), spheres and subjects, and the starting wars.
3. Add the small lore events from section 3.

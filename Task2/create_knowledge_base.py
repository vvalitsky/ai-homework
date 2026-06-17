#!/usr/bin/env python3
"""
Скрипт для подготовки базы знаний из Star Wars с заменой ключевых терминов.
Создаёт переименованные документы и словарь замен (terms_map.json).
"""

import json
import os
import random
from pathlib import Path

# базовая информация о вселенной Star Wars (переделано на альтернативные названия)
STAR_WARS_UNIVERSE = {
    "characters": {
        "Darth Vader": "Xarn Velgor",
        "Luke Skywalker": "Kael Starfire",
        "Leia Organa": "Sera Lightborn",
        "Han Solo": "Drix Void",
        "Obi-Wan Kenobi": "Thran Wise",
        "Yoda": "Zoras",
        "Anakin Skywalker": "Kaelin Skyfire",
        "Padmé Amidala": "Lyria Nightshade",
        "Palpatine": "Malthor the Dark",
        "Mace Windu": "Vex Windborn",
        "Dooku": "Count Vorthan",
        "Jar Jar Binks": "Quix Lumina",
        "Lando Calrissian": "Gren Shadowborn",
        "Emperor": "The Eternal Ruler",
        "Jedi": "Void Sentinels",
        "Sith": "Void Darklings",
    },
    "locations": {
        "Death Star": "Void Core",
        "Tatooine": "Skarron Prime",
        "Coruscant": "Nexus Crown",
        "Naboo": "Lumina Realm",
        "Alderaan": "Crystal Haven",
        "Hoth": "The Frozen Abyss",
        "Endor": "The Green Sanctuary",
        "Cloud City": "Sky Citadel",
        "Mustafar": "The Ash Wastes",
        "Kashyyyk": "Forest Stronghold",
        "Dagobah": "Swamp of Whispers",
        "Bespin": "Wind Towers",
    },
    "technology": {
        "The Force": "Synth Flux",
        "Lightsaber": "Plasma Blade",
        "Blaster": "Void Rifle",
        "Hyperspace": "Phase Drift",
        "Warp Drive": "Quantum Leap",
        "Millennium Falcon": "The Silver Phantom",
        "TIE Fighter": "Void Viper",
        "X-Wing": "Star Arrow",
        "Star Destroyer": "Titan Cruiser",
        "AT-AT": "Steel Titan",
        "R2-D2": "Unit-7",
        "C-3PO": "Protocol Bot",
    },
    "terms": {
        "Rebellion": "The Free Alliance",
        "Empire": "The Void Order",
        "Republic": "The United Dominion",
        "Clone": "Synthetic Being",
        "Padawan": "Apprentice of the Way",
        "Master": "Sage Conductor",
        "Dark Side": "The Void Path",
        "Light Side": "The Bright Way",
        "Chosen One": "The Balance Bearer",
    }
}

# Документы из Star Wars вселенной
KNOWLEDGE_BASE_DOCUMENTS = [
    {
        "title": "The Birth of the Sith",
        "content": """The fall of Anakin Skywalker is one of the most tragic tales in galactic history.
        A gifted Jedi with unprecedented command of the Force, Anakin believed he could save lives
        through power. When the Jedi Council refused him the rank of Master, he fell into despair.
        Palpatine's whispers of dark side abilities finally pushed him over the edge. Renouncing
        his vows, Anakin pledged himself to the Sith, taking the name Darth Vader. He slew the
        Jedi younglings and helped execute Order 66, nearly extinguishing the Jedi Order forever."""
    },
    {
        "title": "The Force Explained",
        "content": """The Force is an energy field created by all living things. It binds the galaxy
        together and connects all sentient beings. Jedi learn to sense and manipulate the Force for
        good. The light side is associated with self-discipline and harmony. The dark side corrupts
        the user, promising power but demanding sacrifice. Master Yoda once said: 'Fear leads to anger,
        anger leads to hate, hate leads to suffering.' The Force balances light and dark eternally."""
    },
    {
        "title": "Death Star Construction",
        "content": """The Death Star was the Empire's greatest achievement—a mobile space station
        capable of destroying entire planets. Constructed in secret over many years, it housed
        millions of workers and soldiers. The station featured a superlaser of unprecedented power,
        capable of firing across star systems. The station was heavily fortified and defended by
        thousands of TIE fighters. Despite its might, the Rebellion found a weakness: a small thermal
        exhaust port leading to the main reactor. Luke Skywalker exploited this flaw, destroying the
        station and dealing a major blow to the Empire."""
    },
    {
        "title": "The Jedi Order",
        "content": """The Jedi have protected the galaxy for thousands of years as keepers of peace
        and justice. Based on Coruscant, the Jedi Temple housed thousands of knights and countless
        apprentices. The Order was led by the Council of Jedi Masters, including Mace Windu, Yoda,
        and Ki-Adi-Mundi. Their code emphasized discipline, compassion, and harmony with the Force.
        Each Jedi carried a lightsaber, a weapon powered by a kyber crystal. The Order's fall came
        during Order 66 when Clone Troopers, implanted with control chips, turned against their
        Jedi generals. Only a few Jedi survived."""
    },
    {
        "title": "The Clone Wars",
        "content": """The Clone Wars lasted three years and devastated the galaxy. Clones, created
        from Jango Fett's template, formed the backbone of the Republic's military. Jedi served as
        generals commanding vast armies. The Separatists, led by Dooku, controlled droids and
        bioweapons. Battles raged across countless worlds: Geonosis, Utapau, and many others. The war
        was orchestrated by Palpatine to weaken both sides and prepare for his rise to power. Jedi
        General Grievous commanded droid forces and killed many Jedi. The war ended when Palpatine
        executed Order 66, turning all clones against the Jedi."""
    },
    {
        "title": "Padmé: From Senator to Queen",
        "content": """Padmé Amidala rose from the elected Queen of Naboo to a powerful Senator in
        the Republic. Her diplomatic skills and courage inspired many. She secretly married Anakin
        Skywalker despite the Jedi Code forbidding attachments. Padmé gave birth to twins: Luke and
        Leia, though she died immediately after. Some whispered that her death wasn't natural but
        caused by the pain of Anakin's fall to the dark side. Luke was hidden on Tatooine with his
        uncle Owen, while Leia was adopted by Senator Organa of Alderaan. Her children would later
        become key figures in the Rebellion against the Empire."""
    },
    {
        "title": "Tatooine: Desert World",
        "content": """Tatooine is a remote desert world on the Outer Rim, orbited by two suns.
        It is sparsely populated and far from civilized space. The planet is home to Jawas, Tusken
        Raiders, and settlers seeking a quiet life. Moisture farms dot the arid landscape, collecting
        water vapor from the air. The cities Mos Eisley and Mos Espa are hubs of smuggling and
        underworld activity. Luke Skywalker grew up on Tatooine with his uncle Owen, unaware of his
        true heritage. The planet appears desolate but holds great significance in the saga, as it
        marks the beginning of Luke's journey."""
    },
    {
        "title": "The Lightsaber: Weapon of the Jedi",
        "content": """The lightsaber is the blade weapon of the Jedi and Sith, powered by kyber
        crystals. The blade glows with brilliant colored light and can cut through almost anything.
        Different colors indicate the wielder's affiliation: blue for Jedi guardians, green for
        scholars, red for Sith. Creating a lightsaber is a personal endeavor—each Jedi must find or
        construct their own blade. The weapon is ancient, used for millennia in conflicts across
        the galaxy. Darth Vader's saber glowed an ominous red. Luke's lightsaber was passed down from
        Anakin, glowing a pure blue."""
    },
    {
        "title": "The Empire Strikes Back",
        "content": """After the Rebellion destroyed the first Death Star, the Empire mobilized its
        full military might. Emperor Palpatine deployed Star Destroyers and probe droids across the
        galaxy to find and eliminate the Rebel Alliance. Han Solo and Princess Leia fled to Cloud City,
        where they hoped to find refuge. Instead, they walked into a trap set by Darth Vader. Han was
        frozen in carbonite as a test for Vader's son, Luke. The Empire's attack on the ice moon Hoth
        scattered the Rebellion, forcing them to regroup. Despite overwhelming losses, the Rebellion
        persisted in their fight for freedom."""
    },
    {
        "title": "The Ewoks of Endor",
        "content": """Endor is a forest moon home to the Ewoks, small furry creatures standing about
        a meter tall. Despite their diminutive stature, Ewoks are fierce warriors with a strong tribal
        culture. Resources are scarce, and they live in harmony with the forest. The Ewoks were
        initially hostile to the Rebellion but formed an alliance after Princess Leia befriended them.
        Armed with spears and bows, thousands of Ewoks participated in the Battle of Endor against
        the Empire's forces. They used guerrilla tactics, traps, and the terrain to their advantage,
        proving that size and technology don't guarantee victory. The Ewoks' victory inspired hope
        throughout the Rebellion."""
    },
    {
        "title": "Palpatine: The Dark Emperor",
        "content": """Darth Sidious, known as Emperor Palpatine, is one of the most powerful Sith
        Lords ever. He orchestrated the Clone Wars, manipulated Anakin Skywalker, and destroyed the
        Jedi Order. His true identity was hidden for decades as he served as Supreme Chancellor of
        the Republic. His mastery of dark side powers allowed him to corrupt entire star systems.
        Palpatine rules the galaxy through fear and authoritarian control. His lightning bolts can
        strike down enemies from a distance. Many believe he is immortal, though his reign ultimately
        ended at his holiest temple on the second Death Star."""
    },
    {
        "title": "The Rebellion Forms",
        "content": """The Rebellion began as scattered cells of resistance against Imperial rule.
        Princess Leia Organa united these groups into a coordinated force. Mon Mothma became the
        political leader, while Admiral Ackbar commanded military operations. The Rebellion sought
        to restore democracy and freedom to the galaxy. Their first major victory came when they
        stole plans to the Death Star, revealing its fatal weakness. Thousands of senators, generals,
        and ordinary citizens joined the cause. They operated from hidden bases on Hoth, Yavin, and
        other remote worlds. Against overwhelming odds, the Rebellion stood against the Empire's
        tyranny."""
    },
    {
        "title": "Return of the Jedi",
        "content": """Luke Skywalker's training with Yoda proved he truly was a Jedi. Facing off
        against Emperor Palpatine and Darth Vader, Luke discovered his father could still be redeemed.
        He refused to kill his father and instead appealed to the good man within. Anakin, finally
        free, turned against Palpatine, destroying him. The Battle of Endor saw the Rebellion defeat
        the second Death Star and the Imperial forces protecting it. Though Anakin died saving Luke,
        his redemption showed that the light side could overcome darkness. The galaxy celebrated the
        fall of the Empire and the restoration of peace."""
    },
    {
        "title": "Cloud City Politics",
        "content": """Cloud City orbits the gas giant Bespin, serving as a hub for mining operations
        and commerce. Lando Calrissian once governed the city, known for its floating platforms and
        unparalleled luxury. The city balanced neutrality between the Empire and Rebellion but was
        eventually forced under Imperial control. When Han Solo and others fled there, Darth Vader
        used the city as a trap. The city's advanced carbonite facilities became a weapon when Han
        was frozen inside the substance. Cloud City represents the complexity of galactic politics—
        neutral parties often find themselves drawn into conflict regardless of their wishes."""
    },
    {
        "title": "The Chosen One Prophecy",
        "content": """The Jedi believed in an ancient prophecy: 'A Chosen One shall come, born
        of no father, who will bring balance to the Force.' Many believed Anakin Skywalker was this
        figure. Anakin's unusual birth and immense connection to the Force suggested he might be the
        one. However, his fall to darkness suggested the prophecy might be misunderstood. After
        Anakin redeems himself and destroys the Sith Emperor, the prophecy is fulfilled. The prophecy
        also could be attributed to Luke, who gave his father the chance to return to the light. The
        prophecy remains mysterious but suggests a larger destiny in the galaxy's spiritual dynamics."""
    },
    {
        "title": "The Order 66 Execution",
        "content": """Order 66 was the command that turned all Clone Troopers against the Jedi
        instantly. Planted biochips in their brains made them execute their Jedi generals without
        question. Orders came from Supreme Chancellor Palpatine directly. Across the galaxy, countless
        Jedi fell in a single coordinated strike. Jedi Master Yoda barely escaped, as did Obi-Wan
        Kenobi. Most Jedi, including powerful Council members, were killed by soldiers they had fought
        with for years. The attack was devastating and nearly complete. Only a handful of Jedi
        survived the purge, including the recently hidden Yoda."""
    },
    {
        "title": "Hyperspace and the Millennium Falcon",
        "content": """Hyperspace allows ships to traverse vast distances in days instead of years.
        The Millennium Falcon, captained by Han Solo, is one of the fastest ships in the galaxy.
        Modified with advanced engines and smuggling compartments, the Falcon has survived countless
        encounters with Imperial forces. The ship's reliability comes from Han's constant maintenance
        and upgrades. Despite looking like a junker, the Falcon has outrun entire fleets. It features
        quadruple laser cannons and a sophisticated computer system. The ship becomes symbolic of the
        Rebellion's spirit: scrappy, resourceful, and impossible to destroy."""
    },
    {
        "title": "Master Yoda's Wisdom",
        "content": """Yoda is the oldest and wisest of the Jedi Masters, having lived for centuries.
        His unusual appearance masks an incredibly sharp mind and powerful connection to the Force.
        Yoda trained Jedi for generations, including Count Dooku and Luke Skywalker. His aphorisms
        guide Jedi principles: 'Do or do not, there is no try.' Yoda's combat lightsaber skills remain
        unmatched despite his age. When the Empire rose and the Jedi fell, Yoda went into hiding on
        Dagobah, training the last hope for the Order. His death after training Luke freed his spirit
        to aid Luke from beyond, guiding him toward final victory."""
    },
    {
        "title": "The AT-AT Walkers",
        "content": """AT-AT walkers are colossal four-legged war machines used by the Imperial
        military. Standing as tall as trees, these assault vehicles can carry entire squads of
        stormtroopers and heavy weaponry. They are incredibly difficult to destroy due to their
        thick armor plating. The Rebellion discovered that AT-ATs could be brought down by entangling
        their legs with cables. During the Battle of Hoth, AT-ATs led the Imperial assault on the
        Rebel base. Luke Skywalker destroyed several AT-ATs using this tactic, proving that even the
        most powerful Imperial weapons could be defeated with creativity and determination."""
    },
    {
        "title": "Princess Leia's Leadership",
        "content": """Princess Leia Organa is a key leader in the Rebellion against the Empire.
        Adopted as a child by Senator Organa of Alderaan, she inherited both title and responsibility.
        Leia is brilliant, courageous, and politically astute. She survived torture on the Death Star
        by Emperor's forces yet refused to break. When Alderaan was destroyed by the Death Star, Leia
        grieved but channeled her pain into determination to defeat the Empire. She earned the rank of
        General in the Rebellion and led from the front lines. Her diplomatic skills were crucial in
        gaining support from various civilizations. Leia symbolizes hope and the possibility of
        redemption through perseverance."""
    },
    {
        "title": "Scarif: The Hidden Base",
        "content": """Scarif was a tropical planet housing the Imperial Archives and secrets of the
        Death Star Project. The planet was protected by military installations and planetary shields.
        Rebel spies infiltrated the facility to obtain Death Star plans. The mission succeeded but at
        great cost, with only a handful of soldiers surviving to transmit the stolen data. The
        transmission intercepted by Princess Leia's ship began the chain of events leading to the
        first Death Star's destruction. Scarif represents the Rebellion's willingness to risk everything
        for a chance at victory."""
    },
    {
        "title": "The Binary Star System",
        "content": """Many worlds orbit binary star systems, creating unique environmental conditions.
        Tatooine orbits two suns, creating intense heat and requiring sophisticated irrigation systems.
        The double sunsets on Tatooine are legendary and inspired young Luke to dream of adventures
        beyond his desert world. These systems create unusual physics that affect hyperspace travel.
        Engineers must account for gravity fluctuations when plotting courses through such systems. The
        unique light and shadows of binary systems have inspired philosophers and poets across the
        galaxy for generations."""
    },
    {
        "title": "Stormtrooper Training",
        "content": """Imperial Stormtroopers are the backbone of the Emperor's military might.
        Trained from youth in loyalty and obedience, they serve without question. Their armor provides
        protection but reduces mobility and vision. Stormtroopers receive combat training, tactical
        education, and psychological conditioning. Elite units include Royal Guards, Shadow Guards, and
        specialized operatives. Despite their numbers and training, Stormtroopers frequently struggle
        against Jedi and Rebel combatants. This may indicate the importance of initiative and passion
        over rote training and discipline."""
    },
    {
        "title": "The Green Sanctuary's Wildlife",
        "content": """Endor is covered in diverse ecosystems supporting thousands of species. The
        forest is old and primarily undisturbed by industrial development. Ewoks coexist with larger
        creatures in a natural balance. Some creatures are dangerous predators, while others are
        herbivorous. The forest provides all necessities: food, shelter, and materials for crafting
        tools and weapons. The interconnected nature of Endor's ecosystem means harming one species
        affects all others. The Ewoks' deep understanding of their environment gives them advantages
        when defending their world."""
    },
    {
        "title": "Mon Mothma and Military Strategy",
        "content": """Mon Mothma is a legendary military strategist and political leader of the
        Rebellion. Originally a Republic Senator, she joined the rebellion against the Empire. She
        coordinated Rebel cells across the galaxy and unified their efforts into coherent operations.
        Her diplomatic skills secured alliances with alien species and independent systems. Mothma's
        strategic insights led to victories against numerically superior Imperial forces. She understood
        the importance of propaganda and communication in winning hearts and minds. After the Empire's
        fall, Mothma became instrumental in establishing the New Republic."""
    },
    {
        "title": "The Sith Way",
        "content": """The Sith are practitioners of the dark side, opposed to the Jedi's philosophy.
        The core Sith belief is that power and dominion are the highest goods. Their abilities include
        lightning generation, enhanced strength, and dark side influence. The Sith Code states: 'Peace
        is a lie, there is only passion.' Each Sith seeks to dominate others and gain supremacy. The
        Rule of Two limited Sith to a Master and an Apprentice to prevent their mutual destruction. The
        Sith's hunger for power ultimately led to their downfall."""
    },
    {
        "title": "Obi-Wan's Journey",
        "content": """Obi-Wan Kenobi is one of the greatest Jedi Knights, known for his wisdom and
        skill with the lightsaber. He trained Anakin Skywalker and later became a hermit on Tatooine
        following the Order 66 purge. Though in hiding, Obi-Wan watched over Luke from afar, waiting
        for the time when the boy would be needed. When Luke discovered his father's lightsaber,
        Obi-Wan revealed the truth about his heritage. Though he died confronting Darth Vader,
        Obi-Wan continued to guide Luke spiritually. His sacrifice gave others time to escape, showing
        that the greatest Jedi acts are about enabling others' destiny."""
    },
    {
        "title": "The Rebel Alliance Fleet",
        "content": """The Rebellion commanded a diverse fleet ranging from massive capital ships to
        fast corvettes. Each ship type served a specific purpose in combined operations. Fighter
        squadrons consisted of X-Wings, A-Wings, and Y-Wings. Mon Calamari designed cruisers served
        as command ships and fleet carriers. The flagship, the Mon Calamari cruiser 'Home One', led
        operations in many major battles. The Rebellion's fleet was outnumbered by the Imperial Navy
        but compensated through superior tactics and crew quality. Victory came through using smaller
        ships' maneuverability against larger Imperial vessels."""
    },
    {
        "title": "The Void Viper Starfighter",
        "content": """The Void Viper is the Empire's primary starfighter, easily distinguished by
        its twin cannon pods and simple design. Built for speed and mass production rather than
        durability, Void Vipers require teamwork to be effective. Pilots joke that flying a Void Viper
        is a suicide mission, lacking shields and creature comforts. However, in large numbers, they
        prove effective against Rebel forces. The Rebellion's fighters are fewer but individually
        superior, leading to interesting strategic dynamics. Many legendary Rebel pilots lost their
        lives in dogfights against waves of Imperial fighters."""
    },
    {
        "title": "Nexus Crown: Heart of the Galaxy",
        "content": """Nexus Crown serves as the political center of Imperial governance and the
        ancient seat of power for the Old Republic. The planet is covered in vast cities and
        technological wonders—artificial structures reach into the clouds. The Jedi Temple once stood
        here before being occupied by Imperial forces. The Senate building, now controlled by Emperor
        Palpatine, coordinates governance across thousands of systems. Lower levels of the city are
        densely crowded and chaotic, while elite areas display luxury beyond measure. The planet epitomizes
        both the heights of civilization and the depths of corruption and inequality."""
    },
    {
        "title": "The Trap at Cloud City",
        "content": """Darth Vader orchestrated an elaborate trap at Cloud City to capture Luke
        Skywalker. Han Solo was frozen in carbonite as bait. Vader's plan exploited Luke's emotional
        weakness—his attachment to his friends. Luke rushed to aid them, exactly as Vader calculated.
        The confrontation between father and son revealed the truth: Luke was Vader's biological son.
        Luke lost his hand in the duel, and Vader offered him power in exchange for joining the dark
        side. Luke refused and escaped, but the psychological impact was significant. The trap showed
        Vader's understanding of human nature and emotional manipulation."""
    },
    {
        "title": "Quantum Leap Technology",
        "content": """Quantum Leap engines enable faster-than-light travel by folding spacetime through
        exotic physics. Ships equipped with Quantum Leap generators can traverse entire star systems in
        hours. Different ship classes have different drive capabilities. Larger cruisers require longer
        charging times, while fighter craft can make quick jumps. The technology remains partially
        mysterious even to galactic engineers. Hyperspace lanes provide safe routes through Quantum Leap,
        avoiding gravitational anomalies that could destroy ships. Mastery of Quantum Leap navigation
        separates elite pilots from novices."""
    },
    {
        "title": "The Swamp of Whispers",
        "content": """The Swamp of Whispers is a remote, desolate world of mist and murky waters.
        Strange creatures inhabit the fog, some deadly, others merely curious. The planet has minimal
        resources and is difficult to traverse even for experienced scouts. Master Yoda chose this world
        as his place of exile after the Jedi purge. The isolation and harshness made it perfect for
        meditation and contemplation. Despite its hostility, the planet showed Yoda the beauty of life
        persisting even in the darkest places. Luke's training here tested his physical and psychological
        limits, transforming him into a true Jedi."""
    },
    {
        "title": "The Symbol of Rebellion",
        "content": """The Rebel insignia—a bird in flight—represents hope, freedom, and resistance
        against oppression. Painted on fighter craft and worn as emblems, the symbol inspired billions
        across the galaxy. The Rebellion's symbol became synonymous with freedom. Even after the Rebel
        Alliance dissolved, the symbol endured as a reminder of victory against tyranny. From hidden
        bases to underground movements, the bird symbol appeared in protests and demonstrations. The
        power of symbols in warfare extends beyond military strategy to psychological warfare and
        morale-building."""
    },
    {
        "title": "New Hope Rises",
        "content": """When young Luke Skywalker destroyed the Death Star, the galaxy saw that
        individuals could accomplish miracles against overwhelming odds. Luke's success proved the
        Rebellion wasn't just hopeful—they could actually win. His single-pilot victory reverberated
        across rebel cells, inspiring recruitment and determination. The destruction of the Death Star
        became the turning point of the war. Historians mark this moment as the beginning of the
        Empire's decline. Luke's heroism showed that farm boys from desert worlds could change the
        destiny of billions. The symbol of Luke's X-Wing became as important as any flag or anthem."""
    },
    {
        "title": "The Final Battle",
        "content": """The Battle of Endor determined the fate of the Empire and galaxy. The Rebellion
        launched simultaneous attacks on the second Death Star in orbit and Imperial forces on Endor's
        surface. The forest battle saw Ewoks defeat stormtroopers through superior knowledge of terrain
        and unconventional tactics. Lando's flight group destroyed the Death Star from within. Luke's
        confrontation with Vader and Palpatine in the throne room sealed the Empire's fate. When
        Anakin finally destroyed the Sith Emperor, balance was restored to the Force. The victory
        came not through superior technology but through courage, determination, and the power of
        redemption."""
    },
]

def create_terms_mapping():
    """Создать словарь замен для всех терминов."""
    terms_map = {}
    for category, items in STAR_WARS_UNIVERSE.items():
        terms_map.update(items)
    return terms_map

def replace_terms(text, terms_map):
    """Заменить все термины в тексте по словарю."""
    result = text
    # Сортируем по длине (длинные первыми) чтобы избежать частичных замен
    for original, replacement in sorted(terms_map.items(), key=lambda x: len(x[0]), reverse=True):
        # Заменяем с учётом регистра
        import re
        pattern = re.compile(re.escape(original), re.IGNORECASE)
        result = pattern.sub(replacement, result)
    return result

def create_knowledge_base(output_dir="knowledge_base"):
    """Создать базу знаний с заменёнными терминами."""
    # Создать директорию
    Path(output_dir).mkdir(exist_ok=True)

    terms_map = create_terms_mapping()

    # Сохранить словарь замен
    with open(f"{output_dir}/terms_map.json", "w", encoding="utf-8") as f:
        json.dump(terms_map, f, ensure_ascii=False, indent=2)

    # Создать переименованные документы
    for idx, doc in enumerate(KNOWLEDGE_BASE_DOCUMENTS, 1):
        # Заменить термины в заголовке и содержимом
        title = replace_terms(doc["title"], terms_map)
        content = replace_terms(doc["content"], terms_map)

        # Сохранить документ
        filename = f"{output_dir}/document_{idx:03d}_{title[:30].replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(content)

    print(f"✓ Created knowledge base with {len(KNOWLEDGE_BASE_DOCUMENTS)} documents in '{output_dir}/'")
    print(f"✓ Terms mapping saved to '{output_dir}/terms_map.json'")
    print(f"✓ Total unique terms replaced: {len(terms_map)}")

if __name__ == "__main__":
    create_knowledge_base()

"""
Données du questionnaire : questions, catalogue de jeux, types de jeux, personas.
"""

from dataclasses import dataclass, field


# ──────────────────────────────────────────────
# QUESTIONS LIKERT
# ──────────────────────────────────────────────

QUESTIONS: dict[int, list[str]] = {
    1: [
        "J'aime découvrir de nouvelles stratégies au fil des parties.",
        "Ce qui me plaît le plus, c'est de mieux comprendre les mécaniques du jeu.",
        "Même quand je perds, je suis satisfait si j'ai le sentiment d'avoir progressé.",
        "J'aime analyser mes erreurs pour mieux jouer la fois suivante.",
        "Je n'aime pas avoir l'impression de ne pas exploiter correctement un jeu.",
        "Je cherche à éviter de jouer moins bien que ce dont je serais capable.",
        "Je suis gêné quand je sens que je n'ai pas bien compris les possibilités du jeu.",
        "J'aime éviter les parties où je risque de faire beaucoup d'erreurs de compréhension.",
    ],
    2: [
        "Lorsque je joue, mon objectif principal est de gagner.",
        "J'aime montrer que je suis meilleur que les autres à ce jeu.",
        "Battre de bons joueurs me procure une vraie satisfaction.",
        "J'apprécie les parties où le classement final montre clairement qui a le mieux joué.",
        "Je n'aime pas perdre de manière visible devant les autres.",
        "Je préfère éviter les jeux où je risque d'avoir l'air mauvais.",
        "Je me sens mal à l'aise quand mes erreurs de jeu sont évidentes pour la table.",
        "Quand je joue, j'essaie surtout d'éviter de faire moins bien que les autres.",
    ],
    3: [
        "J'évite autant que possible les actions qui attaquent directement les autres joueurs.",
        "Je préfère les jeux où la confrontation reste limitée ou indirecte.",
        "Je n'aime pas être à l'origine de tensions autour de la table.",
        "Je suis plus à l'aise quand le jeu ne m'oblige pas à pénaliser directement quelqu'un.",
        "Je préfère les jeux où je n'ai pas à prendre trop de décisions difficiles.",
        "Quand plusieurs options sont possibles, j'aimerais parfois que quelqu'un tranche à ma place.",
        "Je n'aime pas quand mes décisions peuvent fortement impacter le résultat de toute la table.",
        "Je me sens plus à l'aise dans les jeux où les choix à faire sont assez guidés.",
    ],
    4: [
        "Une bonne partie est avant tout une bonne expérience partagée autour de la table.",
        "J'aime les jeux qui génèrent des discussions, des réactions et une vraie dynamique de groupe.",
        "Même sans gagner, je peux beaucoup apprécier une partie si l'ambiance est bonne.",
        "Pour moi, le plaisir du jeu vient aussi de la dynamique de groupe, pas seulement du résultat.",
    ],
}

SECTION_META: dict[int, dict] = {
    1: {"color": "purple", "label": "Progression & maîtrise",  "icon": "🧠", "short": "Maîtrise"},
    2: {"color": "amber",  "label": "Compétition & image",      "icon": "🏆", "short": "Compétition"},
    3: {"color": "coral",  "label": "Évitement conflit",        "icon": "⚔️",  "short": "Anti-conflit"},
    4: {"color": "green",  "label": "Expérience sociale",       "icon": "🤝", "short": "Social"},
}


# ──────────────────────────────────────────────
# CATALOGUE DE JEUX
# ──────────────────────────────────────────────

@dataclass
class Game:
    id: str
    name: str
    emoji: str
    tags: list[str]
    diff: str
    niche: bool = False


GAME_CATALOG: list[Game] = [
    Game("catan",       "Catan",               "🏝️",  ["nego", "euro"],    "★★☆"),
    Game("trio",        "Trio",                "🃏",  ["party"],           "★☆☆"),
    Game("uno",         "UNO",                 "🟥",  ["party"],           "★☆☆"),
    Game("saboteur",    "Saboteur",            "⛏️",  ["semi", "party"],   "★☆☆"),
    Game("terra",       "Terraforming Mars",   "🔴",  ["euro"],            "★★★"),
    Game("dune",        "Dune",                "🐛",  ["ameri", "nego"],   "★★★"),
    Game("sixqui",      "6 qui prend !",       "🐂",  ["party"],           "★☆☆"),
    Game("aventuriers", "Aventuriers du Rail", "🚂",  ["euro"],            "★★☆"),
    Game("dixit",       "DiXit",               "🎨",  ["party"],           "★☆☆"),
    Game("timesup",     "Time's Up",           "⏱️",  ["party"],           "★☆☆"),
    Game("top10",       "Top 10",              "🔟",  ["party"],           "★☆☆"),
    Game("ttmc",        "TTMC",                "❓",  ["party"],           "★☆☆"),
    Game("flip7",       "Flip 7",              "7️⃣",  ["party"],           "★☆☆", niche=True),
    Game("seti",        "SETI",                "📡",  ["euro", "ameri"],   "★★★", niche=True),
    Game("dimoi",       "Di moi",              "💬",  ["party"],           "★☆☆", niche=True),
    Game("harmonie",    "Harmonie",            "🌿",  ["coop", "euro"],    "★★☆", niche=True),
    Game("kot",         "King of Tokyo",       "👹",  ["ameri"],           "★★☆"),
    Game("bomb",        "Bomb Buster",         "💣",  ["coop"],            "★★☆", niche=True),
    Game("eternal",     "Eternal Decks",       "🃏",  ["semi"],            "★★★", niche=True),
    Game("mysterium",   "Mysterium",           "👻",  ["coop"],            "★★☆"),
    Game("wingspan",    "Wingspan",            "🐦",  ["euro"],            "★★☆"),
    Game("five",        "Five Tribes",         "🐪",  ["euro"],            "★★★", niche=True),
    Game("everdell",    "Everdell",            "🐿️",  ["euro", "legacy"],  "★★☆", niche=True),
    Game("splendor",    "Splendor",            "💎",  ["euro", "abstract"],"★★☆"),
]


# ──────────────────────────────────────────────
# TYPES DE JEUX
# ──────────────────────────────────────────────

@dataclass
class GameType:
    id: str
    label: str
    icon: str
    match: dict[str, list[int]]   # {"purple": [min, max], ...}
    why: str
    examples: list[str]


GAME_TYPES: list[GameType] = [
    GameType("euro",     "Eurogame",                   "⚙️",
             {"purple": [5,7], "amber": [3,7], "coral": [3,7], "green": [2,7]},
             "Optimisation, stratégie, faible confrontation directe",
             ["Terraforming Mars","Wingspan","Everdell","Five Tribes","Splendor","Aventuriers du Rail","Harmonie"]),
    GameType("ameri",    "Ameritrash / Ameristyle",    "🎭",
             {"purple": [2,7], "amber": [4,7], "coral": [2,5], "green": [3,7]},
             "Thème fort, affrontement, drama, personnages/factions",
             ["Dune","King of Tokyo","SETI"]),
    GameType("coop",     "Coopératif",                 "🤝",
             {"purple": [3,7], "amber": [1,4], "coral": [5,7], "green": [5,7]},
             "\"Nous contre le jeu\" — zéro conflit inter-joueurs, victoire collective",
             ["Mysterium","Bomb Buster","Harmonie"]),
    GameType("semi",     "Semi-coop / traître",        "🎭",
             {"purple": [3,7], "amber": [3,6], "coral": [3,6], "green": [5,7]},
             "Alliances instables, suspicion, coordination imparfaite",
             ["Saboteur","Eternal Decks"]),
    GameType("nego",     "Négociation / diplomatie",   "🗣️",
             {"purple": [2,7], "amber": [3,7], "coral": [2,5], "green": [5,7]},
             "Aisance sociale, influence, arbitrage, conflit assumé",
             ["Catan","Dune"]),
    GameType("party",    "Party game / ambiance",      "🎉",
             {"purple": [1,5], "amber": [1,5], "coral": [3,7], "green": [5,7]},
             "Le plaisir vient du groupe, pas de la performance",
             ["Time's Up","Top 10","TTMC","DiXit","6 qui prend","Trio","UNO","Flip7","Di moi"]),
    GameType("abstract", "Jeu abstrait / duel expert", "♟️",
             {"purple": [5,7], "amber": [4,7], "coral": [1,4], "green": [1,4]},
             "Lecture pure du système, qualité de décision, sans hasard",
             ["Splendor"]),
    GameType("legacy",   "Legacy / campagne narrative","📖",
             {"purple": [4,7], "amber": [2,6], "coral": [3,7], "green": [4,7]},
             "Progression, coordination et expérience partagée sur la durée",
             ["Wingspan","Everdell"]),
]


# ──────────────────────────────────────────────
# PROFILS & PERSONAS
# ──────────────────────────────────────────────

PROFILE_DESCRIPTIONS: dict[str, str] = {
    "purple": "Vous êtes avant tout motivé par la maîtrise et la progression. Comprendre les mécaniques en profondeur, analyser vos parties, progresser d'une session à l'autre — c'est votre moteur. Les jeux à forte profondeur stratégique vous correspondent parfaitement.",
    "amber":  "La compétition est votre principal moteur. Vous jouez pour gagner et pour mesurer votre niveau face aux autres. Les tournois, classements clairs et affrontements directs vous motivent. Vous aimez démontrer votre supériorité.",
    "coral":  "Vous cherchez avant tout à éviter les conflits directs et les décisions difficiles. Les jeux coopératifs, les mécaniques indirectes et les parties sans confrontation ouverte vous conviennent mieux. Vous privilégiez l'harmonie à la table.",
    "green":  "Votre plaisir du jeu est profondément social. Gagner ou perdre importe peu si le moment partagé est de qualité. L'ambiance, les rires et la dynamique de groupe sont au cœur de votre expérience.",
}

PERSONAS: dict[str, dict[str, str]] = {
    "purple-green": {"name": "L'Explorateur stratège",     "desc": "Cherche à maîtriser des systèmes complexes tout en partageant l'expérience. Apprécie les jeux profonds joués dans un contexte convivial."},
    "purple-amber": {"name": "Le Compétiteur analytique",  "desc": "Veut gagner, mais par la compréhension et l'amélioration continue. Les jeux d'expert avec classement clair sont son terrain de jeu."},
    "purple-coral": {"name": "Le Stratège pacifiste",      "desc": "Aime la profondeur mécanique mais évite l'affrontement direct. Les euros et coopératifs à haute complexité sont sa zone de confort."},
    "amber-green":  {"name": "Le Compétiteur social",      "desc": "Aime gagner mais dans une ambiance chaleureuse. Party games à enjeu et jeux d'ambiance compétitifs lui correspondent."},
    "amber-coral":  {"name": "L'Ambivalent compétitif",    "desc": "Veut performer mais fuit le conflit visible. Les jeux à score caché ou à confrontation indirecte le rassurent."},
    "amber-purple": {"name": "Le Gagnant perfectionniste", "desc": "Veut être le meilleur et le prouve par la maîtrise du système. Très orienté résultat et excellence."},
    "coral-green":  {"name": "Le Joueur convivial",        "desc": "Vient avant tout pour le groupe. Préfère les jeux coopératifs, d'ambiance et sans tension. Le plaisir prime sur la performance."},
    "coral-purple": {"name": "Le Tacticien réservé",       "desc": "Apprécie la profondeur mais reste en retrait sur le conflit. Les jeux à puzzle individuel intégré dans un groupe lui conviennent."},
    "coral-amber":  {"name": "Le Suiveur agréable",        "desc": "S'adapte au groupe, évite de trancher. Préfère les règles claires et les jeux où les décisions sont guidées."},
    "green-purple": {"name": "L'Explorateur convivial",    "desc": "Découvre de nouveaux jeux avec enthousiasme dans un cadre social. Aime autant la nouveauté que le partage."},
    "green-amber":  {"name": "L'Animateur compétitif",     "desc": "Crée l'ambiance et aime gagner. Les party games avec score, les jeux d'ambiance compétitifs lui correspondent parfaitement."},
    "green-coral":  {"name": "Le Rassembleur",             "desc": "Crée le lien autour de la table sans jamais chercher à dominer. Les coops et party games non-compétitifs sont son espace idéal."},
}

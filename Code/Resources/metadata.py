# -*- coding: utf-8 -*-
"""

NAME:
===============================
Metadata (metadata.py)

BY:
===============================
Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Stores initial information about metadata for the sub-corpora and
uses this to initialises sub-directories of When in Rome.

We create individual files so that
1) the information is easily accessible, e.g., from the analysis file in the same dir;
and
2) each sub-corpus can store the slightly different information that is relevant
(e.g., different catalogue names etc.).

Dict keys as consistent as possible, including
All:
    "path_within_WiR": "When-in-Rome/Corpus/<x>"
    "items": itemised lists. NB: format varies
    "item_keys": explanation for the items.
    "analysis_source": the source of the included "analysis.txt" file
Some:
    "analysis<_identifier>.txt" > "analysis<_identifier>_source" for any additional analyses
    "score_source": where a local "score.mxl" is included
    "remote_score_<format>": where a remote score is available.

URLs are initialised here with the base and extended when created.
"""

# ------------------------------------------------------------------------------

from .. import raw_git


# ------------------------------------------------------------------------------

corelli_commit = "e385811"

corelli_op1 = dict(
    path_within_WiR=["Chamber_Other", "Corelli,_Arcangelo"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (1, 1, 4),
        (1, 2, 4),
        (1, 3, 4),
        (1, 4, 4),
        (1, 5, 4),
        (1, 6, 4),
        (1, 7, 3),  # NB
        (1, 8, 4),
        (1, 9, 4),
        (1, 10, 5),  # NB
        (1, 11, 4),
        (1, 12, 4),
    ),
    analysis_source=raw_git + f"DCMLab/corelli/{corelli_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/corelli/{corelli_commit}/MS3/",
    analysis_DT_source="Corelli",  # NB no public listing, so relative path only
    remote_score_krn="https://kern.humdrum.org/cgi-bin/ksdata?l=musedata/corelli/op1&file="
)


corelli_op3 = dict(
    path_within_WiR=["Chamber_Other", "Corelli,_Arcangelo"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (3, 1, 4),
        (3, 2, 4),
        (3, 3, 4),
        (3, 4, 4),
        (3, 5, 4),
        (3, 6, 4),
        (3, 7, 4),
        (3, 8, 4),
        (3, 9, 4),
        (3, 10, 4),
        (3, 11, 4),
        (3, 12, 7),  # NB
    ),
    analysis_source=raw_git + f"DCMLab/corelli/{corelli_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/corelli/{corelli_commit}/MS3/",
    remote_score_krn="https://kern.humdrum.org/cgi-bin/ksdata?l=musedata/corelli/op3&file="
)


corelli_op4 = dict(
    path_within_WiR=["Chamber_Other", "Corelli,_Arcangelo"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (4, 1, 4),
        (4, 2, 4),
        (4, 3, 4),
        (4, 4, 4),
        (4, 5, 4),
        (4, 6, 7),  # NB
        (4, 7, 5),  # NB
        (4, 8, 3),  # NB
        (4, 9, 4),
        (4, 10, 5),  # NB
        (4, 11, 3),  # NB
        (4, 12, 3),  # NB
    ),
    analysis_source=raw_git + f"DCMLab/corelli/{corelli_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/corelli/{corelli_commit}/MS3/",
    remote_score_krn="https://kern.humdrum.org/cgi-bin/ksdata?l=musedata/corelli/op3&file="
)


# ------------------------------------------------------------------------------

# Early_choral

bach_chorales = dict(
    path_within_WiR=["Early_Choral", "Bach,_Johann_Sebastian", "Chorales"],
    item_keys="Riemenschneider",
    items=371,
    analysis_source="Bach Chorales",  # NB no public listing, so relative path only
    remote_score_mxl=raw_git + "MarkGotham/Chorale-Corpus/Bach,_Johann_Sebastian/Chorales/"
)


goudimel_chorales = dict(
    path_within_WiR=["Early_Choral", "Goudimel,_Claude", "Psalmes"],
    item_keys="Psalm Number",
    items=[1, 3, 21, 25, 29, 32, 35, 36, 42, 43, 47, 49,
           52, 54, 56, 60, 66, 68, 73, 75, 79, 81, 84, 89, 97, 98, 99,
           101, 105, 108, 118, 119, 122, 123, 124, 127, 133, 135, 138, 140, 150],
    analysis_source="Goudimel",
    remote_score_mxl=raw_git + "MarkGotham/Chorale-Corpus/Goudimel,_Claude/Psalmes/"
)


madrigals = dict(
    path_within_WiR=["Early_Choral", "Monteverdi,_Claudio"],
    item_keys=("Book", "Number"),
    items=(
        (3, 20),  # "Madrigals_Book_3"
        (4, 20),
        (5, 8)
    ),
    analysis_source="Monteverdi",
    remote_score_mxl=raw_git + "cuthbertLab/music21/master/music21/corpus/monteverdi/"
)


# ------------------------------------------------------------------------------

# Keyboard_other

tempered_I = dict(
    path_within_WiR=["Keyboard_Other", "Bach,_Johann_Sebastian", "The_Well-Tempered_Clavier_I"],
    items=24,
    analysis_source="New"
)

tempered_II = dict(
    path_within_WiR=["Keyboard_Other", "Bach,_Johann_Sebastian", "The_Well-Tempered_Clavier_II"],
    items=(7, 11, 16, 23, 24),
    analysis_source="wtc_fugues",
    remote_score_krn="https://kern.humdrum.org/cgi-bin/ksdata?l=musedata/bach/keyboard/wtc-2&file="
)

chopin_commit = "ad38f0a82e5c50740b1d70a41c84924562bdf9f2"

chopin_etudes = dict(
    repo_name="chopin_etudes",
    path_within_WiR=["Keyboard_Other", "Chopin,_Frédéric", "Études_Op.10"],
    item_keys="Number",
    items=(1, 12),
    analysis_source="New",
    remote_score_mscx="https://musescore.com/user/33306646/sets/5102068"
)


chopin_mazurkas = dict(
    repo_name="chopin_mazurkas",
    path_within_WiR=["Keyboard_Other", "Chopin,_Frédéric", "Mazurkas"],
    item_keys=("Brown Catalogue", "Opus"),  # No sub-movements
    items=(

        ((16, 1), (None, None)),
        ((16, 2), (None, None)),

        ((18, None), (68, 2)),
        ((34, None), (68, 3)),
        ((38, None), (68, 1)),

        ((60, 1), (6, 1)),
        ((60, 2), (6, 2)),
        ((60, 3), (6, 3)),
        ((60, 4), (6, 4)),

        ((61, 1), (7, 1)),
        ((61, 2), (7, 2)),
        ((61, 3), (7, 3)),
        ((61, 4), (7, 4)),
        ((61, 5), (7, 5)),

        ((71, None), (None, None)),
        ((73, None), (None, None)),

        ((77, 1), (17, 1)),
        ((77, 2), (17, 2)),
        ((77, 3), (17, 3)),
        ((77, 4), (17, 4)),

        ((85, None), (None, None)),

        ((89, 1), (24, 1)),
        ((89, 2), (24, 2)),
        ((89, 3), (24, 3)),
        ((89, 4), (24, 4)),

        ((93, 1), (67, 1)),
        ((93, 2), (67, 3)),

        ((105, 2), (30, 2)),
        ((105, 3), (30, 3)),
        ((105, 4), (30, 4)),

        ((115, 1), (33, 1)),
        ((115, 2), (33, 2)),
        ((115, 3), (33, 3)),
        ((115, 4), (33, 4)),

        ((122, None), (41, 2)),

        ((126, 1), (41, 4)),
        ((126, 3), (41, 1)),
        ((126, 4), (41, 3)),

        ((134, None), (None, None)),
        ((140, None), (None, None)),

        ((145, 1), (50, 1)),
        ((145, 2), (50, 2)),
        ((145, 3), (50, 3)),

        ((153, 1), (56, 1)),
        ((153, 2), (56, 2)),
        ((153, 3), (56, 3)),

        ((157, 1), (59, 1)),
        ((157, 2), (59, 2)),
        ((157, 3), (59, 3)),

        ((162, 1), (63, 1)),
        ((162, 2), (63, 2)),
        ((162, 3), (63, 3)),

        ((163, None), (67, 4)),
        ((167, None), (67, 2)),
        ((168, None), (68, 4)),
    ),
    analysis_source=raw_git + f"DCMLab/chopin_mazurkas/{chopin_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/chopin_mazurkas/{chopin_commit}/MS3/",
    analysis_DT_source="Chopin",  # NB no public listing, so relative path only
    remote_score_krn=raw_git + "craigsapp/chopin-mazurkas/master/kern/",
)


# All new, no remote content
# chopin_preludes = dict(
#     repo_name="chopin_preludes",
#     path_within_WiR=["Keyboard_Other", "Chopin,_Frédéric", "Preludes,_Op.28"],
#     item_keys="Number",
#     items=(20,),
#     analysis_source="New",
# )


debussy_commit = "691842d8bc8e03fbf0453542d86f3d1eb7cf44eb"

debussy_suite_bergamasque = dict(
    repo_name="debussy_suite_bergamasque",
    path_within_WiR=["Keyboard_Other", "Debussy,_Claude", "Suite_Bergamasque,_L.75"],
    item_keys=("Lesure Catalogue", "Name"),
    items=(
        (75, "Prelude"),
        (75, "Menuet"),
        (75, "Clair"),
        (75, "Passepied")
    ),
    analysis_source=raw_git + f"DCMLab/debussy_suite_bergamasque/{debussy_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/debussy_suite_bergamasque/{debussy_commit}/MS3/",
)

dvorak_commit = "13502ce2304525eec6b81c68decc6d7dd48dd1e5"

dvorak_silhouettes = dict(
    repo_name="dvorak_silhouettes",
    path_within_WiR=["Keyboard_Other", "Dvořák,_Antonín", "Silhouettes,_Op.8"],
    item_keys=("Opus", "Number"),
    items=(
        (8, 1),
        (8, 2),
        (8, 3),
        (8, 4),
        (8, 5),
        (8, 6),
        (8, 7),
        (8, 8),
        (8, 9),
        (8, 10),
        (8, 11),
        (8, 12)
    ),
    analysis_source=raw_git + f"DCMLab/dvorak_silhouettes/{dvorak_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/dvorak_silhouettes/{dvorak_commit}/MS3/",
)

grieg_commit = "3ae328ea75dd8b2dc360e2be1b9125c604d9e048"

grieg_lyric_pieces = dict(
    repo_name="grieg_lyric_pieces",
    path_within_WiR=["Keyboard_Other", "Grieg,_Edvard", "Lyric_Pieces"],
    item_keys=("Opus", "Number"),
    items=(
        (12, 1),
        (12, 2),
        (12, 3),
        (12, 4),
        (12, 5),
        (12, 6),
        (12, 7),
        (12, 8),
        (38, 1),
        (38, 2),
        (38, 3),
        (38, 4),
        (38, 5),
        (38, 6),
        (38, 7),
        (38, 8),
        (43, 1),
        (43, 2),
        (43, 3),
        (43, 4),
        (43, 5),
        (43, 6),
        (47, 1),
        (47, 2),
        (47, 3),
        (47, 4),
        (47, 5),
        (47, 6),
        (47, 7),
        (54, 1),
        (54, 2),
        (54, 3),
        (54, 4),
        (54, 5),
        (54, 6),
        (57, 1),
        (57, 2),
        (57, 3),
        (57, 4),
        (57, 5),
        (57, 6),
        (62, 1),
        (62, 2),
        (62, 3),
        (62, 4),
        (62, 5),
        (62, 6),
        (65, 1),
        (65, 2),
        (65, 3),
        (65, 4),
        (65, 5),
        (65, 6),
        (68, 1),
        (68, 2),
        (68, 3),
        (68, 4),
        (68, 5),
        (68, 6),
        (71, 1),
        (71, 2),
        (71, 3),
        (71, 4),
        (71, 5),
        (71, 6),
        (71, 7),
    ),
    analysis_source=raw_git + f"DCMLab/grieg_lyric_pieces/{grieg_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/grieg_lyric_pieces/{grieg_commit}/MS3/",
)

liszt_commit = "fde6d94aca05460603a970f0f7d48ee8b8722854"

liszt_pelerinage = dict(
    repo_name="liszt_pelerinage",
    path_within_WiR=["Keyboard_Other", "Liszt,_Franz", "Années_de_pèlerinage"],
    item_keys=("Searle", "Number", "Name"),
    items=(
        (160, 1, "Chapelle_de_Guillaume_Tell"),
        (160, 2, "Au_Lac_de_Wallenstadt"),
        (160, 3, "Pastorale"),
        (160, 4, "Au_Bord_dUne_Source"),
        (160, 5, "Orage"),
        (160, 6, "Vallee_dObermann"),
        (160, 7, "Eglogue"),
        (160, 8, "Le_Mal_du_Pays_(Heimweh)"),
        (160, 9, "Les_Cloches_de_Geneve_(Nocturne)"),
        (161, 1, "Sposalizio"),
        (161, 2, "Il_Pensieroso"),
        (161, 3, "Canzonetta_del_Salvator_Rosa"),
        (161, 4, "Sonetto_47_del_Petrarca"),
        (161, 5, "Sonetto_104_del_Petrarca"),
        (161, 6, "Sonetto_123_del_Petrarca"),
        (161, 7, "Apres_une_lecture_du_Dante"),
        (162, 1, "Gondoliera"),
        (162, 2, "Canzone"),
        (162, 3, "Tarantella_da_Guillaume_Louis_Cottrau._Presto_e_canzone_napolitana"),
    ),
    analysis_source=raw_git + f"DCMLab/liszt_pelerinage/{liszt_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/liszt_pelerinage/{liszt_commit}/MS3/",
)

medtner_commit = "9d2b1991e2c7e3a06da1c41e8bc1dba9fedca05e"

medtner_tales = dict(
    repo_name="medtner_tales",
    path_within_WiR=["Keyboard_Other", "Medtner,_Nikolai", "Tales"],
    item_keys=("Opus", "Number"),
    items=(
        (8, 1),
        (14, 1),
        (26, 1),
        (26, 2),
        (26, 3),
        (26, 4),
        (34, 1),
        (34, 2),
        (34, 3),
        (34, 4),
        (35, 1),
        (35, 2),
        (35, 3),
        (35, 4),
        (42, 1),
        (42, 2),
        (42, 3),
        (48, 1),
        (48, 2)
    ),
    analysis_source=raw_git + f"DCMLab/medtner_tales/{medtner_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/medtner_tales/{medtner_commit}/MS3/",
)

schumann_commit = "22cde8be633af1ad6a2c6e08068924cbcd846274"

schumann_kinderszenen = dict(
    repo_name="schumann_kinderszenen",
    path_within_WiR=["Keyboard_Other", "Schumann,_Robert", "Kinderszenen,_Op.15"],
    item_keys="Number",
    items=13,
    analysis_source=raw_git + f"DCMLab/schumann_kinderszenen/{schumann_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/schumann_kinderszenen/{schumann_commit}/MS3/",
)

tchaikovsky_commit = "8794c63afae7cd3a7f3299c57bd326ae5b681b65"

tchaikovsky_seasons = dict(
    repo_name="schumann_kinderszenen",
    path_within_WiR=["Keyboard_Other", "Tchaikovsky,_Pyotr", "Seasons,_Op.37a"],
    item_keys="Number",
    items=12,
    analysis_source=raw_git + f"DCMLab/tchaikovsky_seasons/{tchaikovsky_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/tchaikovsky_seasons/{tchaikovsky_commit}/MS3/",
)


# ------------------------------------------------------------------------------

# Piano sonatas

lvb_commit = "f131d6dac8605ae7be9f874637330f0b73d11e2f"

sonatas_Beethoven = dict(
    path_within_WiR=["Piano_Sonatas", "Beethoven,_Ludwig_van"],
    item_keys=("Opus", "Number", "Name", "Movements", "DCML"),
    items=(
        (2, 1, None, 4, True),
        (2, 2, None, 4, True),
        (2, 3, None, 4, True),

        (7, None, None, 4, False),

        (10, 1, None, 3, True),
        (10, 2, None, 3, True),
        (10, 3, None, 4, True),

        (13, None, "Pathetique", 3, True),

        (14, 1, None, 3, True),
        (14, 2, None, 4, True),  # 10

        (22, None, None, 4, False),

        (26, None, None, 4, False),

        (27, 1, None, 4, False),
        (27, 2, "Moonlight", 3, False),

        (28, None, "Pastorale", 4, False),  # 15

        (31, 1, None, 3, True),
        (31, 2, None, 3, True),
        (31, 3, None, 4, True),

        (49, 1, None, 2, True),
        (49, 2, None, 2, True),  # 20

        (53, None, None, 3, True),
        (54, None, None, 2, False),
        (57, None, "Appassionata", 3, True),
        (78, None, None, 2, True),
        (79, None, "Sonatina", 3, False),  # 25
        ("81a", None, "Les Adieux", 3, True),
        (90, None, None, 2, False),
        (101, None, None, 4, False),
        (106, None, "Hammerklavier", 4, False),
        (109, None, None, 3, True),  # 30
        (110, None, None, 3, True),
        (111, None, None, 2, True)
    ),
    analysis_BPS_source=raw_git + f"Tsung-Ping/functional-harmony/master/BPS_FH_Dataset/",
    analysis_DCML_source=raw_git + f"DCMLab/beethoven_piano_sonatas/{lvb_commit}/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/beethoven_piano_sonatas/{lvb_commit}/MS3/",
    analysis_DT_source="Beethoven",  # NB no public listing, so relative path only
    remote_score_krn=raw_git + "craigsapp/beethoven-piano-sonatas/master/kern/",
    # No such split file issues here
)

sonatas_Mozart = dict(
    path_within_WiR=["Piano_Sonatas", "Mozart,_Wolfgang_Amadeus"],
    item_keys=("Köchel-Verzeichnis",),
    items=(
        (279, 280, 281, 282, 283, 284, 309, 310, 311, 330, 331, 332, 333, 457, 533, 545, 570, 576)
    ),  # always 3 movements so no need to specify
    analysis_source=raw_git + f"DCMLab/mozart_piano_sonatas/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/mozart_piano_sonatas/MS3/",
    analysis_DT_source="Mozart",  # NB no public listing, so relative path only
    # remote_score_krn=raw_git + "craigsapp/mozart-piano-sonatas/master/kern/",
    # Omit ^ Split files too complex (e.g., "sonata06-3m.krn").
)


# ------------------------------------------------------------------------------

# Quartets

quartets_Beethoven = dict(
    repo_name="ABC",
    path_within_WiR=["Quartets", "Beethoven,_Ludwig_van"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (18, 1, 4),
        (18, 2, 4),
        (18, 3, 4),
        (18, 4, 4),
        (18, 5, 4),
        (18, 6, 4),

        (59, 1, 4),
        (59, 2, 4),
        (59, 3, 4),

        (74, None, 4),
        (95, None, 4),
        (127, None, 4),
        (130, None, 6),
        (131, None, 7),
        (132, None, 3),
        (135, None, 4),
    ),
    analysis_source=raw_git + f"DCMLab/ABC/harmonies/",
    remote_score_mscx=raw_git + f"DCMLab/ABC/MS3/",
    # TODO consider adding "remote_score_krn"
)

haydn_op20 = dict(
    repo_name="haydn_op20",
    path_within_WiR=["Quartets", "Haydn,_Franz_Joseph"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (20, 1, 4),
        (20, 2, 4),
        (20, 3, 4),
        (20, 4, 4),
        (20, 5, 4),
        (20, 6, 4)
    ),
    analysis_source="napulen/haydn_op20_harm/master/op20/",
    remote_score_krn="napulen/humdrum-haydn-quartets/master/kern/"
)

haydn_op74 = dict(
    repo_name="haydn_op74",
    path_within_WiR=["Quartets", "Haydn,_Franz_Joseph"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (74, 1, 4),
        (74, 3, 4)
    ),
    analysis_source="Haydn",
    remote_score_krn="napulen/humdrum-haydn-quartets/master/kern/"
)

brahms_op51 = dict(
    repo_name="brahms_op51",
    path_within_WiR=["Quartets", "Brahms,_Johannes"],
    item_keys=("Opus", "Number", "Movements"),
    items=(
        (51, 1, 4),
    ),
    analysis_source="Brahms",
    score_source=raw_git + "OpenScore/StringQuartets/main/scores/Brahms,_Johannes/Op51_No1/"
)

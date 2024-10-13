import os.path
import json

errors_dict = {
    '': '',
    'missing': ' is not recognized'
}


class InternalError(Exception):
    def __init__(self, message='', context=''):
        super().__init__(message)
        self.message = f'Internal Error: {message}{errors_dict[context]}.'


LOG_PATH = './change_logs'
PROGRAM_NAME = 'Lord of the Mods'
INI_PATH_PART = '/data/ini'
LEVEL_INDENT = ' ' * 4
INI_COMMENTS = [';', '/']
INI_ENDS = ['End', 'END', 'EndScript']  # , 'end'
INI_DELIMITERS = []
STR_DELIMITERS = []


def load_delimiters():
    global INI_DELIMITERS, STR_DELIMITERS
    if os.path.isfile('./_delimiters_ini.json'):
        with open('./_delimiters_ini.json') as delimiters_buffer:
            INI_DELIMITERS = json.load(delimiters_buffer)
        # INI_DELIMITERS
    if os.path.isfile('./_delimiters_str.json'):
        with open('./_delimiters_str.json') as delimiters_buffer:
            STR_DELIMITERS = json.load(delimiters_buffer)


load_delimiters()

INI_PARAMETERS = [
    # "Side",
    # "EditorSorting",
    # "Browser"
]  # parameters to be set as first of each object
# INI_DELIMITERS = [
#     [
#         [
#             "AudioEvent",
#             "Multisound",
#             "AmbientStream",
#             "Animation",
#             "Armor",
#             "ModifierList",
#             "BannerType",
#             "CommandButton",
#             "CommandMap",
#             "DebugCommandMap",
#             "CommandSet",
#             "ControlBarResizer",
#             "CrateData",
#             "SpecialPower",
#             "DamageFX",
#             "DrawGroupInfo",
#             "EmotionNugget",
#             "SkyboxTextureSet",
#             "GlowEffect",
#             "RingEffect",
#             "FireEffect",
#             "CloudEffect",
#             "ShadowMap",
#             "ExperienceScalarTable",
#             "Fire",
#             "FontDefaultSettings",
#             "FontSubstitution",
#             "GameData",
#             "StaticGameLOD",
#             "DynamicGameLOD",
#             "AudioLOD",
#             "HouseColor",
#             "LargeGroupAudioUnusedKnownKeys",
#             "LightPointLevel",
#             "LivingWorldMapInfo",
#             "LivingWorldSound",
#             "LivingWorldObject",
#             "LivingWorldAnimObject",
#             "LivingWorldAITemplate",
#             "AutoResolveArmor",
#             "AutoResolveBody",
#             "AutoResolveCombatChain",
#             "AutoResolveHandicapLevel",
#             "AutoResolveReinforcementSchedule",
#             "AutoResolveWeapon",
#             "LivingWorldPlayerTemplate",
#             "Locomotor",
#             "MeshNameMatches",
#             "MiscAudio",
#             "Mouse",
#             "MouseCursor",
#             "OnlineChatColors",
#             "MultiplayerSettings",
#             "MultiplayerColor",
#             "MusicTrack",
#             "OptionGroup",
#             "ParticleSystem",
#             "Pathfinder",
#             "PlayerAIType",
#             "PlayerTemplate",
#             "Rank",
#             "Bridge",
#             "Road",
#             "Science",
#             "ScoredKillEvaAnnouncer",
#             "SpecialPower",
#             "DialogEvent",
#             "Terrain",
#             "Upgrade",
#             "VictorySystemData",
#             "FactionVictoryData",
#             "Video",
#             "WaterSet",
#             "WaterTextureList",
#             "Weather",
#             "WeatherData",
#             "WebpageURL"
#         ]
#     ],  # all single level items
#     [
#         [
#             "ArmySummaryDescription",
#         ],
#         [
#             "UnitCategory"
#         ]
#     ],  # ArmySummaryDescription
#     [
#         [
#             "AwardSystem"
#         ],
#         [
#             "ObjectAward",
#             "ThingStat"
#         ],
#         [
#             "Trigger"
#         ]
#     ],  # AwardSystem
#     [
#         [
#             "ControlBarScheme"
#         ],
#         [
#             "ImagePart"
#         ]
#     ],  # ControlBarScheme
#     [
#         [
#             "Object",
#             "ChildObject",
#             "ObjectReskin"
#         ],
#         [
#             "Draw",
#             "Body",
#             "ArmorSet",
#             "WeaponSet",
#             "LocomotorSet",
#             "UnitSpecificSounds",
#             "Flammability",
#             "ThreatBreakdown",
#             "ClientUpdate",
#             "ClientBehavior",
#             "Behavior",
#             "AutoResolveArmor",
#             "AutoResolveWeapon",
#             "FormationPreviewDecal",
#             "FormationPreviewItemDecal"
#         ],
#         [
#             "LodOptions",
#             "DefaultModelConditionState",
#             "ModelConditionState",
#             "IdleAnimationState",
#             "AnimationState",
#             "TransitionState",
#             "SoundState",
#             "ProductionModifier",
#             "FireWeaponNugget",
#             "InvisibilityNugget",
#             "FloodMember",
#             "ObjectStatusOfContained ="
#         ],
#         [
#             "Animation",
#             "BeginScript"
#         ]
#     ],  # Object -> if moved, correct file_interpreter: list_objects()
#     [
#         [
#             "CreateAHeroSystem"
#         ],
#         [
#             "CreateAHeroBlingBinder"
#         ]
#     ],  # "CreateAHeroSystem",
#     [
#         [
#             "CrowdResponse"
#         ],
#         [
#             "Threshold"
#         ]
#     ],  # "CrowdResponse",
#     [
#         [
#             "PredefinedEvaEvent",
#             "NewEvaEvent"
#         ],
#         [
#             "SideSound"
#         ]
#     ],  # "PredefinedEvaEvent", "NewEvaEvent",
#     [
#         [
#             "ExperienceLevel"
#         ],
#         [
#             "SelectionDecal"
#         ]
#     ],  # "ExperienceLevel",
#     [
#         [
#             "FireLogicSystem"
#         ],
#         [
#             "TerrainCellType"
#         ]
#     ],  # "FireLogicSystem",
#     [
#         [
#             "FormationAssistant"
#         ],
#         [
#             "UnitDefinition",
#             "FormationTemplate",
#             "FormationSelection"
#         ],
#         [
#             "Rows"
#         ]
#     ],  # "FormationAssistant",
#     [
#         [
#             "FXList"
#         ],
#         [
#             "Sound",
#             "ParticleSystem",
#             "DynamicDecal",
#             "TerrainScorch",
#             "BuffNugget",
#             "ViewShake",
#             "CameraShakerVolume",
#             "TintDrawable",
#             "FXListAtBonePos",
#             "LightPulse",
#             "EvaEvent",
#             "AttachedModel"
#         ]
#     ],  # "FXList",
#     [
#         [
#             "FXParticleSystem"
#         ],
#         [
#             "System",
#             "Color",
#             "Alpha",
#             "Update",
#             "Physics",
#             "EmissionVelocity",
#             "EmissionVolume",
#             "Draw",
#             "Event",
#             "Emitter",
#             "Wind"
#         ]
#     ],  # "FXParticleSystem",
#     [
#         [
#             "InGameNotificationBox",
#         ],
#         [
#             "NotificationType"
#         ]
#     ],  # "InGameNotificationBox",
#     [
#         [
#             "InGameUI"
#         ],
#         [
#             "RadiusCursorTemplate"
#         ]
#     ],  # "InGameUI",
#     [
#         [
#             "LargeGroupAudioMap"
#         ],
#         [
#             "Sound"
#         ]
#     ],  # "LargeGroupAudioMap",
#     [
#         [
#             "LinearCampaign"
#         ],
#         [
#             "Mission"
#         ]
#     ],  # "LinearCampaign",
#     [
#         [
#             "LivingWorldArmyIcon",
#             "LivingWorldBuildingIcon",
#             "LivingWorldBuildPlotIcon"
#         ],
#         [
#             "Object"
#         ]
#     ],  # "LivingWorldArmyIcon", "LivingWorldBuildingIcon", "LivingWorldBuildPlotIcon",
#     [
#         [
#             "AutoResolveLeadership"
#         ],
#         [
#             "BonusForLevel"
#         ]
#     ],  # "AutoResolveLeadership",
#     [
#         [
#             "LivingWorldAutoResolveResourceBonus",
#             "LivingWorldAutoResolveSciencePurchasePointBonus"
#         ],
#         [
#             "Bonus"
#         ]
#     ],  # "LivingWorldAutoResolveResourceBonus", "LivingWorldAutoResolveSciencePurchasePointBonus",
#     [
#         [
#             "LivingWorldBuilding"
#         ],
#         [
#             "BuildingNugget"
#         ],
#         [
#             "ArmyToSpawn"
#         ]
#     ],  # "LivingWorldBuilding",
#     [
#         [
#             "LivingWorldRegionEffects"
#         ],
#         [
#             "BordersEffect",
#             "FilledOwnershipEffect",
#             "MouseoverEffectFlareup",
#             "HomeRegionHighlight",
#             "RegionSelectionEffect",
#             "UnifiedEffect"
#         ],
#         [
#             "ColorIntensityControlPoint"
#         ]
#     ],  # "LivingWorldRegionEffects",
#     [
#         [
#             "RegionCampain"
#         ],
#         [
#             "Region"
#         ]
#     ],  # "RegionCampain",
#     [
#         [
#             "ObjectCreationList"
#         ],
#         [
#             "CreateObject"
#         ]
#     ],  # "ObjectCreationList",
#     [
#         [
#             "StanceTemplate"
#         ],
#         [
#             "Stance"
#         ]
#     ],  # "StanceTemplate",
#     [
#         [
#             "StrategicHUD"
#         ],
#         [
#             "ArmyDetailsPanel",
#             "BattleResolver",
#             "BuildQueueDetailsPanel",
#             "CancelArmyMemberMoveButton",
#             "CancelArmyMoveButton",
#             "Checklist",
#             "DestroyBuildingButton",
#             "CancelBuildingConstructionButton",
#             "DisbandArmyMemberButton",
#             "DynamicAutoResolveDialog",
#             "OptionsButton",
#             "ObjectivesButton",
#             "RegionDetailsPanelStructuresPage",
#             "RegionDisplay",
#             "StatsDisplay",
#             "ToggleSelectionDetailsButton",
#             "TypeImages",
#             "UpgradeUnitButton"
#         ]
#     ],  # "StrategicHUD",
#     [
#         [
#             "Weapon"
#         ],
#         [
#             "DamageNugget",
#             "DamageFieldNugget",
#             "DOTNugget",
#             "AttributeModifierNugget",
#             "StealMoneyNugget",
#             "ProjectileNugget",
#             "MetaImpactNugget",
#             "SlaveAttackNugget",
#             "EmotionWeaponNugget",
#             "FireLogicNugget",
#             "WeaponOCLNugget",
#             "HordeAttackNugget",
#             "DamageContainedNugget",
#             "LuaEventNugget",
#             "ParalyzeNugget",
#             "SpawnAndFadeNugget",
#             "GrabNugget",
#             "SpecialModelConditionNugget",
#             "OpenGateNugget"
#         ]
#     ],  # "Weapon",
#     [
#         [
#             "WindowTransition"
#         ],
#         [
#             "Window"
#         ],
#         [
#             "Transition"
#         ]
#     ]  # "WindowTransition"
# ]
# STR_DELIMITERS = [
#     [
#         "LETTER",
#         "NUMBER",
#         "TIME",
#         "Color",
#         "Team",
#         "MSG",
#         "GUI",
#         "APT",
#         "Apt",
#         "URL",
#         "TOOLTIP",
#         "ToolTip",
#         "Tooltip",
#         "MOTD",
#         "ERROR",
#         "Buddy",
#         "QM",
#         "FTP",
#         "FtpError",
#         "WOL",
#         "CHAT",
#         "Chat",
#         "LAN",
#         "Network",
#         "INI",
#         "SIDE",
#         "KEYBOARD",
#         "MapTransfer",
#         "CAMPAIGN",
#         "DOZER",
#         "UPGRADE",
#         "Upgrade",
#         "Mouse",
#         "SCRIPT",
#         "SCIENCE",
#         "CONTROLBAR",
#         "CONTROLBar",
#         "Controlbar",
#         "RADAR",
#         "OBJECT",
#         "Object",
#         "CampaignName",
#         "MAP",
#         "Map",
#         "DIALOGEVENT",
#         "Audio",
#         "LABEL",
#         "MESSAGE",
#         "ThingTemplate",
#         "CREDITS",
#         "STAT",
#         "Stat",
#         "LW",
#         "LWScenario",
#         "LWA",
#         "WOTR",
#         "WOTRTutorial",
#         "WOTRSCRIPT",
#         "BANNERUI",
#         "SUBTITLE",
#         "BONUSROUND",
#         "FESL",
#         "APPDATA",
#         "RULE",
#         "VALUE",
#         "CAH",
#         "CreateAHero",
#         "WIZARD",
#         "STRATEGICHUD",
#         "HUD",
#         "CP",
#         "Award",
#         "CLAN",
#         "Version"
#     ]
# ]  # .str items

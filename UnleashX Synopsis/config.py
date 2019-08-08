UNLEASHX_CONFIG_FILENAME = "C:\\config.xml"

DESCRIPTION_ICON = "F:\\Dash Icons\\description.png"
FEATURES_ICON = "F:\\Dash Icons\\features.png"
PLAY_ICON = "F:\\Dash Icons\\play.png"

# Set to None if you'd rather use the default save icon
PREFFERED_ICON_FILE = "_resources\\artwork\\icon.png"

# Note these things will only have any effect if they can actually be created
# e.g. no video preview is created if there is no video file
CREATE_SCREENSHOTS_FOLDER = True
CREATE_ARTWORK_FOLDER = True
CREATE_DESCRIPTION_POPUP = True
CREATE_FEATURES_POPUP = True
CREATE_PREVIEW_VIDEO_ITEM = True
# Create a separate title item that just displays the game/app title and can't be clicked on
CREATE_TITLE_ITEM = False
VIDEO_PREVIEW_ON_PLAY_BUTTON = False
VIDEO_PREVIEW_ON_APP_MENU_BUTTON = False

# Just create links to the artwork/screenshot folders rather than submenus that
# include the images. This is useful if you use a skin that doesn't allow for
# menu items to have icons/doesn't show preview icons.
BASIC_IMAGE_FOLDERS = False

# Artwork files to exclude
# (fog.jpg causes crashes sometimes)
EXCLUDED_ARTWORK = ["fog.jpg"]

MENU_ITEMS = [
    {
        # Menu titles seperated by / e.g. might be games/sports
        # Note this path must already exist in your config.xml
        "path": "Xbox Games",
        # Where the games/apps are stored
        "application_directories": [ "E:\\Games", "F:\\Games", "G:\\Games" ],
        # %s is replaced by the name of the game/app
        "launch_button_name": "Play: %s",
    }
]

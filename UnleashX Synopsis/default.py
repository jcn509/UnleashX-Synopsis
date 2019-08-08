import os
import xbmc
import xml.etree.ElementTree as ET
import struct
import operator
from config import *
import re

# From: https://forum.kodi.tv/showthread.php?tid=24666
# Modifed to include region information and fix the ID output
def XbeInfo(FileName):
    try :
        XbeDta          =   {}
        if os.path.isfile(FileName) and FileName.endswith('.xbe'):
            xbe         =   open(FileName,'rb')
            ## Get XbeId Data ##
            xbe.seek(0x104)
            tLoadAddr   =   xbe.read(4)
            xbe.seek(0x118)
            tCertLoc    =   xbe.read(4)
            LoadAddr    =   struct.unpack('L',tLoadAddr)
            CertLoc     =   struct.unpack('L',tCertLoc)
            CertBase    =   CertLoc[0] - LoadAddr[0]
            IdStart     =   xbe.seek(CertBase + 8)
            tIdData     =   xbe.read(4)
            IdData      =   struct.unpack('L',tIdData)
            
            ## Get Xbe Title ##
            XbeTitle    =   ''
            for dta in struct.unpack(operator.repeat('H',40),xbe.read(0x0050)):
                try     :
                    if dta != 00  :   XbeTitle += str(unichr(dta))
                except  :   pass

            RegionStart =   xbe.seek(CertBase + 0xA0)
            tRegionData =   xbe.read(4)
            Region  =   struct.unpack('L',tRegionData)[0]
            XbeDta['Title']     =   str(XbeTitle)
            XbeDta['Id']        =   str(hex(IdData[0])[2:]).lower().rjust(8,'0')
            XbeDta['Path']      =   str(FileName)
            XbeDta['Region']    =   Region
            xbe.close()
        return XbeDta
    except  :
        xbe.close()
        return {}

def create_popup_menu_item(parent_menu_node, popup_title, popup_message, icon_filename = None):
    menu_item = ET.SubElement(parent_menu_node, "List")
    menu_item.set("Text", popup_title)
    menu_item.set("Batch", "True")
    if icon_filename:
        menu_item.set("AltIcon", icon_filename)
    popup = ET.SubElement(menu_item, "Item")
    popup.set("Action", "MessageBox")
    popup.text = popup_message
    popup.set("Arg1", popup_title)

def create_file_manager_button(parent_menu_node, button_text, folder_dir, button_icon = None, button_preview_video = None):
    image_button = ET.SubElement(parent_menu_node, "Item")
    image_button.text = button_text

    if button_icon:
        image_button.set("AltIcon", button_icon)
    if button_preview_video:
        image_button.set("Preview", button_preview_video)
    
    image_button.set("Action", "FileManager")
    image_button.set("Arg1", folder_dir)

def create_images_folder_if_non_empty(parent_menu_node, folder_name, folder_dir, filter_func = None):
    if os.path.isdir(folder_dir):
        images = os.listdir(folder_dir)
        if filter:
            images = filter(filter_func, images)
        if images:
            images = sorted(images)
            first_image = os.path.join(folder_dir, images[0])
            if BASIC_IMAGE_FOLDERS:
                create_file_manager_button(parent_menu_node, folder_name, folder_dir, first_image)
            else:
                images_button = ET.SubElement(parent_menu_node, "List")
                images_button.set("sort", "Off")
                images_button.set("Text", folder_name)
                
                images_button.set("AltIcon", first_image)
                for image in images:
                    text = ('.').join(image.split('.')[:-1])
                    image_file = os.path.join(folder_dir, image)
                    create_file_manager_button(images_button, text, folder_dir, image_file)

def process_synopsis_file(parent_menu_node, synopsis_filename, description_icon_filename, features_icon_filename):
    if os.path.exists(synopsis_filename):
        synopsis = ET.parse(synopsis_filename).getroot()

        if CREATE_DESCRIPTION_POPUP:
            overview = synopsis.find("overview")
            if overview.text:
                create_popup_menu_item(parent_menu_node, "Description", overview.text.replace("\n", "\\n"), description_icon_filename)

        if CREATE_FEATURES_POPUP:
            features = "\\n".join([child.tag + ": "+ child.text for child in synopsis.findall("*") if child.text and child.tag != "overview"])
            create_popup_menu_item(parent_menu_node, "Features", features, features_icon_filename)

def create_app_menu_item(apps_menu, app_directory, launch_button_name):
    xbe_filename = os.path.join(app_directory,"default.xbe")
    if os.path.isfile(xbe_filename):
        xbe_info = XbeInfo(xbe_filename)
        if "Title" in xbe_info:
            title = xbe_info['Title']
        else:
            title = app_directory.split(os.sep)[-1]
            
        app_menu_node = ET.SubElement(apps_menu, "List")
        app_menu_node.set("sort", "Off")
        app_menu_node.set("Text", title)
        if CREATE_TITLE_ITEM:
            title_node = ET.SubElement(app_menu_node, "Item")
            title_node.text = title
        launch_node = ET.SubElement(app_menu_node, "Item")
        launch_node.text = launch_button_name % title
        
        app_icon = None
        if "Id" in xbe_info:
            app_icon = "E:\\UDATA\\"+xbe_info["Id"]+"\\TitleImage.xbx"
            launch_node.set("ID", xbe_info["Id"])
        if "Region" in xbe_info:
            launch_node.set("Region", str(xbe_info["Region"]))
        
        launch_node.set("Action", xbe_filename)

        if PREFFERED_ICON_FILE:
            nicer_icon = os.path.join(app_directory, PREFFERED_ICON_FILE)
            if os.path.isfile(nicer_icon):
                app_icon = nicer_icon
        
        resources = os.path.join(app_directory,"_resources")
        if os.path.isdir(resources):            
            preview_dir = os.path.join(resources,"media")
            if os.path.isdir(preview_dir):
                try:
                    video = next(x for x in os.listdir(preview_dir) if x.split(".")[-1] in ["xmv", "wmv"])
                    video_file = os.path.join(preview_dir, video)
                    if CREATE_PREVIEW_VIDEO_ITEM:
                        create_file_manager_button(app_menu_node, "Preview", preview_dir, PLAY_ICON, button_preview_video = video_file)
                    if VIDEO_PREVIEW_ON_PLAY_BUTTON:
                        launch_node.set("Preview", video_file)
                    if VIDEO_PREVIEW_ON_APP_MENU_BUTTON:
                        app_menu_node.set("Preview", video_file)
                except:
                    pass
            
            synopsis_filename = os.path.join(resources,"default.xml")
            process_synopsis_file(app_menu_node, synopsis_filename, DESCRIPTION_ICON, FEATURES_ICON)

            if CREATE_SCREENSHOTS_FOLDER:
                screenshots_dir = os.path.join(resources, "screenshots")
                create_images_folder_if_non_empty(app_menu_node, "Screenshots", screenshots_dir)

            if CREATE_ARTWORK_FOLDER:
                artwork_dir = os.path.join(resources, "artwork")                
                filter_func = lambda img: img.split(os.sep)[-1] not in EXCLUDED_ARTWORK
                create_images_folder_if_non_empty(app_menu_node, "Artwork", artwork_dir, filter_func = filter_func)
            
        if app_icon:
            app_menu_node.set("AltIcon", app_icon)
            launch_node.set("Icon", app_icon)
            if CREATE_TITLE_ITEM:
                title_node.set("Icon", app_icon)


def create_application_synopsis_menu(parent_menu_node, applications_dirs, path, launch_button_name):
    menu_location = "."
    for xml_list in path.split("/"):
        menu_location += "/List[@Text='" + xml_list + "']"

    app_menu = parent_menu_node.find(menu_location)
    if app_menu is None:
        raise ValueError("Path: " + path + " does not exist in the menu!")

    for child in list(app_menu):
        app_menu.remove(child)
    
    for app_directory in applications_dirs:
        apps = [os.path.join(app_directory, di) for di in os.listdir(app_directory) if os.path.isdir(os.path.join(app_directory,di))]
        for app in apps:
            create_app_menu_item(app_menu, app, launch_button_name)

if __name__ == "__main__":
    with open(UNLEASHX_CONFIG_FILENAME) as xml_file:
        # UnleashX leaves a null byte at the end of the file
        # and the XML parser doesn't like this
        xml = xml_file.read().strip("\x00")
    unleashx_config = ET.fromstring(xml)
    unleashx_menu = unleashx_config.find("Menu")

    for menu_item in MENU_ITEMS:
        create_application_synopsis_menu(unleashx_menu,
                                         menu_item["application_directories"],
                                         menu_item["path"],
                                         menu_item["launch_button_name"])
    tree = ET.ElementTree()
    tree._setroot(unleashx_config)
    tree.write(UNLEASHX_CONFIG_FILENAME)

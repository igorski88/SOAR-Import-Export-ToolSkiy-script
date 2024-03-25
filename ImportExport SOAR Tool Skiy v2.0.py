import json
import requests
import re
import os
import platform
import base64

##TODO: If something already exists the user should have an option to overwrite it.
##TODO: Colors for Success or fail msgs
##TODO: Backup All Cases

# Define global variables
username = ""
password = ""
host = "" 
#username = ""
#password = ""
#host = "" 

# Disable certificate warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

def welcome_page():
    print("""
        /////////////////////////////////////////
        /                                       /
        /    -=[ SOAR IMPORT/EXPORT TOOL ]=-    /
        /                                       /
        /        [O_O]    {^_^}    [x_x]        /
        /                                       /
        /        Where Cyber Meets Code         /
        /         A ToolSkiy Production         /
        /////////////////////////////////////////""")


    print("This script will allow you to Export/Import information from a Splunk SOAR(AKA phantom) instance.")
    print()
    input("Continue...... ")

def ask_host_and_creds():
    global username, password, host

    while True:
        username = input("Enter SOAR Admin username: ")
        if not username:
            print("Username cannot be empty.")
            continue

        password = input("Enter SOAR Admin password: ")
        if not password:
            print("Password cannot be empty.")
            continue

        raw_host = input("Enter the host: ")
        validated_host = validate_and_strip(raw_host)

        if validated_host:
            host = validated_host
            return
        else:
            print("Invalid domain or IP address input. Please try again.")

def validate_api_connection():
    while True:
        api_url = f"https://{username}:{password}@{host}/rest/system_info"

        try:
            response = requests.get(api_url, verify=False)
            if response.status_code == 200:
                data = response.json()
                if 'base_url' in data:
                    print(f"Credentials are working. Connection to SOAR instance verified. Base Host URL: {data['base_url']}")
                    return True
            print(f"Connection to SOAR instance not working. Error Code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error: {e}")

        input("Press Enter to try new credentials...")

def submenuCredsCheckandValidation():
    while True:
        if host:
            print(f"Are we still working with this Host --> {host}")
            choice = input("(y/n): ")
            if choice.lower() == 'n':
                ask_host_and_creds()
                if not validate_api_connection():
                    continue
            elif choice.lower() == 'y':
                return
            else:
                print("Invalid choice. Please select y or n.")
        else:
            ask_host_and_creds()
            if not validate_api_connection():
                continue
            else:
                return

def get_data(api_url):
    try:
        response = requests.get(api_url, verify=False)
        if response.status_code == 200:
            return response#.json()
        else:
            print(f"GET request failed with status code {response.status_code}")
            print(f"Error {response.json()}") #Print the Json Error too
            return None
    except requests.RequestException as e:
        print(f"GET request error: {e}")
        return response#.json()

def post_data(api_url, data):
    #data = json.loads(data)
    try:
        response = requests.post(api_url, json=data, verify=False)
        if response.status_code == 200:
            return response.json()
            #print(f"POST request was a success")
        else:
            print(f"POST request failed with status code {response.status_code}")
            responsJSON = response.json()
            print(f"Error Message: {responsJSON['message']}")
            #print(f"Error {response.json()}") #Print the Json Error too
            return None
    except requests.RequestException as e:
        print(f"POST request error: {e}")
        return None

def Delete_data(api_url, data):
    try:
        response = requests.delete(api_url, json=data, verify=False)
        if response.status_code == 200:
            return response.json()
            #print(f"DELETE request was a success")
        else:
            print(f"DELETE request failed with status code {response.status_code}")
            responsJSON = response.json()
            print(f"Error Message: {responsJSON['message']}")
            #print(f"Error {response.json()}") #Print the Json Error too
            return None
    except requests.RequestException as e:
        print(f"DELETE request error: {e}")
        return None


def validate_and_strip(input_string):
    input_string = input_string.strip()

    # Remove http or https if present
    if input_string.startswith("https://"):
        input_string = input_string[len("https://"):]
    elif input_string.startswith("http://"):
        input_string = input_string[len("http://"):]

    # Check for localhost
    if input_string == "localhost":
        return input_string

    # Check for valid IP address
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ip_pattern, input_string):
        return input_string

    # Validate domain
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(domain_pattern, input_string):
        return input_string
    else:
        return None


def create_file(data, file_name, file_type):
    try:
        # Extract folder name from file_name
        folder_name = file_name.split(" - ")[0]

        # Get the directory where the script is located
        script_directory_ExportParent = os.path.dirname(os.path.abspath(__file__))

        # Create the sub folder if it does not exist
        script_directory_ExportChild = os.path.join(script_directory_ExportParent, "SOAR Export Files")
        if not os.path.exists(script_directory_ExportChild):
            os.makedirs(script_directory_ExportChild)

        # Create the sub folder if it does not exist
        new_folder_path = os.path.join(script_directory_ExportChild, folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        
        file_path = os.path.join(new_folder_path, f"{file_name}{file_type}")
        
        # Save the data to the file in the new folder
        if file_type == ".json":
            with open(file_path, "w") as export_file:
                json.dump(data, export_file, indent=4)
        else:           
            with open(file_path, 'wb') as f:
                f.write(data.content)
        

        print(f"The Export was saved to the following directory: {file_path}")
    except IOError as e:
        print(f"Error saving JSON file: {e}")



def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def RequestSingleWorkbook(WB_Template_ID, WB_Details):
    Cmd = f"workbook_phase_template?_filter_template={WB_Template_ID}"

    # Construct the url for what we are looking for
    api_url = f"https://{username}:{password}@{host}/rest/{Cmd}"
    #api_url = f"https://soar_local_admin:s0aring42@sor-shw-270f21b9e81f49.stg.soar.splunkcloud.com/rest/workbook_phase_template?_filter_template={WB_Template_ID}"

    # Making the GET request
    get_response = (get_data(api_url)).json()
    if get_response:
        if get_response['count'] == 0:
            print(f"Something went wrong. Try confirming that the workbook ID exists") 

        else:           

            #Create the File name
            if WB_Details:                
                WB_Template_Name = WB_Details['name']
                WB_Template_isdefault = WB_Details['is_default']
                WB_Template_Description = WB_Details['description']
                WB_Template_isnoterequired = WB_Details['is_note_required']

                FileName = f"workbook_template_export - {WB_Template_Name}"                
            else: #if no name exists then go grab one
                Cmd = f"workbook_template?_filter_id={WB_Template_ID}"                 
                api_url = f"https://{username}:{password}@{host}/rest/{Cmd}" # Construct the url for what we are looking for
                get_workbookinfo = (get_data(api_url)).json() # Making the GET request
                #print(f"Raw Data: {get_workbookinfo['data']}")
                #print(f"Raw Data: {get_response['data']}")
                WB_Template_Name = get_workbookinfo['data'][0]['name']
                WB_Template_isdefault = get_workbookinfo['data'][0]['is_default']
                WB_Template_Description = get_workbookinfo['data'][0]['description']
                WB_Template_isnoterequired = get_workbookinfo['data'][0]['is_note_required']
                FileName = f"workbook_template_export - {WB_Template_Name}"

            response = f"{get_response['count']} Phases where exported from WorkBook ID - {WB_Template_ID}: {WB_Template_Name}"

            # Add 'name' and is_default to the begining of the json to store
            get_response = {'name': WB_Template_Name, 
                'is_default': WB_Template_isdefault, 
                'description': WB_Template_Description, 
                'is_note_required': WB_Template_isnoterequired,
                **get_response}

            #print(f"Raw Data after changes: {get_response}")

            create_file(get_response, FileName, ".json") #Last perameter is file type
            return response

def RequestAllSpecificData(Cmd, DataType, KeyWordForName):
    # Construct the url for what we are looking for
    api_url = f"https://{username}:{password}@{host}/rest/{Cmd}"

    # Making the GET request
    get_response = (get_data(api_url)).json()

    #print(f"Raw Data - for {DataType}: {get_response}") 

    if get_response:
        isResponseHaveValues = is_valid_json_With_Values(get_response)
        ResultCount = get_response.get("count", "") #Get the Key named 'count' or return "" if one doesnt exist. This ensures nothing breaks
        if isResponseHaveValues and ResultCount == 0:
            print(f"No {DataType} data found to import.") 
            print(f"Return string: {get_response}")
            input("Continue.....")
        elif isResponseHaveValues and ResultCount == "": #In the case that thier is no count in the JSON string so we save it all as one file
            print(f" ~~~~{DataType}s found~~~~ ")
            FileName = f"{DataType}_export - All in one"
            if get_response.get(KeyWordForName, ""): #Only get the data you need if it is available.
                get_response = {KeyWordForName: get_response[KeyWordForName]} #This helps us retain the key with the values instead of just the values
            create_file(get_response, FileName, ".json") #Last perameter is file type               
            input("Continue.....")   
        elif isResponseHaveValues and ResultCount != 0:

            dataItems = [item for item in get_response['data']]
            print(f" ~~~~{DataType}s found~~~~ ")

            for Eachitem in dataItems:
                print(f"{DataType}: {Eachitem[KeyWordForName]}")
                JsonToStore = Eachitem
                FileName = f"{DataType}_export - {Eachitem[KeyWordForName]}"
                create_file(JsonToStore, FileName, ".json") #Last perameter is file type               

                print("-----------------------------------------------")

            input("Continue.....")     
        else:
            print(f"Something went wrong getting all the available data for - {DataType}.") 
            print(f"Looks like Valid a VALID JSON string was not returned") 
            print(f"Error String: {get_response}")   
            input("Continue.....")       

def Export_Playbooks_and_CustomFunctions(Cmd, DataType):
    # Construct the url 
    api_url = f"https://{username}:{password}@{host}/rest/{Cmd}"

    # Making the GET request to get all IDs first
    get_response = (get_data(api_url)).json()

    #print(f"Raw Data - for {DataType}: {get_response}") 

    if get_response:
        ResultCount = get_response.get("count", "") #Get the Key named 'count' or return "" if one doesnt exist. This ensures nothing breaks
        if ResultCount == 0:
            print(f"Something went wrong getting all the available data for - {DataType}.") 
            print(f"Error String: {get_response}")
            input("Continue.....")
        else:
            dataItems = [item for item in get_response['data']]
            print(f" ~~~~{DataType}s found~~~~ ")

            for Eachitem_Json in dataItems:
                id = Eachitem_Json['id']
                print(f"{DataType}: {Eachitem_Json['name']} - ID:{id}")
                #print(f"Raw: {Eachitem_Json}")                
                FileNameTGZ = f"{DataType}_export - {Eachitem_Json['name']}"
                FileNameRawText = f"{DataType}_export - {Eachitem_Json['name']}"
                Cmd = f"{DataType}/{id}/export"
                #Cmd = f"custom_function/1/export"
                # Construct the url 
                api_url = f"https://{username}:{password}@{host}/rest/{Cmd}"

                # Making the GET request to get all IDs first
                get_response = get_data(api_url)
                #print(f"Raw TGZ: {get_response.content}")
                create_file(get_response, FileNameTGZ, ".tgz") #Last perameter is file type    
                #create_file(get_response, FileNameRawText, ".txt") #Last perameter is file type               

                print("-----------------------------------------------")

            input("Continue.....")     


def RequestAllWorkbooks():
    #This will only grab all the workbook template names and IDs
    #This info is then passed to the RequestSingleWorkbook() where only IDs are used

    #Grab all the Available workbook IDs first
    Cmd = "workbook_template?page_size=0" # page zero indicates all pages Refrence: https://docs.splunk.com/Documentation/SOARonprem/6.1.1/PlatformAPI/RESTQueryData

    # Construct the url for what we are looking for
    api_url = f"https://{username}:{password}@{host}/rest/{Cmd}"

    # Making the GET request
    get_response = (get_data(api_url)).json()

    if get_response:
        if get_response['count'] == 0:
            print(f"Something went wrong getting all the available workbook templates.") 
            print(f"Error String: {get_response}")
            input("Continue.....")

        else:
            #print(f"Raw Data: {get_response['data']}")
            Workbook_list = [item for item in get_response['data']]
            id_list = [item['id'] for item in get_response['data']] #Get a list of all availble IDs
            print(f" ~~~~Workbook Templates found~~~~ ")
            name_list = [item['name'] for item in get_response['data']]

            for worbook in Workbook_list:
                print(f"Imported Workbook template: {worbook['name']}")
                #print(f"Raw Data: {worbook}")
                RequestSingleWorkbook(worbook['id'], worbook) 
                print(f"-----------------------------------------------")



        response = f"Found and imported {len(id_list)} Workbook Templates"
        return response 



def export_submenu():
    submenuCredsCheckandValidation()
    print("Export Menu:")
    print("0. Export All below")
    print("1. Export Workbook Templates")
    print("2. Export Users, Roles, & Permissions")
    print("3. Export Case Severity")
    print("4. Export CEFs")
    print("5. Export Container Status")  
    print("6. Export Labels")
    print("7. Export Tags")
    print("8. Export Hud (aka Pin)")
    print("9. Export Playbooks")
    print("10. Export Custom Functions") 
    print("11. Export System Settings") #Not fully tested
    #print("12. Export Cases") ## Future implementation

    
    
    choice = input("Enter your choice: ")
    clear_console()
    if choice == "0":
        Options_ExportWorkbooks()            

        Option_ExportAllUsersAndRoles()

        print("Exporting Severitys...")
        Cmd = "severity?page_size=0"
        RequestAllSpecificData(Cmd, "severity", "name") #command, DataType, Keyword for name

        print("Exporting CEFs...") 
        Cmd = "cef?_filter_type=\"custom\"&page_size=0"
        RequestAllSpecificData(Cmd, "cef", "name") #command, DataType, Keyword for name

        print("Exporting Case Statuses...")
        Cmd = "container_status?page_size=0" # page zero indicates all pages Refrence: https://docs.splunk.com/Documentation/SOARonprem/6.1.1/PlatformAPI/RESTQueryData
        RequestAllSpecificData(Cmd, "container_status", "name") #command, DataType, Keyword for name

        print("Exporting Labels...") ##TODO Will need to be done by pulling Container_Options
        Cmd = "container_options/label"
        RequestAllSpecificData(Cmd, "label", "label") #command, DataType, Keyword for name

        print("Exporting Tags...") ##TODO Will need to be done by pulling Container_Options - Importing will need a container created then deleted.
        Cmd = "container_options/tags"
        RequestAllSpecificData(Cmd, "tags", "tags") #command, DataType, Keyword for name
 
        print("Exporting HUD...") 
        Cmd = "container_pin_settings?page_size=0"
        RequestAllSpecificData(Cmd, "HUD", "id") #command, DataType, Keyword for name

        print("Exporting Playbooks...")        
        Cmd = "playbook?page_size=0"
        Export_Playbooks_and_CustomFunctions(Cmd, "playbook") #command, DataType

        print("Exporting Custom Functions...")
        Cmd = "custom_function?page_size=0"
        Export_Playbooks_and_CustomFunctions(Cmd, "custom_function")

        print("Exporting all other settings ...") 
        Cmd = "system_settings"
        RequestAllSpecificData(Cmd, "system_settings", "name") #command, DataType, Keyword for name
        
        print("Exporting Container Options...") 
        Cmd = "container_options"
        RequestAllSpecificData(Cmd, "container_options", "") #command, DataType, Keyword for name
        
    elif choice == "1":
        Options_ExportWorkbooks()            
    elif choice == "2":
        Option_ExportAllUsersAndRoles()
    elif choice == "3":
        print("Exporting Severitys...")
        Cmd = "severity?page_size=0"
        RequestAllSpecificData(Cmd, "severity", "name") #command, DataType, Keyword for name
    elif choice == "4":
        print("Exporting CEFs...") 
        Cmd = "cef?_filter_type=\"custom\"&page_size=0"
        RequestAllSpecificData(Cmd, "cef", "name") #command, DataType, Keyword for name
    elif choice == "5":
        print("Exporting Case Statuses...")
        Cmd = "container_status?page_size=0" # page zero indicates all pages Refrence: https://docs.splunk.com/Documentation/SOARonprem/6.1.1/PlatformAPI/RESTQueryData
        RequestAllSpecificData(Cmd, "container_status", "name") #command, DataType, Keyword for name
    elif choice == "6":
        print("Exporting Labels...") ##TODO Will need to be done by pulling Container_Options
        Cmd = "container_options/label"
        RequestAllSpecificData(Cmd, "label", "label") #command, DataType, Keyword for name
    elif choice == "7":
        print("Exporting Tags...") ##TODO Will need to be done by pulling Container_Options - Importing will need a container created then deleted.
        Cmd = "container_options/tags"
        RequestAllSpecificData(Cmd, "tags", "tags") #command, DataType, Keyword for name
    elif choice == "8":
        print("Exporting HUD...") 
        Cmd = "container_pin_settings?page_size=0"
        RequestAllSpecificData(Cmd, "HUD", "id") #command, DataType, Keyword for name
    elif choice == "9":
        print("Exporting Playbooks...")        
        Cmd = "playbook?page_size=0"
        Export_Playbooks_and_CustomFunctions(Cmd, "playbook") #command, DataType
    elif choice == "10":
        print("Exporting Custom Functions...")
        Cmd = "custom_function?page_size=0"
        Export_Playbooks_and_CustomFunctions(Cmd, "custom_function") 
    elif choice == "11":
        print("Exporting all other settings ...") 
        Cmd = "system_settings"
        RequestAllSpecificData(Cmd, "system_settings", "name") #command, DataType, Keyword for name
        
        print("Exporting Container Options...") 
        Cmd = "container_options"
        RequestAllSpecificData(Cmd, "container_options", "") #command, DataType, Keyword for name
    #elif choice == "12": ##TODO: Future Implementation       
        #print("Exporting Custome Fields...") 
        #Cmd = "cef?_filter_type=\"custom\"&page_size=0"
        #RequestAllSpecificData(Cmd, "cef", "name") #command, DataType, Keyword for name
    #elif choice == "13": ##TODO: Future Implementation
        #print("Exporting a BACKUP of All Cases...")
        #Maybe this will be created in the future
        #Cmd = "severity?page_size=0"
        #RequestAllSpecificData(Cmd, "severity", "name") #command, DataType, Keyword for name
    else:
        print("Invalid choice. Please select a valid option.")

def Options_ExportWorkbooks():
    print("Ok, Lets Export the Workbook Templates...")
    WB_Template_Response = input("Enter the WorkBook Template ID (or 'all'): ")

    if WB_Template_Response.lower() == "all":
        response = RequestAllWorkbooks()
        print(f"{response}")
        input("Continue.....")
    elif is_number(WB_Template_Response):
        response = RequestSingleWorkbook(WB_Template_Response, "")
        print(f"{response}")
        input("Continue.....")

def Option_ExportAllUsersAndRoles():
    print("Exporting all User Roles & Permissions...")

    #Users
    Cmd = "ph_user?page_size=0" # page zero indicates all pages Refrence: https://docs.splunk.com/Documentation/SOARonprem/6.1.1/PlatformAPI/RESTQueryData
    RequestAllSpecificData(Cmd, "user", "username") #command, DataType, Keyword for name

    #Roles
    Cmd = "role?page_size=0" # page zero indicates all pages Refrence: https://docs.splunk.com/Documentation/SOARonprem/6.1.1/PlatformAPI/RESTQueryData
    RequestAllSpecificData(Cmd, "role", "name") #command, DataType, Keyword for name

def InputPassword():
    print(f"--------------------------------------")
    print(f"A password is required for the username(s) you are trying to import")
    print(f"Passwords must have at least  8 total characters.")
    print(f"Leave password blank to use default --> 'password'")
    SelectedPassword =  input("Password:")
    if SelectedPassword:
        return SelectedPassword
    else:
        return "password" #default
     

def Import_File(SearchKeyword, _ImportAll):
    # Get the directory where the script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    while True:

        found_files = find_files_to_import(SearchKeyword, current_directory)

        if not found_files:
            print(f"No files with '{SearchKeyword}' in the title found in the current directory.")
            change_directory = input("Enter a different directory to search or press Enter to exit: ")
            # This ensures that a new directory was typed in
            if change_directory:
                current_directory = change_directory
                continue
            return

        if _ImportAll:
            selected_file = found_files
        else:
            selected_file = select_file_from_list(found_files)

        #If importing user then prompt for a password(required). 
        if SearchKeyword == "user_export":            
            SelectedPassword = InputPassword()
            
        if selected_file:                    
            for _file in selected_file:
                print(f"You selected '{_file}' to be imported.")
                # Convert the file we exported previously into an import JSON Format
                with open(f'{_file}', 'r') as raw_file:
                    # Parse the JSON data into a Python dictionary
                    
                    
                    if SearchKeyword == "workbook_template_export":
                        RAW_JSONdata = json.load(raw_file)
                        output_json = convert_exported_workbook_into_importable_workbook_JSON(RAW_JSONdata)
                        api_url = f"https://{username}:{password}@{host}/rest/workbook_template"
                        response = post_data(api_url, output_json)
                    elif SearchKeyword == "user_export":
                        RAW_JSONdata = json.load(raw_file)
                        RAW_JSONdata["password"] = SelectedPassword #Passwords must have at least  8 total characters
                        api_url = f"https://{username}:{password}@{host}/rest/ph_user"
                        response = post_data(api_url, RAW_JSONdata)
                    elif SearchKeyword == "role_export":
                        RAW_JSONdata = json.load(raw_file)
                        api_url = f"https://{username}:{password}@{host}/rest/role"
                        response = post_data(api_url, RAW_JSONdata)
                    elif SearchKeyword == "severity_export":
                        RAW_JSONdata = json.load(raw_file)
                        del RAW_JSONdata['disabled'] #required to delete b/c this cannot be set via API
                        api_url = f"https://{username}:{password}@{host}/rest/severity"
                        response = post_data(api_url, RAW_JSONdata)
                    elif SearchKeyword == "cef_export":
                        RAW_JSONdata = json.load(raw_file)
                        api_url = f"https://{username}:{password}@{host}/rest/cef"  
                        response = post_data(api_url, RAW_JSONdata)   
                    elif SearchKeyword == "container_status_export":
                        RAW_JSONdata = json.load(raw_file)
                        del RAW_JSONdata['disabled'] #required to delete b/c this cannot be set via API
                        api_url = f"https://{username}:{password}@{host}/rest/container_status"
                        response = post_data(api_url, RAW_JSONdata)
                    elif SearchKeyword == "label_export": 
                        RAW_JSONdata = json.load(raw_file)                                                  
                        api_url = f"https://{username}:{password}@{host}/rest/system_settings/events"
                        for _label in RAW_JSONdata['label']:
                            #output_json = {"add_label": "true", "label_name": _label}  
                            output_json = {"add_tag": "true", "tag_name": _label}                               
                            response = post_data(api_url, output_json) 
                            if response:      
                                print(response)                        
                                if response.get('success'): #if 'Success' is found it returnes the Keys value
                                     print(f"You Successfully imported label: '{_label}'.")
                                else:
                                    print(f"NOT Successfull importing label: '{_label}'. Error: {response['message']}") 
                            response = None #Reset
                    elif SearchKeyword == "tags_export": #we will have to create a container --> add the tags --> delete the container 
                        RAW_JSONdata = json.load(raw_file)
                        api_url = f"https://{username}:{password}@{host}/rest/container"
                        output_json = {"name": "Temp Case Used to Create Tags", "label": "events", "tags": RAW_JSONdata['tags']}                               
                        response = post_data(api_url, output_json)
                        List = []
                        List.append(response['id'])
                        Delete_json = {"ids": List}                        
                        response = Delete_data(api_url, Delete_json)   
                        response = response[0] ## It returned a list so convert it back to a string                
                    elif SearchKeyword == "HUD_export": ## Hud 
                        RAW_JSONdata = json.load(raw_file)
                        api_url = f"https://{username}:{password}@{host}/rest/container_pin_settings"    
                        response = post_data(api_url, RAW_JSONdata)  
                    elif SearchKeyword == "system_settings_export": 
                        RAW_JSONdata = json.load(raw_file) 
                        api_url = f"https://{username}:{password}@{host}/rest/system_settings"    
                        response = post_data(api_url, RAW_JSONdata)
                    elif SearchKeyword == "playbook_export":                          
                        with open(f'{_file}', 'rb') as raw_b_file:                             
                            RAW_data = raw_b_file.read()
                            encoded_text = base64.b64encode(RAW_data).decode('utf-8')
                            output_json = {"playbook": encoded_text, "scm": "local", "force": True} ##Future Implementation to ask the user to force or not                       
                            api_url = f"https://{username}:{password}@{host}/rest/import_playbook"    
                            response = post_data(api_url, output_json)
                    elif SearchKeyword == "custom_function_export":  
                        with open(f'{_file}', 'rb') as raw_b_file:                             
                            RAW_data = raw_b_file.read()
                            encoded_text = base64.b64encode(RAW_data).decode('utf-8')
                            output_json = {"custom_function": encoded_text, "scm": "local", "force": True} ##Future Implementation to ask the user to force or not                       
                            api_url = f"https://{username}:{password}@{host}/rest/import_custom_function"    
                            response = post_data(api_url, output_json)
                    else:
                        print(f"Something went wrong.... Error 2235  <-- This code is made up but non the less something broke.")
                        break
                                         
                                        
                    if response:
                        print(response)
                        if response.get('success'): #if 'Success' is found it returnes the Keys value
                            print(f"You Successfully imported '{_file}'.")
                        else:
                            print(f"NOT Successfull importing label: '{_file}'. Error: {response['message']}")
            return
        else:
            new_location = input("Enter a different file location or press Enter to exit: ")
            if new_location:
                current_directory = new_location
                print(f"You chose to work with '{new_location}'.")
                continue
            return

def import_submenu():
    submenuCredsCheckandValidation()
    clear_console()
    print("Import Menu:")
    print("0. Import All of the Above")
    print("1. Import Workbook Templates")
    print("2. Import Users, Roles, & Permissions")
    print("3. Import Case Severity")
    print("4. Import CEFs")
    print("5. Import Container Status")  
    print("6. Import Labels")
    print("7. Import Tags")
    print("8. Import Hud (aka Pin)")
    print("9. Import Playbooks")
    print("10. Import Custom Functions") 
    print("11. Import System Settings") #Not fully tested
    #print("12. Import Cases") ## Future implementation
    
    choice = input("Enter your choice: ")
    clear_console()
    if choice == "0":
        print("Importing All of the Above...")
        
        print("Importing Workbook Template...")        
        Import_File("workbook_template_export", True) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Workbook Templates - Continue.....?")
        
        print("Importing User Roles & Permissions...")
        Import_File("user_export", True) 
        Import_File("role_export", True)  
        input("Completed Importing User Roles & Permissions - Continue.....?")
        
        print("Importing Case severity...")
        Import_File("severity_export", True)
        input("Completed Importing Case severities - Continue.....?")
        
        print("Importing CEFs...")
        Import_File("cef_export", True)
        input("Completed Importing CEFs - Continue.....?")
        
        print("Importing Container Status...")
        Import_File("container_status_export", True)
        input("Completed Importing Container Status - Continue.....?")
        
        print("Importing Labels...")
        Import_File("label_export", True)
        input("Completed Importing Labels - Continue.....?")
        
        print("Importing Tags...")
        Import_File("tags_export", True)
        input("Completed Importing Tags - Continue.....?")
        
        print("Importing HUD (AKA Pin)...")
        Import_File("HUD_export", True)
        input("Completed Importing HUD (AKA Pin) - Continue.....?")
        
        print("Importing Playbooks...")
        Import_File("playbook_export", True)
        input("Completed Importing Playbooks - Continue.....?")
        
        print("Importing Custom Functions...")
        Import_File("custom_function_export", True)
        input("Completed Importing Custom Functions - Continue.....?")
        
        print("Importing System Settings...")
        Import_File("system_settings_export", True)
        input("Completed Importing System Settings - Continue.....?")
        
        # Add import logic for all items here
    elif choice == "1":
        print("Importing Workbook Template...")        
        Import_File("workbook_template_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Workbook Templates - Continue.....?")
    elif choice == "2":
        print("Importing User Roles & Permissions...")
        Import_File("user_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        Import_File("role_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.        
        input("Completed Importing User Roles & Permissions - Continue.....?")
        # Add import logic for User Roles & Permissions here
    elif choice == "3": 
        print("Importing Case severity...")
        Import_File("severity_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Case severity - Continue.....?")
    elif choice == "4":    
        print("Importing CEFs...")
        Import_File("cef_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing CEFs - Continue.....?")
    elif choice == "5":    
        print("Importing Container Status...")
        Import_File("container_status_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Container Status - Continue.....?")
    elif choice == "6": 
        print("Importing Labels...")
        Import_File("label_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Labels - Continue.....?")
    elif choice == "7": 
        print("Importing Tags...")
        Import_File("tags_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Tags - Continue.....?")
    elif choice == "8": 
        print("Importing HUD (AKA Pin)...")
        Import_File("HUD_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing HUD (AKA Pin) - Continue.....?")
    elif choice == "9": 
        print("Importing Playbooks...")
        Import_File("playbook_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Playbooks - Continue.....?")
    elif choice == "10": 
        print("Importing Custom Functions...")
        Import_File("custom_function_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Custom Functions - Continue.....?")  
    elif choice == "11": ## Future implementation
        print("Importing System Settings...")
        Import_File("system_settings_export", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing System Settings - Continue.....?")  
    elif choice == "12": ## Future implementation
        print("Importing Cases...")
        Import_File("XXXXX", False) #The Last Perameter is for 'Import_All'? False allows to pik one file at a time.
        input("Completed Importing Cases - Continue.....?")    
 
    
    else:
        print("Invalid choice. Please select a valid option.")


def main_menu():
    while True:
        clear_console()
        print("Main Menu:")
        print("1. Export")
        print("2. Import")
        print("3. Exit")
        choice = input("Enter your choice: ")
        clear_console()

        if choice == "1":
            export_submenu()
        elif choice == "2":
            import_submenu()
        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

def find_files_to_import(Search_Keyword, directory):
    # Initialize a list to store matching file paths
    matching_files = []

    # Recursively search for matching files in subdirectories
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.startswith(Search_Keyword):
                # Construct the full path to the matching file
                file_path = os.path.join(root, filename)
                matching_files.append(file_path)

    return matching_files


    #json_files = glob.glob(os.path.join(directory, f"*{type}*.json"))
    #return json_files

def is_valid_json_With_Values(data):
    return isinstance(data, dict) and len(data) >= 1

def clear_console():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def select_file_from_list(file_list):
    print("Select a JSON file to work with:")
    for i, file_path in enumerate(file_list):
        print(f"{i + 1}: {os.path.basename(file_path)}")

    while True:
        #try:
            choice = input("Enter the number of your choice ('0' to select diffrent file location | or select 'all'): ")
            if choice.lower() == 'all':
                return file_list
            elif 0 <= int(choice) <= len(file_list):
                choice = int(choice)
                file_list_dic = []
                file_list_dic.append(file_list[choice - 1])
                return file_list_dic if choice > 0 else None
            else:
                print("Invalid choice. Please enter a valid number or the 'all'.")
        #except ValueError:
            #print("Invalid choice. Please enter a valid number or the 'all'.")

def convert_exported_workbook_into_importable_workbook_JSON(input_json):

    # Parse the input JSON
    data = input_json

    Template_name = data["name"]
    Template_isdefault = data["is_default"]
    Template_description = data["description"] 
    Template_isnoterequired = data["is_note_required"]

    # Initialize the output structure
    output_data = {
        "name": Template_name,
        "description": Template_description,
        "is_default": Template_isdefault,
        "is_note_required": Template_isnoterequired,
        "phases": []
    }

    # Loop through the phases in the input JSON and transform them
    for phase in data["data"]:
        phase_name = phase["name"]
        phase_order = phase["order"]
        phase_tasks = phase["tasks"]
        phase_sla = phase["sla"]
        phase_sla_type = phase["sla_type"]


        # Initialize the phase structure for the output
        phase_data = {
            "name": phase_name,
            "order": phase_order,
            "sla": phase_sla,
            "sla_type": phase_sla_type,
            "tasks": []
        }

        # Loop through the tasks in the phase and transform them
        for task in phase_tasks:
            task_name = task["name"]
            task_order = task["order"]
            task_description = task["description"]
            task_owner = task["owner"]
            task_role = task["role"]
            task_is_note_required = task["is_note_required"]
            task_sla = task["sla"]
            task_sla_type = task["sla_type"]
            task_suggestions = task["suggestions"]
            task_actions = task_suggestions.get("actions", [])
            task_playbooks = task_suggestions.get("playbooks", [])


            # Initialize the task structure for the output
            task_data = {
                "name": task_name,
                "order": task_order,
                "description": task_description,
                "owner": task_owner,
                "role": task_role,
                "is_note_required": task_is_note_required,
                "sla": task_sla,
                "sla_type": task_sla_type                
            }

            #only add it if there are actions
            if task_actions:
                task_data["actions"] = task_actions

            #only add it if there are playbooks
            if task_playbooks:
                playbooksList = []
                # Loop through the task playbooks
                for playbook in task_playbooks:
                    playbook_scm = playbook["scm"]
                    playbook_name = playbook["playbook"]

                    # Initialize the playbook structure for the output
                    playbook_data = {
                        "scm": playbook_scm,
                        "playbook": playbook_name
                    }

                    # Add the task to the phase
                    playbooksList.append(playbook_data)
                    task_data["playbooks"] = playbooksList

            # Add the task to the phase
            phase_data["tasks"].append(task_data)

        # Add the phase to the output
        output_data["phases"].append(phase_data)

    # Convert the output data to JSON format
    output_json = output_data #json.loads(output_data)
    #print("File successfully converted to readable input file!")
    #print(output_json)
    return output_json


if __name__ == "__main__":
    welcome_page()  # Display the welcome message
    main_menu()

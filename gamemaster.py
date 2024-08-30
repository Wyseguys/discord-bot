

class GameMaster:
    """GameMaster is meant to track all the text manipulation before it goes to the LLM"""
    def __init__(self, name):
        self.name = name


    @classmethod
    def load_main_system_role(self):
        """
        Loads and returns the contents of the main instruction text file. The main instructions should
        probably only be given to the LLM at the start of the session
        """ 
        try:
            with open("gm_instructions/main_system_role_info.txt", "r") as f:
                return f.read()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None



    @classmethod
    def load_reminder_system_role(self):
        """
        Loads and returns the contents of the reminder instruction text file. This is given every time
        the main instructions are not. It is meant to give the LLM reminders to stay on course
        """ 
        try:
            with open("gm_instructions/reminder_system_role_info.txt", "r") as f:
                return f.read()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    @classmethod
    def prepare_message(self, discord_message, message_content) -> str:
        """
        Look for the "!" symbol, which will be an instruction to the GM. Everything else needs to be
        wrapped in ``` marks and labeled as to which discord user is saying it to the DM. This will
        probably make it easier for the LLM to keep who's who clear.
        """
        # Check if the message starts with a specific prefix for DM commands
        message_content = message_content.strip()
        if message_content.startswith('!'):
            player_action = message_content[len('!'):] #! means it is a DM command, not part of the story
        else:
            #Wrap the action in ``` because there will be a directive to tell the bot that it is a player action
            player_action = "```" + discord_message.author.name + " says \""  + message_content + "\"```"

        return player_action
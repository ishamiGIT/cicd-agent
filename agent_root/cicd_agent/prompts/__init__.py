import logging

# You can also get a specific logger instance
logger = logging.getLogger(__name__)

# 2. Initialize a single global dictionary to hold all prompts.
PROMPTS = {}

# 3. Define which files to load into which keys in the dictionary.
FILES_TO_LOAD = {
    'ROOT_PROMPT': 'agent/prompts/root.md',
    'CLOUD_BUILD_PROMPT': 'agent/prompts/cloud_build.md',
    'DESIGN_PROMPT': 'agent/prompts/design.md',
}

def load_prompts_into_dict(target_dict, files_map):
    """
    Reads from files and populates a single dictionary.
    """
    for key, filename in files_map.items():
        try:
            with open(filename, 'r') as f:
                target_dict[key] = f.read().strip()
                logger.info(f"Loaded '{filename}' into PROMPTS['{key}'].")
        except FileNotFoundError:
            target_dict[key] = None
            logger.error(f"File '{filename}' not found.", exc_info=True)

load_prompts_into_dict(PROMPTS, FILES_TO_LOAD)

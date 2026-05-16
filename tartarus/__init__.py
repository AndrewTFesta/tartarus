"""
@title

__init__.py

@description

Common paths and attributes used by and for this project.

"""
import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
# --------------------------------------------
# Project versioning and attributes
# --------------------------------------------
name = 'tartarus'
timezone = 'EST'
env_tag = os.environ.get('ENV', 'nonprod')

# --------------------------------------------
# Base paths for relative pathing to the project base
# --------------------------------------------
source_package = Path(__file__).parent
project_path = Path(os.environ.get('PROJECT_PATH', source_package.parent))

# --------------------------------------------
# Development and source directories
# --------------------------------------------
script_dir = Path(os.environ.get('SCRIPT_DIR', project_path / 'scripts'))
notebook_dir = Path(os.environ.get('NOTEBOOK_DIR', project_path / 'nb'))
execs_dir = Path(os.environ.get('EXECS_DIR', project_path / 'execs'))

# --------------------------------------------
# Paths to store assets and related resources
# --------------------------------------------
resources_dir = Path(os.environ.get('RESOURCES_DIR', project_path / 'resources'))
data_dir = Path(os.environ.get('DATA_DIR', project_path / 'data'))
prompt_dir = Path(os.environ.get('PROMPTS_DIR', project_path / 'prompts'))
docs_dir = Path(os.environ.get('DOCS_DIR', project_path / 'docs'))
model_dir = Path(os.environ.get('MODEL_DIR', project_path / 'models'))
tmp_dir = Path(os.environ.get('TMP_DIR', Path(project_path, 'tmp')))

# --------------------------------------------
# Paths to static assets
# --------------------------------------------
template_dir = Path(os.environ.get('TEMPLATE_DIR', project_path / 'templates'))
static_dir = Path(os.environ.get('STATIC_DIR', project_path / 'static'))
images_dir = Path(os.environ.get('IMAGES_DIR', static_dir / 'images'))
css_dir = Path(os.environ.get('CSS_DIR', static_dir / 'css'))
js_dir = Path(os.environ.get('JS_DIR', static_dir / 'js'))

# --------------------------------------------
# Output directories
# Directories to programs outputs and generated artefacts
# --------------------------------------------
log_dir = Path(os.environ.get('LOG_DIR', project_path / 'logs'))
output_dir = Path(os.environ.get('OUTPUT_DIR', project_path / 'output'))
exps_dir = Path(os.environ.get('EXPS_DIR', output_dir / 'exps'))
profile_dir = Path(os.environ.get('PROFILE_DIR', output_dir / 'profile'))

# --------------------------------------------
# Cached directories
# Used for caching intermittent and temporary states or information
# to aid in computational efficiency
# no guarantee that a cached dir will exist between runs
# --------------------------------------------
cached_dir = Path(os.environ.get('CACHED_DIR', project_path / 'cached'))

# --------------------------------------------
# Test directories
# Directories to store test code and resources
# --------------------------------------------
test_dir = Path(os.environ.get('TEST_DIR', project_path / 'test'))
test_config_dir = Path(os.environ.get('TEST_CONFIG_DIR', test_dir / 'config'))

# --------------------------------------------
# Resource files
# paths to specific resource and configuration files
# --------------------------------------------
config_dir = Path(os.environ.get('CONFIG_DIR', project_path / 'configs'))
creds_dir = Path(os.environ.get('CREDS_DIR', Path(project_path / 'creds')))
env_dir = Path(os.environ.get('ENV_DIR', project_path / 'envs'))
secrets_dir = Path(os.environ.get('SECRETS_DIR', project_path / 'secrets'))

# --------------------------------------------
# Useful properties and values about the runtime environment
# --------------------------------------------
TERMINAL_COLUMNS, TERMINAL_ROWS = shutil.get_terminal_size()
os.environ['HF_HOME'] = str(model_dir)

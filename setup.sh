# Automates the setup of a virtual environment on Ubuntu:
#   - Updates/installs packages
#   - Creates a virtual environment
#   - Installs necessary modules

set -euo pipefail  # Exit on error, undefined variable, or error in a pipeline. 
# The command and options help catch errors early and prevent a script from continuing when 
# something unexpected happens.


########################################
# 1) Update & Install System Packages  #
########################################
echo "==> Updating apt package list and upgrading existing packages..."
sudo apt update -y
sudo apt upgrade -y
sudo apt autoremove

echo "==> Installing Python3, pip, venv, and nginx..."
sudo apt install -y python3 python3-pip python3-venv


#############################
# 2) Define Your Variables  #
#############################
# Adjust these variables as needed!

# The user who owns the workspace directory
# (Typically your Ubuntu user, e.g., ubuntu for AWS)
USER_NAME="$(whoami)"

# Directory to store your virtual environment, change this as needed!
DIR_WORKSPACE="/home/${USER_NAME}/.GitHub/CSCI 8920/Project Datasets/jira_issue"

# Name of the virtual environment folder
VENV_NAME=".env"

echo "==> Configuring environment variables..."
# You can optionally append these to ~/.bashrc so they're available in future shells:
{
  echo ""
  echo "# [Virtual Environment] Variables"
  echo "export VENV_NAME=\"$VENV_NAME\""
} >> "${HOME}/.bashrc"


#############################################
# 3) Create Workspace & Python Virtual Env  #
#############################################
echo "==> Creating workspace directory at $DIR_WORKSPACE..."
mkdir -p "$DIR_WORKSPACE"
cd "$DIR_WORKSPACE"

echo "==> Creating virtual environment ($VENV_NAME)..."
python3 -m venv "$VENV_NAME"

echo "==> Activating virtual environment..."
# Activate in this script. (Note: once this script ends, the venv is deactivated for your shell.)
source "$DIR_WORKSPACE/$VENV_NAME/bin/activate"


######################################
# 4) Install Modules
######################################
echo "==> Upgrading pip and installing modules ..."
python -m pip install --upgrade pip
pip install langdetect
pip install pandas
pip install openai
pip install load_dotenv

#####################
# 5) All Done!
#####################
echo ""
echo "==========================================================="
echo " Setup is complete!"
echo " Location: $DIR_WORKSPACE"
echo " Virtual Env: $DIR_WORKSPACE/$VENV_NAME"
echo " Remember to reload your shell or run 'source ~/.bashrc'"
echo " if you want the environment variables always available."
echo "==========================================================="

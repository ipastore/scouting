# ⚽ Scouting 
A web app to help you scout football players templated with Streamlit.

## Database
Manage your entries in personal excel "data/source_informes.xlsx"

## Image Repo
Cloudinary: please enter your personal API KEY in a new .env as "CLOUDINARY_URL=cloudinary://xxxxxxxxxxxxxxxxxxxxx"

## Video Repo
Youtube links

## Installation

1) Clone Repo

2) Make environment
If you are familiar with conda:

conda env create -f environment.yml
conda activate myenv

If you are familir with pip: 

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

## Run
streamlit run reports_app.py





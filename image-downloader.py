import streamlit as st
import requests
from pathlib import Path
import pandas as pd
import re
import os
import zipfile
import shutil

st.set_page_config(
    page_title="Image Downloader", 
    page_icon="🖖",
)

st.title('Image Downloader')

st.markdown("""
<style>
.stTabs button[role="tab"] {
    width: 50%;
    font-size: 1rem;
}
label {
    font-size: 1rem !important;
}
#MainMenu {
    visibility: hidden;
}
footer {
    visibility: visible;
    text-align: center;
}
footer:after {
    visibility: visible;
    content: " by Milos Kecovic 🖖";
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def zip_images(file_paths, zip_file_name):
    # Create the zip file and add the images
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path)
            os.remove(file_path)
            
def download_images(image_urls, create_subfolders):
    # Initialize the counter
    download_count = 0

    # Create a progress bar
    progress_bar = st.progress(0)

    # Create a "more details" link with an accordion
    expander = st.expander("More details")
    
    file_paths = []
    
    # Download the images
    for i, url in enumerate(image_urls):
        # Extract the file name from the URL
        file_name = url.split('/')[-1]

        # Sanitize the file name to remove any invalid characters
        file_name = re.sub(r'[^\w\s\.]', '', file_name)

        # Extract the folder path from the URL
        folder_path = '/'.join(url.split('/')[:-1])

        # Remove the "https://" prefix from the folder path
        folder_path = folder_path.replace('https://', '')

        # Split the folder path into subfolders
        first_folder = folder_path.split('/', 1)[0]
        subfolders = folder_path.split('/')
        
        # Create the subfolders if they don't exist
        subfolder_path = ''
        if create_subfolders:
            for subfolder in subfolders:
                subfolder_path = Path(subfolder_path, subfolder)
                subfolder_path.mkdir(parents=True, exist_ok=True)
        #else:
        #    subfolder_path = Path(save_location)
                
        # Download the image
        response = requests.get(url)
        
        # Escape the backslashes in the file path
        file_path = str(Path(subfolder_path, file_name)).replace('\\', '\\\\')
        
        # Save the image to the file
        with open(file_path, 'wb') as f:
            f.write(response.content)
            file_paths.append(file_path)
        
        # Increment the counter
        download_count += 1
        
        # Update the progress bar
        progress_bar.progress((i+1) / len(image_urls))
        
        # Add content to the expander
        with expander:
            # Display a message indicating that the image was saved
            st.write(f'`{file_name}` is saved!', markdown=True)
    
    zip_file_name = 'images.zip'        
    zip_images(file_paths, zip_file_name)
    with open(zip_file_name, "rb") as file:
        st.download_button("Download ZIP", file, zip_file_name)
        file.close()
        os.remove(zip_file_name)
        
    try:
        shutil.rmtree(first_folder)
    except FileNotFoundError:
        pass

    return download_count

# Create the tabs
tab1, tab2 = st.tabs(["Paste URLs", "Upload CSV"])

# Define the contents of the tabs
with tab1:
    
    image_urls = st.text_area("Paste image URLs here:", key = "image_urls")
    
    # Add a checkbox to choose whether to create subfolders
    create_subfolders = st.checkbox('Create subfolders based on URL structure', key = "create_subfolders_urls")
    
    placeholder = st.empty()
    btn = placeholder.button("Download Images", disabled=False, key = "button_urls_1")
    if btn:
        placeholder.button("Download Images", disabled=True, key = "button_urls_2")
        # Split the image_urls by newline
        image_urls = image_urls.split("\n")
        # Remove empty URLs
        image_urls = list(filter(None, image_urls))
        # Display the download count after the download process is complete
        download_count = download_images(image_urls, create_subfolders)
        st.write("Number of images downloaded: ", download_count)
        
 
with tab2:

    # Get the list of image URLs
    uploaded_file = st.file_uploader('Choose a CSV file with a list of image URLs:', key = "uploaded_file_csv")

    # Add a checkbox to choose whether to create subfolders
    create_subfolders = st.checkbox('Create subfolders based on URL structure', key = "create_subfolders_csv")

    # Add a download button
    if st.button('Download Images', key = "button_csv"):

        # Add a download button
        if uploaded_file is not None:
            
            # Load the CSV file into a Pandas dataframe
            df = pd.read_csv(uploaded_file)

            # Get the list of image URLs from the 'url' column of the dataframe
            image_urls = df['url'].tolist()
         
            # Display the download count after the download process is complete
            download_count = download_images(image_urls, create_subfolders)
            st.write("Number of images downloaded: ", download_count)

        else:
            st.warning('Please upload a CSV file with a list of image URLs.')
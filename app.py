import streamlit as st # type: ignore
import os
import shutil
from pathlib import Path
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="File Organizer Automation",
    page_icon="📁",
    layout="wide"
)

# Define file type categories
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".csv"],
    "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".wma"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Programs": [".py", ".c", ".cpp", ".java", ".html", ".css", ".js", ".php", ".json", ".xml"],
    "Executables": [".exe", ".msi", ".apk", ".app", ".bat", ".sh"],
    "Others": []
}

def get_file_category(file_ext):
    """Determine the category for a given file extension"""
    file_ext = file_ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_ext in extensions:
            return category
    return "Others"

def organize_files(source_folder, progress_callback=None):
    """
    Organize files in the source folder into categorized subfolders
    Returns: dict with statistics
    """
    stats = {
        "total_files": 0,
        "moved_files": 0,
        "skipped_files": 0,
        "categories": {},
        "errors": []
    }
    
    # Check if folder exists
    if not os.path.exists(source_folder):
        return {"error": "Folder not found. Please check the path."}
    
    # Get list of files
    files = [f for f in os.listdir(source_folder) 
             if os.path.isfile(os.path.join(source_folder, f))]
    
    stats["total_files"] = len(files)
    
    # First pass: determine which categories are needed
    needed_categories = set()
    for filename in files:
        file_ext = os.path.splitext(filename)[1].lower()
        category = get_file_category(file_ext)
        needed_categories.add(category)
    
    # Create only the needed category folders
    for category in needed_categories:
        folder_path = os.path.join(source_folder, category)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        stats["categories"][category] = 0
    
    # Process each file
    for idx, filename in enumerate(files):
        file_path = os.path.join(source_folder, filename)
        
        # Update progress
        if progress_callback:
            progress_callback(idx + 1, len(files), filename)
        
        # Get file extension
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Determine category
        category = get_file_category(file_ext)
        
        # Move file
        try:
            dest_path = os.path.join(source_folder, category, filename)
            
            # Handle duplicate filenames
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(source_folder, category, new_filename)
                    counter += 1
            
            shutil.move(file_path, dest_path)
            stats["moved_files"] += 1
            stats["categories"][category] += 1
            
        except Exception as e:
            stats["errors"].append(f"Error moving {filename}: {str(e)}")
            stats["skipped_files"] += 1
    
    return stats

def undo_organize_files(source_folder, progress_callback=None):
    """
    Undo file organization by moving files from category subfolders back to the parent folder
    Returns: dict with statistics
    """
    stats = {
        "total_files": 0,
        "moved_files": 0,
        "skipped_files": 0,
        "errors": []
    }
    
    # Check if folder exists
    if not os.path.exists(source_folder):
        return {"error": "Folder not found. Please check the path."}
    
    # Get all category folders
    category_folders = [os.path.join(source_folder, cat) for cat in FILE_CATEGORIES.keys()
                        if os.path.isdir(os.path.join(source_folder, cat))]
    
    # Collect all files from category subfolders
    all_files = []
    for cat_folder in category_folders:
        files_in_cat = [os.path.join(cat_folder, f) for f in os.listdir(cat_folder)
                        if os.path.isfile(os.path.join(cat_folder, f))]
        all_files.extend(files_in_cat)
    
    stats["total_files"] = len(all_files)
    
    # Move files back to parent folder
    for idx, file_path in enumerate(all_files):
        if progress_callback:
            progress_callback(idx + 1, len(all_files), os.path.basename(file_path))
        
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(source_folder, filename)
            
            # Handle duplicate filenames
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{base}_restored_{counter}{ext}"
                    dest_path = os.path.join(source_folder, new_filename)
                    counter += 1
            
            shutil.move(file_path, dest_path)
            stats["moved_files"] += 1
        except Exception as e:
            stats["errors"].append(f"Error moving {os.path.basename(file_path)}: {str(e)}")
            stats["skipped_files"] += 1
    
    # Delete empty category folders
    for category in FILE_CATEGORIES.keys():
        folder_path = os.path.join(source_folder, category)
        if os.path.isdir(folder_path):
            try:
                # Check if folder is empty
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
            except Exception as e:
                # Silently skip if folder is not empty or can't be deleted
                pass
    
    return stats

def preview_organization(source_folder):
    """Preview what files will be moved where"""
    preview = {}
    
    if not os.path.exists(source_folder):
        return None
    
    files = [f for f in os.listdir(source_folder) 
             if os.path.isfile(os.path.join(source_folder, f))]
    
    for filename in files:
        file_ext = os.path.splitext(filename)[1].lower()
        category = get_file_category(file_ext)
        
        if category not in preview:
            preview[category] = []
        preview[category].append(filename)
    
    return preview

# Main App
st.title("📁 File Organizer Automation")
st.markdown("**Developed by: Yash Sondekar**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    This tool automatically organizes files in a folder based on their type:
    
    - 🖼️ Images
    - 📄 Documents
    - 🎥 Videos
    - 🎵 Audio
    - 📦 Archives
    - 💻 Programs
    - ⚙️ Executables
    - 📂 Others
    """)
    
    st.header("🎯 Features")
    st.markdown(
        """
    <div style="background:#0f5132;border-radius:8px;padding:12px;color:#eaffea;">
      <ul style="margin:0;padding-left:20px;">
        <li>✅ Automatic file categorization</li>
        <li>✅ Preview before organizing</li>
        <li>✅ Undo organization (restore files)</li>
        <li>✅ Duplicate file handling</li>
        <li>✅ Progress tracking</li>
        <li>✅ Detailed statistics</li>
      </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Main content
tab1, tab2, tab3 = st.tabs(["📂 Organize Files", "🔄 Undo Organization", "📊 File Categories"])

with tab1:
    st.header("Organize Your Files")
    
    # Folder path input
    folder_path = st.text_input(
        "Enter folder path to organize:",
        placeholder="D:/Python Projects",
        help="Enter the full path of the folder you want to organize"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        preview_btn = st.button("🔍 Preview", use_container_width=True)
    
    with col2:
        organize_btn = st.button("🚀 Organize Files", type="primary", use_container_width=True)
    
    # Preview functionality
    if preview_btn and folder_path:
        with st.spinner("Analyzing folder..."):
            preview = preview_organization(folder_path)
            
            if preview is None:
                st.error("❌ Folder not found. Please check the path.")
            elif not preview:
                st.warning("⚠️ No files found in this folder.")
            else:
                st.success(f"Found {sum(len(files) for files in preview.values())} files")
                
                st.subheader("Preview of file organization:")
                
                for category, files in sorted(preview.items()):
                    with st.expander(f"📁 {category} ({len(files)} files)"):
                        for file in files:
                            st.text(f"  • {file}")
    
    # Organize functionality
    if organize_btn and folder_path:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, filename):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing: {filename} ({current}/{total})")
        
        with st.spinner("Organizing files..."):
            stats = organize_files(folder_path, update_progress)
            
            if "error" in stats:
                st.error(f"❌ {stats['error']}")
            else:
                progress_bar.progress(1.0)
                status_text.empty()
                
                st.balloons()
                st.success("✅ File organization completed successfully!")
                
                # Display statistics
                st.subheader("📊 Organization Summary")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Files", stats["total_files"])
                col2.metric("Files Moved", stats["moved_files"])
                col3.metric("Files Skipped", stats["skipped_files"])
                
                # Category breakdown
                st.subheader("📁 Files per Category")
                
                chart_data = {k: v for k, v in stats["categories"].items() if v > 0}
                if chart_data:
                    st.bar_chart(chart_data)
                
                # Detailed breakdown
                with st.expander("📋 Detailed Breakdown"):
                    for category, count in sorted(stats["categories"].items()):
                        if count > 0:
                            st.write(f"**{category}:** {count} files")
                
                # Show errors if any
                if stats["errors"]:
                    with st.expander("⚠️ Errors encountered", expanded=False):
                        for error in stats["errors"]:
                            st.warning(error)

with tab2:
    st.header("🔄 Undo File Organization")
    st.write("Move all organized files back to the main folder.")
    
    undo_folder_path = st.text_input(
        "Enter folder path to undo organization:",
        placeholder="e.g., C:/Users/YourName/Downloads",
        help="Enter the full path of the organized folder"
    )
    
    undo_btn = st.button("↩️ Undo Organization", type="secondary", use_container_width=True)
    
    if undo_btn and undo_folder_path:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_undo_progress(current, total, filename):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Moving: {filename} ({current}/{total})")
        
        with st.spinner("Undoing organization..."):
            stats = undo_organize_files(undo_folder_path, update_undo_progress)
            
            if "error" in stats:
                st.error(f"❌ {stats['error']}")
            else:
                progress_bar.progress(1.0)
                status_text.empty()
                
                st.success("✅ Organization undo completed!")
                
                # Display statistics
                st.subheader("📊 Undo Summary")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Files", stats["total_files"])
                col2.metric("Files Restored", stats["moved_files"])
                col3.metric("Files Skipped", stats["skipped_files"])
                
                # Show errors if any
                if stats["errors"]:
                    with st.expander("⚠️ Errors encountered", expanded=False):
                        for error in stats["errors"]:
                            st.warning(error)

with tab3:
    st.header("📊 Supported File Categories")
    st.markdown("These are the file types that will be automatically categorized:")
    
    for category, extensions in FILE_CATEGORIES.items():
        if extensions:  # Skip "Others" category
            with st.expander(f"📁 {category}"):
                st.write(", ".join(extensions))

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ using Python & Streamlit</p>
        <p><small>File Organizer Automation v1.0 | Developed by Yash Sondekar</small></p>
    </div>
    """,
    unsafe_allow_html=True
)
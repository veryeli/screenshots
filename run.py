import os
import hashlib
import cv2
import sqlite3

# Hardcoded path to the SQLite database file

OUTPUT_DIR = 'output'
DB_PATH = os.path.join(OUTPUT_DIR, "video_metadata.db")


def initialize_db(db_path):
    """Initialize the SQLite database and create a table if it doesn't exist."""
    if not os.path.exists(db_path):
        print(f"Creating database at {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT,
                ultimate_path TEXT,
                full_sha_hash TEXT
            )
        ''')
        conn.commit()
        conn.close()
    else:
        print(f"Using existing database at {db_path}")

def insert_video_record(db_path, original_path, ultimate_path, full_sha_hash):
    """Insert a record of the video into the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (original_path, ultimate_path, full_sha_hash)
        VALUES (?, ?, ?)
    ''', (original_path, ultimate_path, full_sha_hash))
    conn.commit()
    conn.close()

def generate_sha_hash(filepath, length=5):
    """Generate SHA1 hash of the file's contents and return the full hash and last `length` digits."""
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    full_hash = sha1.hexdigest()
    return full_hash, full_hash[-length:]

def capture_screenshot(video_path, output_path):
    """Capture a screenshot from the first frame of the video and save it."""
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
        cv2.imwrite(output_path, frame)
    cap.release()

def video_already_processed(db_path, original_path):
    """Check if a video with the given original path is already in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM videos WHERE original_path = ?', (original_path,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def video_already_processed(db_path, original_path):
    """Check if a video with the given original path is already in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM videos WHERE original_path = ?', (original_path,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def process_videos_in_directory(input_directory, output_directory, db_path):
    """Recursively process each video file in the directory."""
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                video_path = os.path.join(root, file)

                # Check if the video has already been processed
                if video_already_processed(db_path, video_path):
                    print(f"Skipping already processed video: {video_path}")
                    continue

                full_sha_hash, hash_suffix = generate_sha_hash(video_path)
                filename = os.path.splitext(file)[0]
                output_filename = f"{filename}_{hash_suffix}.jpg"
                output_path = os.path.join(output_directory, output_filename)

                # Capture and save a screenshot
                capture_screenshot(video_path, output_path)

                # Insert record into the database
                insert_video_record(db_path, video_path, output_path, full_sha_hash)
                print(f"Saved screenshot: {output_path} and inserted record into DB.")

def main():
    # Get input from the user for input and output directories
    input_dir = input("Enter the input directory containing video files: ").strip()
    output_dir = input("Enter the output directory where screenshots will be saved: ").strip()
    if not output_dir:
        output_dir = OUTPUT_DIR

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize the SQLite database (create if it doesn't exist)
    initialize_db(DB_PATH)

    # Process the videos
    process_videos_in_directory(input_dir, OUTPUT_DIR, DB_PATH)

if __name__ == "__main__":
    main()

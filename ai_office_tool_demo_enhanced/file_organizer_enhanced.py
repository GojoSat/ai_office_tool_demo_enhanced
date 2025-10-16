"""
AI Office Tool — File Organizer (Enhanced Demo)
Author: Wick Chen
License: MIT

Features:
- Organize files by extension into subfolders.
- Support dry-run, logging, and undo (restore) functionality.
- Command-line interface with flexible options.

Usage examples:
    python file_organizer_enhanced.py organize ./test_files
    python file_organizer_enhanced.py organize ./test_files --dry-run
    python file_organizer_enhanced.py undo ./test_files
    python file_organizer_enhanced.py history ./test_files
"""

import os
import shutil
import sys
import argparse
import json
import logging
from datetime import datetime

LOGS_DIR = ".aioffice_logs"

def setup_logging(base_folder):
    os.makedirs(os.path.join(base_folder, LOGS_DIR), exist_ok=True)
    log_file = os.path.join(base_folder, LOGS_DIR, "organizer.log")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    return log_file

def scan_and_organize(folder, dry_run=False, prefix=""):
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        logging.error("Folder does not exist: %s", folder)
        return None

    actions = []
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath) and not fpath.startswith(os.path.join(folder, LOGS_DIR)):
            ext = os.path.splitext(fname)[1].lower().strip('.')
            if not ext:
                ext = 'no_ext'
            target_dir = os.path.join(folder, ext)
            os.makedirs(target_dir, exist_ok=True)
            dest = os.path.join(target_dir, fname)
            actions.append({"src": fpath, "dst": dest})
    # perform moves
    for act in actions:
        logging.info("Move: %s -> %s", act["src"], act["dst"])
    if dry_run:
        logging.info("Dry run mode; no changes made.")
        return actions
    # do moves and save log
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    history_file = os.path.join(folder, LOGS_DIR, f"history_{timestamp}.json")
    for act in actions:
        try:
            shutil.move(act["src"], act["dst"])
        except Exception as e:
            logging.error("Failed to move %s: %s", act["src"], e)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)
    logging.info("Organization complete. History saved to %s", history_file)
    return actions

def undo_last(folder):
    folder = os.path.abspath(folder)
    logs_path = os.path.join(folder, LOGS_DIR)
    if not os.path.isdir(logs_path):
        logging.error("No history found.")
        return
    history_files = sorted([f for f in os.listdir(logs_path) if f.startswith("history_")])
    if not history_files:
        logging.error("No history files to undo.")
        return
    last = history_files[-1]
    history_file = os.path.join(logs_path, last)
    with open(history_file, "r", encoding="utf-8") as f:
        actions = json.load(f)
    # reverse moves
    for act in actions:
        try:
            if os.path.exists(act["dst"]):
                # ensure src dir exists
                src_dir = os.path.dirname(act["src"])
                os.makedirs(src_dir, exist_ok=True)
                shutil.move(act["dst"], act["src"])
                logging.info("Restored: %s -> %s", act["dst"], act["src"])
        except Exception as e:
            logging.error("Failed to restore %s: %s", act["dst"], e)
    # move history to undone
    undone_file = history_file.replace("history_", "undone_")
    os.replace(history_file, undone_file)
    logging.info("Undo complete. Moved history to %s", undone_file)

def list_history(folder):
    folder = os.path.abspath(folder)
    logs_path = os.path.join(folder, LOGS_DIR)
    if not os.path.isdir(logs_path):
        logging.info("No history found.")
        return
    files = sorted(os.listdir(logs_path))
    for f in files:
        print(f)

def main():
    parser = argparse.ArgumentParser(prog="ai-file-organizer", description="AI Office File Organizer (Enhanced Demo)")
    sub = parser.add_subparsers(dest="cmd")
    p1 = sub.add_parser("organize", help="Organize files in folder by extension")
    p1.add_argument("folder")
    p1.add_argument("--dry-run", action="store_true")
    p1.add_argument("--prefix", type=str, default="")

    p2 = sub.add_parser("undo", help="Undo last organize action")
    p2.add_argument("folder")

    p3 = sub.add_parser("history", help="List history files")
    p3.add_argument("folder")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    folder = os.path.abspath(args.folder)
    log_file = setup_logging(folder)
    logging.info("Log file: %s", log_file)

    if args.cmd == "organize":
        scan_and_organize(folder, dry_run=args.dry_run, prefix=args.prefix)
    elif args.cmd == "undo":
        undo_last(folder)
    elif args.cmd == "history":
        list_history(folder)

if __name__ == "__main__":
    main()

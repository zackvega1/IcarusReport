# main.py

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from api_utils import fetch_event_ids, fetch_phase_groups, fetch_pools, fetch_sets_data, connect_to_google_sheet, fetch_player_details, batch_update_google_sheet
from helpers import parse_matches, export_to_csv, calculate_elo


def show_matches():
    match_display.delete(1.0, tk.END)
    if tournament_data:
        matches = parse_matches(tournament_data)
        if matches:
            for match in matches:
                match_text = f"{match[0]}: {match[1]} vs {match[4]} - Score: {match[2]} - {match[5]}"
                match_display.insert(tk.END, match_text + "\n")
        else:
            match_display.insert(tk.END, "No matches found for the selected pool.\n")
    else:
        match_display.insert(tk.END, "No data available.\n")

def save_to_google_sheet():
    try:
        sheet = connect_to_google_sheet(credentials_file, sheet_name)
        tournament_type = tournament_type_var.get()  # Get the selected tournament type
        batch_update_google_sheet(sheet, tournament_data, selected_tournament.get(), tournament_url_entry.get(), tournament_type)
        messagebox.showinfo("Success", "Matches saved to Google Sheets successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save to Google Sheets: {e}")

def save_all_pools():
    try:
        if not pool_listbox.curselection():
            messagebox.showerror("Error", "Please select a starting pool to begin saving.")
            return

        # Get the index of the currently selected pool
        start_index = pool_listbox.curselection()[0]

        sheet = connect_to_google_sheet(credentials_file, sheet_name)
        tournament_type = tournament_type_var.get()  # Get the selected tournament type

        # Iterate over all pools from the selected pool onwards
        for i in range(start_index, pool_listbox.size()):
            pool_name = pool_listbox.get(i)
            pool_id = pool_id_map[pool_name]
            global tournament_data
            tournament_data = fetch_sets_data(api_key, pool_id)

            if not tournament_data:
                messagebox.showerror("Error", f"Failed to fetch data for pool {pool_name}.")
                continue

            batch_update_google_sheet(sheet, tournament_data, selected_tournament.get(), tournament_url_entry.get(), tournament_type)
            match_display.insert(tk.END, f"Saved pool {pool_name}.\n")

        messagebox.showinfo("Success", "All pools saved to Google Sheets successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save all pools: {e}")

def on_event_selected(event):
    if not event_listbox.curselection():
        return

    selected_event_name = event_listbox.get(event_listbox.curselection())
    selected_event_id = event_id_map[selected_event_name]
    phases = fetch_phase_groups(api_key, selected_event_id)
    if phases:
        phase_id_map.clear()
        phase_listbox.delete(0, tk.END)
        for phase_id, phase_name in phases:
            phase_id_map[phase_name] = phase_id
            phase_listbox.insert(tk.END, phase_name)

def on_phase_selected(event):
    if not phase_listbox.curselection():
        return

    selected_phase_name = phase_listbox.get(phase_listbox.curselection())
    selected_phase_id = phase_id_map[selected_phase_name]
    pools = fetch_pools(api_key, selected_phase_id)
    if pools:
        pool_id_map.clear()
        pool_listbox.delete(0, tk.END)
        for pool_id, pool_name in pools:
            pool_id_map[pool_name] = pool_id
            pool_listbox.insert(tk.END, pool_name)

def on_pool_selected(event):
    if not pool_listbox.curselection():
        return

    selected_pool_name = pool_listbox.get(pool_listbox.curselection())
    selected_pool_id = pool_id_map[selected_pool_name]
    global tournament_data
    tournament_data = fetch_sets_data(api_key, selected_pool_id)
    show_matches()

def fetch_events():
    slug = slug_entry.get()
    events = fetch_event_ids(api_key, slug)
    if events:
        event_id_map.clear()
        event_listbox.delete(0, tk.END)
        for event_id, event_name in events:
            event_id_map[event_name] = event_id
            event_listbox.insert(tk.END, event_name)

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Tournament Viewer")

api_key = "YOUR_API_KEY"
credentials_file = "credentials.json"
sheet_name = "AutoElo"
tournament_data = None

# Widgets for slug entry and fetching events
slug_label = tk.Label(root, text="Enter Tournament Slug:")
slug_label.pack(pady=5)

slug_entry = tk.Entry(root, width=50)
slug_entry.pack(pady=5)

fetch_button = tk.Button(root, text="Fetch Events", command=fetch_events)
fetch_button.pack(pady=10)

# Listbox to display and select events
event_listbox = tk.Listbox(root)
event_listbox.pack(pady=5)
event_listbox.bind('<<ListboxSelect>>', on_event_selected)

# Listbox to display and select phases
phase_listbox = tk.Listbox(root)
phase_listbox.pack(pady=5)
phase_listbox.bind('<<ListboxSelect>>', on_phase_selected)

# Listbox to display and select pools
pool_listbox = tk.Listbox(root)
pool_listbox.pack(pady=5)
pool_listbox.bind('<<ListboxSelect>>', on_pool_selected)

# Dropdown to select tournament name
selected_tournament = tk.StringVar()
tournament_dropdown = ttk.Combobox(root, textvariable=selected_tournament)
tournament_dropdown['values'] = ('TNS', 'GG', 'EVO')  # Add other tournament names as needed
tournament_dropdown.set('Select Tournament')
tournament_dropdown.pack(pady=5)

# Entry for tournament URL
tournament_url_entry = tk.Entry(root, width=50)
tournament_url_entry.insert(0, "Enter Tournament URL")
tournament_url_entry.pack(pady=5)

# Dropdown for selecting tournament type (online/offline)
tournament_type_var = tk.StringVar()
tournament_type_dropdown = ttk.Combobox(root, textvariable=tournament_type_var)
tournament_type_dropdown['values'] = ('Online', 'Offline')
tournament_type_dropdown.set('Select Tournament Type')
tournament_type_dropdown.pack(pady=5)

# Button to save matches to Google Sheets
save_button = tk.Button(root, text="Save to Google Sheet", command=save_to_google_sheet)
save_button.pack(pady=10)

# Button to save all pools starting from the selected pool
save_all_button = tk.Button(root, text="Save All Pools", command=save_all_pools)
save_all_button.pack(pady=5)

# Display area for matches
match_display = scrolledtext.ScrolledText(root, width=60, height=20)
match_display.pack(pady=5)

# Dictionaries to map event, phase, and pool names to their IDs
event_id_map = {}
phase_id_map = {}
pool_id_map = {}

root.mainloop()
